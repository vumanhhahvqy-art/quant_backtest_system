"""Trend indicators evaluated only after the current candle is complete."""

import numpy as np
import pandas as pd

from ._utils import ohlc, positive_window, true_range, validate_series
from .moving_averages import rma
from .volatility import atr


def adx(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Wilder movement; DI needs window+1 prices, ADX needs 2*window.

    RMA uses SMA seeds. Zero TR or zero sum of directional indices produces
    NaN. Missing changes restart the corresponding smoothing warm-up.
    """
    _, high, low, _ = ohlc(data)
    up, down = high.diff(), -low.diff()
    plus = up.where((up > down) & (up > 0), 0).where(up.notna())
    minus = down.where((down > up) & (down > 0), 0).where(down.notna())
    tr = rma(true_range(data).where(up.notna()), window).replace(0, np.nan)
    plus_di, minus_di = 100 * rma(plus, window) / tr, 100 * rma(minus, window) / tr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return pd.DataFrame({"plus_di": plus_di, "minus_di": minus_di, "adx": rma(dx, window)})


def supertrend(data: pd.DataFrame, window: int = 10, multiplier: float = 3) -> pd.DataFrame:
    """ATR trailing bands, initialized bullish at first valid ATR; resets on NaN."""
    if multiplier <= 0:
        raise ValueError("multiplier must be positive")
    _, high, low, close = ohlc(data)
    mid, width = (high + low) / 2, multiplier * atr(data, window)
    result = pd.DataFrame(np.nan, index=data.index, columns=["supertrend", "direction", "upper", "lower"])
    previous = None
    for i in range(len(data)):
        upper, lower, price = mid.iloc[i] + width.iloc[i], mid.iloc[i] - width.iloc[i], close.iloc[i]
        if pd.isna(upper) or pd.isna(lower) or pd.isna(price):
            previous = None
            continue
        if previous is None:
            direction = 1
        else:
            old_upper, old_lower, old_direction, old_close = previous
            upper = upper if upper < old_upper or old_close > old_upper else old_upper
            lower = lower if lower > old_lower or old_close < old_lower else old_lower
            direction = (1 if price > upper else -1) if old_direction < 0 else (-1 if price < lower else 1)
        result.iloc[i] = [lower if direction == 1 else upper, direction, upper, lower]
        previous = upper, lower, direction, price
    return result


def aroon(data: pd.DataFrame, window: int = 25) -> pd.DataFrame:
    """window+1 bars; newest tied extreme wins; up/down range 0..100."""
    positive_window(window)
    _, high, low, _ = ohlc(data)
    up = high.rolling(window + 1).apply(lambda x: 100 * (window - np.argmax(x[::-1])) / window, raw=True)
    down = low.rolling(window + 1).apply(lambda x: 100 * (window - np.argmin(x[::-1])) / window, raw=True)
    return pd.DataFrame({"up": up, "down": down, "oscillator": up - down})


def parabolic_sar(data: pd.DataFrame, step: float = 0.02, maximum: float = 0.2) -> pd.DataFrame:
    """Wilder SAR, initial direction from two closes; output begins on bar 3.

    Initial SAR is the two-bar opposite extreme. Projected SAR is clamped to
    the two previous lows/highs; crossing reverses to the previous extreme.
    Missing OHLC restarts the two-bar initialization.
    """
    if not 0 < step <= maximum <= 1:
        raise ValueError("Require 0 < step <= maximum <= 1")
    _, high, low, close = ohlc(data)
    result = pd.DataFrame(np.nan, index=data.index, columns=["sar", "direction"])
    start, state = 0, None
    for i in range(len(data)):
        if data[["high", "low", "close"]].iloc[i].isna().any():
            start, state = i + 1, None
            continue
        if i - start < 2:
            continue
        if state is None:
            direction = 1 if close.iloc[i - 1] >= close.iloc[i - 2] else -1
            sar = low.iloc[i-2:i].min() if direction == 1 else high.iloc[i-2:i].max()
            extreme = high.iloc[i-2:i].max() if direction == 1 else low.iloc[i-2:i].min()
            acceleration = step
        else:
            sar, extreme, acceleration, direction = state
        projected = sar + acceleration * (extreme - sar)
        projected = min(projected, low.iloc[i-2:i].min()) if direction == 1 else max(projected, high.iloc[i-2:i].max())
        reverse = low.iloc[i] < projected if direction == 1 else high.iloc[i] > projected
        if reverse:
            projected, direction, acceleration = extreme, -direction, step
            extreme = high.iloc[i] if direction == 1 else low.iloc[i]
        else:
            new_extreme = high.iloc[i] if direction == 1 else low.iloc[i]
            if (direction == 1 and new_extreme > extreme) or (direction == -1 and new_extreme < extreme):
                extreme, acceleration = new_extreme, min(maximum, acceleration + step)
        result.iloc[i] = projected, direction
        state = projected, extreme, acceleration, direction
    return result


def ichimoku(data: pd.DataFrame, conversion: int = 9, base: int = 26, span: int = 52, displacement: int = 26) -> pd.DataFrame:
    """Causal cloud aligned to current time. No backward-shifted Chikou.

    Raw spans are available now; displayed cloud uses positive displacement.
    lagging_close is close.shift(displacement), a causal historical feature.
    """
    for value in (conversion, base, span):
        positive_window(value)
    if not isinstance(displacement, int) or displacement < 0:
        raise ValueError("displacement must be a non-negative integer")
    _, high, low, close = ohlc(data)
    def midpoint(window: int) -> pd.Series:
        return (high.rolling(window).max() + low.rolling(window).min()) / 2
    tenkan, kijun = midpoint(conversion), midpoint(base)
    a, b = (tenkan + kijun) / 2, midpoint(span)
    return pd.DataFrame({"conversion": tenkan, "base": kijun, "span_a_raw": a, "span_b_raw": b, "cloud_a": a.shift(displacement), "cloud_b": b.shift(displacement), "lagging_close": close.shift(displacement)})


def vortex(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Sum cross-bar movement / sum TR over window changes; NaN on zero TR."""
    positive_window(window)
    _, high, low, _ = ohlc(data)
    denominator = true_range(data).rolling(window).sum().replace(0, np.nan)
    return pd.DataFrame({"plus": (high - low.shift()).abs().rolling(window).sum() / denominator, "minus": (low - high.shift()).abs().rolling(window).sum() / denominator})


def choppiness(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """100 log10(sum(TR)/(max(H)-min(L)))/log10(window); window >= 2."""
    positive_window(window)
    if window < 2:
        raise ValueError("window must be at least 2")
    _, high, low, _ = ohlc(data)
    width = high.rolling(window).max() - low.rolling(window).min()
    return 100 * np.log10(true_range(data).rolling(window).sum() / width.replace(0, np.nan)) / np.log10(window)


def vhf(close: pd.Series, window: int = 28) -> pd.Series:
    """Close range over window / sum of window absolute changes."""
    positive_window(window)
    validate_series(close)
    width = close.rolling(window).max() - close.rolling(window).min()
    return width / close.diff().abs().rolling(window).sum().replace(0, np.nan)


def linear_regression_slope(close: pd.Series, window: int = 20) -> pd.Series:
    """OLS slope in price/bar over trailing window (x=0..window-1)."""
    positive_window(window)
    validate_series(close)
    if window < 2:
        raise ValueError("window must be at least 2")
    x = np.arange(window, dtype=float) - (window - 1) / 2
    return close.rolling(window).apply(lambda y: np.dot(x, y) / np.dot(x, x), raw=True)


def linear_regression_channel(close: pd.Series, window: int = 20, deviations: float = 2) -> pd.DataFrame:
    """OLS endpoint +/- deviations * population residual std; no backpainting."""
    if deviations <= 0:
        raise ValueError("deviations must be positive")
    slope = linear_regression_slope(close, window)
    endpoint = close.rolling(window).mean() + slope * (window - 1) / 2
    x = np.arange(window, dtype=float)
    def residual_std(y: np.ndarray) -> float:
        centered = x - x.mean()
        b = np.dot(centered, y) / np.dot(centered, centered)
        return float(np.sqrt(np.mean((y - (y.mean() + b * centered)) ** 2)))
    width = close.rolling(window).apply(residual_std, raw=True) * deviations
    return pd.DataFrame({"lower": endpoint - width, "middle": endpoint, "upper": endpoint + width, "slope": slope})