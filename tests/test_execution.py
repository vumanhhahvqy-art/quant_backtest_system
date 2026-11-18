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