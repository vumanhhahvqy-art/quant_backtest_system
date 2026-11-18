# FINAL SYSTEM AUDIT REPORT

**Dự án:** `quant_backtest_system` · **Commit nền:** `7af3b774b1721e091e2527a00563912255d44702` (snapshot là working tree chưa commit)
**Ngày kiểm toán tổng hợp:** 2026-11-17 · **Loại kiểm toán:** hợp nhất bằng chứng thứ cấp, đọc tĩnh
**Không có mã nào được chạy trong cuộc kiểm toán này. Không có test nào được tuyên bố là đã passed bởi kiểm toán này.**

---

## 1. Executive Summary

**Kết luận ngắn:** không thể kết luận PASS toàn hệ thống, và hệ thống chưa nên được dùng để tạo kết quả nghiên cứu. Lý do chính là thiếu bằng chứng tích hợp và thực thi, chứ chưa phải vì đã chứng minh được một lỗi tính toán nghiêm trọng.

**Bằng chứng nền tảng.** Cuộc kiểm toán này chỉ có 4 báo cáo thứ cấp (đều là đọc tĩnh, mỗi báo cáo chỉ thấy một phần mã), tài liệu tổng quan, hồ sơ bàn giao và manifest. Không có mã nguồn, không có `07_TEST_RESULTS.md`, không có `00A`, `00B`. Con số "296 passed" xuất hiện trong `00_PROJECT_OVERVIEW.md` nhưng không ai trong chuỗi kiểm toán xem được stdout gốc.

**Kết quả hợp nhất:**

| Hạng mục | Số lượng |
|---|---|
| Phát hiện nguồn (4 báo cáo) | 34 (STRATEGIES 8, CORE 8, DATA 8, INDICATORS 10) |
| Vấn đề hợp nhất (SYS-xxx) | 27 |
| Trong đó P0 (cổng phải xử lý trước khi dùng kết quả cho nghiên cứu) | 5 |
| Trong đó P1 | 13 |
| Trong đó P2 | 9 |
| Phát hiện được chứng minh bằng thực thi | 0 |
| Phát hiện CONFIRMED từ văn bản trực tiếp (E1, xem mục 2.4) | 4 nhóm lỗi tài liệu/quy trình, chi tiết ở mục 12.2 |
| Vấn đề hợp nhất mới, không có trong danh sách gốc | 4 (SYS-005, 008, 012, 017) |

