output "project" {
  value = var.project_name
}

output "mode" {
  value = var.enable_aws ? "aws" : "local"
}

output "github_repo_url" {
  value = try(module.github_repo.repo_url, "github module disabled (set github_owner)")
}

output "aws_enabled" {
  value = var.enable_aws
}

output "aws_public_ip" {
  value = try(module.aws_deploy.public_ip, null)
}
