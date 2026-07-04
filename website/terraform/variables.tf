variable "region" {
  description = "Region with Nova 2 Lite, Titan Embed v2, and S3 Vectors availability"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix for all resources"
  type        = string
  default     = "aip-study"
}

variable "model_id" {
  description = "Chat model (global cross-Region inference profile for capacity resilience)"
  type        = string
  default     = "global.amazon.nova-2-lite-v1:0"
}

variable "embedding_model" {
  description = "Embedding model for the knowledge base"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "embedding_dimensions" {
  description = "Titan v2 supports 256/512/1024. 512 = near-1024 quality at half the storage cost."
  type        = number
  default     = 512
}

variable "lambda_web_adapter_layer_arn" {
  description = <<-EOT
    AWS Lambda Web Adapter public layer (enables response streaming from a
    Python Lambda). Region/version drift: check the latest at
    https://github.com/awslabs/aws-lambda-web-adapter#lambda-functions-packaged-as-zip-package-for-aws-managed-runtimes
  EOT
  type        = string
  default     = "arn:aws:lambda:us-east-1:753240598075:layer:LambdaAdapterLayerX86:25"
}

variable "chat_max_tokens" {
  description = "Response cap — the biggest single latency/cost lever after reasoning mode"
  type        = number
  default     = 700
}

variable "additional_model_fields_json" {
  description = <<-EOT
    JSON passed through to Converse additionalModelRequestFields. Used to pin
    Nova 2 Lite reasoning OFF for lightning-fast TTFT. Field name is
    point-in-time — verify against current Nova 2 docs at deploy time.
  EOT
  type        = string
  default     = "{}"
}
