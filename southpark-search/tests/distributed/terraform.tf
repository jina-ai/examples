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

resource "aws_ecs_cluster" "southpark_cluster" {
  name = "southpark_cluster"
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
  family                   = "southpark_task" 
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
  requires_compatibilities = ["FARGATE"] # Stating that we are using ECS Fargate
  network_mode             = "awsvpc"    # Using awsvpc as our network mode as this is required for Fargate
  memory                   = 512         # Specifying the memory our container requires
  cpu                      = 256         # Specifying the CPU our container requires
  execution_role_arn       = "${aws_iam_role.ecsExecutionRole.arn}"
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
  launch_type     = "FARGATE"
  desired_count   = 1

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
