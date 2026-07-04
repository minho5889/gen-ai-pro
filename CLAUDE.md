# CLAUDE.md — editing contract for this repo

Exam-prep content repo for AWS Certified Generative AI Developer – Professional (AIP-C01). All
markdown, no build. The failure mode that matters here is **silent inconsistency** — derived copies
drifting from sources, answer keys disagreeing with option tables, stale AWS facts asserted as
current. Everything below exists to prevent a recurrence.

## Source-of-truth rules

- `guides/*.md` are the source of truth for all study content; `_cram/*.md` are their condensed
  companions. There are no derived copies to keep in sync (the NotebookLM bundle was removed in
  July 2026).
- Do **not** rename the guide files to match strategy numbering — the mapping table in README.md is
  canonical, and renames would break cross-links in the exams, cram sheets, agents, and drills.

## Exam-content invariants (checker-enforced)

- Each mock exam: exactly 65 questions; domain ranges Q01–20/21–37/38–50/51–58/59–65.
- Multi-select markers `(Select TWO|THREE)` must agree across the question header, question body,
  answer-sheet header, and the analysis file's Ask line.
- In every analysis block, the ✅ letters in the Option Analysis table must equal the letters in
  `**Answer: …**`.
- Answer-key corrections are **never silent**: leave a `> Note:` block in the analysis entry saying
  what changed and why, citing the doc page.

## Facts and freshness

- Any quota, price, region list, service status, or model-specific number is a *point-in-time* fact:
  flag it inline `*(point-in-time)*` **and** add/refresh a row in `VERIFICATION-LOG.md` (claim,
  status, source, date, files).
- Never assert an AWS capability boundary ("X cannot do Y") without checking current docs first —
  two of this repo's worst historical bugs were confident absolutes that AWS had since shipped past
  (custom-model on-demand; KB resource policies).

## Before committing

Run `make check` — it mirrors CI exactly: `tools/consistency_check.py` (question counts,
select-marker agreement, option-table/answer agreement, link integrity, banned stale phrases),
ruff lint + format, prettier, `terraform validate`, the frontend build, and the backend smoke
test. Fix findings rather than suppressing them. `make fmt` auto-formats.

## Grading answer sheets

Follow `templates/AIP-C01_Performance-Analysis-Template.md` exactly and write the result to the exam
folder's `analysis/AIP-C01_Performance_Analysis.md`. All-or-nothing scoring on multi-select.
