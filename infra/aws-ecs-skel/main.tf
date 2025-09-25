// Minimal Terraform skeleton for ECS/Fargate skeleton. No ALB/DNS yet.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.region
}

// Placeholder: ECR repository
resource "aws_ecr_repository" "app" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"
}

// Placeholder: ECS cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"
}

// Placeholder: Task definition and service will be added later
