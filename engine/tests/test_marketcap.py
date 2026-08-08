"""marketcap tests: formatting, source fallback, and graceful degradation.

No network — marketcap.get is monkeypatched. The contract under test is that a
dead aggregator degrades the sweep header to one note instead of breaking the
sweep, and that a partial source still contributes the fields it does carry.
"""
import pytest

import marketcap

PAPRIKA_OK = {
    "market_cap_usd": 2_307_072_219_825,
    "bitcoin_dominance_percentage": 56.44,
    "market_cap_change_24h": 0.51,
    "market_cap_ath_value": 4_823_580_636_226,
    "market_cap_ath_date": "2025-10-05T10:10:00Z",
}
GECKO_OK = {"data": {
    "total_market_cap": {"usd": 2_293_375_916_829.896, "btc": 35_348_460.7},
    "market_cap_percentage": {"btc": 56.1, "eth": 9.8},
    "market_cap_change_percentage_24h_usd": -0.42,
}}


@pytest.mark.parametrize("val, expected", [
    (None, "n/a"),
    (950, "$950"),
    (1_234, "$1.23K"),
    (5_600_000, "$5.60M"),
    (2_300_000_000, "$2.30B"),
    (2_307_072_219_825, "$2.31T"),      # trillions is the whole point of this fmt
    (-2_307_072_219_825, "$-2.31T"),
])
def test_fmt_usd(val, expected):
    assert marketcap.fmt_usd(val) == expected


def test_collect_prefers_paprika(monkeypatch):
    monkeypatch.setattr(marketcap, "get",
                        lambda url: PAPRIKA_OK if url == marketcap.PAPRIKA else GECKO_OK)
    d = marketcap.collect()
    assert d["source"] == "CoinPaprika"
    assert d["total"] == 2_307_072_219_825
    assert d["btc_dominance"] == 56.44
    assert d["ath_date"] == "2025-10-05"          # timestamp truncated to a date


def test_collect_falls_back_to_gecko(monkeypatch):
    monkeypatch.setattr(marketcap, "get",
                        lambda url: None if url == marketcap.PAPRIKA else GECKO_OK)
    d = marketcap.collect()
    assert d["source"] == "CoinGecko"
    assert d["btc_dominance"] == 56.1
    assert d["ath"] is None                       # gecko carries no ATH


def test_collect_falls_back_when_paprika_shape_is_wrong(monkeypatch):
    """A 200 with a missing cap field must fall through, not return a broken read."""
    monkeypatch.setattr(marketcap, "get",
                        lambda url: {"unexpected": True} if url == marketcap.PAPRIKA
                        else GECKO_OK)
    assert marketcap.collect()["source"] == "CoinGecko"


def test_collect_both_sources_dead(monkeypatch):
    monkeypatch.setattr(marketcap, "get", lambda url: None)
    d = marketcap.collect()
    assert d["total"] is None and d["source"] is None


def test_summary_line_full(monkeypatch):
    monkeypatch.setattr(marketcap, "get",
                        lambda url: PAPRIKA_OK if url == marketcap.PAPRIKA else None)
    line = marketcap.summary_line(marketcap.collect())
    assert "**TOTAL (crypto market cap): $2.31T** (+0.51% 24h)" in line
    assert "BTC dominance 56.44%" in line
    assert "-52.2% from ATH $4.82T (2025-10-05)" in line


def test_summary_line_partial_source_keeps_what_it_has(monkeypatch):
    monkeypatch.setattr(marketcap, "get",
                        lambda url: None if url == marketcap.PAPRIKA else GECKO_OK)
    line = marketcap.summary_line(marketcap.collect())
    assert "$2.29T" in line and "(-0.42% 24h)" in line
    assert "BTC dominance 56.10%" in line
    assert "ATH" not in line                      # absent field is dropped, not "n/a"


def test_summary_line_data_error(monkeypatch):
    monkeypatch.setattr(marketcap, "get", lambda url: None)
    assert "DATA ERROR" in marketcap.summary_line(marketcap.collect())


def test_get_returns_none_on_network_error(monkeypatch):
    def boom(*a, **k):
        raise TimeoutError("down")
    monkeypatch.setattr(marketcap.urllib.request, "urlopen", boom)
    assert marketcap.get(marketcap.PAPRIKA) is None


def test_to_markdown_states_the_no_history_limitation(monkeypatch):
    monkeypatch.setattr(marketcap, "get",
                        lambda url: PAPRIKA_OK if url == marketcap.PAPRIKA else None)
    md = marketcap.to_markdown(marketcap.collect())
    assert "no history on the free tier" in md
    assert "Source: CoinPaprika" in md
