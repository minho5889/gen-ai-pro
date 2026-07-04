"""Shared model factory and repo-grounded tools for the AIP-C01 study agents.

Everything both agents know about AWS comes from THIS repo's guides and cram
sheets — the tools below are deliberately section-scoped so a local model with
a small context window never gets a 40k-word guide dumped into its prompt.
"""

import os
import re
from pathlib import Path

from strands import tool
from strands.models.ollama import OllamaModel

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO_ROOT / "guides"
CRAM_DIR = REPO_ROOT / "_cram"

# Strategy-guide number -> (topic, filename). The canonical mapping table
# lives in the root README; keep this in sync with it.
GUIDE_MAP = {
    1: ("Foundation Models & Bedrock Core", "01-Foundation-Models-Bedrock-Core.md"),
    2: ("RAG, Vector Stores & Knowledge Bases", "02-RAG-Vector-Stores-Knowledge-Bases.md"),
    3: ("Prompt Engineering & Management", "05-Prompt-Engineering-Management.md"),
    4: (
        "Agentic AI: Agents, AgentCore, Strands, MCP",
        "04-Agentic-AI-Agents-AgentCore-Strands-MCP.md",
    ),
    5: ("Enterprise Integration & Deployment", "08-Enterprise-Integration-Deployment.md"),
    6: ("AI Safety, Security & Governance", "03-AI-Safety-Security-Governance.md"),
    7: ("Cost, Performance & Monitoring", "07-Cost-Performance-Monitoring.md"),
    8: ("Testing, Evaluation & Troubleshooting", "06-Testing-Evaluation-Troubleshooting.md"),
}

MAX_SECTION_CHARS = 6000


def local_model(temperature: float = 0.7) -> OllamaModel:
    """Build the locally served Ollama model both agents run on.

    Environment overrides: ``OLLAMA_HOST`` (default http://localhost:11434)
    and ``AIP_AGENT_MODEL`` (default qwen3:8b — needs tool-calling support).

    Args:
        temperature: Sampling temperature for the agent's model.

    Returns:
        A configured Strands OllamaModel.
    """
    return OllamaModel(
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model_id=os.getenv("AIP_AGENT_MODEL", "qwen3:8b"),
        temperature=temperature,
    )


def _guide_path(file_name: str) -> Path | None:
    p = GUIDES_DIR / Path(file_name).name  # never escape guides/
    return p if p.exists() else None


@tool
def list_topics() -> str:
    """Map the study material: every guide file with its top-level sections.

    Call this first to see what exists and get exact file names and section
    headings for read_section(). Cram sheets are listed at the end.

    Returns:
        One line per guide ("Guide N — Topic [file]") with its sections
        indented beneath, then the cram-sheet file names.
    """
    out = []
    for n, (topic, fname) in GUIDE_MAP.items():
        text = (GUIDES_DIR / fname).read_text(encoding="utf-8")
        sections = re.findall(
            r"(?m)^## (?!Document Metadata|How to Use|Table of Contents)(.+)$", text
        )
        out.append(f"Guide {n} — {topic} [{fname}]")
        out.extend(f"  - {s.strip()}" for s in sections)
    out.append(
        "Cram sheets (condensed, one per exam domain): "
        + ", ".join(sorted(p.name for p in CRAM_DIR.glob("cram-d*.md")))
    )
    return "\n".join(out)


@tool
def read_section(file_name: str, heading: str) -> str:
    """Read ONE section of a guide or cram sheet by its heading text.

    Args:
        file_name: Exact file name from list_topics, e.g.
            '02-RAG-Vector-Stores-Knowledge-Bases.md' or 'cram-d1.md'.
        heading: The section title, with or without the leading ##.

    Returns:
        That section's text only (truncated if very long) — ask for another
        section if you need more. On a miss, an ERROR line listing the
        available headings.
    """
    path = _guide_path(file_name) or (
        CRAM_DIR / Path(file_name).name if (CRAM_DIR / Path(file_name).name).exists() else None
    )
    if path is None:
        return f"ERROR: no such file '{file_name}'. Use list_topics() for exact names."
    text = path.read_text(encoding="utf-8")
    want = heading.lstrip("#").strip().lower()
    matches = list(re.finditer(r"(?m)^(#{2,3}) (.+)$", text))
    for i, m in enumerate(matches):
        if want in m.group(2).strip().lower():
            level = len(m.group(1))
            end = len(text)
            for nxt in matches[i + 1 :]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            body = text[m.start() : end].strip()
            if len(body) > MAX_SECTION_CHARS:
                body = (
                    body[:MAX_SECTION_CHARS] + "\n[...section truncated — ask for a subsection...]"
                )
            return body
    heads = "\n".join(f"  {m.group(1)} {m.group(2)}" for m in matches[:40])
    return f"ERROR: heading '{heading}' not found in {path.name}. Available headings:\n{heads}"


@tool
def search_guides(query: str) -> str:
    """Search all guides and cram sheets, case-insensitively.

    Use a short, specific query (a service or concept name), then pick which
    section to read_section() next.

    Args:
        query: Substring to search for (minimum 3 characters).

    Returns:
        Up to 12 hits as 'file :: section :: matching line', or an ERROR/no-match line.
    """
    q = query.strip().lower()
    if len(q) < 3:
        return "ERROR: query too short."
    hits = []
    files = [GUIDES_DIR / f for _, f in GUIDE_MAP.values()] + sorted(CRAM_DIR.glob("cram-d*.md"))
    for path in files:
        section = "(top)"
        for line in path.read_text(encoding="utf-8").splitlines():
            hm = re.match(r"^(#{2,3}) (.+)$", line)
            if hm:
                section = hm.group(2).strip()
                continue
            if q in line.lower():
                hits.append(f"{path.name} :: {section} :: {line.strip()[:160]}")
                if len(hits) >= 12:
                    return "\n".join(hits)
    return "\n".join(hits) if hits else f"No matches for '{query}'."
