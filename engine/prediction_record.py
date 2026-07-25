#!/usr/bin/env python3
"""Prediction Record schema + parser — the machine-readable contract of a report.

Reports stay markdown (canonical, human-first). This module parses the mandatory
fields out of a report's Prediction Record and validates them with pydantic, so
the calibration loop scores typed fields instead of regexing prose and hoping.

Usage:
    python prediction_record.py path/to/report.md      # validate one report
    python prediction_record.py --all                  # validate every report in data/Reports
    python prediction_record.py path.md --json         # dump the parsed record

Exit code: 0 = every checked report valid, 1 = any invalid (missing/malformed fields).
"""
import argparse
import json
import re
import sys
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


class TargetRow(BaseModel):
    horizon: str
    price: float = Field(gt=0)
    return_pct: float | None = None
    basis: str = Field(min_length=3)  # a target without a basis is a vibe


class PredictionRecord(BaseModel):
    ticker: str
    version: int = Field(ge=1)
    supersedes: str  # previous report filename or "none — first report"
    trigger: str
    verdict: str = Field(min_length=10)
    direction: Literal["buy", "hold", "avoid"]
    regime: Literal["risk_on", "neutral", "risk_off"]
    stop: float = Field(gt=0)  # the invalidation level — mandatory, no exceptions
    confidence: Literal["high", "medium", "low"]
    review_date: date
    kill_criteria: str = Field(min_length=10)
    targets: list[TargetRow] = Field(min_length=1)
    downside_flag: bool = False  # secondary opt-in downside call present

    @field_validator("verdict", "kill_criteria")
    @classmethod
    def no_mush(cls, v: str) -> str:
        if re.search(r"\b(wait and see|hold and see|it depends)\b", v, re.I):
            raise ValueError("hedging mush — commit to a call (house style)")
        return v


_NUM = r"[-+]?[\d][\d,]*(?:\.\d+)?"  # sign must attach ([-+], not an em-dash separator)


def _first_number(text: str) -> float | None:
    m = re.search(_NUM, text)
    return float(m.group(0).replace(",", "")) if m else None


def _downside_flag(text: str) -> bool:
    """True if ANY 'downside flag' mention in the cell is affirmative (SPEC.md opt-in).

    Reports state the *absence* of a flag far more often than its presence, so a
    literal substring match reads inverted. An occurrence is negated when a
    negator (no/not/without/never) sits in the ~30 chars before it, or when
    none/absent/not follows it; any single affirmative occurrence wins.
    """
    for m in re.finditer(r"downside flag", text, re.I):
        if re.search(r"\b(?:no|not|without|never)\b", text[max(0, m.start() - 30):m.start()], re.I):
            continue
        if re.match(r"\s*[:\-—]?\s*(?:none|absent|not\b)", text[m.end():], re.I):
            continue
        return True
    return False


def _table_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if cols and not set(cols[0]) <= {"-", " ", ":"}:
            rows.append(cols)
    return rows


def has_unlock_table(text: str) -> bool:
    """A literal markdown table under a heading containing 'unlock' (crypto hard gate)."""
    m = re.search(r"^#{2,4}[^\n]*unlock[^\n]*$", text, re.M | re.I)
    if not m:
        return False
    following = text[m.end():].split("\n#", 1)[0]
    return bool(re.search(r"^\s*\|.+\|\s*$", following, re.M))


