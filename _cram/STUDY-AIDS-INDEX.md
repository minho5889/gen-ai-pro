# AIP-C01 Study Aids — Index

Everything you need to study for the AWS Certified Generative AI Developer – Professional (AIP-C01)
exam, organized by how you'd use it. The certification is real (verified against the AWS catalog):
$300, 75 questions (65 scored + 10 unscored), 180 min, 750/1000 to pass, professional level.

## 1. Learn it — the deep-dive guides (`AIP/0*.md`)

Eight textbook-depth guides, one per study block. Read in the recommended order (see
`00-AIP-C01-Study-Strategy.md`). Accuracy fact-checked against live AWS docs.

| Strategy Guide | File |
|---|---|
| 01 Foundation Models & Bedrock Core | `01-Foundation-Models-Bedrock-Core.md` |
| 02 RAG, Vector Stores & Knowledge Bases | `02-RAG-Vector-Stores-Knowledge-Bases.md` |
| 03 Prompt Engineering & Management | `05-Prompt-Engineering-Management.md` |
| 04 Agentic AI: Agents, AgentCore, Strands, MCP | `04-Agentic-AI-Agents-AgentCore-Strands-MCP.md` |
| 05 Enterprise Integration & Deployment | `08-Enterprise-Integration-Deployment.md` |
| 06 AI Safety, Security & Governance | `03-AI-Safety-Security-Governance.md` |
| 07 Cost, Performance & Monitoring | `07-Cost-Performance-Monitoring.md` |
| 08 Testing, Evaluation & Troubleshooting | `06-Testing-Evaluation-Troubleshooting.md` |

Each guide ends with a **Multiple-Response Knowledge Check** matching the real exam's select-TWO/THREE format.

## 2. Review it — cram sheets (`AIP/_cram/`)

One condensed, scannable quick-reference per domain — the **night-before track** the dense guides lack.
Distilled "If the exam says X → answer Y → why" tables, top traps, decision rules, and hard numbers.

- `cram-d1.md` … `cram-d5.md` (one per exam domain)

## 3. Listen to it / synthesize — NotebookLM bundle (`AIP/_notebooklm/`)

A NotebookLM-optimized copy of all guides (diagrams converted to prose, quizzes flattened). Upload
the 9 files to a NotebookLM notebook for Audio Overviews and cross-guide synthesis Q&A. See
`_notebooklm/README.md` for setup and the important "answers only from sources" caveat.

## 4. Test it — practice exam (`AIP/AIP-C01-Mock-Exam-1/`)

A full 65-question, domain-weighted mock exam with answer keys **fact-checked against AWS docs**,
wired into the drill → answer-sheet → performance-analyzer pipeline. See its `README.md`. Ask Claude
Code for "Practice Exam 2" when you want fresh reps.

## Suggested study loop

1. Read a guide → 2. drill its Knowledge Checks → 3. skim the matching cram sheet → 4. (passive)
listen to the NotebookLM Audio Overview → 5. after a few guides, sit a slice of the practice exam and
run the performance analyzer → 6. let the weak-topic output point you back to the right guide/cram sheet.

## Maintenance

- `scripts/lint_generation_artifacts.py` (or the *Lint Generation Artifacts* Kiro hook) guards against
  LLM scaffolding leaking into any deliverable — run it before trusting newly generated material.
- Fast-moving facts (Bedrock quotas, AgentCore components, model availability) drift; re-verify with
  Claude Code + the AWS docs MCP before relying on a specific number close to exam day.
