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