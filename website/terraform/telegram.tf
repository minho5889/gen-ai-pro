# Telegram bot Lambda (website/TELEGRAM-SPEC.md).
# NOTE: run `make telegram-package` before plan/apply — the archive stages
# handler + shared core + bank.json into website/telegram/.build/.
# (CI's `terraform validate` is static and doesn't need the directory.)

variable "telegram_owner_chat_id" {
  description = "The single chat id this bot serves; empty = unbound (bot replies with your id)"
  type        = string
  default     = ""
}

variable "telegram_param_name" {
  description = "SSM SecureString holding {\"token\": ..., \"secret\": ...} — created manually so it never enters state"
  type        = string
  default     = "/aip-study/telegram"
}

data "archive_file" "telegram" {
  type        = "zip"
  source_dir  = "${path.module}/../telegram/.build"
  output_path = "${path.module}/.build/telegram.zip"
}

resource "aws_iam_role" "telegram" {
  name = "${var.project}-telegram-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "telegram_logs" {
  role       = aws_iam_role.telegram.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "telegram" {
  name = "telegram-permissions"
  role = aws_iam_role.telegram.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadBotCredentials"
        Effect   = "Allow"
        Action   = ["ssm:GetParameter"]
        Resource = ["arn:aws:ssm:${var.region}:${data.aws_caller_identity.me.account_id}:parameter${var.telegram_param_name}"]
      },
      {
        Sid      = "RetrieveFromKb"
        Effect   = "Allow"
        Action   = ["bedrock:Retrieve"]
        Resource = [local.kb_arn]
      },
      {
        Sid    = "StreamFromNova"
        Effect = "Allow"
        Action = ["bedrock:InvokeModelWithResponseStream", "bedrock:InvokeModel"]
        Resource = [
          "arn:aws:bedrock:*:${data.aws_caller_identity.me.account_id}:inference-profile/${var.model_id}",
          "arn:aws:bedrock:*::foundation-model/*nova*",
        ]
      },
    ]
  })
}

resource "aws_lambda_function" "telegram" {
  function_name = "${var.project}-telegram"
  role          = aws_iam_role.telegram.arn
  runtime       = "python3.13"
  architectures = ["x86_64"]
  handler       = "handler.lambda_handler"
  timeout       = 60
  memory_size   = 256

  filename         = data.archive_file.telegram.output_path
  source_code_hash = data.archive_file.telegram.output_base64sha256

  environment {
    variables = {
      KB_ID                        = awscc_bedrock_knowledge_base.study.knowledge_base_id
      MODEL_ID                     = var.model_id
      OWNER_CHAT_ID                = var.telegram_owner_chat_id
      TELEGRAM_PARAM               = var.telegram_param_name
      ADDITIONAL_MODEL_FIELDS_JSON = var.additional_model_fields_json
    }
  }
}

# DEVIATION (flight plan in TELEGRAM-SPEC.md): Telegram cannot SigV4-sign, so
# this URL is public-auth. Mitigations: webhook secret-token constant-time
# check + single-owner chat allowlist, both enforced in handler.py.
resource "aws_lambda_function_url" "telegram" {
  function_name      = aws_lambda_function.telegram.function_name
  authorization_type = "NONE"
}

output "telegram_function_url" {
  value       = aws_lambda_function_url.telegram.function_url
  description = "Register with `make telegram-webhook`"
}

output "telegram_function_name" {
  value       = aws_lambda_function.telegram.function_name
  description = "CD target for bot code updates"
}
