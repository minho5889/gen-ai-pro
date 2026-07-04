output "site_url" {
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
  description = "The study chat site"
}

output "site_bucket" {
  value       = aws_s3_bucket.site.id
  description = "Upload the built frontend here (aws s3 sync frontend/dist/ s3://<this>)"
}

output "corpus_bucket" {
  value       = aws_s3_bucket.corpus.id
  description = "scripts/sync_corpus.py uploads chunks here"
}

output "knowledge_base_id" {
  value       = awscc_bedrock_knowledge_base.study.knowledge_base_id
  description = "Pass to scripts/sync_corpus.py --kb-id"
}

output "data_source_id" {
  value       = awscc_bedrock_data_source.corpus.data_source_id
  description = "Pass to scripts/sync_corpus.py --data-source-id"
}

output "cloudfront_distribution_id" {
  value       = aws_cloudfront_distribution.site.id
  description = "For cache invalidation after frontend deploys"
}
