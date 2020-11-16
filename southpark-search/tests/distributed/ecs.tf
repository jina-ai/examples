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