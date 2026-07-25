"""defillama tests: fmt_usd formatting and collect/to_markdown over a mocked get.

No network — defillama.get is monkeypatched to canned responses. Characterization
tests: they pin current formatting and the endpoint-fallback behavior.
"""
import pytest

import defillama

# A protocol with every endpoint alive.
FULL = {
    "/protocol/hyperliquid": {"name": "Hyperliquid"},
    "/tvl/hyperliquid": 1_000_000.0,
    "/summary/fees/hyperliquid": {"total24h": 1000, "total7d": 7000, "total30d": 30000},
    "/summary/fees/hyperliquid?dataType=dailyRevenue":
        {"total24h": 500, "total7d": 3500, "total30d": 15000},
    "/summary/dexs/hyperliquid": {"total24h": 2_000_000, "total7d": 14_000_000,
                                  "total30d": 60_000_000},
}


@pytest.mark.parametrize("val, expected", [
    (None, "n/a"),
    (950, "$950"),
    (1_234, "$1.23K"),
    (5_600_000, "$5.60M"),
    (2_300_000_000, "$2.30B"),
    (-1_234, "$-1.23K"),          # negative keeps its sign with the unit
    (-5_600_000, "$-5.60M"),
])
def test_fmt_usd(val, expected):
    assert defillama.fmt_usd(val) == expected


def test_summary_block_none_when_total24h_missing(monkeypatch):
    monkeypatch.setattr(defillama, "get",
                        lambda path: {"total24h": None, "total7d": 1, "total30d": 2})
    assert defillama.summary_block("fees", "x") is None


def test_summary_block_none_when_endpoint_dead(monkeypatch):
    monkeypatch.setattr(defillama, "get", lambda path: None)
    assert defillama.summary_block("fees", "x") is None


def test_collect_and_markdown_full(monkeypatch):
    monkeypatch.setattr(defillama, "get", lambda path: FULL.get(path))
    d = defillama.collect("hyperliquid")
    assert d["name"] == "Hyperliquid"
    assert d["tvl"] == 1_000_000.0
    assert d["fees"]["total24h"] == 1000
    assert d["revenue"]["total24h"] == 500

    md = defillama.to_markdown(d)
    assert "**TVL:** $1.00M" in md
    assert "**Fees:** 24h $1.00K  |  7d $7.00K  |  30d $30.00K" in md
    assert "**DEX volume:** 24h $2.00M" in md
    assert "Derivatives volume / perps share" in md
    assert "No data on any endpoint" not in md


def test_all_endpoints_dead(monkeypatch):
    monkeypatch.setattr(defillama, "get", lambda path: None)
    d = defillama.collect("ghost")
    assert d["name"] == "ghost"           # slug falls through when /protocol is dead
    assert d["tvl"] is None
    assert d["fees"] is None
    md = defillama.to_markdown(d)
    assert "No data on any endpoint for slug 'ghost'" in md
