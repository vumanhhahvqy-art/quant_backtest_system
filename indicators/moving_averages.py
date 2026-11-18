"""Moving averages. Warm-up observations are NaN and no input is mutated."""

from __future__ import annotations

import pandas as pd
import numpy as np

from ._utils import positive_window, validate_series


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average; first window - 1 values are NaN."""
    positive_window(window)
    validate_series(series)
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, window: int, adjust: bool = False) -> pd.Series:
    """Pandas EWM, seeded at first sample, hidden until window samples.

    adjust=False uses alpha=2/(window+1). Missing values restart warm-up.
    adjust=True uses normalized finite-history exponential weights.
    """
    positive_window(window)
    validate_series(series)
    if series.empty:
        return series.astype(float).copy()
    groups = series.isna().cumsum()
    return series.groupby(groups, group_keys=False).transform(
        lambda part: part.ewm(span=window, adjust=adjust, min_periods=window).mean()
    ).where(series.notna())


def wma(series: pd.Series, window: int) -> pd.Series:
    """Linearly weighted moving average, newest value has weight ``window``."""
    positive_window(window)
    validate_series(series)
    weights = pd.Series(range(1, window + 1), dtype=float)
    return series.rolling(window, min_periods=window).apply(
        lambda values: float((values * weights.to_numpy()).sum() / weights.sum()), raw=True
    )


def rma(series: pd.Series, window: int) -> pd.Series:
    """Wilder alpha=1/window with SMA seed; NaN resets full warm-up."""
    positive_window(window)
    validate_series(series)
    result = pd.Series(np.nan, index=series.index, dtype=float, name=series.name)
    count, total, previous = 0, 0.0, np.nan
    for i, value in enumerate(series):
        if pd.isna(value):
            count, total, previous = 0, 0.0, np.nan
            continue
        count += 1
        if count <= window:
            total += value
            if count == window:
                previous = total / window
        else:
            previous += (value - previous) / window
        result.iloc[i] = previous
    return result


smma = rma