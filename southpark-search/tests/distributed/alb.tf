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
  vpc_id      = "${aws_vpc.main.id}" # Referencing the default VPC
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

resource "aws_lb_listener" "lsr" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" # Referencing our load balancer
  port              = "45678"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Referencing our tagrte group
  }
}