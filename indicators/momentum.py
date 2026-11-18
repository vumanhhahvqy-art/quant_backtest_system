"""Causal momentum and oscillator indicators."""

from __future__ import annotations

import pandas as pd
import numpy as np

from ._utils import ohlc, positive_window, validate_series
from .moving_averages import ema, rma, sma


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder RSI with SMA seed of window changes (window+1 prices).

    No loss => 100; no gain => 0; both zero => NaN. Missing change restarts
    smoothing warm-up. Output percentage is aligned to current completed bar.
    """
    positive_window(window)
    change = close.diff()
    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)
    average_gain, average_loss = rma(gain, window), rma(loss, window)
    result = 100 - 100 / (1 + average_gain / average_loss)
    return result.where(~((average_gain == 0) & (average_loss == 0)))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Fast EMA - slow EMA, signal EMA and histogram in price units.

    First-sample EMA seeds; line needs slow samples, signal slow+signal-1.
    Missing values reset each EMA. Require fast < slow.
    """
    if fast >= slow:
        raise ValueError("fast must be less than slow")
    line = ema(close, fast) - ema(close, slow)
    signal_line = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": signal_line, "histogram": line - signal_line})


def stochastic(data: pd.DataFrame, window: int = 14, smooth: int = 3) -> pd.DataFrame:
    """Fast %K=100*(C-min L)/(max H-min L), %D=SMA(%K,smooth).

    Needs window bars then smooth valid K values; flat range returns NaN.
    """
    positive_window(window)
    _, high, low, close = ohlc(data)
    lowest, highest = low.rolling(window, min_periods=window).min(), high.rolling(window, min_periods=window).max()
    percent_k = 100 * (close - lowest) / (highest - lowest).replace(0, np.nan)
    return pd.DataFrame({"%k": percent_k, "%d": sma(percent_k, smooth)})


def stochastic_rsi(close: pd.Series, rsi_window: int = 14, stoch_window: int = 14, smooth: int = 3) -> pd.DataFrame:
    """0..100 RSI stochastic; K=SMA(raw,smooth), D=SMA(K,smooth).

    K needs rsi_window+stoch_window+smooth-1 prices, D another smooth-1.
    Flat RSI range produces NaN; all rolling windows require full coverage.
    """
    positive_window(stoch_window)
    positive_window(smooth, "smooth")
    value = rsi(close, rsi_window)
    low, high = value.rolling(stoch_window, min_periods=stoch_window).min(), value.rolling(stoch_window, min_periods=stoch_window).max()
    k = 100 * (value - low) / (high - low).replace(0, np.nan)
    smoothed_k = sma(k, smooth)
    return pd.DataFrame({"%k": smoothed_k, "%d": sma(smoothed_k, smooth)})


def roc(close: pd.Series, window: int = 12) -> pd.Series:
    """100*(C/C.shift(window)-1); window+1 prices, zero base -> NaN."""
    positive_window(window)
    validate_series(close)
    return 100 * (close / close.shift(window).replace(0, np.nan) - 1)


def momentum(close: pd.Series, window: int = 10) -> pd.Series:
    """C-C.shift(window) in price units; window+1 prices, no NaN fill."""
    positive_window(window)
    validate_series(close)
    return close - close.shift(window)


def cci(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """Typical-price deviation / (0.015 * mean absolute deviation).

    Mean absolute deviation is around the SAME window mean. window samples;
    missing windows or constant typical price return NaN.
    """
    _, high, low, close = ohlc(data)
    typical = (high + low + close) / 3
    mean = sma(typical, window)
    deviation = typical.rolling(window, min_periods=window).apply(lambda x: abs(x - x.mean()).mean(), raw=True)
    return (typical - mean) / (0.015 * deviation).replace(0, np.nan)


def williams_r(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """-100*(max H-C)/(max H-min L), window bars; flat range -> NaN."""
    positive_window(window)
    _, high, low, close = ohlc(data)
    highest = high.rolling(window, min_periods=window).max()
    lowest = low.rolling(window, min_periods=window).min()
    return -100 * (highest - close) / (highest - lowest).replace(0, np.nan)


def ppo(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Percentage MACD, same EMA seeds/warm-up; zero slow EMA -> NaN."""
    if fast >= slow:
        raise ValueError("fast must be less than slow")
    slow_ema = ema(close, slow)
    line = 100 * (ema(close, fast) - slow_ema) / slow_ema.replace(0, np.nan)
    signal_line = ema(line, signal)
    return pd.DataFrame({"ppo": line, "signal": signal_line, "histogram": line - signal_line})


def tsi(close: pd.Series, long: int = 25, short: int = 13) -> pd.Series:
    """100*double-EMA(change)/double-EMA(abs(change)).

    Needs long+short prices, EMA first-sample seeds; flat denominator -> NaN.
    """
    change = close.diff()
    return 100 * ema(ema(change, long), short) / ema(ema(change.abs(), long), short).replace(0, np.nan)


def awesome_oscillator(data: pd.DataFrame, fast: int = 5, slow: int = 34) -> pd.Series:
    """Fast SMA - slow SMA of (H+L)/2; slow bars; missing window -> NaN."""
    if fast >= slow:
        raise ValueError("fast must be less than slow")
    _, high, low, _ = ohlc(data)
    median = (high + low) / 2
    return sma(median, fast) - sma(median, slow)