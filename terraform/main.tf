# Root: orquesta módulos. Local no requiere credenciales AWS/GH.
provider "github" {
  # usa GITHUB_TOKEN env var si se setea
  owner = var.github_owner != "" ? var.github_owner : null
}

provider "aws" {
  region = var.aws_region
  # skip creds validation cuando enable_aws=false para no requerir AWS en local
  skip_credentials_validation = !var.enable_aws
  skip_metadata_api_check     = !var.enable_aws
  skip_requesting_account_id  = !var.enable_aws
  access_key                  = var.enable_aws ? null : "mock"
  secret_key                  = var.enable_aws ? null : "mock"
}

module "github_repo" {
  source      = "./modules/github-repo"
  count       = var.github_owner != "" ? 1 : 0
  repo_name   = var.github_repo_name
  owner       = var.github_owner
  description = "BTC-AI — Copiloto cripto local-first: real-time data + Ollama + 3 modos + Binance Testnet"
}

module "docker_host" {
  source       = "./modules/docker-host"
  project_name = var.project_name
}

module "aws_deploy" {
  source        = "./modules/aws-deploy"
  count         = var.enable_aws ? 1 : 0
  project_name  = var.project_name
  env           = var.env
  instance_type = var.aws_instance_type
  allowed_cidr  = var.allowed_cidr
}
