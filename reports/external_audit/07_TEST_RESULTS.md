# Kết quả kỹ thuật thực thi thực tế

Thu thập UTC: 2026-11-17T09:33:31.742505+00:00. Commit nền: `7af3b774b1721e091e2527a00563912255d44702`; working tree có thay đổi sẵn.
Interpreter: `C:\Users\Admin\Documents\quant_backtest_system\.venv\Scripts\python.exe`. Python: `3.15.2 (tags/v3.15.2:5e58eaa, Oct 25 2026, 17:27:03) [MSC v.1951 64 bit (AMD64)]`.

Pytest: **296 passed / 0 failed / 0 errors / 0 skipped**.
Không có test thất bại nên không có traceback thất bại để ghi; bật --tb=long trong lệnh thực tế.
JUnit XML đầy đủ có tại pytest_results.xml và được nhúng dưới đây để gói tự chứa.
Compile: 39 file thành công, 0 lỗi.
Biên dịch dùng compile(bytes, absolute_path, 'exec') trong bộ nhớ, không viết pyc và không chạy top-level của script.
Không phải kiểm tra type hay chứng minh import/runtime mọi entry point.

Coverage: CHƯA THỰC HIỆN, coverage và pytest-cov không cài.
Static analysis: CHƯA THỰC HIỆN với các analyzer không có sẵn trong bảng dưới.
Không cài dependency, không fetch web, không chạy pipeline dữ liệu thật hoặc benchmark.
git diff --check chỉ kiểm tra diff tracked, không bao phủ nội dung file untracked; mã untracked vẫn được compile và đóng gói.
Git có cảnh báo LF sẽ đổi sang CRLF ở indicators/__init__.py; return code diff check vẫn bằng 0.
pip check chỉ xác minh quan hệ dependency đang cài, không là security audit.

## Khả dụng công cụ

| Tool | Module có sẵn | Executable trong PATH |
|---|---|---|
| coverage | False | Không |
| pytest_cov | False | Không |
| ruff | False | Không |
| mypy | False | Không |
| pylint | False | Không |
| flake8 | False | Không |
| bandit | False | Không |
| pyright | False | Không |


## pytest

Lệnh: `C:\Users\Admin\Documents\quant_backtest_system\.venv\Scripts\python.exe -B -m pytest -vv --tb=long -p no:cacheprovider --color=no --junitxml=C:\Users\Admin\Documents\quant_backtest_system\reports\external_audit\pytest_results.xml`

Exit code: 0; thời gian wall-clock: 4.327 giây.

stdout:

