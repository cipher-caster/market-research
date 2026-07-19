"""Deterministic tests of the indicator math against recorded fixtures.

Two layers:
- invariants: properties that must hold on any input (bounds, ordering, consistency)
- goldens: exact regression against tests/fixtures/golden.json — catches silent
  changes in the math (library upgrades, refactors) at 1e-6 relative tolerance
"""
import json
from pathlib import Path

import pytest

from regime import GATE, compute_regime
from technicals import compute

GOLDEN = json.loads((Path(__file__).parent / "fixtures" / "golden.json").read_text())


def assert_matches(got, want, path=""):
    """Recursive compare; floats at rel=1e-6, everything else exact."""
    if isinstance(want, dict):
        assert isinstance(got, dict), path
        assert set(got) == set(want), f"{path}: keys {set(got) ^ set(want)}"
        for k in want:
            assert_matches(got[k], want[k], f"{path}.{k}")
    elif isinstance(want, list):
        assert len(got) == len(want), path
        for i, (g, w) in enumerate(zip(got, want, strict=True)):
            assert_matches(g, w, f"{path}[{i}]")
    elif isinstance(want, float) or isinstance(got, float):
        assert got == pytest.approx(float(want), rel=1e-6), path
    else:
        # goldens were serialized with default=str; compare on the same footing
        assert str(got) == str(want), f"{path}: {got!r} != {want!r}"


# --- invariants ---

def test_snapshot_invariants(mu_df):
    s = compute("MU", mu_df)
    assert 0 <= s["rsi14"] <= 100
    assert s["atr14"] > 0
    assert s["stop_long_2atr"] < s["price"]
    dr = s["dealing_range"]
    assert dr["range_low"] <= dr["equilibrium"] <= dr["range_high"]
    assert (dr["zone"] == "premium") == (dr["pct_in_range"] > 50)
    assert s["support_20"] <= s["resistance_20"]
    assert s["support_50"] <= s["resistance_50"]


def test_regime_invariants(btc_df):
    r = compute_regime(btc_df)
    assert r["regime"] in GATE
    assert r["reasons"]
    assert r["drawdown_90bar_pct"] <= 0


def test_regime_rules_consistency(btc_df):
    """The label must follow the documented deterministic rules."""
    r = compute_regime(btc_df)
    below_200 = r["price"] < r["ma200"]
    deep_dd = r["drawdown_90bar_pct"] <= -20
    if below_200 or deep_dd:
        assert r["regime"] == "risk_off"


# --- goldens ---

def test_mu_snapshot_golden(mu_df):
    assert_matches(compute("MU", mu_df), GOLDEN["mu_snapshot"], "mu")


def test_btc_regime_golden(btc_df):
    assert_matches(compute_regime(btc_df), GOLDEN["btc_regime"], "regime")
