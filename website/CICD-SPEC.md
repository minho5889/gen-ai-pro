# CI/CD Spec — GitHub Actions

One page. Encodes the automation policy for this repo before it becomes YAML. Companion to
[FEASIBILITY.md](FEASIBILITY.md); implementation follows sign-off on the three open decisions at the
bottom.

## Goals / non-goals

**Goals:** every push gets the full check suite (the manual verification pass caught 3 real bugs —
automate exactly that); the three frequent, low-blast-radius paths deploy themselves; zero stored
AWS credentials; $0/month (public repo → unlimited Actions minutes).
**Non-goals:** `terraform apply` in CI (solo project — a human applies); multi-environment
(single personal prod); rollback automation beyond `git revert` + redeploy.

## Pipeline 1 — `ci.yml` (every push and PR, all branches)

| Job | What it runs | Needs AWS? |
|---|---|---|
| content | `tools/consistency_check.py` (absorbs today's `consistency.yml`) | no |
| lint | ruff check + format-check (Google docstring convention enforced) | no |
| terraform | `fmt -check` + `init -backend=false` + `validate` | no |
| frontend | `npm ci`, prettier check, `npm run build` (tsc strict + Vite) | no |
| tests | `pytest tests/` (functional-core units) + `backend/test_smoke.py` (SSE contract: health, 400, meta→tokens→done, clean close) | no |

Property worth keeping: **CI needs zero AWS access**, so fork PRs and feature branches are safe by
construction. Concurrency: cancel-in-progress per branch.

## Pipeline 2 — `deploy.yml` (push to `main` only, path-filtered)

| Changed path | Action | Guard before deploy |
|---|---|---|
| `website/frontend/**` | build → `s3 sync dist/ --delete` → CloudFront invalidation | build is the guard |
| `website/backend/**` | zip → `lambda update-function-code` | smoke test re-runs first |
| `guides/**`, `_cram/**`, `AIP-C01-Exam-Blueprint.md` | `sync_corpus.py` — re-chunk, md5-diff upload, **one batched ingestion job** | consistency checker re-runs first |
| `website/terraform/**` | `terraform plan` posted to the job summary — **never apply** | requires remote state (decision 1) |

Deploy targets (bucket names, distribution id, function name, KB id) come from `terraform output`
via remote state — one source of truth, nothing hardcoded in workflows.

## Auth — OIDC, no keys

- `token.actions.githubusercontent.com` IAM OIDC provider + one role, `gen-ai-pro-gha-deploy`
  (managed in Terraform alongside everything else).
- Trust policy: assumable **only** by `repo:minho5889/gen-ai-pro:ref:refs/heads/main`. PRs and forks
  can't even authenticate.
- Permissions, least-priv, no create/destroy/IAM: `s3` sync on the two buckets,
  `cloudfront:CreateInvalidation` on the one distribution, `lambda:UpdateFunctionCode` on the one
  function, `bedrock:StartIngestionJob`/`GetIngestionJob` on the one KB, read on the state bucket.
- (This is Task 2.3 identity federation, running in your own repo.)

## Failure & rollback policy

- A red guard job skips its deploy job; other paths deploy independently.
- Deploy concurrency: queued, never cancelled mid-sync.
- Rollback = `git revert` + push; every target is stateless or re-derivable (site files, Lambda
  code, corpus chunks).

## Cost

$0/month: public-repo Actions minutes are unlimited; OIDC is free; deploy API calls are
free/negligible; ingestion re-runs cost cents (Titan embeddings on changed chunks only would be
ideal, but Bedrock re-embeds the data source's changed objects — md5-diff upload keeps that small).
*(Actions pricing policy is point-in-time.)*

## Open decisions (sign-off before implementation)

> **Approved 2026-07-06: all three, as recommended.** Implemented in `.github/workflows/`
> (ci / deploy-frontend / deploy-backend / sync-corpus / terraform-plan), `terraform/oidc.tf`,
> `terraform/state.tf`, and `scripts/bootstrap_state.sh`. Branch protection is a one-time manual
> GitHub setting — steps in [README.md](README.md#cicd).

1. **Remote Terraform state** — move state to a versioned S3 bucket with native lockfile locking
   (`use_lockfile`)? **Recommended: yes.** Enables plan-in-CI + `terraform output` as the deploy
   source of truth, and survives laptop loss. One-time bootstrap: create the state bucket, add
   `backend "s3"`, `terraform init -migrate-state`. If deferred: drop the terraform row from
   deploy.yml and pass deploy targets as GitHub repo variables instead.
2. **Auto-ingest corpus on guide edits** — every push to `main` touching guides re-chunks and
   re-ingests (~cents, ~minutes). **Recommended: yes** — it's the whole point of the site staying
   current. Alternative: manual `workflow_dispatch` button.
3. **Branch protection** — require CI green before merge to `main`. **Recommended: on**, even solo
   (it's what makes the guards real). Costs nothing; direct pushes then need PRs.