**Về mức P0.** Chỉ một phát hiện nguồn mang mức P0 (INDICATORS #1, có điều kiện). Năm "cổng P0" ở đây được nâng mức theo đúng định nghĩa của đề bài: *phải xử lý trước khi dùng kết quả backtest cho nghiên cứu*. Việc nâng mức không có nghĩa là đã chứng minh sai phép tính. Mỗi cổng P0 có thể được đóng bằng cách sửa hoặc bằng bằng chứng thực thi chứng minh nó không phải lỗi.

| Cổng | Nội dung | Bản chất |
|---|---|---|
| SYS-001 | Quy ước nhãn thời gian (open hay close) chưa thống nhất giữa dữ liệu, `sessions` và engine | Rủi ro look-ahead / lệch một nến; SUSPECTED |
| SYS-002 | Kết quả không truy được về commit, dữ liệu, tham số, môi trường | Rủi ro quy trình, đã chứng minh từ văn bản |
| SYS-003 | So sánh chạm SL/TP và làm tròn tick trên số thực | Rủi ro sai khớp lệnh; SUSPECTED, kiểm chứng rẻ |
| SYS-004 | Test nhân quả dùng dung sai ngầm nên bằng chứng "không look-ahead" yếu hơn vẻ ngoài | Rủi ro bằng chứng |
| SYS-005 | Metadata dữ liệu thật chưa xác nhận; chưa rõ engine có chặn dữ liệu `ready_for_research=False` hay không | Rủi ro tích hợp; NEEDS VERIFICATION |

**Ba chủ đề xuyên module nổi bật:**

1. **Đường nhân quả chưa được kiểm chứng từ đầu đến cuối.** Từng chỉ báo được báo cáo là không có look-ahead khi đọc mã, nhưng nhãn thời gian giữa `sessions` và engine mâu thuẫn trong tài liệu, các cột tính sẵn không được bảo vệ, và dung sai của test prefix lỏng.
2. **Hiệu năng ở 1,44 triệu nến.** Đường chiến lược mặc định của engine (đưa toàn bộ prefix cho strategy ở mỗi nến), `parabolic_sar` và `structure_breaks` đều có độ phức tạp O(n²) theo các đoạn mã được trích. Tôi đã kiểm tra lại phần số học của các ước lượng (xem mục 7). Chưa có phép đo nào.
3. **Tái lập.** Mã chưa commit, phụ thuộc chưa khóa, kết quả engine không ghi provenance, trong khi lớp dữ liệu đã ghi git revision và phiên bản phần mềm. Hai lớp không thống nhất.

**Điểm thiết kế đã được cả bốn báo cáo công nhận là đúng, cần giữ** (chi tiết ở mục 6): tách tín hiệu cuối nến và khớp ở nến kế tiếp, Bid/Ask suy ra từ một luồng giá, chi phí chỉ nằm trong giá khớp, SL ưu tiên khi cùng chạm, metadata fail-closed, không sort/fill/drop dữ liệu, vị thế cuối mẫu không bị ép đóng.

**Đánh giá bốn tiêu chí (chi tiết mục 12.1):**

| Tiêu chí | Đánh giá |
|---|---|
| A. Correctness | NOT VERIFIED (chiều hướng bằng chứng tĩnh thuận lợi) |
| B. Integration | NOT VERIFIED (hai mắt xích cuối NOT IMPLEMENTED) |
| C. Performance | FAIL cho đường mặc định theo phân tích độ phức tạp (chưa đo); đường gia tăng NOT VERIFIED |
| D. Reproducibility | FAIL cho truy xuất nguồn gốc ở mức nghiên cứu; tính tất định giữa các lần chạy NOT VERIFIED |

---

## 2. Audit Scope and Evidence

### 2.1 Tệp đã nhận và đã đọc

| Tệp | Vai trò | Mức đọc |
|---|---|---|
| `09_FINAL_AUDIT_INPUT.md` | Đề bài kiểm toán tổng hợp | Đọc đủ |
| `00_PROJECT_OVERVIEW.md` | Kiến trúc, trạng thái, môi trường, README, `pyproject.toml`, `run_backtest.py`, `.gitignore`, git status | Đọc đủ |
| `08_AUDIT_HANDOFF.md` | Điểm cần kiểm toán, danh sách gói, phạm vi loại trừ | Đọc đủ |
| `MANIFEST.md` | Hash và gói chứa 54 file nguồn | Đọc đủ; chỉ đối chiếu được số lượng (54 file, khớp với 00), không băm lại được vì không có file nguồn |
| `CLAUDE_AUDIT_CORE.md` | Báo cáo 1: engine, execution, cost, portfolio, models, BaseStrategy | Đọc đủ (346 dòng) |
| `CLAUDE_AUDIT_DATA.md` | Báo cáo 2: loader, validator, cấu hình, metadata | Đọc đủ (243 dòng) |
| `CLAUDE_AUDIT_INDICATORS.md` | Báo cáo 3: các module chỉ báo và test chỉ báo | Đọc đủ (189 dòng) |
| `CLAUDE_AUDIT_STRATEGIES.md` | Báo cáo 4: `causality.py`, `benchmark_engine.py`, scaffolding | Đọc đủ |

### 2.2 Mỗi báo cáo đã thấy gì

| Báo cáo | Đã thấy mã | Chỉ thấy qua test/mô tả | Không thấy | Kết luận tự nêu |
|---|---|---|---|---|
| CORE | `models`, `cost_model`, `execution`, `portfolio`, `engine`, `base_strategy`, `BACKTEST_ENGINE.md`, README, pyproject, test 05A–05D | `data_loader`, `data_validator`, `causality`, `indicators/*` | `benchmark_engine`, `configs`, `.clinerules`, 00A, 07 | PASS WITH LIMITATIONS cho logic mô phỏng lõi |
| DATA | `data_loader`, `data_validator`, `inspect_data`, `configs/*`, `data/metadata/*` (khoảng 13 trên 54 file) | không | engine stack, indicators, tests | PASS WITH LIMITATIONS cho lớp dữ liệu |
| INDICATORS | Các module chỉ báo, `_utils`, `inspect_indicators`, `test_indicators.py` | không | engine stack, loader, validator, `causality`, 05A–05C | PASS WITH LIMITATIONS cho chỉ báo; #1 có thể thành P0 |
| STRATEGIES | `causality.py`, `benchmark_engine.py`, `run_backtest.py`, README, pyproject, `.gitignore` | không | engine stack, loader, validator, indicators, tests | PASS WITH LIMITATIONS chỉ cho phạm vi đã đọc; không phán quyết P0 |

### 2.3 Những gì không ai đã thấy

- **Các điểm tiếp giáp (seam) chưa từng được xem đồng thời cả hai phía:**
  - Engine ↔ validator: CORE thấy engine nhưng không thấy validator; DATA thấy validator nhưng không thấy engine.
  - Indicators ↔ engine/strategy (nhãn thời gian của `sessions`): INDICATORS không thấy engine; CORE không thấy indicators.
  - Config ↔ CostModel ↔ metadata: chỉ có `08_AUDIT_HANDOFF.md` mô tả, không báo cáo nào kết luận.
- **Không báo cáo nào đọc `00B_PROJECT_RULES.md`**, nơi chứa các quy tắc gốc mà chỉ thị về gap trong ngày UTC được ưu tiên hơn.
- **Không có `07_TEST_RESULTS.md`** trong tay bất kỳ ai. Không có coverage, lint hay type check.
- **Không có dữ liệu thật.** Dữ liệu EURUSD M1 khoảng 1,44 triệu nến chưa được chạy qua pipeline trong hồ sơ.
- **Tôi cũng không có mã nguồn.** Mọi đoạn mã trích trong các báo cáo là bằng chứng thứ cấp mà tôi không thể đối chiếu với tệp gốc, nên hash trong `MANIFEST.md` chưa được kiểm.

### 2.4 Thang bằng chứng và nhãn trạng thái dùng trong báo cáo này

| Mức | Ý nghĩa |
|---|---|
| E0 | Bằng chứng thực thi (chạy test/benchmark). **Không có trong cuộc kiểm toán này.** |
| E1 | Suy ra trực tiếp từ văn bản tôi đang giữ (`00`, `08`, `MANIFEST`, `09`, pyproject, README, git status) |
| E2 | Phân tích tĩnh do báo cáo thứ cấp nêu, có trích mã; tôi chưa đối chiếu với mã gốc |
| E3 | Suy luận hoặc giả thuyết, phụ thuộc hành vi thư viện hoặc mã chưa thấy |

| Nhãn | Điều kiện dùng trong báo cáo này |
|---|---|
| CONFIRMED | Chỉ khi có bằng chứng E1 hoặc E0. Một báo cáo trước ghi "CONFIRMED" không đủ. |
| NEEDS VERIFICATION | Bằng chứng E2; kèm nhãn phụ `static-strong` nếu kết luận suy ra trực tiếp từ cấu trúc mã trích (ví dụ độ phức tạp), `static-weak` nếu phụ thuộc hành vi runtime hoặc thư viện |
| SUSPECTED | Bằng chứng E3, cần chạy mã để xác nhận hoặc bác bỏ |
| DESIGN LIMITATION | Hành vi có chủ đích, đã tài liệu hóa hoặc nằm trong phạm vi được chấp nhận |
| FALSE POSITIVE | Chỉ dùng khi có bằng chứng bác bỏ. **Chưa có phát hiện nào bị bác bỏ**, vì chưa có thực thi |
| NOT IMPLEMENTED | Module chưa có triển khai; không suy đoán nó hoạt động |

### 2.5 Hạn chế về tính độc lập của bằng chứng

Bốn báo cáo cùng dùng một phương pháp (đọc tĩnh), được viết trong các phiên riêng với phạm vi đầu vào khác nhau, và cùng nhắc lại con số 296 test chưa kiểm chứng. Hai báo cáo đồng ý với nhau **không** được coi là hai bằng chứng độc lập. Sai sót hệ thống trong cách đọc tĩnh (ví dụ hiểu sai ngữ nghĩa một hàm pandas) có thể lặp lại ở nhiều báo cáo. Vì vậy mọi phát hiện về hành vi runtime đều giữ nhãn NEEDS VERIFICATION hoặc SUSPECTED cho đến khi có test chạy.

---

## 3. Findings Consolidation

### 3.1 Bảng 34 phát hiện nguồn

Quy ước mã nguồn: `ST-` = `CLAUDE_AUDIT_STRATEGIES.md`, `CO-` = `CLAUDE_AUDIT_CORE.md` (F1–F8), `DA-` = `CLAUDE_AUDIT_DATA.md` (#1–#8), `IN-` = `CLAUDE_AUDIT_INDICATORS.md` (#1–#10). Cột "P gốc" là mức báo cáo nguồn gán. Cột "Trạng thái" là đánh giá của kiểm toán này, không phải sao chép từ báo cáo nguồn. Các báo cáo nguồn không có số dòng, nên vị trí chỉ gồm file và hàm.

| Nguồn | Nhóm | File / hàm | P gốc | Bằng chứng nguồn đã cung cấp | Trạng thái (kiểm toán này) | Hợp nhất |
|---|---|---|---|---|---|---|
| ST-01 | Validation | `core/causality.py::check_prefix_invariance` | P1 | `assert_frame_equal` không đặt `check_exact`/`rtol`/`atol`; bảng ví dụ 1e-5 | SUSPECTED (phụ thuộc mặc định pandas 3.1.1, kiểm chứng rẻ) | SYS-004 |
| ST-02 | Validation | `causality.py` (closure, cột tính sẵn) | P1 | Lập luận: trạng thái bên ngoài cho kết quả giống nhau ở mọi prefix | DESIGN LIMITATION (rủi ro quy trình) | SYS-018 |
| ST-03 | Validation | `causality.py` (`len(data) < 2`, `cutoffs=[]`, `isinstance(cutoff, int)`) | P1 | Trích cấu trúc vòng lặp; hàm trả `None` | NEEDS VERIFICATION (static-strong) | SYS-018, SYS-026 |
| ST-04 | Performance | `causality.py` (mọi prefix, `copy(deep=True)`) | P1 | Σ n²/2 ≈ 1,04×10¹² hàng ở n = 1,44×10⁶ | NEEDS VERIFICATION (static-strong); tiện ích kiểm thử, có cảnh báo trong docstring | SYS-018 |
| ST-05 | Performance / Integration | `benchmark_engine.py`, `BaseStrategy.generate_signals` (batch) | P1 | Suy đoán từ cấu trúc benchmark; CO-F1 sau đó cho thấy engine gọi lại strategy trên từng prefix | NEEDS VERIFICATION (câu hỏi mở của ST đã được CO-F1 thu hẹp, xem C-02) | SYS-006 |
| ST-06 | Reproducibility | git status, `pyproject.toml` | P1 | Phần lớn mã `??` hoặc `M`; `numpy>=1.26,<3`, `pandas>=2.2,<4`, không lock | **CONFIRMED (E1)**: git status và pyproject có trong `00` | SYS-002 |
| ST-07 | Benchmark | `benchmark_engine.py` | P2 | `assert` bị bỏ với `-O`; `outputs_identical: True` cố định; chỉ so lần lặp cuối | NEEDS VERIFICATION (static-strong; tôi không có mã script) | SYS-024 |
| ST-08 | Tài liệu | README, `pyproject.toml`, `run_backtest.py` | P2 | README nói chưa cần pyarrow và pytest có 1 bài; pyproject có `pyarrow>=23`; overview nói 296 test | **CONFIRMED (E1)**: cả README lẫn pyproject nằm trong `00`; `run_backtest.py` chỉ in thông báo | SYS-025 |
| CO-F1 | Performance | `engine.py::BacktestEngine.run`, `base_strategy.py::generate_signal` | P1 | `frame.iloc[start:i+1].copy(deep=True)` mỗi nến, `start=0` khi `signal_history_limit=None`; vị thế vòng lặp tạo `Series` mỗi nến | NEEDS VERIFICATION (static-strong) | SYS-006 |
| CO-F2 | Execution | `execution.py::protective_exit`, `cost_model.py::side_bar`, `fill` | P1 | So sánh `low <= sl` trên float; `ceil(ticks - 1e-9)`; lập luận dung sai 1e-9 không co giãn với BTC | SUSPECTED | SYS-003 |
| CO-F3 | Execution / Portfolio | `portfolio.py::open`, `engine.py` (nhánh `except ValueError`) | P1 | Lệnh bị từ chối khi gap làm SL/TP không bao quanh giá khớp; event không có mã, không có bộ đếm | DESIGN LIMITATION (có tài liệu) + thiếu quan sát được | SYS-010 |
| CO-F4 | Strategy lifecycle | `base_strategy.py`, `engine.py::run` | P1 | Không có `reset`, không truyền trạng thái vị thế/fill | NEEDS VERIFICATION (static-strong về thiếu cơ chế; tác động tùy strategy) | SYS-009 |
| CO-F5 | Reproducibility | `engine.py` (dict `assumptions`) | P1 | Thiếu hash dữ liệu, tên và tham số strategy, phiên bản thư viện, commit | Phần working tree/lock: **CONFIRMED (E1)**; phần nội dung `assumptions`: NEEDS VERIFICATION | SYS-002 |
| CO-F6 | Integration | `engine.py` (`states.append(portfolio.mark(closing, ...))`), nhãn `AccountState`/`Fill` | P2 | Với nến nhãn open, `states[i].timestamp == data.index[i+1]`; fill SL/TP intrabar mang nhãn đầu nến | DESIGN LIMITATION; liên quan trực tiếp tới IN-1 (xem C-01) | SYS-001 |
| CO-F7 | Robustness | `engine.py`, `cost_model.py::side_bar` | P2 | `except ValueError` dùng làm luồng điều khiển; lỗi giá ≤ 0 không nêu nến | NEEDS VERIFICATION (static-weak) | SYS-020 |
| CO-F8 | Tài liệu / cấu hình | README, `Instrument.pip_size`, `configs/config.yaml`, `BACKTEST_ENGINE.md` | P2 | Phần README/pyproject như ST-08; `pip_size` bắt buộc nhưng không dùng; số benchmark chưa tái lập | Phần README/pyproject: **CONFIRMED (E1)**; các phần còn lại NEEDS VERIFICATION | SYS-025, SYS-021, SYS-014 |
| DA-1 | Data validation | `data_validator.py::validate_data` | P1 | `irregular` chỉ sinh cảnh báo, chỉ xét cặp liên tiếp cùng ngày | NEEDS VERIFICATION (static-strong); cần quyết định chính sách của chủ dự án (xem 4.2) | SYS-011 |
| DA-2 | Data loading | `data_loader.py::load_csv(diagnostic=False)` | P1 | Token lỗi thành NaN/NaT (`errors="coerce"`), hàm trả `LoadResult`, không raise | SUSPECTED (phụ thuộc có engine chặn dữ liệu lỗi hay không) | SYS-013, SYS-005 |
| DA-3 | Metadata | `symbols.json`, `datasets.json`, `metadata_blockers` | P1 | XAUUSD: `point_value 1e-05` (legacy) so với `point_size 0.001` (registry); chênh 100 lần | NEEDS VERIFICATION (static-strong; `08` xác nhận legacy không được engine tin cậy nên rủi ro có điều kiện) | SYS-014 |
| DA-4 | Data I/O | `data_loader.py::write_json` | P2 | Mở file chế độ `"x"` rồi `json.dump` có thể raise giữa chừng, để lại file cụt | NEEDS VERIFICATION (static-strong) | SYS-022 |
| DA-5 | Cấu hình | `configs/config.yaml` | P2 | `include_swap: true`; timeframe `"H1"`; ngày kết thúc `2026-01-01`; `slippage_points` không nêu đơn vị | Phần `include_swap` và đơn vị slippage: có xác nhận gián tiếp ở `08`; phần còn lại NEEDS VERIFICATION. Chưa có tác động thực thi vì `run_backtest.py` chưa đọc cấu hình | SYS-021 |
| DA-6 | Data loading | `load_csv` nhánh `unix_*` | P2 | `pd.to_numeric(..., errors="coerce")` ra float64; `unix_ns` vượt 2⁵³; epoch phân số được chấp nhận | SUSPECTED | SYS-013 |
| DA-7 | Performance | `source_inferred_dtypes`, `raw.copy()`, `intraday_gaps` | P2 | Parse hai lần mỗi cột giá; danh sách gap không giới hạn | SUSPECTED (chưa đo); validator được báo là vector hóa O(n) | SYS-023 |
| DA-8 | Data I/O | `data_loader.py::save_parquet` | P2 | `"raw" in path.parts` yếu; `os.link` không di động | NEEDS VERIFICATION (static-strong) | SYS-022 |
| IN-1 | Integration / Causality | `sessions.py::session_features`, docstring, `INDICATORS.md` | P0 (có điều kiện) | Docstring nói "availability time" với khoảng `[open, close)`; mã dùng `seconds >= start` và `seconds < end` | SUSPECTED; nâng thành P0 gate (xem C-01) | SYS-001 |
| IN-2 | Performance | `trend.py::parabolic_sar`, `market_structure.py::structure_breaks` | P1 | `data[[...]].iloc[i].isna().any()` trong vòng lặp tạo bản sao mỗi bước | NEEDS VERIFICATION (static-strong) | SYS-007 |
| IN-3 | Performance | `rma`, `atr`, `rsi`, `adx`, `supertrend`, `wma`, `aroon`, `confirmed_swings`, `dominant_cycle`, v.v. | P1 | Vòng lặp Python hoặc `rolling.apply`; ước lượng chục giây đến phút mỗi lần (chưa đo) | NEEDS VERIFICATION (cấu trúc static-strong; thời gian chưa đo) | SYS-007 |
| IN-4 | Validation | `tests/test_indicators.py`, `inspect_indicators.py` | P1 | `pd.testing.assert_frame_equal` mặc định; 80 nến, `window=3`; NaN không được kiểm prefix | SUSPECTED (cùng căn nguyên với ST-01) | SYS-004, SYS-019 |
| IN-5 | Numerics | `momentum.cci`, `volatility.bollinger_percent_b`, `bollinger_bandwidth`, `rolling_std` | P1 | `.replace(0, np.nan)` chỉ bắt đúng 0; cửa sổ phẳng với giá không biểu diễn chính xác có thể ra số rác | SUSPECTED | SYS-015 |
| IN-6 | Indicator semantics | `market_structure.py::previous_period_levels`, `daily_pivots` | P1 | `groupby(normalize()).agg().shift()`; thứ Hai lấy "ngày trước" là mảnh Chủ nhật | DESIGN LIMITATION (docstring thừa nhận) có rủi ro nghiên cứu | SYS-016 |
| IN-7 | Validation | `positive_window`, kiểm tham số float | P2 | `isinstance(window, int)` loại `np.int64`; `multiplier <= 0` không bắt NaN | NEEDS VERIFICATION (static-strong); cùng mẫu với ST-03 | SYS-026 |
| IN-8 | Performance | `volatility.garman_klass_volatility` | P2 | `.stack()` trên OHLC để kiểm dương | NEEDS VERIFICATION (static-strong) | SYS-027 |
| IN-9 | Tài liệu / kiến trúc | import lười `_utc_index`, sơ đồ thiếu cạnh, README, stub mô tả sai | P2 | Nêu cụ thể từng mục | Phần README: **CONFIRMED (E1)**; các phần còn lại NEEDS VERIFICATION | SYS-025 |
| IN-10 | Reproducibility | git status, `inspect_indicators.py` hardcode đường dẫn artifact bị `.gitignore` | P2 | Đường dẫn `data/processed/inspection-...parquet` bị loại bởi `.gitignore` | Phần working tree/lock: **CONFIRMED (E1)**; phần script: NEEDS VERIFICATION | SYS-002 |

### 3.2 Bảng vấn đề hợp nhất

Mức ưu tiên là mức của kiểm toán tổng hợp. Cột "Tác động toàn hệ thống" nêu thành phần của chuỗi DATA → INDICATORS → STRATEGY → ENGINE → EXECUTION → PORTFOLIO → METRICS → REPORTS bị ảnh hưởng.

#### P0: cổng phải xử lý trước khi dùng kết quả cho nghiên cứu

| ID | Vấn đề | Nguồn | Tác động toàn hệ thống | Trạng thái | Hành động đề xuất |
|---|---|---|---|---|---|
| SYS-001 | Quy ước nhãn thời gian (nhãn mở hay nhãn đóng) không được thống nhất và ghim bằng test giữa dữ liệu, `sessions` và engine | IN-1, CO-F6, `08` | DATA → INDICATORS → ENGINE. Có thể gây lệch một nến ở đặc trưng phiên, ORB, VWAP phiên; nếu lệch theo hướng dùng nến chưa đóng thì là look-ahead | SUSPECTED | Xác định nhãn thật của dataset, chốt một quy ước, ghim bằng test ở cả `sessions` lẫn engine; thêm tham số nhãn tường minh |
| SYS-002 | Kết quả không truy được về commit, dữ liệu, tham số, môi trường; mã chưa commit, phụ thuộc chưa khóa | ST-06, CO-F5, IN-10 | ENGINE → REPORTS. Không thể tái lập hoặc kiểm toán lại một kết quả đã công bố | CONFIRMED (phần working tree, lock); NEEDS VERIFICATION (nội dung `assumptions`) | Commit/tag; lock phụ thuộc; ghi provenance vào kết quả |
| SYS-003 | So sánh chạm SL/TP và làm tròn tick trên số thực | CO-F2 | EXECUTION → PORTFOLIO. Bỏ lỡ hoặc kích hoạt nhầm SL/TP ở đúng biên; lệch 1 tick với giá lớn | SUSPECTED | Chạy probe test trước; nếu xác nhận, chuẩn hóa về số nguyên tick |
| SYS-004 | Test nhân quả dùng dung sai ngầm nên bằng chứng "không look-ahead" chưa đáng tin | ST-01, IN-4, CO (test nhân quả của engine chỉ sửa nến cuối) | INDICATORS, ENGINE. Toàn bộ kết luận causal của chỉ báo dựa vào test này | SUSPECTED | `check_exact=True` mặc định; sửa nến ngẫu nhiên thay vì chỉ nến cuối |
| SYS-005 | Metadata dataset thật chưa xác nhận; chưa rõ engine có chặn dữ liệu chưa `ready_for_research` | DA-2, `08`, `00` (cạnh Engine → Validator) | DATA → ENGINE. Chạy dữ liệu chưa xác nhận `price_type`, `timestamp_kind`, `timeframe`, `tick_size` thì mọi giả định khớp lệnh vô nghĩa | NEEDS VERIFICATION | Chủ dự án xác nhận metadata có bằng chứng; test tích hợp chứng minh engine từ chối dữ liệu chưa sẵn sàng |

#### P1: phải xử lý trước khi chạy tích hợp dài hạn hoặc nghiệm thu toàn hệ thống

| ID | Vấn đề | Nguồn | Tác động toàn hệ thống | Trạng thái | Hành động đề xuất |
|---|---|---|---|---|---|
| SYS-006 | Đường mặc định của engine O(n²) ở 1,44M nến; kết quả giữ trạng thái mỗi nến; chiến lược mức tạo lệnh/event mỗi nến | CO-F1, ST-05 | STRATEGY → ENGINE → RESULT | NEEDS VERIFICATION (static-strong) | Đo; NumPy hóa vòng lặp; bỏ deep-copy; golden-master trước và sau |
| SYS-007 | `parabolic_sar`, `structure_breaks` O(n²); nhiều chỉ báo dùng vòng lặp Python | IN-2, IN-3 | INDICATORS | NEEDS VERIFICATION (static-strong cho O(n²); thời gian chưa đo) | Tính `valid` một lần; oracle bản cũ để đối chiếu |
| SYS-008 | **Mới.** Chiến lược gia tăng với `signal_history_limit` hữu hạn tính chỉ báo đệ quy/phụ thuộc đường đi trên cửa sổ cắt, nên giá trị chỉ báo khác với tính trên toàn lịch sử | Suy luận tích hợp từ CO-F1 và IN (tài liệu nói EMA/RMA có seed, SAR/SuperTrend là máy trạng thái) | INDICATORS ↔ STRATEGY ↔ ENGINE. Tối ưu hiệu năng bằng cửa sổ có thể đổi logic (rủi ro số 10 của đề bài) | SUSPECTED | Test tương đương giữa chạy cửa sổ và chạy toàn lịch sử; ghi tài liệu giới hạn cửa sổ tối thiểu |
| SYS-009 | Không có vòng đời strategy (reset) và không phản hồi vị thế/fill cho strategy | CO-F4 | STRATEGY ↔ ENGINE. Chạy lại cùng instance cho kết quả khác; strategy lệch trạng thái với engine | NEEDS VERIFICATION (static-strong) | `deepcopy`/`reset()` đầu mỗi run |
| SYS-010 | Lệnh vào bị từ chối khi gap phá SL/TP không được định lượng; có thể lạc quan | CO-F3 | ENGINE → PORTFOLIO → METRICS | DESIGN LIMITATION + thiếu quan sát | Mã lý do cấu trúc và bộ đếm trong kết quả |
| SYS-011 | Timestamp lệch lưới chỉ là cảnh báo | DA-1 | DATA | NEEDS VERIFICATION; cần chủ dự án quyết định chính sách | Nếu chủ dự án đồng ý, đưa vào `errors` |
| SYS-012 | **Mới.** Giao diện validator ↔ engine không thống nhất về gap trong ngày: validator chỉ cảnh báo, engine khớp ở nến quan sát tiếp theo bất kể khoảng cách | DA (mục F), `00` | DATA ↔ ENGINE. Tín hiệu cuối nến có thể khớp ở open sau một gap dài cùng ngày | NEEDS VERIFICATION | Ghi khoảng cách tín hiệu → khớp vào kết quả; không bắt buộc chặn (đúng chính sách đã chấp nhận) |
| SYS-013 | `load_csv(diagnostic=False)` trả NaN/NaT không raise; epoch phân số/`unix_ns` mất độ chính xác | DA-2, DA-6 | DATA | SUSPECTED | Raise ở chế độ không diagnostic; parse số nguyên |
| SYS-014 | Đơn vị và thông số công cụ: XAUUSD legacy so với registry; `point_size` không trong `SPECIFICATION_FIELDS`; `slippage_points` so với đơn vị giá; `pip_size` không dùng | DA-3, CO-F8, `08` | DATA → EXECUTION → PORTFOLIO. Sai bậc 100 đến 1000 nếu có đường nào đọc nhầm nguồn | NEEDS VERIFICATION | Một nguồn thông số duy nhất; test nhất quán. **Thành P0 trước bất kỳ lần chạy XAUUSD nào** |
| SYS-015 | Cửa sổ phẳng với giá không biểu diễn chính xác cho số rác thay vì NaN (CCI, Bollinger) | IN-5 | INDICATORS | SUSPECTED | Probe test; nếu xác nhận, ngưỡng epsilon hoặc phát hiện cửa sổ phẳng |
| SYS-016 | "Ngày trước" của thứ Hai là mảnh Chủ nhật trong pivot/previous-period | IN-6 | INDICATORS (không nằm trong chấp nhận gap ngày UTC) | DESIGN LIMITATION có rủi ro | Chủ dự án quyết định chính sách; `min_bars` tùy chọn |
| SYS-017 | **Mới.** Chưa có test tích hợp end-to-end và test bất biến kế toán trên chuỗi dài; test engine chạy chế độ lịch nghiêm ngặt trong khi production mặc định không lịch | CO (mục D, 13 mục), ST (mục D), DA (mục D) | Toàn chuỗi | NEEDS VERIFICATION | Bộ test ở mục 9 |
| SYS-018 | Helper `check_prefix_invariance`: input rỗng cho PASS, không kiểm tra index, từ chối `np.int64`, O(n²) mặc định, không có test cấp pipeline từ dữ liệu thô | ST-02, ST-03, ST-04 | VALIDATION | NEEDS VERIFICATION (static-strong) | Kiểm tra đầu vào; bộ cutoff lấy mẫu tất định; test pipeline |

#### P2: có thể cải thiện ở giai đoạn sau

| ID | Vấn đề | Nguồn | Hành động đề xuất |
|---|---|---|---|
| SYS-019 | Fixture chỉ báo đơn điệu, 80 nến, `window=3`; thiếu NaN một phần, thiếu tham chiếu độc lập cho ADX/RSI/SAR phía sell | IN-4 (hạn chế khác), IN (mục D) | Bổ sung fixture hai chiều và ví dụ tham chiếu công bố |
| SYS-020 | `except ValueError` làm luồng điều khiển; lỗi giá không nêu nến | CO-F7 | `OrderRejected` có mã; bọc lỗi kèm timestamp |
| SYS-021 | `config.yaml`: `include_swap`, `timeframe`, ngày, đơn vị slippage; `run_backtest.py` chưa đọc cấu hình | DA-5, `08` | Đồng bộ khi nối cấu hình vào `run_backtest.py` (lúc đó thành P1) |
| SYS-022 | `write_json` không atomic; `save_parquet` chốt chặn `raw` yếu, `os.link` không di động | DA-4, DA-8 | Ghi qua chuỗi + temp; so sánh với đường dẫn raw đã resolve |
| SYS-023 | Parse trùng, sao chép toàn chuỗi, danh sách gap không giới hạn ở loader | DA-7 | Đo trước; giới hạn danh sách (giữ số đếm) |
| SYS-024 | Benchmark: `assert` bỏ với `-O`, hằng số `True`, chỉ so lần lặp cuối, kịch bản không chạm chi phí/SL/TP | ST-07 | Tính `identical` thật; thêm kịch bản |
| SYS-025 | README, sơ đồ kiến trúc, mô tả stub, thông báo `run_backtest.py` lệch với thực tế | ST-08, CO-F8, IN-9 | Đồng bộ tài liệu |
| SYS-026 | Tham số `NaN`/`inf` không bị từ chối; `np.int64` bị từ chối (ở cả `_utils` lẫn `causality`) | IN-7, ST-03 | `numbers.Integral`, `np.isfinite` |
| SYS-027 | `garman_klass_volatility` dùng `.stack()` tốn bộ nhớ | IN-8 | So sánh trực tiếp |

### 3.3 Hạng mục NOT IMPLEMENTED (không tính là lỗi, không suy đoán là hoạt động)

| Hạng mục | Bằng chứng (E1) |
|---|---|
| `core/metrics.py` (equity curve, drawdown, thống kê hiệu suất) | `00`: "chỉ có docstring/import" |
| `core/data_manager.py` | `00` |
| `indicators/custom_indicators.py` | `00` |
| `strategies/first_strategy.py` | `00` |
| `run_backtest.py` nối cấu hình, mô phỏng, xuất báo cáo | `00`: chỉ in thông báo |
| `validation/`, walk-forward, sensitivity, chiến lược nghiên cứu hoàn chỉnh | `00`: không tồn tại |
| Lịch Forex đầy đủ (cuối tuần, lễ) | Giới hạn được chấp nhận theo chỉ thị, xem 6.3 |

Hệ quả: Phần IV mục 6 của đề (sai equity hoặc drawdown) chỉ kiểm tra được ở mức equity theo từng nến trong `portfolio.mark`; **drawdown chưa tồn tại** nên không có gì để kiểm.

---

## 4. Duplicated and Conflicting Findings

### 4.1 Nhóm trùng lặp (đã hợp nhất, giữ nguồn gốc)

| Cụm | Nguồn | Hợp nhất | Ghi chú về lệch mức ưu tiên |
|---|---|---|---|
| Tái lập, commit, lock | ST-06 (P1), CO-F5 (P1), IN-10 (P2) | SYS-002 | IN-10 xếp P2. Hợp nhất thành P0 gate vì ba báo cáo cùng thấy một nguyên nhân và nó chặn việc dùng kết quả cho nghiên cứu |
| Dung sai test prefix | ST-01 (P1), IN-4 (P1); CO mục D13 (test nhân quả của engine chỉ sửa nến cuối) | SYS-004 | Ba vị trí khác nhau (helper, test chỉ báo, test engine), cùng căn nguyên: bằng chứng nhân quả yếu |
| Hiệu năng O(n²) | ST-04, ST-05, CO-F1, IN-2, IN-3, DA-7 | SYS-006, 007, 018, 023 | Chia theo tầng: engine, chỉ báo, helper kiểm thử, loader. DA-7 xếp P2 vì validator vector hóa; không mâu thuẫn |
| Tài liệu lệch | ST-08, CO-F8, IN-9 | SYS-025 | Cùng một lỗi README (pyarrow, "1 bài test") được ba báo cáo nêu độc lập; tôi đã xác nhận trực tiếp từ `00` |
| Kiểu số nguyên `np.int64` | ST-03, IN-7 | SYS-026 | Cùng mẫu `isinstance(x, int)` ở `causality.py` và `_utils` (`positive_window`). Có thể là một thói quen lập trình chung, nên sửa đồng bộ |
| Nhãn thời gian | IN-1 (P0 có điều kiện), CO-F6 (P2) | SYS-001 | Xem C-01 |
| Cấu hình so với CostModel | DA-5, CO-F8, `08` | SYS-021, SYS-014 | `08` nêu `include_swap=true` và `slippage_points`; DA đọc file nhưng CO không đọc. Không mâu thuẫn, chỉ khác phạm vi |

### 4.2 Mâu thuẫn và điểm không nhất quán

Mỗi dòng gồm: (1) hai kết luận; (2) bằng chứng và nguồn; (3) nguyên nhân có thể; (4) cách kiểm chứng; (5) kết luận hiện tại.

| ID | (1) Hai kết luận liên quan | (2) Bằng chứng, nguồn | (3) Nguyên nhân có thể | (4) Cách kiểm chứng | (5) Kết luận hiện tại |
|---|---|---|---|---|---|
| C-01 | IN-1: nhãn thời gian ở `sessions` mâu thuẫn, **P0 có điều kiện**. CO-F6: ngữ nghĩa nhãn `AccountState`/`Fill` là **P2 DESIGN LIMITATION**. | IN-1: docstring "availability time" nhưng mã xét `[start, end)`. CO-F6: với nến nhãn open, `states[i].timestamp == data.index[i+1]`. `08`: `sessions` yêu cầu timestamp khả dụng, engine có thể dùng nhãn open. DA: `timestamp_kind` là trường metadata phải xác nhận. | Hai báo cáo nhìn hai phía của cùng một câu hỏi (nhãn mở hay đóng) mà không thấy phía kia. Không ai thấy nhãn thực của parquet EURUSD. | (a) Đọc `timestamp_kind` đã xác nhận trong `datasets.json`. (b) Test `session_features` với cùng dữ liệu gắn nhãn open và nhãn close. (c) Test engine: tín hiệu ở nến i khớp ở open của nến i+1 với cả hai quy ước. | **Chưa thể giải quyết.** Giữ ở P0 gate đến khi có bằng chứng nhãn của dữ liệu thật. Mức P2 của CO-F6 chỉ đúng nếu mọi lớp tiêu thụ ghép theo chỉ số nguyên. |
| C-02 | ST-05: không rõ engine tin chiến lược batch hay gọi lại trên từng prefix. CO-F1: engine gọi `generate_signal(prefix)` mặc định gọi `generate_signals(prefix)` với prefix cắt từ đầu. | CO-F1 trích `prefix = frame.iloc[start:i+1].copy(deep=True)`. ST-05 chỉ suy đoán từ cấu trúc benchmark. | ST không có `engine.py`. | Đọc `engine.py` và đếm số hàng truyền vào strategy ở n = 5k, 10k, 20k. | Câu hỏi mở của ST-05 được CO-F1 trả lời **theo hướng gọi lại trên prefix** (E2, chưa tự xác minh). Hệ quả: an toàn nhân quả đối với strategy (chỉ thấy quá khứ) nhưng O(n²) mặc định. |
| C-03 | CO mục D9: đa số test engine truyền `expected_timestamps=bars.index`, tức chạy **chế độ lịch nghiêm ngặt**. `00`/DA: chế độ **mặc định** của production là cảnh báo gap trong cùng ngày UTC, không lịch. | CO mục D9: `test_intraday_gaps` chỉ có 2 nến và 1 lệnh BUY. | Test viết với lịch tự suy từ dữ liệu để dễ kiểm soát. | Chạy bộ test engine ở chế độ mặc định, nhiều nến, nhiều lệnh (E2E-09). | Bằng chứng kiểm thử của engine **không phủ** chế độ mà production sẽ dùng. Gom vào SYS-017. |
| C-04 | DA-3 xếp mâu thuẫn `symbols.json` so với `datasets.json` là **P1**. `08`: `symbols.json` là legacy, engine không tin cậy; `00`: `Instrument.from_metadata` không đọc file này. | DA-3: XAUUSD `point_value 1e-05` so với `point_size 0.001`; `contract_size 100000` trong legacy (một giá trị đáng ngờ cho vàng). | Legacy chưa được xóa; không test nào cấm đọc lại nó. | Test nhất quán của DA-3; quét import để chắc chắn không mã nào đọc `symbols.json`. | Rủi ro **có điều kiện**. Giữ P1; thành P0 trước bất kỳ lần chạy XAUUSD nào. |
| C-05 | `config.yaml`: `include_swap=true` và `slippage_points: 2` (DA-5, `08`). `CostModel`: từ chối swap khác 0 và làm việc theo đơn vị giá (CO). | `08` điểm cần kiểm toán; CO-F8 ghi "chưa kết luận" vì không đọc file. | Cấu hình viết trước khi chốt phạm vi engine. | Khi nối `run_backtest.py` với cấu hình, chạy một lần với cấu hình hiện tại, kỳ vọng lỗi rõ ràng. | **Mâu thuẫn xác nhận ở mức tài liệu** (`08`), chưa có tác động thực thi. P2 cho đến khi cấu hình được nối. |
| C-06 | ST (mục F) cần xác nhận TP gap dùng **giá target** thay vì open, nhận xét "bất đối xứng với SL gap". CO-E coi đó là thiết kế đúng. CO-D4: EXIT pending khi giá mở gap qua TP lấy open (tốt hơn). | CO-E: gap SL dùng open; gap TP bị chặn ở target. | Chính sách thận trọng có chủ đích nhưng không đối xứng giữa các kiểu thoát. | Test khóa hành vi (CO-D4); ghi chính sách vào `BACKTEST_ENGINE.md`. | **DESIGN LIMITATION** thận trọng (đánh giá thấp lợi nhuận TP). Lưu ý: chiến lược dùng TP và chiến lược dùng EXIT sẽ bị đối xử khác nhau khi có gap thuận lợi. Cần ghi nhận khi so sánh chiến lược. |
| C-07 | DA-E: báo cáo của validator **đã ghi** git revision, trạng thái dirty, phiên bản phần mềm, hash mã. CO-F5: kết quả của engine **không ghi** provenance. | DA-E (E2) và CO-F5 (E2). | Provenance được xây ở lớp dữ liệu nhưng chưa được kế thừa lên lớp mô phỏng. | Kiểm tra `BacktestResult.assumptions` so với báo cáo validator. | Không nhất quán giữa hai lớp. Có thể tái dùng cơ chế đã có ở lớp dữ liệu. Gom vào SYS-002. |
| C-08 | IN-A: chỉ báo không có look-ahead (không `shift(-n)`, không `center=True`, không chuẩn hóa toàn lịch sử). `08` và ST-02: prefix invariance của đầu vào không bảo đảm toàn pipeline nhân quả; cột tính sẵn/nguồn ngoài có thể rò rỉ. | `08`: "kiểm tra rò rỉ từ cột feature đã tính sẵn". | Hai phát biểu đúng ở hai tầng khác nhau: từng hàm so với pipeline. | Test cấp pipeline từ dữ liệu thô (E2E-12, mục 9). | Chỉ báo **riêng lẻ** đáng tin hơn (E2); **pipeline** chưa được kiểm chứng. Không mâu thuẫn, nhưng không được dùng kết luận của tầng này thay cho tầng kia. |
| C-09 | DA (mục F): validator chỉ cảnh báo gap trong ngày; engine khớp "ở nến có dữ liệu kế tiếp" (`00`). | Không có báo cáo nào xem hai phía cùng lúc. | Hai chính sách đúng riêng lẻ nhưng nối nhau tạo ra khoảng cách khớp lệnh lớn sau gap trong ngày. | E2E-09: mô phỏng thiếu 3 nến giữa ngày. | **Chưa thể xác minh.** Theo chính sách đã chấp nhận, đây không bị coi là lỗi nghiêm trọng, nhưng cần ghi nhận (SYS-012). |

---

## 5. Cross-Module Integration Analysis

### 5.1 Chuỗi DATA → INDICATORS → STRATEGY → ENGINE → EXECUTION → PORTFOLIO → METRICS → REPORTS

Cột "Đã được xem" cho biết báo cáo nào thấy mã của mắt xích đó. Phần lớn nội dung dưới đây là E2 từ báo cáo thứ cấp.

| Giao diện | Hợp đồng kỳ vọng (vào/ra, kiểu, timestamp, đơn vị) | NaN, warm-up, thời điểm khả dụng của tín hiệu | Điều kiện thất bại | Test hiện có (theo báo cáo) | Test tích hợp còn thiếu | Trạng thái |
|---|---|---|---|---|---|---|
| **DATA → INDICATORS** | `DataFrame` index `DatetimeIndex` UTC, duy nhất, tăng dần; cột OHLC float64. `_utils` từ chối index sai, `inf`, OHLC sai quan hệ (IN). | Không điền NaN; EMA/RMA khởi tạo lại sau NaN (IN). Loader để NaN/NaT cho token lỗi trong chế độ không diagnostic (DA-2). Loader đảm bảo UTC; nhãn mở/đóng phụ thuộc `timestamp_kind` (chưa xác nhận trên dữ liệu thật). | Chỉ báo fail-closed khi index/giá sai (IN). Dữ liệu NaN từ loader không bị chặn trước chỉ báo ở chế độ không diagnostic (DA-2, SUSPECTED). | `test_data_loader`, `test_data_validator`, `test_intraday_gaps`, `test_indicators` (riêng từng lớp) | Parquet thật → validator → chỉ báo, với NaN một phần, DST, thiếu nến trong ngày | NEEDS VERIFICATION |
| **INDICATORS → STRATEGY** | Chỉ báo nhận `Series`/`DataFrame` và trả cùng index. `BaseStrategy.generate_signals(data)` trả `signal` và `exit` cùng index (CO). | Warm-up: giá trị đầu NaN; `sessions` yêu cầu timestamp khả dụng nhưng engine có thể dùng nhãn open (`08`); cột tính sẵn không được bảo vệ (`08`, ST-02). Chiến lược gia tăng bị cắt cửa sổ có thể đổi giá trị chỉ báo đệ quy (SYS-008). | `BaseStrategy` kiểm `signals.index.equals(completed_data.index)` (CO). Không có kiểm cho cột nhiễm tương lai. | Prefix-invariance cho mọi hàm public (IN, với dung sai mặc định); không có test strategy thật (strategy mẫu chưa tồn tại) | Chiến lược mẫu dùng chỉ báo thật trên dữ liệu thô, test pipeline và test cắt cửa sổ | NEEDS VERIFICATION |
| **STRATEGY → ENGINE** | Engine truyền `prefix` (bản sao các nến đã hoàn tất), nhận `signal` (+1/−1/0), `exit`, tùy chọn `sl`/`tp` (CO). Tín hiệu cuối nến i, khớp ở open của nến có dữ liệu kế tiếp, kèm chốt chặn `opening < order.submitted_at` (CO). | Tín hiệu ở nến cuối bị bỏ (CO). Không có reset strategy, không phản hồi vị thế/fill cho strategy (SYS-009). | Strategy trả index sai → lỗi. Strategy mức (`close > x` trả 1 liên tục) tạo `Order` và event "rejected" mỗi nến khi đang giữ vị thế (CO-F1). | `test_engine` (4 nến, tối đa một giao dịch), test không sửa đầu vào, test replay `==` | Nhiều giao dịch liên tiếp; tái dùng instance; chiến lược batch và gia tăng cho kết quả giống nhau | NEEDS VERIFICATION |
| **ENGINE → EXECUTION (CostModel)** | Engine gọi `CostModel` để suy Bid/Ask từ một luồng giá (Mid/Bid/Ask) và tính giá khớp; spread và slippage nằm trong giá khớp, commission mỗi phía (CO). Giá làm tròn tick bất lợi. | Tỷ giá as-of `searchsorted(side="right") - 1`, không nội suy; tỷ giá intrabar dùng đầu nến (CO). | `positive(value, "executable price")` ném `ValueError` chung nếu giá ≤ 0 (CO-F7). | `test_cost_model`, `test_execution`; số tính tay (CO) | Chạm đúng biên (SYS-003); BTC; chi phí lớn; quy đổi quote khác account | NEEDS VERIFICATION |
| **EXECUTION → PORTFOLIO** | `Fill` có `price`, `quantity`, trường chi phí chỉ để đối chiếu. Portfolio dùng tài sản bảo đảm 100% notional, không đòn bẩy; P/L realized/unrealized; vị thế cuối mẫu giữ nguyên (CO). | `portfolio.open` kiểm SL/TP bao quanh giá khớp, nếu không `ValueError` bị engine bắt thành event "rejected" (CO-F3). | Từ chối lệnh không có bộ đếm (SYS-010). | `test_portfolio`, ví dụ tính tay 103,1 / 108,9 → net 52 (CO) | Bất biến kế toán trên chuỗi ngẫu nhiên: Σ gross − Σ commission = Δ balance, equity = balance + unrealized | NEEDS VERIFICATION |
| **PORTFOLIO → METRICS** | `AccountState` theo từng nến; `core/metrics.py` | — | — | — | — | **NOT IMPLEMENTED** |
| **METRICS → REPORTS** | `run_backtest.py` chỉ in thông báo; không có xuất báo cáo nghiên cứu | — | — | — | — | **NOT IMPLEMENTED** |

### 5.2 Điểm tích hợp quan trọng

1. **Nhãn thời gian (SYS-001).** Chuỗi chỉ đúng khi mọi lớp cùng hiểu "timestamp của nến" là thời điểm mở hay đóng. Dữ liệu (`timestamp_kind`), `sessions`, engine (`order.submitted_at`, `AccountState.timestamp`) đều có phát biểu riêng. Không có test nào ghim quy ước này xuyên qua cả ba.
2. **Warm-up và cắt cửa sổ (SYS-008).** Đây là phát hiện mới của kiểm toán tổng hợp. Chỉ báo đệ quy (EMA/RMA, ATR, RSI) phụ thuộc điểm bắt đầu tính; chỉ báo máy trạng thái (Parabolic SAR, SuperTrend) phụ thuộc cả đường đi. Một strategy gia tăng với `signal_history_limit = L` tính lại chỉ báo trên L nến cuối, nên có thể cho giá trị khác với tính trên toàn lịch sử. Đối với EMA sai lệch có thể giảm dần, nhưng với máy trạng thái trạng thái xu hướng có thể khác vĩnh viễn. Đây là suy luận từ tài liệu, chưa có ai chạy; mức SUSPECTED.
3. **Đơn vị giá và khối lượng (SYS-014).** CO nói số lượng và commission tính theo "đơn vị khai báo" và `Instrument.pip_size` không được dùng; DA thấy `contract_size` của XAUUSD trong tệp legacy là 100000 (đáng ngờ). Chưa ai trình bày đầy đủ cách `quantity`, `contract_size` và tiền tệ quote/account kết hợp thành P/L. Tôi không thể kết luận đúng hay sai.
4. **Tỷ giá as-of.** `searchsorted(side="right") - 1` dùng tỷ giá có nhãn **bằng** thời điểm truy vấn. Nếu nhãn tỷ giá là nhãn open nhưng giá trị là close của chính nến đó, đây là look-ahead (ST đã yêu cầu xác nhận, CO nói "tỷ giá đã công bố"). Kiểm chứng gắn với SYS-001.
5. **Cổng dữ liệu (SYS-005).** `00` có cạnh Engine → Validator nhưng DA không thấy engine, CO không thấy validator. Chưa ai xác nhận engine từ chối dữ liệu `ready_for_research=False`.
6. **Quy ước tín hiệu BaseStrategy ↔ Engine.** CO thấy cả hai phía và không nêu mâu thuẫn: tín hiệu `{signal, exit}`, `BaseStrategy` kiểm index, engine khớp ở nến kế tiếp. Trong 4 báo cáo không có mâu thuẫn cấp quy ước nào được nêu ở điểm này, và tôi cũng không có bằng chứng ngược lại.
7. **Phí và đơn vị giữa Execution và Portfolio.** CO thấy cả hai phía và kết luận chi phí chỉ nằm trong giá khớp, commission mỗi phía, các trường chi phí trong `Fill` chỉ để đối chiếu, không có double-charge (E2, chưa tự xác minh).

---

## 6. Critical Correctness Risks

### 6.1 Rủi ro theo thứ tự ưu tiên của đề bài (Phần IV)

| # | Rủi ro | Những gì được biết (nguồn) | Trạng thái | Liên kết |
|---|---|---|---|---|
| 1 | Look-ahead bias | Chỉ báo riêng lẻ: không thấy `shift(-n)`/`center=True` (IN, E2). Engine: strategy chỉ thấy bản sao prefix (CO, E2). Nhưng nhãn thời gian chưa thống nhất; test prefix dung sai lỏng | NEEDS VERIFICATION | SYS-001, 004 |
| 2 | Rò rỉ đặc trưng tương lai | Cột tính sẵn và trạng thái bên ngoài không được kiểm (ST-02, `08`); `dominant_cycle` dùng cửa sổ quá khứ từng bar (IN, E2) | DESIGN LIMITATION (quy trình) | SYS-018 |
| 3 | Sai thời điểm tín hiệu và khớp lệnh | Thiết kế: tín hiệu cuối nến, khớp ở open nến kế tiếp có chốt chặn (CO, E2). Chưa xác minh sau gap trong ngày | NEEDS VERIFICATION | SYS-001, 012 |
| 4 | Sai Bid/Ask hoặc chi phí | Bid/Ask suy ra từ một luồng giá, không double-charge (CO, E2). Nguy cơ làm tròn tick với giá lớn | SUSPECTED (một phần) | SYS-003 |
| 5 | Sai SL/TP và gap | SL ưu tiên, gap SL ở open, gap TP ở target (CO, E2). Thiếu test gap SHORT ở cấp engine; lệnh vào bị từ chối khi gap | NEEDS VERIFICATION | SYS-003, 010, 017 |
| 6 | Sai P/L, equity, drawdown | Ví dụ tính tay khớp (CO, E2). Drawdown NOT IMPLEMENTED | NEEDS VERIFICATION; phần drawdown NOT IMPLEMENTED | SYS-017 |
| 7 | Không nhất quán khối lượng, contract size, tiền tệ | Chưa có mô tả hoàn chỉnh; `pip_size` không dùng; dữ liệu legacy XAUUSD mâu thuẫn | NEEDS VERIFICATION | SYS-014 |
| 8 | Sai warm-up hoặc trạng thái chỉ báo | Công thức warm-up đối chiếu tay đúng (IN, E2); nhưng cửa sổ cắt của chiến lược gia tăng chưa ai xét | SUSPECTED | SYS-008 |
| 9 | Không tái lập | Không dùng ngẫu nhiên, test replay `==` (CO, E2). Nhưng không truy xuất nguồn gốc; state strategy rò rỉ giữa các lần chạy | FAIL cho truy xuất; NEEDS VERIFICATION cho tính tất định | SYS-002, 009 |
| 10 | Tối ưu hóa đổi logic | Chưa có tối ưu nào được thực hiện. Rủi ro tương lai: cửa sổ cắt, NumPy hóa vòng lặp | Rủi ro dự phòng | SYS-006, 007, 008 |

### 6.2 Điểm thiết kế đã đúng theo bằng chứng thứ cấp (nên bảo toàn)

- Tách tín hiệu cuối nến và khớp ở open nến có dữ liệu kế tiếp, kèm kiểm tra chống khớp trước thời điểm gửi lệnh.
- Bid/Ask suy ra từ một luồng giá; spread và slippage nằm trong giá khớp; commission mỗi phía; tick làm tròn theo hướng bất lợi.
- SL ưu tiên khi cùng chạm kèm cờ `ambiguous`; SL/TP kiểm tra ở phía giá thanh lý.
- Kế toán dự trữ 100% notional, không đòn bẩy; vị thế cuối mẫu giữ nguyên và được đánh giá.
- Metadata fail-closed; không sort, drop, fill, nội suy dữ liệu; băm SHA256 file raw trước và sau; Parquet không ghi đè.
- Chỉ báo fail-closed ở `_utils`; swing và structure chỉ phát tại bar xác nhận; `session_vwap` đòi `volume_kind` tường minh.
- `causality.py`: deep copy trước khi gọi builder; so sánh nghiêm kiểu; docstring nói thẳng đây chỉ là bằng chứng trên mẫu.

### 6.3 Giới hạn được chấp nhận (không coi là lỗi)

| Giới hạn | Nguồn chấp nhận | Hệ quả cần ghi nhận khi diễn giải kết quả |
|---|---|---|
| Chỉ cảnh báo khoảng thiếu nến giữa hai timestamp liên tiếp cùng ngày UTC; bỏ qua khoảng qua ngày UTC, cuối tuần, lễ; không bắt buộc lịch Forex đầy đủ | Đề bài + `00` (chỉ thị cụ thể ưu tiên hơn quy tắc gốc ở `00B`) | Khoảng cách khớp lệnh sau gap qua ngày không bị cảnh báo; chỉ báo có cửa sổ quanh cuối tuần không được gắn cờ |
| Engine một công cụ, một vị thế, không đòn bẩy | Đề bài | Không kiểm danh mục, ký quỹ, margin call |
| Không có swap | `CostModel` từ chối swap khác 0 | Chi phí giữ qua đêm không được mô phỏng |
| Vị thế cuối mẫu không bị ép đóng | Thiết kế (CO-E) | Equity cuối mẫu bao gồm lãi lỗ chưa thực hiện |
| `expected_timestamps` là chế độ lịch tùy chọn, chặt hơn mặc định | `00` | Không bắt buộc |
| `core/__init__.py`, `strategies/__init__.py` rỗng; `BaseStrategy.generate_signals` raise `NotImplementedError` | `00` | Không phải lỗi |

---

## 7. Performance and Scalability

Mục tiêu: dữ liệu dài hạn khoảng 1,44 triệu nến. **Không có phép đo nào** (E0 không tồn tại). Mọi con số thời gian và bộ nhớ dưới đây là ước lượng của báo cáo nguồn. Tôi chỉ kiểm tra lại phần số học của các ước lượng.

### 7.1 Kiểm tra số học các ước lượng

| Ước lượng nguồn | Phép tính lại | Kết quả |
|---|---|---|
| ST-04, CO-F1: Σ i = n²/2 ≈ 1,04×10¹² hàng với n = 1,44×10⁶ | (1,44×10⁶)² / 2 = 1,0368×10¹² | Khớp |
| CO-F1: 5 cột float64 ≈ 40 TB lưu lượng | 1,0368×10¹² × 5 × 8 B ≈ 4,1×10¹³ B ≈ 41 TB | Khớp (cùng bậc) |
| IN-2: mỗi bản sao `data[["high","low","close"]]` khoảng 35 MB | 1,44×10⁶ × 3 × 8 B ≈ 34,6 MB | Khớp |
| IN-2: tổng cỡ 5×10¹³ byte | 1,44×10⁶ lần × 34,6 MB ≈ 5,0×10¹³ B | Khớp |
| CO-F1: đường gia tăng 251 µs/nến, khoảng 6 phút | 1,44×10⁶ × 251×10⁻⁶ s ≈ 361 s ≈ 6,0 phút | Khớp; nhưng 251 µs lấy từ tài liệu chưa tái lập |
| CO-F1: quét 100 cấu hình ≈ 10 giờ | 100 × 6 phút = 600 phút = 10 giờ | Khớp |

Số học nhất quán. Đây **chỉ** chứng minh các con số tự nhất quán, không chứng minh chúng phản ánh thực tế. ST-07 cho biết `benchmark_engine.py` chưa từng được chạy trong hồ sơ, còn CO-F1 dựa vào số benchmark trong `BACKTEST_ENGINE.md` mà CO cũng ghi là chưa tái lập. Hai báo cáo không mâu thuẫn nhưng cùng dựa vào cùng một nguồn số chưa kiểm chứng.

### 7.2 Các đường có rủi ro

| Đường | Độ phức tạp theo mã trích | Ước lượng nguồn | Trạng thái | ID |
|---|---|---|---|---|
| Engine, strategy mặc định (`signal_history_limit=None`) | O(n²) thời gian; sao chép prefix mỗi nến | Hàng giờ mỗi lần chạy (CO: 4–5 giờ ngoại suy) | NEEDS VERIFICATION (static-strong) | SYS-006 |
| Engine, đường gia tăng (`signal_history_limit` nhỏ) | Gần O(n) | ≈ 6 phút/lần (CO, từ tài liệu) | NOT VERIFIED | SYS-006 |
| Bộ nhớ kết quả (`AccountState` mỗi nến, `events`, `orders`) | O(n) với hằng số lớn | Hàng trăm MB đến hơn 1 GB (CO, ước lượng) | NOT VERIFIED | SYS-006 |
| `parabolic_sar`, `structure_breaks` | O(n²) | Hàng giờ (IN, ước lượng) | NEEDS VERIFICATION (static-strong) | SYS-007 |
| `rma`, `atr`, `rsi`, `adx`, `supertrend`, `wma`, `aroon`, `confirmed_swings`, `dominant_cycle` | O(n) nhưng vòng lặp Python | Chục giây đến phút mỗi lần (IN, chưa đo) | NEEDS VERIFICATION | SYS-007 |
| Loader/validator | O(n), vector hóa; sao chép chuỗi; parse trùng | Rủi ro thấp (DA, chưa đo) | SUSPECTED | SYS-023 |
| `check_prefix_invariance` mặc định mọi prefix | O(n²) cộng deep-copy | Không chạy được ở quy mô thật (ST-04) | NEEDS VERIFICATION (static-strong) | SYS-018 |

### 7.3 Nhận xét tích hợp

- Một lần chạy nghiên cứu thật gồm chỉ báo, engine, và các lần quét tham số. Chi phí nhân lên: nếu `parabolic_sar` thuộc chiến lược, nó nằm trong vòng lặp của strategy mặc định (tính lại trên từng prefix), tạo thêm một tầng O(n) hoặc O(n²) tùy thuộc cách gọi.
- `inspect_indicators.py` chạy trên lát 10.080 dòng (IN-2), nên smoke test hiện có không bắt được O(n²).
- Không đề xuất tối ưu trước khi có golden-master (mục 9.4): rủi ro số 10 của đề (tối ưu đổi logic) là có thật, đặc biệt với SYS-008.
- `pyproject.toml` có `--strict-markers` và không đăng ký marker `slow` (E1, xem 12.2). Bất kỳ test hiệu năng nào dùng `@pytest.mark.slow` như các báo cáo đề xuất sẽ lỗi ở bước thu thập nếu chưa đăng ký marker.

---

## 8. Reproducibility

| Khía cạnh | Bằng chứng | Trạng thái |
|---|---|---|
| Phiên bản mã | Git status: 6 file `M` và 33 file `??` (E1, `00`); báo cáo thu thập trên working tree, không phải snapshot sạch | **FAIL** (CONFIRMED E1) |
| Phụ thuộc | `numpy>=1.26,<3`, `pandas>=2.2,<4`, `pyarrow>=23,<40`; không có lock; README tự nêu chưa phải tệp khóa; chỉ một tổ hợp được kiểm (Python 3.15.2, pandas 3.1.1, numpy 2.5.5) trong khi `requires-python>=3.11` (E1) | **FAIL** cho nghiên cứu cần tái lập chính xác |
| Dữ liệu | Validator ghi SHA256 file raw và so `raw_unchanged` (DA-E, E2). Engine không ghi hash dữ liệu (CO-F5) | Chia đôi: lớp dữ liệu tốt, lớp mô phỏng thiếu |
| Tham số và tên chiến lược | Không có trong `assumptions` (CO-F5, E2) | NEEDS VERIFICATION |
| Phiên bản thư viện trong kết quả | Validator ghi phiên bản phần mềm (DA-E); engine không (CO-F5) | Không nhất quán (C-07) |
| Tính tất định trong một lần chạy | Không dùng ngẫu nhiên; test replay `==` (CO-E, E2) | NOT VERIFIED (không có E0) |
| Tái dùng instance strategy | Không có reset; lần chạy thứ hai có thể khác (CO-F4, E2) | NEEDS VERIFICATION |
| Số test | "296 passed" tự báo cáo, không có stdout trong tay các auditor | NOT VERIFIED |
| Truy xuất giả định | `assumptions` có `metadata`, `costs`, `quantity`, `initial_capital`, `execution` (CO-F5, E2) | PASS WITH LIMITATIONS về nội dung đã có; thiếu các trường trên |
| Script hỗ trợ | `inspect_indicators.py` hardcode artifact trong `data/processed/` mà `.gitignore` loại (IN-10); benchmark chưa chạy (ST-07) | NEEDS VERIFICATION |
| Metadata thật | `08`: chưa xác nhận đầy đủ | Chặn nghiên cứu theo thiết kế (hành vi đúng) |

---

## 9. Missing Integration Tests

**Quan trọng:** phần này chỉ là thiết kế. Không có test nào dưới đây đã được viết hay chạy trong cuộc kiểm toán này. Mọi giá trị kỳ vọng phải được tính bằng một oracle độc lập từ quy ước trong `BACKTEST_ENGINE.md`, **không** được lấy từ đầu ra của engine rồi dán lại.

### 9.1 Nguyên tắc chung

1. **Oracle độc lập.** Một script thuần Python (không import engine, tối đa khoảng 80 dòng) tính giá khớp, P/L, commission, equity từ nến và quy ước đã nêu. Test so engine với oracle bằng đẳng thức chính xác khi phép tính trùng nhau, hoặc dung sai tường minh khi khác phép toán.
2. **Dữ liệu tổng hợp tất định.** Seed cố định, số nhỏ dễ tính tay.
3. **Hai chế độ lịch.** Mỗi kịch bản chạy cả `expected_timestamps=index` (nghiêm ngặt) và chế độ mặc định (xem C-03).
4. **Test có kiểm tra nhãn thời gian.** Mỗi kịch bản chạy với dữ liệu gắn nhãn open và nhãn close, trừ khi SYS-001 đã chốt quy ước duy nhất.

### 9.2 Kịch bản end-to-end (OHLC → equity)

| ID | Kịch bản | Mục đích | Kỳ vọng (thiết kế, chưa chạy) | Liên quan |
|---|---|---|---|---|
| E2E-01 | Chiến lược đơn giản: BUY khi điều kiện A, SELL khi điều kiện B, thoát bằng TP; 5–8 nến H1 | Round trip có chi phí | Giá khớp BUY = Mid(open nến kế tiếp) + s/2 + slippage (bất lợi), làm tròn tick bất lợi; commission hai phía; P/L khớp oracle | SYS-003, 017 |
| E2E-02 | SELL mở vị thế, đóng bằng SL | Đối xứng long/short | SELL khớp ở Bid, thoát ở phía Ask; kết quả đối xứng E2E-01 khi đảo gương dữ liệu | SYS-017 |
| E2E-03 | Chuỗi tín hiệu HOLD (0) | Không có lệnh, không có thay đổi | Không có `Order`/`Fill`/event; equity = vốn đầu ở mọi nến; không chi phí | SYS-006, 017 |
| E2E-04 | Nến chạm cả SL lẫn TP | SL ưu tiên | Thoát tại SL; sự kiện có cờ `ambiguous` | CO-E |
| E2E-05 | Gap qua SL (long và short), gap qua TP | Gap | Gap SL: khớp ở open; gap TP: bị chặn ở target (chính sách hiện tại); khóa hành vi bằng test (CO-D4) | C-06 |
| E2E-06 | Gap làm SL/TP không còn bao quanh giá khớp tại nến vào lệnh | Lệnh bị từ chối | Event có mã lý do; bộ đếm tổng hợp trong kết quả (sau khi sửa SYS-010) | SYS-010 |
| E2E-07 | EXIT đang chờ cùng nến với SL/TP | Thứ tự xử lý | Không đóng hai lần; thứ tự đúng như tài liệu | CO-D3 |
| E2E-08 | Tín hiệu ở nến cuối; vị thế còn mở cuối mẫu | Giao dịch cuối mẫu | Tín hiệu ở nến cuối bị bỏ; vị thế mở không bị ép đóng; equity gồm unrealized | CO-E |
| E2E-09 | Khoảng nghỉ: (a) thiếu 3 nến giữa ngày UTC; (b) nghỉ qua cuối tuần | Chính sách gap đã chấp nhận | (a) validator cảnh báo; engine khớp ở open nến quan sát tiếp theo và ghi khoảng cách; (b) không cảnh báo, kết quả đúng | C-09, SYS-012 |
| E2E-10 | Timestamp lệch lưới (giây = 30) với metadata đã xác nhận | Dữ liệu hỏng | Sau khi chủ dự án chốt chính sách, `errors` khác rỗng (SYS-011) | SYS-011 |
| E2E-11 | Chiến lược dùng SMA có warm-up | Warm-up | Không có tín hiệu trước khi đủ cửa sổ; chỉ số nến tín hiệu đầu tiên khớp oracle; NaN một phần (chỉ `close` hoặc chỉ `high` thiếu) được xử lý fail-closed | SYS-017, 019 |
| E2E-12 | **Prefix invariance cấp pipeline:** builder dựng toàn bộ đặc trưng từ dữ liệu thô, so `check_exact=True` ở bộ cutoff lấy mẫu (biên cửa sổ ±1, đổi ngày UTC, đầu phiên, seed ngẫu nhiên) | Rò rỉ tương lai | Không khác biệt. Kèm **mutation test**: một builder cố ý rò rỉ (hàng i phụ thuộc hàng i+1) phải bị bắt | SYS-004, 018 |
| E2E-13 | Chuỗi ngẫu nhiên dài (50 seed) với gap, SL/TP, tỷ giá khác đồng tiền | Bất biến kế toán | Các bất biến ở 9.3 | SYS-017 |
| E2E-14 | Hai lần chạy cùng instance và hai lần chạy instance mới | Tái lập | `a == b` từng bit cho `orders/fills/trades/states/events`; sau khi sửa SYS-009 | SYS-009 |
| E2E-15 | Cùng dữ liệu gắn nhãn open rồi nhãn close | Quy ước nhãn | `session_features`, thời điểm khớp, `AccountState.timestamp` nhất quán với quy ước đã chốt | SYS-001 |
| E2E-16 | Kết quả ghi provenance | Truy xuất | `assumptions` có hash dữ liệu, tên và tham số strategy, phiên bản thư viện, git revision và cờ dirty | SYS-002 |
| E2E-17 | Dữ liệu `ready_for_research=False` đi vào engine | Cổng dữ liệu | Engine từ chối với lỗi rõ ràng | SYS-005 |
| E2E-18 | Quote khác account; tỷ giá đổi giữa nến | FX as-of | Không dùng tỷ giá có nhãn sau thời điểm truy vấn; thoát intrabar dùng tỷ giá đầu nến | SYS-001, 014 |
| E2E-19 | SL đặt đúng lưới tick (chạm đúng biên); giá BTC cỡ 10⁵ với tick 0,01 | Float và tick | Chạm đúng biên thì kích hoạt; giá trên lưới không bị dịch 1 tick khi slippage = 0 | SYS-003 |
| E2E-20 | Chiến lược gia tăng chạy với `signal_history_limit = L` so với chạy trên toàn lịch sử | Trạng thái chỉ báo | Tín hiệu giống nhau từ chỉ số đủ warm-up; nếu khác, ghi tài liệu giới hạn L tối thiểu | SYS-008 |

**Ví dụ tính tay cho E2E-01 (minh họa quy ước, phải đối chiếu lại với `BACKTEST_ENGINE.md` trước khi dùng):** dữ liệu Mid, tick 0,01, spread s = 0,10, slippage 0,05 bất lợi, số lượng 1, đồng tiền quote bằng account (tỷ giá 1). Tín hiệu BUY cuối nến 0; nến 1 mở Mid = 100,30. Ask = 100,30 + 0,05 = 100,35; cộng slippage bất lợi 0,05 thành 100,40 (đã nằm trên lưới tick). Kiểm chạm SL/TP của vị thế long dùng giá Bid: Bid_high = high − s/2, Bid_low = low − s/2. Nếu TP = 102,00 và nến 2 có high = 102,20 thì Bid_high = 102,15 ≥ 102,00, TP kích hoạt. Giá thoát theo chính sách hiện tại (gap TP ở target) là 102,00; **không xác định được từ báo cáo nguồn** liệu slippage có áp dụng cho thoát TP hay không; nếu `BACKTEST_ENGINE.md` không nêu, đó là một lỗ hổng tài liệu cần ghi nhận. P/L gộp = (giá thoát − 100,40) × 1; trừ commission hai phía.

### 9.3 Bất biến tài khoản (kiểm trên mọi kịch bản, đặc biệt E2E-13)

| ID | Bất biến |
|---|---|
| INV-01 | `balance_cuối − vốn_đầu = Σ gross_pnl(giao dịch đã đóng) − Σ commission(đã trả, kể cả phí mở của vị thế còn mở)` |
| INV-02 | `equity = balance + unrealized` ở mọi `AccountState` (định nghĩa tài sản bảo đảm theo tài liệu) |
| INV-03 | Không có fill với thời gian nhỏ hơn `order.submitted_at`; fill vào lệnh ở open của nến sau nến tín hiệu |
| INV-04 | Tối đa một vị thế tại một thời điểm; không đòn bẩy (vốn dự trữ không vượt vốn khả dụng theo tài liệu) |
| INV-05 | `net_pnl = gross_pnl − commission` cho từng giao dịch; Σ net của các giao dịch đã đóng = Δ balance khi phẳng |
| INV-06 | Giá khớp nằm trên lưới tick và ở phía bất lợi so với Mid |
| INV-07 | Giá thoát bởi SL/TP không tốt hơn mức SL/TP (trừ EXIT thị trường theo tài liệu) |
| INV-08 | Số `AccountState` bằng số nến đã xử lý theo tài liệu |
| INV-09 | Hai lần chạy cùng đầu vào cho kết quả bằng nhau từng bit |
| INV-10 | Đầu vào (`DataFrame`) không bị sửa: hash trước và sau bằng nhau |

### 9.4 Benchmark (chỉ thiết kế)

| ID | Quy mô | Đo | Tiêu chí đề xuất (chủ dự án chốt lại) |
|---|---|---|---|
| BM-01 | 10.000 nến | thời gian tường, đỉnh bộ nhớ (`tracemalloc`) cho: chỉ báo riêng, engine đường gia tăng, engine đường mặc định | Đường cơ sở; dùng làm golden-master cho tối ưu |
| BM-02 | 100.000 nến | như trên | Độ dốc log-log giữa 10k và 100k gần 1 cho đường gia tăng; khoảng 2 nghĩa là O(n²) |
| BM-03 | 1.000.000 nến (nếu môi trường cho phép) | như trên, kèm kích thước `BacktestResult` | Hoàn thành trong thời gian chủ dự án chấp nhận; đỉnh bộ nhớ trong giới hạn máy |
| BM-04 | 1,44 triệu nến thật | một lần chạy tích hợp đầy đủ | Chỉ sau khi các cổng P0 đóng |

Mỗi benchmark phải: (a) đối chiếu đầu ra đầy đủ giữa bản trước và sau tối ưu bằng đẳng thức chính xác (không dùng `approx`, vì cùng chuỗi phép tính phải ra cùng bit); (b) chạy nhiều lần và so các lần với nhau, không chỉ lần cuối; (c) không dùng `assert` làm bước kiểm duy nhất (bị bỏ với `python -O`); (d) đăng ký marker `slow` trong `pyproject.toml`.

---

## 10. Prioritized Remediation Backlog

Nguyên tắc: sửa tối thiểu, bảo toàn thiết kế đang đúng (mục 6.2), xác minh bằng probe test **trước** khi sửa các mục SUSPECTED. Một mục SUSPECTED mà probe cho thấy không có lỗi thì đóng thành FALSE POSITIVE và không sửa mã. Mọi tối ưu hiệu năng phải có golden-master trước.

### 10.1 P0: trước khi dùng kết quả backtest cho nghiên cứu

| ID | Module / file | Mô tả | Bằng chứng | Hướng sửa | Regression test | Phụ thuộc | Điều kiện nghiệm thu |
|---|---|---|---|---|---|---|---|
| SYS-001 | `indicators/sessions.py`, `core/engine.py`, `core/BACKTEST_ENGINE.md`, `data/metadata/datasets.json` | Quy ước nhãn thời gian không thống nhất | IN-1, CO-F6, `08` (E2) | Chủ dự án chốt quy ước theo `timestamp_kind` đã xác nhận; thêm tham số nhãn tường minh ở `sessions` (mặc định giữ hành vi cũ, không đổi âm thầm); tùy chọn thêm `bar_index` vào `AccountState`/`Fill` | E2E-15, test `session_features` với nhãn open và close; test engine ghim `states[0].timestamp` | T01 (probe) | Một quy ước duy nhất được ghi trong tài liệu; test ghim ở cả `sessions` và engine; kết quả probe lưu lại |
| SYS-002 | `pyproject.toml`, `core/engine.py` (`assumptions`), repository | Không truy xuất nguồn gốc; mã chưa commit; phụ thuộc chưa khóa | ST-06, CO-F5, IN-10; git status (E1) | Commit/tag baseline; lock phụ thuộc hoặc `constraints.txt`; thêm vào `assumptions` hash dữ liệu, tên và tham số strategy, phiên bản thư viện, git revision, cờ dirty (tái dùng cơ chế sẵn có của lớp dữ liệu) | E2E-16 | Không | Kết quả mang đủ trường provenance; tồn tại baseline commit; tồn tại tệp khóa; CI hoặc script ghi cấu hình môi trường |
| SYS-003 | `core/execution.py`, `core/cost_model.py` | So sánh chạm và làm tròn tick trên float | CO-F2 (E2/E3) | Chạy probe trước. Nếu xác nhận: chuẩn hóa về số nguyên tick, so sánh chạm bằng số nguyên tick | E2E-19; `test_exact_touch_is_grid_exact`, `test_on_grid_price_not_moved_for_large_tick_counts` (CO mục C-F2) | T01 | Probe xác nhận hoặc bác bỏ; nếu sửa, differential test bản cũ so với bản mới chỉ khác ở các biên đã liệt kê |
| SYS-004 | `core/causality.py`, `tests/test_indicators.py`, `inspect_indicators.py`, `tests/test_engine.py` | Dung sai ngầm; test nhân quả engine chỉ sửa nến cuối | ST-01, IN-4, CO-D13 | `check_exact=True` mặc định (dung sai chỉ khi truyền tường minh); thêm biến thể có NaN và dữ liệu giá 1,08 bước 1e-5; test engine sửa nến k ngẫu nhiên | `test_rejects_sub_tolerance_leak` (ST mục D); mutation test E2E-12 | T01 | Rò rỉ cỡ 1e-5 bị phát hiện; toàn bộ test hiện tại vẫn pass (nếu có test fail, đó là phát hiện, không được nới dung sai) |
| SYS-005 | `core/engine.py`, `core/data_validator.py`, `data/metadata/datasets.json` | Metadata chưa xác nhận; engine có chặn dữ liệu chưa sẵn sàng hay không | DA-2, `08`, `00` | (a) Chủ dự án xác nhận từng trường metadata của dataset thật kèm bằng chứng. (b) Test tích hợp. Nếu engine không chặn, thêm bước kiểm tra tối thiểu ở điểm nạp | E2E-17 | Không | Test chứng minh từ chối; dataset thật có `ready_for_research=True` dưới validator hiện hành |

### 10.2 P1: trước khi chạy tích hợp dài hạn hoặc nghiệm thu toàn hệ thống

| ID | Module / file | Mô tả | Bằng chứng | Hướng sửa | Regression test | Phụ thuộc | Điều kiện nghiệm thu |
|---|---|---|---|---|---|---|---|
| SYS-006 | `core/engine.py`, `strategies/base_strategy.py`, `pyproject.toml` | Đường mặc định O(n²); bộ nhớ kết quả; spam `Order`/event | CO-F1, ST-05 | Đo trước (BM-01, 02). NumPy hóa OHLC dựng một lần; bỏ deep-copy thừa; không tạo Order/event cho tín hiệu bị bỏ khi đang có vị thế (hoặc gộp bộ đếm); đăng ký marker `slow` | Golden-master 50 seed; `test_incremental_path_scales_near_linearly` | SYS-017 (lưới an toàn) | Đầu ra giống bản cũ từng bit; độ dốc log-log theo BM-02 đạt tiêu chí |
| SYS-007 | `indicators/trend.py`, `indicators/market_structure.py`, `indicators/moving_averages.py` và các hàm vòng lặp | `parabolic_sar`, `structure_breaks` O(n²); vòng lặp Python | IN-2, IN-3 | Tính `valid` một lần ngoài vòng lặp; mảng NumPy thay `.iloc`; bản cũ giữ làm oracle trong test | So `old` với `new` bit-for-bit, 5 seed nhiều độ dài, có NaN; test thời gian n = 50.000 | SYS-004, SYS-019 | Kết quả bằng nhau từng bit (hoặc `rtol=1e-12` chỉ cho các hàm đã nêu lý do); thời gian đạt tiêu chí |
| SYS-008 | `strategies/base_strategy.py`, `core/engine.py`, tài liệu | Cửa sổ cắt đổi giá trị chỉ báo đệ quy/máy trạng thái | Suy luận tích hợp (E3) | Probe trước. Nếu có khác biệt, ghi tài liệu giới hạn L tối thiểu theo chỉ báo; không đổi ngữ nghĩa chỉ báo | E2E-20 | SYS-006 | Có kết quả probe; tài liệu nêu rõ chính sách cửa sổ |
| SYS-009 | `strategies/base_strategy.py`, `core/engine.py` | Không có vòng đời strategy | CO-F4 | `deepcopy` strategy hoặc hook `reset()` mặc định no-op đầu mỗi run | `test_rerun_same_strategy_instance_is_identical` (CO mục C-F4), E2E-14 | Không | Hai lần chạy bằng nhau từng bit |
| SYS-010 | `core/engine.py`, `core/portfolio.py`, `core/models.py` | Từ chối lệnh do gap không được đếm | CO-F3 | Thêm `code` cho event; `assumptions["rejected_orders"]` đếm theo mã; tùy chọn chính sách bracket, mặc định giữ hành vi cũ | E2E-06 | SYS-020 (nếu dùng `OrderRejected`) | Kết quả có bộ đếm; hành vi mặc định không đổi |
| SYS-011 | `core/data_validator.py` | Off-grid chỉ cảnh báo | DA-1 | Chủ dự án quyết định chính sách trước. Nếu đồng ý: kiểm tra tuyệt đối `index - index.floor(timeframe)` ghi vào `errors`, không đụng chính sách gap cùng ngày | E2E-10, `test_off_grid_timestamps_block_research` (DA mục C-#1) | Quyết định chủ dự án | Test đạt; quy tắc gap cùng ngày UTC không đổi |
| SYS-012 | `core/engine.py`, `core/data_validator.py` | Khoảng cách tín hiệu → khớp sau gap trong ngày | DA mục F, `00` | Ghi khoảng cách vào kết quả (không bắt buộc chặn) | E2E-09 | SYS-017 | Kết quả có chỉ số khoảng cách; chính sách chấp nhận gap không đổi |
| SYS-013 | `core/data_loader.py` | `diagnostic=False` trả NaN/NaT; epoch phân số, `unix_ns` | DA-2, DA-6 | Raise khi có token lỗi ở chế độ không diagnostic; parse số nguyên | `test_research_mode_rejects_bad_tokens` (DA mục C-#2) và test epoch/`unix_ns` | Không | Chế độ nghiên cứu raise; chế độ diagnostic giữ nguyên |
| SYS-014 | `data/metadata/symbols.json`, `datasets.json`, `core/data_validator.py`, `core/models.py`, `configs/config.yaml` | Thông số công cụ và đơn vị | DA-3, CO-F8, `08` | Gắn `symbols.json` là legacy hoặc xóa; thêm `point_size` vào `SPECIFICATION_FIELDS`; quyết định vai trò `instrument_specification_confirmations`; ghi đơn vị slippage | `test_legacy_symbols_do_not_conflict_with_registry`; test quét import | Không | Một nguồn thông số duy nhất. Bắt buộc trước mọi lần chạy XAUUSD |
| SYS-015 | `indicators/momentum.py`, `indicators/volatility.py` | Cửa sổ phẳng cho số rác | IN-5 | Probe; nếu xác nhận, ngưỡng epsilon theo thang | `bollinger_percent_b` và `cci` trên `[1.2345, 1.2350, 1.2341] + [1.0845]*30` | SYS-004 | Probe xác nhận hoặc bác bỏ; nếu sửa, cửa sổ phẳng cho NaN |
| SYS-016 | `indicators/market_structure.py`, `INDICATORS.md` | Pivot thứ Hai từ mảnh Chủ nhật | IN-6 | Chủ dự án quyết định chính sách; `min_bars` tùy chọn (mặc định giữ nguyên) | Test thứ Hai sau Chủ nhật mảnh | Quyết định chủ dự án | Chính sách ghi tài liệu; test đạt |
| SYS-017 | `tests/` (thư mục mới `tests/integration/`) | Thiếu test tích hợp và bất biến kế toán; test engine chạy chế độ lịch nghiêm ngặt | CO mục D, ST mục D, DA mục D | Thực hiện mục 9.2 và 9.3 | E2E-01…E2E-20, INV-01…INV-10 | T01 | Toàn bộ kịch bản có test; oracle độc lập |
| SYS-018 | `core/causality.py` | Input rỗng cho PASS; không kiểm index; `np.int64`; O(n²) mặc định; thiếu test pipeline | ST-02, ST-03, ST-04 | `ValueError` khi `len < 2`, `cutoffs=[]`, index không tăng/duy nhất/tz-aware; chấp nhận `numbers.Integral`; từ chối `cutoffs is None` khi n vượt ngưỡng; bộ cutoff lấy mẫu tất định | Bảy test của ST mục D | SYS-004 | Các test đạt; cutoff lấy mẫu bắt được mutation test E2E-12 |

### 10.3 P2: cải thiện ở các giai đoạn sau

| ID | Module / file | Mô tả | Hướng sửa | Regression test | Điều kiện nghiệm thu |
|---|---|---|---|---|---|
| SYS-019 | `tests/test_indicators.py` | Fixture yếu | Fixture hai chiều; NaN một phần; ví dụ tham chiếu công bố cho ADX, RSI, SAR | Test mới | Test mới đạt; không sửa kỳ vọng cũ |
| SYS-020 | `core/engine.py`, `core/cost_model.py` | `except ValueError` làm luồng điều khiển | `OrderRejected(ValueError)` có `code`; bọc lỗi giá kèm timestamp | `test_excess_spread_error_names_the_bar` | Lỗi nêu rõ nến; không bắt nhầm lỗi lập trình |
| SYS-021 | `configs/config.yaml`, `run_backtest.py` | Cấu hình lệch | Sửa `include_swap`, `timeframe`, ngày, đơn vị slippage khi nối cấu hình | Test nạp cấu hình | Cấu hình hợp lệ với `CostModel` và validator |
| SYS-022 | `core/data_loader.py` | `write_json`, `save_parquet` | Dump ra chuỗi rồi ghi atomic; so sánh với đường dẫn raw đã resolve; xử lý `OSError` | `test_write_json_failure_leaves_no_file` | Không để lại file cụt |
| SYS-023 | `core/data_loader.py`, `core/data_validator.py` | Hiệu năng loader | Đo trước; giới hạn danh sách gap (giữ số đếm) | So `assert_frame_equal` và JSON báo cáo trước/sau | Đầu ra giống nhau |
| SYS-024 | `benchmark_engine.py` | Kiểm chứng yếu | Tính `identical` thật; thoát khác 0 khi khác; so các lần lặp; kịch bản có chi phí, SL/TP, gap | Test benchmark qua `subprocess` với `-O` | Benchmark thất bại khi kết quả khác |
| SYS-025 | README, `INDICATORS.md`, sơ đồ, `run_backtest.py` | Tài liệu lệch | Đồng bộ pyarrow, số test, sơ đồ thiếu cạnh, mô tả stub, thông báo "đã sẵn sàng" | Không | Tài liệu khớp mã |
| SYS-026 | `indicators/_utils.py`, các hàm kiểm tham số | NaN/inf; `np.int64` | `np.isfinite`; `numbers.Integral` | `pytest.raises(ValueError)` với `deviations=np.nan`; `ma.sma(s, np.int64(3))` chạy | Test đạt |
| SYS-027 | `indicators/volatility.py` | `.stack()` | `(data[cols] <= 0).any().any()` | So kết quả trước và sau | Kết quả bằng nhau |

---

## 11. Acceptance Criteria

### 11.1 Cổng chấp nhận theo giai đoạn

| Cổng | Điều kiện (tất cả phải đạt) |
|---|---|
| **G0: Baseline** | Có baseline commit/tag; có stdout pytest gốc lưu lại; có danh sách phiên bản thư viện; không có thay đổi chưa commit ngoài các sửa đang làm |
| **G1: Dùng kết quả cho nghiên cứu** | Toàn bộ SYS-001…005 đã đóng (bằng sửa hoặc bằng bằng chứng thực thi bác bỏ); SYS-001 ghim quy ước nhãn bằng test; metadata dataset thật được xác nhận; mỗi kết quả mang provenance đầy đủ |
| **G2: Tích hợp dài hạn** | G1 đạt; SYS-006…018 đã đóng hoặc được chủ dự án chấp nhận thành giới hạn có tài liệu; bộ E2E-01…E2E-20 và INV-01…INV-10 đạt trên môi trường thật; golden-master cho mọi tối ưu |
| **G3: Hiệu năng** | BM-01…BM-03 chạy được; đường chính thức có độ dốc log-log và thời gian đạt tiêu chí do chủ dự án chốt; bộ nhớ trong giới hạn; kết quả tối ưu bằng bản cũ từng bit |
| **G4: Nghiệm thu toàn hệ thống** | G1–G3 đạt; METRICS và REPORTS đã triển khai và có test; chạy BM-04 trên 1,44 triệu nến thật |

### 11.2 Quy tắc đóng một vấn đề

- Một vấn đề SUSPECTED chỉ được đóng khi có (a) test thực thi chứng minh lỗi rồi sửa, hoặc (b) test thực thi chứng minh không có lỗi (đóng thành FALSE POSITIVE, lưu test lại).
- Không được đổi giá trị kỳ vọng của test cũ để làm test pass.
- Không được đóng bằng cách nới dung sai.
- Mỗi sửa đổi đi kèm test hồi quy và cập nhật tài liệu liên quan.

---

## 12. Final Verdict

### 12.1 Đánh giá bốn tiêu chí (không gộp thành điểm số)

| Tiêu chí | Bằng chứng ủng hộ | Rủi ro còn tồn tại | Test cần thực hiện | Đánh giá |
|---|---|---|---|---|
| **A. Correctness** | CO kiểm tay thời điểm khớp, Bid/Ask, chi phí, SL/TP, tỷ giá, kế toán và đối chiếu ví dụ tính tay (E2). IN đối chiếu tay công thức warm-up (E2). Báo cáo tổng quan ghi 296 test đạt (chưa kiểm chứng) | Float và tick (SYS-003); nhãn thời gian (SYS-001); test nhân quả yếu (SYS-004); lệnh bị từ chối khi gap (SYS-010); đơn vị công cụ (SYS-014); không có test E2E; METRICS chưa có | E2E-01…08, 13, 15, 18, 19; probe SYS-003; INV-01…10 | **NOT VERIFIED** |
| **B. Integration** | Kiến trúc có sơ đồ phụ thuộc; hai bên giao diện BaseStrategy ↔ engine và Execution ↔ Portfolio được một báo cáo thấy cả hai phía và không nêu mâu thuẫn (E2) | Các seam engine ↔ validator và indicators ↔ engine chưa ai xem đủ hai phía; METRICS và REPORTS NOT IMPLEMENTED; test engine chạy lịch nghiêm ngặt trong khi production mặc định không lịch (C-03) | E2E-09, 12, 15, 17, 20 | **NOT VERIFIED** cho mắt xích đã triển khai; không thể bắt đầu nghiệm thu toàn chuỗi vì hai mắt xích cuối chưa có |
| **C. Performance** | Đường gia tăng ước lượng khoảng 6 phút/lần (từ tài liệu, chưa tái lập); validator vector hóa | Đường mặc định O(n²); `parabolic_sar` và `structure_breaks` O(n²); vòng lặp Python; bộ nhớ kết quả. Chưa có phép đo nào | BM-01…BM-04 | **FAIL** cho đường chiến lược mặc định và hai chỉ báo O(n²) theo phân tích độ phức tạp (chưa đo); **NOT VERIFIED** cho đường gia tăng |
| **D. Reproducibility** | Không dùng ngẫu nhiên; test replay `==` (CO, E2); lớp dữ liệu ghi SHA256, git revision, phiên bản (DA, E2) | Mã chưa commit và phụ thuộc chưa khóa (E1); kết quả engine không ghi provenance; state strategy rò rỉ giữa các lần chạy; script hardcode artifact | E2E-14, E2E-16; baseline G0 | **FAIL** cho truy xuất nguồn gốc ở mức nghiên cứu (E1); **NOT VERIFIED** cho tính tất định giữa các lần chạy |

Không tiêu chí nào được xếp PASS hoặc PASS WITH LIMITATIONS, vì không tiêu chí nào có bằng chứng thực thi. Bốn báo cáo nguồn đều ghi PASS WITH LIMITATIONS nhưng đó là kết luận trong phạm vi tệp mỗi báo cáo thấy và dựa trên đọc tĩnh; kiểm toán tổng hợp này không kế thừa các nhãn đó.

### 12.2 Kết luận phân loại

| Loại | Nội dung |
|---|---|
| **Đã chứng minh đúng** | **Chưa có hạng mục nào** được chứng minh đúng bằng thực thi trong chuỗi bằng chứng này. Các điểm thiết kế ở mục 6.2 chỉ có bằng chứng ủng hộ E2 |
| **Đã chứng minh có lỗi** (E1, từ văn bản tôi đang giữ) | (1) Mã được kiểm toán chưa commit: 6 file `M` và 33 file `??`, snapshot là working tree (SYS-002). (2) Phụ thuộc chưa khóa; `requires-python>=3.11` nhưng chỉ có bằng chứng trên Python 3.15.2 (SYS-002). (3) README lệch với `pyproject.toml` và hiện trạng: README nói chưa cần pyarrow trong khi pyproject yêu cầu `pyarrow>=23`; README nói pytest có 1 bài test trong khi tổng quan báo 296 (SYS-025). (4) `pyproject.toml` bật `--strict-markers` và không khai báo marker nào, nên mọi test dùng `@pytest.mark.slow` do các báo cáo đề xuất sẽ lỗi khi thu thập nếu chưa đăng ký (SYS-006); và `run_backtest.py` in "đã sẵn sàng" dù chưa nối engine (SYS-025). Đây là các lỗi quy trình và tài liệu, **không phải lỗi tính toán** |
| **Chưa đủ bằng chứng** | Toàn bộ tính đúng đắn của mô phỏng khớp lệnh, SL/TP, P/L, equity (chưa chạy); tính nhân quả của pipeline; nhãn thời gian thật của dữ liệu; hiệu năng thật ở 1,44 triệu nến; số "296 passed"; các nghi ngờ số học (SYS-003, 015); hành vi của engine với dữ liệu chưa sẵn sàng (SYS-005); tương đương giữa chạy cửa sổ và chạy toàn lịch sử (SYS-008) |
| **Chưa triển khai** | `core/metrics.py` (drawdown, thống kê), `core/data_manager.py`, `indicators/custom_indicators.py`, `strategies/first_strategy.py`, nối cấu hình và xuất báo cáo ở `run_backtest.py`, `validation/`, walk-forward, sensitivity |
| **Giới hạn được chấp nhận** | Chỉ cảnh báo gap trong cùng ngày UTC; bỏ qua gap qua ngày, cuối tuần, lễ; không có lịch Forex đầy đủ; engine một công cụ, một vị thế, không đòn bẩy; không swap; vị thế cuối mẫu không bị ép đóng; chính sách TP gap thận trọng (C-06) |

### 12.3 Phán quyết

> **Hệ thống chưa đạt điều kiện để dùng kết quả backtest cho nghiên cứu, và không thể tuyên bố PASS toàn hệ thống.** Lý do không phải là đã chứng minh một lỗi nghiêm trọng, mà là: (i) chưa có bằng chứng thực thi nào; (ii) chưa có kiểm thử tích hợp; (iii) kết quả chưa truy xuất được nguồn gốc; (iv) nhãn thời gian chưa được thống nhất và ghim; (v) hai mắt xích cuối của chuỗi (METRICS, REPORTS) chưa tồn tại.
>
> Thiết kế được mô tả trong bốn báo cáo là thận trọng và nhất quán ở nhiều điểm quan trọng. Con đường hợp lý là: đóng baseline (G0), chạy các probe cho các nghi vấn rẻ, đóng năm cổng P0, rồi mới tối ưu hiệu năng với golden-master.

---

## 13. Unverified Questions and Missing Evidence

### 13.1 Câu hỏi chưa thể trả lời từ bằng chứng hiện có

| ID | Câu hỏi | Cần bằng chứng gì | Liên quan |
|---|---|---|---|
| Q-01 | Nhãn thời gian thực của parquet EURUSD là nhãn mở hay đóng? Giá trị `timestamp_kind` đã xác nhận là gì? | `data/metadata/datasets.json`; kiểm tra thủ công một vài nến với nguồn gốc | SYS-001 |
| Q-02 | Engine có gọi `validate_data` và kiểm tra `ready_for_research` trước khi chạy không? | `core/engine.py`, test E2E-17 | SYS-005 |
| Q-03 | `pd.testing.assert_frame_equal` trên pandas 3.1.1 có dung sai mặc định nào cho float64? | Chạy thử một dòng lệnh | SYS-004 |
| Q-04 | `CostModel.side_bar` và `fill` có sai lệch với `low <= sl` ở đúng biên không? Giá BTC có bị lệch 1 tick không? | Probe SYS-003 | SYS-003 |
| Q-05 | Slippage có áp dụng cho thoát TP và thoát SL không? | `BACKTEST_ENGINE.md`, `execution.py` | E2E-01, 05 |
| Q-06 | Quan hệ giữa `quantity`, `contract_size`, `pip_size` và tiền tệ quote/account? Ý nghĩa "đơn vị khai báo"? | `core/models.py`, `BACKTEST_ENGINE.md` | SYS-014 |
| Q-07 | Tỷ giá trong `ConversionRates` có nhãn bằng thời điểm khả dụng hay thời điểm mở nến? | `core/models.py`, `engine.py`, nguồn tỷ giá | SYS-001 |
| Q-08 | Số 251 µs/nến và số benchmark ở `BACKTEST_ENGINE.md` đến từ lần chạy nào? | Chạy lại BM-01, 02 | SYS-006 |
| Q-09 | Chiến lược gia tăng với `signal_history_limit = L` cho tín hiệu khác chiến lược toàn lịch sử không? | Probe E2E-20 | SYS-008 |
| Q-10 | `pd.Timedelta("H1")` có hợp lệ không? `config.yaml` có thể nạp được vào validator không? | Chạy thử; đọc `config.yaml` | SYS-021 |
| Q-11 | `00B_PROJECT_RULES.md` quy định gì? Chỉ thị gap trong ngày UTC mâu thuẫn ở đâu so với quy tắc gốc? | `00B_PROJECT_RULES.md` | Mục 6.3 |
| Q-12 | Validator có kiểm khoảng cách chuẩn khớp `timeframe` đã khai báo không (khai 1min mà dữ liệu thật 5min)? | `data_validator.py`; CO mục F nêu nghi vấn | SYS-011 |
| Q-13 | Dữ liệu thật có các nến cuối tuần Chủ nhật vài giờ? Pivot thứ Hai bị ảnh hưởng bao nhiêu phần trăm số ngày? | Chạy `previous_period_levels` trên dữ liệu thật | SYS-016 |
| Q-14 | Cơ chế nào trong code đọc `symbols.json`? | Quét import toàn repo | SYS-014 |
| Q-15 | `BacktestResult.__eq__` hoạt động thế nào khi có `DataFrame`? | `core/models.py` | SYS-024 |
| Q-16 | Hash các file nguồn có khớp `MANIFEST.md` không? | Băm lại file | Mục 2.3 |

### 13.2 Bằng chứng còn thiếu

- Mã nguồn thật (hoặc quyền đọc repo) cho các seam chưa được xem đủ hai phía.
- `07_TEST_RESULTS.md` hoặc stdout pytest gốc; coverage; lint; type check.
- `00A_SOURCE_INVENTORY.md`, `00B_PROJECT_RULES.md`.
- Một lần chạy thực tế trên dữ liệu thật (hoặc lát đại diện) với đo thời gian và bộ nhớ.
- Xác nhận metadata dataset thật từ chủ dự án.
- Quyết định chính sách của chủ dự án cho SYS-011, SYS-016 và nhãn thời gian (SYS-001).

---


# CLINE REMEDIATION HANDOFF

Tài liệu này dành cho Cline. Cuộc kiểm toán không sửa mã. Mọi nhiệm vụ dưới đây là **đề xuất**, được sắp theo trình tự thực hiện. Trạng thái của từng vấn đề là của kiểm toán tổng hợp: phần lớn là SUSPECTED hoặc NEEDS VERIFICATION, tức **chưa được chứng minh bằng thực thi**. Việc đầu tiên với mỗi vấn đề là xác minh, không phải sửa.

## Quy tắc chung

1. **Xác minh trước, sửa sau.** Với mục SUSPECTED hoặc NEEDS VERIFICATION, viết probe test trước. Dùng `xfail(strict=True)` kèm `reason="SYS-xxx"`: nếu lỗi có thật, test fail như dự kiến (xfail); nếu không có lỗi, test XPASS và làm bộ test fail, báo hiệu FALSE POSITIVE. Ghi kết quả vào `reports/audit_followup/PROBE_RESULTS.md`.
2. **Không đổi giá trị kỳ vọng của test hiện có** và không nới dung sai để test pass. Nếu một test cũ fail sau khi siết kiểm tra, đó là phát hiện: ghi lại, không tự sửa kỳ vọng.
3. **Một vấn đề một commit**, thông điệp nêu SYS-ID. Không gộp tối ưu hiệu năng với sửa logic.
4. **Mọi tối ưu cần golden-master:** chạy bản cũ và bản mới trên ít nhất 50 chuỗi ngẫu nhiên (seed cố định, có gap, SL/TP, tỷ giá), so `orders/fills/trades/states/events` bằng đẳng thức chính xác, không dùng `approx`.
5. **Không tuyên bố test đã pass nếu chưa chạy.** Lưu stdout pytest gốc vào `reports/audit_followup/` sau mỗi nhiệm vụ.
6. **Dừng và hỏi chủ dự án** ở các điểm cần quyết định chính sách: nhãn thời gian (T04), off-grid (T14), pivot thứ Hai (T16), chính sách bracket (T13).
7. Không dùng dữ liệu thật để chạy CLI xử lý dữ liệu hay benchmark dài trừ khi nhiệm vụ nêu rõ.

## Những phần KHÔNG được thay đổi (áp dụng cho mọi nhiệm vụ)

- Chính sách gap được chấp nhận: chỉ cảnh báo khoảng thiếu nến giữa hai timestamp liên tiếp cùng ngày UTC; bỏ qua gap qua ngày UTC; không xây lịch Forex đầy đủ.
- Phạm vi engine: một công cụ, một vị thế, không đòn bẩy, không swap.
- Thời điểm khớp: tín hiệu cuối nến, khớp ở open nến có dữ liệu kế tiếp, kèm chốt chặn `opening < order.submitted_at`.
- Công thức Bid/Ask từ một luồng giá; chi phí chỉ nằm trong giá khớp; commission mỗi phía; tick làm tròn bất lợi.
- SL ưu tiên khi cùng chạm; gap SL ở open; gap TP bị chặn ở target (trừ khi chủ dự án quyết định khác).
- Vị thế cuối mẫu không bị ép đóng.
- Metadata fail-closed; không sort, drop, fill, nội suy dữ liệu; băm SHA256 file raw; không ghi đè Parquet; không ghi vào `data/raw`.
- Chỉ báo fail-closed ở `_utils`; không dùng `shift(-n)`, `center=True`; swing và structure chỉ phát tại bar xác nhận.
- Dữ liệu gốc và báo cáo cũ trong `reports/runs/` phải được bảo toàn.
- Chữ ký API công khai hiện có: mọi tham số mới phải có mặc định giữ hành vi cũ.

## Trình tự nhiệm vụ

### T00: Baseline và đóng băng trạng thái (SYS-002, cổng G0)

- **Mục tiêu:** có một điểm tham chiếu để mọi thay đổi sau đó so sánh được.
- **File liên quan:** toàn bộ repository; `pyproject.toml`.
- **Bằng chứng cần xác minh:** chạy `pytest` đầy đủ và lưu stdout; so số kết quả với "296 passed". Ghi `pip list`, `pip freeze`, phiên bản Python.
- **Test cần viết:** không.
- **Thay đổi cho phép:** tạo commit hoặc tag baseline cho working tree hiện tại (cần chủ dự án đồng ý); tạo thư mục `reports/audit_followup/`; tạo `requirements.lock` hoặc `constraints.txt` từ môi trường đã kiểm.
- **Điều kiện nghiệm thu:** baseline commit tồn tại; stdout pytest gốc được lưu; số liệu so với 296 được ghi nhận (khác thì báo cáo, không sửa).
- **Không được thay đổi:** mã nguồn và test.

### T01: Bộ probe cho các nghi vấn rẻ (SYS-003, 004, 005, 008, 013, 015)

- **Mục tiêu:** biến các nghi vấn SUSPECTED thành bằng chứng thực thi trước khi sửa.
- **File liên quan:** tệp mới `tests/probes/` (không sửa mã nguồn); tham khảo `core/causality.py`, `core/cost_model.py`, `core/execution.py`, `core/engine.py`, `core/data_loader.py`, `indicators/momentum.py`, `indicators/volatility.py`.
- **Bằng chứng cần xác minh:**
  - (a) `assert_frame_equal` bỏ qua rò rỉ cỡ 1e-5 trên giá 1,1 không (builder `d.close + 1e-5*(len(d)%2)`).
  - (b) Chạm đúng biên SL/TP với `CostModel(k*1e-5, 0, 0)`, k chẵn; giá trên lưới BTC (tick 0,01, giá 10⁷ tick) có bị dịch 1 tick khi slippage = 0 không.
  - (c) Engine có từ chối dữ liệu `ready_for_research=False` không.
  - (d) `load_csv(diagnostic=False)` với token `abc` có raise không; epoch `"1704153600000.5"`.
  - (e) `cci` và `bollinger_percent_b` trên cửa sổ phẳng 1,0845 sau cửa sổ biến động.
  - (f) Chiến lược gia tăng với `signal_history_limit = L` so với toàn lịch sử, dùng `rma`/`supertrend`/`parabolic_sar`.
- **Test cần viết:** probe tương ứng ở trên (mã mẫu có trong báo cáo CORE mục C-F2, DATA mục C-#1, #2, #4, INDICATORS mục C-#5).
- **Thay đổi cho phép:** chỉ thêm tệp test mới và tệp ghi kết quả.
- **Điều kiện nghiệm thu:** mỗi probe có kết quả (lỗi xác nhận, hoặc FALSE POSITIVE) trong `PROBE_RESULTS.md`; danh sách SYS-ID nào cần sửa được cập nhật.
- **Không được thay đổi:** mã nguồn, test hiện có.

### T02: Siết bằng chứng nhân quả (SYS-004)

- **Mục tiêu:** test prefix-invariance bắt được sai lệch 1 tick.
- **File liên quan:** `core/causality.py`, `tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs`, `inspect_indicators.py`, `tests/test_engine.py::test_future_candles_do_not_change_earlier_outputs`.
- **Bằng chứng cần xác minh:** kết quả probe (a) của T01.
- **Test cần viết:** `test_rejects_sub_tolerance_leak`; biến thể chỉ báo trên 400+ nến quanh 1,08 bước 1e-5 có một NaN ở giữa, tham số mặc định (14/20/26) cho vài hàm chính; test engine sửa nến k ngẫu nhiên và khẳng định mọi đầu ra thuộc nến < k không đổi.
- **Thay đổi cho phép:** đổi so sánh sang `check_exact=True` (mặc định) với dung sai chỉ khi truyền tường minh; thêm test.
- **Điều kiện nghiệm thu:** test mới đạt; nếu test cũ fail khi siết, ghi lại như phát hiện (không nới).
- **Không được thay đổi:** kỳ vọng của test hiện có; ngữ nghĩa deep-copy và so sánh nghiêm kiểu của `check_prefix_invariance`.

### T03: Test cấp pipeline và harness nhân quả (SYS-018)

- **Mục tiêu:** chặn PASS giả và có cách chạy được ở quy mô thật.
- **File liên quan:** `core/causality.py`, `tests/` mới.
- **Bằng chứng cần xác minh:** hàm hiện trả `None` với `len(data) < 2` hoặc `cutoffs=[]`; từ chối `np.int64`; không kiểm tra index.
- **Test cần viết:** bảy test của báo cáo STRATEGIES mục D; mutation test E2E-12 (rò rỉ một hàng).
- **Thay đổi cho phép:** thêm kiểm tra đầu vào (`ValueError` với input rỗng, index không tăng/duy nhất/tz-aware); `numbers.Integral`; từ chối `cutoffs is None` khi n vượt ngưỡng; hàm sinh cutoff lấy mẫu tất định (biên cửa sổ ±1, đổi ngày UTC, đầu phiên, mẫu ngẫu nhiên có seed).
- **Điều kiện nghiệm thu:** các test đạt; mutation test bị bắt ở bộ cutoff lấy mẫu.
- **Không được thay đổi:** thiết kế deep-copy, từ chối `bool` làm cutoff, `raise ... from exc`.

### T04: Chốt quy ước nhãn thời gian (SYS-001)

- **Mục tiêu:** một quy ước duy nhất xuyên suốt dữ liệu, `sessions`, engine.
- **File liên quan:** `indicators/sessions.py`, `indicators/INDICATORS.md`, `core/engine.py`, `core/BACKTEST_ENGINE.md`, `data/metadata/datasets.json`.
- **Bằng chứng cần xác minh:** `timestamp_kind` đã xác nhận của dataset thật; kết quả `session_features` với đầu vào `07:59, 08:00, 16:59, 17:00` UTC (kỳ vọng nhãn close: `[F, F, T, T]`; hiện tại theo IN-1: `[F, T, T, F]`); `states[0].timestamp` với nến nhãn open.
- **Test cần viết:** E2E-15; test `session_features` với `label="open"` và `label="close"`; test `states[0].timestamp == bars.index[0] + timedelta(1h)` ghim hành vi hiện tại (CO-F6).
- **Thay đổi cho phép:** **dừng và hỏi chủ dự án** trước. Sau đó: thêm tham số nhãn tường minh với `bar_minutes` (mặc định giữ hành vi cũ); cập nhật tài liệu thành một quy ước; tùy chọn thêm `bar_index` vào `AccountState` và `Fill`.
- **Điều kiện nghiệm thu:** test ghim ở cả `sessions` và engine; tài liệu không còn mâu thuẫn; kết quả probe ghi lại.
- **Không được thay đổi:** quy tắc tín hiệu cuối nến / khớp nến kế tiếp.

### T05: Cổng dữ liệu tại điểm nạp của engine (SYS-005)

- **Mục tiêu:** engine không chạy dữ liệu chưa sẵn sàng cho nghiên cứu.
- **File liên quan:** `core/engine.py`, `core/data_validator.py`, `data/metadata/datasets.json`.
- **Bằng chứng cần xác minh:** kết quả probe (c) của T01.
- **Test cần viết:** E2E-17.
- **Thay đổi cho phép:** nếu engine không chặn, thêm bước kiểm tra tối thiểu ở điểm nạp; nếu đã chặn, chỉ thêm test. Metadata dataset thật do **chủ dự án** xác nhận, không tự điền.
- **Điều kiện nghiệm thu:** E2E-17 đạt.
- **Không được thay đổi:** cơ chế metadata fail-closed; không tự đặt `confirmed=true`.

### T06: Float và tick (SYS-003)

- **Mục tiêu:** chạm biên và làm tròn tick chính xác theo lưới.
- **File liên quan:** `core/execution.py::protective_exit`, `core/cost_model.py::side_bar`, `fill`.
- **Bằng chứng cần xác minh:** kết quả probe (b). **Nếu probe cho thấy không có lỗi, đóng thành FALSE POSITIVE và dừng.**
- **Test cần viết:** `test_exact_touch_is_grid_exact`, `test_on_grid_price_not_moved_for_large_tick_counts`, E2E-19; differential test bản cũ so với mới.
- **Thay đổi cho phép:** chuẩn hóa về số nguyên tick (`n = round(x / tick)` kèm ngưỡng theo thang); so sánh chạm bằng số nguyên tick.
- **Điều kiện nghiệm thu:** chạm đúng biên kích hoạt; giá trên lưới không dịch khi slippage = 0; mọi khác biệt so với bản cũ nằm đúng ở các biên đã liệt kê.
- **Không được thay đổi:** hướng làm tròn bất lợi; SL ưu tiên; công thức Bid/Ask.

### T07: Provenance trong kết quả (SYS-002)

- **Mục tiêu:** mỗi kết quả truy được dữ liệu, mã, tham số, môi trường.
- **File liên quan:** `core/engine.py` (`assumptions`), `core/data_loader.py` (cơ chế ghi git revision và phiên bản sẵn có).
- **Bằng chứng cần xác minh:** các trường hiện có của `assumptions`.
- **Test cần viết:** E2E-16 (`data_sha256`, `strategy`, `strategy_params`, `library_versions`, git revision, cờ dirty).
- **Thay đổi cho phép:** thêm trường vào `assumptions`; tái dùng hàm lấy git/phiên bản từ lớp dữ liệu thay vì viết lại.
- **Điều kiện nghiệm thu:** E2E-16 đạt; `BacktestResult` so sánh bằng vẫn hoạt động.
- **Không được thay đổi:** các trường `assumptions` hiện có; tính tất định.

### T08: Bộ test tích hợp và bất biến kế toán (SYS-017)

- **Mục tiêu:** lưới an toàn trước khi tối ưu. Đặt **trước** T09 và T10.
- **File liên quan:** `tests/integration/` (mới), `tests/conftest.py`.
- **Bằng chứng cần xác minh:** chế độ mặc định không lịch (C-03); xem `BACKTEST_ENGINE.md` để chốt quy ước cho oracle (Q-05, Q-06).
- **Test cần viết:** E2E-01…E2E-20 (trừ những mục đang chờ sửa) và INV-01…INV-10 theo mục 9 của báo cáo; oracle độc lập tối đa khoảng 80 dòng, không import engine.
- **Thay đổi cho phép:** chỉ thêm test và fixture.
- **Điều kiện nghiệm thu:** test đạt trên mã hiện tại; kịch bản nào lộ khác biệt so với oracle thì ghi thành phát hiện mới, không sửa oracle cho khớp.
- **Không được thay đổi:** mã nguồn; kỳ vọng test hiện có.

### T09: Hiệu năng engine (SYS-006)

- **Mục tiêu:** đường chính thức gần tuyến tính theo n.
- **File liên quan:** `core/engine.py`, `strategies/base_strategy.py`, `pyproject.toml` (đăng ký marker `slow`).
- **Bằng chứng cần xác minh:** BM-01, BM-02 trước khi sửa (đo baseline); đếm số hàng truyền vào strategy ở n = 5k, 10k, 20k.
- **Test cần viết:** golden-master 50 seed; `test_incremental_path_scales_near_linearly`.
- **Thay đổi cho phép:** dựng mảng NumPy OHLC một lần ngoài vòng lặp; bỏ deep-copy thừa; không tạo `Order` hoặc event cho tín hiệu bị bỏ khi đã có vị thế (hoặc gộp bộ đếm); đăng ký marker `slow`.
- **Điều kiện nghiệm thu:** đầu ra bằng bản cũ từng bit; độ dốc log-log đạt tiêu chí chủ dự án chốt.
- **Không được thay đổi:** thứ tự xử lý EXIT/SL/TP; ngữ nghĩa khớp lệnh; strategy vẫn chỉ nhận bản sao prefix.

### T10: Hiệu năng chỉ báo (SYS-007, 027)

- **Mục tiêu:** `parabolic_sar` và `structure_breaks` tuyến tính; giảm vòng lặp Python.
- **File liên quan:** `indicators/trend.py`, `indicators/market_structure.py`, `indicators/moving_averages.py`, `indicators/volatility.py` (`garman_klass_volatility`).
- **Bằng chứng cần xác minh:** đo `parabolic_sar` ở n = 20.000 và 40.000 (độ dốc ≈ 2 nghĩa là O(n²)); đo `rma`, `atr`, `rsi`, `adx`, `supertrend` ở 1,44M nến tổng hợp.
- **Test cần viết:** giữ bản cũ làm oracle trong test; so bit-for-bit (`assert_frame_equal(..., check_exact=True)`) trên 5 seed nhiều độ dài có NaN; test thời gian n = 50.000 đánh dấu `slow`.
- **Thay đổi cho phép:** tính `valid` một lần; mảng NumPy thay `.iloc`; tính trọng số `wma` một lần; thay `.stack()` bằng so sánh trực tiếp.
- **Điều kiện nghiệm thu:** kết quả bằng bản cũ; prefix-invariance giữ nguyên với kiểm tra chính xác (T02).
- **Không được thay đổi:** ngữ nghĩa seed và NaN-restart của EMA/RMA; tài liệu về seed khác TA-Lib.

### T11: Cửa sổ lịch sử của chiến lược gia tăng (SYS-008)

- **Mục tiêu:** biết và ghi tài liệu `signal_history_limit` tối thiểu cho từng chỉ báo.
- **File liên quan:** `strategies/base_strategy.py`, `core/BACKTEST_ENGINE.md`, `indicators/INDICATORS.md`.
- **Bằng chứng cần xác minh:** kết quả probe (f).
- **Test cần viết:** E2E-20.
- **Thay đổi cho phép:** chỉ tài liệu và test, trừ khi probe cho thấy sai lệch nghiêm trọng, khi đó hỏi chủ dự án.
- **Điều kiện nghiệm thu:** tài liệu nêu chính sách cửa sổ; test ghim kết quả.
- **Không được thay đổi:** ngữ nghĩa chỉ báo.

### T12: Vòng đời strategy (SYS-009)

- **Mục tiêu:** chạy lại không rò trạng thái.
- **File liên quan:** `strategies/base_strategy.py`, `core/engine.py`.
- **Bằng chứng cần xác minh:** strategy có `self.n` tăng mỗi lần gọi, chạy hai lần trên cùng instance cho kết quả khác.
- **Test cần viết:** `test_rerun_same_strategy_instance_is_identical`; E2E-14.
- **Thay đổi cho phép:** `copy.deepcopy(strategy)` ở đầu `run`, hoặc hook `reset()` mặc định no-op; tùy chọn `position_state` tham số tùy chọn.
- **Điều kiện nghiệm thu:** hai lần chạy bằng nhau từng bit.
- **Không được thay đổi:** `generate_signals` vẫn raise `NotImplementedError` ở lớp cơ sở.

### T13: Quan sát được lệnh bị từ chối (SYS-010, 020)

- **Mục tiêu:** biết tỷ lệ lệnh vào bị từ chối do gap.
- **File liên quan:** `core/engine.py`, `core/portfolio.py`, `core/models.py`.
- **Bằng chứng cần xác minh:** hành vi hiện tại với `bars.iloc[1] = [98, 99, 97, 98]`, BUY `sl=99.5`, `tp=110`.
- **Test cần viết:** E2E-06; `test_excess_spread_error_names_the_bar`.
- **Thay đổi cho phép:** `code` cho event; `assumptions["rejected_orders"]`; lớp `OrderRejected(ValueError)` chỉ bắt lớp này; bọc `side_bar` kèm timestamp. Chính sách bracket mới chỉ thêm nếu chủ dự án đồng ý, mặc định giữ hành vi cũ.
- **Điều kiện nghiệm thu:** bộ đếm có trong kết quả; hành vi mặc định không đổi.
- **Không được thay đổi:** quy tắc từ chối hiện tại (mặc định).

### T14: Lớp dữ liệu (SYS-011, 012, 013, 022, 023)

- **Mục tiêu:** dữ liệu lỗi bị chặn ở chế độ nghiên cứu, ghi file an toàn.
- **File liên quan:** `core/data_validator.py`, `core/data_loader.py`, `core/engine.py` (chỉ ghi khoảng cách tín hiệu → khớp).
- **Bằng chứng cần xác minh:** kết quả probe (d); hành vi với 3 nến lúc 00:00:00, 00:01:30, 00:03:00. **Hỏi chủ dự án** về chính sách off-grid.
- **Test cần viết:** `test_off_grid_timestamps_block_research`, `test_research_mode_rejects_bad_tokens`, `test_write_json_failure_leaves_no_file`, test epoch phân số và `unix_ns`, E2E-09, E2E-10.
- **Thay đổi cho phép:** kiểm tra tuyệt đối `index - index.floor(timeframe)` vào `errors`; raise ở chế độ không diagnostic; parse số nguyên; ghi JSON qua chuỗi + temp; so sánh với đường dẫn raw đã resolve; giới hạn danh sách gap (giữ số đếm) sau khi đo.
- **Điều kiện nghiệm thu:** các test đạt; quy tắc gap cùng ngày UTC không đổi; báo cáo JSON trước/sau tối ưu giống nhau.
- **Không được thay đổi:** không sort, drop, fill; cảnh báo gap cùng ngày vẫn chỉ là cảnh báo.

### T15: Thông số công cụ và cấu hình (SYS-014, 021)

- **Mục tiêu:** một nguồn thông số duy nhất; cấu hình hợp lệ khi được nối.
- **File liên quan:** `data/metadata/symbols.json`, `data/metadata/datasets.json`, `core/data_validator.py`, `core/models.py`, `configs/config.yaml`.
- **Bằng chứng cần xác minh:** quét import xem mã nào đọc `symbols.json`; kết quả của test nhất quán XAUUSD (kỳ vọng EURUSD đạt, XAUUSD fail theo DA).
- **Test cần viết:** `test_legacy_symbols_do_not_conflict_with_registry`; test quét import.
- **Thay đổi cho phép:** đánh dấu hoặc xóa `symbols.json` legacy (cần chủ dự án đồng ý); thêm `point_size` vào `SPECIFICATION_FIELDS`; quyết định vai trò `instrument_specification_confirmations`; sửa `include_swap`, `timeframe`, ngày, ghi chú đơn vị slippage.
- **Điều kiện nghiệm thu:** test nhất quán đạt; **chặn mọi lần chạy XAUUSD cho đến khi xong nhiệm vụ này**.
- **Không được thay đổi:** thông số đã được chủ dự án xác nhận trong `datasets.json`.

### T16: Chỉ báo: số học và ngữ nghĩa kỳ trước (SYS-015, 016, 019, 026)

- **Mục tiêu:** cửa sổ phẳng, pivot thứ Hai, tham số không hợp lệ, fixture mạnh hơn.
- **File liên quan:** `indicators/momentum.py`, `indicators/volatility.py`, `indicators/market_structure.py`, `indicators/_utils.py`, `tests/test_indicators.py`.
- **Bằng chứng cần xác minh:** kết quả probe (e); **hỏi chủ dự án** về chính sách pivot thứ Hai.
- **Test cần viết:** cửa sổ phẳng; `previous_period_levels(d, min_bars=...)`; `deviations=np.nan` phải raise; `ma.sma(s, np.int64(3))` chạy; fixture hai chiều cho ADX, RSI, SAR, SuperTrend; NaN một phần.
- **Thay đổi cho phép:** ngưỡng epsilon theo thang hoặc phát hiện cửa sổ phẳng bằng `rolling.max() == rolling.min()`; `min_bars` tùy chọn (mặc định cũ); `np.isfinite`, `numbers.Integral`.
- **Điều kiện nghiệm thu:** test đạt; không thay đổi kết quả trên dữ liệu không phẳng.
- **Không được thay đổi:** công thức chỉ báo đã đối chiếu tay đúng (warm-up `stochastic_rsi`, `vortex`, VHF, ADX, SAR giá trị đầu, Ichimoku `cloud_a`).

### T17: Tài liệu và benchmark (SYS-024, 025)

- **Mục tiêu:** tài liệu khớp mã; benchmark kiểm chứng thật.
- **File liên quan:** `README.md`, `indicators/INDICATORS.md`, sơ đồ trong `03_INDICATORS_AUDIT.md`, `run_backtest.py`, `benchmark_engine.py`, mô tả `custom_indicators.py`.
- **Bằng chứng cần xác minh:** các điểm lệch ở mục 12.2.
- **Test cần viết:** test benchmark qua `subprocess` với `-O` (benchmark phải thoát khác 0 khi hai kết quả khác nhau).
- **Thay đổi cho phép:** sửa tài liệu; thông báo của `run_backtest.py` nêu rõ chưa nối engine; benchmark tính `identical` thật, so các lần lặp, thêm kịch bản có chi phí, SL/TP, gap.
- **Điều kiện nghiệm thu:** tài liệu khớp pyproject, số test, phụ thuộc; benchmark thất bại khi kết quả khác.
- **Không được thay đổi:** logic engine.

### T18: Nghiệm thu hiệu năng và tích hợp (cổng G2, G3)

- **Mục tiêu:** thu thập bằng chứng E0 cho các tiêu chí A–D.
- **File liên quan:** `benchmark_engine.py`, `tests/integration/`.
- **Bằng chứng cần xác minh:** BM-01…BM-03; tùy chọn BM-04 trên 1,44M nến thật sau khi G1 đạt.
- **Test cần viết:** không thêm; chạy bộ có sẵn.
- **Thay đổi cho phép:** chỉ tạo báo cáo kết quả `reports/audit_followup/ACCEPTANCE_RESULTS.md` với lệnh thực tế, stdout nguyên vẹn, môi trường.
- **Điều kiện nghiệm thu:** theo mục 11 (G1–G3); báo cáo nêu rõ từng tiêu chí A–D đã có bằng chứng E0 nào.
- **Không được thay đổi:** kết quả đã ghi; không làm đẹp số liệu.

---

*Hết báo cáo. Báo cáo này là đánh giá và hợp nhất bằng chứng thứ cấp, đọc tĩnh. Không có mã hay test nào được thực thi; không có kết luận nào ở trên là bằng chứng thực thi.*
