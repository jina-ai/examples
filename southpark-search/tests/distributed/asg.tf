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
}


resource "aws_autoscaling_group" "asg" {
  name                      = "test-asg"
  launch_configuration      = aws_launch_configuration.lc.name
  min_size                  = 3
  max_size                  = 4
  desired_capacity          = 3
  health_check_type         = "ELB"
  health_check_grace_period = 300
  vpc_zone_identifier       = aws_subnet_ids.default.public_subnets

  target_group_arns     = [aws_lb_target_group.target_group.arn]
  protect_from_scale_in = true
  lifecycle {
    create_before_destroy = true
  }
}
