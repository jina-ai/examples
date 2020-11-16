 # create the VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    "env"       = "dev"
  } 
}

resource "aws_subnet_ids" "default" {
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}
