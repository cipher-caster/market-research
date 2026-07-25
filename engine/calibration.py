#!/usr/bin/env python3
"""Calibration scoreboard stats — the deterministic side of the calibration loop.

The Scoreboard table in data/Reports/_meta/calibration.md is the compounding
record of how past calls resolved. This module parses that table into typed rows
and computes the rolling stats the spec's (docs/SPEC.md) monthly sweep calls for — per-bucket
hit rate vs implied p, the gap, the Brier score, hit rate by direction — so the
arithmetic is a script, not agent prose (the repo's rule: agents interpret, never
recompute). Same pattern as prediction_record.py: parse markdown, validate loudly.

Deliberately minimal (YAGNI): no bias lifecycle, no report scanning, no
per-sector/horizon splits until real scored data demands them.

Usage:
    python calibration.py          # markdown summary (clean empty-state, exit 0)
    python calibration.py --json    # machine-readable stats
"""
import argparse
import json
import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from prediction_record import _first_number, _table_rows

# The spec's canonical confidence -> probability map. The one source of truth.
CONF_P = {"high": 0.7, "medium": 0.55, "low": 0.4}


class ScoreRow(BaseModel):
    scored: date
    ticker: str = Field(min_length=1)
    report: str = Field(min_length=1)
    direction: Literal["buy", "hold", "avoid"]
    confidence: Literal["high", "medium", "low"]
    dir_hit: bool
    mag_hit: bool
    realized_pct: float
    event: Literal["target", "invalidation", "kill", "withdrawn", "review-matured"]

    @property
    def p(self) -> float:
        return CONF_P[self.confidence]


def _parse_conf(cell: str) -> str:
    """Parse a 'Conf (p)' cell -> canonical confidence label.

    Accepts a bare label ('high'), a bare probability ('0.7'), or 'high (0.7)'.
    A number must be one of the canonical probabilities; if both a label and a
    number are given they must agree with CONF_P, else the row is rejected.
    """
    raw = cell.strip().lower()
    label = next((lab for lab in CONF_P if lab in raw), None)
    m = re.search(r"\d(?:\.\d+)?", raw)
    num = float(m.group(0)) if m else None
    if label and num is not None and abs(CONF_P[label] - num) > 1e-9:
        raise ValueError(f"Conf (p) label and number disagree: {cell!r} "
                         f"({label} -> {CONF_P[label]}, got {num})")
    if label:
        return label
    if num is not None:
        for lab, p in CONF_P.items():
            if abs(p - num) < 1e-9:
                return lab
        raise ValueError(f"Conf (p) number is not a canonical probability: {cell!r}")
    raise ValueError(f"Conf (p) empty or unrecognized: {cell!r}")


def _yesno(cell: str) -> bool:
    v = cell.strip().lower()
    if v in ("yes", "y"):
        return True
    if v in ("no", "n"):
        return False
    raise ValueError(f"expected yes/no (or y/n), got {cell!r}")


def _realized(cell: str) -> float:
    v = _first_number(cell)  # tolerates a trailing % and a sign
    if v is None:
        raise ValueError(f"Realized % is not a number: {cell!r}")
    return v


def _scoreboard_section(text: str) -> str:
    m = re.search(r"^##\s+Scoreboard\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        raise ValueError("no '## Scoreboard' section in calibration.md")
    return m.group(1)


def parse_scoreboard(text: str) -> list[ScoreRow]:
    """Parse the Scoreboard table from calibration.md into typed rows.

    Raises ValueError (cell/parse) or pydantic.ValidationError (content) on any
    malformed row — a bad row means the calibration log violates its own schema.
    """
    rows: list[ScoreRow] = []
    for cols in _table_rows(_scoreboard_section(text)):
        if cols[0].lower() == "scored":  # header row
            continue
        if len(cols) < 9:
            raise ValueError(f"Scoreboard row has {len(cols)} cells, expected 9: {cols}")
        scored, ticker, report, direction, conf, dir_hit, mag_hit, realized, event = cols[:9]
        rows.append(ScoreRow(
            scored=date.fromisoformat(scored),
            ticker=ticker,
            report=report,
            direction=direction.lower(),  # type: ignore[arg-type]
            confidence=_parse_conf(conf),  # type: ignore[arg-type]
            dir_hit=_yesno(dir_hit),
            mag_hit=_yesno(mag_hit),
            realized_pct=_realized(realized),
            event=event.lower(),  # type: ignore[arg-type]
        ))
    return rows


def stats(rows: list[ScoreRow]) -> dict:
    """Rolling stats over parsed rows: per-bucket calibration, Brier, direction."""
    by_confidence: dict[str, dict] = {}
    for label in CONF_P:
        bucket = [r for r in rows if r.confidence == label]
        if bucket:
            rate = sum(r.dir_hit for r in bucket) / len(bucket)
            p = CONF_P[label]
            by_confidence[label] = {
                "count": len(bucket),
                "hit_rate": round(rate, 3),
                "implied_p": p,
                "gap": round(rate - p, 3),
            }

    by_direction: dict[str, dict] = {}
    for d in ("buy", "hold", "avoid"):
        bucket = [r for r in rows if r.direction == d]
        if bucket:
            by_direction[d] = {
                "count": len(bucket),
                "hit_rate": round(sum(r.dir_hit for r in bucket) / len(bucket), 3),
            }

    brier = (round(sum((r.p - r.dir_hit) ** 2 for r in rows) / len(rows), 4)
             if rows else None)
    return {"n": len(rows), "brier": brier,
            "by_confidence": by_confidence, "by_direction": by_direction}


def to_markdown(rows: list[ScoreRow]) -> str:
    s = stats(rows)
    if s["n"] == 0:
        return ("### Calibration — no scored calls yet\n\n"
                "The Scoreboard in calibration.md has no rows; nothing to score. "
                "Rows accrue as predictions mature (see the docs/SPEC.md calibration loop).")

    lines = [
        f"### Calibration — {s['n']} scored call{'s' if s['n'] != 1 else ''} "
        f"(Brier {s['brier']})",
        "",
        "**By confidence bucket** (hit rate vs implied p):",
        "",
        "| Conf | p | N | Hit rate | Gap |",
        "|---|---|---|---|---|",
    ]
    for label in CONF_P:
        b = s["by_confidence"].get(label)
        if b:
            lines.append(f"| {label} | {b['implied_p']} | {b['count']} | "
                         f"{b['hit_rate']} | {b['gap']:+} |")
    lines += ["", "**By direction** (hit rate):", "",
              "| Direction | N | Hit rate |", "|---|---|---|"]
    for d in ("buy", "hold", "avoid"):
        b = s["by_direction"].get(d)
        if b:
            lines.append(f"| {d} | {b['count']} | {b['hit_rate']} |")
    lines += ["", "Brier = mean (p − outcome)² using Dir hit as outcome. "
              "This module only computes; agents interpret."]
    return "\n".join(lines)


def main() -> None:
    from config import CALIBRATION
    p = argparse.ArgumentParser(description="Calibration scoreboard stats (deterministic)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    rows = parse_scoreboard(CALIBRATION.read_text())
    print(json.dumps(stats(rows), indent=2) if args.json else to_markdown(rows))


if __name__ == "__main__":
    main()
