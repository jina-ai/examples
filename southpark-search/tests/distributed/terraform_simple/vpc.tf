# Creating a VPC!
resource "aws_vpc" "custom" {

  # IP Range for the VPC
  cidr_block = var.vpc_cidr

  # Enabling automatic hostname assigning
  enable_dns_hostnames = true
  tags = {
    Name = "custom"
  }
}

# Creating Public subnet!
resource "aws_subnet" "public" {
  depends_on = [
    aws_vpc.custom
  ]

  # VPC in which subnet has to be created!
  vpc_id = aws_vpc.custom.id

  # IP Range of this subnet
  cidr_block = var.public_subnet_cidr

  # Data Center of this subnet.
  availability_zone = var.aws_availability_zone

  # Enabling automatic public IP assignment on instance launch!
  map_public_ip_on_launch = true

  tags = {
    Name = "Public Subnet"
  }
}


# Creating Private subnet!
resource "aws_subnet" "private" {
  depends_on = [
    aws_vpc.custom,
    aws_subnet.public
  ]

  # VPC in which subnet has to be created!
  vpc_id = aws_vpc.custom.id

  # IP Range of this subnet
  cidr_block = var.private_subnet_cidr

  # Data Center of this subnet.
  availability_zone = var.aws_availability_zone

  tags = {
    Name = "Private Subnet"
  }
}

# Creating an Internet Gateway for the VPC
resource "aws_internet_gateway" "Internet_Gateway" {
  depends_on = [
    aws_vpc.custom,
    aws_subnet.public,
    aws_subnet.private
  ]

  # VPC in which it has to be created!
  vpc_id = aws_vpc.custom.id

  tags = {
    Name = "IG-Public-&-Private-VPC"
  }
}

# Creating an Route Table for the public subnet!
resource "aws_route_table" "Public-Subnet-RT" {
  depends_on = [
    aws_vpc.custom,
    aws_internet_gateway.Internet_Gateway
  ]

   # VPC ID
  vpc_id = aws_vpc.custom.id

  # NAT Rule
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.Internet_Gateway.id
  }

  tags = {
    Name = "Route Table for Internet Gateway"
  }
}

# Creating a resource for the Route Table Association!
resource "aws_route_table_association" "RT-IG-Association" {

  depends_on = [
    aws_vpc.custom,
    aws_subnet.public,
    aws_subnet.private,
    aws_route_table.Public-Subnet-RT
  ]

# Public Subnet ID
  subnet_id      = aws_subnet.public.id

#  Route Table ID
  route_table_id = aws_route_table.Public-Subnet-RT.id
}
