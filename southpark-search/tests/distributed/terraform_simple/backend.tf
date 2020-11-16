# Creating security group for Backend, this will allow access only from the instances having the security group created above.
resource "aws_security_group" "backend" {

  depends_on = [
    aws_vpc.custom,
    aws_subnet.public,
    aws_subnet.private,
    aws_security_group.flow
  ]

  description = "Index and Encoder Access only from the Flow Instance!"
  name = "backend"
  vpc_id = aws_vpc.custom.id

  # Created an inbound rule for Backend
  ingress {
    description = "Backend Access"
    from_port   = 10000
    to_port     = 60000
    protocol    = "tcp"
    security_groups = [aws_security_group.flow.id]
  }

  egress {
    description = "output from Backend"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Creating an AWS instance for the Backend! It should be launched in the private subnet!
resource "aws_instance" "encoder" {

  ami = lookup(var.amis, var.aws_region)
  instance_type = "t2.micro"
  subnet_id = aws_subnet.private.id

  vpc_security_group_ids = [aws_security_group.backend.id]

  tags = {
   Name = "BackendFromTerraform"
  }
}

# Creating an AWS instance for the Backend! It should be launched in the private subnet!
resource "aws_instance" "indexer" {

  ami = lookup(var.amis, var.aws_region)
  instance_type = "t2.micro"
  subnet_id = aws_subnet.private.id

  vpc_security_group_ids = [aws_security_group.backend.id]

  tags = {
   Name = "BackendFromTerraform"
  }
}
