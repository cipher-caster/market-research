"""Routing tests: fetch_routed sends crypto to the exchange, stocks to Yahoo, and
falls back to Yahoo only when every exchange venue is empty. No network — the
exchange and Yahoo fetchers are monkeypatched."""
import pandas as pd
import pytest

import fetch_ohlcv


def _df(close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [close], "High": [close], "Low": [close],
         "Close": [close], "Volume": [1.0]},
        index=pd.to_datetime(["2026-07-24"]),
    )


def test_crypto_routes_to_exchange(monkeypatch):
    monkeypatch.setattr(fetch_ohlcv, "fetch_crypto", lambda t, p: (_df(111.0), "OKX"))
    monkeypatch.setattr(fetch_ohlcv, "fetch",
                        lambda *a, **k: pytest.fail("crypto must not hit Yahoo when the exchange has data"))
    df, src = fetch_ohlcv.fetch_routed("BTC-USD", "1y", crypto=True)
    assert src == "OKX"
    assert float(df["Close"].iloc[-1]) == 111.0


def test_crypto_falls_back_to_yahoo(monkeypatch):
    monkeypatch.setattr(fetch_ohlcv, "fetch_crypto", lambda t, p: (pd.DataFrame(), ""))
    seen = {}

    def fake_fetch(sym, period, interval="1d"):
        seen["sym"] = sym
        return _df(99.0)

    monkeypatch.setattr(fetch_ohlcv, "fetch", fake_fetch)
    df, src = fetch_ohlcv.fetch_routed("HYPE", "1y", crypto=True)
    assert src == "Yahoo Finance"
    assert seen["sym"] == "HYPE32196-USD"  # SYMBOL_OVERRIDE resolves the fallback
    assert float(df["Close"].iloc[-1]) == 99.0


def test_stock_routes_to_yahoo(monkeypatch):
    monkeypatch.setattr(fetch_ohlcv, "fetch_crypto",
                        lambda *a, **k: pytest.fail("stock must not hit the exchange"))
    monkeypatch.setattr(fetch_ohlcv, "fetch", lambda sym, period, interval="1d": _df(50.0))
    df, src = fetch_ohlcv.fetch_routed("MU", "1y", crypto=False)
    assert src == "Yahoo Finance"
    assert float(df["Close"].iloc[-1]) == 50.0
