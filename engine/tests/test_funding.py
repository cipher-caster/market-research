"""funding.analyze tests: interval inference, annualization, crowding tags, OI math.

Raw dicts are built by hand (the shape from_binance/from_bybit produce) so no
network is touched. These pin current behavior.
"""
from funding import analyze


def _raw(**kw) -> dict:
    base = {
        "venue": "Binance USD-M futures",
        "mark_price": 100.0,
        "funding_now": 0.0002,
        "funding_history": [(0, 0.0001), (28_800_000, 0.0002), (57_600_000, 0.0003)],
        "oi_now": 1200.0,
        "oi_history": [(0, 1000.0), (86_400_000, 1050.0), (172_800_000, 1100.0)],
    }
    base.update(kw)
    return base


def test_8h_interval_inference_and_annualization():
    a = analyze(_raw())
    # 8h spacing between the last two timestamps -> per_year = 365*24/8 = 1095
    assert a["funding_interval_h"] == 8.0
    assert a["funding_now_pct"] == 0.02
    assert a["funding_now_apr_pct"] == 21.9      # 0.0002 * 1095 * 100
    assert a["funding_7d_mean_pct"] == 0.02
    assert a["funding_7d_mean_apr_pct"] == 21.9
    assert a["crowding"].startswith("neutral")


def test_4h_interval_changes_apr_and_8h_equiv_crowding():
    # 4h spacing -> per_year = 2190, so the same-magnitude rate annualizes higher,
    # and the 8h-equivalent (rate * 8/4) doubles a 0.0003 rate past the 0.0005 gate.
    a = analyze(_raw(funding_now=0.0003, oi_now=None, oi_history=[],
                     funding_history=[(0, 0.0003), (14_400_000, 0.0003),
                                      (28_800_000, 0.0003)]))
    assert a["funding_interval_h"] == 4.0
    assert a["funding_now_apr_pct"] == 65.7      # 0.0003 * 2190 * 100
    assert a["crowding"].startswith("ELEVATED")


def test_crowding_tags_on_rate_8h_equiv():
    # thresholds are on the 8h-equivalent rate (== funding_now here, 8h interval)
    assert analyze(_raw(funding_now=-0.0002))["crowding"].startswith("NEGATIVE")
    assert analyze(_raw(funding_now=0.0006))["crowding"].startswith("ELEVATED")
    assert analyze(_raw(funding_now=0.0002))["crowding"].startswith("neutral")


def test_oi_change_24h_and_7d():
    a = analyze(_raw())
    # 24h uses the second-to-last point (1050), 7d uses the oldest (1000)
    assert a["open_interest"] == 1200.0
    assert a["oi_change_24h_pct"] == 14.3        # 1200/1050 - 1
    assert a["oi_change_7d_pct"] == 20.0         # 1200/1000 - 1


def test_len_lt_2_history_defaults_to_8h():
    a = analyze(_raw(funding_history=[(0, 0.0001)], oi_now=None, oi_history=[]))
    assert a["funding_interval_h"] == 8.0        # no second timestamp to infer from
    assert a["funding_now_apr_pct"] == 21.9      # still annualized at 1095
    assert a["funding_7d_mean_apr_pct"] == 10.9  # single 0.0001 rate * 1095 * 100


def test_empty_rates_gives_none_means():
    a = analyze(_raw(funding_history=[], oi_now=None, oi_history=[]))
    assert a["funding_7d_mean_pct"] is None
    assert a["funding_7d_mean_apr_pct"] is None
    assert a["oi_change_24h_pct"] is None
