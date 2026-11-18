"""Known long/short P/L, conversion, capital reservation and fee accounting."""

from dataclasses import replace

import pandas as pd
import pytest

from core.models import Fill, Order
from core.portfolio import Portfolio
from test_backtest_models import instrument, simulation_metadata


@pytest.mark.parametrize("direction,exit_price", [(1, 110), (-1, 90)])
def test_accounting_with_currency_conversion(instrument, direction, exit_price):
    timestamp = pd.Timestamp("2024-01-01", tz="UTC")
    order = Order(1, "BUY" if direction == 1 else "SELL", 1, timestamp)
    entry = Fill(1, timestamp, direction, 1, 100, 2, 0, 0, "entry")
    portfolio = Portfolio(instrument, 5000)
    portfolio.open(order, entry, 2)
    state = portfolio.mark(timestamp, 100 + 5 * direction, 3)
    assert state.balance == 4998
    assert state.unrealized_pnl == 150  # 5 * 10 units * FX 3
    assert state.equity == 5148
    assert state.reserved_capital == 2000
    assert state.free_capital == 3148
    exit_fill = replace(entry, side=-direction, price=exit_price, reason="exit", commission=3)
    trade = portfolio.close(exit_fill, 3)
    assert trade.gross_pnl == 300
    assert trade.net_pnl == 295
    assert portfolio.balance == 5295
    assert portfolio.mark(timestamp, 100, 3).realized_pnl == 295


def test_insufficient_capital_and_invalid_stops_do_not_mutate(instrument):
    timestamp = pd.Timestamp("2024-01-01", tz="UTC")
    order = Order(1, "BUY", 1, timestamp)
    fill = Fill(1, timestamp, 1, 1, 100, 2, 0, 0, "entry")
    portfolio = Portfolio(instrument, 1000)
    with pytest.raises(ValueError, match="Insufficient"):
        portfolio.open(order, fill, 1)
    assert portfolio.balance == 1000
    assert portfolio.position is None
    with pytest.raises(ValueError, match="bracket"):
        portfolio.open(replace(order, stop_loss=101), fill, 1)
    with pytest.raises(ValueError, match="No position"):
        portfolio.close(fill, 1)