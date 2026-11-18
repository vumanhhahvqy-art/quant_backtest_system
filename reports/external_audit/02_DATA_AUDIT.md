# Data loader, validator, manager, cấu hình và metadata

Metadata schema hiện được thể hiện qua template YAML và các hàm read_metadata/metadata_blockers, không có JSON Schema riêng.
Registry ghi nhiều trường confirmed=false; không suy ra nguồn/timezone/price side từ tên file.
symbols.json là metadata legacy; Instrument.from_metadata dùng metadata xác nhận và không tự đọc file legacy này.
Không kèm CSV, Parquet hoặc cache JSON giá. inspect_data.py được đóng gói để đọc, không thực thi trong nhiệm vụ này.

## File gốc: `core/data_loader.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\data_loader.py`

Số dòng: 239; kích thước: 10823 bytes; SHA256: `82973a19cc0fca229accd3517c331d99983cdf076b4d786f4f2a14c28e793d11`.

<!-- SOURCE_BEGIN core/data_loader.py -->
```python
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
```
<!-- SOURCE_END core/data_loader.py -->

## File gốc: `core/data_validator.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\data_validator.py`

Số dòng: 199; kích thước: 10363 bytes; SHA256: `99d379352c38a509765d0e0fc7a73b77508bde9e2946cb3f7b467aad749449c4`.

