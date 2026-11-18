# 05C_TESTS_DATA

Toàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.

## File gốc: `tests/test_data_loader.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_data_loader.py`

Số dòng: 154; kích thước: 6705 bytes; SHA256: `3cc3774987d25aa1206b5c88e5603a7b743ef0a3d7a5915b8cb32edb6084930f`.

<!-- SOURCE_BEGIN tests/test_data_loader.py -->
```python
"""Synthetic parsing, preservation and explicit timestamp interpretation tests."""

import copy
from pathlib import Path

import pandas as pd
import pytest

from core.data_loader import (
    load_csv, load_parquet, read_metadata, save_parquet, sha256_file, write_json,
)


@pytest.fixture
def metadata() -> dict:
    """Use synthetic confirmed specifications, never real instrument claims."""
    values = {
        "source": "synthetic", "symbol": "TEST", "source_timezone": "UTC",
        "timestamp_encoding": "unix_ms", "timestamp_kind": "open",
        "price_type": "Bid", "timeframe": "1min",
        "instrument_specifications": {"tick_size": 0.01, "pip_size": 0.1,
            "contract_size": 1, "quantity_unit": "units", "quote_currency": "USD",
            "minimum_quantity_increment": 1},
        "volume_unit": "synthetic_units",
    }
    return {"schema_version": 1, **{key: {"value": value, "confirmed": True,
                                         "evidence": "Synthetic test fixture"}
                                   for key, value in values.items()}}


def make_csv(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "input.csv"
    path.write_text("timestamp,open,high,low,close,volume\n" + rows, encoding="utf-8")
    return path


def test_round_trip_preserves_rows_and_raw(tmp_path, metadata):
    path = make_csv(tmp_path, "1704067260000,2,3,1,2,0\n1704067200000,1,2,1,2,5\n")
    before = sha256_file(path)
    result = load_csv(path, metadata)
    assert result.data.index[0] == pd.Timestamp("2024-01-01 00:01Z")
    assert result.data.index[1] == pd.Timestamp("2024-01-01 00:00Z")
    assert result.data.open.tolist() == [2.0, 1.0]
    output = tmp_path / "output.parquet"
    save_parquet(result.data, output)
    pd.testing.assert_frame_equal(result.data, load_parquet(output))
    assert sha256_file(path) == before
    with pytest.raises(FileExistsError):
        save_parquet(result.data, output)
    with pytest.raises(ValueError, match="raw"):
        save_parquet(result.data, tmp_path / "raw" / "output.parquet")


def test_parquet_failure_leaves_no_partial_or_temporary_file(tmp_path, monkeypatch):
    data = pd.DataFrame({"close": [1.]}, index=pd.date_range("2024-01-01", periods=1, tz="UTC"))
    output = tmp_path / "failed.parquet"
    def fail_write(*args, **kwargs):
        args[1].write(b"partial parquet contents")
        raise OSError("synthetic disk failure")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", fail_write)
    with pytest.raises(OSError, match="synthetic"):
        save_parquet(data, output)
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []


def test_parquet_publication_failure_cleans_temp_and_preserves_existing(tmp_path, monkeypatch):
    import core.data_loader as loader

    data = pd.DataFrame({"close": [1.]}, index=pd.date_range("2024-01-01", periods=1, tz="UTC"))
    output = tmp_path / "existing.parquet"
    output.write_bytes(b"previous artifact")
    with pytest.raises(FileExistsError):
        save_parquet(data, output)
    assert output.read_bytes() == b"previous artifact"
    assert list(tmp_path.iterdir()) == [output]

    def fail_publish(*args):
        raise OSError("synthetic publication failure")

    monkeypatch.setattr(loader.os, "link", fail_publish)
    with pytest.raises(OSError, match="publication"):
        save_parquet(data, tmp_path / "new.parquet")
    assert list(tmp_path.iterdir()) == [output]


def test_invalid_tokens_are_reported_not_removed(tmp_path, metadata):
    path = make_csv(tmp_path, "bad,wrong,2,1,1,\n1704067200000,1,2,1,1,0\n")
    result = load_csv(path, metadata)
    assert len(result.data) == 2
    assert pd.isna(result.data.index[0])
    assert pd.isna(result.data.open.iloc[0])
    assert result.diagnostics["invalid_timestamps"]["examples"] == [{"data_row": 1, "token": "bad"}]
    assert result.diagnostics["numeric_parsing"]["open"]["count"] == 1
    output = tmp_path / "invalid.parquet"
    save_parquet(result.data, output)
    pd.testing.assert_frame_equal(result.data, load_parquet(output))


def test_unconfirmed_encoding_requires_diagnostic_mode(tmp_path, metadata):
    path = make_csv(tmp_path, "1704067200000,1,2,1,1,1\n")
    metadata["timestamp_encoding"]["confirmed"] = False
    with pytest.raises(ValueError, match="Confirm"):
        load_csv(path, metadata)
    assert len(load_csv(path, metadata, diagnostic=True).data) == 1
    metadata["timestamp_encoding"]["value"] = None
    with pytest.raises(ValueError, match="Declare"):
        load_csv(path, metadata, diagnostic=True)


def test_missing_columns_and_mapping(tmp_path, metadata):
    path = tmp_path / "mapped.csv"
    path.write_text("Time;Open;high;low;close\n1704067200000;1;2;1;1\n")
    with pytest.raises(ValueError, match="Missing required"):
        load_csv(path, metadata, delimiter=";")
    result = load_csv(path, metadata, delimiter=";", column_map={"Time": "timestamp", "Open": "open"})
    assert result.data.open.iloc[0] == 1


def test_explicit_local_timezone_and_dst(tmp_path, metadata):
    metadata["timestamp_encoding"]["value"] = "local"
    metadata["source_timezone"]["value"] = "America/New_York"
    metadata["timestamp_format"] = "%Y-%m-%d %H:%M"
    path = make_csv(tmp_path, "2024-01-01 00:00,1,2,1,1,1\n2024-03-10 02:30,1,2,1,1,1\n2024-11-03 01:30,1,2,1,1,1\n")
    result = load_csv(path, metadata)
    assert result.data.index[0] == pd.Timestamp("2024-01-01 05:00Z")
    assert result.diagnostics["invalid_timestamps"]["count"] == 2
    metadata["source_timezone"]["value"] = None
    with pytest.raises(ValueError, match="source_timezone"):
        load_csv(path, metadata)


def test_aware_strings_do_not_accept_naive_values(tmp_path, metadata):
    metadata["timestamp_encoding"]["value"] = "aware"
    metadata["timestamp_format"] = "%Y-%m-%dT%H:%M%z"
    path = make_csv(tmp_path, "2024-01-01T02:00+0200,1,2,1,1,1\n2024-01-01T02:00,1,2,1,1,1\n")
    result = load_csv(path, metadata)
    assert result.data.index[0] == pd.Timestamp("2024-01-01 00:00Z")
    assert pd.isna(result.data.index[1])


def test_metadata_and_json_no_overwrite(tmp_path, metadata):
    path = tmp_path / "metadata.json"
    write_json(path, metadata)
    assert read_metadata(path) == metadata
    with pytest.raises(FileExistsError):
        write_json(path, metadata)
    invalid = copy.deepcopy(metadata)
    invalid.pop("source")
    other = tmp_path / "invalid.json"
    write_json(other, invalid)
    with pytest.raises(ValueError, match="source"):
        read_metadata(other)
```
<!-- SOURCE_END tests/test_data_loader.py -->

## File gốc: `tests/test_data_validator.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_data_validator.py`

Số dòng: 102; kích thước: 4612 bytes; SHA256: `a34c3fbebae332d582b4152c7ebc7a4e5530845e12d809381d790d953153d1a5`.

<!-- SOURCE_BEGIN tests/test_data_validator.py -->
```python
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
```
<!-- SOURCE_END tests/test_data_validator.py -->

## File gốc: `tests/test_intraday_gaps.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_intraday_gaps.py`

Số dòng: 90; kích thước: 4582 bytes; SHA256: `519e1e8d0a60fa174af2b8280b3921750fd0b1bd29fd3f0b3f154323ca5a0c57`.

<!-- SOURCE_BEGIN tests/test_intraday_gaps.py -->
```python
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
```
<!-- SOURCE_END tests/test_intraday_gaps.py -->
