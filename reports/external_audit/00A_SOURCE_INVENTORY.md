# Danh mục nguồn và API

Danh mục toàn bộ file thuộc phạm vi, không gồm hồ sơ kiểm toán tự sinh.

| File | Bytes | Dòng | Trạng thái | Gói chính |
|---|---|---|---|---|
| .clinerules/01-project.md | 4394 | 148 | document/config | 00B_PROJECT_RULES.md |
| .clinerules/02-architecture.md | 8448 | 379 | document/config | 00B_PROJECT_RULES.md |
| .clinerules/03-backtest-rules.md | 9474 | 378 | document/config | 00B_PROJECT_RULES.md |
| .clinerules/04-coding-standards.md | 8057 | 354 | document/config | 00B_PROJECT_RULES.md |
| .gitignore | 579 | 37 | document/config | 00_PROJECT_OVERVIEW.md |
| .vscode/settings.json | 68 | 3 | document/config | 00_PROJECT_OVERVIEW.md |
| README.md | 5310 | 116 | document/config | 00_PROJECT_OVERVIEW.md |
| benchmark_engine.py | 3683 | 82 | implementation | 04_STRATEGIES_AUDIT.md |
| configs/config.yaml | 624 | 14 | document/config | 02_DATA_AUDIT.md |
| configs/data_pipeline.yaml | 323 | 8 | document/config | 02_DATA_AUDIT.md |
| core/BACKTEST_ENGINE.md | 14292 | 207 | document/config | 01_CORE_AUDIT.md |
| core/__init__.py | 0 | 0 | empty | 01_CORE_AUDIT.md |
| core/causality.py | 1945 | 40 | implementation | 06_VALIDATION_AUDIT.md |
| core/cost_model.py | 2746 | 57 | implementation | 01_CORE_AUDIT.md |
| core/data_loader.py | 10823 | 239 | implementation | 02_DATA_AUDIT.md |
| core/data_manager.py | 112 | 1 | placeholder | 02_DATA_AUDIT.md |
| core/data_validator.py | 10363 | 199 | implementation | 02_DATA_AUDIT.md |
| core/engine.py | 12934 | 229 | implementation | 01_CORE_AUDIT.md |
| core/execution.py | 1401 | 37 | implementation | 01_CORE_AUDIT.md |
| core/metrics.py | 93 | 1 | placeholder | 06_VALIDATION_AUDIT.md |
| core/models.py | 5714 | 153 | implementation | 01_CORE_AUDIT.md |
| core/portfolio.py | 3954 | 70 | implementation | 01_CORE_AUDIT.md |
| data/metadata/datasets.json | 1718 | 31 | document/config | 02_DATA_AUDIT.md |
| data/metadata/metadata_template.yaml | 994 | 24 | document/config | 02_DATA_AUDIT.md |
| data/metadata/symbols.json | 893 | 32 | document/config | 02_DATA_AUDIT.md |
| indicators/INDICATORS.md | 15348 | 199 | document/config | 03_INDICATORS_AUDIT.md |
| indicators/__init__.py | 385 | 11 | implementation | 03_INDICATORS_AUDIT.md |
| indicators/_utils.py | 2419 | 56 | implementation | 03_INDICATORS_AUDIT.md |
| indicators/custom_indicators.py | 108 | 1 | placeholder | 03_INDICATORS_AUDIT.md |
| indicators/market_structure.py | 10174 | 189 | implementation | 03D_INDICATORS_STRUCTURE.md |
| indicators/momentum.py | 5488 | 128 | implementation | 03B_INDICATORS_MOMENTUM.md |
| indicators/moving_averages.py | 2280 | 65 | implementation | 03A_INDICATORS_TREND.md |
| indicators/price_action.py | 7330 | 142 | implementation | 03E_INDICATORS_PRICE_ACTION.md |
| indicators/sessions.py | 10890 | 210 | implementation | 03F_INDICATORS_SESSIONS_VOLUME.md |
| indicators/trend.py | 8659 | 167 | implementation | 03A_INDICATORS_TREND.md |
| indicators/volatility.py | 5186 | 106 | implementation | 03C_INDICATORS_VOLATILITY.md |
| inspect_data.py | 6421 | 122 | implementation | 02_DATA_AUDIT.md |
| inspect_indicators.py | 7359 | 124 | implementation | 03G_INDICATORS_DIAGNOSTICS.md |
| pyproject.toml | 726 | 29 | document/config | 00_PROJECT_OVERVIEW.md |
| run_backtest.py | 288 | 9 | implementation | 00_PROJECT_OVERVIEW.md |
| strategies/__init__.py | 0 | 0 | empty | 04_STRATEGIES_AUDIT.md |
| strategies/base_strategy.py | 1769 | 33 | implementation | 01_CORE_AUDIT.md |
| strategies/first_strategy.py | 133 | 2 | placeholder | 04_STRATEGIES_AUDIT.md |
| tests/test_backtest_models.py | 2891 | 78 | implementation | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md |
| tests/test_cost_model.py | 1330 | 33 | implementation | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md |
| tests/test_data_loader.py | 6705 | 154 | implementation | 05C_TESTS_DATA.md |
| tests/test_data_validator.py | 4612 | 102 | implementation | 05C_TESTS_DATA.md |
| tests/test_engine.py | 13110 | 273 | implementation | 05B_TESTS_ENGINE_REVIEW.md |
| tests/test_environment.py | 759 | 22 | implementation | 05E_TESTS_ENVIRONMENT.md |
| tests/test_execution.py | 1343 | 30 | implementation | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md |
| tests/test_indicators.py | 20622 | 384 | implementation | 05D_TESTS_INDICATORS.md |
| tests/test_intraday_gaps.py | 4582 | 90 | implementation | 05C_TESTS_DATA.md |
| tests/test_portfolio.py | 1985 | 46 | implementation | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md |
| tests/test_stage4_review.py | 3401 | 78 | implementation | 05B_TESTS_ENGINE_REVIEW.md |


