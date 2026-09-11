variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "btc-ai"
}

variable "env" {
  description = "Entorno"
  type        = string
  default     = "local"
}

variable "github_owner" {
  description = "Owner de GitHub para repo (usuario u org). Dejar vacío para skip módulo github"
  type        = string
  default     = ""
}

variable "github_repo_name" {
  description = "Nombre del repo"
  type        = string
  default     = "BTC-AI"
}

variable "enable_aws" {
  description = "Si true, despliega infra AWS. False = solo validación local + github"
  type        = bool
  default     = false
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_instance_type" {
  type    = string
  default = "t3.medium"
}

variable "allowed_cidr" {
  description = "CIDR permitido para acceder a 3000/8000 cuando enable_aws=true"
  type        = string
  default     = "0.0.0.0/0"
}

variable "symbols" {
  type    = string
  default = "BTCUSDT,ETHUSDT"
}
