"""Shared fixtures: recorded OHLCV frames, loaded the same way the goldens were built."""
from pathlib import Path

import pandas as pd
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> pd.DataFrame:
    df = pd.read_csv(FIXTURES / name, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True, format="mixed")
    return df


@pytest.fixture(scope="session")
def mu_df() -> pd.DataFrame:
    return load_fixture("MU_1y.csv")


@pytest.fixture(scope="session")
def btc_df() -> pd.DataFrame:
    return load_fixture("BTC-USD_2y.csv")