## API, vai trò và import từng module Python

Docstring vai trò bên dưới là trích từ file gốc. Trạng thái implementation chỉ có nghĩa AST có thân thực thi; không là chứng nhận hoàn thiện.

### benchmark_engine.py

Reproducible synthetic benchmark; verify complete output equality before timing.

Trạng thái AST: implementation.

Hàm/class/method: BatchMean (dòng 18), BatchMean.generate_signals (dòng 19), IncrementalMean (dòng 24), IncrementalMean.__init__ (dòng 27), IncrementalMean.generate_signal (dòng 31), main (dòng 38).

Imports:

```python
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
```

### core/__init__.py

(Không có docstring module)

Trạng thái AST: empty.

Hàm/class/method: Không có.

Imports:

```python

```

### core/causality.py

Finite-sample prefix checks for indicator and feature builders.

Trạng thái AST: implementation.

Hàm/class/method: check_prefix_invariance (dòng 8).

Imports:

```python
from collections.abc import Callable, Iterable
import pandas as pd
```

### core/cost_model.py

Centralized fixed spread, adverse slippage and per-side commission.

Trạng thái AST: implementation.

Hàm/class/method: CostModel (dòng 10), CostModel.__post_init__ (dòng 22), CostModel.side_bar (dòng 29), CostModel.fill (dòng 40).

Imports:

```python
from dataclasses import dataclass
from math import ceil, floor, isfinite
from core.models import Fill, Instrument, positive
```

### core/data_loader.py

Explicit CSV parsing and lossless-row diagnostic normalization to UTC.

Invalid numeric tokens become NaN and invalid timestamps become NaT. Their
original row numbers and tokens are retained in the load diagnostics. No rows
are sorted, removed, or filled. Diagnostic output is not research-ready data.

Trạng thái AST: implementation.

Hàm/class/method: LoadResult (dòng 37), sha256_file (dòng 44), read_metadata (dòng 53), metadata_blockers (dòng 70), _issue_details (dòng 98), load_csv (dòng 108), write_json (dòng 195), save_parquet (dòng 204), load_parquet (dòng 231).

