import sys, json, hashlib, pickle
sys.path.insert(0, r"C:\Users\Admin\Documents\quant_backtest_system")
import numpy as np, pandas as pd
from core.cost_model import CostModel
from core.models import Instrument
from core.engine import BacktestEngine
from strategies.base_strategy import BaseStrategy

def meta(tick, contract=1, unit="units", inc=0.001):
    v = {"source": "p", "symbol": "T", "source_timezone": "UTC", "timestamp_encoding": "aware", "timestamp_kind": "open",
         "price_type": "Bid", "timeframe": "1min", "instrument_specifications": {"tick_size": tick, "pip_size": tick,
         "contract_size": contract, "quantity_unit": unit, "quote_currency": "USD", "minimum_quantity_increment": inc}}
    return {k: {"value": x, "confirmed": True, "evidence": "p"} for k, x in v.items()}

mode = sys.argv[1]
if mode == "f2b":
    ts = pd.Timestamp("2024-01-01", tz="UTC"); out = {}
    for label, tick, lo, slip_ticks in (("BTC", 0.01, 10_000_000, 1), ("BTC", 0.01, 10_000_000, 3), ("EURUSD", 1e-5, 100_000, 1), ("XAU", 0.001, 1_800_000, 2)):
        inst = Instrument.from_metadata(meta(tick)); c = CostModel(0, slip_ticks * tick, 0); bad_b = bad_s = 0
        for j in range(lo, lo + 5000):
            p = j * tick
            b = c.fill(instrument=inst, order_id=1, side=1, quantity=0.001, timestamp=ts, price=p, conversion_rate=1, reason="BUY")
            s = c.fill(instrument=inst, order_id=1, side=-1, quantity=0.001, timestamp=ts, price=p, conversion_rate=1, reason="SELL")
            if round((b.price - p) / tick) != slip_ticks: bad_b += 1
            if round((p - s.price) / tick) != slip_ticks: bad_s += 1
        out[f"{label}_slip{slip_ticks}"] = {"buy_extra_tick": f"{bad_b}/5000", "sell_extra_tick": f"{bad_s}/5000"}
    print(json.dumps(out))
elif mode == "hash":
    rng = np.random.default_rng(42); n = 5000
    idx = pd.date_range("2024-01-01", periods=n, freq="min", tz="UTC")
    c = np.round(1.08 + np.cumsum(rng.normal(0, 1e-4, n)), 5); o = np.round(np.r_[c[0], c[:-1]], 5)
    d = pd.DataFrame({"open": o, "high": np.maximum(o, c) + 5e-5, "low": np.minimum(o, c) - 5e-5, "close": c}, index=idx)
    class S(BaseStrategy):
        def generate_signals(self, x):
            f = x.close.rolling(10).mean(); s = x.close.rolling(40).mean(); sig = (f > s).astype(int) - (f < s).astype(int)
            return pd.DataFrame({"signal": sig, "exit": False, "sl": x.close - 3e-4 * sig, "tp": x.close + 6e-4 * sig}, index=x.index)
    S.signal_history_limit = 60
    e = BacktestEngine(meta(1e-5, 100000, "lots", 0.01), CostModel(1e-4, 1e-5, 3.5), initial_capital=1e6, account_currency="USD", quantity=1)
    r = e.run(d, S())
    payload = repr((r.orders, r.fills, r.trades, r.states, [sorted(ev.items(), key=str) for ev in r.events]))
    print(json.dumps({"sha256": hashlib.sha256(payload.encode()).hexdigest(), "trades": len(r.trades), "final_equity": r.states[-1].equity}))
