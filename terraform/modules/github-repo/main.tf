variable "repo_name" { type = string }
variable "owner" { type = string }
variable "description" { type = string }

resource "github_repository" "this" {
  name        = var.repo_name
  description = var.description
  visibility  = "public"
  auto_init   = false
  has_issues  = true
  has_wiki    = false
  topics      = ["bitcoin", "trading", "ollama", "binance", "fastapi", "nextjs", "terraform", "local-first"]
}

resource "github_branch_protection" "main" {
  repository_id = github_repository.this.node_id
  pattern       = "main"
  required_status_checks {
    strict = true
    # contexts = ["ci"] # habilitar cuando exista workflow
  }
  required_pull_request_reviews {
    required_approving_review_count = 0
  }
}

output "repo_url" {
  value = github_repository.this.html_url
}
