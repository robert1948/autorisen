# AWS ECS Skeleton (scaffolding only)

This folder contains a minimal Terraform skeleton for an ECS/Fargate migration.

Notes:

- Intentionally minimal: no ALB, no DNS, no task/service definitions yet.
- Purpose: give a starting point (ECR repo + ECS cluster) for incremental migration.

Next steps:

- Add IAM roles, task definition, ALB + target groups, RDS provisioning (or external RDS), and CI/CD integration.
