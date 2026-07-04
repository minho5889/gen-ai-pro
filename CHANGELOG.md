# Changelog

Notable changes, [Keep a Changelog](https://keepachangelog.com/) style. Dates are commit dates;
hashes are the landing commits.

## 2026-07-07 — The paved road

- ENGINEERING-STANDARD.md: the single authoritative layer — fixed stack (AWS-native, Python
  Lambda, Terraform, Strands, GitHub), trunk-based branching, Conventional Commits (PR titles
  linted in CI), FCIS development style, OIDC-only deployment, deviation-by-decision-record
- Functional core / imperative shell refactor of the logic-dense trio with 25 behavior-locking
  unit tests; Google docstrings enforced repo-wide (`90c77b4`)

## 2026-07-06 — Engineering hygiene & CI/CD

- CI/CD per [website/CICD-SPEC.md](website/CICD-SPEC.md): check suite on every push/PR (zero AWS
  access), path-filtered OIDC deploys from `main`, remote Terraform state, plan-never-apply
  (`64e0584`, `114df54`)
- Repo professionalization: LICENSE, CONTRIBUTING, SECURITY, CODEOWNERS, Dependabot, PR/issue
  templates, Makefile, ruff + prettier enforced, this changelog
- Phase 1 hardening from local verification — three real fixes: `history` DOM-global shadow,
  SSE missing end-of-stream close, region-pinned adapter layer (`ada8ad9`)

## 2026-07-06 — Study-chat website (Phase 1)

- TypeScript chat UI (streaming SSE, TTFT badge), zero-dependency Python streaming backend
  (Lambda Web Adapter), Terraform for CloudFront/S3/Lambda/Bedrock KB on S3 Vectors, and a
  section-aware chunker (864 chunks, median 373 words) (`8bd4912`)
- Feasibility study + cloud decision record: AWS/Nova 2 Lite over GCP/Gemini Flash; RAG-first,
  fine-tune-for-persona-later (`0fffba1`, `b0a37f6`)
- Removed the NotebookLM bundle (31 derived files) and its copy-sync surface (`1a9f695`)

## 2026-07-05 — Study agents

- Local Strands/Ollama agents over the audited content: Socratic tutor (tool-grounded) and
  understanding verifier (deterministic MC scoring + LLM-judged free recall) (`95db9e3`)

## 2026-07-04 — Audit remediation & protective layer

- Applied all nine July-2026 audit fixes across guides, exams, and metadata; corrected two stale
  AWS facts at every occurrence (ingestion quotas, custom-model on-demand) (`cf9bf8d`)
- Post-fix verification pass: 11/11 exam edits and 14/14 new format drills confirmed; answer-sheet
  and blueprint propagation gaps closed (`f45364e`)
- Added VERIFICATION-LOG.md (point-in-time fact register), CLAUDE.md (editing contract),
  tools/consistency_check.py + CI (`0468163`)
- Restructured docs: single README front door, one derived set; later minors closed
  (Lake Formation coverage, hedges) (`93c7a2c`, `5e24a06`)

## 2026-07-02 — Initial import

- AIP-C01 study corpus: 8 deep-dive guides, 2 fact-checked 65-question mock exams, 5 cram sheets,
  strategy + blueprint (`612cc50`)