<!-- SOURCE_BEGIN core/data_validator.py -->
```python
"""Non-mutating OHLC checks, intraday gap warnings and optional full calendar."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from core.data_loader import PRICE_COLUMNS, metadata_blockers, write_json


def validate_expected_timestamps(
    expected_timestamps: pd.DatetimeIndex,
    *,
    timeframe: str,
    timestamp_kind: str,
) -> None:
    """Validate an independently generated, exact-window trading schedule.

    This checks the schedule's contract, not its authenticity: callers must
    construct it from a confirmed calendar and the requested date boundaries.
    """
    if (not isinstance(expected_timestamps, pd.DatetimeIndex)
            or str(expected_timestamps.tz) != "UTC"
            or expected_timestamps.hasnans
            or not expected_timestamps.is_unique
            or not expected_timestamps.is_monotonic_increasing):
        raise ValueError("Expected timestamps must be unique, ordered, non-null UTC timestamps.")
    if not len(expected_timestamps):
        raise ValueError("Expected timestamps cannot be empty.")
    if timestamp_kind not in ("open", "close"):
        raise ValueError("timestamp_kind must be open or close.")
    try:
        interval = pd.Timedelta(timeframe)
    except (TypeError, ValueError) as exc:
        raise ValueError("timeframe must be a fixed duration such as '1min'.") from exc
    if interval <= pd.Timedelta(0):
        raise ValueError("timeframe must be positive.")
    # Candle intervals must not overlap; gaps are valid calendar closures.
    if len(expected_timestamps) > 1 and (expected_timestamps[1:] - expected_timestamps[:-1] < interval).any():
        raise ValueError("Expected timestamps describe overlapping candles.")


def validate_data(
    data: pd.DataFrame,
    metadata: dict[str, Any],
    *,
    load_diagnostics: dict[str, Any] | None = None,
    expected_timestamps: pd.DatetimeIndex | None = None,
) -> dict[str, Any]:
    """Report row defects, same-UTC-day gaps and optional calendar coverage.

    Duplicate counts count all participating rows. OHLC comparisons apply only
    to rows with finite prices. Gaps are candidates, not proven missing candles:
    cross-day intervals are ignored by the simple gap policy. Callers may
    optionally supply an authoritative expected UTC timestamp index for this
    exact window. It must be generated independently of the observed rows.
    """
    errors: dict[str, Any] = {}
    warnings: list[str] = []
    blockers = metadata_blockers(metadata)
    report: dict[str, Any] = {
        "row_count": len(data), "errors": errors, "warnings": warnings,
        "metadata_blockers": blockers, "load_diagnostics": load_diagnostics,
        "gap_check_mode": "full_calendar" if expected_timestamps is not None else "intraday_only",
        "intraday_gap_check_passed": False,
        "full_calendar_verified": False,
        "columns": list(data.columns),
        "dtypes": {key: str(value) for key, value in data.dtypes.items()},
        "assumptions": ["No rows sorted, dropped, filled or interpolated.",
                        "Candidate timestamp interpretation must be confirmed before research.",
                        "Simple gap checks ignore intervals crossing UTC dates; they do not prove calendar completeness."],
    }

    def record(name: str, mask: Any) -> None:
        positions = np.flatnonzero(np.asarray(mask, dtype=bool))
        if len(positions):
            errors[name] = {"count": int(len(positions)),
                            "example_data_rows": (positions[:10] + 1).tolist()}

    if data.empty:
        errors["empty_dataset"] = {"count": 1}
    missing = sorted(set(PRICE_COLUMNS) - set(data.columns))
    if missing:
        errors["missing_columns"] = missing
    if not isinstance(data.index, pd.DatetimeIndex) or str(data.index.tz) != "UTC":
        errors["timestamp_index"] = "Requires timezone-aware UTC DatetimeIndex"
    else:
        index = data.index
        record("invalid_timestamps", index.isna())
        record("duplicate_timestamps", index.duplicated(keep=False) & ~index.isna())
        valid = index[~index.isna()]
        report["start_utc"] = valid.min().isoformat() if len(valid) else None
        report["end_utc"] = valid.max().isoformat() if len(valid) else None
        report["chronologically_ordered"] = bool(valid.is_monotonic_increasing)
        if not valid.is_monotonic_increasing:
            errors["unordered_timestamps"] = "Rows are not chronological; not automatically sorted."
        timeframe = metadata.get("timeframe", {}).get("value")
        report["interval_analysis"] = {"declared_timeframe": timeframe}
        if timeframe:
            try:
                interval = pd.Timedelta(timeframe)
            except (TypeError, ValueError) as exc:
                raise ValueError("timeframe must be a fixed duration such as '1min'.") from exc
            if interval <= pd.Timedelta(0):
                raise ValueError("timeframe must be positive.")
            # Compare consecutive input rows only; never sort to repair defects.
            ordered = index
            delta = ordered[1:] - ordered[:-1]
            same_day = (ordered[1:].normalize() == ordered[:-1].normalize())
            positive_pairs = (delta > pd.Timedelta(0)) & same_day
            gap_positions = np.flatnonzero(positive_pairs & (delta > interval))
            irregular = np.flatnonzero(positive_pairs & (delta % interval != pd.Timedelta(0)))
            # Count expected grid points strictly between the observed endpoints.
            missing_counts = {int(i): int((delta[i] - pd.Timedelta(1, unit="ns")) // interval)
                              for i in gap_positions}
            gaps = [
                {"after": ordered[i].isoformat(), "before": ordered[i + 1].isoformat(),
                 "start_utc": ordered[i].isoformat(), "end_utc": ordered[i + 1].isoformat(),
                 "seconds": float(delta[i].total_seconds()),
                 "candidate_missing_slots": missing_counts[int(i)]}
                for i in gap_positions
            ]
            report["intraday_gap_check_passed"] = bool(
                len(index) and not index.hasnans and index.is_unique
                and index.is_monotonic_increasing and not len(gap_positions)
                and not len(irregular)
            )
            gap_info = report["interval_analysis"]
            gap_info.update({
                "timeframe_confirmed": metadata["timeframe"].get("confirmed") is True,
                "candidate_gap_count": int(len(gap_positions)),
                "non_multiple_interval_count": int(len(irregular)),
                "candidate_missing_slots": sum(missing_counts.values()),
                "largest_interval_seconds": float(delta.max().total_seconds()) if len(delta) else None,
                "gap_examples": gaps[:10],
                "intraday_gaps": gaps,
                "cross_day_interval_count_ignored": int(np.count_nonzero(
                    ~same_day & ~ordered[1:].isna() & ~ordered[:-1].isna())),
                "calendar_evaluated": expected_timestamps is not None,
            })
            if len(gap_positions):
                warnings.append("Potential missing intraday candles detected; warning only under the simple UTC-day gap policy.")
            if len(irregular):
                warnings.append("Some timestamp intervals are not multiples of the declared timeframe.")
        else:
            blockers.append("Cannot check intervals without a declared timeframe")
        if expected_timestamps is not None:
            validate_expected_timestamps(
                expected_timestamps,
                timeframe=str(timeframe),
                timestamp_kind=metadata.get("timestamp_kind", {}).get("value"),
            )
            absent = expected_timestamps.difference(valid)
            extra = valid.unique().difference(expected_timestamps)
            report["calendar_check"] = {
                "missing_count": len(absent), "unexpected_count": len(extra),
                "missing_examples": [t.isoformat() for t in absent[:10]],
                "unexpected_examples": [t.isoformat() for t in extra[:10]],
            }
            report["full_calendar_verified"] = bool(
                not len(absent) and not len(extra) and len(index)
                and not index.hasnans and index.is_unique and index.is_monotonic_increasing
            )
            if len(absent):
                errors["missing_expected_candles"] = {"count": len(absent)}
            if len(extra):
                errors["unexpected_candles"] = {"count": len(extra)}
    numeric: dict[str, pd.Series] = {}
    for column in (*PRICE_COLUMNS, "volume"):
        if column not in data:
            continue
        values = pd.to_numeric(data[column], errors="coerce")
        numeric[column] = values
        record(f"{column}_missing_or_non_numeric", values.isna())
        record(f"{column}_infinite", np.isinf(values))
        record(f"{column}_invalid_sign", values < 0 if column == "volume" else values <= 0)
    if not missing:
        prices = pd.DataFrame({key: numeric[key] for key in PRICE_COLUMNS})
        finite = np.isfinite(prices).all(axis=1)
        record("invalid_ohlc", finite & (
            (prices["high"] < prices[["open", "close"]].max(axis=1))
            | (prices["low"] > prices[["open", "close"]].min(axis=1))
            | (prices["high"] < prices["low"])
        ))
    if "volume" not in data:
        warnings.append("Volume column absent; volume is optional for OHLC validation.")
    elif not metadata.get("volume_unit", {}).get("confirmed", False):
        warnings.append("Volume units and meaning are unconfirmed; do not interpret as traded quantity.")
    report["structural_checks_passed"] = not bool(errors)
    report["ready_for_research"] = not bool(errors or blockers)
    report["status"] = "ready" if report["ready_for_research"] else "blocked"
    return report


def save_report(report: dict[str, Any], path: str) -> None:
    """Export a new JSON report without overwriting earlier results."""
    write_json(path, report)
```
<!-- SOURCE_END core/data_validator.py -->

