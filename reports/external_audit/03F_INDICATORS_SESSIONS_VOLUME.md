# 03F_INDICATORS_SESSIONS_VOLUME

Đọc cùng 03_INDICATORS_AUDIT.md và 05D_TESTS_INDICATORS.md.

## File gốc: `indicators/sessions.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\indicators\sessions.py`

Số dòng: 210; kích thước: 10890 bytes; SHA256: `2bc30841a895d433b25813297e9aef7c343ce4a2a21024f4948ea14672794a16`.

<!-- SOURCE_BEGIN indicators/sessions.py -->
```python
"""Explicit local-time sessions and causal market-regime features.

Session inputs are timestamps of completed candles (availability time).
Intervals are [open, close). Session definitions are research parameters,
not assertions about a broker's calendar. DST follows the IANA timezone.
"""

from datetime import time

import numpy as np
import pandas as pd

from ._utils import ohlc, positive_window, validate_series
from .trend import adx
from .volatility import natr


def _utc_index(index: pd.Index) -> None:
    if not isinstance(index, pd.DatetimeIndex) or index.tz is None or str(index.tz) != "UTC":
        raise ValueError("A timezone-aware UTC DatetimeIndex is required")
    if index.hasnans or not index.is_unique or not index.is_monotonic_increasing:
        raise ValueError("Timestamps must be unique, valid and chronologically ordered")


def session_features(index: pd.DatetimeIndex, *, timezone: str, start: str, end: str) -> pd.DataFrame:
    """Active session, local session date and elapsed minutes; no warm-up.

    Overnight sessions belong to their opening date; start=end is rejected.
    Elapsed minutes are actual UTC minutes, including DST transitions.
    Off-session elapsed/date are NaN/NaT. Ambiguous/nonexistent opens raise.
    """
    _utc_index(index)
    start_time, end_time = time.fromisoformat(start), time.fromisoformat(end)
    if start_time == end_time:
        raise ValueError("start and end must differ")
    local = index.tz_convert(timezone)
    naive = local.tz_localize(None)
    seconds = naive.hour * 3600 + naive.minute * 60 + naive.second
    start_second = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_second = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    overnight = start_second > end_second
    active = (seconds >= start_second) | (seconds < end_second) if overnight else (seconds >= start_second) & (seconds < end_second)
    dates = naive.normalize() - pd.to_timedelta((overnight & (seconds < end_second)).astype(int), unit="D")
    opens = (dates + pd.to_timedelta(start_second, unit="s")).tz_localize(timezone, ambiguous="raise", nonexistent="raise").tz_convert("UTC")
    result = pd.DataFrame({"active": active, "session_date": dates, "minutes_since_open": (index - opens).total_seconds() / 60}, index=index)
    result.loc[~result.active, "session_date"] = pd.NaT
    result.loc[~result.active, "minutes_since_open"] = np.nan
    return result


def session_range(data: pd.DataFrame, *, timezone: str, start: str, end: str) -> pd.DataFrame:
    """Running session H/L/range using only candles observed so far.

    Off-session values are NaN. This never maps a final session extreme back
    to the opening bar. Requires complete coverage from session open.
    """
    _, h, l, _ = ohlc(data)
    features = session_features(data.index, timezone=timezone, start=start, end=end)
    high = h.where(features.active).groupby(features.session_date).cummax()
    low = l.where(features.active).groupby(features.session_date).cummin()
    return pd.DataFrame({"high": high, "low": low, "range": high - low})


def asia_session_range(data: pd.DataFrame, start: str = "09:00", end: str = "18:00") -> pd.DataFrame:
    """Tokyo session wrapper, configurable local hours; running extremes."""
    return session_range(data, timezone="Asia/Tokyo", start=start, end=end)


def london_session_range(data: pd.DataFrame, start: str = "08:00", end: str = "17:00") -> pd.DataFrame:
    """London session wrapper; DST-aware local hours; running extremes."""
    return session_range(data, timezone="Europe/London", start=start, end=end)


def new_york_session_range(data: pd.DataFrame, start: str = "08:00", end: str = "17:00") -> pd.DataFrame:
    """New York session wrapper; DST-aware local hours; running extremes."""
    return session_range(data, timezone="America/New_York", start=start, end=end)


def london_new_york_overlap(index: pd.DatetimeIndex, london_start: str = "08:00", london_end: str = "17:00", ny_start: str = "08:00", ny_end: str = "17:00") -> pd.Series:
    """Intersection of explicitly configurable London/New York sessions."""
    london = session_features(index, timezone="Europe/London", start=london_start, end=london_end)
    ny = session_features(index, timezone="America/New_York", start=ny_start, end=ny_end)
    return london.active & ny.active


def opening_range_breakout(data: pd.DataFrame, *, timezone: str, start: str, end: str, minutes: int = 30) -> pd.DataFrame:
    """Freeze observed range in first minutes; emit signed close breakout.

    Range bars satisfy 0<=elapsed<minutes. Output levels become available at
    elapsed>=minutes, signal is +1/-1/0 on each outside/inside close. If no
    opening bars were observed, result is NaN; completeness is caller's duty.
    """
    positive_window(minutes, "minutes")
    _, h, l, c = ohlc(data)
    f = session_features(data.index, timezone=timezone, start=start, end=end)
    opening = f.active & (f.minutes_since_open < minutes)
    high = h.where(opening).groupby(f.session_date).cummax().groupby(f.session_date).ffill()
    low = l.where(opening).groupby(f.session_date).cummin().groupby(f.session_date).ffill()
    ready = f.active & (f.minutes_since_open >= minutes) & high.notna() & low.notna()
    direction = pd.Series(np.select([c > high, c < low], [1, -1], default=0), index=data.index, dtype=float)
    return pd.DataFrame({"high": high.where(ready), "low": low.where(ready), "breakout": direction.where(ready & c.notna())})


def session_vwap(data: pd.DataFrame, *, timezone: str, start: str, end: str, volume_kind: str) -> pd.Series:
    """Cumulative typical-price*volume / cumulative volume per session.

    volume_kind must explicitly be 'traded' or 'tick'; tick volume is only a
    proxy. Zero cumulative volume yields NaN. Missing inputs poison remaining
    session values; negative volume raises. No implicit unit volume fallback.
    """
    _, h, l, c = ohlc(data)
    if "volume" not in data:
        raise ValueError("Session VWAP requires volume")
    if volume_kind not in {"traded", "tick"}:
        raise ValueError("volume_kind must be traded or tick")
    volume = data.volume
    if (volume.dropna() < 0).any():
        raise ValueError("Volume must be non-negative")
    f = session_features(data.index, timezone=timezone, start=start, end=end)
    typical = (h + l + c) / 3
    numerator = (typical * volume).where(f.active).groupby(f.session_date).cumsum(skipna=False)
    denominator = volume.where(f.active).groupby(f.session_date).cumsum(skipna=False)
    return numerator / denominator.replace(0, np.nan)


def calendar_features(index: pd.DatetimeIndex, timezone: str = "UTC") -> pd.DataFrame:
    """Local weekday Monday=0..Sunday=6 and hour=0..23, no warm-up."""
    _utc_index(index)
    local = index.tz_convert(timezone)
    return pd.DataFrame({"day_of_week": local.day_of_week, "hour_of_day": local.hour}, index=index)


def weekend_gap(data: pd.DataFrame, timezone: str = "UTC") -> pd.Series:
    """First Sunday/Monday bar after Friday: open-prior close, price units.

    Other bars zero, first bar NaN. Only dates 2..3 days after Friday qualify;
    holidays and source missingness are not inferred as weekend closures.
    """
    _utc_index(data.index)
    o, _, _, c = ohlc(data)
    local = data.index.tz_convert(timezone).tz_localize(None)
    weekday = pd.Series(local.day_of_week, index=data.index)
    days = pd.Series(local.normalize(), index=data.index).diff().dt.days
    event = weekday.shift().eq(4) & weekday.isin([6, 0]) & days.isin([2, 3])
    result = (o - c.shift()).where(event, 0.0)
    if len(result):
        result.iloc[0] = np.nan
    return result.where(o.notna() & c.shift().notna())


def trend_range_regime(data: pd.DataFrame, window: int = 14, trend_threshold: float = 25) -> pd.Series:
    """1 if ADX >= threshold, 0 otherwise; NaN until ADX available."""
    if not 0 <= trend_threshold <= 100:
        raise ValueError("trend_threshold must be in [0, 100]")
    strength = adx(data, window).adx
    return strength.ge(trend_threshold).astype(float).where(strength.notna())


def volatility_regime(data: pd.DataFrame, window: int = 14, reference_window: int = 100, quantile: float = 0.5) -> pd.Series:
    """1 high / 0 low NATR vs previous reference_window NATR quantile.

    Current value never influences its threshold. Full historical window needed.
    """
    positive_window(reference_window)
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be in [0, 1]")
    value = natr(data, window)
    threshold = value.shift().rolling(reference_window).quantile(quantile)
    return value.gt(threshold).astype(float).where(value.notna() & threshold.notna())


def dominant_cycle(close: pd.Series, window: int = 64, min_period: int = 6, max_period: int = 32) -> pd.DataFrame:
    """Trailing-window analytic signal (DFT Hilbert), not centered full-series.

    Detrend each completed window by OLS, select largest Fourier amplitude in
    period bounds. Phase is analytic-signal phase at newest sample, radians.
    Requires window samples; flat/detrended-zero windows yield NaN. Frequency
    resolution is window/k; this is NOT Ehlers HT_DCPERIOD or a future forecast.
    """
    positive_window(window)
    validate_series(close)
    if not 2 <= min_period <= max_period <= window:
        raise ValueError("Require 2 <= min_period <= max_period <= window")
    result = pd.DataFrame(np.nan, index=close.index, columns=["period", "phase"])
    x = np.arange(window, dtype=float)
    centered = x - x.mean()
    frequencies = np.fft.rfftfreq(window)
    eligible = (frequencies >= 1 / max_period) & (frequencies <= 1 / min_period)
    if not eligible.any():
        raise ValueError("No Fourier bins within period bounds")
    multiplier = np.zeros(window)
    multiplier[0] = 1
    if window % 2 == 0:
        multiplier[window // 2] = 1
        multiplier[1:window // 2] = 2
    else:
        multiplier[1:(window + 1) // 2] = 2
    for i in range(window - 1, len(close)):
        y = close.iloc[i-window+1:i+1].to_numpy(dtype=float)
        if not np.isfinite(y).all():
            continue
        detrended = y - y.mean() - centered * np.dot(centered, y) / np.dot(centered, centered)
        if np.max(np.abs(detrended)) <= 1e-12 * max(1, np.max(np.abs(y))):
            continue
        spectrum = np.fft.rfft(detrended)
        bins = np.flatnonzero(eligible)
        chosen = bins[np.argmax(np.abs(spectrum[bins]))]
        analytic = np.fft.ifft(np.fft.fft(detrended) * multiplier)
        result.iloc[i] = 1 / frequencies[chosen], np.angle(analytic[-1])
    return result
```
<!-- SOURCE_END indicators/sessions.py -->
