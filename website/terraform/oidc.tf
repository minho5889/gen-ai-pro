# GitHub Actions OIDC federation (CICD-SPEC "Auth" section): no stored AWS
# keys anywhere in GitHub. One role, assumable only from this repo's main.

variable "github_repo" {
  description = "owner/name of the GitHub repository allowed to deploy"
  type        = string
  default     = "minho5889/gen-ai-pro"
}

variable "tf_state_bucket" {
  description = "Remote-state bucket (from bootstrap_state.sh); plan-in-CI reads it"
  type        = string
  default     = ""
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]
}

data "aws_iam_policy_document" "gha_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    # Deploys only ever run from main; PRs and forks cannot even authenticate.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

locals {
  state_bucket = var.tf_state_bucket != "" ? var.tf_state_bucket : "aip-study-tfstate-${data.aws_caller_identity.me.account_id}"
}

data "aws_iam_policy_document" "gha_deploy" {
  statement {
    sid       = "SiteSync"
    effect    = "Allow"
    actions   = ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.site.arn, "${aws_s3_bucket.site.arn}/*"]
  }
  statement {
    sid       = "CorpusSync"
    effect    = "Allow"
    actions   = ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.corpus.arn, "${aws_s3_bucket.corpus.arn}/*"]
  }
  statement {
    sid       = "Invalidate"
    effect    = "Allow"
    actions   = ["cloudfront:CreateInvalidation"]
    resources = [aws_cloudfront_distribution.site.arn]
  }
  statement {
    sid       = "LambdaCode"
    effect    = "Allow"
    actions   = ["lambda:UpdateFunctionCode", "lambda:GetFunction"]
    resources = [aws_lambda_function.chat.arn]
  }
  statement {
    sid       = "Ingest"
    effect    = "Allow"
    actions   = ["bedrock:StartIngestionJob", "bedrock:GetIngestionJob"]
    resources = [local.kb_arn]
  }
  statement {
    # terraform init + plan -refresh=false -lock=false: state read only.
    sid       = "StateRead"
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = ["arn:aws:s3:::${local.state_bucket}", "arn:aws:s3:::${local.state_bucket}/*"]
  }
}

resource "aws_iam_role" "gha_deploy" {
  name                 = "${var.project}-gha-deploy"
  assume_role_policy   = data.aws_iam_policy_document.gha_trust.json
  max_session_duration = 3600
}

resource "aws_iam_role_policy" "gha_deploy" {
  name   = "deploy-permissions"
  role   = aws_iam_role.gha_deploy.id
  policy = data.aws_iam_policy_document.gha_deploy.json
}

output "gha_deploy_role_arn" {
  value       = aws_iam_role.gha_deploy.arn
  description = "Set as the GHA_DEPLOY_ROLE_ARN repo variable"
}
