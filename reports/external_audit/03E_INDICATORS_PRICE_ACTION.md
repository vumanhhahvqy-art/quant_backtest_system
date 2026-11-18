# 03E_INDICATORS_PRICE_ACTION

Đọc cùng 03_INDICATORS_AUDIT.md và 05D_TESTS_INDICATORS.md.

## File gốc: `indicators/price_action.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\indicators\price_action.py`

Số dòng: 142; kích thước: 7330 bytes; SHA256: `3ba1ca770837f91bed1408ef5cf31f8abfd38b298c33cccf3e7069fff8bd8c0d`.

<!-- SOURCE_BEGIN indicators/price_action.py -->
```python
"""Candle geometry and explicitly parameterized pattern heuristics.

Patterns describe completed bars, not a forecast. Zero-range ratios are NaN.
Boolean patterns use pandas nullable booleans: unavailable inputs produce NA.
"""

import numpy as np
import pandas as pd

from ._utils import ohlc, positive_window


def candle_features(data: pd.DataFrame) -> pd.DataFrame:
    """Body/range in price units; wick ratios relative to total range; no warm-up."""
    open_, high, low, close = ohlc(data)
    body, range_ = (close - open_).abs(), high - low
    top = pd.concat([open_, close], axis=1).max(axis=1, skipna=False)
    bottom = pd.concat([open_, close], axis=1).min(axis=1, skipna=False)
    denominator = range_.replace(0, np.nan)
    return pd.DataFrame({"body": body, "range": range_, "upper_wick": high - top, "lower_wick": bottom - low, "upper_wick_ratio": (high - top) / denominator, "lower_wick_ratio": (bottom - low) / denominator, "body_to_range": body / denominator})


def _pattern(condition: pd.Series, data: pd.DataFrame, bars: int = 1) -> pd.Series:
    valid = data[["open", "high", "low", "close"]].notna().all(axis=1)
    valid = valid.rolling(bars).sum().eq(bars)
    return condition.astype("boolean").where(valid)


def inside_bar(data: pd.DataFrame) -> pd.Series:
    """Strict high<prior high and low>prior low; one-bar warm-up."""
    _, high, low, _ = ohlc(data)
    return _pattern((high < high.shift()) & (low > low.shift()), data, 2)


def outside_bar(data: pd.DataFrame) -> pd.Series:
    """Strict high>prior high and low<prior low; one-bar warm-up."""
    _, high, low, _ = ohlc(data)
    return _pattern((high > high.shift()) & (low < low.shift()), data, 2)


def engulfing(data: pd.DataFrame) -> pd.DataFrame:
    """Opposite-color real-body engulfing, inclusive boundaries; excludes doji."""
    o, _, _, c = ohlc(data)
    bull = (c > o) & (c.shift() < o.shift()) & (o <= c.shift()) & (c >= o.shift())
    bear = (c < o) & (c.shift() > o.shift()) & (o >= c.shift()) & (c <= o.shift())
    return pd.DataFrame({"bullish": _pattern(bull, data, 2), "bearish": _pattern(bear, data, 2)})


def pin_bar(data: pd.DataFrame, wick_ratio: float = 0.6, max_opposite_ratio: float = 0.2) -> pd.DataFrame:
    """Long wick >= wick_ratio of range, opposite wick <= threshold; no warm-up."""
    if not 0 < wick_ratio <= 1 or not 0 <= max_opposite_ratio < 1:
        raise ValueError("Invalid wick thresholds")
    f = candle_features(data)
    return pd.DataFrame({"bullish": _pattern((f.lower_wick_ratio >= wick_ratio) & (f.upper_wick_ratio <= max_opposite_ratio), data).where(f.range > 0), "bearish": _pattern((f.upper_wick_ratio >= wick_ratio) & (f.lower_wick_ratio <= max_opposite_ratio), data).where(f.range > 0)})


def doji(data: pd.DataFrame, max_body_ratio: float = 0.1) -> pd.Series:
    """Body/range <= threshold; zero-range bars unavailable."""
    if not 0 <= max_body_ratio <= 1:
        raise ValueError("max_body_ratio must be in [0, 1]")
    f = candle_features(data)
    return _pattern(f.body_to_range <= max_body_ratio, data).where(f.range > 0)


def hammer_shooting_star(data: pd.DataFrame, wick_to_body: float = 2, max_opposite_ratio: float = 0.1) -> pd.DataFrame:
    """Geometry only, no preceding trend filter. Long wick >= factor*body."""
    if wick_to_body <= 0 or not 0 <= max_opposite_ratio <= 1:
        raise ValueError("Invalid candle thresholds")
    f = candle_features(data)
    valid = (f.body > 0) & (f.range > 0)
    return pd.DataFrame({"hammer": _pattern(valid & (f.lower_wick >= wick_to_body * f.body) & (f.upper_wick_ratio <= max_opposite_ratio), data), "shooting_star": _pattern(valid & (f.upper_wick >= wick_to_body * f.body) & (f.lower_wick_ratio <= max_opposite_ratio), data)})


def morning_evening_star(data: pd.DataFrame, small_body_ratio: float = 0.3, penetration: float = 0.5) -> pd.DataFrame:
    """Three-bar star heuristic without mandatory Forex gaps; two-bar warm-up.

    Middle body <= small_body_ratio * first body; final close penetrates
    penetration of the first body's length. First/last colors must reverse.
    """
    if not 0 <= small_body_ratio <= 1 or not 0 <= penetration <= 1:
        raise ValueError("Ratios must be in [0, 1]")
    o, _, _, c = ohlc(data)
    body = (c - o).abs()
    small = body.shift() <= small_body_ratio * body.shift(2)
    bull = small & (c.shift(2) < o.shift(2)) & (c > o) & (c >= c.shift(2) + penetration * body.shift(2))
    bear = small & (c.shift(2) > o.shift(2)) & (c < o) & (c <= c.shift(2) - penetration * body.shift(2))
    return pd.DataFrame({"morning_star": _pattern(bull, data, 3), "evening_star": _pattern(bear, data, 3)})


def marubozu(data: pd.DataFrame, min_body_ratio: float = 0.9) -> pd.DataFrame:
    """Directional candle with body/range >= threshold; no warm-up."""
    if not 0 <= min_body_ratio <= 1:
        raise ValueError("min_body_ratio must be in [0, 1]")
    o, _, _, c = ohlc(data)
    f = candle_features(data)
    return pd.DataFrame({"bullish": _pattern((c > o) & (f.body_to_range >= min_body_ratio), data), "bearish": _pattern((c < o) & (f.body_to_range >= min_body_ratio), data)})


def heikin_ashi(data: pd.DataFrame) -> pd.DataFrame:
    """HA close=OHLC/4; initial HA open=(O+C)/2; NaN restarts state."""
    o, h, l, c = ohlc(data)
    ha_close = (o + h + l + c) / 4
    ha_open = pd.Series(np.nan, index=data.index, dtype=float)
    for i in range(len(data)):
        if pd.isna(ha_close.iloc[i]):
            continue
        ha_open.iloc[i] = (o.iloc[i] + c.iloc[i]) / 2 if i == 0 or pd.isna(ha_open.iloc[i-1]) else (ha_open.iloc[i-1] + ha_close.iloc[i-1]) / 2
    valid = ha_close.notna()
    return pd.DataFrame({"open": ha_open, "high": pd.concat([h, ha_open, ha_close], axis=1).max(axis=1).where(valid), "low": pd.concat([l, ha_open, ha_close], axis=1).min(axis=1).where(valid), "close": ha_close})


def narrow_range(data: pd.DataFrame, window: int = 4) -> pd.Series:
    """NR4/NR7 via window=4/7; ties count; needs window completed bars."""
    positive_window(window)
    range_ = candle_features(data)["range"]
    minimum = range_.rolling(window).min()
    return _pattern(range_.eq(minimum), data).where(minimum.notna())


def consecutive_candles(data: pd.DataFrame) -> pd.Series:
    """Signed run length: bullish positive, bearish negative, doji zero; NaN resets."""
    o, _, _, c = ohlc(data)
    result = pd.Series(np.nan, index=data.index, dtype=float)
    run = 0
    for i, difference in enumerate(c - o):
        if pd.isna(difference):
            run = 0
            continue
        sign = int(np.sign(difference))
        run = 0 if sign == 0 else run + sign if np.sign(run) == sign else sign
        result.iloc[i] = run
    return result


def range_expansion(data: pd.DataFrame, window: int = 20, multiplier: float = 1.5) -> pd.Series:
    """Current range > multiplier * mean of previous window ranges."""
    positive_window(window)
    if multiplier <= 0:
        raise ValueError("multiplier must be positive")
    range_ = candle_features(data)["range"]
    baseline = range_.shift().rolling(window).mean()
    return _pattern(range_ > multiplier * baseline, data).where(baseline.notna())
```
<!-- SOURCE_END indicators/price_action.py -->
