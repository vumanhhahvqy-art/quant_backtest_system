"""Read-only verification probes for the final audit. Imports project code; never writes to project."""
import sys, json, math, os, tempfile, traceback, hashlib
sys.path.insert(0, r"C:\Users\Admin\Documents\quant_backtest_system")
import numpy as np, pandas as pd
from core.cost_model import CostModel
from core.engine import BacktestEngine, ConversionRates
from core.models import Instrument
from core.data_validator import validate_data
from core.data_loader import load_csv, write_json
from core.causality import check_prefix_invariance
from strategies.base_strategy import BaseStrategy

R = {}
def probe(name):
    def deco(fn):
        try:
            R[name] = fn()
        except Exception as e:
            R[name] = {"EXCEPTION": f"{type(e).__name__}: {str(e)[:300]}"}
        print(name, "=>", json.dumps(R[name], default=str)[:900]); sys.stdout.flush()
        return fn
    return deco

def meta(timeframe="1h", kind="open", price_type="Mid", tick=0.01, contract=10, unit="lots", inc=0.1, quote="USD"):
    v = {"source": "probe", "symbol": "TESTUSD", "source_timezone": "UTC", "timestamp_encoding": "aware",
         "timestamp_kind": kind, "price_type": price_type, "timeframe": timeframe,
         "instrument_specifications": {"tick_size": tick, "pip_size": tick, "contract_size": contract,
                                       "quantity_unit": unit, "quote_currency": quote,
                                       "minimum_quantity_increment": inc}}
    return {k: {"value": x, "confirmed": True, "evidence": "probe"} for k, x in v.items()}

def bars4():
    return pd.DataFrame({"open": [100., 102., 110., 112.], "high": [101., 105., 113., 114.],
                         "low": [99., 101., 109., 111.], "close": [100., 104., 112., 113.]},
                        index=pd.date_range("2024-01-01", periods=4, freq="h", tz="UTC"))

class Scripted(BaseStrategy):
    def __init__(self, ins):
        super().__init__(); self.ins = ins
    def generate_signals(self, df):
        out = pd.DataFrame({"signal": 0, "exit": False}, index=df.index)
        for k, v in self.ins.get(len(df), {}).items():
            if k not in out: out[k] = float("nan")
            out.loc[df.index[-1], k] = v
        return out

def eng(m=None, costs=None, cap=10000, q=1):
    return BacktestEngine(m or meta(), costs or CostModel(0, 0, 0), initial_capital=cap, account_currency="USD", quantity=q)

