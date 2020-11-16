/*
  Flow Servers
*/
resource "aws_security_group" "flow" {
    depends_on = [
        aws_vpc.custom,
        aws_subnet.public,
        aws_subnet.private
    ]
    name = "vpc_flow"
    description = "Allow incoming HTTP connections and connect to private subnet"

    ingress {
        from_port = 45678
        to_port = 45678
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 10000
        to_port = 60000
        protocol = "tcp"
        cidr_blocks = [aws_subnet.private.cidr_block]
    }

    egress {
        from_port = 10000
        to_port = 60000
        protocol = "tcp"
        cidr_blocks = [var.private_subnet_cidr]
    }

    vpc_id = aws_vpc.custom.id

    tags = {
        Name = "FlowServerSG"
    }
}

resource "aws_instance" "flow" {
    depends_on = [
        aws_vpc.custom,
        aws_subnet.public,
        aws_subnet.private,
        aws_security_group.flow,
        aws_security_group.backend,
        aws_instance.encoder,
        aws_instance.indexer
    ]

    ami = lookup(var.amis, var.aws_region)
    availability_zone = var.aws_availability_zone
    instance_type = "t2.micro"
    vpc_security_group_ids = [aws_security_group.flow.id]
    subnet_id = aws_subnet.public.id
    associate_public_ip_address = true
    source_dest_check = false

    tags = {
        Name = "Flow Server"
    }
}


# Sets environment variables for encoder and indexer
resource "null_resource" "environment" {

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command = "tests/distributed/terraform_simple/start.sh"
    working_dir = "../../.."
    environment = {
      JINA_ENCODER_HOST = aws_instance.encoder.private_ip
      JINA_INDEX_HOST = aws_instance.indexer.private_ip
      JINA_FLOW_HOST = aws_instance.flow.public_ip
    }
  }
}


resource "aws_eip" "flow" {
    instance = aws_instance.flow.id
    vpc = true
}
