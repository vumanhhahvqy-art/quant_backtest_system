# FINAL SYSTEM AUDIT REPORT — `quant_backtest_system`

| Thuộc tính | Giá trị |
|---|---|
| Ngày kiểm toán | 2026-11-17 → 2026-11-18 |
| Gốc dự án | `C:/Users/Admin/Documents/quant_backtest_system/` |
| Git HEAD | `7af3b774b1721e091e2527a00563912255d44702` (working tree **có 6 file M và nhiều file untracked**: mã được kiểm toán **không nằm trong commit nào**) |
| Môi trường chạy | Python 3.15.2, pandas 3.1.1, NumPy 2.5.5, pytest 9.2.0, Windows 10 (`.venv` của dự án) |
| Phương pháp | (1) Đọc 6 tài liệu đính kèm; (2) đọc trực tiếp mã nguồn tại các ranh giới tích hợp; (3) **chạy lại** pytest; (4) chạy probe xác minh và benchmark **chỉ import** mã dự án, đặt ở thư mục scratch của phiên kiểm toán |
| Thay đổi mã nguồn | **Không có.** `git status --short` vẫn 39 mục trước và sau kiểm toán; pytest chạy với `-p no:cacheprovider` và `PYTHONDONTWRITEBYTECODE=1` |
| Bằng chứng máy đọc | [probes.py](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/probes.py), [probe_results.json](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/probe_results.json), [probes2.py](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/probes2.py), [perf.py](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/perf.py), [perf_results.jsonl](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/perf_results.jsonl), [perf_results_large.jsonl](file:///C:/Users/Admin/.gemini/antigravity/brain/7022fcc8-43b1-4837-9f65-458cfcebf9d9/scratch/perf_results_large.jsonl) |

> [!IMPORTANT]
> Khác với bốn báo cáo thành phần (chỉ đọc tĩnh), phiên này **có môi trường chạy mã**. Nhãn **VERIFIED-RUN** nghĩa là đã tái hiện bằng thực thi trong phiên này. **STATIC** nghĩa là chỉ xác minh bằng đọc mã. **NEEDS VERIFICATION** nghĩa là chưa đủ bằng chứng. Không có kết luận nào được nâng thành CONFIRMED chỉ vì báo cáo trước đã ghi như vậy.

---

## 1. Executive Summary

**Kết luận chính**

1. **Lõi mô phỏng (engine → execution → cost → portfolio) tính đúng trên dữ liệu tổng hợp.** Đã kiểm bằng thực thi:
   - 296/296 test hiện có đạt (tái hiện).
   - 0 vi phạm bất biến kế toán trên 20.000 nến ngẫu nhiên có gap, chi phí, SL/TP (904 giao dịch).
   - Sửa nến *k* ngẫu nhiên không làm đổi output trước *k*.
   - Hai tiến trình độc lập cho cùng SHA256 kết quả.
2. **Có lỗi đã chứng minh làm sai kết quả nghiên cứu.** Ba mục P0:
   - **QBS-01:** so sánh chạm SL/TP bằng float bỏ sót **1.752/4.286** trường hợp chạm đúng biên khi spread = 4 tick.
   - **QBS-02:** công cụ kiểm tra nhân quả `check_prefix_invariance` cho **PASS** một rò rỉ 1 tick (1e-5) và cho PASS với đầu vào rỗng.
   - **QBS-03:** kết quả không truy xuất được (không hash dữ liệu/strategy/phiên bản; mã chưa commit).
3. **Chuỗi tích hợp DATA → … → REPORTS chưa khép kín.**
   - `core/metrics.py`, runner `run_backtest.py` và lớp xuất báo cáo: **NOT IMPLEMENTED**.
   - Metadata thật của EURUSD/XAUUSD bị **15 blocker** nên engine **không thể chạy dữ liệu thật**. Đây là thiết kế fail-closed đúng, nhưng hệ thống chưa sẵn sàng nghiên cứu.
4. **Hiệu năng.** Đường gia tăng chạy được 1.000.000 nến trong **554 s**, peak **1,31 GB**. Đường full-prefix mặc định tăng bậc hai: ngoại suy ≈ **19 giờ** cho 1,44M nến.
   - Nhận định O(n²) của INDICATORS #2 (SAR, `structure_breaks`) **bị bác bỏ bằng đo đạc** trên pandas 3.1.1: tuyến tính ≈ 365 µs/nến. Tuy vậy vẫn chậm, ≈ 9 phút cho 1,44M nến.
5. **Bác bỏ hoặc hạ mức một số nhận định:**
   - CORE-F2 (phần BTC tick rounding): không tái hiện.
   - INDICATORS #1 (P0 có điều kiện): **không có rò rỉ tương lai**. Đây là lỗi hợp đồng nhãn thời gian lệch 1 nến ở biên phiên, hạ xuống **P1**.
   - INDICATORS #5: không tái hiện số rác.
   - DATA #2: engine đã chặn, hạ xuống **P2**.

**Phán quyết theo tiêu chí** (chi tiết ở §12):

| Tiêu chí | Đánh giá |
|---|---|
| A. Correctness | **PASS WITH LIMITATIONS**: lõi đúng trên dữ liệu tổng hợp; **còn P0 QBS-01, QBS-02** |
| B. Integration | **FAIL**: thiếu metrics/runner/report; metadata thật không qua cổng; hợp đồng nhãn phiên mâu thuẫn |
| C. Performance | **PASS WITH LIMITATIONS**: chỉ đường gia tăng; 1,44M nến chưa đo trực tiếp |
| D. Reproducibility | **FAIL**: tất định đã chứng minh, nhưng không truy xuất được giả định/dữ liệu/mã |

**Toàn hệ thống: NOT READY cho nghiên cứu.** Có thể tiếp tục phát triển sau khi xử lý 3 mục P0.

---

## 2. Audit Scope and Evidence

### 2.1 Tài liệu đã đọc toàn văn

| File | Nội dung | Ghi chú |
|---|---|---|
| `00_PROJECT_OVERVIEW.md` | Kiến trúc quan sát, quy tắc gap, môi trường | Quy tắc gap §49–55 áp dụng cho kiểm toán này |
| `09_FINAL_AUDIT_INPUT.md` | Hồ sơ bàn giao, bảng API liên kết, 7 câu hỏi chưa phân xử | Dùng làm khung §5 |
| `CLAUDE_AUDIT_CORE.md` | F1–F8 | Đọc tĩnh |
| `CLAUDE_AUDIT_DATA.md` | #1–#8 | Đọc tĩnh, 13/54 file |
| `CLAUDE_AUDIT_INDICATORS.md` | #1–#10 | Đọc tĩnh |
| `CLAUDE_AUDIT_STRATEGIES.md` | P1-01…P2-08 | Đọc tĩnh, không nhận engine |

### 2.2 Mã nguồn đọc trực tiếp trong phiên này

- `core/engine.py`, `models.py`, `cost_model.py`, `execution.py`, `portfolio.py`, `causality.py`, `data_validator.py`, `data_loader.py` (L20–239)
- `strategies/base_strategy.py`
- `indicators/sessions.py`, `trend.py` (L61–100), `INDICATORS.md` (L1–40)
- `core/BACKTEST_ENGINE.md` (L185–207)
- `benchmark_engine.py`
- `configs/*.yaml`, `data/metadata/*`
- Phần đầu `tests/test_engine.py` và `tests/test_backtest_models.py`; danh sách test của `test_engine.py`, `test_intraday_gaps.py` và `test_stage4_review.py`

### 2.3 Bằng chứng thực thi mới

| ID | Lệnh / probe | Kết quả |
|---|---|---|
| EV-01 | `pytest -p no:cacheprovider -q` | **296 passed in 3.80s** (khớp `07_TEST_RESULTS.md`) |
| EV-02 | `probes.py` (31 probe chức năng) | Xem `probe_results.json`; trích dẫn từng mục ở §3 |
| EV-03 | `perf.py` (timing + peak working set, mỗi case một tiến trình) | `perf_results*.jsonl`; peak memory chỉ hợp lệ ở lần chạy lớn (lần đầu ghi 0 do lỗi ctypes, đã sửa) |
| EV-04 | `probes2.py f2b` | Tick rounding có slippage: 0 lệch ở BTC/EURUSD/XAU |
| EV-05 | `probes2.py hash` ×2 tiến trình | SHA256 `e43265bc…fb2814` giống nhau; 290 trades |
| EV-06 | `benchmark_engine.py --sizes 200 --repeats 1` | Chạy được; `outputs_identical: true` (hằng số) |

### 2.4 Ngoài phạm vi / không thực hiện

- Không chạy CLI `inspect_data.py`/`inspect_indicators.py`, vì có thể ghi artifact vào `data/processed`, `reports/runs`.
- Không chạy engine trên CSV thật (metadata bị chặn, xem QBS-17).
- Không chạy benchmark trực tiếp 1,44M nến cho engine; đã đo 1,0M.
- Không kiểm tra coverage (công cụ không có sẵn). Chưa đọc toàn văn `00A`, `00B`, `.clinerules/*`, `MANIFEST.md` (đọc dòng 1 và grep).

---

## 3. Findings Consolidation

**Quy ước ID hợp nhất:** `QBS-xx`. Cột “Nguồn” giữ nguyên ID gốc. `NEW` là phát hiện mới của phiên tổng hợp.

**Trạng thái:**
- **CONFIRMED-RUN:** tái hiện bằng thực thi.
- **CONFIRMED-STATIC:** khẳng định bằng mã, không cần chạy.
- **SUSPECTED / NEEDS VERIFICATION:** chưa đủ bằng chứng.
- **DESIGN LIMITATION:** giới hạn thiết kế.
- **FALSE POSITIVE / NOT REPRODUCED:** bị bác bỏ hoặc không tái hiện được.

### 3.1 Bảng hợp nhất

| QBS | Nguồn (mức gốc) | File / hàm | Bằng chứng gốc | Bằng chứng phiên này | Trạng thái | Mức cuối | Ảnh hưởng hệ thống | Hành động |
|---|---|---|---|---|---|---|---|---|
| **QBS-01** | CORE-F2 phần exact-touch (P1, SUSPECTED) | `cost_model.py::side_bar` L34–35; `execution.py::protective_exit` L31–32 | Đọc mã | Spread 4e-5, so `Bid_low <= SL` trên lưới: **1.752/4.286 sai**; k=2,10,16: 0 sai | **CONFIRMED-RUN** | **P0** (nâng) | SL/TP chạm đúng biên bị bỏ sót, thiên lệch lạc quan, không đối xứng theo spread | So sánh theo số nguyên tick |
| QBS-02 | IND-4 (P1, CONFIRMED) + STR-P1-01 (P1, SUSPECTED) + STR-P1-03 (P1, CONFIRMED) | `core/causality.py` L28–36; `tests/test_indicators.py` L273; `inspect_indicators.py` L95–96 | Đọc mã | Rò rỉ `+1e-5` trên giá 1,08: **PASS**. Input 1 dòng: PASS. `cutoffs=[]`: PASS. Index đảo ngược: PASS. `np.int64` cutoff: bị từ chối | **CONFIRMED-RUN** | **P0** (nâng) | Lưới an toàn duy nhất cho look-ahead có thể cho PASS giả | `check_exact=True`, kiểm tra đầu vào |
| QBS-03 | CORE-F5 (P1) + IND-10 (P2) + STR-P1-06 (P1) | `engine.py` L214–229 (`assumptions`); `pyproject.toml` L12–15; Git | Đọc mã, git status | `assumptions` thiếu `data_sha256, strategy, strategy_params, library_versions, git_commit`; git: 6 M + untracked | **CONFIRMED-RUN** | **P0** (nâng, cổng nghiên cứu) | Không thể truy ngược kết quả về dữ liệu/mã/môi trường | Commit/tag, lock, ghi provenance |
| QBS-04 | CORE-F1 (P1) + STR-P1-05 (P1, SUSPECTED) | `engine.py` L134, L186–188; `base_strategy.py` L28–33 | Ước lượng 4–5 h | Full-prefix: 725 µs/nến @4k → 1.172 @16k → 1.633 @32k (bậc hai); ngoại suy 1,44M ≈ **19 h**. Gia tăng: 1M nến = **554 s, peak 1,31 GB** | **CONFIRMED-RUN** | P1 | Đường mặc định không dùng được cho dữ liệu dài | NumPy hóa vòng lặp, bỏ deep copy, giới hạn history |
| QBS-05 | NEW (liên quan CORE-F1 mục 3) | `engine.py` L199–209 | — | Strategy kiểu mức: **500 orders / 1 fill / 498 rejected** trên 500 nến; 1M nến: 999.981 orders, ~2M events | **CONFIRMED-RUN** | P1 | Phình bộ nhớ; log rejected che tín hiệu thật | Không tạo Order khi biết chắc bị từ chối, hoặc đếm gộp |
| QBS-06 | CORE-F3 (P1, DESIGN LIMITATION + SUSPECTED) | `portfolio.py` L29–31; `engine.py` L154–157 | Đọc mã | BUY gap dưới SL: event `rejected` chuỗi tự do, 0 fill, **không có bộ đếm** | **CONFIRMED-RUN** (hành vi) / DESIGN LIMITATION | P1 | Bỏ qua kịch bản đuôi xấu nhất, kết quả có thể lạc quan | Mã lý do + bộ đếm; tùy chọn `fill_and_stop` |
| QBS-07 | CORE-F4 (P1) | `engine.py` L84–209; `base_strategy.py` L9–10; `BACKTEST_ENGINE.md` L29 | Đọc mã | Tái dùng instance stateful: run1 = 1 fill, run2 = 0 fill, `a == b` False | **CONFIRMED-RUN** | P1 | Hai lần chạy cùng dữ liệu cho kết quả khác | `deepcopy` hoặc hook `reset()` |
| QBS-08 | IND-1 (P0 có điều kiện, SUSPECTED) ↔ CORE-F6 (P2) | `sessions.py` L3–4, L42; `INDICATORS.md` L12–14; `engine.py` L108–111, L186–188 | Ví dụ tay | Index 07:59/08:00/16:59/17:00 → `active=[F,T,T,F]`: đúng với nhãn **open**, sai với nhãn **close** mà tài liệu yêu cầu | **CONFIRMED-RUN** (mâu thuẫn hợp đồng); **không có rò rỉ tương lai** | **P1** (hạ từ P0) | Làm theo tài liệu thì lệch 1 nến ở hai biên phiên (ORB, session range, VWAP) | Một quy ước nhãn duy nhất + test ghim |
| QBS-09 | DATA-1 (P1, CONFIRMED) | `data_validator.py` L109–146, L191–192; `engine.py` L112 | Đọc mã | Off-grid hỗn hợp: `ready_for_research=True`. Lệch đều +30 s: **không cảnh báo nào**. Engine chấp nhận chạy | **CONFIRMED-RUN** | P1 | Sai `timestamp_kind`/đơn vị có thể lọt vào mô phỏng | Lỗi `off_grid_timestamps` |
| QBS-10 | STR-P1-02 (P1, DESIGN LIMITATION) + NEW | `engine.py` L102, L187; `causality.py` docstring | Đọc mã | Cột tính sẵn `close.shift(-2)` đi thẳng vào strategy: **102/149 lệnh thắng**, engine/validator không cảnh báo | **CONFIRMED-RUN** | P1 | Chỉ báo causal không đảm bảo pipeline causal | Whitelist cột hoặc cảnh báo; test pipeline từ dữ liệu thô |
| QBS-11 | STR-P1-04 (P1) | `causality.py` L28 | Ước lượng | 1k: 1,8 s; 2k: 7,0 s; 4k: 27,4 s (×3,9 mỗi lần gấp đôi) | **CONFIRMED-RUN** | P1 | Không thể dùng mặc định trên dữ liệu thật | Bắt buộc `cutoffs` khi n lớn |
| QBS-12 | IND-2 (P1, CONFIRMED O(n²)) | `trend.py::parabolic_sar` L74; `market_structure.py::structure_breaks` L67 | Ước lượng hàng giờ | SAR: 368 → 362 → 364 µs/nến ở 2k → 32k → 64k. `structure_breaks`: 390 → 377. **Tuyến tính** trên pandas 3.1.1 | **FALSE POSITIVE** (độ phức tạp, pandas 3.1.1); NEEDS VERIFICATION trên pandas 2.x | P1 (gộp QBS-13) | ≈ 520–545 s mỗi lần gọi ở 1,44M | Gộp vào tối ưu vòng lặp |
| QBS-13 | IND-3 (P1, CONFIRMED cấu trúc) | `moving_averages.py` L50, L61; `trend.py`; `momentum.py` | Ước lượng | 100k: rma 7,9; atr 8,0; rsi 16,0; adx 31,4; supertrend 35,3 µs/nến. **ADX 1,44M: 149,8 s** (104 µs/nến) | **CONFIRMED-RUN** | P1 | Quét tham số nhân thời gian lên nhiều lần | NumPy hóa, oracle bit-exact |
| QBS-14 | IND-6 (P1, DESIGN LIMITATION) | `market_structure.py` L109–111 | Ví dụ tay | High “ngày trước” của thứ Hai = **109,8** (mảnh Chủ nhật) thay vì 110,2 (thứ Sáu) | **CONFIRMED-RUN** / DESIGN LIMITATION (đã ghi tài liệu) | P1 | Pivot sai cho thứ Hai nếu dùng ngây thơ | `min_bars` hoặc cờ phiên không đầy đủ |
| QBS-15 | NEW | `engine.py` L36–65 (`ConversionRates`) | — | `at(t)` trả giá trị có nhãn **đúng bằng t**; không tài liệu hóa nhãn là thời điểm công bố hay nhãn nến | **CONFIRMED-STATIC** (thiếu hợp đồng); tác động NEEDS VERIFICATION | P1 | Nếu truyền close nến FX gắn nhãn open thì dùng tỷ giá tương lai trong nến | Ghi rõ “publication timestamp”, test |
| QBS-16 | DATA-3 (P1) + CORE-F8 (`pip_size` không dùng) | `data/metadata/symbols.json`; `datasets.json`; `models.py` L21–49 | So sánh JSON | `symbols.json` **không được mã Python nào đọc** (grep); XAU point lệch 100× | **CONFIRMED-STATIC** (mâu thuẫn dữ liệu); tác động runtime: **không** | P2 (hạ) | Rủi ro tiềm ẩn nếu ai đó nạp file legacy | Đánh dấu legacy + test nhất quán |
| QBS-17 | NEW (từ DATA §A, 09 §6) | `datasets.json`; `metadata_template.yaml`; `Instrument.from_metadata` | — | EURUSD và XAUUSD: **15 blocker** mỗi bộ; thiếu `tick_size, contract_size, quantity_unit, quote_currency, minimum_quantity_increment`; `point_size` không phải trường của `Instrument` | **CONFIRMED-RUN** | P1 (điều kiện tiên quyết, **không phải bug**) | Không có backtest dữ liệu thật nào khả thi | Xác nhận metadata có bằng chứng |
| QBS-18 | CORE-F6 (P2, DESIGN LIMITATION) | `engine.py` L170–181 | Đọc mã | Nhãn open: `states[0].timestamp = index[1]`; fill intrabar mang nhãn `opening` | **CONFIRMED-RUN** / DESIGN LIMITATION | P2 → P1 khi làm metrics | Lớp metrics ghép theo timestamp dễ lệch 1 nến | Thêm `bar_index` |
| QBS-19 | CORE-F7 (P2) | `engine.py` L154–157; `cost_model.py` L36–37 | Đọc mã | Spread 250: lỗi `"executable price must be finite and positive."` không có timestamp; mọi `ValueError` từ `open` thành “rejected” | **CONFIRMED-RUN** | P2 | Lỗi cấu hình/lập trình bị che thành event | `OrderRejected` + ngữ cảnh nến |
| QBS-20 | CORE-F2 phần BTC tick rounding (P1, SUSPECTED) | `cost_model.py` L48–51 | Lập luận ulp | 2.000 giá BTC (slip 0, 1, 3 tick), 20.000 EURUSD, 20.000 XAU: **0 lệch** | **NOT REPRODUCED** | P2 (giữ test) | Chưa thấy ảnh hưởng | Thêm test hồi quy; sửa chung với QBS-01 |
| QBS-21 | IND-5 (P1, SUSPECTED) | `volatility.py` L41, L47; `momentum.py` L91 | Lập luận | Đầu vào đề xuất: %B = NaN, bandwidth = 0,0, std = 0,0. **CCI = 0,0** (tài liệu hứa NaN khi chia 0) | **NOT REPRODUCED** (số rác); lệch hợp đồng nhỏ ở CCI | P2 (hạ) | Thấp | Test thêm đầu vào; thống nhất NaN |
| QBS-22 | DATA-2 (P1, SUSPECTED) | `data_loader.py` L126–192; `engine.py` L94–96 | Đọc mã | `load_csv(diagnostic=False)` trả NaN; **engine chặn** (`close_missing_or_non_numeric`) | **CONFIRMED-RUN** (loader) / **FALSE POSITIVE** cho đường engine | P2 (hạ) | Chỉ còn rủi ro ở entry point không qua engine (`inspect_indicators.py` L49 dùng `load_parquet` không validate) | Raise ở chế độ nghiên cứu |
| QBS-23 | DATA-4 (P2) | `data_loader.py::write_json` L195–201 | Đọc mã | NaN để lại **file 21 byte** | **CONFIRMED-RUN** | P2 | Báo cáo cụt, không ghi đè được | `json.dumps` trước + temp/link |
| QBS-24 | DATA-5 (P2) + CORE-F8 (config) | `configs/config.yaml` L6, L11, L14 | Đọc YAML | `pd.Timedelta("H1")` → **ValueError**; `include_swap: true` mâu thuẫn `CostModel` L26–27; runner chưa đọc YAML | **CONFIRMED-RUN** | P2 (P1 khi nối runner) | Không có tác động hiện tại | Sửa cùng runner |
| QBS-25 | DATA-6 (P2, SUSPECTED) | `data_loader.py` L148–151 | Lập luận | `"1704153600000.5"` → `…00:00:00.000500`, `invalid_count = 0` | **CONFIRMED-RUN** (epoch phân số); `unix_ns` > 2^53 NEEDS VERIFICATION | P2 | Thấp với M1 `unix_ms` | Parse nguyên |
| QBS-26 | DATA-7 (P2, SUSPECTED) | `data_loader.py` L146, L173; validator L138 | Đọc mã | `validate_data` 1,44M: **0,15 s**, peak 318 MB; loader CSV 1,44M chưa đo | **PARTIAL** (validator ổn); loader NEEDS VERIFICATION | P2 | Thấp | Đo loader, giới hạn `intraday_gaps` |
| QBS-27 | DATA-8 (P2) | `data_loader.py::save_parquet` L207, L223 | Đọc mã | — | **CONFIRMED-STATIC** | P2 | Thấp | So với raw đã resolve; xử lý `OSError` |
| QBS-28 | IND-7 (P2) + STR-P1-03 (np.int64) + NEW (engine) | `_utils.py` L16; `causality.py` L29; `engine.py` L104–107, L192 | Đọc mã | `sma(np.int64(3))` bị từ chối; `deviations=nan` cho toàn NaN; `signal_history_limit=np.int64(5)` bị từ chối; **`signal=True` được chấp nhận** | **CONFIRMED-RUN** | P2 | Lỗi kiểu khó hiểu; bool lọt vào tín hiệu | `numbers.Integral`, `np.isfinite`, loại bool |
| QBS-29 | IND-8 (P2) | `volatility.py` L103 | Đọc mã | — | **CONFIRMED-STATIC** | P2 | Bộ nhớ ở 1,44M | So sánh trực tiếp |
| QBS-30 | IND-9 + CORE-F8 + STR-P2-08 (P2) | README; `pyproject.toml` L15; `run_backtest.py` L4–6; `custom_indicators.py` | Đối chiếu tài liệu | README nói “1 test”, thực tế 296; README nói “chưa cần pyarrow” nhưng pyproject yêu cầu | **CONFIRMED-STATIC** | P2 | Gây hiểu nhầm | Đồng bộ tài liệu |
| QBS-31 | STR-P2-07 (P2) | `benchmark_engine.py` L74–75 | Đọc mã | `assert` rồi `"outputs_identical": True` hằng số; chạy được ở 200 nến | **CONFIRMED-STATIC** + RUN | P2 | Benchmark không tự chứng minh | `raise SystemExit`, so mọi lần lặp |
| QBS-32 | NEW | `engine.py` L143–144; `BACKTEST_ENGINE.md` L8, L15 | — | SELL khi đang long: `rejected position_already_open`, vị thế vẫn long | **CONFIRMED-RUN** / DESIGN LIMITATION (đã tài liệu hóa) | P2 | Strategy viết sai quy ước sẽ âm thầm bị bỏ lệnh | Bộ đếm rejection (QBS-06) |
| QBS-33 | NEW | `cost_model.py` L34, L55 | — | Nguồn Bid/Ask: BUY lệch cả `s`, SELL lệch 0, nhưng `spread_cost` ghi `s/2` mỗi phía (tổng khứ hồi vẫn đúng) | **CONFIRMED-STATIC** | P2 | Chỉ sai phân bổ chẩn đoán từng phía (vị thế mở cuối mẫu bị ghi thiếu) | Ghi theo offset thực |
| QBS-34 | DATA §F; 09 §6 | `engine.py` L131–150 | — | Lệnh khớp ở open của nến **có dữ liệu kế tiếp**, kể cả sau gap trong ngày; không ghi độ trễ | **CONFIRMED-STATIC** / DESIGN LIMITATION (đã tài liệu hóa) | P2 | Fill xa thời điểm tín hiệu sau gap | Ghi `fill_delay` vào event |
| QBS-35 | CORE-D13 (test yếu) | `tests/test_engine.py` L143–155 | Đọc test | Test cũ chỉ sửa nến cuối; probe phiên này sửa k ∈ {50, 137, 250, 399}: **0 vi phạm** | Hành vi engine **VERIFIED-RUN**; test vẫn yếu | P2 | — | Nâng cấp test (§9) |

### 3.2 Phát hiện “đúng”: đã kiểm chứng bằng thực thi

| Hạng mục | Bằng chứng |
|---|---|
| Tín hiệu cuối nến i, khớp open nến kế tiếp, cả nhãn open lẫn close | Test hiện có + `SYS-close_labelled_fill_timing`: submit 00:00, fill 00:00 (open nến 1), giá 102 |
| Bất biến kế toán | 20k nến, 904 trades: `balance − vốn = Σnet − commission vào lệnh còn mở`; `equity = balance + unrealized` cho mọi state; không có fill trước submit; `net = gross − 2 commission` |
| Nhân quả engine | Sửa nến k: states/fills/orders trước k không đổi |
| Tất định | Cùng tiến trình `r == r2`; hai tiến trình cùng SHA256 |
| Cổng dữ liệu | Engine chặn NaN token (QBS-22) và metadata chưa xác nhận (QBS-17) |
| Gap SL tại open, TP gap tại target, SL trước TP khi cùng chạm | Test hiện có (`test_gap_stop…`, `test_same_bar_brackets_sl_first`), mã `execution.py` L27–36 |

---

## 4. Duplicated and Conflicting Findings

### 4.1 Trùng lặp đã hợp nhất (giữ nguồn)

| QBS | Các mục gốc trùng | Ghi chú |
|---|---|---|
| QBS-02 | IND-4, STR-P1-01, STR-P1-03 | Hai phiên thấy cùng dung sai mặc định từ hai góc (test và helper) |
| QBS-03 | CORE-F5, IND-10, STR-P1-06 | Ba mức khác nhau: P1/P2/P1 |
| QBS-04 | CORE-F1, STR-P1-05 | STR suy đoán, CORE phân tích mã, phiên này đo |
| QBS-10 | STR-P1-02 + phát hiện tích hợp mới | |
| QBS-24, QBS-30 | DATA-5, CORE-F8, IND-9, STR-P2-08 | Tài liệu và cấu hình |
| QBS-28 | IND-7, STR-P1-03 (np.int64), engine | Cùng mẫu `isinstance(x, int)` ở 3 module |

### 4.2 Mâu thuẫn

| # | Kết luận A | Kết luận B | Bằng chứng / nguồn | Nguyên nhân | Cách kiểm chứng | Kết luận hiện tại |
|---|---|---|---|---|---|---|
| C1 | IND-1: **P0 có điều kiện**, nhãn phiên có thể gây lệch | CORE: không P0; F6 nhãn thời gian chỉ là **P2 design limitation** | `sessions.py` L3–4 + L42; `INDICATORS.md` L12–14; `engine.py` L108–111, L187 (prefix giữ nhãn input) | Mỗi phiên chỉ thấy một nửa hợp đồng | Probe `IND-1`: `[F,T,T,F]` | Mã đúng cho nhãn open, tài liệu đòi nhãn close nên mâu thuẫn **thật**. **Không có dữ liệu tương lai**: nến bị xếp sai đều đã đóng. Hạ xuống **P1** (QBS-08) |
| C2 | IND-2: SAR/`structure_breaks` **O(n²), hàng giờ** (CONFIRMED) | Đo phiên này: tuyến tính | `trend.py` L74; `perf_results*.jsonl` | Ước lượng tĩnh bỏ qua chi phí cố định của Python và Copy-on-Write của pandas 3 | Đo 2k → 64k | **FALSE POSITIVE** về độ phức tạp trên pandas 3.1.1; vẫn chậm ≈ 9 phút/1,44M. NEEDS VERIFICATION trên pandas 2.x (pyproject cho phép `>=2.2`) |
| C3 | CORE-F1: full-prefix ≈ **4–5 h** | Đo phiên này | `engine.py` L187 | Ngoại suy tuyến tính từ 2 điểm nhỏ | 1k → 32k nến | Bậc hai rõ ở > 8k; ngoại suy ≈ **19 h** (ước lượng từ mô hình `a + c·n`). CORE-F1 đúng hướng, **đánh giá thấp** mức độ |
| C4 | DATA-2: P1, dữ liệu lỗi có thể vào mô phỏng | CORE: engine validate trước khi chạy | `engine.py` L94–96 | DATA không có mã engine | Probe `DATA-2` | Engine chặn; hạ xuống **P2** (QBS-22). Rủi ro còn ở entry point khác |
| C5 | DATA-1: off-grid là **P1** | Chính sách dự án: gap trong ngày chỉ cảnh báo | `00_PROJECT_OVERVIEW.md` L49–55; validator L114, L145–146 | Gộp “off-grid” với “gap” | Probe `DATA-1` | Chính sách chỉ miễn **gap**. Off-grid là sai cấu trúc nhãn; lệch đều còn không có cảnh báo. Giữ **P1** (QBS-09), không đụng chính sách gap |
| C6 | STR-P1-01: SUSPECTED | IND-4: CONFIRMED | `causality.py` L34–36 | Khác mức xác tín | Probe `IND-4` | **CONFIRMED-RUN**, nâng **P0** (QBS-02) |
| C7 | CORE-F2 coi hai rủi ro float là một | — | `cost_model.py` | — | Probe F2a/F2b + `probes2 f2b` | Exact-touch **CONFIRMED**; BTC rounding **NOT REPRODUCED**: tách thành QBS-01 và QBS-20 |
| C8 | CORE: chi phí và spread đúng | DATA-3/5: point_size XAU lệch 100×, `slippage_points`, `include_swap` | grep `symbols.json`; `run_backtest.py` L4–6 | DATA không thấy engine | grep + probe metadata | Không có đường runtime nào đọc `symbols.json`/`config.yaml`, nên **tiềm ẩn**, không phải lỗi hiện hành (QBS-16, QBS-24). Khi nối runner sẽ thành P1 |
| C9 | STR: TP gap dùng target “bất đối xứng”, cần xác nhận | CORE: hành vi đúng, nên giữ | `execution.py` L29–30; `BACKTEST_ENGINE.md` | STR không có mã | Đọc mã + test hiện có | **DESIGN LIMITATION** có chủ đích, thận trọng; ghi vào assumptions |
| C10 | CORE-F4: thiếu reset là **lỗi P1** | `BACKTEST_ENGINE.md` L29: strategy tự chịu trách nhiệm reset | — | Ranh giới trách nhiệm | Probe F4 | Tài liệu hóa ≠ an toàn. Tái lập là yêu cầu hệ thống nên giữ **P1** (QBS-07) |
| C11 | INDICATORS: không look-ahead | STR-P1-02: không phát hiện cột tính sẵn | `engine.py` L102, L187 | Phạm vi khác nhau | Probe `future_column_passthrough` | Cả hai đúng trong phạm vi riêng; **khoảng trống tích hợp** là QBS-10 |
| C12 | Ba phiên: “296 passed” chưa kiểm chứng | 00/07: 296 passed | EV-01 | Không có môi trường | Chạy lại | **Đã tái hiện 296 passed** (không chứng minh coverage) |
| C13 | CORE-F5/STR-P1-06: P1; IND-10: P2 | — | — | Khác trọng số | — | Hợp nhất **P0 cổng nghiên cứu** (QBS-03): kết quả không truy xuất được không thể là bằng chứng nghiên cứu |

---

## 5. Cross-Module Integration Analysis

| Giao diện | Đầu vào → đầu ra | Kiểu | Timestamp / TZ | Đơn vị | NaN / warm-up | Thời điểm dùng được | Điều kiện thất bại | Test hiện có | Test còn thiếu | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|---|
| **DATA: Loader → Validator** | `load_csv(path, metadata) → LoadResult(data, diagnostics)`; `validate_data(df, metadata) → dict` | DataFrame float64, index `DatetimeIndex[UTC]` | UTC; nhãn theo `timestamp_kind` (không chuyển đổi) | Giá theo `price_type`; volume chỉ là metadata | Token lỗi → NaN/NaT, **không raise** ở chế độ nghiên cứu (QBS-22) | — | Encoding chưa xác nhận → raise | `test_data_loader.py`, `test_data_validator.py`, `test_intraday_gaps.py` | Off-grid (QBS-09); epoch phân số (QBS-25); khứ hồi Parquet → validate | Hoạt động; P1 off-grid |
| **Validator → Indicators** | Validator trả **báo cáo**, không trả DataFrame | — | Indicators chỉ yêu cầu UTC + đơn điệu (`_utils.py`) | — | Indicators chấp nhận NaN | — | Không có cổng chung | Không có | Test entry point `inspect_indicators.py` bỏ qua validator | **Không có cổng ràng buộc** |
| **Indicators → Strategy** | Series/DataFrame cùng index | float / `pd.NA` | Hàm phiên đòi nhãn **close**; engine truyền nhãn **gốc** (QBS-08) | Giá | Warm-up = NaN; strategy phải xuất 0 | Sau đóng nến | Không có test hợp đồng nhãn | `test_indicators.py` (prefix, rtol 1e-5) | Nhãn open/close; prefix bit-exact | **Mâu thuẫn hợp đồng** |
| **Strategy → Engine** | `generate_signal(prefix) → Series{signal, exit, sl, tp}` | `signal ∈ {-1, 0, 1}` (bool lọt, QBS-28); `exit` bool; SL/TP giá tuyệt đối | Prefix giữ nhãn input; Order `submitted_at = closing` | SL/TP đơn vị giá | NaN signal → raise; NaN sl/tp → None | Order khớp ở open kế tiếp | SELL khi long → rejected (QBS-32); cột lạ không bị chặn (QBS-10) | `test_engine.py`, `test_stage4_review.py` | Reset strategy (QBS-07); cột tương lai; history bounded vs full bit-exact ở n lớn | Hoạt động; P1 |
| **Engine → Execution/Cost** | `side_bar(bar, price_type, side)`; `protective_exit(pos, bar)`; `CostModel.fill(...)` | dict float; `ExitDecision`; `Fill` | Fill open = `opening`; intrabar = `opening` (QBS-18) | Spread/slippage: đơn vị giá; commission: tiền tài khoản × quantity khai báo | — | — | Giá ≤ 0 → ValueError không ngữ cảnh (QBS-19) | Test cost/execution/engine | Exact-touch (QBS-01); gap SHORT ở cấp engine; EXIT + SL cùng nến | **P0 QBS-01** |
| **Execution → Portfolio** | Engine gọi `Portfolio.open(order, fill, rate)` / `close(fill, rate)` | `Trade`, `AccountState` | `rate.at(opening)` cho fill; `rate.at(closing)` cho mark | Notional = units × giá × rate (account/quote) | — | — | Bracket sai → rejected (QBS-06) | `test_portfolio.py`, `test_stage4_review.py` | Hợp đồng nhãn tỷ giá (QBS-15); FX ≠ USD với nhãn close | Hoạt động; P1 hợp đồng FX |
| **Portfolio → Metrics** | `BacktestResult(orders, fills, trades, states, events, open_position, assumptions)` | tuple dataclass | states nhãn **closing** | Tiền tài khoản | — | — | — | — | Toàn bộ | **NOT IMPLEMENTED** (`core/metrics.py` 1 dòng) |
| **Metrics → Reports** | — | — | — | — | — | — | — | — | Toàn bộ | **NOT IMPLEMENTED** |
| **Runner/Config → toàn hệ thống** | `config.yaml` → engine | — | — | `slippage_points`, `H1` không tương thích (QBS-24) | — | — | — | — | Toàn bộ | **NOT IMPLEMENTED** (`run_backtest.py` L4–6 chỉ in) |
| **Metadata thật → Instrument** | `datasets.json` + template → `Instrument.from_metadata` | — | — | `point_size` không có trong `Instrument` | — | — | **15 blocker** | `test_backtest_models.py` (metadata tổng hợp) | Test metadata thật | **Bị chặn** (QBS-17) |

> [!NOTE]
> Giới hạn được chấp nhận: kiểm tra gap chỉ cho cặp timestamp liên tiếp **cùng ngày UTC**; khoảng qua ngày, cuối tuần và lễ được bỏ qua (`cross_day_interval_count_ignored`). Không yêu cầu lịch Forex đầy đủ. Hệ quả cần ghi trong mọi kết quả: `intraday_gap_check_passed ≠ full_calendar_verified`, và fill sau gap dùng nến có dữ liệu kế tiếp (QBS-34).

---

## 6. Critical Correctness Risks

| # | Rủi ro | Trạng thái kiểm chứng | QBS | Ghi chú |
|---|---|---|---|---|
| 1 | Look-ahead trong engine | **Không phát hiện**: VERIFIED-RUN (sửa nến k, prefix copy, `opening < submitted_at`) | — | Chỉ một strategy probe; nên mở rộng (§9) |
| 2 | Future feature leakage | **Khoảng trống có thật**: cột tính sẵn đi qua; công cụ prefix lỏng | QBS-02 (P0), QBS-10 | Indicators không có `shift(-n)` (IND, chưa xác minh lại toàn bộ) |
| 3 | Sai thời điểm tín hiệu/khớp | Đúng cho nhãn open/close (VERIFIED-RUN). Nhãn phiên mâu thuẫn | QBS-08, QBS-18, QBS-34 | |
| 4 | Bid/Ask, chi phí | Giá khớp đúng (test + đọc mã); chẩn đoán spread lệch phân bổ | QBS-33 | Swap bị chặn rõ ràng |
| 5 | SL/TP và gap | **Lỗi chạm biên float** | **QBS-01 (P0)**, QBS-06 | Gap SL/TP đúng thiết kế |
| 6 | P/L, equity, drawdown | Bất biến đúng trên 20k nến. Drawdown chỉ tính trong probe (−0,17%); **metrics chưa có** | — | |
| 7 | Volume, contract size, tiền tệ | Đúng trong `Instrument.units`/Portfolio. Metadata thật thiếu; hợp đồng tỷ giá chưa rõ | QBS-15, QBS-16, QBS-17 | |
| 8 | Warm-up / trạng thái chỉ báo | Warm-up NaN → strategy phải xuất 0 (engine raise nếu NaN). State strategy không reset | QBS-07 | |
| 9 | Tái lập | Tất định OK; truy xuất **FAIL** | **QBS-03 (P0)** | |
| 10 | Tối ưu làm đổi logic | Chưa tối ưu. Golden-master đã có ở dạng nhỏ (`test_incremental_and_legacy_results_are_identical`) | QBS-04, QBS-13 | Bắt buộc oracle bit-exact khi tối ưu |

**Ngoài phạm vi, không tính P0:** đa công cụ, nhiều vị thế, đòn bẩy/margin, swap, partial close, limit/stop order, lịch Forex đầy đủ, walk-forward/sensitivity.

---

## 7. Performance and Scalability

Đo trên máy kiểm toán, mỗi case một tiến trình, dữ liệu tổng hợp M1 kiểu EURUSD.

| Thành phần | n | Thời gian | µs/nến | Peak RAM | Ngoại suy 1,44M |
|---|---:|---:|---:|---:|---|
| `validate_data` | 1.440.000 | 0,15 s | 0,1 | 318 MB | Đo trực tiếp |
| `sma` | 1.440.000 | 0,03 s | 0,02 | — | Đo trực tiếp |
| `adx` | 1.440.000 | 149,8 s | 104 | 286 MB | Đo trực tiếp |
| `rma` / `atr` / `rsi` / `supertrend` | 100.000 | 0,79 / 0,80 / 1,60 / 3,53 s | 7,9 / 8,0 / 16 / 35 | — | ≥ 11 / 11 / 23 / 51 s (có thể tăng theo n như ADX) |
| `parabolic_sar` | 2k → 64k | 0,74 → 23,3 s | 368 → 364 | 92 MB | ≈ 525 s (tuyến tính) |
| `structure_breaks` | 2k → 64k | 0,78 → 24,1 s | 390 → 377 | 95 MB | ≈ 543 s |
| Engine full-prefix | 1k / 4k / 16k / 32k | 0,7 / 2,9 / 18,7 / 52,3 s | 706 / 725 / 1.172 / 1.633 | 134 MB @32k | **≈ 19 h** (mô hình bậc hai, ước lượng) |
| Engine gia tăng (`history=1`) | 10k / 100k / **1M** | 2,5 / 49 / **554 s** | 251 / 490 / 554 | 101 / 215 / **1.309 MB** | ≈ 13–14 phút, ≈ 1,9 GB (ước lượng) |
| `check_prefix_invariance` (mọi prefix) | 1k / 2k / 4k | 1,8 / 7,0 / 27,4 s | — | — | Không khả thi |

**Nhận xét**

- Chi phí mỗi nến của đường gia tăng tăng từ 251 lên 554 µs khi n tăng (10k → 1M). Khả năng cao do danh sách đối tượng phình: ~1M `Order` + 2M event + 1M `AccountState` (QBS-05). Nguyên nhân này **NEEDS VERIFICATION** bằng profiling.
- Benchmark 10k/100k/1M theo yêu cầu: **đã chạy cho engine gia tăng**. Đường full-prefix chỉ chạy đến 32k (1M không khả thi).

---

## 8. Reproducibility

| Khía cạnh | Bằng chứng | Kết quả |
|---|---|---|
| Tất định trong tiến trình | `r == r2` (20k nến, strategy mới mỗi lần) | PASS |
| Tất định liên tiến trình | SHA256 giống nhau qua 2 tiến trình | PASS |
| Tái dùng strategy | run2 ≠ run1 | **FAIL** (QBS-07) |
| Provenance kết quả | Thiếu hash dữ liệu, strategy/params, phiên bản, commit | **FAIL** (QBS-03) |
| Mã gắn commit | 6 M + untracked | **FAIL** |
| Khóa phụ thuộc | Chỉ khoảng phiên bản; chỉ kiểm trên 1 tổ hợp | **FAIL** |
| Hành vi theo phiên bản pandas | Đo hiệu năng chỉ trên pandas 3.1.1; pyproject cho phép 2.2 | NOT VERIFIED |
| Script phụ thuộc artifact bị gitignore | `inspect_indicators.py` L27 hardcode `data/processed/inspection-…` | CONFIRMED-STATIC |

---

## 9. Missing Integration Tests

> [!WARNING]
> Các test dưới đây là **thiết kế, chưa tồn tại trong repo**. Probe của phiên này đã chạy các phiên bản tương tự ngoài repo (ghi ở cột “Probe”), nhưng **không tính là test của dự án**.

Đề xuất file mới: `tests/test_integration_e2e.py`. Marker `slow` phải đăng ký trong `pyproject.toml` vì đang bật `--strict-markers`.

| ID | Test | Thiết lập | Khẳng định | Probe phiên này |
|---|---|---|---|---|
| IT-01 | E2E BUY → TP và SELL → SL | CSV tổng hợp (`unix_ms`, Bid, nhãn open) → `load_csv` → `validate_data` → engine; strategy SMA(5/20) dùng `indicators.moving_averages.sma` | Fill = Ask/Bid open kế tiếp ± slippage, làm tròn bất lợi; PnL tính tay | Một phần |
| IT-02 | HOLD | `signal=0` suốt khi có vị thế | Không có Order; vị thế giữ nguyên | Test hiện có |
| IT-03 | SL/TP chạm đúng biên | Spread 2/4/10 tick; SL đặt đúng `low − s/2` | Kích hoạt 100% | F2a (**FAIL hiện tại**) |
| IT-04 | Gap SL và gap TP, long và short, ở cấp engine | Nến mở vượt SL/TP | SL tại open; TP tại target; ambiguous đúng | Một phần trong test hiện có |
| IT-05 | Spread + slippage + commission | `CostModel(2 tick, 1 tick, 3.5)` | `Σ(spread + slippage)` chỉ nằm trong giá; balance trừ commission đúng 2 lần mỗi trade | Có |
| IT-06 | Giao dịch cuối mẫu | Tín hiệu ở nến cuối; vị thế mở ở nến cuối | Event `unfilled/end_of_data`; `open_position` được mark, không đóng ép | Test hiện có |
| IT-07 | Khoảng nghỉ qua ngày + gap trong ngày | Thứ Sáu 21:00 → Chủ nhật 22:00; gap 15 phút trong ngày | Gap qua ngày bị bỏ qua (đếm); gap trong ngày → warning; fill ở nến có dữ liệu kế tiếp | Có (20k random) |
| IT-08 | Chỉ báo có warm-up | ATR(14) + RSI(14); strategy xuất 0 khi NaN | Không có Order trước nến thứ 15; NaN signal → raise | — |
| IT-09 | Prefix invariance toàn pipeline | Sửa nến k ∈ {đầu, giữa, cuối, ranh giới ngày} | states/fills/orders có timestamp < `opening_k` giữ nguyên **bit-exact** | Có (0 vi phạm) |
| IT-10 | Bất biến tài khoản | 20k–50k nến seed cố định | Các đẳng thức ở §3.2 | Có (0 vi phạm) |
| IT-11 | Tái lập hai lần | Cùng dữ liệu; strategy mới **và** cùng instance | SHA256 kết quả bằng nhau | Cùng instance **FAIL** |
| IT-12 | Cột tương lai | Thêm `close.shift(-1)` | Engine raise hoặc ghi cảnh báo | **FAIL hiện tại** |
| IT-13 | Nhãn phiên | Cùng dữ liệu nhãn open vs nhãn close (+1 phút) | `session_features` cho cùng tập nến vật lý | **FAIL hiện tại** |
| IT-14 | Off-grid | Lệch đều +30 s | `ready_for_research=False` | **FAIL hiện tại** |
| IT-15 | Benchmark (`slow`) | 10k / 100k / 1M, đường gia tăng | Thời gian, peak RAM ghi vào artifact; full-prefix ≤ 32k | Có |
| IT-16 | Golden-master tối ưu | ≥ 50 seed có gap, SL/TP, FX | `old == new` từng bit | — |

---

## 10. Prioritized Remediation Backlog

### P0: bắt buộc trước khi dùng kết quả backtest cho nghiên cứu

| Issue | Module / file | Lỗi | Bằng chứng | Hướng sửa (tối thiểu) | Regression test | Phụ thuộc | Nghiệm thu |
|---|---|---|---|---|---|---|---|
| **QBS-02** | `core/causality.py` L28–36; `tests/test_indicators.py` L273; `inspect_indicators.py` L95–96 | Dung sai ngầm; PASS rỗng; không kiểm index; từ chối `np.int64` | Probe `IND-4` | `check_exact=True` mặc định; raise khi `len < 2` hoặc cutoffs rỗng; kiểm UTC/unique/monotonic; chấp nhận `numbers.Integral` (loại bool) | Các test STR mục D + rò rỉ 1e-5 + NaN | — (làm **đầu tiên**: lưới an toàn) | 296 test cũ vẫn pass; rò rỉ 1e-5 bị phát hiện; 4 đầu vào xấu raise |
| **QBS-01** | `core/execution.py` L27–36; `core/cost_model.py` L29–51 | So sánh chạm SL/TP bằng float | F2a: 1.752/4.286 | Chuẩn hóa sang số nguyên tick (`round(x / tick)` có dung sai tương đối) trước khi so sánh và làm tròn | IT-03 + F2b (giữ BTC) | QBS-02 | 0/4.286 sai với k ∈ {2, 4, 10, 16}; golden-master: chỉ khác ở biên đã liệt kê |
| **QBS-03** | `core/engine.py` L214–229; Git; `pyproject.toml` | Thiếu provenance; mã chưa commit; không lock | Probe F5; git status | Commit/tag; lock file hoặc `constraints.txt`; thêm `data_sha256`, `strategy` (qualname), `strategy_params`, `library_versions`, `python`, `git_commit`, `git_dirty` vào `assumptions` | `test_result_records_provenance` | — | Mọi `BacktestResult` có đủ khóa; chạy trên tree dirty phải ghi `git_dirty=True` |

### P1: trước khi chạy tích hợp dài hạn / nghiệm thu toàn hệ thống

| Issue | File | Lỗi | Hướng sửa | Test | Phụ thuộc | Nghiệm thu |
|---|---|---|---|---|---|---|
| QBS-07 | `engine.py::run` | Không reset strategy | `strategy = copy.deepcopy(strategy)` đầu `run` (hoặc hook `reset()` no-op) | IT-11 | QBS-03 | Hai lần chạy cùng instance `==` |
| QBS-08 | `sessions.py`; `INDICATORS.md` L12–14 | Hợp đồng nhãn mâu thuẫn | Chọn **một** quy ước. Đề xuất: tham số bắt buộc `label ∈ {"open","close"}` + `bar_duration`; sửa tài liệu | IT-13 | QBS-02 | Nhãn open và close (+duration) cho cùng `active` trên cùng nến vật lý |
| QBS-09 | `data_validator.py` L109–146 | Off-grid không chặn | `errors["off_grid_timestamps"]` khi `(index − index.floor(timeframe)) ≠ 0` (kiểm toàn bộ dòng); **không đổi** chính sách gap | IT-14 + DATA #1 | — | Hai trường hợp off-grid → `ready_for_research=False`; test gap hiện có không đổi |
| QBS-10 | `engine.py` L97–102 | Cột lạ đi vào strategy | Tham số `feature_columns` (mặc định chỉ OHLCV) + cảnh báo trong `assumptions`; tài liệu yêu cầu tính feature trong strategy từ prefix | IT-12 | — | Cột ngoài whitelist không tới strategy, hoặc được ghi nhận rõ |
| QBS-06 | `engine.py` L154–162; `portfolio.py` L29–34 | Rejection không cấu trúc | Event thêm `code`; `assumptions["rejected_orders"]` đếm theo code; giữ hành vi mặc định | CORE-F3 test | QBS-19 | Bộ đếm khớp số event |
| QBS-04, QBS-05 | `engine.py` L131–209 | Chậm/phình bộ nhớ | Mảng NumPy dựng một lần; bỏ `frame.iloc[i]`; `iloc` không deep-copy dưới CoW; không tạo Order cho tín hiệu chắc chắn bị từ chối (hoặc đếm gộp) | IT-15, IT-16 | QBS-01, QBS-06 (để golden-master ổn định) | Golden-master bit-exact; 1M nến gia tăng ≤ 50% thời gian hiện tại; peak RAM ≤ 50% |
| QBS-11 | `causality.py` | O(n²) mặc định | Raise khi `cutoffs is None` và `n > ngưỡng`; helper cutoff lấy mẫu tất định | STR P1-04 test | QBS-02 | n = 50k không có cutoffs → raise nhanh |
| QBS-13 (+12) | `moving_averages.py`, `trend.py`, `momentum.py`, `market_structure.py`, `price_action.py` | Vòng lặp chậm | NumPy hóa, giữ ngữ nghĩa seed/NaN-restart | Oracle `check_exact=True` (hoặc ghi rõ `rtol=1e-12`) | QBS-02 | Bit-exact (hoặc ≤ 1e-12 có ghi rõ); SAR 1,44M < 30 s |
| QBS-14 | `market_structure.py` L96–141 | Ngày trước của thứ Hai | `min_bars` tùy chọn, mặc định giữ nguyên | IND #6 | — | Kỳ thiếu bar → NaN khi bật |
| QBS-15 | `engine.py::ConversionRates` | Thiếu hợp đồng nhãn tỷ giá | Docstring + `assumptions`: nhãn = thời điểm công bố; test nhãn close/open | Test FX | — | Tài liệu và test tồn tại |
| QBS-17 | `data/metadata/datasets.json` | 15 blocker | Thu thập và xác nhận có bằng chứng: `source, timestamp_kind, price_type, timeframe, tick_size, contract_size, quantity_unit, quote_currency, minimum_quantity_increment` (**người dùng quyết định**, không suy đoán) | Test metadata thật → `Instrument` | — | `metadata_blockers == []` cho ít nhất một dataset |
| QBS-18 | `models.py`; `engine.py` | Nhãn state/fill | Thêm `bar_index` vào `Fill`/`AccountState` | CORE-F6 | Trước metrics | Metrics ghép theo `bar_index` |
| — | `core/metrics.py`, `run_backtest.py`, reports | NOT IMPLEMENTED | Triển khai (ngoài phạm vi sửa lỗi) | IT-01 | QBS-03, QBS-18, QBS-24 | Chuỗi DATA → REPORTS chạy được |

### P2: cải thiện ở giai đoạn sau

| Issue | Tóm tắt | Nghiệm thu |
|---|---|---|
| QBS-16 | Đánh dấu `symbols.json` là legacy + test nhất quán | Test pass, hoặc file được ghi “not used” |
| QBS-19 | Lớp `OrderRejected(ValueError)` có `code`; lỗi `side_bar` nêu timestamp | Test `match` timestamp |
| QBS-20 | Giữ test BTC tick rounding (hiện pass) | Test tồn tại |
| QBS-21 | CCI trên cửa sổ phẳng → NaN như tài liệu | Test |
| QBS-22 | `load_csv(diagnostic=False)` raise khi có token lỗi | DATA #2 test |
| QBS-23 | `write_json` atomic | DATA #4 test |
| QBS-24 | Sửa `config.yaml` (`1h`, `include_swap: false`, đơn vị slippage) khi nối runner | Runner đọc được |
| QBS-25 | Parse epoch nguyên | DATA #6 test |
| QBS-26 | Giới hạn `intraday_gaps`; đo loader 1,44M | Báo cáo bounded |
| QBS-27 | `save_parquet` so sánh raw đã resolve + xử lý `OSError` | Test |
| QBS-28 | `numbers.Integral`, `np.isfinite`; loại bool khỏi `signal` | Test |
| QBS-29 | Bỏ `.stack()` | So kết quả |
| QBS-30 | Đồng bộ README/tài liệu/`run_backtest.py` | Review |
| QBS-31 | Benchmark: `raise SystemExit` khi khác; so mọi lần lặp; kịch bản có chi phí + SL/TP | Test `-O` |
| QBS-32, QBS-34 | Ghi `fill_delay` và lý do rejection (đã có qua QBS-06) | Event có trường |
| QBS-33 | `spread_cost` theo offset thực | Test Bid source |
| QBS-35 | Nâng cấp `test_future_candles…` theo IT-09 | Test |

---

## 11. Acceptance Criteria

Hệ thống chỉ được nghiệm thu cho **nghiên cứu** khi **tất cả** điều kiện sau đúng, và mỗi điều kiện có artifact chạy thật (stdout/JUnit) gắn commit:

1. Ba mục P0 đóng; regression test của chúng nằm trong repo và pass.
2. IT-01 … IT-14 tồn tại và pass trên commit đã tag. IT-15 có artifact đo.
3. Golden-master (IT-16) pass bit-exact sau mọi tối ưu hiệu năng.
4. Ít nhất một dataset thật có `metadata_blockers == []`. `validate_data` cho `errors == {}`, cảnh báo gap trong ngày được ghi vào kết quả.
5. `BacktestResult.assumptions` chứa đủ provenance (QBS-03) và bộ đếm rejection (QBS-06).
6. `core/metrics.py` và runner tồn tại với test tính tay cho return, drawdown, số trade và xử lý vị thế mở cuối mẫu.
7. 296 test cũ (hoặc phiên bản cập nhật có lý do) vẫn pass. Không test nào bị xóa để “xanh”.

---

## 12. Final Verdict

### 12.1 Theo tiêu chí

| Tiêu chí | Bằng chứng ủng hộ | Rủi ro còn tồn tại | Test cần làm | Đánh giá |
|---|---|---|---|---|
| **A. Correctness** | 296 pass; bất biến 20k nến; prefix-perturbation; tính tay hiện có; tất định | QBS-01 (P0); QBS-06; QBS-08; QBS-09; chưa chạy dữ liệu thật | IT-03, IT-04, IT-08, IT-13, IT-14 | **PASS WITH LIMITATIONS** (lõi, dữ liệu tổng hợp) |
| **B. Integration** | DATA (tổng hợp) → ENGINE → PORTFOLIO chạy end-to-end trong probe | Metrics/runner/report NOT IMPLEMENTED; metadata thật bị chặn; hợp đồng nhãn phiên và tỷ giá; cột tương lai | IT-01, IT-12, IT-13 | **FAIL** |
| **C. Performance** | Gia tăng 1M = 554 s / 1,31 GB; validator 1,44M = 0,15 s | Full-prefix ≈ 19 h; SAR/structure ≈ 9 phút; 1,44M chưa đo trực tiếp; quét tham số | IT-15 | **PASS WITH LIMITATIONS** (chỉ đường gia tăng, một lần chạy) |
| **D. Reproducibility** | SHA256 liên tiến trình giống nhau | Không provenance; mã chưa commit; không lock; tái dùng strategy | IT-11, test provenance | **FAIL** |

### 12.2 Phân loại kết luận

| Loại | Nội dung |
|---|---|
| **Đã chứng minh đúng** | Thời điểm khớp nến kế tiếp (open/close); Bid/Ask từ một luồng giá; chi phí không trừ hai lần; gap SL tại open / gap TP tại target / SL trước TP; bất biến kế toán; nhân quả engine (một strategy); FX as-of tại `opening`; cổng dữ liệu của engine; tất định; 296 test pass |
| **Đã chứng minh có lỗi** | QBS-01, 02, 03, 04, 05, 07, 08, 09, 10, 11, 13, 19, 23, 24, 25, 28 (+ hành vi QBS-06, 14, 18, 32) |
| **Chưa đủ bằng chứng** | QBS-12 trên pandas 2.x; QBS-15 tác động; QBS-26 loader; `unix_ns` > 2^53; engine 1,44M trực tiếp; nguyên nhân chi phí/nến tăng theo n; chất lượng dữ liệu thật |
| **Chưa triển khai** | `core/metrics.py`, `core/data_manager.py`, `run_backtest.py` (runner), reports backtest, `strategies/first_strategy.py`, `custom_indicators.py`, `validation/` (walk-forward, sensitivity), sizing `risk_per_trade` |
| **Giới hạn được chấp nhận** | Một công cụ / một vị thế / không đòn bẩy / không swap; gap chỉ trong ngày UTC; không đảo chiều tự động (QBS-32); không đóng ép cuối mẫu; TP gap tại target; từ chối lệnh khi bracket gãy (cần bộ đếm); fill ở nến có dữ liệu kế tiếp |
| **Bị bác bỏ / hạ mức** | IND-2 O(n²) (FALSE POSITIVE, pandas 3.1.1); CORE-F2 phần BTC (NOT REPRODUCED); IND-5 số rác (NOT REPRODUCED); IND-1 P0 → P1 (không có rò rỉ); DATA-2 P1 → P2; DATA-3 P1 → P2 |

### 12.3 Phán quyết chung

**Hệ thống: NOT READY cho nghiên cứu. CONDITIONALLY READY để phát triển tiếp** sau khi đóng 3 mục P0. Không đưa ra PASS toàn hệ thống: chuỗi METRICS/REPORTS chưa tồn tại và chưa có kiểm thử tích hợp trên dữ liệu thật.

---

## 13. Unverified Questions and Missing Evidence

1. Metadata thật của EURUSD/XAUUSD (`timestamp_kind`, `price_type`, specs) cần **người dùng xác nhận có bằng chứng**. Không suy đoán từ tên file.
2. Hành vi hiệu năng và Copy-on-Write trên pandas 2.2.x (cận dưới pyproject).
3. Engine trên 1,44M nến thật: thời gian, RAM, số cảnh báo gap.
4. Profiling nguyên nhân µs/nến tăng 251 → 554 theo n.
5. Tác động thực tế của QBS-01 trên dữ liệu thật: tỷ lệ chạm đúng biên.
6. Nguồn và nhãn thời gian của chuỗi tỷ giá quote → account (QBS-15) khi có cặp không USD.
7. Coverage nhánh (không có công cụ).
8. Nội dung toàn văn `00A`, `00B`, `.clinerules/*`, `MANIFEST.md`, `07_TEST_RESULTS.md` chưa đối chiếu đầy đủ trong phiên này. Hash 54 file theo baseline chưa tính lại.
9. Loader CSV 1,44M (thời gian, bộ nhớ, `skip_blank_lines=False`).
10. Rò rỉ toàn bộ indicators với `check_exact=True` (chỉ chạy được sau QBS-02).

---

# CLINE REMEDIATION HANDOFF

> [!CAUTION]
> Quy tắc chung cho mọi nhiệm vụ:
> - Không xóa hoặc nới lỏng test hiện có để “xanh”.
> - Không sửa dữ liệu trong `data/raw`, `data/processed`, `reports/runs`.
> - Không đổi chính sách gap (chỉ cảnh báo trong ngày UTC, bỏ qua qua ngày).
> - Không thêm đòn bẩy, đa vị thế hay swap.
> - Không tự điền metadata chưa được người dùng xác nhận.
> - Mỗi nhiệm vụ: **viết test tái hiện → thấy FAIL → sửa tối thiểu → chạy toàn bộ pytest → ghi stdout**.
> - Lệnh chuẩn: `.\.venv\Scripts\python.exe -m pytest -q`

### TASK 0: Chụp baseline
- **Mục tiêu:** điểm tham chiếu tái lập trước khi sửa.
- **File:** toàn repo (chỉ Git).
- **Bằng chứng cần xác minh:** `git status` có 6 M + untracked; pytest 296 passed.
- **Test:** không.
- **Thay đổi cho phép:** commit/tag snapshot hiện tại (`audit-baseline-2026-11-18`) **sau khi người dùng đồng ý**; lưu stdout pytest.
- **Nghiệm thu:** tag tồn tại; 296 passed được ghi lại.
- **Không được thay đổi:** bất kỳ mã nào.

### TASK 1: QBS-02: Siết `check_prefix_invariance` (P0)
- **Mục tiêu:** công cụ nhân quả không còn PASS giả.
- **File:** `core/causality.py`; `tests/test_stage4_review.py` (hoặc `tests/test_causality.py` mới); `tests/test_indicators.py` L273; `inspect_indicators.py` L95–96.
- **Bằng chứng cần xác minh:** builder `close + 1e-5*(len%2)` trên giá 1,08 hiện PASS; `len=1`, `cutoffs=[]`, index đảo hiện PASS; `np.array([2, 5])` hiện bị từ chối.
- **Test cần viết:** 6 test ở `CLAUDE_AUDIT_STRATEGIES.md` mục D (bỏ test “captured state”, chỉ giữ dạng characterization) + biến thể có NaN.
- **Thay đổi cho phép:**
  - Thêm `check_exact=True` (cho phép tham số `rtol`/`atol` tường minh).
  - Kiểm tra `len(data) >= 2`, cutoffs không rỗng; index UTC/unique/monotonic khi là `DatetimeIndex`.
  - Chấp nhận `numbers.Integral` trừ bool.
  - `tests/test_indicators.py` dùng `check_exact=True`.
- **Nghiệm thu:** test mới pass. Nếu test indicators cũ fail với `check_exact=True`, **dừng lại và báo cáo** hàm nào (đó là phát hiện mới, không được nới dung sai).
- **Không được thay đổi:** chữ ký public; logic indicators.

### TASK 2: QBS-01: So sánh chạm SL/TP theo lưới tick (P0)
- **Mục tiêu:** chạm đúng biên luôn kích hoạt.
- **File:** `core/execution.py`, `core/cost_model.py`, `core/engine.py` (truyền `tick_size` nếu cần), `tests/test_execution.py`, `tests/test_cost_model.py`.
- **Bằng chứng cần xác minh:** test `test_exact_touch_is_grid_exact` (CORE-F2) với k=4 hiện FAIL.
- **Test cần viết:** exact-touch k ∈ {2, 4, 10, 16} cho long và short, nguồn Mid/Bid/Ask; giữ `test_on_grid_price_not_moved_for_large_tick_counts`.
- **Thay đổi cho phép:** helper `to_ticks(x, tick)` (làm tròn có dung sai tương đối) dùng trong so sánh SL/TP và làm tròn fill. Golden-master: chạy probe 20k nến (seed 42) trước/sau, mọi khác biệt phải là chạm biên.
- **Nghiệm thu:** 0 trường hợp sai; 296+ test pass; báo cáo diff golden-master.
- **Không được thay đổi:** thứ tự SL trước TP; gap SL tại open; gap TP tại target; slippage bất lợi.

### TASK 3: QBS-03: Provenance (P0)
- **Mục tiêu:** mọi kết quả truy xuất được.
- **File:** `core/engine.py` (khối `assumptions`); `pyproject.toml`; lock file mới; `tests/test_engine.py`.
- **Bằng chứng cần xác minh:** `assumptions` thiếu 5 khóa (probe F5).
- **Test cần viết:** `test_result_records_provenance` (khóa tồn tại; `data_sha256` đổi khi đổi 1 giá; ổn định khi chạy lại).
- **Thay đổi cho phép:**
  - `data_sha256` (`pd.util.hash_pandas_object(frame, index=True)`).
  - `strategy` qualname, `strategy_params`, `signal_history_limit`.
  - `library_versions` (python/numpy/pandas/pyyaml/pyarrow), `git_commit`, `git_dirty` (subprocess an toàn, `None` nếu không có git).
  - Hash chuỗi tỷ giá nếu có.
  - Thêm `requirements.lock`/`constraints.txt` từ `pip freeze` hiện tại.
- **Nghiệm thu:** test pass; `BacktestResult` hai lần chạy vẫn `==`.
- **Không được thay đổi:** các khóa `assumptions` hiện có.

### TASK 4: QBS-07: Cô lập state strategy (P1)
- **File:** `core/engine.py::run`, `strategies/base_strategy.py`, `core/BACKTEST_ENGINE.md` L29.
- **Bằng chứng:** probe F4 (run2 0 fill).
- **Test:** `test_rerun_same_strategy_instance_is_identical`.
- **Thay đổi cho phép:** `deepcopy(strategy)` ở đầu `run` **hoặc** `reset()` no-op được gọi trước vòng lặp; cập nhật tài liệu.
- **Nghiệm thu:** test pass; `test_incremental_strategy_api_matches_batch_output` vẫn pass.
- **Không được thay đổi:** API `generate_signal`/`generate_signals`.

### TASK 5: QBS-06 + QBS-19: Rejection có cấu trúc (P1/P2)
- **File:** `core/engine.py` L140–162, `core/portfolio.py`, `core/models.py`.
- **Bằng chứng:** probe F3, F7.
- **Test:** `test_gapped_entry_rejection_is_structured_and_counted`; `test_excess_spread_error_names_the_bar`.
- **Thay đổi cho phép:** `class OrderRejected(ValueError)` có `code`; chỉ bắt lớp này; event thêm `code`; `assumptions["rejected_orders"]`; bọc lỗi `side_bar` kèm timestamp. Giữ `reason` cũ để test chuỗi hiện có không vỡ.
- **Nghiệm thu:** test mới + cũ pass.
- **Không được thay đổi:** hành vi mặc định “reject” (không thêm `fill_and_stop` trừ khi được yêu cầu).

### TASK 6: QBS-09: Off-grid thành lỗi (P1)
- **File:** `core/data_validator.py`, `tests/test_data_validator.py`, `tests/test_intraday_gaps.py`.
- **Bằng chứng:** probe DATA-1 (lệch đều không có cảnh báo).
- **Test:** test DATA #1 + trường hợp lệch đều +30 s.
- **Thay đổi cho phép:** `errors["off_grid_timestamps"]` dựa trên `index − index.floor(timeframe)` cho mọi dòng hợp lệ.
- **Nghiệm thu:** cả hai trường hợp `ready_for_research=False`; **mọi test gap hiện có không đổi kết quả**.
- **Không được thay đổi:** chính sách gap cùng ngày, `cross_day_interval_count_ignored`, chế độ `expected_timestamps`.

### TASK 7: QBS-08: Một quy ước nhãn cho hàm phiên (P1)
- **File:** `indicators/sessions.py`, `indicators/INDICATORS.md` L12–14, `tests/test_indicators.py`.
- **Bằng chứng:** probe IND-1 `[F,T,T,F]`.
- **Test:** IT-13 (nhãn open và nhãn close +1 phút cho cùng `active` trên cùng nến vật lý).
- **Thay đổi cho phép:** tham số `label` và `bar_duration`. Nếu bắt buộc thì cập nhật mọi wrapper. **Hỏi người dùng** chọn mặc định trước khi làm.
- **Nghiệm thu:** test pass; tài liệu chỉ còn một quy ước.
- **Không được thay đổi:** ngữ nghĩa overnight/DST; giá trị cho dữ liệu nhãn open khi `label="open"`.

### TASK 8: QBS-10: Kiểm soát cột đi vào strategy (P1)
- **File:** `core/engine.py` L97–102, L187; `core/BACKTEST_ENGINE.md`.
- **Bằng chứng:** probe `future_column_passthrough` (102/149 lệnh thắng).
- **Test:** IT-12.
- **Thay đổi cho phép:** tham số `feature_columns` (mặc định OHLC + `volume` nếu có); cột khác bị loại hoặc phải khai báo, và được ghi vào `assumptions`.
- **Nghiệm thu:** cột `close.shift(-1)` không đến strategy khi chưa khai báo.
- **Không được thay đổi:** prefix copy, logic tín hiệu.

### TASK 9: QBS-11: Chốt chặn chi phí causality (P1)
- **File:** `core/causality.py`.
- **Bằng chứng:** 4k nến = 27 s, tăng bậc hai.
- **Test:** `test_requires_cutoffs_for_large_sample`; mutation test cho cutoff lấy mẫu.
- **Thay đổi cho phép:** ngưỡng `max_full_prefix` (ví dụ 2.000); helper `sample_cutoffs(index, seed)`.
- **Nghiệm thu:** n = 50k không có cutoffs → raise < 1 s.
- **Không được thay đổi:** ngữ nghĩa so sánh từ TASK 1.

### TASK 10: QBS-04 + QBS-05: Tối ưu engine với golden-master (P1)
- **File:** `core/engine.py`.
- **Bằng chứng:** `perf_results_large.jsonl` (gia tăng 1M = 554 s / 1,31 GB; full-prefix bậc hai).
- **Test:** IT-16 golden-master trên ≥ 50 seed (gap, SL/TP, FX, chi phí): **đẳng thức chính xác** `orders/fills/trades/states/events`. Benchmark `slow`.
- **Thay đổi cho phép:**
  - Trích OHLC sang NumPy một lần.
  - Bỏ `frame.iloc[i]` trong vòng lặp.
  - Prefix không deep-copy khi pandas ≥ 3 (giữ copy cho 2.x).
  - Đếm gộp tín hiệu chắc chắn bị từ chối, giữ bộ đếm theo QBS-06.
- **Nghiệm thu:** golden-master bit-exact (trừ thay đổi event đã thỏa thuận ở bước đếm gộp, có tài liệu); 1M nến ≤ 50% thời gian và RAM hiện tại.
- **Không được thay đổi:** thứ tự xử lý pending → protective → mark → signal; công thức giá và kế toán.

### TASK 11: QBS-13: Tối ưu indicators với oracle (P1)
- **File:** `indicators/moving_averages.py` (`rma`, `wma`), `trend.py` (`parabolic_sar`, `supertrend`, `aroon`, `adx`), `market_structure.py` (`structure_breaks`, `confirmed_swings`), `price_action.py`, `sessions.py::dominant_cycle`.
- **Bằng chứng:** SAR 364 µs/nến; ADX 1,44M = 150 s.
- **Test:** giữ bản cũ làm oracle trong test; dữ liệu ngẫu nhiên có NaN một phần; `check_exact=True` (hoặc `rtol=1e-12` có ghi lý do); prefix invariance chính xác.
- **Thay đổi cho phép:** vòng lặp NumPy thuần; tính `valid` một lần.
- **Nghiệm thu:** oracle pass; SAR 1,44M < 30 s.
- **Không được thay đổi:** seed, NaN-restart, warm-up.

### TASK 12: Các mục P1 còn lại (QBS-14, QBS-15, QBS-18)
- **QBS-14:** `min_bars` tùy chọn cho `previous_period_levels`/`daily_pivots`; mặc định giữ nguyên.
- **QBS-15:** docstring + `assumptions` cho nhãn tỷ giá; test nhãn.
- **QBS-18:** `bar_index` trong `Fill`/`AccountState` (thêm field có mặc định để không vỡ test).
- **Nghiệm thu:** test riêng từng mục pass.
- **Không được thay đổi:** giá trị mặc định hiện có.

### TASK 13: Test tích hợp end-to-end (IT-01 … IT-15)
- **File:** `tests/test_integration_e2e.py` mới; `pyproject.toml` (đăng ký marker `slow`).
- **Mục tiêu:** khép bằng chứng tích hợp ở §9.
- **Nghiệm thu:** toàn bộ IT pass (trừ IT-15 chỉ ghi số đo).
- **Không được thay đổi:** mã sản phẩm trong task này. Nếu test fail, mở issue mới, không sửa lén.

### TASK 14: Dọn P2
QBS-16, 20–31, 33–35 theo bảng P2 §10. Mỗi mục một commit, kèm test.

### TASK 15 (cần người dùng): Metadata thật và các phần chưa triển khai
- **QBS-17:** người dùng cung cấp bằng chứng cho `timestamp_kind`, `price_type`, `timeframe`, `tick_size`, `contract_size`, `quantity_unit`, `quote_currency`, `minimum_quantity_increment`. Cline chỉ ghi vào `datasets.json` khi có bằng chứng.
- **Metrics/runner/reports:** cần đặc tả riêng (`/plan`). Không gộp vào nhiệm vụ sửa lỗi.
