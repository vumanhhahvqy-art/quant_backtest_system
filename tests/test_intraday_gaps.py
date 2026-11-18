"""Simple UTC-day gap policy and next-observed-candle execution regression."""

import numpy as np
import pandas as pd
import pytest

from core.data_validator import validate_data
from test_backtest_models import simulation_metadata
from test_engine import ScriptedStrategy, engine


def make_candles(timestamps):
    index = pd.DatetimeIndex(timestamps)
    return pd.DataFrame({"open": [100., 110.], "high": [101., 111.],
                         "low": [99., 109.], "close": [100., 110.]}, index=index)


@pytest.mark.parametrize("timestamps,gaps,missing,ignored", [
    (["2024-01-02 10:00Z", "2024-01-02 11:00Z"], 0, 0, 0),
    (["2024-01-02 10:00Z", "2024-01-02 14:00Z"], 1, 3, 0),
    (["2024-01-05 21:00Z", "2024-01-07 22:00Z"], 0, 0, 1),
    (["2024-12-24 21:00Z", "2024-12-26 07:00Z"], 0, 0, 1),
    (["2024-01-02 22:00Z", "2024-01-03 03:00Z"], 0, 0, 1),
])
def test_simple_gap_report_and_actual_next_open(simulation_metadata, timestamps, gaps, missing, ignored):
    data = make_candles(timestamps)
    before = data.copy(deep=True)
    report = validate_data(data, simulation_metadata)
    analysis = report["interval_analysis"]
    assert not report["errors"] and not report["metadata_blockers"]
    assert report["ready_for_research"]
    assert report["gap_check_mode"] == "intraday_only"
    assert not report["full_calendar_verified"]
    assert report["intraday_gap_check_passed"] == (gaps == 0)
    assert analysis["candidate_gap_count"] == gaps
    assert analysis["candidate_missing_slots"] == missing
    assert analysis["cross_day_interval_count_ignored"] == ignored
    if gaps:
        gap = analysis["intraday_gaps"][0]
        assert gap["start_utc"] == data.index[0].isoformat()
        assert gap["end_utc"] == data.index[1].isoformat()
        assert gap["candidate_missing_slots"] == 3
        assert any("intraday" in warning for warning in report["warnings"])
    result = engine(simulation_metadata).run(data, ScriptedStrategy({1: {"signal": 1}}))
    assert len(result.states) == 2 and len(result.fills) == 1
    assert result.fills[0].timestamp == data.index[1]
    assert result.fills[0].price == 110
    assert result.orders[0].submitted_at == data.index[0] + pd.Timedelta("1h")
    assert result.assumptions["full_calendar_verified"] is False
    assert result.assumptions["interval_analysis"] == analysis
    pd.testing.assert_frame_equal(data, before)


def test_explicit_calendar_remains_strict_and_independent(simulation_metadata):
    data = make_candles(["2024-01-02 10:00Z", "2024-01-02 14:00Z"])
    schedule = pd.date_range("2024-01-02 10:00Z", periods=5, freq="h")
    report = validate_data(data, simulation_metadata, expected_timestamps=schedule)
    assert report["gap_check_mode"] == "full_calendar"
    assert not report["full_calendar_verified"]
    assert report["errors"]["missing_expected_candles"]["count"] == 3
    with pytest.raises(ValueError, match="simulation-ready"):
        engine(simulation_metadata).run(data, ScriptedStrategy({}), expected_timestamps=schedule)


@pytest.mark.parametrize("defect", ["duplicate", "reverse", "nan", "inf", "ohlc", "negative"])
def test_mandatory_validation_still_blocks_without_calendar(simulation_metadata, defect):
    data = make_candles(["2024-01-02 10:00Z", "2024-01-02 14:00Z"])
    if defect == "duplicate":
        data.index = pd.DatetimeIndex([data.index[0], data.index[0]])
    elif defect == "reverse":
        data = data.iloc[::-1]
    else:
        column, value = {"nan": ("open", np.nan), "inf": ("close", np.inf),
                         "ohlc": ("high", 1.), "negative": ("low", -1.)}[defect]
        data.iloc[0, data.columns.get_loc(column)] = value
    assert validate_data(data, simulation_metadata)["errors"]
    with pytest.raises(ValueError):
        engine(simulation_metadata).run(data, ScriptedStrategy({}))


def test_nonmultiple_gap_counts_grid_points_and_no_cross_day_warning(simulation_metadata):
    data = make_candles(["2024-01-02 10:00Z", "2024-01-02 12:30Z"])
    report = validate_data(data, simulation_metadata)
    assert report["interval_analysis"]["candidate_missing_slots"] == 2
    assert report["interval_analysis"]["non_multiple_interval_count"] == 1
    assert report["ready_for_research"]
    data.index = pd.DatetimeIndex(["2024-01-02 23:00Z", "2024-01-03 03:30Z"])
    report = validate_data(data, simulation_metadata)
    assert report["interval_analysis"]["non_multiple_interval_count"] == 0
    assert report["intraday_gap_check_passed"]