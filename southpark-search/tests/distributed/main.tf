provider "aws" {
  version = "~> 2.63"
  region  = "us-east-2"
}


#Creates AWS ECR repo for SouthPark image
resource "aws_ecr_repository" "southpark" {
  name = "sp-repo"
  tags = {
    Name = "southpark_repo"
  }
}
