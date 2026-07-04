# gen-ai-pro

Study materials for the **AWS Certified Generative AI Developer – Professional (AIP-C01)** exam.
The certification is real (verified against the AWS catalog and the official exam guide PDF v1.0):
75 questions (65 scored + 10 unscored), 180 minutes, scaled 100–1000 with 750 to pass, compensatory
scoring, professional level. Four question types: multiple choice, multiple response, ordering, and
matching.

## How to use this repo

1. **Plan** — read [00-AIP-C01-Study-Strategy.md](00-AIP-C01-Study-Strategy.md) (readiness by domain,
   priorities, mental models) against the verified task list in
   [AIP-C01-Exam-Blueprint.md](AIP-C01-Exam-Blueprint.md).
2. **Learn** — work through the guides in the recommended order; drill each guide's Knowledge Checks.
3. **Review** — skim the matching cram sheet; (optional) listen via the NotebookLM bundle.
4. **Test** — sit the mock exams, drill the ordering/matching formats, and grade yourself with the
   performance-analysis template.
5. **Before exam day** — re-verify the fast-moving facts listed in
   [VERIFICATION-LOG.md](VERIFICATION-LOG.md).

## Learn it — the deep-dive guides ([guides/](guides/))

Eight textbook-depth guides, fact-checked against live AWS docs (last full audit: July 2026). Build
order diverged from strategy numbering, so the mapping is:

| Strategy Guide | Topic | File |
|---|---|---|
| 01 | Foundation Models & Bedrock Core | [guides/01-Foundation-Models-Bedrock-Core.md](guides/01-Foundation-Models-Bedrock-Core.md) |
| 02 | RAG, Vector Stores & Knowledge Bases | [guides/02-RAG-Vector-Stores-Knowledge-Bases.md](guides/02-RAG-Vector-Stores-Knowledge-Bases.md) |
| 03 | Prompt Engineering & Management | [guides/05-Prompt-Engineering-Management.md](guides/05-Prompt-Engineering-Management.md) |
| 04 | Agentic AI: Agents, AgentCore, Strands, MCP | [guides/04-Agentic-AI-Agents-AgentCore-Strands-MCP.md](guides/04-Agentic-AI-Agents-AgentCore-Strands-MCP.md) |
| 05 | Enterprise Integration & Deployment | [guides/08-Enterprise-Integration-Deployment.md](guides/08-Enterprise-Integration-Deployment.md) |
| 06 | AI Safety, Security & Governance | [guides/03-AI-Safety-Security-Governance.md](guides/03-AI-Safety-Security-Governance.md) |
| 07 | Cost, Performance & Monitoring | [guides/07-Cost-Performance-Monitoring.md](guides/07-Cost-Performance-Monitoring.md) |
| 08 | Testing, Evaluation & Troubleshooting | [guides/06-Testing-Evaluation-Troubleshooting.md](guides/06-Testing-Evaluation-Troubleshooting.md) |

Recommended order: 01 → 02 → 06 → 04 → 03 → 08 → 07 → 05 (front-loads Domain 1 plus
Guardrails/Responsible AI). Every guide has Mermaid diagrams, comparison tables, per-section
Exam-Relevant Distinctions checklists, and collapsible Knowledge Checks including multiple-response
items.

## Review it — cram sheets ([_cram/](_cram/))

One condensed quick-reference per exam domain — the night-before track: "if the exam says X → answer
Y → why" tables, top traps, decision rules, hard numbers. `cram-d1.md` … `cram-d5.md`.

## Listen to it — NotebookLM bundle ([_notebooklm/](_notebooklm/))

NotebookLM-optimized copies of the guides (diagrams described in prose, quizzes flattened), split
into one folder per domain for focused notebooks. See
[_notebooklm/README.md](_notebooklm/README.md) for the per-domain layout, what NotebookLM can and
cannot do here, and the sync rule.

## Test it — mock exams and format drills

- [AIP-C01-Mock-Exam-1/](AIP-C01-Mock-Exam-1/) and [AIP-C01-Mock-Exam-2/](AIP-C01-Mock-Exam-2/) —
  two full 65-question, domain-weighted mock exams with fact-checked answer keys and per-question
  analysis. Each folder's README explains the drill → answer-sheet → performance-analysis loop.
- [AIP-C01-Format-Drills/](AIP-C01-Format-Drills/Ordering-Matching-Drills.md) — 14 drills for the
  ordering and matching formats the mock exams don't cover.
- [templates/AIP-C01_Performance-Analysis-Template.md](templates/AIP-C01_Performance-Analysis-Template.md)
  — the output spec used when grading an answer sheet, so runs are comparable across exams and
  attempts.

## Suggested study loop

Read a guide → drill its Knowledge Checks → skim the matching cram sheet → (passive) NotebookLM Audio
Overview → after a few guides, sit a mock-exam slice and grade it with the template → let the
weak-topic output point you back to the right guide/cram sheet → mix in format drills near the end.

## Maintenance rules

- [guides/](guides/) are the **source of truth**. After editing a guide, regenerate its NotebookLM
  copy and re-copy it into the affected `by-domain/` folder(s) — copies do not auto-sync. See
  [CLAUDE.md](CLAUDE.md) for the full editing contract.
- Every fast-moving fact carries a *(point-in-time)* flag in the text and a row in
  [VERIFICATION-LOG.md](VERIFICATION-LOG.md) with its source and last-verified date. Re-verify before
  relying on a number near exam day.
- Run `python3 tools/consistency_check.py` before committing — it enforces the repo's invariants
  (select-marker consistency, answer-key/table agreement, link integrity, copy sync, banned stale
  claims). CI runs it on every push.
- Answer-key corrections stay visible as `> Note:` blocks in the analysis files rather than being
  silently rewritten.
