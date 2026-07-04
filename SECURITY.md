# Security Policy

## Reporting

Please report vulnerabilities privately via
[GitHub Security Advisories](https://github.com/minho5889/gen-ai-pro/security/advisories/new)
rather than public issues. Expect an acknowledgment within a few days.

## Scope

In scope: the deployed website stack (`website/` — Lambda handler, Terraform IAM/OIDC posture,
CloudFront/S3 configuration), the CI/CD workflows, and the study agents (`agents/`).

Out of scope: the study content's factual accuracy (use the content-error issue template), and
third-party services themselves (AWS, GitHub, Ollama).

## Design invariants worth knowing before reporting

- No long-lived AWS credentials exist in GitHub — deploys use OIDC with a role trusting only
  `main` of this repo, with no create/destroy/IAM permissions.
- The Lambda Function URL is IAM-authenticated and reachable only through CloudFront (SigV4 OAC).
- CI jobs on PRs have zero AWS access by construction.
