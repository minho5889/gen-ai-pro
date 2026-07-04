data "aws_caller_identity" "me" {}

# ---------- Corpus bucket (pre-chunked markdown + metadata sidecars) ----------

resource "aws_s3_bucket" "corpus" {
  bucket = "${var.project}-corpus-${data.aws_caller_identity.me.account_id}"
}

resource "aws_s3_bucket_public_access_block" "corpus" {
  bucket                  = aws_s3_bucket.corpus.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "corpus" {
  bucket = aws_s3_bucket.corpus.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ---------- S3 Vectors store (the ~90%-cheaper vector option) ----------

resource "awscc_s3vectors_vector_bucket" "vectors" {
  vector_bucket_name = "${var.project}-vectors-${data.aws_caller_identity.me.account_id}"
}

resource "awscc_s3vectors_index" "corpus" {
  vector_bucket_name = awscc_s3vectors_vector_bucket.vectors.vector_bucket_name
  index_name         = "${var.project}-corpus"
  data_type          = "float32"
  dimension          = var.embedding_dimensions
  distance_metric    = "cosine"

  metadata_configuration = {
    # breadcrumb/source text is for display, not filtering; keeping it
    # non-filterable leaves filterable metadata for guide/domain/type.
    non_filterable_metadata_keys = ["breadcrumb", "source_file"]
  }
}
