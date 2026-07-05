"""Mock-exam and Knowledge Check parsers — pure, SDK-free.

The audited parsers over the repo's exam content, importable without Strands
(used by the verifier agent, the Telegram bank builder, and tests).
"""

import re

from repo_map import GUIDE_MAP, GUIDES_DIR, REPO_ROOT

DOMAIN_RANGES = {1: (1, 20), 2: (21, 37), 3: (38, 50), 4: (51, 58), 5: (59, 65)}
DOMAIN_NAMES = {
    1: "FM Integration, Data, Compliance",
    2: "Implementation & Integration",
    3: "Safety, Security, Governance",
    4: "Operational Efficiency",
    5: "Testing, Validation, Troubleshooting",
}


def parse_exam(exam_no: str) -> list[dict]:
    """Parse one mock exam into question records with audited answer keys.

    Args:
        exam_no: "1" or "2" — selects the mock-exam folder.

    Returns:
        Question dicts (num/multi/text/key/analysis); only questions whose
        answer key was found in the analysis files are included.
    """
    folder = REPO_ROOT / f"AIP-C01-Mock-Exam-{exam_no}"
    qtext = (folder / "questions" / f"AIP-C01-Mock-Exam-{exam_no}-Questions.md").read_text(
        encoding="utf-8"
    )
    questions = {}
    for block in re.split(r"(?m)(?=^## Question \d+)", qtext):
        m = re.match(r"## Question (\d+)( \(Select (TWO|THREE)\))?", block)
        if m:
            questions[int(m.group(1))] = {
                "exam": exam_no,
                "num": int(m.group(1)),
                "multi": m.group(3),
                "text": block.split("\n---", 1)[0].strip(),
            }
    for afile in sorted((folder / "analysis").glob("AIP-C01_Q*_Analysis.md")):
        for block in re.split(r"(?m)(?=^## Question \d+)", afile.read_text(encoding="utf-8")):
            qm = re.match(r"## Question (\d+)", block)
            am = re.search(r"\*\*Answer:\s*([A-F][A-F ,]*?)\*\*", block)
            if qm and am and int(qm.group(1)) in questions:
                q = questions[int(qm.group(1))]
                q["key"] = frozenset(re.findall(r"[A-F]", am.group(1)))
                q["analysis"] = block.split("\n---", 1)[0].strip()
    return [q for q in questions.values() if "key" in q]


def domain_of(qnum: int) -> int:
    """Map a question number to its exam domain via the blueprint ranges.

    Args:
        qnum: Question number (1-65).

    Returns:
        Domain number 1-5.
    """
    return next(d for d, (lo, hi) in DOMAIN_RANGES.items() if lo <= qnum <= hi)


def parse_knowledge_checks(strategy_no: int) -> list[dict]:
    """Extract a guide's Knowledge Check Q&A blocks.

    Args:
        strategy_no: Strategy-guide number (1-8) from GUIDE_MAP.

    Returns:
        Dicts with ``question`` (the summary line) and ``answer`` (the hidden
        block, used as judging ground truth).
    """
    _, fname = GUIDE_MAP[strategy_no]
    text = (GUIDES_DIR / fname).read_text(encoding="utf-8")
    kcs = []
    for m in re.finditer(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", text, re.S):
        question, hidden = m.group(1).strip(), m.group(2).strip()
        if "**Answer" in hidden or "**A:" in hidden:
            kcs.append({"question": question, "answer": hidden})
    return kcs
