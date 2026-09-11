variable "project_name" { type = string }

# Valida prerequisitos locales sin requerir Docker provider real
resource "null_resource" "prereqs" {
  provisioner "local-exec" {
    command = <<EOT
      echo "=== BTC-AI prereqs check ==="
      docker --version || echo "WARN: docker no encontrado (requerido para docker-compose up)"
      docker compose version || echo "WARN: docker compose no encontrado"
      ollama --version 2>/dev/null || echo "INFO: ollama CLI no en PATH (ok, corre en docker)"
      echo "project: ${var.project_name} -> OK"
    EOT
  }
}
