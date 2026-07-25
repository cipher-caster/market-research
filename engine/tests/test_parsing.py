"""Pure-function tests: watchlist parsing and level parsing (no fixtures, no network)."""
from check_levels import check_row, parse_number, parse_watchlist

SAMPLE = """# Watchlist

## Calls

| Date | Asset | Type | Thesis | Catalyst | Entry | Target | Stop | Horizon | Status | Call |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-19 | [[BTC]] | Crypto | test | test | 100000-105000 | 150000 | 90000 | swing | Active | Buy |
| 2026-07-19 | [[MU]] | Stock | test | test | 100 | 200 | 90 | 6mo | Resolved | Hold |
| 2026-07-19 | [[TBD1]] | Stock | test | test | TBD | TBD | TBD | 6mo | Active | |

## Something else

| Date | Asset | Type | Thesis | Catalyst | Entry | Target | Stop | Horizon | Status | Call |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-19 | [[NOPE]] | Stock | must not parse | x | 1 | 2 | 3 | 1mo | Active | |
"""


def test_parse_number():
    assert parse_number("443") == 443.0
    assert parse_number("504-471") == (471.0, 504.0)
    assert parse_number("1,250") == 1250.0
    assert parse_number("TBD") is None
    assert parse_number("") is None


def test_parse_watchlist_rows():
    rows = parse_watchlist(SAMPLE)
    assert [r["ticker"] for r in rows] == ["BTC", "MU", "TBD1"]
    btc = rows[0]
    assert btc["type"] == "Crypto"
    assert btc["entry"] == (100000.0, 105000.0)
    assert btc["stop"] == 90000.0
    assert btc["status"] == "Active"
    assert btc["call"] == "Buy"


def test_parse_watchlist_empty_states():
    assert parse_watchlist("# Watchlist\n") == []
    assert parse_watchlist("## Calls\n\nno table here\n") == []


def fired_of(result):
    """Narrow Optional for mypy: these cases always return a list."""
    assert result is not None
    return result


def _row(**kw):
    base = {"ticker": "X", "type": "Stock", "entry": None, "target": None,
            "stop": None, "status": "Active", "call": ""}
    base.update(kw)
    return base


def test_check_row_no_levels():
    assert check_row(_row(), px=100.0, lo=99.0) is None


def test_check_row_stop_breach_active_only():
    r = _row(stop=90.0)
    assert any("STOP BREACHED" in t for t in fired_of(check_row(r, px=89.0, lo=88.0)))
    # near-stop within 3%
    assert any("STOP NEAR" in t for t in fired_of(check_row(r, px=92.0, lo=92.0)))
    # resolved calls do not watch the stop
    assert check_row(_row(stop=90.0, status="Resolved"), px=89.0, lo=88.0) == []


def test_check_row_stop_intra_period():
    """A stop pierced by the lookback low but recovered fires a distinct message."""
    r = _row(stop=90.0)
    fired = fired_of(check_row(r, px=95.0, lo=88.0))
    assert any("STOP BREACHED INTRA-PERIOD" in t for t in fired)
    assert not any(t.startswith("STOP BREACHED —") for t in fired)  # current breach not claimed
    # intra-period is Active-only, like a live breach
    assert check_row(_row(stop=90.0, status="Resolved"), px=95.0, lo=88.0) == []
    # low above the stop and price only mildly above: falls through to STOP NEAR
    near = fired_of(check_row(_row(stop=90.0), px=92.0, lo=91.0))
    assert any("STOP NEAR" in t for t in near)
    assert not any("INTRA-PERIOD" in t for t in near)


def test_check_row_entry_zone_tags():
    r = _row(entry=(100.0, 105.0))
    assert any("IN ENTRY ZONE" in t for t in fired_of(check_row(r, px=102.0, lo=101.0)))
    fired = fired_of(check_row(_row(entry=(100.0, 105.0), status="Resolved"), px=102.0, lo=101.0))
    assert any("RE-ENTRY" in t for t in fired)


def test_check_row_target_active_only():
    r = _row(target=200.0)
    assert any("TARGET HIT" in t for t in fired_of(check_row(r, px=201.0, lo=200.0)))
    assert check_row(_row(target=200.0, status="Invalidated"), px=201.0, lo=200.0) == []
