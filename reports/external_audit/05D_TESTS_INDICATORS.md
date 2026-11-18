# 05D_TESTS_INDICATORS

Toàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.

## File gốc: `tests/test_indicators.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_indicators.py`

Số dòng: 384; kích thước: 20622 bytes; SHA256: `9765c5229bf05059e452eec9cb6a592fca2f6277c80783666e84adbc84dd5188`.

<!-- SOURCE_BEGIN tests/test_indicators.py -->
```python
"""Independent arithmetic fixtures plus alignment and causal-prefix contracts."""

import numpy as np
import pandas as pd
import pytest

from indicators import moving_averages as ma
from indicators import momentum as mom
from indicators import trend as tr
from indicators import volatility as vol
from indicators import price_action as pa
from indicators import market_structure as ms
from indicators import sessions as se


def bars(close, index=None):
    close = np.asarray(close, dtype=float)
    if index is None:
        index = pd.date_range("2024-01-01", periods=len(close), freq="h", tz="UTC", name="timestamp")
    return pd.DataFrame({"open": close - 0.5, "high": close + 1, "low": close - 1, "close": close, "volume": 2.0}, index=index)


@pytest.fixture
def data():
    return bars(np.arange(10., 110.))


def test_moving_averages_and_nan_restart():
    s = pd.Series([1., 2., 3., 4.])
    np.testing.assert_allclose(ma.sma(s, 3), [np.nan, np.nan, 2, 3], equal_nan=True)
    np.testing.assert_allclose(ma.ema(s, 3), [np.nan, np.nan, 2.25, 3.125], equal_nan=True)
    np.testing.assert_allclose(ma.wma(s, 3), [np.nan, np.nan, 14 / 6, 20 / 6], equal_nan=True)
    np.testing.assert_allclose(ma.rma(s, 3), [np.nan, np.nan, 2, 8 / 3], equal_nan=True)
    assert ma.smma is ma.rma
    broken = pd.Series([1., 2., np.nan, 4., 5., 6.])
    for function in (ma.sma, ma.ema, ma.wma, ma.rma):
        result = function(broken, 3)
        assert result.iloc[:5].isna().all()
        assert pd.notna(result.iloc[5])


def test_momentum_arithmetic(data):
    assert mom.rsi(pd.Series([1., 3., 2., 4.]), 3).iloc[-1] == pytest.approx(80)
    assert mom.rsi(data.close, 3).iloc[-1] == 100
    assert mom.rsi(pd.Series([2.] * 8), 3).isna().all()
    assert mom.roc(data.close, 2).iloc[2] == pytest.approx(20)
    assert mom.momentum(data.close, 2).iloc[2] == 2
    assert mom.stochastic(data, 3, 2)["%k"].iloc[2] == 75
    assert mom.stochastic(data, 3, 2)["%d"].iloc[3] == 75
    assert mom.williams_r(data, 3).iloc[2] == -25
    assert mom.cci(data, 3).iloc[2] == pytest.approx(100)
    assert mom.awesome_oscillator(data, 2, 4).iloc[3] == 1
    assert mom.tsi(data.close, 3, 2).iloc[-1] == pytest.approx(100)
    # EMA(span=2): [10, 10+2/3, 11+5/9]; EMA(span=3): [10,10.5,11.25].
    expected = 11 + 5 / 9 - 11.25
    m = mom.macd(data.close, 2, 3, 2)
    assert m.macd.iloc[2] == pytest.approx(expected)
    assert m.signal.iloc[3] == pytest.approx(expected / 3 + (12 + 14 / 27 - 12.125) * 2 / 3)
    p = mom.ppo(data.close, 2, 3, 2)
    assert p.ppo.iloc[2] == pytest.approx(100 * expected / 11.25)
    # RSI(2) for changes +1,-1,+1,-1,+1: 50,75,37.5,68.75.
    s = mom.stochastic_rsi(pd.Series([10., 11., 10., 11., 10., 11.]), 2, 2, 1)
    assert s["%k"].iloc[3] == 100
    assert s["%k"].iloc[4] == 0
    assert s["%d"].iloc[5] == 100


def test_volatility_arithmetic(data):
    assert vol.atr(data, 3).iloc[2] == 2
    assert vol.natr(data, 3).iloc[2] == pytest.approx(200 / 12)
    assert vol.rolling_std(data.close, 3).iloc[2] == pytest.approx(np.sqrt(2 / 3))
    bands = vol.bollinger_bands(data.close, 3)
    assert bands.middle.iloc[2] == 11
    assert bands.upper.iloc[2] == pytest.approx(11 + 2 * np.sqrt(2 / 3))
    assert vol.bollinger_bandwidth(data.close, 3).iloc[2] == pytest.approx(400 * np.sqrt(2 / 3) / 11)
    assert vol.bollinger_percent_b(data.close, 3).iloc[2] == pytest.approx((1 + 2 * np.sqrt(2 / 3)) / (4 * np.sqrt(2 / 3)))
    channel = vol.keltner_channels(data, 3, 3, 2)
    assert channel.upper.iloc[2] == 15.25
    assert channel.lower.iloc[2] == 7.25
    donchian = vol.donchian_channels(data, 3)
    assert list(donchian.iloc[2]) == [9, 11, 13]
    returns = np.array([np.log(11 / 10), np.log(12 / 11), np.log(13 / 12)])
    assert vol.historical_volatility(data.close, 3, periods_per_year=10).iloc[3] == pytest.approx(np.std(returns, ddof=1) * np.sqrt(10))
    assert vol.realized_volatility(data.close, 3, periods_per_year=10).iloc[3] == pytest.approx(np.sqrt(sum(returns ** 2) / 3 * 10))
    ranges = np.log(np.array([11 / 9, 12 / 10, 13 / 11]))
    assert vol.parkinson_volatility(data, 3, periods_per_year=10).iloc[2] == pytest.approx(np.sqrt(sum(ranges ** 2) / 3 / (4 * np.log(2)) * 10))
    oc = np.log(np.array([10 / 9.5, 11 / 10.5, 12 / 11.5]))
    variance = 0.5 * ranges ** 2 - (2 * np.log(2) - 1) * oc ** 2
    assert vol.garman_klass_volatility(data, 3, periods_per_year=10).iloc[2] == pytest.approx(np.sqrt(variance.mean() * 10))


def test_trend_arithmetic(data):
    directional = tr.adx(data, 3)
    assert directional.plus_di.iloc[3] == 50
    assert directional.minus_di.iloc[3] == 0
    assert directional.adx.iloc[5] == 100
    assert tr.aroon(data, 3).up.iloc[3] == 100
    assert tr.aroon(data, 3).down.iloc[3] == 0
    st = tr.supertrend(data, 3, 1)
    assert st.supertrend.iloc[2] == 10
    assert st.direction.iloc[2] == 1
    assert tr.supertrend(bars([10, 11, 12, 5]), 3, 1).direction.iloc[-1] == -1
    sar = tr.parabolic_sar(data)
    assert sar.sar.iloc[2] == 9
    assert sar.sar.iloc[3] == pytest.approx(9.16)
    assert tr.parabolic_sar(bars([10, 11, 12, 5])).direction.iloc[-1] == -1
    cloud = tr.ichimoku(data, 2, 3, 4, 1)
    assert cloud.conversion.iloc[3] == 12.5
    assert cloud.base.iloc[3] == 12
    assert cloud.span_b_raw.iloc[3] == 11.5
    assert cloud.cloud_a.iloc[3] == 11.25
    assert cloud.lagging_close.iloc[3] == 12
    assert tr.vortex(data, 3).plus.iloc[3] == 1.5
    assert tr.vortex(data, 3).minus.iloc[3] == 0.5
    assert tr.choppiness(data, 3).iloc[2] == pytest.approx(100 * np.log10(6 / 4) / np.log10(3))
    assert tr.vhf(data.close, 3).iloc[3] == pytest.approx(2 / 3)
    assert tr.linear_regression_slope(data.close, 3).iloc[2] == 1
    regression = tr.linear_regression_channel(data.close, 3)
    assert list(regression.iloc[2]) == [12, 12, 12, 1]


def test_candle_geometry_and_patterns():
    d = bars([10, 11, 12, 13, 14, 15, 16])
    f = pa.candle_features(d)
    assert list(f.iloc[0]) == [0.5, 2, 1, 0.5, 0.5, 0.25, 0.25]
    assert pa.consecutive_candles(d).tolist() == [1, 2, 3, 4, 5, 6, 7]
    assert pa.narrow_range(d, 4).iloc[3]
    assert pa.narrow_range(d, 7).iloc[6]
    assert not pa.range_expansion(d, 2, 1.5).iloc[2]
    assert pa.heikin_ashi(d).open.iloc[0] == 9.75
    assert pa.heikin_ashi(d).close.iloc[0] == 9.875
    assert pa.heikin_ashi(d).open.iloc[1] == 9.8125
    d.loc[d.index[1], ["open", "high", "low", "close"]] = [10, 10.5, 9.5, 10.25]
    assert pa.inside_bar(d).iloc[1]
    d.loc[d.index[2], "low"] = 9
    assert pa.outside_bar(d).iloc[2]
    d = pd.DataFrame([[11, 11.2, 9.8, 10], [9.5, 11.7, 9.3, 11.5]], columns=["open", "high", "low", "close"])
    assert pa.engulfing(d).bullish.iloc[1]
    assert pa.engulfing(d.iloc[::-1].reset_index(drop=True)).bearish.iloc[1] == False
    d = pd.DataFrame([[10, 10.1, 7, 9.9]], columns=["open", "high", "low", "close"])
    assert pa.pin_bar(d).bullish.iloc[0]
    assert pa.doji(d).iloc[0]
    assert pa.hammer_shooting_star(d).hammer.iloc[0]
    d = pd.DataFrame([[10, 12.1, 9.9, 12]], columns=["open", "high", "low", "close"])
    assert pa.marubozu(d).bullish.iloc[0]
    d = pd.DataFrame([[12, 12.1, 7.9, 8], [8, 8.3, 7.8, 8.2], [8.2, 11.1, 8, 11]], columns=["open", "high", "low", "close"])
    assert pa.morning_evening_star(d).morning_star.iloc[2]
    reflected = 20 - d.rename(columns={"high": "low", "low": "high"})
    assert pa.morning_evening_star(reflected).evening_star.iloc[2]
    assert pa.hammer_shooting_star(reflected.iloc[[1]]).shape == (1, 2)


def test_structure_confirmations_and_breaks():
    d = bars([10, 12, 10, 13, 10, 14, 9, 8, 12])
    swings = ms.confirmed_swings(d, 1, 1)
    assert pd.isna(swings.swing_high.iloc[1])
    assert swings.swing_high.iloc[2] == 13
    assert swings.swing_low.iloc[3] == 9
    assert ms.swing_structure(d, 1, 1).higher_high.iloc[4]
    assert ms.swing_structure(d, 1, 1).lower_low.iloc[8]
    equal = ms.equal_high_low(bars([10, 12, 10, 12, 10]), 1, 1)
    assert equal.equal_high.iloc[4]
    zones = ms.support_resistance_zones(d, 1, 1, 0.1)
    assert zones.resistance_lower.iloc[2] == pytest.approx(11.7)
    assert zones.support_upper.iloc[3] == pytest.approx(9.9)
    fibonacci = ms.fibonacci_retracement(d, 1, 1)
    assert fibonacci["level_0.5"].iloc[3] == 11
    gap = ms.fair_value_gap(bars([10, 11, 14]))
    assert gap.bullish.iloc[2]
    assert gap.bull_lower.iloc[2] == 11
    assert gap.bull_upper.iloc[2] == 13
    gap = ms.fair_value_gap(bars([14, 11, 10]))
    assert gap.bearish.iloc[2]
    sweep = bars([10, 12, 10, 12.5])
    assert ms.liquidity_sweep(sweep, 1, 1).high_sweep.iloc[3]
    d = bars([10, 12, 10, 14, 8])
    d.loc[d.index[-1], "open"] = 12
    d.loc[d.index[-1], "high"] = 12.5
    breaks = ms.structure_breaks(d, 1, 1)
    assert breaks.bos.iloc[3] == 1
    assert breaks.choch.iloc[4] == -1
    assert breaks.mss.iloc[4] == -1


@pytest.mark.parametrize("method, column", [("traditional", "r1"), ("fibonacci", "r1"), ("camarilla", "r1"), ("cpr", "top")])
def test_previous_period_pivots(method, column):
    d = bars([10, 12, 20], pd.DatetimeIndex(["2024-01-01 10:00Z", "2024-01-01 11:00Z", "2024-01-02 10:00Z"]))
    # Prior H=13, L=9, C=12, P=34/3.
    expected = {"traditional": 2 * 34 / 3 - 9, "fibonacci": 34 / 3 + 0.382 * 4, "camarilla": 12 + 1.1 * 4 / 12, "cpr": 2 * 34 / 3 - 11}[method]
    result = ms.daily_pivots(d, method)
    assert result[column].iloc[-1] == pytest.approx(expected)
    assert result.iloc[0].isna().all()
    assert ms.previous_period_levels(d).high.iloc[-1] == 13
    d.index = pd.DatetimeIndex(["2024-01-01 10:00Z", "2024-01-01 11:00Z", "2024-01-08 10:00Z"])
    assert ms.previous_period_levels(d, "week").high.iloc[-1] == 13


def test_sessions_vwap_orb_calendar_and_gap():
    index = pd.date_range("2024-01-02 08:00", periods=5, freq="15min", tz="UTC")
    d = bars([10, 11, 13, 14, 15], index)
    kwargs = dict(timezone="Europe/London", start="08:00", end="09:00")
    features = se.session_features(index, **kwargs)
    assert features.minutes_since_open.iloc[2] == 30
    assert not features.active.iloc[-1]
    ranges = se.session_range(d, **kwargs)
    assert ranges.high.iloc[0] == 11
    assert ranges.high.iloc[2] == 14
    assert ranges.low.iloc[2] == 9
    assert ranges.iloc[-1].isna().all()
    orb = se.opening_range_breakout(d, **kwargs, minutes=30)
    assert orb.high.iloc[2] == 12
    assert orb.low.iloc[2] == 9
    assert orb.breakout.iloc[2] == 1
    assert se.session_vwap(d, **kwargs, volume_kind="tick").iloc[1] == 10.5
    assert se.calendar_features(index).day_of_week.iloc[0] == 1
    assert se.calendar_features(index).hour_of_day.iloc[0] == 8
    assert se.london_session_range(d).high.iloc[0] == 11
    assert se.asia_session_range(d).high.iloc[0] == 11
    assert se.new_york_session_range(d).isna().all().all()
    overlap = pd.DatetimeIndex(["2024-03-15 12:00Z", "2024-03-15 13:00Z", "2024-01-15 13:00Z"])
    assert se.london_new_york_overlap(overlap.sort_values()).tolist() == [True, True, True]
    dst = se.session_features(pd.DatetimeIndex(["2024-01-02 13:00Z", "2024-07-02 12:00Z"]), timezone="America/New_York", start="08:00", end="17:00")
    assert dst.minutes_since_open.tolist() == [0, 0]
    overnight = se.session_features(pd.DatetimeIndex(["2024-01-02 01:00Z"]), timezone="UTC", start="22:00", end="06:00")
    assert overnight.minutes_since_open.iloc[0] == 180
    assert str(overnight.session_date.iloc[0].date()) == "2024-01-01"
    d = bars([10, 14], pd.DatetimeIndex(["2024-01-05 21:00Z", "2024-01-07 22:00Z"]))
    assert se.weekend_gap(d).iloc[1] == 3.5


def test_regimes_and_cycle(data):
    assert se.trend_range_regime(data, 3).iloc[-1] == 1
    assert se.volatility_regime(data, 3, 4).iloc[-1] == 0
    wave = pd.Series(100 + np.sin(2 * np.pi * np.arange(128) / 8))
    cycle = se.dominant_cycle(wave, 64, 4, 32)
    assert cycle.period.iloc[-1] == 8
    assert -np.pi <= cycle.phase.iloc[-1] <= np.pi
    assert se.dominant_cycle(pd.Series([10.] * 100)).isna().all().all()


# Every public calculation is exercised on multiple prefixes, with unchanged
# input and identical repeated results. Use nontrivial oscillating prices.
CASES = [
    *[(lambda d, fn=fn: fn(d.close, 3)) for fn in (ma.sma, ma.ema, ma.wma, ma.rma, mom.rsi, mom.roc, mom.momentum, tr.vhf, tr.linear_regression_slope, tr.linear_regression_channel, vol.rolling_std, vol.bollinger_bands, vol.bollinger_bandwidth, vol.bollinger_percent_b)],
    lambda d: mom.macd(d.close, 2, 4, 2), lambda d: mom.ppo(d.close, 2, 4, 2),
    lambda d: mom.stochastic_rsi(d.close, 3, 3, 2), lambda d: mom.tsi(d.close, 3, 2),
    lambda d: mom.stochastic(d, 3, 2), lambda d: mom.cci(d, 3), lambda d: mom.williams_r(d, 3), lambda d: mom.awesome_oscillator(d, 2, 4),
    *[(lambda d, fn=fn: fn(d, 3)) for fn in (tr.adx, tr.supertrend, tr.aroon, tr.vortex, tr.choppiness, vol.atr, vol.natr, vol.keltner_channels, vol.donchian_channels)],
    lambda d: tr.parabolic_sar(d), lambda d: tr.ichimoku(d, 2, 3, 4, 2),
    *[(lambda d, fn=fn: fn(d.close, 3, periods_per_year=100)) for fn in (vol.historical_volatility, vol.realized_volatility)],
    *[(lambda d, fn=fn: fn(d, 3, periods_per_year=100)) for fn in (vol.parkinson_volatility, vol.garman_klass_volatility)],
    *[(lambda d, fn=fn: fn(d)) for fn in (pa.candle_features, pa.inside_bar, pa.outside_bar, pa.engulfing, pa.pin_bar, pa.doji, pa.hammer_shooting_star, pa.morning_evening_star, pa.marubozu, pa.heikin_ashi, pa.narrow_range, pa.consecutive_candles)],
    lambda d: pa.range_expansion(d, 3),
    *[(lambda d, fn=fn: fn(d, 1, 1)) for fn in (ms.confirmed_swings, ms.swing_structure, ms.structure_breaks, ms.support_resistance_zones, ms.fibonacci_retracement, ms.equal_high_low, ms.liquidity_sweep)],
    lambda d: ms.fair_value_gap(d), lambda d: ms.previous_period_levels(d), lambda d: ms.previous_period_levels(d, "week"),
    *[(lambda d, method=method: ms.daily_pivots(d, method)) for method in ("traditional", "fibonacci", "camarilla", "cpr")],
    *[(lambda d, fn=fn: fn(d)) for fn in (se.asia_session_range, se.london_session_range, se.new_york_session_range, se.weekend_gap)],
    lambda d: se.session_features(d.index, timezone="UTC", start="00:00", end="12:00"),
    lambda d: se.session_range(d, timezone="UTC", start="00:00", end="12:00"),
    lambda d: se.session_vwap(d, timezone="UTC", start="00:00", end="12:00", volume_kind="tick"),
    lambda d: se.opening_range_breakout(d, timezone="UTC", start="00:00", end="12:00"),
    lambda d: se.calendar_features(d.index), lambda d: se.london_new_york_overlap(d.index),
    lambda d: se.trend_range_regime(d, 3), lambda d: se.volatility_regime(d, 3, 4), lambda d: se.dominant_cycle(d.close, 16, 4, 8),
]


@pytest.mark.parametrize("calculation", CASES)
def test_all_indicators_preserve_index_causality_and_inputs(calculation):
    d = bars(100 + np.sin(np.arange(80)) * 5 + np.arange(80) / 5)
    original = d.copy(deep=True)
    full = calculation(d)
    assert full.index.equals(d.index)
    compare = pd.testing.assert_frame_equal if isinstance(full, pd.DataFrame) else pd.testing.assert_series_equal
    compare(full, calculation(d))
    for length in (1, 3, 9, 23, 49, 79):
        compare(full.iloc[:length], calculation(d.iloc[:length]))
    pd.testing.assert_frame_equal(d, original)


@pytest.mark.parametrize("function", [ma.sma, ma.ema, ma.wma, ma.rma])
@pytest.mark.parametrize("window", [0, -1, 1.5])
def test_invalid_windows(function, window):
    with pytest.raises(ValueError):
        function(pd.Series([1., 2.]), window)


def test_invalid_inputs(data):
    with pytest.raises(ValueError, match="Missing"):
        vol.atr(data.drop(columns="high"))
    with pytest.raises(ValueError):
        tr.parabolic_sar(data, step=0)
    with pytest.raises(ValueError):
        tr.ichimoku(data, displacement=-1)
    with pytest.raises(ValueError):
        ms.confirmed_swings(data, right=0)
    with pytest.raises(ValueError):
        se.session_features(data.index[::-1], timezone="UTC", start="00:00", end="12:00")
    with pytest.raises(ValueError):
        se.session_vwap(data, timezone="UTC", start="00:00", end="12:00", volume_kind="unknown")
    with pytest.raises(ValueError):
        vol.historical_volatility(data.close, periods_per_year=0)
    with pytest.raises(ValueError):
        vol.historical_volatility(pd.Series([1., 0., 1.]), periods_per_year=252)


@pytest.mark.parametrize("calculation", CASES)
def test_empty_and_missing_inputs(calculation):
    d = bars(100 + np.sin(np.arange(40)) * 5)
    empty = calculation(d.iloc[:0])
    assert empty.index.equals(d.index[:0])
    d.iloc[10] = np.nan
    result = calculation(d)
    assert result.index.equals(d.index)
    numeric = result.select_dtypes(include="number") if isinstance(result, pd.DataFrame) else result if pd.api.types.is_numeric_dtype(result.dtype) else None
    if numeric is not None:
        assert not np.isinf(numeric.to_numpy(dtype=float, na_value=np.nan)).any()


def test_nan_and_zero_denominators():
    flat = bars([10.] * 30)
    flat.loc[:, ["open", "high", "low"]] = 10
    for result in [mom.rsi(flat.close, 3), mom.stochastic(flat, 3)["%k"], mom.williams_r(flat, 3), mom.cci(flat, 3), mom.tsi(flat.close, 3, 2), vol.bollinger_percent_b(flat.close, 3), tr.vhf(flat.close, 3), tr.choppiness(flat, 3), tr.adx(flat, 3).adx]:
        assert result.isna().all()
    assert pa.doji(flat).isna().all()
    d = bars([10.] * 12)
    d.iloc[4] = np.nan
    assert vol.atr(d, 3).iloc[4:7].isna().all()
    assert pd.notna(vol.atr(d, 3).iloc[7])
    assert pa.inside_bar(d).iloc[4:6].isna().all()
    assert ms.confirmed_swings(d, 1, 1).iloc[4:7].isna().all().all()
    kwargs = dict(timezone="UTC", start="00:00", end="23:00", volume_kind="traded")
    assert se.session_vwap(d, **kwargs).iloc[4:].isna().all()
    d.volume = 0
    assert se.session_vwap(d, **kwargs).isna().all()


def test_bearish_patterns_and_lower_structures():
    d = pd.DataFrame([[10, 11.2, 9.8, 11], [11.5, 11.7, 9.3, 9.5]], columns=["open", "high", "low", "close"])
    assert pa.engulfing(d).bearish.iloc[1]
    d = pd.DataFrame([[10, 13, 9.8, 10.1]], columns=["open", "high", "low", "close"])
    assert pa.pin_bar(d).bearish.iloc[0]
    assert pa.hammer_shooting_star(d).shooting_star.iloc[0]
    d = pd.DataFrame([[12, 12.1, 9.9, 10]], columns=["open", "high", "low", "close"])
    assert pa.marubozu(d).bearish.iloc[0]
    d = bars([12, 10, 13, 11, 12, 9, 12])
    structure = ms.swing_structure(d, 1, 1)
    assert structure.higher_low.iloc[4]
    assert structure.lower_high.iloc[5]
    assert ms.equal_high_low(bars([12, 10, 12, 10, 12]), 1, 1).equal_low.iloc[4]
    d = bars([12, 10, 12, 9.5])
    assert ms.liquidity_sweep(d, 1, 1).low_sweep.iloc[3]


def test_ema_against_documented_pandas_reference():
    # pandas reference recurrence and weights, independent of our wrapper.
    s = pd.Series([1., 2., 4., 3., 8., 5.])
    for adjust in (False, True):
        pd.testing.assert_series_equal(ma.ema(s, 3, adjust), s.ewm(span=3, adjust=adjust, min_periods=3).mean())


def test_input_order_and_numeric_validation(data):
    for invalid in (data.iloc[::-1], data.set_axis([data.index[0]] * len(data)), data.set_axis(data.index.tz_localize(None))):
        with pytest.raises(ValueError):
            vol.atr(invalid)
        with pytest.raises(ValueError):
            ma.sma(invalid.close, 3)
    invalid = data.copy()
    invalid.loc[invalid.index[0], "high"] = 1
    with pytest.raises(ValueError, match="OHLC"):
        tr.adx(invalid)
    with pytest.raises(ValueError):
        ma.ema(pd.Series([1., np.inf]), 2)


def test_cycle_phase_independent_direct_hilbert_sum():
    values = 100 + np.sin(2 * np.pi * np.arange(16) / 4)
    x = np.arange(16) - 7.5
    y = values - values.mean() - x * sum(x * values) / sum(x ** 2)
    # Even-length discrete Hilbert kernel: 2/N*cot(pi*k/N) for odd k.
    quadrature = sum(y[j] * (2 / 16) / np.tan(np.pi * (15 - j) / 16) for j in range(16) if (15 - j) % 2)
    expected_phase = np.arctan2(quadrature, y[-1])
    actual = se.dominant_cycle(pd.Series(values), 16, 4, 8)
    assert actual.period.iloc[-1] == 4
    assert actual.phase.iloc[-1] == pytest.approx(expected_phase)
```
<!-- SOURCE_END tests/test_indicators.py -->
