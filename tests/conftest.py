"""Make the functional cores importable without packaging ceremony."""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in ("tools", "website/scripts"):
    sys.path.insert(0, os.path.join(REPO, rel))

# app.py reads its env at import time; give it test values before any import.
os.environ.setdefault("KB_ID", "KB-TEST")
os.environ.setdefault("MODEL_ID", "test-model")
sys.modules.setdefault("boto3", __import__("types").ModuleType("boto3"))
sys.modules["boto3"].client = lambda *a, **k: None  # core tests never call AWS
sys.path.insert(0, os.path.join(REPO, "website/backend"))
sys.path.insert(0, os.path.join(REPO, "website/telegram"))
