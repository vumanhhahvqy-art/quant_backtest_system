"""Explicit CSV parsing and lossless-row diagnostic normalization to UTC.

Invalid numeric tokens become NaN and invalid timestamps become NaT. Their
original row numbers and tokens are retained in the load diagnostics. No rows
are sorted, removed, or filled. Diagnostic output is not research-ready data.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import logging
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np
import pandas as pd
import yaml

LOGGER = logging.getLogger(__name__)
PRICE_COLUMNS = ("open", "high", "low", "close")
REQUIRED_COLUMNS = ("timestamp", *PRICE_COLUMNS)
METADATA_FIELDS = (
    "source", "symbol", "source_timezone", "timestamp_encoding",
    "timestamp_kind", "price_type", "timeframe", "instrument_specifications",
)
SPECIFICATION_FIELDS = (
    "tick_size", "pip_size", "contract_size", "quantity_unit", "quote_currency",
    "minimum_quantity_increment",
)


@dataclass
class LoadResult:
    """Parsed rows and bounded diagnostics; row positions are one-based CSV data rows."""

    data: pd.DataFrame
    diagnostics: dict[str, Any]


def sha256_file(path: str | Path) -> str:
    """Hash a file without loading its entire contents into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_metadata(path: str | Path) -> dict[str, Any]:
    """Read versioned JSON metadata. Each important field needs explicit confirmation."""
    metadata_path = Path(path)
    with metadata_path.open(encoding="utf-8") as stream:
        metadata = (yaml.safe_load(stream) if metadata_path.suffix.lower() in {".yaml", ".yml"}
                    else json.load(stream))
    if metadata.get("schema_version") != 1:
        raise ValueError("Metadata schema_version must be 1.")
    for field in METADATA_FIELDS:
        item = metadata.get(field)
        if not isinstance(item, dict) or not {"value", "confirmed", "evidence"} <= item.keys():
            raise ValueError(f"Metadata field {field!r} needs value, confirmed and evidence.")
        if type(item["confirmed"]) is not bool:
            raise ValueError(f"Metadata field {field!r}: confirmed must be boolean.")
    return metadata


def metadata_blockers(metadata: dict[str, Any]) -> list[str]:
    """List unresolved research requirements; never trust filename hints as facts."""
    blockers = []
    for field in METADATA_FIELDS:
        item = metadata.get(field, {})
        if item.get("confirmed") is not True or item.get("value") in (None, "", {}):
            blockers.append(f"Unconfirmed metadata: {field}")
        elif not item.get("evidence"):
            blockers.append(f"Missing confirmation evidence: {field}")
    values = {key: metadata.get(key, {}).get("value") for key in METADATA_FIELDS}
    if values["price_type"] not in ("Bid", "Ask", "Mid"):
        blockers.append("price_type must be Bid, Ask or Mid")
    if values["timestamp_kind"] not in ("open", "close"):
        blockers.append("timestamp_kind must be open or close")
    specs = values["instrument_specifications"]
    if not isinstance(specs, dict):
        blockers.append("Instrument specifications are missing")
    else:
        for key in SPECIFICATION_FIELDS:
            value = specs.get(key)
            if value is None or value == "":
                blockers.append(f"Missing instrument specification: {key}")
            elif key in ("tick_size", "pip_size", "contract_size", "minimum_quantity_increment"):
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
                    blockers.append(f"Invalid positive instrument specification: {key}")
    return blockers


def _issue_details(raw: pd.Series, mask: pd.Series) -> dict[str, Any]:
    return {
        "count": int(mask.sum()),
        "examples": [
            {"data_row": int(i) + 1, "token": str(raw.loc[i])}
            for i in raw.index[mask][:10]
        ],
    }


