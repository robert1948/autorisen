# AWS ECS Skeleton (scaffolding only)

This folder contains a minimal Terraform skeleton for an ECS/Fargate migration.

Notes:

- Intentionally minimal: no ALB, no DNS, no task/service definitions yet.
- Purpose: provide a starting point (ECR repo + ECS cluster) for incremental migration.

Next steps:

- Add IAM roles, task definition, ALB + target groups, RDS provisioning (or external RDS), and CI/CD integration.

## OIDC trust policy

This directory includes `trust-policy.json` — a recommended trust policy for an IAM role that GitHub Actions can assume via
OIDC.

- File: `trust-policy.json`
- Purpose: restricts assume-role to the repo `robert1948/autorisen` on the `main` branch.
 Requires the token audience to be `sts.amazonaws.com`.

Usage:

1. Create the role using the trust policy, then attach a suitable policy (for example `ReadOnlyAccess` for audits):

```sh
aws iam create-role --role-name github-actions-autorisen-live-audit \
 --assume-role-policy-document file://infra/aws-ecs-skel/trust-policy.json

aws iam attach-role-policy --role-name github-actions-autorisen-live-audit \
 --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

aws iam get-role --role-name github-actions-autorisen-live-audit --query 'Role.Arn' --output text
```text
1. Place the returned Role ARN into the repository secret `AWS_OIDC_ROLE` so workflows can assume it.
