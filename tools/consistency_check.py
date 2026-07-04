#!/usr/bin/env python3
"""Consistency checker for the gen-ai-pro AIP-C01 study repo.

Enforces the invariants in CLAUDE.md. Exit 0 = all green; exit 1 = findings
(printed one per line, prefixed FAIL). Stdlib only. Run from the repo root.
"""
import os
import re
import sys

FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print(f"FAIL: {msg}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def md_files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in {".git", ".claude", ".github", "tools"}]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(root, f)


EXAMS = {
    "1": "AIP-C01-Mock-Exam-1",
    "2": "AIP-C01-Mock-Exam-2",
}
HEADER_RE = re.compile(r"^## Question (\d+)(?: \(Select (TWO|THREE)\))?\s*$", re.M)
ANSWER_RE = re.compile(r"\*\*Answer:\s*([A-F][A-F ,]*?)\*\*")


def headers(path):
    return {int(n): sel for n, sel in HEADER_RE.findall(read(path))}


def check_question_counts_and_markers():
    for n, folder in EXAMS.items():
        qpath = f"{folder}/questions/AIP-C01-Mock-Exam-{n}-Questions.md"
        spath = f"{folder}/AIP-C01-Mock-Exam-{n}_AnswerSheet.md"
        qh, sh = headers(qpath), headers(spath)
        if len(qh) != 65:
            fail(f"{qpath}: expected 65 questions, found {len(qh)}")
        for qn in sorted(set(qh) | set(sh)):
            if qh.get(qn) != sh.get(qn):
                fail(f"Exam {n} Q{qn}: marker mismatch questions={qh.get(qn)} sheet={sh.get(qn)}")
        # body text must agree with the header marker
        content = read(qpath)
        for block in re.split(r"(?m)(?=^## Question \d+)", content):
            m = re.match(r"## Question (\d+)(?: \(Select (TWO|THREE)\))?", block)
            if not m:
                continue
            body_sels = set(re.findall(r"\(Select (TWO|THREE)[.)]", block[m.end():]))
            hdr = m.group(2)
            if hdr and body_sels and body_sels != {hdr}:
                fail(f"Exam {n} Q{m.group(1)}: header says {hdr}, body says {body_sels}")
            if not hdr and body_sels:
                fail(f"Exam {n} Q{m.group(1)}: body has Select marker but header does not")


def check_option_tables():
    for n, folder in EXAMS.items():
        adir = f"{folder}/analysis"
        afiles = sorted(f for f in os.listdir(adir) if re.match(r"AIP-C01_Q\d+-Q\d+_Analysis\.md$", f))
        if len(afiles) != 13:
            fail(f"{adir}: expected 13 analysis files, found {len(afiles)}")
        for af in afiles:
            content = read(os.path.join(adir, af))
            for block in re.split(r"(?m)(?=^## Question \d+)", content):
                qm = re.match(r"## Question (\d+)", block)
                am = ANSWER_RE.search(block)
                if not (qm and am):
                    continue
                letters = set(re.findall(r"[A-F]", am.group(1)))
                checked = set(re.findall(r"(?m)^- \*\*([A-F])\*\* ✅", block))
                if checked != letters:
                    fail(f"Exam {n} {af} Q{qm.group(1)}: answer={sorted(letters)} but ✅={sorted(checked)}")


def check_links():
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in md_files():
        for target in link_re.findall(read(path)):
            if target.startswith(("http", "#", "mailto:")):
                continue
            rel = target.split("#")[0]
            if rel and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), rel))):
                fail(f"{path}: broken link -> {target}")


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


def check_banned_strings():
    for path in md_files():
        for i, line in enumerate(read(path).splitlines(), 1):
            if line.lstrip().startswith(">"):
                continue  # correction notes may quote retired claims
            for b in BANNED:
                if b in line:
                    fail(f"{path}:{i}: banned stale string {b!r}")


