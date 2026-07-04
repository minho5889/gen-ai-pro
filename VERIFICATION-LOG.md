# Verification Log — Point-in-Time Facts Register

Every load-bearing, fast-moving fact in this repo, with its source and last-verified date. Before
exam day, walk this table top to bottom and re-verify anything older than ~2 weeks — AWS moves fast
and content decays even when it was verified true. Statuses: **✅ Verified** (confirmed against the
cited source on the given date) · **⚠️ Unverified** (asserted in content but not pinnable to a
current authoritative source — treat with caution) · **🕐 Point-in-time** (verified or plausible,
but of a kind that drifts: quotas, prices, region lists, service status).

| # | Claim | Status | Source | Last verified | Lives in |
|---|---|---|---|---|---|
| 1 | Exam: 4 question types (MC, MR, ordering, matching); 65 scored + 10 unscored; 750/1000 pass; domains 31/26/20/12/11 | ✅ | Official AIP-C01 Exam Guide PDF v1.0 | 2026-07-03 | blueprint, strategy doc, exam READMEs, format drills |
| 2 | KB ingestion: 50 concurrent ingestion jobs per KB (adjustable); 200 data sources per KB | ✅🕐 | docs: `kb-managed-quotas` | 2026-07-04 | guide 02, cram-d1, E1 Q16, E2 Q19 |
| 3 | Custom-model serving: Provisioned Throughput **or** custom model deployment (on-demand, per-token) — never the base-model ARN | ✅🕐 | docs: `model-customization-use` | 2026-07-04 | guides 01/07, E1 Q3/Q25, E2 Q3/Q26 |
| 4 | Bedrock Agents is "Agents Classic": maintenance mode, closes to new customers 2026-07-30; AgentCore recommended for new builds | ✅🕐 | docs: `agents.html` + AWS What's New (June 2026) | 2026-07-04 | guide 04 §2, cram-d2, drills M4 |
| 5 | Batch inference: not supported for provisioned models; no tool calling / structured output (records processed independently) | ✅ | docs: `batch-inference` (verbatim notes) | 2026-07-05 | guides 01/06/07, several exam items |
| 6 | Anthropic citations + structured outputs mutually exclusive → 400 error | ✅ | Claude platform docs (structured outputs) | 2026-07-05 | guide 03, E1 Q41, E2 Q40 |
| 7 | Guardrails denied topics: definition ≤200 chars (Classic) / ≤1,000 (Standard); ≤5 sample phrases, ≤100 chars each | ✅ | docs: `guardrails-denied-topics` + AWS blog | 2026-07-05 | guide 03, cram-d3 |
| 8 | Guardrails: ≤30 denied topics per guardrail | ⚠️ | AWS pages conflict (one surface says 5); ceiling not pinned | 2026-07-05 | guide 03, cram-d3 (hedged in text) |
| 9 | KB resource policies: managed (MANAGED-type) KBs only; grantable actions `bedrock:Retrieve` + `bedrock:GetDocumentContent`; PutResourcePolicy/Get/Delete; both resource + identity policy required cross-account | ✅ | docs: `kb-managed-cross-account` | 2026-07-04 | E1 Q29 |
| 10 | Amazon Rerank 1.0 not available in us-east-1 | ✅🕐 | docs (rerank regions) | 2026-07-03 | guide 02, E1 Q12, E2 Q6 |
| 11 | AWS Cost Anomaly Detection excludes third-party Marketplace charges (e.g. Claude billed as "Anthropic, PBC") | ✅ | docs (Cost Anomaly Detection) | 2026-07-03 | guide 07, E1 Q56, E2 Q57 |
| 12 | Bedrock TPM quota deducts input + `max_tokens` up front | ✅ | docs (Bedrock quotas) | 2026-07-03 | E2 Q63 |
| 13 | OTPS = OutputTokenCount / (InvocationLatency − TimeToFirstToken) × 1000 | ✅ | docs (Bedrock CloudWatch metrics) | 2026-07-03 | guide 07, E2 Q65 |
| 14 | Hybrid search stores: Amazon RDS/Aurora (pgvector), OpenSearch Serverless, MongoDB Atlas; unsupported store → **silent** semantic fallback, no error | ✅ | docs (KB hybrid search; page says "Amazon RDS … MongoDB" — repo uses the precise product names, accepted) | 2026-07-03 | guide 02, cram-d1, E1 Q13, E2 Q18 |
| 15 | Titan Text Embeddings V2 dimensions: 256 / 512 / 1024 | ✅ | docs (Titan embeddings) | 2026-07-03 | guides 01/02 |
| 16 | Batch inference ≈50% of on-demand price; ~10 concurrent batch jobs | 🕐 | pricing page / quotas | 2026-07-03 | guide 07, cram-d2 |
| 17 | API Gateway REST default max integration timeout 29 s (raisable only for Regional/private) | ✅🕐 | docs (API GW quotas) | 2026-07-03 | guide 08, cram-d2 |
| 18 | Bedrock multi-agent collaboration: max 10 collaborators per supervisor | 🕐 | docs (multi-agent) | 2026-07-03 | guide 04, cram-d2 |
| 19 | AgentCore Runtime sessions up to 8 h | 🕐 | AgentCore docs | 2026-07-03 | guide 04, cram-d2 |
| 20 | OpenSearch Serverless vector field up to 16,000 dimensions | ⚠️🕐 | not independently confirmed this pass | 2026-07-03 | guide 02, cram-d1 |
| 21 | Prompt Flows node-type count (14) | ⚠️🕐 | fast-moving; not re-enumerated | 2026-07-03 | guide 05 |
| 22 | S3 Vectors ≈90% cheaper, sub-second query | 🕐 | AWS launch materials | 2026-07-03 | guide 02, cram-d1 |
| 23 | AWS Agent Squad relocated to `2fastlabs` org | ⚠️ | could not confirm from AWS sources (guide flags it) | 2026-07-03 | guide 04 |
| 24 | STS default ~500 AssumeRole/s per account | 🕐 | STS quotas | 2026-07-03 | guide 08, cram-d2 |
| 25 | Nova 2 Lite: SFT + RFT supported on Bedrock; RFT ~66% avg accuracy gain claim | ✅🕐 | Bedrock RFT docs + AWS blog | 2026-07-06 | website/FEASIBILITY.md |
| 26 | Customized Nova models serve via **on-demand at base-model token pricing** (PEFT models compatible with on-demand + PT) | ✅🕐 | AWS Nova customization blog/docs | 2026-07-06 | website/FEASIBILITY.md |
| 27 | Nova 2 Lite ≈ $0.30/M in, $2.50/M out; reasoning-mode TTFT ~19 s at medium vs interactive-fast defaults | 🕐 | third-party trackers + Artificial Analysis | 2026-07-06 | website/FEASIBILITY.md |

## How to re-verify (the loop)

Ask Claude Code: *"Re-verify rows N–M of VERIFICATION-LOG.md against current AWS documentation;
update statuses, dates, and any content the changes touch — then propagate per CLAUDE.md and run
`tools/consistency_check.py`."* Rows 4, 8, 20, 21, 23 are the most likely to have moved.
