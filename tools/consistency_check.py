#!/usr/bin/env python3
"""Consistency checker for the gen-ai-pro AIP-C01 study repo.

Enforces the invariants in CLAUDE.md. Exit 0 = all green; exit 1 = findings
(printed one per line, prefixed FAIL). Stdlib only. Run from the repo root.

Architecture: functional core / imperative shell. Core functions take file
*contents* and return finding strings — unit-tested with synthetic content in
``tests/test_consistency_check.py``. The shell walks the repo, feeds the core,
and reports.
"""

import os
import re
import sys

EXAMS = {
    "1": "AIP-C01-Mock-Exam-1",
    "2": "AIP-C01-Mock-Exam-2",
}
HEADER_RE = re.compile(r"^## Question (\d+)(?: \(Select (TWO|THREE)\))?\s*$", re.M)
ANSWER_RE = re.compile(r"\*\*Answer:\s*([A-F][A-F ,]*?)\*\*")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Stale claims and dead references that past audits removed. Lines quoting them
# for historical honesty (correction "> Note:" blocks) are exempt.
BANNED = [
    "drill-performance-analyzer",
    ".kiro/steering",
    "lint_generation_artifacts",
    "Certified AI Practitioner",
    "Task Task",
    "0.1 RPS",
    "0.1 requests per second",
    "5 concurrent jobs per account",
    "cannot be invoked on-demand",
    "can only be invoked through Provisioned Throughput",
    "Multiple choice (1 of 4) and multiple response",
]

SKIP_DIRS = {
    ".git",
    ".claude",
    ".github",
    "tools",
    "node_modules",
    "dist",
    "out",
    ".terraform",
    ".build",
    "__pycache__",
}

# --------------------------- functional core ---------------------------------


def _headers(text: str) -> dict[int, str | None]:
    """Map question number to its Select marker (or None) from headers."""
    return {int(n): sel or None for n, sel in HEADER_RE.findall(text)}


def marker_findings(exam_no: str, questions_text: str, sheet_text: str) -> list[str]:
    """Check question counts and Select-marker agreement for one exam.

    Verifies 65 questions exist, the questions file and answer sheet carry
    identical ``(Select TWO|THREE)`` markers, and each question's body text
    agrees with its own header.

    Args:
        exam_no: Exam number as a string ("1" or "2"), used in messages.
        questions_text: Full questions-file markdown.
        sheet_text: Full answer-sheet markdown.

    Returns:
        Finding strings; empty when consistent.
    """
    findings = []
    qh, sh = _headers(questions_text), _headers(sheet_text)
    if len(qh) != 65:
        findings.append(f"Exam {exam_no} questions: expected 65 questions, found {len(qh)}")
    for qn in sorted(set(qh) | set(sh)):
        if qh.get(qn) != sh.get(qn):
            findings.append(
                f"Exam {exam_no} Q{qn}: marker mismatch questions={qh.get(qn)} sheet={sh.get(qn)}"
            )
    for block in re.split(r"(?m)(?=^## Question \d+)", questions_text):
        m = re.match(r"## Question (\d+)(?: \(Select (TWO|THREE)\))?", block)
        if not m:
            continue
        body_sels = set(re.findall(r"\(Select (TWO|THREE)[.)]", block[m.end() :]))
        hdr = m.group(2)
        if hdr and body_sels and body_sels != {hdr}:
            findings.append(
                f"Exam {exam_no} Q{m.group(1)}: header says {hdr}, body says {body_sels}"
            )
        if not hdr and body_sels:
            findings.append(
                f"Exam {exam_no} Q{m.group(1)}: body has Select marker but header does not"
            )
    return findings


def table_findings(exam_no: str, analysis_files: dict[str, str]) -> list[str]:
    """Check that every option table's checkmarks match its answer key.

    Args:
        exam_no: Exam number as a string, used in messages.
        analysis_files: Analysis file name -> markdown content (13 expected).

    Returns:
        Finding strings; empty when consistent.
    """
    findings = []
    if len(analysis_files) != 13:
        findings.append(
            f"Exam {exam_no} analysis: expected 13 analysis files, found {len(analysis_files)}"
        )
    for af, content in sorted(analysis_files.items()):
        for block in re.split(r"(?m)(?=^## Question \d+)", content):
            qm = re.match(r"## Question (\d+)", block)
            am = ANSWER_RE.search(block)
            if not (qm and am):
                continue
            letters = set(re.findall(r"[A-F]", am.group(1)))
            checked = set(re.findall(r"(?m)^- \*\*([A-F])\*\* ✅", block))
            if checked != letters:
                findings.append(
                    f"Exam {exam_no} {af} Q{qm.group(1)}: "
                    f"answer={sorted(letters)} but ✅={sorted(checked)}"
                )
    return findings


def link_refs(md_contents: dict[str, str]) -> list[tuple[str, str, str]]:
    """Extract relative link targets from markdown files.

    Args:
        md_contents: Path -> markdown content.

    Returns:
        ``(source_path, raw_target, resolved_path)`` for every relative link;
        http/anchor/mailto links are skipped. Existence is the shell's job.
    """
    refs = []
    for path, content in md_contents.items():
        for target in LINK_RE.findall(content):
            if target.startswith(("http", "#", "mailto:")):
                continue
            rel = target.split("#")[0]
            if rel:
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), rel))
                refs.append((path, target, resolved))
    return refs


def banned_findings(md_contents: dict[str, str]) -> list[str]:
    """Flag banned stale strings outside quoted correction notes.

    Args:
        md_contents: Path -> markdown content.

    Returns:
        Finding strings with path and line number.
    """
    findings = []
    for path, content in md_contents.items():
        for i, line in enumerate(content.splitlines(), 1):
            if line.lstrip().startswith(">"):
                continue  # correction notes may quote retired claims
            for b in BANNED:
                if b in line:
                    findings.append(f"{path}:{i}: banned stale string {b!r}")
    return findings


# --------------------------- imperative shell --------------------------------


def load_md_contents() -> dict[str, str]:
    """Read every tracked-tree markdown file outside SKIP_DIRS."""
    contents = {}
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as fh:
                    contents[path] = fh.read()
    return contents


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main() -> None:
    """Run every check against the repo and exit non-zero on findings."""
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    findings = []

    for n, folder in EXAMS.items():
        questions = _read(f"{folder}/questions/AIP-C01-Mock-Exam-{n}-Questions.md")
        sheet = _read(f"{folder}/AIP-C01-Mock-Exam-{n}_AnswerSheet.md")
        findings += marker_findings(n, questions, sheet)
        adir = f"{folder}/analysis"
        analysis = {
            f: _read(os.path.join(adir, f))
            for f in os.listdir(adir)
            if re.match(r"AIP-C01_Q\d+-Q\d+_Analysis\.md$", f)
        }
        findings += table_findings(n, analysis)

    md = load_md_contents()
    findings += [
        f"{src}: broken link -> {target}"
        for src, target, resolved in link_refs(md)
        if not os.path.exists(resolved)
    ]
    findings += banned_findings(md)

    for f in findings:
        print(f"FAIL: {f}")
    if findings:
        print(f"\n{len(findings)} finding(s).")
        sys.exit(1)
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