```text
============================= test session starts =============================
platform win32 -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\Admin\Documents\quant_backtest_system\.venv\Scripts\python.exe
rootdir: C:\Users\Admin\Documents\quant_backtest_system
configfile: pyproject.toml
testpaths: tests
collecting ... collected 296 items

tests/test_backtest_models.py::test_instrument_conversion_and_metadata PASSED [  0%]
tests/test_backtest_models.py::test_unsupported_or_invalid_orders[kwargs0] PASSED [  0%]
tests/test_backtest_models.py::test_unsupported_or_invalid_orders[kwargs1] PASSED [  1%]
tests/test_backtest_models.py::test_unsupported_or_invalid_orders[kwargs2] PASSED [  1%]
tests/test_backtest_models.py::test_unsupported_or_invalid_orders[kwargs3] PASSED [  1%]
tests/test_backtest_models.py::test_unsupported_or_invalid_orders[kwargs4] PASSED [  2%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes0] PASSED [  2%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes1] PASSED [  2%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes2] PASSED [  3%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes3] PASSED [  3%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes4] PASSED [  3%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes5] PASSED [  4%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes6] PASSED [  4%]
tests/test_backtest_models.py::test_fill_rejects_invalid_financial_fields[changes7] PASSED [  4%]
tests/test_backtest_models.py::test_position_rejects_invalid_state[changes0] PASSED [  5%]
tests/test_backtest_models.py::test_position_rejects_invalid_state[changes1] PASSED [  5%]
tests/test_backtest_models.py::test_position_rejects_invalid_state[changes2] PASSED [  5%]
tests/test_backtest_models.py::test_position_rejects_invalid_state[changes3] PASSED [  6%]
tests/test_backtest_models.py::test_position_rejects_invalid_state[changes4] PASSED [  6%]
tests/test_cost_model.py::test_bid_ask_conventions[Mid-1-101] PASSED     [  6%]
tests/test_cost_model.py::test_bid_ask_conventions[Mid--1-99] PASSED     [  7%]
tests/test_cost_model.py::test_bid_ask_conventions[Bid-1-102] PASSED     [  7%]
tests/test_cost_model.py::test_bid_ask_conventions[Bid--1-100] PASSED    [  7%]
tests/test_cost_model.py::test_bid_ask_conventions[Ask-1-100] PASSED     [  8%]
tests/test_cost_model.py::test_bid_ask_conventions[Ask--1-98] PASSED     [  8%]
tests/test_cost_model.py::test_fill_costs_and_adverse_tick_rounding PASSED [  8%]
tests/test_cost_model.py::test_reject_invalid_costs_and_swap[args0] PASSED [  9%]
tests/test_cost_model.py::test_reject_invalid_costs_and_swap[args1] PASSED [  9%]
tests/test_cost_model.py::test_reject_invalid_costs_and_swap[args2] PASSED [  9%]
tests/test_cost_model.py::test_reject_invalid_costs_and_swap[args3] PASSED [ 10%]
tests/test_data_loader.py::test_round_trip_preserves_rows_and_raw PASSED [ 10%]
tests/test_data_loader.py::test_parquet_failure_leaves_no_partial_or_temporary_file PASSED [ 10%]
tests/test_data_loader.py::test_parquet_publication_failure_cleans_temp_and_preserves_existing PASSED [ 11%]
tests/test_data_loader.py::test_invalid_tokens_are_reported_not_removed PASSED [ 11%]
tests/test_data_loader.py::test_unconfirmed_encoding_requires_diagnostic_mode PASSED [ 11%]
tests/test_data_loader.py::test_missing_columns_and_mapping PASSED       [ 12%]
tests/test_data_loader.py::test_explicit_local_timezone_and_dst PASSED   [ 12%]
tests/test_data_loader.py::test_aware_strings_do_not_accept_naive_values PASSED [ 12%]
tests/test_data_loader.py::test_metadata_and_json_no_overwrite PASSED    [ 13%]
tests/test_data_validator.py::test_clean_data_ready_without_calendar_but_not_calendar_verified PASSED [ 13%]
tests/test_data_validator.py::test_bad_numeric_values[open-nan-open_missing_or_non_numeric] PASSED [ 13%]
tests/test_data_validator.py::test_bad_numeric_values[close-inf-close_infinite] PASSED [ 14%]
tests/test_data_validator.py::test_bad_numeric_values[low-0-low_invalid_sign] PASSED [ 14%]
tests/test_data_validator.py::test_bad_numeric_values[open--1-open_invalid_sign] PASSED [ 14%]
tests/test_data_validator.py::test_bad_numeric_values[volume--1-volume_invalid_sign] PASSED [ 15%]
tests/test_data_validator.py::test_bad_numeric_values[high-0.75-invalid_ohlc] PASSED [ 15%]
tests/test_data_validator.py::test_bad_numeric_values[low-1.75-invalid_ohlc] PASSED [ 15%]
tests/test_data_validator.py::test_duplicates_unsorted_and_nat PASSED    [ 16%]
tests/test_data_validator.py::test_gap_candidates_do_not_imply_market_missing PASSED [ 16%]
tests/test_data_validator.py::test_closed_session_gap_is_accepted_with_explicit_calendar PASSED [ 16%]
tests/test_data_validator.py::test_unknown_metadata_blocks_readiness PASSED [ 17%]
tests/test_data_validator.py::test_empty_missing_columns_and_non_utc PASSED [ 17%]
tests/test_data_validator.py::test_report_export_is_reproducible_and_no_overwrite PASSED [ 17%]
tests/test_engine.py::test_fee_trade_hand_calculation_and_timing PASSED  [ 18%]
tests/test_engine.py::test_zero_holds_and_last_order_is_unfilled PASSED  [ 18%]
tests/test_engine.py::test_rejections_are_logged_without_charging_costs PASSED [ 18%]
tests/test_engine.py::test_schedule_with_shifted_boundaries_is_rejected PASSED [ 19%]
tests/test_engine.py::test_same_bar_brackets_sl_first[1-101.5-104--5] PASSED [ 19%]
tests/test_engine.py::test_same_bar_brackets_sl_first[-1-104-101.5--20] PASSED [ 19%]
tests/test_engine.py::test_same_executable_prices_without_double_spread[Mid-0] PASSED [ 20%]
tests/test_engine.py::test_same_executable_prices_without_double_spread[Bid--1] PASSED [ 20%]
tests/test_engine.py::test_same_executable_prices_without_double_spread[Ask-1] PASSED [ 20%]
tests/test_engine.py::test_close_labeled_bars_and_weekend_next_available_open PASSED [ 21%]
tests/test_engine.py::test_currency_rates_never_use_future PASSED        [ 21%]
tests/test_engine.py::test_future_candles_do_not_change_earlier_outputs PASSED [ 21%]
tests/test_engine.py::test_invalid_data_blocks_simulation[duplicate] PASSED [ 22%]
tests/test_engine.py::test_invalid_data_blocks_simulation[unordered] PASSED [ 22%]
tests/test_engine.py::test_invalid_data_blocks_simulation[missing] PASSED [ 22%]
tests/test_engine.py::test_invalid_data_blocks_simulation[ohlc] PASSED   [ 23%]
tests/test_engine.py::test_invalid_data_blocks_simulation[metadata] PASSED [ 23%]
tests/test_engine.py::test_existing_position_and_bad_gap_bracket_rejected PASSED [ 23%]
tests/test_engine.py::test_stop_uses_bid_for_long_and_costs_once PASSED  [ 24%]
tests/test_engine.py::test_short_stop_uses_ask PASSED                    [ 24%]
tests/test_engine.py::test_gap_stop_fills_open_and_tp_does_not_use_better_gap_price PASSED [ 25%]
tests/test_engine.py::test_future_conversion_during_bar_not_used_for_stop PASSED [ 25%]
tests/test_engine.py::test_prefix_isolation_and_strategy_output_validation PASSED [ 25%]
tests/test_engine.py::test_incremental_strategy_api_matches_batch_output PASSED [ 26%]
tests/test_engine.py::test_insolvency_is_reported_for_extreme_short_gap PASSED [ 26%]
tests/test_engine.py::test_invalid_conversion_rates[0] PASSED            [ 26%]
tests/test_engine.py::test_invalid_conversion_rates[-1] PASSED           [ 27%]
tests/test_engine.py::test_invalid_conversion_rates[nan] PASSED          [ 27%]
tests/test_engine.py::test_invalid_conversion_rates[inf] PASSED          [ 27%]
tests/test_environment.py::test_research_environment PASSED              [ 28%]
tests/test_execution.py::test_protective_execution[1-bar0-95-stop_loss-True] PASSED [ 28%]
tests/test_execution.py::test_protective_execution[-1-bar1-105-stop_loss-True] PASSED [ 28%]
tests/test_execution.py::test_protective_execution[1-bar2-90-stop_loss_gap-False] PASSED [ 29%]
tests/test_execution.py::test_protective_execution[-1-bar3-110-stop_loss_gap-False] PASSED [ 29%]
tests/test_execution.py::test_protective_execution[1-bar4-105-take_profit_gap-False] PASSED [ 29%]
tests/test_execution.py::test_protective_execution[-1-bar5-95-take_profit_gap-False] PASSED [ 30%]
tests/test_execution.py::test_protective_execution[1-bar6-105-take_profit-False] PASSED [ 30%]
tests/test_execution.py::test_protective_execution[-1-bar7-95-take_profit-False] PASSED [ 30%]
tests/test_indicators.py::test_moving_averages_and_nan_restart PASSED    [ 31%]
tests/test_indicators.py::test_momentum_arithmetic PASSED                [ 31%]
tests/test_indicators.py::test_volatility_arithmetic PASSED              [ 31%]
tests/test_indicators.py::test_trend_arithmetic PASSED                   [ 32%]
tests/test_indicators.py::test_candle_geometry_and_patterns PASSED       [ 32%]
tests/test_indicators.py::test_structure_confirmations_and_breaks PASSED [ 32%]
tests/test_indicators.py::test_previous_period_pivots[traditional-r1] PASSED [ 33%]
tests/test_indicators.py::test_previous_period_pivots[fibonacci-r1] PASSED [ 33%]
tests/test_indicators.py::test_previous_period_pivots[camarilla-r1] PASSED [ 33%]
tests/test_indicators.py::test_previous_period_pivots[cpr-top] PASSED    [ 34%]
tests/test_indicators.py::test_sessions_vwap_orb_calendar_and_gap PASSED [ 34%]
tests/test_indicators.py::test_regimes_and_cycle PASSED                  [ 34%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>0] PASSED [ 35%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>1] PASSED [ 35%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>2] PASSED [ 35%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>3] PASSED [ 36%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>4] PASSED [ 36%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>5] PASSED [ 36%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>6] PASSED [ 37%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>7] PASSED [ 37%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>8] PASSED [ 37%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>9] PASSED [ 38%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>10] PASSED [ 38%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>11] PASSED [ 38%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>12] PASSED [ 39%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>13] PASSED [ 39%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>14] PASSED [ 39%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>15] PASSED [ 40%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>16] PASSED [ 40%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>17] PASSED [ 40%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>18] PASSED [ 41%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>19] PASSED [ 41%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>20] PASSED [ 41%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>21] PASSED [ 42%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>22] PASSED [ 42%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>23] PASSED [ 42%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>24] PASSED [ 43%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>25] PASSED [ 43%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>26] PASSED [ 43%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>27] PASSED [ 44%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>28] PASSED [ 44%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>29] PASSED [ 44%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>30] PASSED [ 45%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>31] PASSED [ 45%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>32] PASSED [ 45%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>33] PASSED [ 46%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>34] PASSED [ 46%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>35] PASSED [ 46%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>36] PASSED [ 47%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>37] PASSED [ 47%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>38] PASSED [ 47%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>39] PASSED [ 48%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>40] PASSED [ 48%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>41] PASSED [ 48%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>42] PASSED [ 49%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>43] PASSED [ 49%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>44] PASSED [ 50%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>45] PASSED [ 50%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>46] PASSED [ 50%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>47] PASSED [ 51%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>48] PASSED [ 51%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>49] PASSED [ 51%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>50] PASSED [ 52%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>51] PASSED [ 52%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>52] PASSED [ 52%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>53] PASSED [ 53%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>54] PASSED [ 53%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>55] PASSED [ 53%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>56] PASSED [ 54%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>57] PASSED [ 54%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>58] PASSED [ 54%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>59] PASSED [ 55%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>60] PASSED [ 55%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>61] PASSED [ 55%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>62] PASSED [ 56%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>63] PASSED [ 56%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>64] PASSED [ 56%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>65] PASSED [ 57%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>66] PASSED [ 57%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>67] PASSED [ 57%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>68] PASSED [ 58%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>69] PASSED [ 58%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>70] PASSED [ 58%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>71] PASSED [ 59%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>72] PASSED [ 59%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>73] PASSED [ 59%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>74] PASSED [ 60%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>75] PASSED [ 60%]
tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs[<lambda>76] PASSED [ 60%]
tests/test_indicators.py::test_invalid_windows[0-sma] PASSED             [ 61%]
tests/test_indicators.py::test_invalid_windows[0-ema] PASSED             [ 61%]
tests/test_indicators.py::test_invalid_windows[0-wma] PASSED             [ 61%]
tests/test_indicators.py::test_invalid_windows[0-rma] PASSED             [ 62%]
tests/test_indicators.py::test_invalid_windows[-1-sma] PASSED            [ 62%]
tests/test_indicators.py::test_invalid_windows[-1-ema] PASSED            [ 62%]
tests/test_indicators.py::test_invalid_windows[-1-wma] PASSED            [ 63%]
tests/test_indicators.py::test_invalid_windows[-1-rma] PASSED            [ 63%]
tests/test_indicators.py::test_invalid_windows[1.5-sma] PASSED           [ 63%]
tests/test_indicators.py::test_invalid_windows[1.5-ema] PASSED           [ 64%]
tests/test_indicators.py::test_invalid_windows[1.5-wma] PASSED           [ 64%]
tests/test_indicators.py::test_invalid_windows[1.5-rma] PASSED           [ 64%]
tests/test_indicators.py::test_invalid_inputs PASSED                     [ 65%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>0] PASSED [ 65%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>1] PASSED [ 65%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>2] PASSED [ 66%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>3] PASSED [ 66%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>4] PASSED [ 66%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>5] PASSED [ 67%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>6] PASSED [ 67%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>7] PASSED [ 67%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>8] PASSED [ 68%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>9] PASSED [ 68%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>10] PASSED [ 68%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>11] PASSED [ 69%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>12] PASSED [ 69%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>13] PASSED [ 69%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>14] PASSED [ 70%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>15] PASSED [ 70%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>16] PASSED [ 70%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>17] PASSED [ 71%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>18] PASSED [ 71%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>19] PASSED [ 71%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>20] PASSED [ 72%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>21] PASSED [ 72%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>22] PASSED [ 72%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>23] PASSED [ 73%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>24] PASSED [ 73%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>25] PASSED [ 73%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>26] PASSED [ 74%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>27] PASSED [ 74%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>28] PASSED [ 75%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>29] PASSED [ 75%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>30] PASSED [ 75%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>31] PASSED [ 76%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>32] PASSED [ 76%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>33] PASSED [ 76%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>34] PASSED [ 77%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>35] PASSED [ 77%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>36] PASSED [ 77%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>37] PASSED [ 78%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>38] PASSED [ 78%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>39] PASSED [ 78%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>40] PASSED [ 79%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>41] PASSED [ 79%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>42] PASSED [ 79%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>43] PASSED [ 80%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>44] PASSED [ 80%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>45] PASSED [ 80%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>46] PASSED [ 81%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>47] PASSED [ 81%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>48] PASSED [ 81%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>49] PASSED [ 82%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>50] PASSED [ 82%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>51] PASSED [ 82%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>52] PASSED [ 83%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>53] PASSED [ 83%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>54] PASSED [ 83%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>55] PASSED [ 84%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>56] PASSED [ 84%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>57] PASSED [ 84%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>58] PASSED [ 85%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>59] PASSED [ 85%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>60] PASSED [ 85%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>61] PASSED [ 86%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>62] PASSED [ 86%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>63] PASSED [ 86%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>64] PASSED [ 87%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>65] PASSED [ 87%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>66] PASSED [ 87%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>67] PASSED [ 88%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>68] PASSED [ 88%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>69] PASSED [ 88%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>70] PASSED [ 89%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>71] PASSED [ 89%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>72] PASSED [ 89%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>73] PASSED [ 90%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>74] PASSED [ 90%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>75] PASSED [ 90%]
tests/test_indicators.py::test_empty_and_missing_inputs[<lambda>76] PASSED [ 91%]
tests/test_indicators.py::test_nan_and_zero_denominators PASSED          [ 91%]
tests/test_indicators.py::test_bearish_patterns_and_lower_structures PASSED [ 91%]
tests/test_indicators.py::test_ema_against_documented_pandas_reference PASSED [ 92%]
tests/test_indicators.py::test_input_order_and_numeric_validation PASSED [ 92%]
tests/test_indicators.py::test_cycle_phase_independent_direct_hilbert_sum PASSED [ 92%]
tests/test_intraday_gaps.py::test_simple_gap_report_and_actual_next_open[timestamps0-0-0-0] PASSED [ 93%]
tests/test_intraday_gaps.py::test_simple_gap_report_and_actual_next_open[timestamps1-1-3-0] PASSED [ 93%]
tests/test_intraday_gaps.py::test_simple_gap_report_and_actual_next_open[timestamps2-0-0-1] PASSED [ 93%]
tests/test_intraday_gaps.py::test_simple_gap_report_and_actual_next_open[timestamps3-0-0-1] PASSED [ 94%]
tests/test_intraday_gaps.py::test_simple_gap_report_and_actual_next_open[timestamps4-0-0-1] PASSED [ 94%]
tests/test_intraday_gaps.py::test_explicit_calendar_remains_strict_and_independent PASSED [ 94%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[duplicate] PASSED [ 95%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[reverse] PASSED [ 95%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[nan] PASSED [ 95%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[inf] PASSED [ 96%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[ohlc] PASSED [ 96%]
tests/test_intraday_gaps.py::test_mandatory_validation_still_blocks_without_calendar[negative] PASSED [ 96%]
tests/test_intraday_gaps.py::test_nonmultiple_gap_counts_grid_points_and_no_cross_day_warning PASSED [ 97%]
tests/test_portfolio.py::test_accounting_with_currency_conversion[1-110] PASSED [ 97%]
tests/test_portfolio.py::test_accounting_with_currency_conversion[-1-90] PASSED [ 97%]
tests/test_portfolio.py::test_insufficient_capital_and_invalid_stops_do_not_mutate PASSED [ 98%]
tests/test_stage4_review.py::test_causal_indicator_and_future_leaking_features PASSED [ 98%]
tests/test_stage4_review.py::test_independent_schedule_detects_missing_first_middle_last PASSED [ 98%]
tests/test_stage4_review.py::test_schedule_rejects_overlapping_candles PASSED [ 99%]
tests/test_stage4_review.py::test_portfolio_rejects_mismatched_ids_and_time_without_mutation PASSED [ 99%]
tests/test_stage4_review.py::test_incremental_and_legacy_results_are_identical PASSED [100%]

- generated xml file: C:\Users\Admin\Documents\quant_backtest_system\reports\external_audit\pytest_results.xml -
============================= 296 passed in 3.87s =============================

```
stderr:

