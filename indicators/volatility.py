"""Trailing volatility estimates; annualization is supplied by the caller."""

import numpy as np
import pandas as pd

from ._utils import ohlc, positive_window, true_range, validate_series
from .moving_averages import ema, rma, sma


def atr(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """Wilder average of true range, including first candle's high-low range."""
    return rma(true_range(data), window)


def natr(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """ATR as percentage of close; same warm-up as ATR."""
    return 100 * atr(data, window) / data["close"].replace(0, np.nan)


def rolling_std(series: pd.Series, window: int = 20, ddof: int = 0) -> pd.Series:
    """Trailing standard deviation; population convention by default."""
    positive_window(window)
    validate_series(series)
    if not isinstance(ddof, int) or not 0 <= ddof < window:
        raise ValueError("ddof must be an integer in [0, window)")
    return series.rolling(window, min_periods=window).std(ddof=ddof)


def bollinger_bands(close: pd.Series, window: int = 20, deviations: float = 2, ddof: int = 0) -> pd.DataFrame:
    """SMA +/- deviations * standard deviation; full-window warm-up."""
    if deviations <= 0:
        raise ValueError("deviations must be positive")
    middle = sma(close, window)
    width = deviations * rolling_std(close, window, ddof)
    return pd.DataFrame({"lower": middle - width, "middle": middle, "upper": middle + width})


def bollinger_bandwidth(close: pd.Series, window: int = 20, deviations: float = 2) -> pd.Series:
    """100 * (upper-lower)/middle; zero middle returns NaN."""
    bands = bollinger_bands(close, window, deviations)
    return 100 * (bands.upper - bands.lower) / bands.middle.replace(0, np.nan)


def bollinger_percent_b(close: pd.Series, window: int = 20, deviations: float = 2) -> pd.Series:
    """Fraction (close-lower)/(upper-lower); flat bands return NaN."""
    bands = bollinger_bands(close, window, deviations)
    return (close - bands.lower) / (bands.upper - bands.lower).replace(0, np.nan)


def keltner_channels(data: pd.DataFrame, window: int = 20, atr_window: int = 10, multiplier: float = 2) -> pd.DataFrame:
    """Close EMA +/- multiplier * Wilder ATR, available after both warm-ups."""
    if multiplier <= 0:
        raise ValueError("multiplier must be positive")
    middle = ema(data["close"], window)
    width = multiplier * atr(data, atr_window)
    return pd.DataFrame({"lower": middle - width, "middle": middle, "upper": middle + width})


def donchian_channels(data: pd.DataFrame, window: int = 20, lag: int = 0) -> pd.DataFrame:
    """Trailing extremes including current completed bar; lag=1 for prior levels."""
    positive_window(window)
    if not isinstance(lag, int) or lag < 0:
        raise ValueError("lag must be a non-negative integer")
    _, high, low, _ = ohlc(data)
    upper = high.rolling(window, min_periods=window).max().shift(lag)
    lower = low.rolling(window, min_periods=window).min().shift(lag)
    return pd.DataFrame({"lower": lower, "middle": (upper + lower) / 2, "upper": upper})


def _annualization(periods_per_year: float) -> float:
    if not np.isfinite(periods_per_year) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be finite and positive")
    return periods_per_year


def _log_returns(close: pd.Series) -> pd.Series:
    if (close.dropna() <= 0).any():
        raise ValueError("Log returns require positive prices")
    return np.log(close / close.shift(1))


def historical_volatility(close: pd.Series, window: int = 20, *, periods_per_year: float, ddof: int = 1) -> pd.Series:
    """Annualized log-return std in fractional units; needs window+1 prices."""
    return rolling_std(_log_returns(close), window, ddof) * np.sqrt(_annualization(periods_per_year))


def realized_volatility(close: pd.Series, window: int = 20, *, periods_per_year: float) -> pd.Series:
    """sqrt(mean(log_return**2)*periods_per_year), without mean subtraction."""
    return np.sqrt(sma(_log_returns(close) ** 2, window) * _annualization(periods_per_year))


def parkinson_volatility(data: pd.DataFrame, window: int = 20, *, periods_per_year: float) -> pd.Series:
    """sqrt(mean(log(H/L)^2)/(4 log(2))*annualization); needs window bars."""
    _, high, low, _ = ohlc(data)
    if (low.dropna() <= 0).any():
        raise ValueError("Parkinson requires positive prices")
    return np.sqrt(sma(np.log(high / low) ** 2, window) * _annualization(periods_per_year) / (4 * np.log(2)))


def garman_klass_volatility(data: pd.DataFrame, window: int = 20, *, periods_per_year: float) -> pd.Series:
    """OHLC variance estimator; excludes overnight gaps; window-bar warm-up."""
    open_, high, low, close = ohlc(data)
    if (data[["open", "high", "low", "close"]].stack() <= 0).any():
        raise ValueError("Garman-Klass requires positive prices")
    variance = 0.5 * np.log(high / low) ** 2 - (2 * np.log(2) - 1) * np.log(close / open_) ** 2
    return np.sqrt(sma(variance, window).clip(lower=0) * _annualization(periods_per_year))