# 05B_TESTS_ENGINE_REVIEW

Toàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.

## File gốc: `tests/test_engine.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_engine.py`

Số dòng: 273; kích thước: 13110 bytes; SHA256: `dea2360ce920923cd6479da095fcd004997301d06c99ae903d0f13e635e84ad7`.

<!-- SOURCE_BEGIN tests/test_engine.py -->
```python
"""Integration: signal -> timing -> executable prices -> costs -> account."""

import pandas as pd
import pytest

from core.cost_model import CostModel
from core.engine import BacktestEngine, ConversionRates
from strategies.base_strategy import BaseStrategy
from test_backtest_models import instrument, simulation_metadata


class ScriptedStrategy(BaseStrategy):
    """Emit a prescribed instruction only at its completed-prefix length."""

    def __init__(self, instructions):
        super().__init__()
        self.instructions = instructions
        self.seen = []

    def generate_signals(self, df):
        self.seen.append(df.index[-1])
        output = pd.DataFrame({"signal": 0, "exit": False}, index=df.index)
        for key, value in self.instructions.get(len(df), {}).items():
            if key not in output:
                output[key] = float("nan")
            output.loc[df.index[-1], key] = value
        return output

@pytest.fixture
def bars():
    return pd.DataFrame({"open": [100., 102., 110., 112.],
                         "high": [101., 105., 113., 114.],
                         "low": [99., 101., 109., 111.],
                         "close": [100., 104., 112., 113.]},
                        index=pd.date_range("2024-01-01", periods=4, freq="h", tz="UTC"))


def engine(metadata, costs=None, capital=10000, account="USD"):
    return BacktestEngine(metadata, costs or CostModel(0, 0, 0),
                          initial_capital=capital, account_currency=account, quantity=1)


def run(model, bars, instructions, **kwargs):
    return model.run(bars, ScriptedStrategy(instructions), expected_timestamps=bars.index, **kwargs)


def test_fee_trade_hand_calculation_and_timing(simulation_metadata, bars):
    model = engine(simulation_metadata, CostModel(2, 0.1, 3))
    strategy = ScriptedStrategy({1: {"signal": 1}, 2: {"exit": True}})
    original = bars.copy(deep=True)
    result = model.run(bars, strategy, expected_timestamps=bars.index)
    entry, exit_fill = result.fills
    assert entry.price == pytest.approx(103.1)  # next open 102 + half spread 1 + slippage .1
    assert exit_fill.price == pytest.approx(108.9)  # next open 110 - 1 - .1
    assert entry.timestamp == bars.index[1]
    assert exit_fill.timestamp == bars.index[2]
    assert result.orders[0].submitted_at == bars.index[0] + pd.Timedelta("1h")
    assert result.trades[0].gross_pnl == pytest.approx(58)  # (108.9 - 103.1) * 10
    assert result.trades[0].net_pnl == pytest.approx(52)  # two commissions of 3
    assert result.states[-1].balance == pytest.approx(10052)
    assert result.states[1].unrealized_pnl == pytest.approx(-1)  # Bid close 103 vs entry 103.1
    assert result.states[1].balance == 9997
    assert result.states[-1].equity == pytest.approx(10052)
    assert strategy.seen == list(bars.index)
    pd.testing.assert_frame_equal(bars, original)
    assert result == run(model, bars, {1: {"signal": 1}, 2: {"exit": True}})


def test_zero_holds_and_last_order_is_unfilled(simulation_metadata, bars):
    result = run(engine(simulation_metadata), bars, {1: {"signal": 1}, 4: {"exit": True}})
    assert len(result.fills) == 1
    assert result.open_position is not None
    assert result.states[-1].balance == 10000
    assert result.states[-1].unrealized_pnl == 110  # (113 - 102) * 10
    assert result.events[-1]["status"] == "unfilled"
    assert result.events[-1]["reason"] == "end_of_data"


def test_rejections_are_logged_without_charging_costs(simulation_metadata, bars):
    result = run(engine(simulation_metadata, CostModel(0, 0, 3), capital=100), bars,
                 {1: {"signal": 1}, 2: {"exit": True}})
    assert not result.fills
    assert result.states[-1].balance == 100
    rejected = [event for event in result.events if event["status"] == "rejected"]
    assert "Insufficient" in rejected[0]["reason"]
    assert rejected[1]["reason"] == "no_open_position"
    assert len(result.fills) == 0


def test_schedule_with_shifted_boundaries_is_rejected(simulation_metadata, bars):
    result = run(engine(simulation_metadata), bars, {})
    assert len(result.states) == len(bars)
    bad_schedule = bars.index + pd.Timedelta("1h")
    with pytest.raises(ValueError):
        engine(simulation_metadata).run(bars, ScriptedStrategy({}), expected_timestamps=bad_schedule)


@pytest.mark.parametrize("signal,sl,tp,expected", [(1, 101.5, 104, -5), (-1, 104, 101.5, -20)])
def test_same_bar_brackets_sl_first(simulation_metadata, bars, signal, sl, tp, expected):
    result = run(engine(simulation_metadata), bars, {1: {"signal": signal, "sl": sl, "tp": tp}})
    assert len(result.trades) == 1
    assert result.trades[0].net_pnl == expected
    assert result.fills[-1].ambiguous
    assert result.fills[-1].timing == "intrabar"


@pytest.mark.parametrize("price_type,offset", [("Mid", 0), ("Bid", -1), ("Ask", 1)])
def test_same_executable_prices_without_double_spread(simulation_metadata, bars, price_type, offset):
    simulation_metadata["price_type"]["value"] = price_type
    shifted = bars + offset
    result = run(engine(simulation_metadata, CostModel(2, 0, 0)), shifted,
                 {1: {"signal": 1}, 2: {"exit": True}})
    assert result.fills[0].price == 103
    assert result.fills[1].price == 109
    assert result.trades[0].net_pnl == 60


def test_close_labeled_bars_and_weekend_next_available_open(simulation_metadata, bars):
    simulation_metadata["timestamp_kind"]["value"] = "close"
    bars.index = bars.index + pd.Timedelta("1h")
    result = run(engine(simulation_metadata), bars, {1: {"signal": 1}})
    assert result.orders[0].submitted_at == bars.index[0]
    assert result.fills[0].timestamp == bars.index[1] - pd.Timedelta("1h")
    simulation_metadata["timestamp_kind"]["value"] = "open"
    bars.index = pd.DatetimeIndex(["2024-01-05 21:00Z", "2024-01-07 22:00Z",
                                   "2024-01-07 23:00Z", "2024-01-08 00:00Z"])
    result = run(engine(simulation_metadata), bars, {1: {"signal": 1}})
    assert result.fills[0].timestamp == bars.index[1]


def test_currency_rates_never_use_future(simulation_metadata, bars):
    rates = pd.Series([2., 3.], index=bars.index[[0, 2]])
    result = run(engine(simulation_metadata, account="EUR"), bars,
                 {1: {"signal": 1}, 2: {"exit": True}}, conversion_rates=rates)
    assert result.trades[0].net_pnl == 240  # (110 - 102) * 10 * exit FX 3
    assert result.states[1].reserved_capital == 2040  # entry 102 * 10 * available FX 2
    with pytest.raises(ValueError, match="No conversion rate"):
        run(engine(simulation_metadata, account="EUR"), bars, {}, conversion_rates=rates.iloc[1:])
    with pytest.raises(ValueError, match="required"):
        run(engine(simulation_metadata, account="EUR"), bars, {})


def test_future_candles_do_not_change_earlier_outputs(simulation_metadata, bars):
    class CausalStrategy(BaseStrategy):
        def generate_signals(self, df):
            return pd.DataFrame({"signal": (df.close > 103).astype(int)}, index=df.index)

    model = engine(simulation_metadata)
    original = model.run(bars, CausalStrategy(), expected_timestamps=bars.index)
    altered = bars.copy()
    altered.iloc[-1] = [500., 600., 400., 550.]
    changed = model.run(altered, CausalStrategy(), expected_timestamps=altered.index)
    assert original.states[:-1] == changed.states[:-1]
    assert original.fills[:1] == changed.fills[:1]


@pytest.mark.parametrize("defect", ["duplicate", "unordered", "missing", "ohlc", "metadata"])
def test_invalid_data_blocks_simulation(simulation_metadata, bars, defect):
    expected = bars.index.copy()
    if defect == "duplicate":
        bars.index = pd.DatetimeIndex([bars.index[0], bars.index[0], *bars.index[2:]])
    elif defect == "unordered":
        bars = bars.iloc[::-1]
    elif defect == "missing":
        bars = bars.iloc[[0, 2, 3]]
    elif defect == "ohlc":
        bars.iloc[0, bars.columns.get_loc("high")] = 1
    else:
        simulation_metadata["price_type"]["confirmed"] = False
    with pytest.raises(ValueError):
        engine(simulation_metadata).run(bars, ScriptedStrategy({}), expected_timestamps=expected)


def test_existing_position_and_bad_gap_bracket_rejected(simulation_metadata, bars):
    result = run(engine(simulation_metadata), bars,
                 {1: {"signal": 1}, 2: {"signal": -1}})
    assert len(result.fills) == 1
    assert any(e["reason"] == "position_already_open" for e in result.events)
    result = run(engine(simulation_metadata), bars, {1: {"signal": 1, "tp": 101}})
    assert not result.fills
    assert any("bracket" in e["reason"] for e in result.events)


def test_stop_uses_bid_for_long_and_costs_once(simulation_metadata, bars):
    # At entry, Ask=103. During that candle Mid low=101 but Bid low=100.
    # A long stop at 100.5 must trigger on Bid even though Mid never reaches it.
    result = run(engine(simulation_metadata, CostModel(2, 0, 3)), bars,
                 {1: {"signal": 1, "sl": 100.5}})
    assert result.fills[-1].reason == "stop_loss"
    assert result.fills[-1].price == 100.5
    assert result.trades[0].net_pnl == -31  # (100.5 - 103) * 10 - 6


def test_short_stop_uses_ask(simulation_metadata, bars):
    # SELL at Bid=101; Ask high=106 reaches 105.5 while Mid high=105 does not.
    result = run(engine(simulation_metadata, CostModel(2, 0, 0)), bars,
                 {1: {"signal": -1, "sl": 105.5}})
    assert result.trades[0].net_pnl == -45
    assert result.fills[-1].reason == "stop_loss"


def test_gap_stop_fills_open_and_tp_does_not_use_better_gap_price(simulation_metadata, bars):
    bars.iloc[2] = [90., 95., 89., 92.]
    result = run(engine(simulation_metadata, CostModel(0, 0.1, 0)), bars,
                 {1: {"signal": 1, "sl": 100}})
    assert result.fills[-1].reason == "stop_loss_gap"
    assert result.fills[-1].price == pytest.approx(89.9)
    assert result.trades[0].net_pnl == pytest.approx(-122)
    bars.iloc[2] = [110., 113., 109., 112.]
    result = run(engine(simulation_metadata), bars, {1: {"signal": 1, "tp": 108}})
    assert result.fills[-1].price == 108
    assert result.fills[-1].reason == "take_profit_gap"


def test_future_conversion_during_bar_not_used_for_stop(simulation_metadata, bars):
    rates = pd.Series([2., 9.], index=pd.DatetimeIndex([
        bars.index[0], bars.index[1] + pd.Timedelta("30min")]))
    result = run(engine(simulation_metadata, account="EUR"), bars,
                 {1: {"signal": 1, "sl": 101.5}}, conversion_rates=rates)
    assert result.trades[0].net_pnl == -10  # -.5 * 10 * known opening FX 2


def test_prefix_isolation_and_strategy_output_validation(simulation_metadata, bars):
    class MutatingStrategy(BaseStrategy):
        def generate_signals(self, df):
            df.iloc[-1, 0] = 99999
            return pd.DataFrame({"signal": 0}, index=df.index)

    before = bars.copy(deep=True)
    engine(simulation_metadata).run(bars, MutatingStrategy(), expected_timestamps=bars.index)
    pd.testing.assert_frame_equal(before, bars)

    class BadStrategy(BaseStrategy):
        def generate_signals(self, df):
            return pd.DataFrame({"signal": [1]})

    with pytest.raises(ValueError, match="aligned unique"):
        engine(simulation_metadata).run(bars, BadStrategy(), expected_timestamps=bars.index)
    with pytest.raises(ValueError, match="EXIT and entry"):
        run(engine(simulation_metadata), bars, {1: {"signal": 1, "exit": True}})


def test_incremental_strategy_api_matches_batch_output(simulation_metadata, bars):
    class IncrementalStrategy(BaseStrategy):
        def __init__(self):
            super().__init__()
            self.count = 0

        def generate_signals(self, df):
            raise AssertionError("Incremental strategy must not rebuild batch output")

        def generate_signal(self, completed_data):
            self.count += 1
            return pd.Series({"signal": int(completed_data.close.iloc[-1] > 105), "exit": False})

    result = engine(simulation_metadata).run(
        bars, IncrementalStrategy(), expected_timestamps=bars.index)
    assert len(result.states) == len(bars)
    assert len(result.orders) == 2


def test_insolvency_is_reported_for_extreme_short_gap(simulation_metadata, bars):
    bars.iloc[2] = [2000., 2100., 1900., 2000.]
    result = run(engine(simulation_metadata, capital=2000), bars,
                 {1: {"signal": -1}, 2: {"exit": True}})
    assert result.states[2].balance == -16980  # 2000 + (102 - 2000) * 10
    assert any(event["status"] == "insolvent" for event in result.events)


@pytest.mark.parametrize("bad_rate", [0, -1, float("nan"), float("inf")])
def test_invalid_conversion_rates(bars, bad_rate):
    with pytest.raises(ValueError, match="Conversion rates"):
        ConversionRates("USD", "EUR", pd.Series([bad_rate], index=bars.index[:1]))
```
<!-- SOURCE_END tests/test_engine.py -->

## File gốc: `tests/test_stage4_review.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_stage4_review.py`

Số dòng: 78; kích thước: 3401 bytes; SHA256: `611717b706e4ff73e8a6f2a15e3d217aff2c1327517e4caf2ea0e60c081d6d0c`.

<!-- SOURCE_BEGIN tests/test_stage4_review.py -->
```python
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
```
<!-- SOURCE_END tests/test_stage4_review.py -->
