# 05A_TESTS_MODELS_COSTS_PORTFOLIO

Toàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.

## File gốc: `tests/test_backtest_models.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_backtest_models.py`

Số dòng: 78; kích thước: 2891 bytes; SHA256: `ecd084d2ca4cb1da762d3010473885569fb81f607b00e2d20c7a01d4a37b481f`.

<!-- SOURCE_BEGIN tests/test_backtest_models.py -->
```python
"""Instrument metadata and order validation using explicit synthetic units."""

from copy import deepcopy

import pandas as pd
import pytest

from core.models import Fill, Instrument, Order, Position


@pytest.fixture
def simulation_metadata():
    values = {
        "source": "synthetic hand-calculated fixture", "symbol": "TESTUSD",
        "source_timezone": "UTC", "timestamp_encoding": "aware",
        "timestamp_kind": "open", "price_type": "Mid", "timeframe": "1h",
        "instrument_specifications": {
            "tick_size": 0.01, "pip_size": 0.01, "contract_size": 10,
            "quantity_unit": "lots", "quote_currency": "USD",
            "minimum_quantity_increment": 0.1,
        },
    }
    return {key: {"value": value, "confirmed": True, "evidence": "Synthetic test definition"}
            for key, value in values.items()}


@pytest.fixture
def instrument(simulation_metadata):
    return Instrument.from_metadata(simulation_metadata)


def test_instrument_conversion_and_metadata(instrument, simulation_metadata):
    assert instrument.units(0.2) == 2
    for quantity in (0, -1, 0.15, float("inf"), True):
        with pytest.raises(ValueError):
            instrument.units(quantity)
    broken = deepcopy(simulation_metadata)
    broken["instrument_specifications"]["confirmed"] = False
    with pytest.raises(ValueError, match="Unconfirmed"):
        Instrument.from_metadata(broken)


@pytest.mark.parametrize("kwargs", [
    {"order_type": "limit"}, {"action": "HOLD"}, {"quantity": 0},
    {"stop_loss": float("nan")}, {"submitted_at": pd.Timestamp("2024-01-01")},
])
def test_unsupported_or_invalid_orders(kwargs):
    fields = dict(order_id=1, action="BUY", quantity=1,
                  submitted_at=pd.Timestamp("2024-01-01", tz="UTC"))
    fields.update(kwargs)
    with pytest.raises(ValueError):
        Order(**fields)


@pytest.mark.parametrize("changes", [
    {"side": 0}, {"quantity": -1}, {"price": -1}, {"commission": -1},
    {"spread_cost": float("nan")}, {"slippage_cost": float("inf")},
    {"timestamp": pd.Timestamp("2024-01-01")}, {"timing": "unknown"},
])
def test_fill_rejects_invalid_financial_fields(changes):
    from dataclasses import replace

    fill = Fill(1, pd.Timestamp("2024-01-01", tz="UTC"), 1, 1, 10, 0, 0, 0, "entry")
    with pytest.raises(ValueError):
        replace(fill, **changes)


@pytest.mark.parametrize("changes", [
    {"direction": 0}, {"quantity": -1}, {"reserved_capital": 0},
    {"stop_loss": -1}, {"take_profit": float("nan")},
])
def test_position_rejects_invalid_state(changes):
    from dataclasses import replace

    fill = Fill(1, pd.Timestamp("2024-01-01", tz="UTC"), 1, 1, 10, 0, 0, 0, "entry")
    position = Position(1, 1, fill, 9, 11, 10)
    with pytest.raises(ValueError):
        replace(position, **changes)
```
<!-- SOURCE_END tests/test_backtest_models.py -->

## File gốc: `tests/test_cost_model.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_cost_model.py`

Số dòng: 33; kích thước: 1330 bytes; SHA256: `71936c1a12518f645480ba31b6305091dfada45543440c1f374610485bb38e41`.

<!-- SOURCE_BEGIN tests/test_cost_model.py -->
```python
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
```
<!-- SOURCE_END tests/test_cost_model.py -->

## File gốc: `tests/test_execution.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_execution.py`

Số dòng: 30; kích thước: 1343 bytes; SHA256: `c30cbef36f5ff8f6227437f1e706d8319c45a3ba31bd9982a350bfa0161c5a60`.

<!-- SOURCE_BEGIN tests/test_execution.py -->
```python
"""Long and short OHLC stops, targets, gaps and ambiguity."""

from dataclasses import replace

import pandas as pd
import pytest

from core.execution import protective_exit
from core.models import Fill, Position


@pytest.mark.parametrize("direction,bar,expected,reason,ambiguous", [
    (1, (100, 106, 94), 95, "stop_loss", True),
    (-1, (100, 106, 94), 105, "stop_loss", True),
    (1, (90, 106, 89), 90, "stop_loss_gap", False),
    (-1, (110, 111, 94), 110, "stop_loss_gap", False),
    (1, (110, 111, 99), 105, "take_profit_gap", False),
    (-1, (90, 101, 89), 95, "take_profit_gap", False),
    (1, (100, 106, 99), 105, "take_profit", False),
    (-1, (100, 101, 94), 95, "take_profit", False),
])
def test_protective_execution(direction, bar, expected, reason, ambiguous):
    fill = Fill(1, pd.Timestamp("2024-01-01", tz="UTC"), direction, 1, 100, 0, 0, 0, "entry")
    position = Position(direction, 1, fill, 100 - direction * 5, 100 + direction * 5, 100)
    result = protective_exit(position, dict(zip(("open", "high", "low"), bar)))
    assert result.price == expected
    assert result.reason == reason
    assert result.ambiguous == ambiguous
    assert protective_exit(replace(position, stop_loss=None, take_profit=None),
                           {"open": 100, "high": 1000, "low": 1}) is None
```
<!-- SOURCE_END tests/test_execution.py -->

## File gốc: `tests/test_portfolio.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_portfolio.py`

Số dòng: 46; kích thước: 1985 bytes; SHA256: `d0b990946cfdb10b8d56acf7b6f705ec4e74c7965c5f78386385b9a158dafa4c`.

<!-- SOURCE_BEGIN tests/test_portfolio.py -->
```python
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
```
<!-- SOURCE_END tests/test_portfolio.py -->
