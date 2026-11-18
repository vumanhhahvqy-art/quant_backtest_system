"""Costs and executable sides, with hand-computed account-currency amounts."""

import pandas as pd
import pytest

from core.cost_model import CostModel
from test_backtest_models import instrument, simulation_metadata


@pytest.mark.parametrize("price_type,side,expected", [
    ("Mid", 1, 101), ("Mid", -1, 99), ("Bid", 1, 102),
    ("Bid", -1, 100), ("Ask", 1, 100), ("Ask", -1, 98),
])
def test_bid_ask_conventions(price_type, side, expected):
    costs = CostModel(2, 0, 0)
    assert costs.side_bar({"open": 100}, price_type, side)["open"] == expected


def test_fill_costs_and_adverse_tick_rounding(instrument):
    costs = CostModel(2, 0.015, 3)
    fill = costs.fill(instrument=instrument, order_id=1,
                      timestamp=pd.Timestamp("2024-01-01", tz="UTC"),
                      side=1, quantity=0.2, price=101, conversion_rate=2, reason="BUY")
    assert fill.price == pytest.approx(101.02)
    assert fill.commission == pytest.approx(0.6)
    assert fill.spread_cost == 4  # 2 underlying units * half-spread 1 * FX 2
    assert fill.slippage_cost == pytest.approx(0.08)


@pytest.mark.parametrize("args", [(-1, 0, 0), (0, float("nan"), 0), (0, 0, -1), (0, 0, 0, 1)])
def test_reject_invalid_costs_and_swap(args):
    with pytest.raises(ValueError):
        CostModel(*args)