## File gốc: `core/data_manager.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\data_manager.py`

Số dòng: 1; kích thước: 112 bytes; SHA256: `df7b63964ada00c56fca5f763a24e2152a282649a57871e8c1f397423be43e8c`.

<!-- SOURCE_BEGIN core/data_manager.py -->
```python
"""Module đọc dữ liệu thô, kiểm tra nến lỗi/múi giờ và xuất file .parquet chuẩn hóa."""
```
<!-- SOURCE_END core/data_manager.py -->

## File gốc: `inspect_data.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\inspect_data.py`

Số dòng: 122; kích thước: 6421 bytes; SHA256: `9987700c7c745d27fc1e16ddc710ec2c0f4742c0e6b27743fe03a46e426d49f8`.

<!-- SOURCE_BEGIN inspect_data.py -->
```python
"""Inspect all raw CSVs and export selected full diagnostic Parquet datasets."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import platform
import subprocess
from uuid import uuid4

import pandas as pd
import pyarrow
import yaml

from core.data_loader import (
    load_csv, load_parquet, read_metadata, save_parquet, sha256_file, write_json,
)
from core.data_validator import validate_data

ROOT = Path(__file__).resolve().parent


def merge_metadata(template: dict, overrides: dict) -> dict:
    """Recursively apply dataset overrides to the single shared metadata template."""
    result = deepcopy(template)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_metadata(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def main() -> None:
    """Run reproducible inspection; unknown CSV metadata must be provided first."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/data_pipeline.yaml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    with args.config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if config.get("diagnostic") is not True:
        raise ValueError("This inspection entry point requires diagnostic: true.")
    registry_path = ROOT / config["registry"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(registry.get("datasets"), list) or not registry["datasets"]:
        raise ValueError("Registry datasets must be a non-empty list.")
    filenames = [item.get("filename") for item in registry["datasets"]]
    if any(not isinstance(name, str) for name in filenames) or len(set(filenames)) != len(filenames):
        raise ValueError("Registry filenames must be unique non-empty strings.")
    entries = {item["filename"]: item for item in registry["datasets"]}
    raw_files = sorted((ROOT / config["raw_directory"]).glob("*.csv"))
    if not raw_files:
        raise ValueError("No CSV files found in configured raw directory.")
    unknown = [path.name for path in raw_files if path.name not in entries]
    if unknown:
        raise ValueError(f"Add explicit metadata registry entries for: {unknown}")
    missing_raw_entries = sorted(set(entries) - {path.name for path in raw_files})
    if missing_raw_entries:
        raise ValueError(f"Registry contains files absent from data/raw: {missing_raw_entries}")
    template_name = registry.get("metadata_template")
    if not isinstance(template_name, str):
        raise ValueError("Registry must define one metadata_template YAML file.")
    template = read_metadata(ROOT / config["metadata_directory"] / template_name)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    report_directory = ROOT / config["report_directory"] / ("data-quality-" + run_id)
    output_directory = ROOT / config["output_directory"] / ("inspection-" + run_id)
    report_directory.mkdir(parents=True, exist_ok=False)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip() or None
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    summary = {"run_id": run_id, "config": config, "registry": registry,
               "git_revision": revision, "working_tree_dirty": bool(dirty),
               "software": {"python": platform.python_version(), "pandas": pd.__version__,
                            "pyarrow": pyarrow.__version__},
               "code_sha256": {name: sha256_file(ROOT / name) for name in (
                   "inspect_data.py", "core/data_loader.py", "core/data_validator.py")},
               "datasets": []}
    for path in raw_files:
        before = sha256_file(path)
        metadata = merge_metadata(template, entries[path.name].get("metadata_overrides", {}))
        result = load_csv(path, metadata, diagnostic=True)
        report = validate_data(result.data, metadata, load_diagnostics=result.diagnostics)
        report["source_sha256"] = before
        report["metadata_snapshot"] = metadata
        # Every registered raw CSV is exported; the registry completeness
        # checks above prevent silent omissions.
        if path.name in entries:
            target = output_directory / (path.stem + ".diagnostic.parquet")
            save_parquet(result.data, target)
            pd.testing.assert_frame_equal(result.data, load_parquet(target))
            artifact = {"parquet_path": str(target), "parquet_sha256": sha256_file(target),
                        "source_path": str(path), "source_sha256": before,
                        "metadata_snapshot": metadata, "diagnostic_only": True,
                        "run_id": run_id, "ready_for_research": report["ready_for_research"],
                        "transformations": ["Explicit candidate Unix milliseconds to UTC", "Numeric parsing; no sorting, deduplication or filling"],
                        "row_count": len(result.data)}
            write_json(target.with_suffix(".metadata.json"), artifact)
            report["processed_artifact"] = artifact
        after = sha256_file(path)
        report["raw_unchanged"] = before == after
        if before != after:
            raise RuntimeError(f"Raw file changed during inspection: {path}")
        write_json(report_directory / (path.stem + ".quality.json"), report)
        summary["datasets"].append({"filename": path.name, "rows": len(result.data),
                                    "errors": report["errors"], "status": report["status"],
                                    "raw_unchanged": report["raw_unchanged"]})
        print(json.dumps(summary["datasets"][-1], ensure_ascii=False))
    write_json(report_directory / "summary.json", summary)
    print(f"Reports: {report_directory}")
    print(f"Processed: {output_directory}")


if __name__ == "__main__":
    main()
```
<!-- SOURCE_END inspect_data.py -->

