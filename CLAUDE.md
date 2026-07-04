# CLAUDE.md — editing contract for this repo

Exam-prep content repo for AWS Certified Generative AI Developer – Professional (AIP-C01). All
markdown, no build. The failure mode that matters here is **silent inconsistency** — derived copies
drifting from sources, answer keys disagreeing with option tables, stale AWS facts asserted as
current. Everything below exists to prevent a recurrence.

## Source-of-truth and propagation rules

- `guides/*.md` are the source of truth. `_notebooklm/by-domain/*/` holds **derived, transformed
  copies** (Mermaid diagrams rewritten as "Diagram (described)" prose; `<details>` quizzes flattened
  to Q:/A:). After editing a guide, apply the equivalent edit to its by-domain copy (or regenerate
  the transform). Guide→folder map: 01→d1 **and** d2 · 02→d1 · 03→d3 · 04→d2 · 05→d1 · 06→d5 ·
  07→d4 · 08→d2.
- `_cram/cram-dN.md` and `AIP-C01-Exam-Blueprint.md` are copied **byte-identical** into by-domain
  folders (blueprint into all five). After editing, `cp` them over; the checker diffs them.
- Do **not** rename the guide files to match strategy numbering — the mapping table in README.md is
  canonical; renames would break NotebookLM notebooks users already uploaded and every cross-link.

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

Run `python3 tools/consistency_check.py` (CI runs it too). It checks: question counts,
select-marker agreement, option-table/answer agreement, relative-link integrity, identical-copy
invariants, and banned stale phrases. Fix findings rather than suppressing them.

## Grading answer sheets

Follow `templates/AIP-C01_Performance-Analysis-Template.md` exactly and write the result to the exam
folder's `analysis/AIP-C01_Performance_Analysis.md`. All-or-nothing scoring on multi-select.