```text

```

## git_diff_check

Lệnh: `git diff --check`

Exit code: 0; thời gian wall-clock: 0.028 giây.

stdout:

```text

```
stderr:

```text
warning: in the working copy of 'indicators/__init__.py', LF will be replaced by CRLF the next time Git touches it

```

## git_diff_cached_check

Lệnh: `git diff --cached --check`

Exit code: 0; thời gian wall-clock: 0.021 giây.

stdout:

```text

```
stderr:

```text

```

## pip_check

Lệnh: `C:\Users\Admin\Documents\quant_backtest_system\.venv\Scripts\python.exe -B -m pip check`

Exit code: 0; thời gian wall-clock: 0.379 giây.

stdout:

```text
No broken requirements found.

```
stderr:

```text

```

## compile

```json
{
  "method": "Python compile(bytes, absolute_path, exec), in memory; no pyc files",
  "passed": [
    "benchmark_engine.py",
    "inspect_data.py",
    "inspect_indicators.py",
    "run_backtest.py",
    "core/__init__.py",
    "core/causality.py",
    "core/cost_model.py",
    "core/data_loader.py",
    "core/data_manager.py",
    "core/data_validator.py",
    "core/engine.py",
    "core/execution.py",
    "core/metrics.py",
    "core/models.py",
    "core/portfolio.py",
    "indicators/__init__.py",
    "indicators/_utils.py",
    "indicators/custom_indicators.py",
    "indicators/market_structure.py",
    "indicators/momentum.py",
    "indicators/moving_averages.py",
    "indicators/price_action.py",
    "indicators/sessions.py",
    "indicators/trend.py",
    "indicators/volatility.py",
    "strategies/__init__.py",
    "strategies/base_strategy.py",
    "strategies/first_strategy.py",
    "tests/test_backtest_models.py",
    "tests/test_cost_model.py",
    "tests/test_data_loader.py",
    "tests/test_data_validator.py",
    "tests/test_engine.py",
    "tests/test_environment.py",
    "tests/test_execution.py",
    "tests/test_indicators.py",
    "tests/test_intraday_gaps.py",
    "tests/test_portfolio.py",
    "tests/test_stage4_review.py"
  ],
  "failures": []
}
```