def parse_report(text: str, ticker: str, crypto: bool = False) -> PredictionRecord:
    """Extract the Prediction Record fields from a report's markdown.

    Raises ValueError (parse) or pydantic.ValidationError (content) on failure —
    both mean the report violates the contract in docs/SPEC.md. With crypto=True,
    a missing Token Unlocks table is a failure (the spec's hard gate).
    """
    if crypto and not has_unlock_table(text):
        raise ValueError("crypto report missing the Token Unlocks table "
                         "(literal table under a '## Token Unlocks' heading — hard gate)")
    # Provenance header: v{N} | Supersedes: ... | Trigger: ...
    prov = re.search(r"^v(\d+)\s*\|\s*Supersedes:\s*(.+?)\s*\|\s*Trigger:\s*(.+)$",
                     text, re.M)
    if not prov:
        raise ValueError("missing provenance header (v{N} | Supersedes: ... | Trigger: ...)")

    verdict = re.search(r"\*\*Verdict:\*\*\s*(.+)", text)
    kill = re.search(r"\*\*Kill criteria:\*\*\s*(.+)", text)

    # Entries & risk table: | Field | Value |
    fields: dict[str, str] = {}
    er = re.search(r"\*\*Entries & risk:\*\*(.*?)(?:\n\*\*|\n##|\Z)", text, re.S)
    if er:
        for cols in _table_rows(er.group(1)):
            if len(cols) >= 2 and cols[0].lower() != "field":
                fields[cols[0].lower()] = cols[1]

    # Targets table: | Horizon | Target | Return | Basis |
    targets: list[TargetRow] = []
    tg = re.search(r"\*\*Targets\*\*.*?\n(.*?)(?:\n\*\*|\n##|\Z)", text, re.S)
    if tg:
        for cols in _table_rows(tg.group(1)):
            if len(cols) >= 4 and cols[0].lower() != "horizon" and "<price>" not in cols[1]:
                price = _first_number(cols[1])
                if price is None:
                    continue
                targets.append(TargetRow(horizon=cols[0], price=price,
                                         return_pct=_first_number(cols[2]),
                                         basis=cols[3]))

    def keyword(name: str, options: list[str]) -> str:
        # Earliest occurrence wins, not list order: "hold — no buy yet" must
        # parse as hold, not buy. The primary call leads the cell by contract.
        raw = fields.get(name, "").lower().replace("-", "_")
        hits = [(raw.find(opt), opt) for opt in options if opt in raw]
        if not hits:
            raise ValueError(f"field '{name}' missing or not one of {options}: {raw!r}")
        return min(hits)[1]

    review = re.search(r"\d{4}-\d{2}-\d{2}", fields.get("review date", ""))
    if not review:
        raise ValueError("Review date missing or not YYYY-MM-DD")
    stop = _first_number(fields.get("stop", ""))
    if stop is None:
        raise ValueError("Stop (invalidation level) missing — mandatory, no exceptions")

    return PredictionRecord(
        ticker=ticker,
        version=int(prov.group(1)),
        supersedes=prov.group(2),
        trigger=prov.group(3),
        verdict=verdict.group(1).strip() if verdict else "",
        direction=keyword("direction", ["buy", "hold", "avoid"]),  # type: ignore[arg-type]
        regime=keyword("regime", ["risk_off", "risk_on", "neutral"]),  # type: ignore[arg-type]
        stop=stop,
        confidence=keyword("confidence", ["high", "medium", "low"]),  # type: ignore[arg-type]
        review_date=date.fromisoformat(review.group(0)),
        kill_criteria=kill.group(1).strip() if kill else "",
        targets=targets,
        downside_flag=_downside_flag(fields.get("direction", "")),
    )


def validate_file(path) -> tuple[bool, str]:
    from pathlib import Path
    p = Path(path)
    ticker = p.parent.name if p.parent.name not in ("Reports", "_meta") else p.stem
    crypto = "Crypto" in p.parts
    try:
        rec = parse_report(p.read_text(), ticker, crypto=crypto)
        return True, f"OK    {p.name}  v{rec.version} {rec.direction} " \
                     f"stop={rec.stop:g} review={rec.review_date}"
    except (ValueError, ValidationError) as e:
        first = str(e).splitlines()[0] if isinstance(e, ValueError) else \
            "; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors()[:3])
        return False, f"FAIL  {p.name}  {first}"


def is_scoreable_report(path) -> bool:
    """True if a report is expected to carry a Prediction Record.

    Excludes _meta (not a ticker report), Watchlist-Scan sweeps, and Tier 1
    quick checks (`{date}-quick-{slug}.md` per docs/SPEC.md's Tier 1
    contract — one-shot, no scoreable call, no Prediction Record by design).
    """
    from pathlib import Path
    p = Path(path)
    return (p.parent.name not in ("_meta",)
            and "Watchlist-Scan" not in str(p)
            and "-quick-" not in p.name)


def main() -> None:
    from config import REPORTS
    ap = argparse.ArgumentParser(description="Validate Prediction Records in reports")
    ap.add_argument("paths", nargs="*", help="report .md files")
    ap.add_argument("--all", action="store_true", help="validate all of data/Reports")
    ap.add_argument("--json", action="store_true", help="dump parsed record(s) as JSON")
    args = ap.parse_args()

    paths = list(args.paths)
    if args.all:
        paths += [p for p in REPORTS.rglob("*.md") if is_scoreable_report(p)]
    if not paths:
        ap.error("give report paths or --all")

    ok_all = True
    for path in paths:
        ok, msg = validate_file(path)
        ok_all &= ok
        if args.json and ok:
            from pathlib import Path
            p = Path(path)
            rec = parse_report(p.read_text(), p.parent.name)
            print(json.dumps(rec.model_dump(), indent=2, default=str))
        else:
            print(msg)
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
