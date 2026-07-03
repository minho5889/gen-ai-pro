# NotebookLM Study Bundle — AIP-C01

NotebookLM-optimized copies of the AIP-C01 study material. Content is identical to the guides in
`AIP/`, but reformatted for Google NotebookLM, which reads Markdown as plain text:

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

`_common/` holds the overall study strategy — add it to any notebook (or a separate "AIP Overview"
notebook) for cross-domain planning context.

`_all-in-one/` keeps the original single-notebook layout (all 8 guides together) if you'd rather have
one big "AIP-C01" notebook. Lower retrieval precision, but fine for broad Audio Overviews. Optionally
add `_common/00-AIP-C01-Study-Strategy.md` to it.

## How to study in NotebookLM

- **Audio Overview** for passive review (commute/walk) — its strongest feature.
- **Synthesis Q&A** — "compare prompt caching vs. semantic caching," "list every place Guardrails
  contextual grounding is discussed," "build a one-page cheat sheet for this domain."
- **Quiz me** — fine as light recall warm-ups, but for exam-representative practice use the
  fact-checked `AIP/AIP-C01-Mock-Exam-1` and `-2`, not NotebookLM quizzes.

## What NotebookLM CANNOT do here (use Claude Code instead)

- **Generate diagrams/images** — it doesn't. Diagrams come from the Mermaid in `AIP/` (or Claude Code).
- **Fact-check against current AWS docs** — it answers only from these sources and will repeat any
  staleness. For fast-moving services (AgentCore, Bedrock quotas, Knowledge Bases) confirm with
  Claude Code + the AWS docs MCP.
- **Upgrade/refresh the material** — read-only over its sources; refreshing content is the
  Claude-Code-plus-AWS-docs loop.

## Keeping this in sync

If you edit a guide in `AIP/`, regenerate its NotebookLM copy ("re-run the NotebookLM transform for
guide 0X"), then re-copy it into the affected domain folder(s) and re-upload — NotebookLM does not
auto-sync. The source of truth is always `AIP/*.md`; everything here is a derived copy.
