"""Read-only performance probes. Usage: python perf.py <case> <n>. Prints JSON with seconds and peak working set."""
import sys, json, time, ctypes, ctypes.wintypes as wt
sys.path.insert(0, r"C:\Users\Admin\Documents\quant_backtest_system")
import numpy as np, pandas as pd

class PMC(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]
_k32 = ctypes.WinDLL("kernel32"); _k32.GetCurrentProcess.restype = wt.HANDLE
_ps = ctypes.WinDLL("psapi"); _ps.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
def peak_mb():
    c = PMC(); c.cb = ctypes.sizeof(PMC)
    _ps.GetProcessMemoryInfo(_k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 2**20

def data(n, freq="min"):
    rng = np.random.default_rng(0)
    idx = pd.date_range("2024-01-01", periods=n, freq=freq, tz="UTC")
    c = np.round(1.08 + np.cumsum(rng.normal(0, 1e-4, n)), 5); o = np.round(np.r_[c[0], c[:-1]], 5)
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + 5e-5, "low": np.minimum(o, c) - 5e-5, "close": c, "volume": 1.0}, index=idx)

case, n = sys.argv[1], int(sys.argv[2])
d = data(n); base_mb = peak_mb()
t = time.perf_counter(); extra = {}
if case.startswith("engine"):
    from core.cost_model import CostModel
    from core.engine import BacktestEngine
    from strategies.base_strategy import BaseStrategy
    v = {"source": "perf", "symbol": "EURUSD", "source_timezone": "UTC", "timestamp_encoding": "aware", "timestamp_kind": "open",
         "price_type": "Bid", "timeframe": "1min", "instrument_specifications": {"tick_size": 1e-5, "pip_size": 1e-4,
         "contract_size": 100000, "quantity_unit": "lots", "quote_currency": "USD", "minimum_quantity_increment": 0.01}}
    m = {k: {"value": x, "confirmed": True, "evidence": "perf"} for k, x in v.items()}
    e = BacktestEngine(m, CostModel(1e-4, 1e-5, 3.5), initial_capital=1e6, account_currency="USD", quantity=1)
    class Batch(BaseStrategy):
        def generate_signals(self, x):
            a = x.close.rolling(20).mean()
            return pd.DataFrame({"signal": (x.close > a).astype(int), "exit": x.close < a}, index=x.index).assign(
                signal=lambda f: f.signal.where(~f.exit, 0))
    from collections import deque
    class Inc(BaseStrategy):
        signal_history_limit = 1
        def __init__(self): super().__init__(); self.v = deque(maxlen=20)
        def generate_signal(self, x):
            c = float(x.close.iloc[-1]); self.v.append(c)
            if len(self.v) < 20: return pd.Series({"signal": 0, "exit": False})
            a = sum(self.v) / 20
            return pd.Series({"signal": 0, "exit": True}) if c < a else pd.Series({"signal": 1, "exit": False})
    r = e.run(d, Batch() if case == "engine_batch" else Inc())
    extra = {"orders": len(r.orders), "fills": len(r.fills), "states": len(r.states), "events": len(r.events)}
elif case == "sar":
    from indicators.trend import parabolic_sar; parabolic_sar(d)
elif case == "structure_breaks":
    from indicators.market_structure import structure_breaks; structure_breaks(d)
elif case == "rma":
    from indicators.moving_averages import rma; rma(d.close, 14)
elif case == "atr":
    from indicators.volatility import atr; atr(d, 14)
elif case == "rsi":
    from indicators.momentum import rsi; rsi(d.close, 14)
elif case == "adx":
    from indicators.trend import adx; adx(d, 14)
elif case == "supertrend":
    from indicators.trend import supertrend; supertrend(d)
elif case == "sma":
    from indicators.moving_averages import sma; sma(d.close, 20)
elif case == "validate":
    from core.data_validator import validate_data
    v = {"source": "perf", "symbol": "EURUSD", "source_timezone": "UTC", "timestamp_encoding": "aware", "timestamp_kind": "open",
         "price_type": "Bid", "timeframe": "1min", "instrument_specifications": {"tick_size": 1e-5, "pip_size": 1e-4,
         "contract_size": 100000, "quantity_unit": "lots", "quote_currency": "USD", "minimum_quantity_increment": 0.01}}
    validate_data(d, {k: {"value": x, "confirmed": True, "evidence": "perf"} for k, x in v.items()})
elif case == "causality_all":
    from core.causality import check_prefix_invariance
    from indicators.moving_averages import sma
    check_prefix_invariance(lambda f: sma(f.close, 20), d)
el = time.perf_counter() - t
print(json.dumps({"case": case, "n": n, "seconds": round(el, 3), "us_per_bar": round(el / n * 1e6, 2),
                  "peak_working_set_mb": round(peak_mb(), 1), "baseline_mb": round(base_mb, 1), **extra}))
