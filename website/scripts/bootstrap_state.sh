#!/usr/bin/env bash
# One-time Terraform remote-state bootstrap (CICD-SPEC decision 1).
# Creates a versioned, private S3 bucket for state, writes backend.hcl,
# and prints the migrate + GitHub-variable steps.
set -euo pipefail

REGION="${1:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET="aip-study-tfstate-${ACCOUNT_ID}"
TF_DIR="$(cd "$(dirname "$0")/../terraform" && pwd)"

if ! aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
  else
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
      --create-bucket-configuration LocationConstraint="$REGION"
  fi
fi
aws s3api put-bucket-versioning --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled
aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

cat > "$TF_DIR/backend.hcl" <<EOF
bucket       = "${BUCKET}"
key          = "website/terraform.tfstate"
region       = "${REGION}"
use_lockfile = true
EOF

cat <<EOF

State bucket ready: ${BUCKET}
backend.hcl written (gitignored — CI builds its own from repo variables).

Next steps:
  1. cd ${TF_DIR}
     terraform init -backend-config=backend.hcl -migrate-state
  2. terraform apply           # creates the OIDC deploy role; note the outputs
  3. Set GitHub repo variables (Settings > Secrets and variables > Actions > Variables):
       AWS_REGION           = ${REGION}
       TF_STATE_BUCKET      = ${BUCKET}
       GHA_DEPLOY_ROLE_ARN  = (terraform output -raw gha_deploy_role_arn)
EOF
