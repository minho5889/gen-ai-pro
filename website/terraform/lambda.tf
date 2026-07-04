locals {
  kb_arn = "arn:aws:bedrock:${var.region}:${data.aws_caller_identity.me.account_id}:knowledge-base/${awscc_bedrock_knowledge_base.study.knowledge_base_id}"
  # Public layer lives per-region under the awslabs account; must match var.region.
  adapter_layer_arn = var.lambda_web_adapter_layer_arn != "" ? var.lambda_web_adapter_layer_arn : "arn:aws:lambda:${var.region}:753240598075:layer:LambdaAdapterLayerX86:${var.lambda_web_adapter_layer_version}"
}

data "archive_file" "chat" {
  type        = "zip"
  source_dir  = "${path.module}/../backend"
  output_path = "${path.module}/.build/chat.zip"
  excludes    = ["test_smoke.py", "__pycache__"]
}

resource "aws_iam_role" "chat" {
  name = "${var.project}-chat-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "chat_logs" {
  role       = aws_iam_role.chat.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "chat" {
  name = "chat-permissions"
  role = aws_iam_role.chat.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
          # global inference profile + the regional foundation models it routes to
          "arn:aws:bedrock:*:${data.aws_caller_identity.me.account_id}:inference-profile/${var.model_id}",
          "arn:aws:bedrock:*::foundation-model/*nova*",
        ]
      },
    ]
  })
}

resource "aws_lambda_function" "chat" {
  function_name = "${var.project}-chat"
  role          = aws_iam_role.chat.arn
  runtime       = "python3.13"
  architectures = ["x86_64"]
  handler       = "run.sh" # Lambda Web Adapter launches this; it starts app.py
  timeout       = 120
  memory_size   = 512

  filename         = data.archive_file.chat.output_path
  source_code_hash = data.archive_file.chat.output_base64sha256

  # The adapter layer is what gives a *Python* function true response
  # streaming (natively that's a Node-only Lambda feature).
  layers = [local.adapter_layer_arn]

  environment {
    variables = {
      AWS_LAMBDA_EXEC_WRAPPER      = "/opt/bootstrap"
      AWS_LWA_INVOKE_MODE          = "response_stream"
      PORT                         = "8080"
      KB_ID                        = awscc_bedrock_knowledge_base.study.knowledge_base_id
      MODEL_ID                     = var.model_id
      MAX_TOKENS                   = tostring(var.chat_max_tokens)
      ADDITIONAL_MODEL_FIELDS_JSON = var.additional_model_fields_json
    }
  }
}

resource "aws_lambda_function_url" "chat" {
  function_name      = aws_lambda_function.chat.function_name
  authorization_type = "AWS_IAM" # CloudFront OAC signs requests; URL is not public
  invoke_mode        = "RESPONSE_STREAM"
}

# Allow only this distribution to invoke the function URL.
resource "aws_lambda_permission" "cloudfront" {
  statement_id           = "AllowCloudFrontOAC"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.chat.function_name
  principal              = "cloudfront.amazonaws.com"
  source_arn             = aws_cloudfront_distribution.site.arn
  function_url_auth_type = "AWS_IAM"
}