## File gốc: `configs/config.yaml`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\configs\config.yaml`

Số dòng: 14; kích thước: 624 bytes; SHA256: `2cc5306a3d1c2936082d016558d8f08b7b79f90386ed41487382b73cd4036a53`.

<!-- SOURCE_BEGIN configs/config.yaml -->
```yaml
# CẤU HÌNH CHẠY BACKTEST MẶC ĐỊNH
backtest:
  initial_capital: 10000.0       # Vốn khởi điểm (USD)
  risk_per_trade: 0.01           # Rủi ro tối đa mỗi lệnh (1% vốn)
  default_symbol: "XAUUSD"       # Cặp giao dịch mặc định
  timeframe: "H1"                # Khung thời gian: M15, H1, H4, D1
  start_date: "2023-01-01"
  end_date: "2026-01-01"

execution:
  fill_on: "next_open"           # Khớp lệnh tại giá mở cửa nến tiếp theo
  slippage_points: 2             # Độ trượt giá giả định (points)
  include_commission: true
  include_swap: true
```
<!-- SOURCE_END configs/config.yaml -->

## File gốc: `configs/data_pipeline.yaml`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\configs\data_pipeline.yaml`

Số dòng: 8; kích thước: 323 bytes; SHA256: `29aaaf776797b23b37c8fcd1bb8aca53eaf4c9888770d26b77aae23a150111cc`.

<!-- SOURCE_BEGIN configs/data_pipeline.yaml -->
```yaml
# Paths are relative to the project root, not the shell working directory.
registry: data/metadata/datasets.json
raw_directory: data/raw
metadata_directory: data/metadata
output_directory: data/processed
report_directory: reports/runs
# Every CSV in data/raw is inspected and exported automatically.
diagnostic: true
```
<!-- SOURCE_END configs/data_pipeline.yaml -->

## File gốc: `data/metadata/datasets.json`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\data\metadata\datasets.json`

Số dòng: 31; kích thước: 1718 bytes; SHA256: `7e628dc9a7cfa90a71b287434e71f36d7d03aef4b4350f5de38853cd46dc5ffc`.

