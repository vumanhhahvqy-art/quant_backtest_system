# Chiến lược và ví dụ trực tiếp

BaseStrategy nằm nguyên văn tại 01_CORE_AUDIT.md, không lặp lại.
first_strategy.py chỉ import BaseStrategy, chưa có lớp chiến lược hoặc quy tắc vào/ra.
benchmark_engine.py có BatchMean/IncrementalMean dùng dữ liệu tổng hợp cho benchmark;
đây là ví dụ API, không là chiến lược đã kiểm định lợi thế. Script benchmark không chạy lại trong hồ sơ này.
Các lớp chiến lược fixture khác nằm trong test_engine.py và test_stage4_review.py, xem 05B.

## File gốc: `strategies/__init__.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\strategies\__init__.py`

Số dòng: 0; kích thước: 0 bytes; SHA256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

<!-- SOURCE_BEGIN strategies/__init__.py -->
```python
```
<!-- SOURCE_END strategies/__init__.py -->

## File gốc: `strategies/first_strategy.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\strategies\first_strategy.py`

Số dòng: 2; kích thước: 133 bytes; SHA256: `f1ebc4e02a4e55fc7f5db75e83a740b0980384b09784f7216a3b3518fc6d963c`.

<!-- SOURCE_BEGIN strategies/first_strategy.py -->
```python
"""Chiến lược thử nghiệm đầu tiên kế thừa từ BaseStrategy."""
from strategies.base_strategy import BaseStrategy
```
<!-- SOURCE_END strategies/first_strategy.py -->

## File gốc: `benchmark_engine.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\benchmark_engine.py`

Số dòng: 82; kích thước: 3683 bytes; SHA256: `cd05b5f735df19d816d32ad9e155bdd8331194ec52d73322d4844f5cc1b21e34`.

<!-- SOURCE_BEGIN benchmark_engine.py -->
```python
"""Reproducible synthetic benchmark; verify complete output equality before timing."""

import argparse
from collections import deque
import json
from platform import platform, python_version
from statistics import median
from time import perf_counter

import numpy as np
import pandas as pd

from core.cost_model import CostModel
from core.engine import BacktestEngine
from strategies.base_strategy import BaseStrategy


class BatchMean(BaseStrategy):
    def generate_signals(self, data):
        average = data.close.rolling(20).mean()
        return pd.DataFrame({"signal": (data.close > average).astype(int), "exit": False}, index=data.index)


class IncrementalMean(BaseStrategy):
    signal_history_limit = 1

    def __init__(self):
        super().__init__()
        self.values = deque(maxlen=20)

    def generate_signal(self, completed_data):
        close = float(completed_data.close.iloc[-1])
        self.values.append(close)
        signal = int(len(self.values) == 20 and close > sum(self.values) / 20)
        return pd.Series({"signal": signal, "exit": False})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[2000, 10000])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1 or any(size < 20 for size in args.sizes):
        parser.error("Require repeats >= 1 and sizes >= 20")
    values = {
        "source": "synthetic benchmark", "symbol": "TESTUSD", "source_timezone": "UTC",
        "timestamp_encoding": "aware", "timestamp_kind": "open", "price_type": "Mid",
        "timeframe": "1min", "instrument_specifications": {
            "tick_size": 0.01, "pip_size": 0.01, "contract_size": 1,
            "quantity_unit": "units", "quote_currency": "USD", "minimum_quantity_increment": 1,
        },
    }
    metadata = {key: {"value": value, "confirmed": True, "evidence": "Synthetic specification"}
                for key, value in values.items()}
    output = {"python": python_version(), "platform": platform(), "pandas": pd.__version__,
              "numpy": np.__version__, "repeats": args.repeats, "measurements": []}
    model = BacktestEngine(metadata, CostModel(0, 0, 0), initial_capital=10000,
                           account_currency="USD", quantity=1)
    for size in args.sizes:
        # Independent schedule from fixture definition, not derived from data.
        schedule = pd.date_range("2024-01-01", periods=size, freq="min", tz="UTC")
        close = 100 + np.sin(np.arange(size) * 0.17) + np.arange(size) * 0.0001
        data = pd.DataFrame({"open": close, "high": close+1, "low": close-1, "close": close}, index=schedule)
        results = []
        timings = {}
        for strategy_type in (BatchMean, IncrementalMean):
            elapsed = []
            for _ in range(args.repeats):
                started = perf_counter()
                result = model.run(data, strategy_type(), expected_timestamps=schedule)
                elapsed.append(perf_counter() - started)
            results.append(result)
            timings[strategy_type.__name__] = median(elapsed)
        assert results[0] == results[1], "Incremental execution changed simulation results"
        output["measurements"].append({"bars": size, "outputs_identical": True,
                                       "median_seconds": timings,
                                       "speedup": timings["BatchMean"] / timings["IncrementalMean"]})
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
```
<!-- SOURCE_END benchmark_engine.py -->