# ---------------- CORE ----------------
@probe("CORE-F2a_exact_touch_float")
def _():
    out = {}
    tick = 1e-5
    for k in (2, 4, 10, 16):
        c = CostModel(k * tick, 0, 0); miss = 0; total = 0
        for m in range(100_000, 130_000, 7):
            bar = {"open": m*tick, "high": m*tick, "low": m*tick, "close": m*tick}
            low = c.side_bar(bar, "Mid", -1)["low"]; total += 1
            if not low <= (m - k // 2) * tick: miss += 1
        out[f"k={k}"] = f"{miss}/{total} exact-touch SL comparisons evaluate False"
    return out

@probe("CORE-F2b_tick_rounding_large_price")
def _():
    m = meta(tick=0.01, contract=1, unit="units", inc=0.001)
    inst = Instrument.from_metadata(m); c = CostModel(0, 0, 0); moved_buy = moved_sell = 0
    ts = pd.Timestamp("2024-01-01", tz="UTC")
    for j in range(10_000_000, 10_002_000):
        p = j * 0.01
        fb = c.fill(instrument=inst, order_id=1, side=1, quantity=0.001, timestamp=ts, price=p, conversion_rate=1, reason="BUY")
        fs = c.fill(instrument=inst, order_id=1, side=-1, quantity=0.001, timestamp=ts, price=p, conversion_rate=1, reason="SELL")
        if abs(fb.price - p) > 5e-3: moved_buy += 1
        if abs(fs.price - p) > 5e-3: moved_sell += 1
    # also EURUSD-scale and XAU-scale
    res = {"BTC_scale_buy_moved_1tick": f"{moved_buy}/2000", "BTC_scale_sell_moved_1tick": f"{moved_sell}/2000"}
    for label, tick, lo in (("EURUSD_scale", 1e-5, 100_000), ("XAU_scale", 0.001, 1_800_000)):
        inst2 = Instrument.from_metadata(meta(tick=tick, contract=1, unit="units", inc=1)); mv = 0
        for j in range(lo, lo + 20000):
            p = j * tick
            f = c.fill(instrument=inst2, order_id=1, side=1, quantity=1, timestamp=ts, price=p, conversion_rate=1, reason="BUY")
            if abs(f.price - p) > tick / 2: mv += 1
        res[label + "_buy_moved"] = f"{mv}/20000"
    return res

@probe("CORE-F3_gap_entry_rejected")
def _():
    b = bars4(); b.iloc[1] = [98., 99., 97., 98.]
    r = eng().run(b, Scripted({1: {"signal": 1, "sl": 99.5, "tp": 110}}), expected_timestamps=b.index)
    return {"events": [e for e in r.events if e["status"] != "submitted"], "fills": len(r.fills),
            "trades": len(r.trades), "has_rejection_counter": "rejected_orders" in r.assumptions,
            "final_equity": r.states[-1].equity}

@probe("CORE-F4_strategy_reuse")
def _():
    class Stateful(BaseStrategy):
        signal_history_limit = 1
        def __init__(self): super().__init__(); self.n = 0
        def generate_signal(self, d):
            self.n += 1
            return pd.Series({"signal": int(self.n == 1), "exit": False})
    b = bars4(); e = eng(); s = Stateful()
    a = e.run(b, s, expected_timestamps=b.index); c = e.run(b, s, expected_timestamps=b.index)
    return {"run1_fills": len(a.fills), "run2_fills": len(c.fills), "identical": a == c}

@probe("CORE-F5_provenance_keys")
def _():
    b = bars4(); r = eng().run(b, Scripted({}), expected_timestamps=b.index)
    keys = sorted(r.assumptions.keys())
    return {"keys": keys, "missing": [k for k in ("data_sha256", "strategy", "strategy_params", "library_versions", "git_commit") if k not in keys]}

@probe("CORE-F7_excess_spread_error_context")
def _():
    b = bars4()
    try:
        eng(costs=CostModel(250, 0, 0)).run(b, Scripted({1: {"signal": 1}}), expected_timestamps=b.index)
        return "no error"
    except ValueError as e:
        return {"message": str(e), "mentions_timestamp": "2024" in str(e)}

@probe("CORE-F7b_programming_error_swallowed_as_rejection")
def _():
    # Insufficient capital path: free-text rejection, same except-branch as any ValueError in Portfolio.open
    b = bars4(); r = eng(cap=100).run(b, Scripted({1: {"signal": 1}}), expected_timestamps=b.index)
    return [e for e in r.events if e["status"] == "rejected"]

@probe("NEW-SELL_while_long_does_not_reverse")
def _():
    b = bars4(); r = eng().run(b, Scripted({1: {"signal": 1}, 2: {"signal": -1}}), expected_timestamps=b.index)
    return {"events": [(e["status"], e["reason"]) for e in r.events], "open_position_dir": r.open_position.direction if r.open_position else None}

@probe("NEW-level_signal_spam_orders")
def _():
    n = 500; idx = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    c = 100 + np.arange(n) * 0.01
    d = pd.DataFrame({"open": c, "high": c + .5, "low": c - .5, "close": c}, index=idx)
    class Always(BaseStrategy):
        signal_history_limit = 1
        def generate_signal(self, x): return pd.Series({"signal": 1, "exit": False})
    r = eng().run(d, Always())
    return {"bars": n, "orders": len(r.orders), "fills": len(r.fills),
            "rejected_events": sum(e["status"] == "rejected" for e in r.events)}

@probe("NEW-bool_and_float_signal_accepted")
def _():
    out = {}
    for val in (True, 1.0, np.int64(1)):
        class S(BaseStrategy):
            signal_history_limit = 1
            def generate_signal(self, x, v=val): return pd.Series({"signal": v, "exit": False})
        b = bars4()
        try:
            r = eng().run(b, S(), expected_timestamps=b.index); out[repr(val)] = f"accepted, orders={len(r.orders)}"
        except Exception as e:
            out[repr(val)] = f"rejected: {e}"
    class L(BaseStrategy):
        signal_history_limit = np.int64(5)
        def generate_signal(self, x): return pd.Series({"signal": 0})
    try:
        eng().run(bars4(), L(), expected_timestamps=bars4().index); out["np.int64 history limit"] = "accepted"
    except ValueError as e:
        out["np.int64 history limit"] = f"rejected: {e}"
    return out

@probe("NEW-future_column_passthrough_to_strategy")
def _():
    n = 300; rng = np.random.default_rng(1); idx = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    c = 100 + np.cumsum(rng.normal(0, 0.5, n)); o = np.r_[c[0], c[:-1]]
    d = pd.DataFrame({"open": o, "high": np.maximum(o, c) + .1, "low": np.minimum(o, c) - .1, "close": c}, index=idx)
    d["next_close"] = d["close"].shift(-2)  # precomputed leaking column
    class Peek(BaseStrategy):
        signal_history_limit = 1
        def __init__(self): super().__init__(); self.pos = 0
        def generate_signal(self, x):
            nc = x["next_close"].iloc[-1]; cl = x["close"].iloc[-1]
            if np.isnan(nc): return pd.Series({"signal": 0, "exit": self.pos != 0})
            want = 1 if nc > cl else -1
            if self.pos == 0: self.pos = want; return pd.Series({"signal": want, "exit": False})
            self.pos = 0; return pd.Series({"signal": 0, "exit": True})
    r = eng(cap=1e6).run(d, Peek())
    wins = sum(t.gross_pnl > 0 for t in r.trades)
    return {"engine_raised": False, "trades": len(r.trades), "winning": wins,
            "validate_flags_extra_column": any("next_close" in w for w in validate_data(d, meta())["warnings"])}

@probe("NEW-ConversionRates_semantics")
def _():
    idx = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC")
    rates = pd.Series([1.10, 1.20, 1.30], index=idx)  # if these were bar CLOSES labelled by bar OPEN...
    cr = ConversionRates("JPY", "USD", rates)
    return {"at(bar1 open)": cr.at(idx[1]), "note": "returns value stamped at the open instant; if series is close-of-bar labelled by open, this is the bar's own future close"}

# ---------------- Engine causality: perturb bar k ----------------
@probe("SYS-engine_prefix_invariance_random_k")
def _():
    rng = np.random.default_rng(7); n = 400; idx = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    c = 100 + np.cumsum(rng.normal(0, 0.3, n)); o = np.r_[c[0], c[:-1]]
    d = pd.DataFrame({"open": o, "high": np.maximum(o, c) + .2, "low": np.minimum(o, c) - .2, "close": c}, index=idx)
    class SMA(BaseStrategy):
        def generate_signals(self, x):
            f = x.close.rolling(10).mean(); s = x.close.rolling(30).mean()
            sig = np.where(f > s, 1, np.where(f < s, -1, 0))
            ex = pd.Series(False, index=x.index)
            return pd.DataFrame({"signal": sig, "exit": ex, "sl": x.close - 1.5 * np.sign(sig + 1e-9), "tp": x.close + 3 * np.sign(sig + 1e-9)}, index=x.index)
    e = eng(costs=CostModel(0.02, 0.01, 1), cap=1e6)
    base = e.run(d, SMA()); bad = []
    for k in (50, 137, 250, 399):
        d2 = d.copy(); d2.iloc[k] = [d2.open.iloc[k], d2.high.iloc[k] + 50, d2.low.iloc[k], d2.close.iloc[k] + 40]
        r = e.run(d2, SMA()); cut = idx[k]
        if [s for s in base.states if s.timestamp <= cut] != [s for s in r.states if s.timestamp <= cut]: bad.append((k, "states"))
        if [f for f in base.fills if f.timestamp < cut] != [f for f in r.fills if f.timestamp < cut]: bad.append((k, "fills"))
        if [o for o in base.orders if o.submitted_at <= cut] != [o for o in r.orders if o.submitted_at <= cut]: bad.append((k, "orders"))
    return {"trades": len(base.trades), "violations": bad}

# ---------------- Account invariants on long random run, no calendar, day gaps, costs, SL/TP ----------------
@probe("SYS-account_invariants_random_20k")
def _():
    rng = np.random.default_rng(42); n = 20000
    idx = pd.date_range("2024-01-01", periods=n * 2, freq="h", tz="UTC")
    idx = idx[rng.random(len(idx)) > 0.5][:n]  # random gaps incl. intraday -> warnings, not errors
    c = 100 + np.cumsum(rng.normal(0, 0.3, n)); c = np.round(c, 2); o = np.round(np.r_[c[0], c[:-1]] + rng.normal(0, .05, n), 2)
    d = pd.DataFrame({"open": o, "high": np.maximum(o, c) + 0.1, "low": np.minimum(o, c) - 0.1, "close": c}, index=idx)
    class Rnd(BaseStrategy):
        signal_history_limit = 1
        def __init__(self): super().__init__(); self.r = np.random.default_rng(3)
        def generate_signal(self, x):
            u = self.r.random(); cl = float(x.close.iloc[-1])
            if u < .05: return pd.Series({"signal": 1, "exit": False, "sl": cl - 1, "tp": cl + 1.5})
            if u < .10: return pd.Series({"signal": -1, "exit": False, "sl": cl + 1, "tp": cl - 1.5})
            if u < .13: return pd.Series({"signal": 0, "exit": True})
            return pd.Series({"signal": 0, "exit": False})
    e = eng(costs=CostModel(0.02, 0.01, 0.7), cap=1e6)
    r = e.run(d, Rnd()); viol = []
    sub = {o.order_id: o.submitted_at for o in r.orders}
    for f in r.fills:
        if f.reason in ("BUY", "SELL", "EXIT") and f.timestamp < sub[f.order_id]: viol.append("fill before submit")
    net = sum(t.net_pnl for t in r.trades)
    open_comm = r.open_position.entry.commission if r.open_position else 0.0
    last = r.states[-1]
    if not math.isclose(last.balance - 1e6, net - open_comm, abs_tol=1e-6): viol.append(("balance recon", last.balance - 1e6, net - open_comm))
    for s in r.states:
        if not math.isclose(s.equity, s.balance + s.unrealized_pnl, abs_tol=1e-9): viol.append("equity!=bal+unreal"); break
    for t in r.trades:
        if t.exit.timestamp < t.entry.timestamp: viol.append("exit<entry")
        if not math.isclose(t.net_pnl, t.gross_pnl - t.entry.commission - t.exit.commission, abs_tol=1e-9): viol.append("net mismatch")
    reasons = pd.Series([t.exit.reason for t in r.trades]).value_counts().to_dict()
    eq = np.array([s.equity for s in r.states]); dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    r2 = e.run(d, Rnd())
    return {"bars": n, "orders": len(r.orders), "fills": len(r.fills), "trades": len(r.trades), "exit_reasons": reasons,
            "ambiguous_exits": sum(f.ambiguous for f in r.fills), "violations": viol, "max_drawdown": dd,
            "warnings": r.assumptions["warnings"], "rerun_identical": r == r2,
            "rejections": pd.Series([e_["reason"] for e_ in r.events if e_["status"] == "rejected"]).value_counts().to_dict()}

@probe("SYS-close_labelled_fill_timing")
def _():
    b = bars4(); m = meta(kind="close")
    r = eng(m).run(b, Scripted({1: {"signal": 1}}), expected_timestamps=b.index)
    return {"order_submitted": str(r.orders[0].submitted_at), "fill_ts": str(r.fills[0].timestamp), "fill_price": r.fills[0].price,
            "state0_ts": str(r.states[0].timestamp)}

@probe("CORE-F6_state_timestamp_offset_open_label")
def _():
    b = bars4(); r = eng().run(b, Scripted({}), expected_timestamps=b.index)
    return {"data_index0": str(b.index[0]), "states0_ts": str(r.states[0].timestamp)}

@probe("SYS-result_equality_with_nan_assumption")
def _():
    # BacktestResult equality relies on dataclass/tuple/dict eq; check NaN-free under normal run
    b = bars4(); e = eng(); a = e.run(b, Scripted({1: {"signal": 1}})); c = e.run(b, Scripted({1: {"signal": 1}}))
    return {"equal": a == c}

# ---------------- DATA ----------------
@probe("DATA-1_off_grid")
def _():
    m = meta(timeframe="1min")
    idx = pd.DatetimeIndex(["2024-01-02 00:00:00", "2024-01-02 00:01:30", "2024-01-02 00:03:00"], tz="UTC")
    df = pd.DataFrame({"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.1}, index=idx)
    rep = validate_data(df, m)
    idx2 = pd.date_range("2024-01-02 00:00:30", periods=5, freq="min", tz="UTC")  # uniformly offset
    rep2 = validate_data(pd.DataFrame({"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.1}, index=idx2), m)
    try:
        eng(meta(timeframe="1min")).run(df, Scripted({})); engine_ran = True
    except Exception as e:
        engine_ran = f"raised {e}"
    return {"mixed_offgrid_ready": rep["ready_for_research"], "warnings": rep["warnings"],
            "uniform_offset_ready": rep2["ready_for_research"], "uniform_offset_warnings": rep2["warnings"],
            "engine_accepts_offgrid": engine_ran}

@probe("DATA-2_bad_token_nondiagnostic_and_engine_gate")
def _():
    m = meta(timeframe="1min"); m["timestamp_encoding"] = {"value": "unix_ms", "confirmed": True, "evidence": "probe"}
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, "x.csv")
    with open(p, "w") as f:
        f.write("timestamp,open,high,low,close\n1704153600000,1.1,1.2,1.0,abc\n1704153660000,1.1,1.2,1.0,1.1\n")
    lr = load_csv(p, m, diagnostic=False)
    try:
        eng(m).run(lr.data, Scripted({})); gate = "engine ran"
    except ValueError as e:
        gate = "engine blocked: " + str(e)[:120]
    return {"load_csv_returned": True, "close_nan_count": int(lr.data.close.isna().sum()), "engine": gate}

@probe("DATA-4_write_json_partial_file")
def _():
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, "r.json")
    try:
        write_json(p, {"a": 1, "b": float("nan")})
    except ValueError:
        pass
    return {"file_left_behind": os.path.exists(p), "size": os.path.getsize(p) if os.path.exists(p) else None}

@probe("DATA-5_timeframe_H1")
def _():
    try:
        return f"pd.Timedelta('H1') = {pd.Timedelta('H1')}"
    except Exception as e:
        return f"raises {type(e).__name__}: {e}"

@probe("DATA-6_fractional_epoch")
def _():
    m = meta(timeframe="1min"); m["timestamp_encoding"] = {"value": "unix_ms", "confirmed": True, "evidence": "probe"}
    tmp = tempfile.mkdtemp(); p = os.path.join(tmp, "x.csv")
    with open(p, "w") as f:
        f.write("timestamp,open,high,low,close\n1704153600000.5,1.1,1.2,1.0,1.1\n")
    lr = load_csv(p, m, diagnostic=False)
    return {"parsed": str(lr.data.index[0]), "invalid_count": lr.diagnostics["invalid_timestamps"]["count"]}

@probe("DATA-3_real_metadata_into_engine")
def _():
    import yaml
    root = r"C:\Users\Admin\Documents\quant_backtest_system\data\metadata"
    tpl = yaml.safe_load(open(os.path.join(root, "metadata_template.yaml"), encoding="utf-8"))
    reg = json.load(open(os.path.join(root, "datasets.json"), encoding="utf-8"))
    out = {}
    for d in reg["datasets"]:
        m = dict(tpl); m.update(d["metadata_overrides"])
        try:
            Instrument.from_metadata(m); out[d["symbol_hint"]] = "Instrument OK"
        except ValueError as e:
            out[d["symbol_hint"]] = f"blocked ({len(str(e).split(';'))} blockers): " + str(e)[:200]
    return out

# ---------------- INDICATORS ----------------
from indicators import sessions, volatility as vol, momentum as mom, moving_averages as ma, market_structure as ms

@probe("IND-1_session_membership_labels")
def _():
    idx = pd.DatetimeIndex(["2024-01-02 07:59", "2024-01-02 08:00", "2024-01-02 16:59", "2024-01-02 17:00"], tz="UTC")
    f = sessions.session_features(idx, timezone="UTC", start="08:00", end="17:00")
    return {"active": f.active.tolist(), "if_close_labels_expected": [False, False, True, True],
            "if_open_labels_expected": [False, True, True, False]}

@probe("IND-4_default_tolerance_masks_1tick_leak")
def _():
    idx = pd.date_range("2024-01-01", periods=10, freq="min", tz="UTC")
    df = pd.DataFrame({"close": np.full(10, 1.08)}, index=idx)
    leaky = lambda d: d["close"] + 1e-5 * (len(d) % 2)
    try:
        check_prefix_invariance(leaky, df); r1 = "PASSED (leak undetected)"
    except ValueError:
        r1 = "detected"
    try:
        check_prefix_invariance(lambda d: d["close"], df.iloc[:1]); r2 = "returned None (PASS) for 1-row input"
    except ValueError as e:
        r2 = f"raised {e}"
    try:
        check_prefix_invariance(lambda d: d["close"], df, cutoffs=[]); r3 = "returned None (PASS) for empty cutoffs"
    except ValueError as e:
        r3 = f"raised {e}"
    try:
        check_prefix_invariance(lambda d: d["close"], df.iloc[::-1]); r4 = "PASSED on reversed (non-chronological) index"
    except ValueError as e:
        r4 = f"raised {e}"
    g = float(np.linspace(1, 2, 10).mean()); df2 = pd.DataFrame({"close": np.linspace(1, 2, 10)}, index=idx)
    try:
        check_prefix_invariance(lambda d: d["close"] - g, df2); r5 = "PASSED with captured full-sample mean (expected limitation)"
    except ValueError:
        r5 = "detected"
    try:
        check_prefix_invariance(lambda d: d["close"], df, cutoffs=np.array([2, 5])); r6 = "np.int64 cutoffs accepted"
    except ValueError as e:
        r6 = f"np.int64 cutoffs rejected: {e}"
    return {"sub_tolerance_leak": r1, "len1": r2, "empty_cutoffs": r3, "reversed": r4, "captured_state": r5, "numpy_cutoffs": r6}

@probe("IND-5_flat_window_inexact_price")
def _():
    s = pd.Series([1.2345, 1.2350, 1.2341] + [1.0845] * 30, index=pd.date_range("2024-01-01", periods=33, freq="min", tz="UTC"))
    pb = vol.bollinger_percent_b(s, 20); bw = vol.bollinger_bandwidth(s, 20)
    d = pd.DataFrame({"open": s, "high": s, "low": s, "close": s})
    cc = mom.cci(d, 20)
    return {"percent_b_last": [None if np.isnan(x) else float(x) for x in pb.iloc[-3:]],
            "bandwidth_last": [None if np.isnan(x) else float(x) for x in bw.iloc[-3:]],
            "cci_last": [None if np.isnan(x) else float(x) for x in cc.iloc[-3:]],
            "rolling_std_last": float(vol.rolling_std(s, 20).iloc[-1])}

@probe("IND-6_monday_previous_day_from_sunday_fragment")
def _():
    fri = pd.date_range("2024-01-05 00:00", "2024-01-05 21:00", freq="h", tz="UTC")
    sun = pd.date_range("2024-01-07 22:00", "2024-01-07 23:00", freq="h", tz="UTC")
    mon = pd.date_range("2024-01-08 00:00", "2024-01-08 03:00", freq="h", tz="UTC")
    idx = fri.append(sun).append(mon); n = len(idx)
    c = np.r_[np.linspace(100, 110, len(fri)), [109.5, 109.6], np.full(len(mon), 109.7)]
    d = pd.DataFrame({"open": c, "high": c + .2, "low": c - .2, "close": c}, index=idx)
    p = ms.previous_period_levels(d, "day")
    return {"monday_prev_high": float(p.iloc[-1, 0]) if p.shape[1] else None, "cols": list(p.columns),
            "monday_row": p.iloc[-1].to_dict(), "friday_high": float(d.loc[fri, "high"].max())}

@probe("IND-7_param_validation")
def _():
    s = pd.Series(np.linspace(1, 2, 30), index=pd.date_range("2024-01-01", periods=30, freq="min", tz="UTC"))
    out = {}
    try: ma.sma(s, np.int64(3)); out["sma_np_int64"] = "accepted"
    except Exception as e: out["sma_np_int64"] = f"rejected: {type(e).__name__}"
    try: r = vol.bollinger_bands(s, 20, deviations=float("nan")); out["bollinger_dev_nan"] = f"accepted, all-NaN upper={bool(r.iloc[:, 0].isna().all())}"
    except Exception as e: out["bollinger_dev_nan"] = f"rejected: {type(e).__name__}"
    return out

json.dump(R, open(os.path.join(os.path.dirname(__file__), "probe_results.json"), "w"), indent=2, default=str)
