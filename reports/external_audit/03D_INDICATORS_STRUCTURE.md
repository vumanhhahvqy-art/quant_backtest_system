# 03D_INDICATORS_STRUCTURE

Đọc cùng 03_INDICATORS_AUDIT.md và 05D_TESTS_INDICATORS.md.

## File gốc: `indicators/market_structure.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\indicators\market_structure.py`

Số dòng: 189; kích thước: 10174 bytes; SHA256: `fb8b1238e509b3684c6f929dd6a965201603e76f957a28cea335b9d4efdf7180`.

<!-- SOURCE_BEGIN indicators/market_structure.py -->
```python
"""Causal market structure heuristics, published on confirmation bars.

BOS/CHoCH/MSS and zones have no unique industry definition. The definitions
below are explicit research features, not order instructions.
"""

import numpy as np
import pandas as pd

from ._utils import ohlc, positive_window


def confirmed_swings(data: pd.DataFrame, left: int = 2, right: int = 2) -> pd.DataFrame:
    """Strict local extrema, emitted right bars after pivot, never backdated.

    First possible observation is at left+right. Tied extrema do not qualify.
    Missing windows and non-events return NaN; values are pivot prices.
    """
    positive_window(left, "left")
    positive_window(right, "right")
    _, high, low, _ = ohlc(data)
    width = left + right + 1
    def extreme(values: np.ndarray, maximum: bool) -> float:
        candidate = values[left]
        others = np.delete(values, left)
        qualifies = (candidate > others).all() if maximum else (candidate < others).all()
        return float(candidate) if qualifies else np.nan
    return pd.DataFrame({"swing_high": high.rolling(width).apply(lambda x: extreme(x, True), raw=True), "swing_low": low.rolling(width).apply(lambda x: extreme(x, False), raw=True)})


def swing_structure(data: pd.DataFrame, left: int = 2, right: int = 2) -> pd.DataFrame:
    """HH/LH and HL/LL at confirmation; nullable until two same-kind pivots.

    Non-pivot bars are False after a prior pivot; equality is neither HH nor LH.
    """
    swings = confirmed_swings(data, left, right)
    result = pd.DataFrame(index=data.index)
    for column, higher_name, lower_name in [("swing_high", "higher_high", "lower_high"), ("swing_low", "higher_low", "lower_low")]:
        values = swings[column]
        previous = values.ffill().shift()
        result[higher_name] = (values > previous).astype("boolean").where(previous.notna())
        result[lower_name] = (values < previous).astype("boolean").where(previous.notna())
    return result


def structure_breaks(data: pd.DataFrame, left: int = 2, right: int = 2, displacement_ratio: float = 0.6) -> pd.DataFrame:
    """Close breaks last unbroken confirmed level (strict crossing).

    Trend initializes on first break. Same-direction break=BOS; opposite=CHoCH.
    MSS is CHoCH with real body/range >= displacement_ratio. Each pivot level
    is consumed once. Levels confirmed on current bar are eligible next bar.
    Direction is +1/-1, zero means no event; missing OHLC produces NaN.
    """
    if not 0 <= displacement_ratio <= 1:
        raise ValueError("displacement_ratio must be in [0, 1]")
    o, h, l, c = ohlc(data)
    swings = confirmed_swings(data, left, right)
    result = pd.DataFrame(0.0, index=data.index, columns=["break", "bos", "choch", "mss", "trend"])
    high_level = low_level = np.nan
    trend = 0
    for i in range(len(data)):
        if i > 0:
            if pd.notna(swings.swing_high.iloc[i-1]):
                high_level = swings.swing_high.iloc[i-1]
            if pd.notna(swings.swing_low.iloc[i-1]):
                low_level = swings.swing_low.iloc[i-1]
        if data[["open", "high", "low", "close"]].iloc[i].isna().any():
            result.iloc[i] = np.nan
            continue
        direction = 1 if pd.notna(high_level) and c.iloc[i] > high_level else -1 if pd.notna(low_level) and c.iloc[i] < low_level else 0
        bos = direction if direction and (trend == 0 or direction == trend) else 0
        choch = direction if direction and trend and direction != trend else 0
        ratio = abs(c.iloc[i] - o.iloc[i]) / (h.iloc[i] - l.iloc[i]) if h.iloc[i] > l.iloc[i] else 0
        mss = choch if ratio >= displacement_ratio else 0
        if direction:
            trend = direction
            if direction == 1:
                high_level = np.nan
            else:
                low_level = np.nan
        result.iloc[i] = direction, bos, choch, mss, trend
    return result


def support_resistance_zones(data: pd.DataFrame, left: int = 2, right: int = 2, tolerance: float = 0.001) -> pd.DataFrame:
    """Last confirmed pivot +/- relative tolerance; NaN until first pivot.

    These are single-pivot zones, not retrospectively clustered levels.
    """
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    swings = confirmed_swings(data, left, right).ffill()
    return pd.DataFrame({"support_lower": swings.swing_low * (1 - tolerance), "support_upper": swings.swing_low * (1 + tolerance), "resistance_lower": swings.swing_high * (1 - tolerance), "resistance_upper": swings.swing_high * (1 + tolerance)})


def previous_period_levels(data: pd.DataFrame, period: str = "day", timezone: str = "UTC") -> pd.DataFrame:
    """Previous observed calendar day/week OHLC in explicit timezone.

    Index must be unique, ordered UTC. Week starts Monday. Current incomplete
    period is never used. First observed period is NaN. A prior partial period
    remains partial: caller must supply validated complete session coverage.
    """
    from .sessions import _utc_index
    _utc_index(data.index)
    if period not in {"day", "week"}:
        raise ValueError("period must be day or week")
    ohlc(data)
    local = data.index.tz_convert(timezone).tz_localize(None)
    keys = local.normalize() if period == "day" else local.to_period("W-SUN").start_time
    keys = pd.Series(keys, index=data.index)
    aggregate = data.groupby(keys).agg({"high": "max", "low": "min", "close": "last"}).shift()
    return pd.DataFrame({name: keys.map(aggregate[name]) for name in aggregate.columns}, index=data.index)


def daily_pivots(data: pd.DataFrame, method: str = "traditional", timezone: str = "UTC") -> pd.DataFrame:
    """Previous-day traditional/Fibonacci/Camarilla/CPR pivot levels.

    NaN for first day; uses previous_period_levels coverage assumptions.
    """
    previous = previous_period_levels(data, "day", timezone)
    h, l, c = previous.high, previous.low, previous.close
    pivot, width = (h + l + c) / 3, h - l
    result = pd.DataFrame({"pivot": pivot})
    if method == "traditional":
        result["r1"], result["s1"] = 2 * pivot - l, 2 * pivot - h
        result["r2"], result["s2"] = pivot + width, pivot - width
        result["r3"], result["s3"] = h + 2 * (pivot - l), l - 2 * (h - pivot)
    elif method == "fibonacci":
        for i, ratio in enumerate((0.382, 0.618, 1.0), 1):
            result[f"r{i}"], result[f"s{i}"] = pivot + ratio * width, pivot - ratio * width
    elif method == "camarilla":
        for i, divisor in enumerate((12, 6, 4, 2), 1):
            result[f"r{i}"], result[f"s{i}"] = c + 1.1 * width / divisor, c - 1.1 * width / divisor
    elif method == "cpr":
        bottom, top = (h + l) / 2, 2 * pivot - (h + l) / 2
        result["bottom"] = pd.concat([bottom, top], axis=1).min(axis=1, skipna=False)
        result["top"] = pd.concat([bottom, top], axis=1).max(axis=1, skipna=False)
    else:
        raise ValueError("Unknown pivot method")
    return result


def fibonacci_retracement(data: pd.DataFrame, left: int = 2, right: int = 2, ratios: tuple[float, ...] = (0, 0.236, 0.382, 0.5, 0.618, 0.786, 1)) -> pd.DataFrame:
    """Retracement from latest confirmed high/low; direction from newest pivot.

    New high: H-ratio*(H-L); new low: L+ratio*(H-L). Both pivots required.
    """
    if not ratios or any(not np.isfinite(r) or not 0 <= r <= 1 for r in ratios):
        raise ValueError("ratios must be finite in [0, 1]")
    swings = confirmed_swings(data, left, right)
    high, low = swings.swing_high.ffill(), swings.swing_low.ffill()
    direction = pd.Series(np.nan, index=data.index)
    direction.loc[swings.swing_high.notna()] = 1
    direction.loc[swings.swing_low.notna()] = -1
    direction = direction.ffill()
    return pd.DataFrame({f"level_{ratio:g}": (high - ratio * (high - low)).where(direction == 1, low + ratio * (high - low)) for ratio in ratios})


def equal_high_low(data: pd.DataFrame, left: int = 2, right: int = 2, tolerance: float = 0.001) -> pd.DataFrame:
    """Successive confirmed same-kind pivots within relative tolerance."""
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    swings = confirmed_swings(data, left, right)
    result = pd.DataFrame(index=data.index)
    for source, name in [("swing_high", "equal_high"), ("swing_low", "equal_low")]:
        values = swings[source]
        previous = values.ffill().shift()
        result[name] = ((values - previous).abs() <= previous.abs() * tolerance).astype("boolean").where(previous.notna())
    return result


def liquidity_sweep(data: pd.DataFrame, left: int = 2, right: int = 2) -> pd.DataFrame:
    """Wick crosses previous confirmed level but close returns strictly inside."""
    _, h, l, c = ohlc(data)
    levels = confirmed_swings(data, left, right).ffill().shift()
    valid = data[["high", "low", "close"]].notna().all(axis=1)
    return pd.DataFrame({"high_sweep": ((h > levels.swing_high) & (c < levels.swing_high)).astype("boolean").where(valid & levels.swing_high.notna()), "low_sweep": ((l < levels.swing_low) & (c > levels.swing_low)).astype("boolean").where(valid & levels.swing_low.notna())})


def fair_value_gap(data: pd.DataFrame) -> pd.DataFrame:
    """Three-bar wick gap emitted on third close; bounds NaN on non-events.

    Bullish: current low > high two bars ago; bearish: current high < old low.
    No additional displacement or gap-mitigation assumptions.
    """
    _, h, l, _ = ohlc(data)
    valid = data[["open", "high", "low", "close"]].notna().all(axis=1).rolling(3).sum().eq(3)
    bull, bear = (l > h.shift(2)) & valid, (h < l.shift(2)) & valid
    return pd.DataFrame({"bullish": bull.astype("boolean").where(valid), "bearish": bear.astype("boolean").where(valid), "bull_lower": h.shift(2).where(bull), "bull_upper": l.where(bull), "bear_lower": h.where(bear), "bear_upper": l.shift(2).where(bear)})
```
<!-- SOURCE_END indicators/market_structure.py -->
