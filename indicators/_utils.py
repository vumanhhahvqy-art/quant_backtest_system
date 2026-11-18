"""Small validation and alignment helpers shared by indicator modules."""

from __future__ import annotations

import numpy as np
import pandas as pd


def require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def positive_window(window: int, name: str = "window") -> int:
    if isinstance(window, bool) or not isinstance(window, int) or window < 1:
        raise ValueError(f"{name} must be a positive integer")
    return window


def ohlc(data: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    require_columns(data, ["open", "high", "low", "close"])
    validate_index(data.index)
    values = data[["open", "high", "low", "close"]]
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in values.dtypes):
        raise ValueError("OHLC columns must be numeric")
    if np.isinf(values.to_numpy(dtype=float)).any():
        raise ValueError("OHLC must be finite or NaN")
    invalid = (data.high < data[["open", "close"]].max(axis=1)) | (data.low > data[["open", "close"]].min(axis=1)) | (data.high < data.low)
    if invalid.any():
        raise ValueError("Invalid OHLC relationships")
    return data["open"], data["high"], data["low"], data["close"]


def validate_index(index: pd.Index) -> None:
    if index.hasnans or not index.is_unique or not index.is_monotonic_increasing:
        raise ValueError("Index must be valid, unique and chronologically ordered")
    if isinstance(index, pd.DatetimeIndex) and (index.tz is None or str(index.tz) != "UTC"):
        raise ValueError("DatetimeIndex must be timezone-aware UTC")


def validate_series(series: pd.Series) -> None:
    validate_index(series.index)
    if not pd.api.types.is_numeric_dtype(series.dtype):
        raise ValueError("Series must be numeric")
    if np.isinf(series.to_numpy(dtype=float)).any():
        raise ValueError("Series must be finite or NaN")


def true_range(data: pd.DataFrame) -> pd.Series:
    _, high, low, close = ohlc(data)
    previous_close = close.shift(1)
    result = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    ).max(axis=1)
    return result.where(data[["high", "low", "close"]].notna().all(axis=1))