def load_csv(
    path: str | Path,
    metadata: dict[str, Any],
    *,
    diagnostic: bool = False,
    column_map: dict[str, str] | None = None,
    delimiter: str = ",",
) -> LoadResult:
    """Parse CSV using declared encoding (unix_s/ms/us/ns, aware, or local).

    'aware' and 'local' require an explicit strptime timestamp_format. Local
    timestamps additionally require source_timezone; ambiguous/nonexistent DST
    times become NaT and are reported. Unconfirmed timestamp assumptions are
    allowed only in diagnostic mode. Numeric volume units remain metadata-only.
    """
    path = Path(path).resolve()
    encoding_info = metadata.get("timestamp_encoding", {})
    encoding = encoding_info.get("value")
    if not diagnostic and encoding_info.get("confirmed") is not True:
        raise ValueError("Confirm timestamp_encoding or use diagnostic=True explicitly.")
    if encoding not in ("unix_s", "unix_ms", "unix_us", "unix_ns", "aware", "local"):
        raise ValueError("Declare timestamp_encoding: unix_s/ms/us/ns, aware, or local.")
    timezone_info = metadata.get("source_timezone", {})
    if encoding == "local" and (
        not timezone_info.get("value")
        or (not diagnostic and timezone_info.get("confirmed") is not True)
    ):
        raise ValueError("Local timestamps require an explicitly declared source_timezone.")
    LOGGER.info("Loading CSV %s (diagnostic=%s)", path, diagnostic)
    raw = pd.read_csv(path, sep=delimiter, dtype=str, keep_default_na=False,
                      skip_blank_lines=False)
    if column_map:
        raw = raw.rename(columns=column_map)
    if not raw.columns.is_unique:
        raise ValueError("Column mapping creates duplicate column names.")
    missing = set(REQUIRED_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
    data = raw.copy()
    token = raw["timestamp"]
    if encoding.startswith("unix_"):
        numeric = pd.to_numeric(token, errors="coerce")
        timestamp = pd.to_datetime(numeric, unit=encoding.removeprefix("unix_"),
                                   origin="unix", utc=True, errors="coerce")
    else:
        timestamp_format = metadata.get("timestamp_format")
        if not timestamp_format:
            raise ValueError("Text timestamps require an explicit timestamp_format.")
        if encoding == "aware":
            # %z prevents naive strings from silently being interpreted as UTC.
            if "%z" not in timestamp_format:
                raise ValueError("Aware timestamp_format must include %z.")
            timestamp = pd.to_datetime(token, format=timestamp_format, utc=True, errors="coerce")
        else:
            if "%z" in timestamp_format or "%Z" in timestamp_format:
                raise ValueError("Local timestamp_format must not contain a timezone.")
            timestamp = pd.to_datetime(token, format=timestamp_format, errors="coerce")
            timestamp = timestamp.dt.tz_localize(
                timezone_info["value"], ambiguous="NaT", nonexistent="NaT"
            ).dt.tz_convert("UTC")
    data["timestamp"] = timestamp
    diagnostics: dict[str, Any] = {
        "source_path": str(path), "row_count": len(raw),
        "source_columns": list(raw.columns),
        "source_inferred_dtypes": {
            column: str(pd.to_numeric(raw[column], errors="coerce").dtype)
            if column in (*PRICE_COLUMNS, "volume", "timestamp") else "string"
            for column in raw.columns
        },
        "timestamp_encoding_used": encoding,
        "timestamp_encoding_confirmed": encoding_info.get("confirmed") is True,
        "diagnostic_mode": diagnostic,
        "invalid_timestamps": _issue_details(token, timestamp.isna()),
        "numeric_parsing": {},
    }
    for column in (*PRICE_COLUMNS, "volume"):
        if column not in raw:
            continue
        numeric = pd.to_numeric(raw[column], errors="coerce").astype("float64")
        data[column] = numeric
        diagnostics["numeric_parsing"][column] = _issue_details(raw[column], numeric.isna())
    data = data.set_index("timestamp")
    diagnostics["normalized_dtypes"] = {key: str(value) for key, value in data.dtypes.items()}
    diagnostics["timestamp_dtype"] = str(data.index.dtype)
    return LoadResult(data, diagnostics)


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a new JSON artifact; never overwrite an existing report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def save_parquet(data: pd.DataFrame, path: str | Path) -> None:
    """Atomically save UTC-indexed rows without replacing existing output."""
    path = Path(path).resolve()
    if "raw" in path.parts:
        raise ValueError("Output must not be inside a raw directory.")
    if not isinstance(data.index, pd.DatetimeIndex) or str(data.index.tz) != "UTC":
        raise ValueError("Parquet data must have a timezone-aware UTC DatetimeIndex.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            data.to_parquet(stream, engine="pyarrow", index=True)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic no-clobber publication on the same filesystem.
        os.link(temporary_path, path)
    except FileExistsError:
        raise FileExistsError(f"Refusing to overwrite existing output: {path}") from None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_parquet(path: str | Path) -> pd.DataFrame:
    """Read normalized Parquet and require the same UTC index convention."""
    data = pd.read_parquet(path, engine="pyarrow")
    if not isinstance(data.index, pd.DatetimeIndex) or str(data.index.tz) != "UTC":
        raise ValueError("Parquet does not have a timezone-aware UTC DatetimeIndex.")
    missing = set(PRICE_COLUMNS) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required Parquet columns: {sorted(missing)}")
    return data