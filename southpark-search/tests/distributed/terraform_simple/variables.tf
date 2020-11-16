
variable "aws_region" {
    description = "EC2 Region for the VPC"
    default = "us-east-2"
}

variable "aws_availability_zone" {
    description = "Availabtility zone"
    default = "us-east-2a"
}

variable "amis" {
    description = "AMIs by region"
    default = {
        us-east-2 = "ami-07efac79022b86107" # ubuntu 14.04 LTS
    }
}

variable "vpc_cidr" {
    description = "CIDR for the whole VPC"
    default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
    description = "CIDR for the Public Subnet"
    default = "10.0.0.0/24"
}

variable "private_subnet_cidr" {
    description = "CIDR for the Private Subnet"
    default = "10.0.1.0/24"
}
