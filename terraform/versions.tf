terraform {
  required_version = ">= 1.5.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
  # Backend local por defecto. Para equipo descomentar S3:
  # backend "s3" {
  #   bucket = "btc-ai-terraform-state"
  #   key    = "btc-ai/terraform.tfstate"
  #   region = "us-east-1"
  # }
}
