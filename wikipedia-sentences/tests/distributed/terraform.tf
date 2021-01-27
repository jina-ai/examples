provider "aws" {
  version = "~> 2.0"
  region  = "us-east-2"
}

#Creates AWS ECR repo for SouthPark image
resource "aws_ecr_repository" "southpark" {
  name = "sp-repo-db"
  tags = {
    Name = "southpark_repo"
  }
}

#Create Cluster
resource "aws_ecs_cluster" "southpark_cluster" {
  name = "southpark_cluster"
}

#Create task
resource "aws_ecs_task_definition" "southpark_task" {
  family                   = "southpark_task" 
  container_definitions    = <<DEFINITION
  [
    {
      "name": "southpark_task",
      "image": "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 45678
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.southpark_loggroup.name}",  
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "streaming"
        }
      },
      "memory": 1024,
      "cpu": 128
    },
    {
      "name": "encoder",
      "image": "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 49152
        }
      ],
      "memory": 1024,
      "cpu": 128
    },
    {
      "name": "indexer",
      "image": "416454113568.dkr.ecr.us-east-2.amazonaws.com/sp-db",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 49153
        }
      ],
      "memory": 1024,
      "cpu": 128
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"] # Stating that we are using ECS Fargate
  network_mode             = "awsvpc"    # Using awsvpc as our network mode as this is required for Fargate
  memory                   = 1024         # Specifying the memory our container requires
  cpu                      = 512         # Specifying the CPU our container requires
  execution_role_arn       = "${aws_iam_role.ecsExecutionRole.arn}"
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

resource "aws_cloudwatch_log_group" "southpark_loggroup" {
  name              = "southpark-log"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_stream" "southpark-distributed-logs" {
  name           = "southpark-distributed-logs"
  log_group_name = "${aws_cloudwatch_log_group.southpark_loggroup.name}"
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

#create service
resource "aws_ecs_service" "southpark_service" {
  name            = "southpark_service"
  cluster         = "${aws_ecs_cluster.southpark_cluster.id}"
  task_definition = "${aws_ecs_task_definition.southpark_task.arn}"
  launch_type     = "FARGATE"
  desired_count   = 3
  health_check_grace_period_seconds = 30

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

#create load balancer
resource "aws_alb" "application_load_balancer" {
  name               = "southpark-lb-tf" # Naming our load balancer
  load_balancer_type = "application"
  subnets            = "${data.aws_subnet_ids.default.ids}" 
  # Referencing the security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
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
    matcher             = "200,301,302,404"
    path                = "/"
  }
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


output "alb_url" {
  value = "http://${aws_alb.application_load_balancer.dns_name}"
}
