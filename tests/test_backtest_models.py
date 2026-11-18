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