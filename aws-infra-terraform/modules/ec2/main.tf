resource "aws_instance" "this" {

    ami = var.ami_id

    instance_type = var.instance_type_

    associate_public_ip_address = true

    subnet_id = aws_subnet.public_subnet.id

    vpc_security_group_ids = [aws_security_group.this.id]

    key_name = var.key_name

    user_data = file("./modules/ec2/deploy.sh")

    tags = {

      Name = "pipeline-ec2"
      Environment = "test"
    }

}

resource "aws_vpc" "this" {
    cidr_block = "10.0.0.0/16"

    tags = {
      Name = "pipeline-vpc"
    }
  
}


resource "aws_internet_gateway" "this" {
    vpc_id = aws_vpc.this.id

    tags = {
        Name = "pipeline-vpc-igw"
    }
  
}

resource "aws_subnet" "public_subnet" {
    vpc_id = aws_vpc.this.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "eu-west-2a"
  
}

resource "aws_subnet" "private_subnet" {
    vpc_id = aws_vpc.this.id
    cidr_block = "10.0.2.0/24"
    availability_zone = "eu-west-2b"
  
}


resource "aws_route_table" "public" {
    vpc_id = aws_vpc.this.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.this.id
    }

    tags = {
      Name = "pipeline-public-route-table"
    }

  
}

resource "aws_route_table_association" "public" {
    subnet_id      = aws_subnet.public_subnet.id
    route_table_id = aws_route_table.public.id
}


resource "aws_security_group" "this" {
    name        = "pipeline-ec2-security-group"
    description = "Allow SSH and HTTP"
    vpc_id      = aws_vpc.this.id

    ingress {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
      description = "HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
      Name = "pipeline-ec2-sg"
    }
}

