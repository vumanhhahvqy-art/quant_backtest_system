# Ánh xạ module và kiểm thử

Ánh xạ được suy ra từ AST import: trực tiếp và bắc cầu. Đây là liên hệ tĩnh,
không phải coverage theo dòng/nhánh và không chứng minh tất cả hàm đã được kiểm tra.
Dynamic import, getattr và khả năng gọi thực tế cần đọc test; coverage chưa đo được.
Các entry point run_backtest.py, inspect_data.py, inspect_indicators.py và benchmark_engine.py không có test import trực tiếp.
Các module placeholder chưa có kiểm thử hành vi vì chưa triển khai; không suy ra chúng hoàn thiện từ test toàn bộ pass.

| Module | Test import trực tiếp | Liên hệ import bắc cầu |
|---|---|---|
| benchmark_engine.py | Không có import trực tiếp | Không có |
| inspect_data.py | Không có import trực tiếp | Không có |
| inspect_indicators.py | Không có import trực tiếp | Không có |
| run_backtest.py | Không có import trực tiếp | Không có |
| core/__init__.py | Không có import trực tiếp | Không có |
| core/causality.py | tests/test_stage4_review.py | Không có |
| core/cost_model.py | tests/test_cost_model.py, tests/test_engine.py | tests/test_intraday_gaps.py, tests/test_stage4_review.py |
| core/data_loader.py | tests/test_data_loader.py | tests/test_backtest_models.py, tests/test_cost_model.py, tests/test_data_validator.py, tests/test_engine.py, tests/test_execution.py, tests/test_intraday_gaps.py, tests/test_portfolio.py, tests/test_stage4_review.py |
| core/data_manager.py | Không có import trực tiếp | Không có |
| core/data_validator.py | tests/test_data_validator.py, tests/test_intraday_gaps.py, tests/test_stage4_review.py | tests/test_engine.py |
| core/engine.py | tests/test_engine.py | tests/test_intraday_gaps.py, tests/test_stage4_review.py |
| core/execution.py | tests/test_execution.py | tests/test_engine.py, tests/test_intraday_gaps.py, tests/test_stage4_review.py |
| core/metrics.py | Không có import trực tiếp | Không có |
| core/models.py | tests/test_backtest_models.py, tests/test_execution.py, tests/test_portfolio.py, tests/test_stage4_review.py | tests/test_cost_model.py, tests/test_engine.py, tests/test_intraday_gaps.py |
| core/portfolio.py | tests/test_portfolio.py, tests/test_stage4_review.py | tests/test_engine.py, tests/test_intraday_gaps.py |
| indicators/__init__.py | tests/test_indicators.py | Không có |
| indicators/_utils.py | Không có import trực tiếp | tests/test_indicators.py, tests/test_stage4_review.py |
| indicators/custom_indicators.py | Không có import trực tiếp | Không có |
| indicators/market_structure.py | tests/test_indicators.py | Không có |
| indicators/momentum.py | tests/test_indicators.py | Không có |
| indicators/moving_averages.py | tests/test_indicators.py, tests/test_stage4_review.py | Không có |
| indicators/price_action.py | tests/test_indicators.py | Không có |
| indicators/sessions.py | tests/test_indicators.py | Không có |
| indicators/trend.py | tests/test_indicators.py | Không có |
| indicators/volatility.py | tests/test_indicators.py | Không có |
| strategies/__init__.py | Không có import trực tiếp | Không có |
| strategies/base_strategy.py | tests/test_engine.py, tests/test_stage4_review.py | tests/test_intraday_gaps.py |
| strategies/first_strategy.py | Không có import trực tiếp | Không có |

## Kiểm thử integrity cần đọc

- Timing, PnL tính tay, deterministic replay, prefix isolation, quy đổi FX, insolvency: test_engine.py (05B).
- Bid/Ask, tick rounding, commission, swap bị từ chối: test_cost_model.py (05A).
- SL/TP cùng nến và gap: test_execution.py (05A), test_engine.py (05B).
- Timestamp trùng/sai thứ tự, invalid OHLC, raw preservation trên fixture, lỗi ghi Parquet: 05C.
- Gap chỉ cảnh báo trong cùng ngày UTC và nến có dữ liệu kế tiếp: test_intraday_gaps.py (05C).
- Indicator alignment, prefix invariance, công thức tính tay, previous-period pivots, DST: 05D.
- Prefix leakage shift(-1)/centered rolling/full-sample normalization và incremental equivalence: test_stage4_review.py (05B).
- Chưa có pipeline đa khung thời gian hoàn chỉnh; test previous-period feature không thay thế kiểm thử toàn hệ thống MTF.

## Kết quả theo file từ JUnit lần chạy mới

| Test module | Passed | Failed/errors | Skipped |
|---|---|---|---|
| tests.test_backtest_models | 19 | 0 | 0 |
| tests.test_cost_model | 11 | 0 | 0 |
| tests.test_data_loader | 9 | 0 | 0 |
| tests.test_data_validator | 14 | 0 | 0 |
| tests.test_engine | 29 | 0 | 0 |
| tests.test_environment | 1 | 0 | 0 |
| tests.test_execution | 8 | 0 | 0 |
| tests.test_indicators | 184 | 0 | 0 |
| tests.test_intraday_gaps | 13 | 0 | 0 |
| tests.test_portfolio | 3 | 0 | 0 |
| tests.test_stage4_review | 5 | 0 | 0 |

