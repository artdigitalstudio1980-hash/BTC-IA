variable "project_name" { type = string }
variable "env" { type = string }
variable "instance_type" { type = string }
variable "allowed_cidr" { type = string }

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "btc_ai" {
  name   = "${var.project_name}-${var.env}-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "btc_ai" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.btc_ai.id]

  user_data = <<-EOT
              #!/bin/bash
              apt-get update && apt-get install -y docker.io docker-compose git
              systemctl enable --now docker
              git clone https://github.com/${var.project_name}/BTC-AI.git /opt/btc-ai || true
              cd /opt/btc-ai && docker compose up -d || true
              EOT

  tags = {
    Name = "${var.project_name}-${var.env}"
  }
}

output "public_ip" {
  value = aws_instance.btc_ai.public_ip
}
