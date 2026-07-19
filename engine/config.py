#!/usr/bin/env python3
"""Data-layer paths — the one place the engine learns where the data lives.

Code and data live in the same repo now: engine/ (code) and data/ (Trade-Log,
Research, Reports). This module resolves the data directory repo-relative, so
nothing else hardcodes a path. Override with the DATA_DIR env var only for
testing against a different data tree.
"""
import os
from pathlib import Path

_raw = os.environ.get("DATA_DIR", "").strip()
DATA = Path(_raw).expanduser() if _raw else Path(__file__).resolve().parent.parent / "data"
if not DATA.is_dir():
    raise SystemExit(
        f"Data directory not found: {DATA}\n"
        "Expected the repo's data/ folder (Trade-Log.md, Research/, Reports/), "
        "or set DATA_DIR to point elsewhere."
    )

# Kept name: the investments data layer (knowledge, not code).
INVESTMENTS = DATA
TRADE_LOG = INVESTMENTS / "Trade-Log.md"
REPORTS = INVESTMENTS / "Reports"
LEVEL_WATCH = REPORTS / "_meta" / "Level-Watch.md"
