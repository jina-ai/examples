terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region  = "us-east-2"
  shared_credentials_file = "/home/maximilian/.aws/credentials"
}

#Creates AWS ECR repo for SouthPark image
resource "aws_ecr_repository" "southpark" {
  name = "sp-repo2"
  tags = {
    Name = "southpark_repo"
  }
}
