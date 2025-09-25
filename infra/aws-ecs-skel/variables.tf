variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "autolocal"
}

variable "ecr_repo_name" {
  description = "ECR repository name"
  type        = string
  default     = "autolocal-health"
}