## JUnit XML nguyên vẹn

```xml
<?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests"><testsuite name="pytest" errors="0" failures="0" skipped="0" tests="296" time="3.866" timestamp="2026-11-17T16:33:32.163141+07:00" hostname="DESKTOP-8KVEPHO"><testcase classname="tests.test_backtest_models" name="test_instrument_conversion_and_metadata" time="0.001" /><testcase classname="tests.test_backtest_models" name="test_unsupported_or_invalid_orders[kwargs0]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_unsupported_or_invalid_orders[kwargs1]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_unsupported_or_invalid_orders[kwargs2]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_unsupported_or_invalid_orders[kwargs3]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_unsupported_or_invalid_orders[kwargs4]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes0]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes1]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes2]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes3]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes4]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes5]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes6]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_fill_rejects_invalid_financial_fields[changes7]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_position_rejects_invalid_state[changes0]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_position_rejects_invalid_state[changes1]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_position_rejects_invalid_state[changes2]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_position_rejects_invalid_state[changes3]" time="0.000" /><testcase classname="tests.test_backtest_models" name="test_position_rejects_invalid_state[changes4]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Mid-1-101]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Mid--1-99]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Bid-1-102]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Bid--1-100]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Ask-1-100]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_bid_ask_conventions[Ask--1-98]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_fill_costs_and_adverse_tick_rounding" time="0.000" /><testcase classname="tests.test_cost_model" name="test_reject_invalid_costs_and_swap[args0]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_reject_invalid_costs_and_swap[args1]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_reject_invalid_costs_and_swap[args2]" time="0.000" /><testcase classname="tests.test_cost_model" name="test_reject_invalid_costs_and_swap[args3]" time="0.000" /><testcase classname="tests.test_data_loader" name="test_round_trip_preserves_rows_and_raw" time="0.040" /><testcase classname="tests.test_data_loader" name="test_parquet_failure_leaves_no_partial_or_temporary_file" time="0.002" /><testcase classname="tests.test_data_loader" name="test_parquet_publication_failure_cleans_temp_and_preserves_existing" time="0.006" /><testcase classname="tests.test_data_loader" name="test_invalid_tokens_are_reported_not_removed" time="0.011" /><testcase classname="tests.test_data_loader" name="test_unconfirmed_encoding_requires_diagnostic_mode" time="0.005" /><testcase classname="tests.test_data_loader" name="test_missing_columns_and_mapping" time="0.006" /><testcase classname="tests.test_data_loader" name="test_explicit_local_timezone_and_dst" time="0.007" /><testcase classname="tests.test_data_loader" name="test_aware_strings_do_not_accept_naive_values" time="0.005" /><testcase classname="tests.test_data_loader" name="test_metadata_and_json_no_overwrite" time="0.004" /><testcase classname="tests.test_data_validator" name="test_clean_data_ready_without_calendar_but_not_calendar_verified" time="0.010" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[open-nan-open_missing_or_non_numeric]" time="0.004" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[close-inf-close_infinite]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[low-0-low_invalid_sign]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[open--1-open_invalid_sign]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[volume--1-volume_invalid_sign]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[high-0.75-invalid_ohlc]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_bad_numeric_values[low-1.75-invalid_ohlc]" time="0.003" /><testcase classname="tests.test_data_validator" name="test_duplicates_unsorted_and_nat" time="0.006" /><testcase classname="tests.test_data_validator" name="test_gap_candidates_do_not_imply_market_missing" time="0.006" /><testcase classname="tests.test_data_validator" name="test_closed_session_gap_is_accepted_with_explicit_calendar" time="0.003" /><testcase classname="tests.test_data_validator" name="test_unknown_metadata_blocks_readiness" time="0.003" /><testcase classname="tests.test_data_validator" name="test_empty_missing_columns_and_non_utc" time="0.006" /><testcase classname="tests.test_data_validator" name="test_report_export_is_reproducible_and_no_overwrite" time="0.006" /><testcase classname="tests.test_engine" name="test_fee_trade_hand_calculation_and_timing" time="0.011" /><testcase classname="tests.test_engine" name="test_zero_holds_and_last_order_is_unfilled" time="0.005" /><testcase classname="tests.test_engine" name="test_rejections_are_logged_without_charging_costs" time="0.005" /><testcase classname="tests.test_engine" name="test_schedule_with_shifted_boundaries_is_rejected" time="0.007" /><testcase classname="tests.test_engine" name="test_same_bar_brackets_sl_first[1-101.5-104--5]" time="0.005" /><testcase classname="tests.test_engine" name="test_same_bar_brackets_sl_first[-1-104-101.5--20]" time="0.005" /><testcase classname="tests.test_engine" name="test_same_executable_prices_without_double_spread[Mid-0]" time="0.005" /><testcase classname="tests.test_engine" name="test_same_executable_prices_without_double_spread[Bid--1]" time="0.005" /><testcase classname="tests.test_engine" name="test_same_executable_prices_without_double_spread[Ask-1]" time="0.005" /><testcase classname="tests.test_engine" name="test_close_labeled_bars_and_weekend_next_available_open" time="0.009" /><testcase classname="tests.test_engine" name="test_currency_rates_never_use_future" time="0.011" /><testcase classname="tests.test_engine" name="test_future_candles_do_not_change_earlier_outputs" time="0.009" /><testcase classname="tests.test_engine" name="test_invalid_data_blocks_simulation[duplicate]" time="0.004" /><testcase classname="tests.test_engine" name="test_invalid_data_blocks_simulation[unordered]" time="0.004" /><testcase classname="tests.test_engine" name="test_invalid_data_blocks_simulation[missing]" time="0.004" /><testcase classname="tests.test_engine" name="test_invalid_data_blocks_simulation[ohlc]" time="0.003" /><testcase classname="tests.test_engine" name="test_invalid_data_blocks_simulation[metadata]" time="0.001" /><testcase classname="tests.test_engine" name="test_existing_position_and_bad_gap_bracket_rejected" time="0.009" /><testcase classname="tests.test_engine" name="test_stop_uses_bid_for_long_and_costs_once" time="0.005" /><testcase classname="tests.test_engine" name="test_short_stop_uses_ask" time="0.005" /><testcase classname="tests.test_engine" name="test_gap_stop_fills_open_and_tp_does_not_use_better_gap_price" time="0.010" /><testcase classname="tests.test_engine" name="test_future_conversion_during_bar_not_used_for_stop" time="0.006" /><testcase classname="tests.test_engine" name="test_prefix_isolation_and_strategy_output_validation" time="0.012" /><testcase classname="tests.test_engine" name="test_incremental_strategy_api_matches_batch_output" time="0.005" /><testcase classname="tests.test_engine" name="test_insolvency_is_reported_for_extreme_short_gap" time="0.006" /><testcase classname="tests.test_engine" name="test_invalid_conversion_rates[0]" time="0.001" /><testcase classname="tests.test_engine" name="test_invalid_conversion_rates[-1]" time="0.001" /><testcase classname="tests.test_engine" name="test_invalid_conversion_rates[nan]" time="0.001" /><testcase classname="tests.test_engine" name="test_invalid_conversion_rates[inf]" time="0.001" /><testcase classname="tests.test_environment" name="test_research_environment" time="0.001" /><testcase classname="tests.test_execution" name="test_protective_execution[1-bar0-95-stop_loss-True]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[-1-bar1-105-stop_loss-True]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[1-bar2-90-stop_loss_gap-False]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[-1-bar3-110-stop_loss_gap-False]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[1-bar4-105-take_profit_gap-False]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[-1-bar5-95-take_profit_gap-False]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[1-bar6-105-take_profit-False]" time="0.000" /><testcase classname="tests.test_execution" name="test_protective_execution[-1-bar7-95-take_profit-False]" time="0.000" /><testcase classname="tests.test_indicators" name="test_moving_averages_and_nan_restart" time="0.008" /><testcase classname="tests.test_indicators" name="test_momentum_arithmetic" time="0.024" /><testcase classname="tests.test_indicators" name="test_volatility_arithmetic" time="0.021" /><testcase classname="tests.test_indicators" name="test_trend_arithmetic" time="0.086" /><testcase classname="tests.test_indicators" name="test_candle_geometry_and_patterns" time="0.062" /><testcase classname="tests.test_indicators" name="test_structure_confirmations_and_breaks" time="0.038" /><testcase classname="tests.test_indicators" name="test_previous_period_pivots[traditional-r1]" time="0.013" /><testcase classname="tests.test_indicators" name="test_previous_period_pivots[fibonacci-r1]" time="0.012" /><testcase classname="tests.test_indicators" name="test_previous_period_pivots[camarilla-r1]" time="0.012" /><testcase classname="tests.test_indicators" name="test_previous_period_pivots[cpr-top]" time="0.012" /><testcase classname="tests.test_indicators" name="test_sessions_vwap_orb_calendar_and_gap" time="0.038" /><testcase classname="tests.test_indicators" name="test_regimes_and_cycle" time="0.023" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;0]" time="0.004" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;1]" time="0.008" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;2]" time="0.007" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;3]" time="0.007" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;4]" time="0.014" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;5]" time="0.004" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;6]" time="0.003" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;7]" time="0.005" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;8]" time="0.004" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;9]" time="0.012" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;10]" time="0.003" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;11]" time="0.007" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;12]" time="0.008" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;13]" time="0.007" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;14]" time="0.021" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;15]" time="0.020" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;16]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;17]" time="0.023" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;18]" time="0.017" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;19]" time="0.016" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;20]" time="0.014" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;21]" time="0.014" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;22]" time="0.050" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;23]" time="0.044" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;24]" time="0.017" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;25]" time="0.032" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;26]" time="0.030" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;27]" time="0.022" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;28]" time="0.024" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;29]" time="0.032" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;30]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;31]" time="0.142" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;32]" time="0.021" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;33]" time="0.005" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;34]" time="0.005" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;35]" time="0.015" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;36]" time="0.024" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;37]" time="0.021" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;38]" time="0.019" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;39]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;40]" time="0.029" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;41]" time="0.036" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;42]" time="0.026" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;43]" time="0.036" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;44]" time="0.030" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;45]" time="0.043" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;46]" time="0.027" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;47]" time="0.027" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;48]" time="0.016" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;49]" time="0.028" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;50]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;51]" time="0.032" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;52]" time="0.159" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;53]" time="0.021" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;54]" time="0.037" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;55]" time="0.026" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;56]" time="0.037" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;57]" time="0.026" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;58]" time="0.026" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;59]" time="0.026" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;60]" time="0.036" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;61]" time="0.035" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;62]" time="0.039" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;63]" time="0.032" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;64]" time="0.030" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;65]" time="0.029" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;66]" time="0.029" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;67]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;68]" time="0.011" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;69]" time="0.028" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;70]" time="0.027" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;71]" time="0.036" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;72]" time="0.004" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;73]" time="0.018" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;74]" time="0.050" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;75]" time="0.025" /><testcase classname="tests.test_indicators" name="test_all_indicators_preserve_index_causality_and_inputs[&lt;lambda&gt;76]" time="0.022" /><testcase classname="tests.test_indicators" name="test_invalid_windows[0-sma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[0-ema]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[0-wma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[0-rma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[-1-sma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[-1-ema]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[-1-wma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[-1-rma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[1.5-sma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[1.5-ema]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[1.5-wma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_windows[1.5-rma]" time="0.000" /><testcase classname="tests.test_indicators" name="test_invalid_inputs" time="0.003" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;0]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;1]" time="0.002" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;2]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;3]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;4]" time="0.003" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;5]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;6]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;7]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;8]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;9]" time="0.002" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;10]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;11]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;12]" time="0.002" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;13]" time="0.002" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;14]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;15]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;16]" time="0.003" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;17]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;18]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;19]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;20]" time="0.003" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;21]" time="0.003" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;22]" time="0.010" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;23]" time="0.009" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;24]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;25]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;26]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;27]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;28]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;29]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;30]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;31]" time="0.020" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;32]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;33]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;34]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;35]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;36]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;37]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;38]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;39]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;40]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;41]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;42]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;43]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;44]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;45]" time="0.010" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;46]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;47]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;48]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;49]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;50]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;51]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;52]" time="0.022" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;53]" time="0.005" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;54]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;55]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;56]" time="0.009" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;57]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;58]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;59]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;60]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;61]" time="0.009" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;62]" time="0.009" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;63]" time="0.008" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;64]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;65]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;66]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;67]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;68]" time="0.002" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;69]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;70]" time="0.007" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;71]" time="0.009" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;72]" time="0.001" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;73]" time="0.004" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;74]" time="0.011" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;75]" time="0.006" /><testcase classname="tests.test_indicators" name="test_empty_and_missing_inputs[&lt;lambda&gt;76]" time="0.002" /><testcase classname="tests.test_indicators" name="test_nan_and_zero_denominators" time="0.037" /><testcase classname="tests.test_indicators" name="test_bearish_patterns_and_lower_structures" time="0.025" /><testcase classname="tests.test_indicators" name="test_ema_against_documented_pandas_reference" time="0.001" /><testcase classname="tests.test_indicators" name="test_input_order_and_numeric_validation" time="0.002" /><testcase classname="tests.test_indicators" name="test_cycle_phase_independent_direct_hilbert_sum" time="0.001" /><testcase classname="tests.test_intraday_gaps" name="test_simple_gap_report_and_actual_next_open[timestamps0-0-0-0]" time="0.007" /><testcase classname="tests.test_intraday_gaps" name="test_simple_gap_report_and_actual_next_open[timestamps1-1-3-0]" time="0.007" /><testcase classname="tests.test_intraday_gaps" name="test_simple_gap_report_and_actual_next_open[timestamps2-0-0-1]" time="0.006" /><testcase classname="tests.test_intraday_gaps" name="test_simple_gap_report_and_actual_next_open[timestamps3-0-0-1]" time="0.007" /><testcase classname="tests.test_intraday_gaps" name="test_simple_gap_report_and_actual_next_open[timestamps4-0-0-1]" time="0.006" /><testcase classname="tests.test_intraday_gaps" name="test_explicit_calendar_remains_strict_and_independent" time="0.006" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[duplicate]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[reverse]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[nan]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[inf]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[ohlc]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_mandatory_validation_still_blocks_without_calendar[negative]" time="0.005" /><testcase classname="tests.test_intraday_gaps" name="test_nonmultiple_gap_counts_grid_points_and_no_cross_day_warning" time="0.005" /><testcase classname="tests.test_portfolio" name="test_accounting_with_currency_conversion[1-110]" time="0.000" /><testcase classname="tests.test_portfolio" name="test_accounting_with_currency_conversion[-1-90]" time="0.000" /><testcase classname="tests.test_portfolio" name="test_insufficient_capital_and_invalid_stops_do_not_mutate" time="0.000" /><testcase classname="tests.test_stage4_review" name="test_causal_indicator_and_future_leaking_features" time="0.003" /><testcase classname="tests.test_stage4_review" name="test_independent_schedule_detects_missing_first_middle_last" time="0.012" /><testcase classname="tests.test_stage4_review" name="test_schedule_rejects_overlapping_candles" time="0.000" /><testcase classname="tests.test_stage4_review" name="test_portfolio_rejects_mismatched_ids_and_time_without_mutation" time="0.000" /><testcase classname="tests.test_stage4_review" name="test_incremental_and_legacy_results_are_identical" time="0.009" /></testsuite></testsuites>
```

## Giới hạn bảo toàn dữ liệu

SHA256 của mọi source đã khảo sát không thay đổi sau kiểm tra.
Đối chiếu size/mtime của 1435 file trong data/, download/ và cache không phát hiện thay đổi. Không đọc/hash toàn bộ dữ liệu giá lớn; size/mtime không phải chứng minh byte-for-byte cho dữ liệu lịch sử.
