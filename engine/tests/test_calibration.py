"""Calibration tests: hand-computed scoreboard stats, clean empty-state, loud junk.

The Scoreboard rows below are scored by hand (see the asserts) so the module's
arithmetic — per-bucket hit rate, gap vs implied p, Brier — is pinned, not trusted.
"""
import pytest
from pydantic import ValidationError

from calibration import parse_scoreboard, stats, to_markdown

# Four rows exercising every accepted 'Conf (p)' form (bare label, label(p), bare
# number, bare label) and yes/no + y/n cell forms. Trailing sections must not parse.
SCOREBOARD = """# Calibration Log

## Scoreboard

Append-only, most recent first. Conf (p): high = 0.7, medium = 0.55, low = 0.4.

| Scored | Ticker | Report | Direction | Conf (p) | Dir hit | Mag hit | Realized % | Event |
|---|---|---|---|---|---|---|---|---|
| 2026-08-01 | BTC | r1.md | buy | high | yes | yes | +12% | target |
| 2026-08-02 | ETH | r2.md | hold | high (0.7) | no | no | -5% | review-matured |
| 2026-08-03 | SOL | r3.md | buy | 0.55 | Y | n | +8% | target |
| 2026-08-04 | ZEC | r4.md | avoid | low | N | Y | -3% | invalidation |

## Entries

### 2026-08-04 — narrative, not a row | a | b | c |
"""

EMPTY = """# Calibration Log

## Scoreboard

| Scored | Ticker | Report | Direction | Conf (p) | Dir hit | Mag hit | Realized % | Event |
|---|---|---|---|---|---|---|---|---|

## Entries
"""


def test_parses_every_conf_and_yesno_form():
    rows = parse_scoreboard(SCOREBOARD)
    assert len(rows) == 4
    assert [r.confidence for r in rows] == ["high", "high", "medium", "low"]
    assert [r.p for r in rows] == [0.7, 0.7, 0.55, 0.4]
    assert [r.dir_hit for r in rows] == [True, False, True, False]
    assert [r.mag_hit for r in rows] == [True, False, False, True]
    assert [r.realized_pct for r in rows] == [12.0, -5.0, 8.0, -3.0]
    assert [r.event for r in rows] == ["target", "review-matured", "target", "invalidation"]


def test_hand_computed_bucket_stats_and_brier():
    s = stats(parse_scoreboard(SCOREBOARD))
    assert s["n"] == 4
    # Brier = mean of (p - dir_hit)^2 = (0.09 + 0.49 + 0.2025 + 0.16) / 4
    assert s["brier"] == 0.2356
    assert s["by_confidence"]["high"] == {
        "count": 2, "hit_rate": 0.5, "implied_p": 0.7, "gap": -0.2}
    assert s["by_confidence"]["medium"] == {
        "count": 1, "hit_rate": 1.0, "implied_p": 0.55, "gap": 0.45}
    assert s["by_confidence"]["low"] == {
        "count": 1, "hit_rate": 0.0, "implied_p": 0.4, "gap": -0.4}
    assert s["by_direction"]["buy"] == {"count": 2, "hit_rate": 1.0}
    assert s["by_direction"]["hold"] == {"count": 1, "hit_rate": 0.0}
    assert s["by_direction"]["avoid"] == {"count": 1, "hit_rate": 0.0}


def test_markdown_summary_renders_the_numbers():
    md = to_markdown(parse_scoreboard(SCOREBOARD))
    assert "Brier 0.2356" in md
    assert "| high | 0.7 | 2 | 0.5 | -0.2 |" in md
    assert "| medium | 0.55 | 1 | 1.0 | +0.45 |" in md


def test_empty_scoreboard_clean_zero_state():
    rows = parse_scoreboard(EMPTY)
    assert rows == []
    assert stats(rows) == {"n": 0, "brier": None, "by_confidence": {}, "by_direction": {}}
    assert "no scored calls yet" in to_markdown(rows)


def test_bad_event_fails_loudly():
    bad = SCOREBOARD.replace("| +12% | target |", "| +12% | moon |")
    with pytest.raises(ValidationError):
        parse_scoreboard(bad)


def test_conf_label_and_number_disagreement_fails_loudly():
    bad = SCOREBOARD.replace("| high (0.7) |", "| high (0.4) |")
    with pytest.raises(ValueError, match="disagree"):
        parse_scoreboard(bad)


def test_noncanonical_conf_number_fails_loudly():
    bad = SCOREBOARD.replace("| 0.55 |", "| 0.6 |")
    with pytest.raises(ValueError, match="canonical"):
        parse_scoreboard(bad)
