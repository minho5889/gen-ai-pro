# Remote state backend (CICD-SPEC decision 1).
# Values live in backend.hcl (gitignored), created by scripts/bootstrap_state.sh;
# CI passes the same values via -backend-config flags from repo variables.
#   terraform init -backend-config=backend.hcl -migrate-state
terraform {
  backend "s3" {}
}
