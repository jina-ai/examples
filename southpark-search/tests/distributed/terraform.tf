provider "aws" {
  version = "~> 2.0"
  region  = "us-east-2"
}

#Creates AWS ECR repo for SouthPark image
resource "aws_ecr_repository" "southpark" {
  name = "sp-repo"
  tags = {
    Name = "southpark_repo"
  }
}

resource "aws_default_vpc" "default_vpc" {
}

# AWS Instance for Encoder
resource "aws_instance" "encoder" {
  ami           = "ami-07efac79022b86107"
  instance_type = "t2.micro"
  tags = {
    Name = "encoder"
  }
}

# AWS Instance for Indexer
resource "aws_instance" "indexer" {
  ami           = "ami-07efac79022b86107"
  instance_type = "t2.micro"
  tags = {
    Name = "indexer"
  }
}

# AWS Instance for running Flow
resource "aws_instance" "flow" {
  ami           = "ami-07efac79022b86107"
  instance_type = "t2.micro"
  tags = {
    Name = "flow"
  }
  provisioner "remote-exec" {
    inline = [<<EOF
    curl -s --request PUT "http://localhost:8000/v1/flow/yaml" \
    -H  "accept: application/json" \
    -H  "Content-Type: multipart/form-data" \
    -F "uses_files=@pods/encode.yml" \
    -F "uses_files=@pods/extract.yml" \
    -F "uses_files=@pods/index.yml" \
    -F "pymodules_files=@pods/text_loader.py" \
    -F "yamlspec=@tests/distributed/flow-query.yml"
    EOF
    ]
  }
}

# Sets environment variables for encoder and indexer
resource "null_resource" "environment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command = ""
    environment = {
      JINA_ENCODER_HOST = "${aws_instance.encoder.private_ip}"
      JINA_INDEX_HOST = "${aws_instance.indexer.private_ip}"
    }
  }
}

data "aws_subnet_ids" "default" {
  vpc_id = "${aws_default_vpc.default_vpc.id}"
}

#we need to set the clusters manually since we dont use Fargate anymore
resource "aws_ecs_cluster" "southpark_cluster" {
  name = "southpark_cluster"
  capacity_providers = [aws_ecs_capacity_provider.capacity-provider-test.name]
  tags = {
    "env"       = "dev"
  }
}

resource "aws_ecs_capacity_provider" "capacity-provider-test" {
  name = "capacity-provider-test"
  
  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.asg.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      maximum_scaling_step_size = 1000
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 10
    }
  }
}


resource "aws_iam_role" "ecs-instance-role" {
  name = "ecs-instance-role-test"
  path = "/"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": ["ec2.amazonaws.com"]
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs-instance-role-attachment" {
  role       = aws_iam_role.ecs-instance-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_service_role" {
  role = aws_iam_role.ecs-instance-role.name
}


variable "key_name" {
  type        = string
  description = "The name for ssh key, used for aws_launch_configuration"
}

variable "cluster_name" {
  type        = string
  description = "The name of AWS ECS cluster"
}

resource "aws_launch_configuration" "lc" {
  name          = "test_ecs"
  image_id      = aws_instance.flow.id
  instance_type = "t2.micro"
  lifecycle {
    create_before_destroy = true
  }
  iam_instance_profile        = aws_iam_instance_profile.ecs_service_role.name
  key_name                    = var.key_name
  security_groups             = [aws_security_group.service_security_group.id]
  associate_public_ip_address = true
  user_data                   = <<EOF
#! /bin/bash
sudo apt-get update
sudo echo "ECS_CLUSTER=${var.cluster_name}" >> /etc/ecs/ecs.config
EOF
}

resource "aws_autoscaling_group" "asg" {
  name                      = "test-asg"
  launch_configuration      = aws_launch_configuration.lc.name
  min_size                  = 3
  max_size                  = 4
  desired_capacity          = 3
  health_check_type         = "ELB"
  health_check_grace_period = 300
  vpc_zone_identifier       = aws_subnet_ids.default.vpc_id

  target_group_arns     = [aws_lb_target_group.lb_target_group.arn]
  protect_from_scale_in = true
  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecsExecutionRole" {
  name               = "ecsExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

#Create ECS task
resource "aws_ecs_task_definition" "southpark_task" {
  family                   = "southpark_family" 
  container_definitions    = <<DEFINITION
  [
    {
      "name": "southpark_task",
      "image": "${aws_ecr_repository.southpark.repository_url}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 45678,
          "hostPort": 45678
        }
      ],
      "memory": 512,
      "cpu": 256
    }
  ]
  DEFINITION
  network_mode          = "bridge"
  memory                   = 512         # Specifying the memory our container requires
  cpu                      = 256         # Specifying the CPU our container requires
  execution_role_arn       = "${aws_iam_role.ecsExecutionRole.arn}"
  tags = {
    "env"       = "dev"
  }
}


#create load balancer
resource "aws_alb" "application_load_balancer" {
  name               = "southpark-lb-tf" # Naming our load balancer
  load_balancer_type = "application"
  subnets            = "${data.aws_subnet_ids.default.ids}" 
  # Referencing the security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

resource "aws_lb_listener" "lsr" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" # Referencing our load balancer
  port              = "45678"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our tagrte group
  }
}

resource "aws_lb_target_group" "target_group" {
  name        = "target-gp"
  port        = 45678
  protocol    = "HTTP"
  target_type = "ip"
  deregistration_delay = 90
  vpc_id      = "${aws_default_vpc.default_vpc.id}" # Referencing the default VPC
  health_check {
    healthy_threshold   = "3"
    interval            = "80"
    protocol            = "HTTP"
    timeout             = "60"
    unhealthy_threshold = "2"
    matcher             = "200,301,302"
    path                = "/"
  }
}

# Creating a security group for the load balancer:
# This is the one that will receive traffic from internet
resource "aws_security_group" "load_balancer_security_group" {
  description = "control access to the ALB"
  ingress {
    from_port   = 45678
    to_port     = 45678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allowing traffic in from all sources
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#ECS will receive traffic from the ALB
resource "aws_security_group" "service_security_group" {
  description = "Allow acces only from the ALB"
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    # Only allowing traffic in from the load balancer security group
    security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
  }

  egress { 
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#create service
resource "aws_ecs_service" "southpark_service" {
  name            = "southpark_service"
  cluster         = "${aws_ecs_cluster.southpark_cluster.id}"
  task_definition = "${aws_ecs_task_definition.southpark_task.arn}"
  desired_count   = 1 #this should still be 1?
  ordered_placement_strategy { #Im not sure if we need this
    type  = "binpack"
    field = "cpu"
  }

  load_balancer {
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our target group
    container_name   = "${aws_ecs_task_definition.southpark_task.family}"
    container_port   = 45678 # Specifying the container port
  }

  network_configuration {
    subnets          = data.aws_subnet_ids.default.ids
    assign_public_ip = true
    security_groups  = ["${aws_security_group.service_security_group.id}"] # Setting the security group
  }
  depends_on = [aws_lb_listener.lsr, aws_iam_role_policy_attachment.ecsTaskExecutionRole_policy]
}

output "alb_url" {
  value = "http://${aws_alb.application_load_balancer.dns_name}"
}