Imports:

```python
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import logging
import os
from pathlib import Path
import tempfile
from typing import Any
import numpy as np
import pandas as pd
import yaml
```

### core/data_manager.py

Module đọc dữ liệu thô, kiểm tra nến lỗi/múi giờ và xuất file .parquet chuẩn hóa.

Trạng thái AST: placeholder.

Hàm/class/method: Không có.

Imports:

```python

```

### core/data_validator.py

Non-mutating OHLC checks, intraday gap warnings and optional full calendar.

Trạng thái AST: implementation.

Hàm/class/method: validate_expected_timestamps (dòng 13), validate_data (dòng 45), save_report (dòng 197).

Imports:

```python
from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd
from core.data_loader import PRICE_COLUMNS, metadata_blockers, write_json
```

### core/engine.py

Chronological single-instrument backtest with prefix-only strategy input.

Trạng thái AST: implementation.

Hàm/class/method: BacktestResult (dòng 24), ConversionRates (dòng 36), ConversionRates.__init__ (dòng 43), ConversionRates.at (dòng 59), BacktestEngine (dòng 68), BacktestEngine.__init__ (dòng 71), BacktestEngine.run (dòng 84).

Imports:

```python
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
import logging
from typing import Any
import numpy as np
import pandas as pd
from core.cost_model import CostModel
from core.data_validator import validate_data
from core.execution import protective_exit
from core.models import AccountState, Fill, Instrument, Order, Position, Trade, positive
from core.portfolio import Portfolio
from strategies.base_strategy import BaseStrategy
```

### core/execution.py

OHLC market and protective execution; prices are executable-side prices.

Trạng thái AST: implementation.

Hàm/class/method: ExitDecision (dòng 11), protective_exit (dòng 18).

Imports:

```python
from __future__ import annotations
from dataclasses import dataclass
from core.models import Position
```

### core/metrics.py

Module tính toán hiệu suất: Winrate, Profit Factor, Sharpe Ratio, Max Drawdown.

Trạng thái AST: placeholder.

Hàm/class/method: Không có.

Imports:

```python

```

### core/models.py

Explicit records and units for deterministic, single-instrument simulation.

Trạng thái AST: implementation.

Hàm/class/method: positive (dòng 14), Instrument (dòng 21), Instrument.__post_init__ (dòng 30), Instrument.from_metadata (dòng 41), Instrument.units (dòng 51), Order (dòng 61), Order.__post_init__ (dòng 70), Fill (dòng 84), Fill.__post_init__ (dòng 97), Position (dòng 117), Position.__post_init__ (dòng 125), Trade (dòng 138), AccountState (dòng 146).

Imports:

```python
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, isclose
from typing import Any
import pandas as pd
from core.data_loader import metadata_blockers
```

### core/portfolio.py

Single-position full-notional collateral accounting, without leverage.

Trạng thái AST: implementation.

Hàm/class/method: Portfolio (dòng 6), Portfolio.__init__ (dòng 9), Portfolio.open (dòng 17), Portfolio.close (dòng 39), Portfolio.mark (dòng 58).

Imports:

```python
from core.models import AccountState, Fill, Instrument, Order, Position, Trade, positive
```

### indicators/__init__.py

Reusable causal indicators; import functions from their thematic modules.

See INDICATORS.md for formulas, initialization, warm-up and time semantics.

Trạng thái AST: implementation.

Hàm/class/method: Không có.

Imports:

```python
from . import market_structure, momentum, moving_averages, price_action, sessions, trend, volatility
```

### indicators/_utils.py

Small validation and alignment helpers shared by indicator modules.

Trạng thái AST: implementation.

Hàm/class/method: require_columns (dòng 9), positive_window (dòng 15), ohlc (dòng 21), validate_index (dòng 35), validate_series (dòng 42), true_range (dòng 50).

