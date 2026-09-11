# Terraform — BTC-AI

> Local por defecto **no requiere Terraform**. Esta carpeta es IaC opcional para reproducibilidad y deploy cloud.

## Cuándo usar

| Uso | Comando | Requiere |
|-----|---------|----------|
| Validar prereqs local | `terraform apply -var-file=environments/local/terraform.tfvars` | `terraform >=1.5` |
| Gestionar repo GitHub como código | `GITHUB_TOKEN=ghp_xxx terraform apply -var="github_owner=tu_user"` | token con `repo` scope |
| Deploy AWS (EC2 + docker) | `terraform apply -var-file=environments/aws/terraform.tfvars` | `AWS creds` |

## Estructura

- `modules/github-repo` → `github_repository` + branch protection (opcional, `count=0` si `github_owner=""`)
- `modules/docker-host` → `null_resource` que valida `docker`, `docker compose`, `ollama`
- `modules/aws-deploy` → VPC default + SG (22,3000,8000) + EC2 t3.medium con `user_data` que hace `docker compose up` (solo si `enable_aws=true`)
- `environments/local` → `enable_aws=false` (coste 0)
- `environments/aws` → `enable_aws=true`

## Quick start local (sin AWS)

```bash
cd terraform
terraform init
terraform validate
terraform plan -var-file=environments/local/terraform.tfvars
terraform apply -var-file=environments/local/terraform.tfvars
# output: github_repo_url = "github module disabled" -> normal si no seteaste github_owner
```

## AWS deploy

```bash
export AWS_PROFILE=tu-profile
cd terraform
terraform init
terraform plan -var-file=environments/aws/terraform.tfvars -var="allowed_cidr=TU_IP/32"
terraform apply -var-file=environments/aws/terraform.tfvars
# output public_ip -> abre http://<ip>:3000 y :8000
terraform destroy -var-file=environments/aws/terraform.tfvars # al terminar
```

State es local por defecto (`terraform.tfstate` gitignored). Para equipo, descomenta backend S3 en `versions.tf`.