<!-- SOURCE_BEGIN data/metadata/datasets.json -->
```json
{
  "schema_version": 1,
  "description": "Every CSV in data/raw must have exactly one entry. Dataset-specific values override metadata_template.yaml.",
  "metadata_template": "metadata_template.yaml",
  "datasets": [
    {
      "filename": "eurusd-m1-bid-2023-01-01-2026-11-15.csv",
      "symbol_hint": "EURUSD",
      "metadata_overrides": {
        "symbol": {"value": "EURUSD", "confirmed": false, "evidence": "Filename hint only"},
        "instrument_specifications": {"value": {"point_size": 0.00001, "pip_size": 0.0001}, "confirmed": false, "evidence": "Point and pip confirmed by user; remaining specifications unresolved"},
        "instrument_specification_confirmations": {
          "point_size": {"value": 0.00001, "confirmed": true, "evidence": "User confirmed EURUSD point = 0.00001; 1 pip = 10 points"},
          "pip_size": {"value": 0.0001, "confirmed": true, "evidence": "User confirmed EURUSD pip = 0.0001"}
        }
      }
    },
    {
      "filename": "xauusd-m1-bid-2023-01-01-2026-11-15.csv",
      "symbol_hint": "XAUUSD",
      "metadata_overrides": {
        "symbol": {"value": "XAUUSD", "confirmed": false, "evidence": "Filename hint only"},
        "instrument_specifications": {"value": {"point_size": 0.001, "pip_size": 0.01}, "confirmed": false, "evidence": "Point and pip confirmed by user; remaining specifications unresolved"},
        "instrument_specification_confirmations": {
          "point_size": {"value": 0.001, "confirmed": true, "evidence": "User confirmed XAUUSD point = 0.001; 1 pip = 10 points"},
          "pip_size": {"value": 0.01, "confirmed": true, "evidence": "User confirmed XAUUSD pip = 0.01"}
        }
      }
    }
  ]
}
```
<!-- SOURCE_END data/metadata/datasets.json -->

## File gốc: `data/metadata/metadata_template.yaml`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\data\metadata\metadata_template.yaml`

Số dòng: 24; kích thước: 994 bytes; SHA256: `d3609fd78dd00c8e74da0b2400063c58517f20beedeb8504f96412596afeb80c`.

<!-- SOURCE_BEGIN data/metadata/metadata_template.yaml -->
```yaml
schema_version: 1

# One shared schema for every dataset. Dataset-specific values belong in datasets.json.
source: {value: null, confirmed: false, evidence: null}
symbol: {value: null, confirmed: false, evidence: null}
source_timezone: {value: null, confirmed: false, evidence: null}
timestamp_encoding: {value: unix_ms, confirmed: false, evidence: Diagnostic hypothesis only}
timestamp_kind: {value: null, confirmed: false, evidence: null}
price_type: {value: null, confirmed: false, evidence: null}
timeframe: {value: null, confirmed: false, evidence: null}
instrument_specifications:
  value:
    point_size: null
    tick_size: null
    pip_size: null
    contract_size: null
    quantity_unit: null
    quote_currency: null
    minimum_quantity_increment: null
  confirmed: false
  evidence: null
instrument_specification_confirmations: {}
volume_unit: {value: null, confirmed: false, evidence: null}
trading_calendar: {value: null, confirmed: false, evidence: null}
```
<!-- SOURCE_END data/metadata/metadata_template.yaml -->

## File gốc: `data/metadata/symbols.json`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\data\metadata\symbols.json`

Số dòng: 32; kích thước: 893 bytes; SHA256: `c02e3acb85953637e0eb377b2a017512746a1b28ad135f6b30884a4fd41eadff`.

<!-- SOURCE_BEGIN data/metadata/symbols.json -->
```json
{
    "XAUUSD": {
        "asset_class": "commodity",
        "description": "Gold vs US Dollar",
        "contract_size": 100000,
        "pip_value": 0.0001,
        "point_value": 1e-05,
        "typical_spread_points": 20,
        "commission_per_lot": 7.0,
        "min_lot": 0.01
    },
    "EURUSD": {
        "asset_class": "forex",
        "description": "Euro vs US Dollar",
        "contract_size": 100000,
        "pip_value": 0.0001,
        "point_value": 1e-05,
        "typical_spread_points": 10,
        "commission_per_lot": 7.0,
        "min_lot": 0.01
    },
    "BTCUSDT": {
        "asset_class": "crypto",
        "description": "Bitcoin Perpetual / Spot",
        "contract_size": 1,
        "pip_value": 1.0,
        "point_value": 0.01,
        "maker_fee_pct": 0.0002,
        "taker_fee_pct": 0.0005,
        "min_lot": 0.001
    }
}
```
<!-- SOURCE_END data/metadata/symbols.json -->