Imports:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
```

### indicators/custom_indicators.py

Nơi định nghĩa các chỉ báo tự thiết kế, Price Action và cấu trúc thị trường.

Trạng thái AST: placeholder.

Hàm/class/method: Không có.

Imports:

```python

```

### indicators/market_structure.py

Causal market structure heuristics, published on confirmation bars.

BOS/CHoCH/MSS and zones have no unique industry definition. The definitions
below are explicit research features, not order instructions.

Trạng thái AST: implementation.

Hàm/class/method: confirmed_swings (dòng 13), swing_structure (dòng 31), structure_breaks (dòng 46), support_resistance_zones (dòng 85), previous_period_levels (dòng 96), daily_pivots (dòng 115), fibonacci_retracement (dòng 143), equal_high_low (dòng 159), liquidity_sweep (dòng 172), fair_value_gap (dòng 180).

Imports:

```python
import numpy as np
import pandas as pd
from ._utils import ohlc, positive_window
from .sessions import _utc_index
```

### indicators/momentum.py

Causal momentum and oscillator indicators.

Trạng thái AST: implementation.

Hàm/class/method: rsi (dòng 12), macd (dòng 27), stochastic (dòng 40), stochastic_rsi (dòng 52), roc (dòng 67), momentum (dòng 74), cci (dòng 81), williams_r (dòng 94), ppo (dòng 103), tsi (dòng 113), awesome_oscillator (dòng 122).

Imports:

```python
from __future__ import annotations
import pandas as pd
import numpy as np
from ._utils import ohlc, positive_window, validate_series
from .moving_averages import ema, rma, sma
```

### indicators/moving_averages.py

Moving averages. Warm-up observations are NaN and no input is mutated.

Trạng thái AST: implementation.

Hàm/class/method: sma (dòng 11), ema (dòng 18), wma (dòng 34), rma (dòng 44).

Imports:

```python
from __future__ import annotations
import pandas as pd
import numpy as np
from ._utils import positive_window, validate_series
```

### indicators/price_action.py

Candle geometry and explicitly parameterized pattern heuristics.

Patterns describe completed bars, not a forecast. Zero-range ratios are NaN.
Boolean patterns use pandas nullable booleans: unavailable inputs produce NA.

Trạng thái AST: implementation.

Hàm/class/method: candle_features (dòng 13), _pattern (dòng 23), inside_bar (dòng 29), outside_bar (dòng 35), engulfing (dòng 41), pin_bar (dòng 49), doji (dòng 57), hammer_shooting_star (dòng 65), morning_evening_star (dòng 74), marubozu (dòng 90), heikin_ashi (dòng 99), narrow_range (dòng 112), consecutive_candles (dòng 120), range_expansion (dòng 135).

Imports:

```python
import numpy as np
import pandas as pd
from ._utils import ohlc, positive_window
```

### indicators/sessions.py

Explicit local-time sessions and causal market-regime features.

Session inputs are timestamps of completed candles (availability time).
Intervals are [open, close). Session definitions are research parameters,
not assertions about a broker's calendar. DST follows the IANA timezone.

Trạng thái AST: implementation.

Hàm/class/method: _utc_index (dòng 18), session_features (dòng 25), session_range (dòng 51), asia_session_range (dòng 64), london_session_range (dòng 69), new_york_session_range (dòng 74), london_new_york_overlap (dòng 79), opening_range_breakout (dòng 86), session_vwap (dòng 104), calendar_features (dòng 126), weekend_gap (dòng 133), trend_range_regime (dòng 151), volatility_regime (dòng 159), dominant_cycle (dòng 172).

Imports:

```python
from datetime import time
import numpy as np
import pandas as pd
from ._utils import ohlc, positive_window, validate_series
from .trend import adx
from .volatility import natr
```

### indicators/trend.py

Trend indicators evaluated only after the current candle is complete.

Trạng thái AST: implementation.

Hàm/class/method: adx (dòng 11), supertrend (dòng 27), aroon (dòng 52), parabolic_sar (dòng 61), ichimoku (dòng 101), vortex (dòng 119), choppiness (dòng 127), vhf (dòng 137), linear_regression_slope (dòng 145), linear_regression_channel (dòng 155).

Imports:

```python
import numpy as np
import pandas as pd
from ._utils import ohlc, positive_window, true_range, validate_series
from .moving_averages import rma
from .volatility import atr
```

### indicators/volatility.py

Trailing volatility estimates; annualization is supplied by the caller.

Trạng thái AST: implementation.

Hàm/class/method: atr (dòng 10), natr (dòng 15), rolling_std (dòng 20), bollinger_bands (dòng 29), bollinger_bandwidth (dòng 38), bollinger_percent_b (dòng 44), keltner_channels (dòng 50), donchian_channels (dòng 59), _annualization (dòng 70), _log_returns (dòng 76), historical_volatility (dòng 82), realized_volatility (dòng 87), parkinson_volatility (dòng 92), garman_klass_volatility (dòng 100).

Imports:

```python
import numpy as np
import pandas as pd
from ._utils import ohlc, positive_window, true_range, validate_series
from .moving_averages import ema, rma, sma
```

### inspect_data.py

Inspect all raw CSVs and export selected full diagnostic Parquet datasets.

Trạng thái AST: implementation.

Hàm/class/method: merge_metadata (dòng 27), main (dòng 38).

Imports:

```python
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import platform
import subprocess
from uuid import uuid4
import pandas as pd
import pyarrow
import yaml
from core.data_loader import load_csv, load_parquet, read_metadata, save_parquet, sha256_file, write_json
from core.data_validator import validate_data
```

### inspect_indicators.py

Run a diagnostic real-data smoke check without modifying market data.

Trạng thái AST: implementation.

Hàm/class/method: main (dòng 24).

Imports:

```python
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
```

### run_backtest.py

Điểm khởi chạy chính của hệ thống Quant Backtest.

Trạng thái AST: implementation.

Hàm/class/method: main (dòng 4).

Imports:

```python
from pathlib import Path
```

### strategies/__init__.py

(Không có docstring module)

Trạng thái AST: empty.

Hàm/class/method: Không có.

Imports:

```python

