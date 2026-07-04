# AIP-C01 Study Chat — Phase 1

Interactive study site with a streaming chatbot grounded in this repo's audited guides.
Stack per the [feasibility study](FEASIBILITY.md): **TypeScript** static UI (Vite, no framework),
**Python** backend (zero pip dependencies), **Terraform** IaC, Nova 2 Lite + Bedrock Knowledge Base
on **S3 Vectors**.

```
frontend/  Vite + vanilla TS chat UI (streaming SSE client, TTFT badge)
backend/   Python Lambda: KB retrieve -> Nova 2 Lite ConverseStream -> SSE
terraform/ CloudFront + S3 site, Lambda (streaming via Web Adapter), KB + S3 Vectors
scripts/   sync_corpus.py — section-aware chunker + batched ingestion
```

## Architecture decisions (the why)

- **Streaming from Python.** Lambda response streaming is natively Node-only; the
  [AWS Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter) layer gives a plain
  stdlib Python HTTP server true streaming through a Function URL (`RESPONSE_STREAM`), fronted by
  CloudFront with OAC + SigV4 — the URL is never public.
- **Chunking: pre-chunked, `NONE` strategy.** The corpus is heading-structured textbook prose, so
  [scripts/sync_corpus.py](scripts/sync_corpus.py) chunks by section/subsection, prepends a
  breadcrumb so each embedding carries its own context, strips Mermaid noise, keeps 60–600-word
  units (paragraph-boundary splits with one-paragraph overlap), and writes metadata sidecars
  (guide/domain/type filterable). Result on the current corpus: **864 chunks, median 373 words**.
- **Indexing: S3 Vectors, Titan v2 @ 512 dims, cosine.** The cost-economical store (~90% cheaper
  than OpenSearch Serverless) at sub-second query latency — semantic-only is the right tradeoff for
  conceptual study Q&A; 512 dims ≈ 1024-dim quality at half the vector storage.
- **Ingestion is batched** — one `StartIngestionJob` per sync, never per file (the repo's own
  guide-02 lesson).
- **Speed levers:** reasoning pinned off/minimal (see below — the single biggest TTFT factor),
  `maxTokens` capped at 700, top-4 retrieval, CloudFront edge for all static assets,
  `PriceClass_100`.

## Deploy

Prereqs: Terraform ≥ 1.7, AWS CLI creds, Node 20+, Python 3.11+. In the Bedrock console, enable
**model access** for `Nova 2 Lite` and `Titan Text Embeddings V2` in your region first.

```bash
cd website/terraform
terraform init && terraform apply

# 2. Chunk + upload the corpus, then run one batched ingestion job:
cd ..
python3 scripts/sync_corpus.py --dry-run        # inspect chunks locally first (optional)
python3 scripts/sync_corpus.py \
  --bucket "$(terraform -chdir=terraform output -raw corpus_bucket)" \
  --kb-id "$(terraform -chdir=terraform output -raw knowledge_base_id)" \
  --data-source-id "$(terraform -chdir=terraform output -raw data_source_id)"

# 3. Build + publish the frontend:
cd frontend && npm install && npm run build
aws s3 sync dist/ "s3://$(terraform -chdir=../terraform output -raw site_bucket)" --delete
aws cloudfront create-invalidation \
  --distribution-id "$(terraform -chdir=../terraform output -raw cloudfront_distribution_id)" \
  --paths "/*"

# 4. Open the site:
terraform -chdir=../terraform output -raw site_url
```

Re-run step 2 whenever guides/cram change; re-run step 3 for UI changes.

## Pinning reasoning off (do this before judging latency)

Nova 2 Lite is reasoning-capable; with reasoning engaged, TTFT can be tens of seconds. Verify the
current field name in the Nova 2 docs, then set it, e.g.:

```bash
terraform apply -var='additional_model_fields_json={"reasoningConfig":{"type":"disabled"}}'
```

The exact field is point-in-time (VERIFICATION-LOG row 27) — the variable passes any JSON through
to `additionalModelRequestFields` untouched. The header badge in the UI shows measured TTFT and
total time per response; target ≤ ~800 ms TTFT.

## CI/CD

Policy in [CICD-SPEC.md](CICD-SPEC.md). Five workflows: `ci` (checker, terraform validate,
frontend build, backend smoke — every push/PR, zero AWS access), plus path-filtered, main-only,
OIDC-authenticated CD: `deploy-frontend`, `deploy-backend`, `sync-corpus` (auto re-ingest on
guide/cram edits), and `terraform-plan` (plan-never-apply). Deploy workflows skip gracefully until
bootstrapped.

One-time bootstrap (after your first `terraform apply`):

```bash
# 1. Remote state (creates the versioned state bucket + backend.hcl, then):
./scripts/bootstrap_state.sh us-east-1
cd terraform && terraform init -backend-config=backend.hcl -migrate-state

# 2. OIDC deploy role (in the stack already — just apply and read the output):
terraform apply
terraform output -raw gha_deploy_role_arn

# 3. GitHub repo variables (Settings > Secrets and variables > Actions > Variables):
#      AWS_REGION, TF_STATE_BUCKET, GHA_DEPLOY_ROLE_ARN

# 4. Branch protection (Settings > Branches > Add rule for main):
#      require status checks: content, terraform, frontend, backend
```

No AWS keys are ever stored in GitHub — the role trusts only `main` of this repo via OIDC.

## Known point-in-time risks

- `awscc` schemas for S3 Vectors / KB are young — if `terraform plan` errors on an attribute name,
  check the registry docs for `awscc_s3vectors_index` / `awscc_bedrock_knowledge_base` (the classic
  `aws` provider may have gained `S3_VECTORS` support by the time you read this: see
  hashicorp/terraform-provider-aws#44871).
- The Lambda Web Adapter layer ARN pins a version/region (`variables.tf`) — bump per its README.
- Nova 2 Lite model ID uses the `global.` inference profile; confirm availability in your region.

## Cost guardrails

Steady state ≈ $5/month at personal volume (see [FEASIBILITY.md](FEASIBILITY.md)). The levers that
keep it there: S3 Vectors (not OpenSearch), 512-dim embeddings, `maxTokens` 700, top-4 retrieval,
history trimmed to 8 turns, CloudFront `PriceClass_100`, and no idle-billed infrastructure anywhere
in the stack — everything is pay-per-request.