IDENTICAL = [
    ("_cram/cram-d1.md", "_notebooklm/by-domain/d1-foundation-data-compliance/cram-d1.md"),
    ("_cram/cram-d2.md", "_notebooklm/by-domain/d2-implementation-integration/cram-d2.md"),
    ("_cram/cram-d3.md", "_notebooklm/by-domain/d3-safety-security-governance/cram-d3.md"),
    ("_cram/cram-d4.md", "_notebooklm/by-domain/d4-operational-efficiency/cram-d4.md"),
    ("_cram/cram-d5.md", "_notebooklm/by-domain/d5-testing-validation-troubleshooting/cram-d5.md"),
] + [
    ("AIP-C01-Exam-Blueprint.md", f"_notebooklm/by-domain/{d}/AIP-C01-Exam-Blueprint.md")
    for d in [
        "d1-foundation-data-compliance",
        "d2-implementation-integration",
        "d3-safety-security-governance",
        "d4-operational-efficiency",
        "d5-testing-validation-troubleshooting",
    ]
]


def check_identical_copies():
    for src, copy in IDENTICAL:
        if not os.path.exists(copy):
            fail(f"missing copy: {copy}")
        elif read(src) != read(copy):
            fail(f"copy drifted from source: {copy} != {src}")


# Every guide edit must reach its transformed by-domain copies. Transforms
# preclude a byte-diff, so enforce presence + a same-section-count heuristic.
GUIDE_COPIES = {
    "guides/01-Foundation-Models-Bedrock-Core.md": [
        "_notebooklm/by-domain/d1-foundation-data-compliance/01-Foundation-Models-Bedrock-Core.md",
        "_notebooklm/by-domain/d2-implementation-integration/01-Foundation-Models-Bedrock-Core.md",
    ],
    "guides/02-RAG-Vector-Stores-Knowledge-Bases.md": [
        "_notebooklm/by-domain/d1-foundation-data-compliance/02-RAG-Vector-Stores-Knowledge-Bases.md",
    ],
    "guides/03-AI-Safety-Security-Governance.md": [
        "_notebooklm/by-domain/d3-safety-security-governance/03-AI-Safety-Security-Governance.md",
    ],
    "guides/04-Agentic-AI-Agents-AgentCore-Strands-MCP.md": [
        "_notebooklm/by-domain/d2-implementation-integration/04-Agentic-AI-Agents-AgentCore-Strands-MCP.md",
    ],
    "guides/05-Prompt-Engineering-Management.md": [
        "_notebooklm/by-domain/d1-foundation-data-compliance/05-Prompt-Engineering-Management.md",
    ],
    "guides/06-Testing-Evaluation-Troubleshooting.md": [
        "_notebooklm/by-domain/d5-testing-validation-troubleshooting/06-Testing-Evaluation-Troubleshooting.md",
    ],
    "guides/07-Cost-Performance-Monitoring.md": [
        "_notebooklm/by-domain/d4-operational-efficiency/07-Cost-Performance-Monitoring.md",
    ],
    "guides/08-Enterprise-Integration-Deployment.md": [
        "_notebooklm/by-domain/d2-implementation-integration/08-Enterprise-Integration-Deployment.md",
    ],
}


def check_guide_copies():
    for src, copies in GUIDE_COPIES.items():
        src_sections = re.findall(r"(?m)^## Section \d+", read(src))
        for copy in copies:
            if not os.path.exists(copy):
                fail(f"missing transformed copy: {copy}")
                continue
            copy_sections = re.findall(r"(?m)^## Section \d+", read(copy))
            if len(src_sections) != len(copy_sections):
                fail(f"{copy}: section count {len(copy_sections)} != source {len(src_sections)}")


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    check_question_counts_and_markers()
    check_option_tables()
    check_links()
    check_banned_strings()
    check_identical_copies()
    check_guide_copies()
    if FAILURES:
        print(f"\n{len(FAILURES)} finding(s).")
        sys.exit(1)
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
