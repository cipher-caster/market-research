"""exchange_ohlcv pure-function tests: base_ticker normalization and _df shaping.

Characterization tests — they pin what the functions do now (no network).
"""
import pandas as pd
import pytest

from exchange_ohlcv import _df, base_ticker


@pytest.mark.parametrize("ticker, expected", [
    ("HYPE32196-USD", "HYPE"),   # Yahoo numeric suffix + -USD stripped
    ("BTC-USD", "BTC"),
    ("BTC", "BTC"),
    ("btc", "BTC"),              # lowercase uppercased
    ("hype32196-usd", "HYPE"),
    ("123", "123"),             # all-digits token: nothing left to keep, stays itself
])
def test_base_ticker(ticker, expected):
    assert base_ticker(ticker) == expected


def test_df_sorts_orders_and_types():
    # rows deliberately out of order and given as strings, as the exchange APIs do
    rows = [
        (172_800_000, "3", "4", "1", "2.0", "10"),   # 1970-01-03
        (86_400_000, "1.5", "2.5", "0.5", "2.0", "5"),  # 1970-01-02
    ]
    df = _df(rows)

    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert all(str(dt) == "float64" for dt in df.dtypes)
    assert df.index.name == "Date"
    assert df.index.tz is None                     # tz-naive (localized off UTC)
    assert df.index.is_monotonic_increasing        # sorted oldest -> newest
    assert list(df.index) == [pd.Timestamp("1970-01-02"), pd.Timestamp("1970-01-03")]
    # earliest bar is first after the sort
    first = df.iloc[0]
    assert (first["Open"], first["High"], first["Low"], first["Close"], first["Volume"]) == \
        (1.5, 2.5, 0.5, 2.0, 5.0)
