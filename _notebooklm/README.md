# NotebookLM Study Bundle — AIP-C01

NotebookLM-optimized copies of the AIP-C01 study material. Content is identical to the guides in
`../guides/`, but reformatted for Google NotebookLM, which reads Markdown as plain text:

- **Mermaid diagrams → prose.** Every diagram is rewritten as a "**Diagram (described):**" paragraph
  so Audio Overview can read it aloud and chat can reason over it. (Originals render as meaningless
  code in NotebookLM, and NotebookLM does not generate diagrams of its own.)
- **Collapsible quizzes → Q:/A: pairs.** The `<details>` Knowledge Checks are flattened.
- **File-numbering meta-notes trimmed.**

## Layout — upload ONE folder per notebook (recommended)

NotebookLM's retrieval, quiz, and synthesis quality are better with **focused** notebooks than with
one giant blob. So this bundle is split by exam domain. Create one NotebookLM notebook per domain and
upload the contents of the matching folder:

| Notebook | Folder | Weight | Sources inside |
|---|---|---|---|
| AIP D1 — FM Integration, Data, Compliance | `by-domain/d1-foundation-data-compliance/` | 31% | guides 01, 02, 05 + cram-d1 + blueprint |
| AIP D2 — Implementation & Integration | `by-domain/d2-implementation-integration/` | 26% | guides 04, 08, 01 + cram-d2 + blueprint |
| AIP D3 — Safety, Security, Governance | `by-domain/d3-safety-security-governance/` | 20% | guide 03 + cram-d3 + blueprint |
| AIP D4 — Operational Efficiency | `by-domain/d4-operational-efficiency/` | 12% | guide 07 + cram-d4 + blueprint |
| AIP D5 — Testing, Validation, Troubleshooting | `by-domain/d5-testing-validation-troubleshooting/` | 11% | guide 06 + cram-d5 + blueprint |

Notes on the split:
- **Guide 01 (Foundation Models) appears in both D1 and D2** because D2's tasks 2.2/2.4 (model
  deployment, FM API integration) build on it and Guide 04 leans on it.
- The **exam blueprint is included in every domain folder** so each notebook is self-contained and
  grounded in the authoritative task list.
- Each domain folder bundles the matching **cram sheet** — the densest, highest-signal source for
  NotebookLM's quiz/flashcard generation.

Want cross-domain planning context in a notebook? Also upload the root
`00-AIP-C01-Study-Strategy.md` alongside any domain folder's files.

> The former `_all-in-one/` and `_common/` folders were removed in July 2026: they duplicated every
> transformed guide byte-for-byte and doubled the copy-sync surface for zero unique content. If you
> want one big notebook anyway, upload each transformed guide once from across the `by-domain/`
> folders (skip the duplicate blueprint copies).

## How to study in NotebookLM

- **Audio Overview** for passive review (commute/walk) — its strongest feature.
- **Synthesis Q&A** — "compare prompt caching vs. semantic caching," "list every place Guardrails
  contextual grounding is discussed," "build a one-page cheat sheet for this domain."
- **Quiz me** — fine as light recall warm-ups, but for exam-representative practice use the
  fact-checked `../AIP-C01-Mock-Exam-1` and `-2` (plus `../AIP-C01-Format-Drills/` for
  ordering/matching), not NotebookLM quizzes.

## What NotebookLM CANNOT do here (use Claude Code instead)

- **Generate diagrams/images** — it doesn't. Diagrams come from the Mermaid in `../guides/` (or Claude Code).
- **Fact-check against current AWS docs** — it answers only from these sources and will repeat any
  staleness. For fast-moving services (AgentCore, Bedrock quotas, Knowledge Bases) confirm with
  Claude Code + the AWS docs MCP.
- **Upgrade/refresh the material** — read-only over its sources; refreshing content is the
  Claude-Code-plus-AWS-docs loop.

## Keeping this in sync

If you edit a guide in `../guides/`, regenerate its NotebookLM copy ("re-run the NotebookLM transform
for guide 0X"), re-copy it into the affected domain folder(s) (guide 01 lives in both d1 and d2), and
re-upload — NotebookLM does not auto-sync. The source of truth is always `../guides/*.md`; everything
here is a derived copy. Run `python3 tools/consistency_check.py` from the repo root after any edit —
it verifies the identical-copy invariants (cram sheets, blueprint) and the repo's other consistency
rules.
