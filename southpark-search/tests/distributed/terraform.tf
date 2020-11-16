
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


output "alb_url" {
  value = "http://${aws_alb.application_load_balancer.dns_name}"
}
