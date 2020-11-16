module "vpc" {
  source         = "terraform-aws-modules/vpc/aws"
  version        = "2.38.0"
  name           = "test_ecs_provisioning"
  cidr           = "10.0.0.0/16"
  azs            = ["us-east-2a"]
  public_subnets = ["10.0.1.0/24"]
  tags = {
    "env"       = "dev"
  }
}

data "aws_vpc" "main" {
  id = module.vpc.vpc_id
}

data "aws_subnet_ids" "default" {
  vpc_id = "${aws_default_vpc.default_vpc.id}"
}
