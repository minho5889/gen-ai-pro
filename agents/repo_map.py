"""Repo paths and the canonical guide mapping — SDK-free.

Importable by anything (agents, the Telegram bank builder, tests) without
pulling in Strands. The guide table mirrors the canonical mapping in the
root README; keep them in sync.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO_ROOT / "guides"
CRAM_DIR = REPO_ROOT / "_cram"

# Strategy-guide number -> (topic, filename).
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
