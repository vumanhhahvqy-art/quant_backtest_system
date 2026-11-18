"""Manually verifiable quality checks, calendar handling and reproducibility."""

import copy
import json

import numpy as np
import pandas as pd
import pytest

from core.data_validator import save_report, validate_data
from test_data_loader import metadata


@pytest.fixture
def candles():
    return pd.DataFrame({"open": [1., 2., 3.], "high": [2., 3., 4.],
                         "low": [0.5, 1., 2.], "close": [1.5, 2.5, 3.5],
                         "volume": [0., 1., 2.]},
                        index=pd.date_range("2024-01-01", periods=3, freq="min", tz="UTC", name="timestamp"))


def test_clean_data_ready_without_calendar_but_not_calendar_verified(candles, metadata):
    original = candles.copy(deep=True)
    report = validate_data(candles, metadata, expected_timestamps=candles.index)
    assert report["ready_for_research"]
    assert report["errors"] == {}
    simple = validate_data(candles, metadata)
    assert simple["status"] == "ready"
    assert simple["intraday_gap_check_passed"]
    assert not simple["full_calendar_verified"]
    assert report["full_calendar_verified"]
    pd.testing.assert_frame_equal(candles, original)
    assert report == validate_data(candles, metadata, expected_timestamps=candles.index)


@pytest.mark.parametrize("column,value,error", [
    ("open", np.nan, "open_missing_or_non_numeric"),
    ("close", np.inf, "close_infinite"),
    ("low", 0, "low_invalid_sign"),
    ("open", -1, "open_invalid_sign"),
    ("volume", -1, "volume_invalid_sign"),
    ("high", 0.75, "invalid_ohlc"),
    ("low", 1.75, "invalid_ohlc"),
])
def test_bad_numeric_values(candles, metadata, column, value, error):
    candles.iloc[0, candles.columns.get_loc(column)] = value
    report = validate_data(candles, metadata)
    assert report["errors"][error]["count"] == 1
    assert report["errors"][error]["example_data_rows"] == [1]
    assert not report["ready_for_research"]


def test_duplicates_unsorted_and_nat(candles, metadata):
    candles.index = pd.DatetimeIndex([candles.index[1], candles.index[0], candles.index[0]])
    report = validate_data(candles, metadata)
    assert report["errors"]["duplicate_timestamps"]["count"] == 2
    assert "unordered_timestamps" in report["errors"]
    candles.index = pd.DatetimeIndex([candles.index[0], pd.NaT, candles.index[2]])
    assert validate_data(candles, metadata)["errors"]["invalid_timestamps"]["count"] == 1


def test_gap_candidates_do_not_imply_market_missing(candles, metadata):
    sparse = candles.iloc[[0, 2]]
    report = validate_data(sparse, metadata)
    assert report["interval_analysis"]["candidate_gap_count"] == 1
    assert report["interval_analysis"]["candidate_missing_slots"] == 1
    assert "missing_expected_candles" not in report["errors"]
    confirmed = validate_data(sparse, metadata, expected_timestamps=candles.index)
    assert confirmed["errors"]["missing_expected_candles"]["count"] == 1
    assert not confirmed["ready_for_research"]


def test_closed_session_gap_is_accepted_with_explicit_calendar(candles, metadata):
    candles.index = pd.DatetimeIndex(["2024-01-05 21:59Z", "2024-01-07 22:00Z", "2024-01-07 22:01Z"])
    report = validate_data(candles, metadata, expected_timestamps=candles.index)
    assert report["interval_analysis"]["candidate_gap_count"] == 0
    assert report["ready_for_research"]


def test_unknown_metadata_blocks_readiness(candles, metadata):
    metadata["price_type"]["confirmed"] = False
    metadata["instrument_specifications"]["value"]["contract_size"] = None
    report = validate_data(candles, metadata, expected_timestamps=candles.index)
    assert report["structural_checks_passed"]
    assert not report["ready_for_research"]
    assert "Unconfirmed metadata: price_type" in report["metadata_blockers"]


def test_empty_missing_columns_and_non_utc(candles, metadata):
    assert "empty_dataset" in validate_data(candles.iloc[:0], metadata)["errors"]
    assert validate_data(candles.drop(columns="open"), metadata)["errors"]["missing_columns"] == ["open"]
    candles.index = candles.index.tz_localize(None)
    assert "timestamp_index" in validate_data(candles, metadata)["errors"]


def test_report_export_is_reproducible_and_no_overwrite(tmp_path, candles, metadata):
    report = validate_data(candles, metadata)
    target = tmp_path / "quality.json"
    save_report(report, str(target))
    assert json.loads(target.read_text(encoding="utf-8")) == report
    with pytest.raises(FileExistsError):
        save_report(report, str(target))