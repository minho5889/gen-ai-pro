locals {
  embed_model_arn  = "arn:aws:bedrock:${var.region}::foundation-model/${var.embedding_model}"
  vector_index_arn = awscc_s3vectors_index.corpus.index_arn
}

# ---------- Service role the Knowledge Base assumes ----------

resource "aws_iam_role" "kb" {
  name = "${var.project}-kb-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.me.account_id }
      }
    }]
  })
}

resource "aws_iam_role_policy" "kb" {
  name = "kb-permissions"
  role = aws_iam_role.kb.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "EmbedOnIngestAndQuery"
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = [local.embed_model_arn]
      },
      {
        Sid      = "ReadCorpus"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.corpus.arn, "${aws_s3_bucket.corpus.arn}/*"]
      },
      {
        Sid    = "VectorIndexReadWrite"
        Effect = "Allow"
        Action = [
          "s3vectors:GetIndex",
          "s3vectors:PutVectors",
          "s3vectors:GetVectors",
          "s3vectors:QueryVectors",
          "s3vectors:DeleteVectors",
          "s3vectors:ListVectors",
        ]
        Resource = [local.vector_index_arn]
      },
    ]
  })
}

# ---------- Knowledge Base + data source ----------

resource "awscc_bedrock_knowledge_base" "study" {
  name        = "${var.project}-kb"
  description = "AIP-C01 study guides and cram sheets (pre-chunked by section)"
  role_arn    = aws_iam_role.kb.arn

  knowledge_base_configuration = {
    type = "VECTOR"
    vector_knowledge_base_configuration = {
      embedding_model_arn = local.embed_model_arn
      embedding_model_configuration = {
        bedrock_embedding_model_configuration = {
          dimensions          = var.embedding_dimensions
          embedding_data_type = "FLOAT32"
        }
      }
    }
  }

  storage_configuration = {
    type = "S3_VECTORS"
    s3_vectors_configuration = {
      vector_bucket_arn = awscc_s3vectors_vector_bucket.vectors.vector_bucket_arn
      index_arn         = local.vector_index_arn
    }
  }

  depends_on = [aws_iam_role_policy.kb]
}

resource "awscc_bedrock_data_source" "corpus" {
  knowledge_base_id = awscc_bedrock_knowledge_base.study.knowledge_base_id
  name              = "${var.project}-corpus"

  data_source_configuration = {
    type = "S3"
    s3_configuration = {
      bucket_arn = aws_s3_bucket.corpus.arn
    }
  }

  # Chunking is done by scripts/sync_corpus.py (section-aware, breadcrumbed,
  # metadata sidecars). NONE = "my chunks are already made" — each uploaded
  # object is embedded as-is.
  vector_ingestion_configuration = {
    chunking_configuration = {
      chunking_strategy = "NONE"
    }
  }

  data_deletion_policy = "DELETE"
}
