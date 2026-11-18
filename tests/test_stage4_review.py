"""Regression checks for review findings and incremental equivalence."""

from dataclasses import replace

import pandas as pd
import pytest

from core.causality import check_prefix_invariance
from core.data_validator import validate_data, validate_expected_timestamps
from core.models import Fill, Order
from core.portfolio import Portfolio
from indicators.moving_averages import sma
from strategies.base_strategy import BaseStrategy
from test_backtest_models import instrument, simulation_metadata
from test_engine import bars, engine


def test_causal_indicator_and_future_leaking_features(bars):
    check_prefix_invariance(lambda df: sma(df.close, 2), bars)
    for builder in (
        lambda df: df.close.shift(-1),
        lambda df: df.close.rolling(3, center=True).mean(),
        lambda df: df.close / df.close.max(),
    ):
        with pytest.raises(ValueError, match="Future-dependent"):
            check_prefix_invariance(builder, bars)


def test_independent_schedule_detects_missing_first_middle_last(simulation_metadata, bars):
    # Construct a schedule from known fixture boundaries, before dropping rows.
    schedule = pd.date_range("2024-01-01", periods=4, freq="h", tz="UTC")
    for missing in range(4):
        report = validate_data(bars.drop(bars.index[missing]), simulation_metadata,
                               expected_timestamps=schedule)
        assert report["errors"]["missing_expected_candles"]["count"] == 1


def test_schedule_rejects_overlapping_candles():
    with pytest.raises(ValueError, match="overlapping"):
        validate_expected_timestamps(
            pd.date_range("2024-01-01", periods=4, freq="30min", tz="UTC"),
            timeframe="1h", timestamp_kind="open")


def test_portfolio_rejects_mismatched_ids_and_time_without_mutation(instrument):
    at = pd.Timestamp("2024-01-01", tz="UTC")
    order = Order(1, "BUY", 1, at)
    fill = Fill(1, at, 1, 1, 100, 0, 0, 0, "BUY")
    portfolio = Portfolio(instrument, 10000)
    for broken in (replace(fill, order_id=2), replace(fill, timestamp=at-pd.Timedelta("1h"))):
        with pytest.raises(ValueError, match="ID/timestamp"):
            portfolio.open(order, broken, 1)
        assert portfolio.balance == 10000 and portfolio.position is None
    portfolio.open(order, fill, 1)
    with pytest.raises(ValueError, match="precede"):
        portfolio.close(replace(fill, side=-1, timestamp=at-pd.Timedelta("1h")), 1)
    assert portfolio.position is not None and not portfolio.trades


class BatchThreshold(BaseStrategy):
    def generate_signals(self, data):
        return pd.DataFrame({"signal": (data.close > 105).astype(int), "exit": False}, index=data.index)


class IncrementalThreshold(BaseStrategy):
    signal_history_limit = 1

    def generate_signal(self, completed_data):
        assert len(completed_data) == 1
        return pd.Series({"signal": int(completed_data.close.iloc[-1] > 105), "exit": False})


def test_incremental_and_legacy_results_are_identical(simulation_metadata, bars):
    model = engine(simulation_metadata)
    schedule = pd.date_range("2024-01-01", periods=4, freq="h", tz="UTC")
    batch = model.run(bars, BatchThreshold(), expected_timestamps=schedule)
    incremental = model.run(bars, IncrementalThreshold(), expected_timestamps=schedule)
    assert batch == incremental