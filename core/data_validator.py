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