```

### strategies/base_strategy.py

Khung chuẩn (Base Class) cho mọi chiến lược giao dịch trong hệ thống.

Trạng thái AST: implementation.

Hàm/class/method: BaseStrategy (dòng 4), BaseStrategy.__init__ (dòng 9), BaseStrategy.generate_signals (dòng 12), BaseStrategy.generate_signal (dòng 21).

Imports:

```python
import pandas as pd
```

| Dòng | Marker cần đọc ngữ cảnh |
|---|---|
| 19 | raise NotImplementedError("Chiến lược con bắt buộc phải định nghĩa hàm generate_signals()") |


### strategies/first_strategy.py

Chiến lược thử nghiệm đầu tiên kế thừa từ BaseStrategy.

Trạng thái AST: placeholder.

Hàm/class/method: Không có.

Imports:

```python
from strategies.base_strategy import BaseStrategy
```

### tests/test_backtest_models.py

Instrument metadata and order validation using explicit synthetic units.

Trạng thái AST: implementation.

Hàm/class/method: simulation_metadata (dòng 12), instrument (dòng 28), test_instrument_conversion_and_metadata (dòng 32), test_unsupported_or_invalid_orders (dòng 47), test_fill_rejects_invalid_financial_fields (dòng 60), test_position_rejects_invalid_state (dòng 72).

Imports:

```python
from copy import deepcopy
import pandas as pd
import pytest
from core.models import Fill, Instrument, Order, Position
from dataclasses import replace
from dataclasses import replace
```

### tests/test_cost_model.py

Costs and executable sides, with hand-computed account-currency amounts.

Trạng thái AST: implementation.

Hàm/class/method: test_bid_ask_conventions (dòng 14), test_fill_costs_and_adverse_tick_rounding (dòng 19), test_reject_invalid_costs_and_swap (dòng 31).

Imports:

```python
import pandas as pd
import pytest
from core.cost_model import CostModel
from test_backtest_models import instrument, simulation_metadata
```

### tests/test_data_loader.py

Synthetic parsing, preservation and explicit timestamp interpretation tests.

Trạng thái AST: implementation.

Hàm/class/method: metadata (dòng 15), make_csv (dòng 31), test_round_trip_preserves_rows_and_raw (dòng 37), test_parquet_failure_leaves_no_partial_or_temporary_file (dòng 54), test_parquet_publication_failure_cleans_temp_and_preserves_existing (dòng 68), test_invalid_tokens_are_reported_not_removed (dòng 88), test_unconfirmed_encoding_requires_diagnostic_mode (dòng 101), test_missing_columns_and_mapping (dòng 112), test_explicit_local_timezone_and_dst (dòng 121), test_aware_strings_do_not_accept_naive_values (dòng 134), test_metadata_and_json_no_overwrite (dòng 143).

Imports:

```python
import copy
from pathlib import Path
import pandas as pd
import pytest
from core.data_loader import load_csv, load_parquet, read_metadata, save_parquet, sha256_file, write_json
import core.data_loader as loader
```

### tests/test_data_validator.py

Manually verifiable quality checks, calendar handling and reproducibility.

Trạng thái AST: implementation.

Hàm/class/method: candles (dòng 15), test_clean_data_ready_without_calendar_but_not_calendar_verified (dòng 22), test_bad_numeric_values (dòng 45), test_duplicates_unsorted_and_nat (dòng 53), test_gap_candidates_do_not_imply_market_missing (dòng 62), test_closed_session_gap_is_accepted_with_explicit_calendar (dòng 73), test_unknown_metadata_blocks_readiness (dòng 80), test_empty_missing_columns_and_non_utc (dòng 89), test_report_export_is_reproducible_and_no_overwrite (dòng 96).

Imports:

```python
import copy
import json
import numpy as np
import pandas as pd
import pytest
from core.data_validator import save_report, validate_data
from test_data_loader import metadata
```

### tests/test_engine.py

Integration: signal -> timing -> executable prices -> costs -> account.

Trạng thái AST: implementation.

Hàm/class/method: ScriptedStrategy (dòng 12), ScriptedStrategy.__init__ (dòng 15), ScriptedStrategy.generate_signals (dòng 20), bars (dòng 30), engine (dòng 38), run (dòng 43), test_fee_trade_hand_calculation_and_timing (dòng 47), test_zero_holds_and_last_order_is_unfilled (dòng 69), test_rejections_are_logged_without_charging_costs (dòng 79), test_schedule_with_shifted_boundaries_is_rejected (dòng 90), test_same_bar_brackets_sl_first (dòng 99), test_same_executable_prices_without_double_spread (dòng 108), test_close_labeled_bars_and_weekend_next_available_open (dòng 118), test_currency_rates_never_use_future (dòng 131), test_future_candles_do_not_change_earlier_outputs (dòng 143), test_invalid_data_blocks_simulation (dòng 158), test_existing_position_and_bad_gap_bracket_rejected (dòng 174), test_stop_uses_bid_for_long_and_costs_once (dòng 184), test_short_stop_uses_ask (dòng 194), test_gap_stop_fills_open_and_tp_does_not_use_better_gap_price (dòng 202), test_future_conversion_during_bar_not_used_for_stop (dòng 215), test_prefix_isolation_and_strategy_output_validation (dòng 223), test_incremental_strategy_api_matches_batch_output (dòng 243), test_insolvency_is_reported_for_extreme_short_gap (dòng 262), test_invalid_conversion_rates (dòng 271).

Imports:

```python
import pandas as pd
import pytest
from core.cost_model import CostModel
from core.engine import BacktestEngine, ConversionRates
from strategies.base_strategy import BaseStrategy
from test_backtest_models import instrument, simulation_metadata
```

### tests/test_environment.py

Smoke test for the isolated Python research environment.

Trạng thái AST: implementation.

Hàm/class/method: test_research_environment (dòng 11).

Imports:

```python
import sys
import numpy as np
import pandas as pd
import pytest
import yaml
```

### tests/test_execution.py

Long and short OHLC stops, targets, gaps and ambiguity.

Trạng thái AST: implementation.

Hàm/class/method: test_protective_execution (dòng 22).

Imports:

```python
from dataclasses import replace
import pandas as pd
import pytest
from core.execution import protective_exit
from core.models import Fill, Position
```

### tests/test_indicators.py

Independent arithmetic fixtures plus alignment and causal-prefix contracts.

Trạng thái AST: implementation.

Hàm/class/method: bars (dòng 16), data (dòng 24), test_moving_averages_and_nan_restart (dòng 28), test_momentum_arithmetic (dòng 42), test_volatility_arithmetic (dòng 68), test_trend_arithmetic (dòng 92), test_candle_geometry_and_patterns (dòng 122), test_structure_confirmations_and_breaks (dòng 153), test_previous_period_pivots (dòng 186), test_sessions_vwap_orb_calendar_and_gap (dòng 198), test_regimes_and_cycle (dòng 231), test_all_indicators_preserve_index_causality_and_inputs (dòng 268), test_invalid_windows (dòng 282), test_invalid_inputs (dòng 287), test_empty_and_missing_inputs (dòng 307), test_nan_and_zero_denominators (dòng 319), test_bearish_patterns_and_lower_structures (dòng 337), test_ema_against_documented_pandas_reference (dòng 354), test_input_order_and_numeric_validation (dòng 361), test_cycle_phase_independent_direct_hilbert_sum (dòng 375).

Imports:

```python
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
```

### tests/test_intraday_gaps.py

Simple UTC-day gap policy and next-observed-candle execution regression.

Trạng thái AST: implementation.

Hàm/class/method: make_candles (dòng 12), test_simple_gap_report_and_actual_next_open (dòng 25), test_explicit_calendar_remains_strict_and_independent (dòng 54), test_mandatory_validation_still_blocks_without_calendar (dòng 66), test_nonmultiple_gap_counts_grid_points_and_no_cross_day_warning (dòng 81).

Imports:

```python
import numpy as np
import pandas as pd
import pytest
from core.data_validator import validate_data
from test_backtest_models import simulation_metadata
from test_engine import ScriptedStrategy, engine
```

### tests/test_portfolio.py

Known long/short P/L, conversion, capital reservation and fee accounting.

Trạng thái AST: implementation.

Hàm/class/method: test_accounting_with_currency_conversion (dòng 14), test_insufficient_capital_and_invalid_stops_do_not_mutate (dòng 34).

Imports:

```python
from dataclasses import replace
import pandas as pd
import pytest
from core.models import Fill, Order
from core.portfolio import Portfolio
from test_backtest_models import instrument, simulation_metadata
```

### tests/test_stage4_review.py

Regression checks for review findings and incremental equivalence.

Trạng thái AST: implementation.

Hàm/class/method: test_causal_indicator_and_future_leaking_features (dòng 18), test_independent_schedule_detects_missing_first_middle_last (dòng 29), test_schedule_rejects_overlapping_candles (dòng 38), test_portfolio_rejects_mismatched_ids_and_time_without_mutation (dòng 45), BatchThreshold (dòng 60), BatchThreshold.generate_signals (dòng 61), IncrementalThreshold (dòng 65), IncrementalThreshold.generate_signal (dòng 68), test_incremental_and_legacy_results_are_identical (dòng 73).

Imports:

```python
from dataclasses import replace
import pandas as pd
import pytest
from core.causality import check_prefix_invariance
from core.data_validator import validate_data, validate_expected_timestamps
from core.models import Fill, Order
from core.portfolio import Portfolio
from indicators.moving_averages import sma
from strategies.base_strategy import BaseStrategy
from test_backtest_models import instrument, simulation_metadata
from test_engine import bars, engine
```
