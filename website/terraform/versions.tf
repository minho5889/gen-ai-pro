terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.95"
    }
    # Cloud Control provider tracks CloudFormation schemas, which already
    # support S3 Vectors for Bedrock Knowledge Bases while the classic aws
    # provider lags (hashicorp/terraform-provider-aws#44871).
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 1.30"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4"
    }
  }
}

provider "aws" {
  region = var.region
}

provider "awscc" {
  region = var.region
}
