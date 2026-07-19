"""Schema tests: a compliant report parses; contract violations fail loudly."""
import pytest
from pydantic import ValidationError

from prediction_record import parse_report

GOOD = """v3 | Supersedes: 2026-07-01-deep-dive.md | Trigger: owner request

## Prediction Record

**Verdict:** BUY the reclaim of 105; next action at 150 (trim) or 90 (call invalid).

**Targets** (time-bound, each with a basis):

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Q3) | 150,000 | +43% | measured move from the 90-105 base |
| EOY 2026 (base) | 180,000 | +71% | halving-cycle comp, prior-cycle multiple |

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | buy (primary). Downside flag: none |
| Regime | risk_off (BTC below 200-MA) |
| Add levels | reclaim of 105k on daily close |
| Stop | 90,000 — daily close below invalidates |
| Confidence | medium |
| Review date | 2026-09-30 |

**Kill criteria:** daily close below 90k, or ETF outflows > 3 consecutive weeks.
"""


def test_good_report_parses():
    rec = parse_report(GOOD, "BTC")
    assert rec.version == 3
    assert rec.direction == "buy"
    assert rec.regime == "risk_off"
    assert rec.stop == 90000.0
    assert rec.confidence == "medium"
    assert str(rec.review_date) == "2026-09-30"
    assert len(rec.targets) == 2
    assert rec.targets[0].price == 150000.0
    assert rec.targets[0].return_pct == 43.0


def test_missing_provenance_fails():
    bad = GOOD.replace("v3 | Supersedes: 2026-07-01-deep-dive.md | Trigger: owner request", "")
    with pytest.raises(ValueError, match="provenance"):
        parse_report(bad, "BTC")


def test_missing_stop_fails():
    bad = GOOD.replace("| Stop | 90,000 — daily close below invalidates |", "")
    with pytest.raises(ValueError, match="[Ss]top"):
        parse_report(bad, "BTC")


def test_missing_targets_fails():
    bad = GOOD.replace("| Swing (~Q3) | 150,000 | +43% | measured move from the 90-105 base |", "") \
              .replace("| EOY 2026 (base) | 180,000 | +71% | halving-cycle comp, prior-cycle multiple |", "")
    with pytest.raises(ValidationError):
        parse_report(bad, "BTC")


def test_hedging_mush_fails():
    bad = GOOD.replace("BUY the reclaim of 105; next action at 150 (trim) or 90 (call invalid).",
                       "Probably fine, wait and see how it develops from here.")
    with pytest.raises(ValidationError, match="mush"):
        parse_report(bad, "BTC")


def test_bad_direction_fails():
    bad = GOOD.replace("| Direction | buy (primary). Downside flag: none |",
                       "| Direction | maybe long? |")
    with pytest.raises(ValueError, match="direction"):
        parse_report(bad, "BTC")


UNLOCKS = """

## Token Unlocks

| Date | Amount | % of circulating |
|---|---|---|
| 2026-07-28 | 88.9M | +138% |
"""


def test_crypto_gate_requires_unlock_table():
    with pytest.raises(ValueError, match="[Uu]nlock"):
        parse_report(GOOD, "XPL", crypto=True)
    rec = parse_report(GOOD + UNLOCKS, "XPL", crypto=True)
    assert rec.direction == "buy"


def test_unlock_prose_does_not_satisfy_gate():
    prose = GOOD + "\n## Token Unlocks\n\nA big unlock happens July 28, about 138%.\n"
    with pytest.raises(ValueError, match="[Uu]nlock"):
        parse_report(prose, "XPL", crypto=True)


def test_direction_earliest_keyword_wins():
    """'hold ... no buy yet' must parse as hold — position beats option order."""
    r = GOOD.replace("| Direction | buy (primary). Downside flag: none |",
                     "| Direction | hold (primary) — no buy call until the reclaim confirms |")
    assert parse_report(r, "BTC").direction == "hold"
