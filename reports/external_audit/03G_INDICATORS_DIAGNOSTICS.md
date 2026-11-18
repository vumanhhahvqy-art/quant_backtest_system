# 03G_INDICATORS_DIAGNOSTICS

Đọc cùng 03_INDICATORS_AUDIT.md và 05D_TESTS_INDICATORS.md.

## File gốc: `inspect_indicators.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\inspect_indicators.py`

Số dòng: 124; kích thước: 7359 bytes; SHA256: `c033894bee8c3be300fb31f3d574daa94f513d212a1fa3f98d8dfbd785536125`.

<!-- SOURCE_BEGIN inspect_indicators.py -->
```python
"""Run a diagnostic real-data smoke check without modifying market data."""

from __future__ import annotations

import inspect
import json
import platform
import time
import traceback
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from core.data_loader import load_parquet, sha256_file
from indicators import market_structure, momentum, moving_averages
from indicators import price_action, sessions, trend, volatility
from indicators._utils import ohlc


def main() -> None:
    """Inspect full input and exercise all canonical functions on three slices."""
    root = Path(__file__).resolve().parent
    source = root / "data/processed/inspection-20261116T161144Z-ef6d90f0/eurusd-m1-bid-2023-01-01-2026-11-15.diagnostic.parquet"
    metadata_path = source.with_name(source.name.replace(".parquet", ".metadata.json"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output = root / "reports/runs" / ("indicator-smoke-" + run_id)
    output.mkdir(parents=True, exist_ok=False)
    print(f"REPORT_DIRECTORY={output}", flush=True)
    report = {
        "run_id": run_id, "diagnostic_only": True,
        "python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__,
        "source": str(source), "source_sha256": sha256_file(source),
        "assumptions": [
            "Use diagnostic UTC interpretation from phase 2, not verified source metadata.",
            "Session checks assume recorded timestamps are availability times; unconfirmed.",
            "VWAP uses volume_kind=tick as a diagnostic hypothesis, not a verified volume unit.",
            "Annualization=252*1440 for numerical smoke testing only, not an inferred trading calendar.",
            "Three independent slices restart indicator warm-up and may begin within incomplete periods.",
            "No sorting, filling, deduplication, source modification or full-history indicator run.",
        ],
        "metadata_ready_for_research": metadata["ready_for_research"],
        "results": [],
    }
    data = load_parquet(source)
    ohlc(data)
    report["input"] = {
        "rows": len(data), "start": str(data.index[0]), "end": str(data.index[-1]),
        "missing": data.isna().sum().to_dict(),
        "infinite": int(np.isinf(data.to_numpy(dtype=float)).sum()),
        "nonpositive_ohlc": int((data[["open", "high", "low", "close"]] <= 0).sum().sum()),
        "negative_volume": int((data.volume < 0).sum()),
        "zero_volume": int(data.volume.eq(0).sum()),
        "zero_range": int(data.high.eq(data.low).sum()),
        "intervals_not_one_minute": int((data.index.to_series().diff().iloc[1:] != pd.Timedelta(minutes=1)).sum()),
        "structural_validation": "passed",
    }
    assert report["source_sha256"] == metadata["parquet_sha256"]
    size = 10080
    samples = {"start": data.iloc[:size], "middle": data.iloc[len(data)//2:len(data)//2+size], "end": data.iloc[-size:]}
    report["samples"] = {name: {"rows": len(part), "start": str(part.index[0]), "end": str(part.index[-1])} for name, part in samples.items()}
    modules = [moving_averages, trend, momentum, volatility, market_structure, price_action, sessions]
    for module in modules:
        functions = [(name, fn) for name, fn in inspect.getmembers(module, inspect.isfunction)
                     if fn.__module__ == module.__name__ and not name.startswith("_") and name != "smma"]
        for name, fn in functions:
            signature = inspect.signature(fn)
            parameters = list(signature.parameters)
            kwargs = {}
            if "periods_per_year" in parameters:
                kwargs["periods_per_year"] = 252 * 1440
            if "timezone" in parameters and signature.parameters["timezone"].default is inspect.Parameter.empty:
                kwargs.update(timezone="UTC", start="08:00", end="17:00")
            if "volume_kind" in parameters:
                kwargs["volume_kind"] = "tick"
            if name in {"sma", "ema", "wma", "rma"}:
                kwargs["window"] = 20
            for label, part in samples.items():
                started = time.perf_counter()
                entry = {"function": f"{module.__name__}.{name}", "sample": label, "parameters": str(signature), "overrides": kwargs}
                before = pd.util.hash_pandas_object(part, index=True)
                def calculate(frame: pd.DataFrame):
                    argument = frame.index if parameters[0] == "index" else frame["close"] if parameters[0] in {"series", "close"} else frame
                    return fn(argument, **kwargs)
                try:
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        result = calculate(part)
                        prefix = calculate(part.iloc[:512])
                    assert result.index.equals(part.index), "Output index changed"
                    compare = pd.testing.assert_frame_equal if isinstance(result, pd.DataFrame) else pd.testing.assert_series_equal
                    compare(result.iloc[:512], prefix)
                    pd.testing.assert_series_equal(before, pd.util.hash_pandas_object(part, index=True))
                    frame = result.to_frame(name="value") if isinstance(result, pd.Series) else result
                    numeric = frame.select_dtypes(include="number")
                    infinite = int(np.isinf(numeric.to_numpy(dtype=float, na_value=np.nan)).sum())
                    assert infinite == 0, f"Found {infinite} infinite values"
                    entry.update(status="passed", infinite=infinite,
                                 warnings=sorted(set(str(w.message) for w in caught)),
                                 columns={str(c): {"missing": int(frame[c].isna().sum()),
                                                  "valid": int(frame[c].notna().sum()),
                                                  "first_valid": str(frame[c].first_valid_index())} for c in frame})
                except Exception as error:
                    entry.update(status="failed", error=str(error), traceback=traceback.format_exc())
                entry["seconds"] = round(time.perf_counter() - started, 3)
                report["results"].append(entry)
                with (output / "results.json").open("w", encoding="utf-8") as stream:
                    json.dump(report, stream, ensure_ascii=False, indent=2)
            print(f"{module.__name__}.{name}: completed", flush=True)
    report["summary"] = {"checks": len(report["results"]),
                         "passed": sum(r["status"] == "passed" for r in report["results"]),
                         "failed": sum(r["status"] == "failed" for r in report["results"])}
    report["source_unchanged"] = sha256_file(source) == report["source_sha256"]
    with (output / "results.json").open("w", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(report["summary"]), flush=True)


if __name__ == "__main__":
    main()
```
<!-- SOURCE_END inspect_indicators.py -->
