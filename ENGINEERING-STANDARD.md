# Engineering Standard — the Paved Road

The single authoritative layer every piece of work in this repo happens inside. It pins the stack
and the workflow so decisions are made once, here — not re-litigated per feature. When documents
conflict, this one wins; [CLAUDE.md](CLAUDE.md) (session contract), [CONTRIBUTING.md](CONTRIBUTING.md)
(human workflow), and per-area specs ([website/CICD-SPEC.md](website/CICD-SPEC.md),
[website/FEASIBILITY.md](website/FEASIBILITY.md)) implement it.

**Deviation rule:** you may leave the road, but you file a flight plan first — a short decision
record in the relevant spec (what, why, the flip condition), like the AWS-vs-GCP record in
FEASIBILITY.md. Undocumented deviations get reverted on sight.

## 1. The layer (fixed choices)

| Dimension | Standard | Notes |
|---|---|---|
| Cloud | **AWS, single-cloud** | AWS-native managed service first; anything else is a deviation |
| Compute | **AWS Lambda, Python 3.13** | zero-pip-dependency bias (stdlib + boto3); Lambda Web Adapter when streaming; containers only when a measured constraint demands |
| IaC | **Terraform** (`aws` + `awscc`) | remote state in S3 (versioned, lockfile); plan in CI, apply by a human, always |
| Agentic | **Strands Agents SDK** | Ollama-served models for local dev, Bedrock for deployed; MCP for tool surfaces |
| GenAI serving | **Bedrock managed primitives first** | Knowledge Bases before hand-rolled RAG, Converse/ConverseStream API, Guardrails at the boundary; pay-per-request until sustained volume justifies provisioned capacity |
| Frontend | **TypeScript strict + Vite**, framework-free | a framework is a deviation needing a record |
| VCS / CI | **GitHub + GitHub Actions** | OIDC federation only — long-lived cloud keys are prohibited everywhere |

## 2. Git strategy

**Branching — trunk-based.** `main` is the only long-lived branch, protected, always deployable
(CD hangs off it, path-filtered). Work happens on short-lived branches named
`type/short-slug` (e.g. `feat/quiz-mode`, `fix/sse-close`, `content/guide-04-agentcore`,
`infra/state-backend`, `docs/standard`). No develop, release, or environment branches.

**Commits — Conventional Commits.**

```
type(scope): imperative subject, ≤72 chars

Body: the why, wrapped ~72. Point-in-time facts cite their source.
```

Types: `feat` `fix` `content` (study material), `infra` (terraform/CI), `docs` `test` `refactor`
`chore`. Scope is the area (`backend`, `agents`, `exam-1`, `guide-02`, `ci`…). PRs squash-merge —
the PR title *is* the commit, so CI lints PR titles against this grammar. Answer-key corrections
keep their `> Note:` blocks in content regardless of commit style.

**Merges.** PR → squash → main. Direct pushes to main are for the repo owner's solo flow only and
still run the full check suite; once branch protection is on, everything rides a PR.

## 3. Development style

- **Functional core / imperative shell** for logic-dense modules: pure functions take content and
  return results (unit-tested in `tests/`); shells own files, sockets, boto3. Chat REPLs and thin
  handlers are shells by nature — don't force the pattern onto them.
- **Google-style docstrings** on public functions; TypeScript `strict`; both machine-enforced
  (ruff pydocstyle, tsc) — a convention CI can't see doesn't exist.
- **Tests are behavior locks.** New core logic lands with a unit test; refactors prove
  byte-identical behavior where output is hashable (the chunker's corpus hash is the model).
  Integration smoke tests cover shells (`test_smoke.py` pattern: stub the SDK, run the real server).
- **Verify before asserting.** No AWS capability claim without checking current docs; fast-moving
  facts get `*(point-in-time)*` flags plus a [VERIFICATION-LOG.md](VERIFICATION-LOG.md) row. The
  repo's two worst historical bugs were confident absolutes AWS had shipped past.
- **One command:** `make check` mirrors CI exactly. If it's green locally, CI is green.

## 4. Deployment (how code reaches the world)

- **CI on every push/PR needs zero cloud access** — fork-safe by construction.
- **CD is path-filtered, main-only, OIDC-authenticated**: frontend → S3 + CloudFront invalidation;
  backend → `update-function-code`; content → re-chunk + one batched KB ingestion. Deploy targets
  resolve from `terraform output` via remote state — never hardcoded.
- **Terraform applies are human + local.** CI plans (`-refresh=false`, state-read-only role) and
  posts the plan; a person applies. The deploy role cannot create, destroy, or touch IAM.
- **Rollback = `git revert` + push.** Every deploy target is stateless or re-derivable; if a
  change can't be reverted that way, it needs a decision record before it lands.
- **Environments:** one personal prod today. Adding an env is a state-key + variable split
  (`key=website/<env>.tfstate`), not a branch.

## 5. Security baseline (non-negotiable)

No long-lived cloud credentials anywhere. Least-privilege, resource-scoped IAM everywhere (the
KB role, the Lambda role, the deploy role). Buckets private with CloudFront OAC; function URLs
IAM-auth behind CloudFront. Secrets and machine-local config (`backend.hcl`) are gitignored.
Dependabot watches all four ecosystems weekly. Security reports go through
[SECURITY.md](SECURITY.md), never public issues.

## 6. Changing this standard

The standard itself changes by PR (`docs(standard): …`) with the reasoning in the body — the same
bar as any deviation. History of what changed and why lives in [CHANGELOG.md](CHANGELOG.md) and
the git log this standard makes readable.
