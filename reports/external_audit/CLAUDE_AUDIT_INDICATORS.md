# BÁO CÁO KIỂM TOÁN ĐỘC LẬP: LỚP INDICATORS CỦA QUANT BACKTEST SYSTEM

* **Phạm vi kiểm toán thực tế:** Tôi chỉ nhận được `00_PROJECT_OVERVIEW.md`, `03_INDICATORS_AUDIT.md`, `03A–03G` và `05D_TESTS_INDICATORS.md`. Đó là 7 module chỉ báo, `_utils.py`, `__init__.py`, stub `custom_indicators.py`, `inspect_indicators.py`, `tests/test_indicators.py`, cùng `README`, `pyproject.toml` và `run_backtest.py`.
* **Ngoài phạm vi:** Không có `core/engine.py`, `execution.py`, `cost_model.py`, `portfolio.py`, `data_loader.py`, `data_validator.py`, `causality.py`, `base_strategy.py` và các test `05A–05C`, nên tôi không kiểm toán engine. Các hạng mục P0 về Bid/Ask, SL/TP, P/L và equity nằm ngoài phạm vi.
* **Phương pháp kiểm toán:** Tôi chưa chạy code hay test nào trong phiên này. `"296 passed"` là số liệu từ `00_PROJECT_OVERVIEW.md` mà tôi không kiểm chứng được, và `07_TEST_RESULTS.md` không có trong gói. Mọi kết luận dưới đây dựa trên đọc mã và đối chiếu tay. Tệp cung cấp không có số dòng đáng tin, nên tôi dùng tên hàm cùng đoạn mã neo thay cho số dòng.

---

## A. Kết luận tổng quan

* Qua đọc mã, tôi không tìm thấy look-ahead đã xác nhận trong lớp chỉ báo. Không có `shift(-n)`, `center=True` hay chuẩn hóa toàn lịch sử. Swing chỉ phát ở bar xác nhận, previous-period dùng `.shift()` trên kỳ đã đóng, và `volatility_regime` loại bar hiện tại khỏi ngưỡng.
* Rủi ro nhân quả lớn nhất là hợp đồng nhãn thời gian của hàm phiên tự mâu thuẫn (**#1**). Mức độ ảnh hưởng chưa kết luận được nếu thiếu engine và metadata dữ liệu.
* Hai hàm không dùng được ở quy mô $1{,}44$ triệu nến vì độ phức tạp $O(n^2)$: `parabolic_sar` và `structure_breaks` (**#2**). Smoke test chỉ chạy lát $10.080$ dòng nên không bắt được lỗi này.
* Bộ test mạnh về cấu trúc nhưng bằng chứng nhân quả yếu hơn vẻ ngoài. Test prefix dùng dung sai mặc định của pandas, và nhiều fixture số học chỉ là chuỗi đơn điệu tăng (**#4**).

---

## B. Danh sách vấn đề (P0 $\rightarrow$ P2)

| # | Mức | Trạng thái | Vấn đề |
| :--- | :--- | :--- | :--- |
| **1** | **P0** (có điều kiện) | `SUSPECTED`, cần engine và metadata | `sessions.py`: hợp đồng "index = thời điểm đóng nến" mâu thuẫn với phép thành viên `[start, end)` |
| **2** | **P1** | `CONFIRMED` (độ phức tạp, đọc mã) | `parabolic_sar` và `structure_breaks` sao chép cả DataFrame trong mỗi vòng lặp $\rightarrow O(n^2)$ |
| **3** | **P1** | `CONFIRMED` (cấu trúc), thời gian chưa đo | Nhiều vòng lặp Python/`rolling.apply` (RMA, ATR, RSI, ADX, SuperTrend, HA, WMA, Aroon, swings, cycle) rất chậm ở $1{,}44$ triệu nến |
| **4** | **P1** | `CONFIRMED` | Test prefix-invariance và `inspect_indicators.py` dùng dung sai mặc định `rtol=1e-5` |
| **5** | **P1** | `SUSPECTED` | Cửa sổ phẳng với giá không biểu diễn chính xác: CCI, Bollinger %B/bandwidth có thể ra số rác thay vì `NaN` |
| **6** | **P1** | `DESIGN LIMITATION` với rủi ro nghiên cứu | `previous_period_levels` và `daily_pivots` lấy "ngày trước" của thứ Hai là mảnh Chủ nhật vài giờ UTC |
| **7** | **P2** | `CONFIRMED` | Tham số float `NaN`/`inf` không bị từ chối; `numpy.int64` bị từ chối |
| **8** | **P2** | `CONFIRMED` | `garman_klass_volatility` dùng `.stack()` trên toàn bộ OHLC, tốn bộ nhớ không cần thiết |
| **9** | **P2** | `CONFIRMED` | Kiến trúc và tài liệu lệch: import lười từ `sessions._utc_index`, sơ đồ thiếu cạnh, `README` cũ, stub sai mô tả |
| **10** | **P2** | `CONFIRMED` | Khả năng tái lập: toàn bộ mã chưa commit, script smoke phụ thuộc artifact bị `.gitignore`, phụ thuộc chưa khóa |

---

## C. Bảng bằng chứng

### #1. Mâu thuẫn nhãn thời gian ở hàm phiên (P0 có điều kiện, SUSPECTED)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `sessions.py::session_features`; docstring module và `INDICATORS.md` |
| **Trích đoạn** | Docstring: *"Session inputs are timestamps of completed candles (availability time). Intervals are [open, close)"*. Mã: `active = (seconds >= start_second) & (seconds < end_second)` |
| **Vì sao rủi ro** | Nếu nến M1 gắn nhãn thời điểm đóng, nến `07:59–08:00` mang nhãn `08:00` bị xếp trong phiên với `minutes_since_open=0`, còn nến `16:59–17:00` mang nhãn `17:00` bị xếp ngoài phiên. Với nhãn đóng, khoảng đúng là `(open, close]`. Nếu dữ liệu gắn nhãn mở (kiểu Dukascopy), phép thành viên đúng nhưng tuyên bố *"availability time"* sai. Tài liệu bảo người dùng chuyển nhãn mở $\rightarrow$ đóng trước khi gọi, và làm theo thì lệch một nến. `00_PROJECT_OVERVIEW.md` cũng nêu rõ không có tự động đổi nhãn trong `BaseStrategy` |
| **Hậu quả** | `session_range`, `opening_range_breakout`, `session_vwap`, `london_new_york_overlap` nhiễm một nến ngoài phiên ở đầu phiên và mất nến cuối. ORB đóng băng range sai. Test hiện tại không ghim quy ước nhãn |
| **Đầu vào tối thiểu** | `idx = DatetimeIndex(["2024-01-02 07:59Z","2024-01-02 08:00Z","2024-01-02 16:59Z","2024-01-02 17:00Z"]); session_features(idx, timezone="UTC", start="08:00", end="17:00")` |
| **Mong đợi (nhãn đóng)** | `active = [F, F, T, T]` |
| **Mã hiện tại cho** | `active = [F, T, T, F]` |
| **Regression test** | `session_features(idx, ..., label="close", bar_minutes=1).active.tolist() == [False, False, True, True]` và `label="open"` cho kết quả `[F, T, T, F]` (tham số `label` là đề xuất, chưa tồn tại) |
| **Sửa tối thiểu** | Thêm tham số bắt buộc `label` $\in$ `{"open","close"}` cùng `bar_minutes`. Với `"close"`, trừ `bar_minutes` trước khi xét thành viên. Sửa tài liệu cho một quy ước duy nhất |
| **Cần để kết luận** | Nhãn thực của parquet EURUSD và cách engine gán nhãn/khớp lệnh |

### #2. $O(n^2)$ trong `parabolic_sar` và `structure_breaks` (P1, CONFIRMED)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `trend.py::parabolic_sar`; `market_structure.py::structure_breaks` |
| **Trích đoạn** | `if data[["high", "low", "close"]].iloc[i].isna().any():` và `if data[["open", "high", "low", "close"]].iloc[i].isna().any():` |
| **Vì sao lỗi** | `data[[...]]` tạo bản sao toàn bộ cột trong mỗi vòng lặp, tức $O(n)$ mỗi bước và $O(n^2)$ tổng. Với $n=1{,}44$ triệu, mỗi bản sao khoảng $35\text{ MB}$, tổng dữ liệu di chuyển cỡ $5 \times 10^{13}\text{ byte}$. Ước lượng của tôi là hàng giờ, chưa đo. Ở lát $10.080$ dòng của `inspect_indicators.py`, mỗi bản sao chỉ khoảng $240\text{ KB}$ nên lỗi bị che |
| **Đầu vào** | `parabolic_sar(bars(random_walk(n)))` với $n = 20.000$ rồi $40.000$ |
| **Mong đợi** | Thời gian tăng khoảng $2\times$ |
| **Mã hiện tại** | Thời gian tăng khoảng $4\times$ (dự đoán từ độ phức tạp) |
| **Regression test** | So `old` và `new` bit-for-bit trên 5 seed $\times$ nhiều độ dài, có chèn `NaN`: `assert_frame_equal(new, old, check_exact=True)`. Thêm test thời gian $n=50.000 < 5\text{ s}$, đánh dấu `slow` và đăng ký marker trong `pyproject.toml` vì `--strict-markers` |
| **Sửa tối thiểu** | Tính một lần `valid = data[cols].notna().all(axis=1).to_numpy()` ngoài vòng lặp. Đọc `high`/`low`/`close` bằng mảng numpy, không dùng `.iloc` trong vòng lặp. Đối chiếu trước/sau bằng test trên |

### #3. Vòng lặp Python và `rolling.apply` chậm (P1, CONFIRMED cấu trúc)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `moving_averages.rma` (vòng `for` với `pd.isna` và `result.iloc[i] =`), kéo theo `atr`, `rsi`, `adx` (gọi `rma` nhiều lần); `supertrend` (`result.iloc[i] = [...]`); `heikin_ashi`, `consecutive_candles`; `wma` (`weights.sum()` kiểu Series trong mỗi cửa sổ); `aroon`; `confirmed_swings` (`np.delete` mỗi cửa sổ); `dominant_cycle` (FFT mỗi bar) |
| **Vì sao rủi ro** | Mỗi lần gọi trên $1{,}44$ triệu nến cỡ chục giây đến vài phút (ước lượng, chưa đo). Quét tham số nhân lên theo số cấu hình |
| **Đầu vào** | `rma`, `atr`, `rsi`, `adx`, `supertrend` trên $1{,}44$ triệu giá tổng hợp |
| **Mong đợi** | Vài giây mỗi chỉ báo |
| **Mã hiện tại** | Dự đoán chục giây đến phút mỗi chỉ báo (chưa đo) |
| **Regression test** | Giữ bản hiện tại làm oracle tham chiếu trong test. Trên dữ liệu ngẫu nhiên có `NaN` và nhiều window, so `rtol=1e-12` cho bản mới. Prefix-invariance giữ nguyên |
| **Sửa tối thiểu** | Chuyển vòng lặp sang mảng numpy/float thuần (không cần thêm thư viện). Với `wma`, tính trọng số một lần. Không đổi ngữ nghĩa seed/`NaN`-restart |

### #4. Test nhân quả dùng dung sai lỏng (P1, CONFIRMED)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `tests/test_indicators.py::test_all_indicators_preserve_index_causality_and_inputs`; `inspect_indicators.py::main` |
| **Trích đoạn** | `compare = pd.testing.assert_frame_equal ... compare(full.iloc[:length], calculation(d.iloc[:length]))` |
| **Vì sao lỗi** | `assert_*_equal` mặc định `check_exact=False, rtol=1e-5, atol=1e-8`. Với giá EURUSD $\approx 1{,}08$, dung sai $\approx 1{,}1 \times 10^{-5}$, tức khoảng một tick 5 chữ số. Rò rỉ nhỏ như vậy lọt qua. Phép tính prefix và full chạy cùng chuỗi phép toán từ đầu nên kết quả phải khớp từng bit |
| **Hạn chế khác** | Chỉ 80 bar, `window=3` và cửa sổ nhỏ. Dữ liệu `NaN` không được kiểm prefix (chỉ kiểm chỉ số và `inf`). Nhiều fixture số học dùng chuỗi đơn điệu tăng nên phía giảm (`minus_di`, loss của RSI, phía sell của SAR/SuperTrend) gần như không được ép |
| **Đầu vào** | Giá $\approx 1{,}08$ bước `1e-5` |
| **Mong đợi** | Khác biệt 1 tick giữa prefix và full bị phát hiện |
| **Mã hiện tại** | Không bị phát hiện |
| **Regression test** | `assert_frame_equal(..., check_exact=True)` trên dữ liệu 400+ bar quanh $1{,}08$ với một `NaN` ở giữa. Dùng tham số mặc định (14/20/26) cho vài hàm chính |
| **Sửa tối thiểu** | Đổi sang `check_exact=True` trong test và trong script smoke. Thêm biến thể có `NaN` |

### #5. Cửa sổ phẳng với giá không biểu diễn chính xác (P1, SUSPECTED)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `momentum.cci`; `volatility.bollinger_percent_b`, `bollinger_bandwidth`, `rolling_std` |
| **Trích đoạn** | `.replace(0, np.nan)` chỉ bắt đúng `0`. Ví dụ `(typical - mean) / (0.015 * deviation).replace(0, np.nan)` |
| **Vì sao rủi ro** | Với giá phẳng như $1{,}0845$ (thường gặp trên M1 ngoài giờ thanh khoản), trung bình/độ lệch có thể lệch 1 ulp, hoặc `rolling.std` sau cửa sổ có biến động có thể ra $\sim 10^{-9}$. Mẫu số khác $0$ nhưng cực nhỏ nên ra số rác ($\pm$lớn hoặc phân số tùy ý) thay vì `NaN` như tài liệu hứa. Test hiện tại chỉ dùng `flat=10.0` biểu diễn chính xác và phẳng từ đầu |
| **Đầu vào** | `pd.Series([1.2345, 1.2350, 1.2341] + [1.0845]*30), window=20` |
| **Mong đợi** | `bollinger_percent_b` và `cci` là `NaN` trên cửa sổ phẳng |
| **Mã hiện tại** | Có thể là số hữu hạn tùy ý. Chưa chạy nên chỉ là `SUSPECTED` |
| **Regression test** | `assert vol.bollinger_percent_b(s, 20).iloc[-1:].isna().all()` và tương tự `cci` với OHLC phẳng $1{,}0845$ |
| **Sửa tối thiểu** | Coi mẫu số $\le \text{eps} \times |\text{scale}|$ là $0$ (ví dụ `eps=1e-12`), hoặc bắt cửa sổ phẳng bằng `rolling.max() == rolling.min()` |

### #6. "Ngày trước" của thứ Hai là mảnh Chủ nhật (P1, DESIGN LIMITATION có rủi ro)

| Mục | Nội dung |
| :--- | :--- |
| **Vị trí** | `market_structure.py::previous_period_levels`, `daily_pivots` |
| **Trích đoạn** | `keys = local.normalize()` rồi `groupby(keys).agg(...).shift()` |
| **Vì sao rủi ro** | Kỳ trước là kỳ quan sát trước. Với FX theo ngày UTC, thứ Hai nhận H/L/C từ nến Chủ nhật vài giờ. Docstring và `INDICATORS.md` đã thừa nhận *"caller must supply validated complete session coverage"*. Đây là giới hạn đã chấp nhận, nhưng có thể làm sai pivot khoảng $20\%$ số ngày nếu dùng ngây thơ |
| **Đầu vào** | Bar Thứ Sáu cả ngày, Chủ nhật `22:00–23:59 UTC`, rồi thứ Hai |
| **Mong đợi** | Pivot thứ Hai từ phiên đầy đủ (hoặc `NaN`/cờ cảnh báo) |
| **Mã hiện tại** | Pivot từ mảnh Chủ nhật |
| **Regression test** | `previous_period_levels(d, min_bars=...)` trả `NaN` khi kỳ trước thiếu bar (tham số là đề xuất) |
| **Sửa tối thiểu** | Thêm `min_bars` tùy chọn, mặc định giữ hành vi cũ. Ghi rõ rủi ro này trong tài liệu |

### #7–#10 (P2)

| # | Bằng chứng | Mong đợi / Hiện tại | Test | Sửa |
| :--- | :--- | :--- | :--- | :--- |
| **7** | `if multiplier <= 0`, `if deviations <= 0`, `if wick_to_body <= 0` không bắt `NaN`; `positive_window` dùng `isinstance(window, int)` nên loại `np.int64` | `NaN`/`inf` phải bị từ chối; `np.int64(14)` nên được chấp nhận. Hiện `NaN` âm thầm ra `NaN`, còn numpy int ném lỗi | `pytest.raises(ValueError)` với `deviations=np.nan`; `ma.sma(s, np.int64(3))` chạy được | Dùng `np.isfinite` và `numbers.Integral` |
| **8** | `garman_klass_volatility`: `data[["open","high","low","close"]].stack() <= 0` | Kiểm tra dương không cần MultiIndex $5{,}76$ triệu phần tử (ước lượng hàng trăm MB) | So kết quả với `(data[cols] <= 0).any().any()` | Thay bằng phép so sánh trực tiếp |
| **9** | `previous_period_levels` import lười `from .sessions import _utc_index`; sơ đồ ở `03_INDICATORS_AUDIT.md` thiếu cạnh `market_structure` $\rightarrow$ `sessions`; `custom_indicators.py` nói chứa Price Action/cấu trúc nhưng chúng nằm ở module khác; `README` vẫn nói *"Chưa cần ... pyarrow"* trong khi `pyproject.toml` có `pyarrow`; `_utc_index` trùng một phần `validate_index`; `session_features` ném lỗi do giờ mở phiên mơ hồ/không tồn tại ngay cả ở ngày không có bar trong phiên | Tài liệu khớp mã; helper dùng chung ở `_utils` | Test import-graph đơn giản; test `session_features` với ngày DST không có bar phiên | Chuyển helper về `_utils`, sửa tài liệu và sơ đồ, chỉ kiểm mở phiên mơ hồ cho ngày có bar active |
| **10** | Snapshot là working tree trên commit nền `7af3b77`, phần lớn mã là untracked; `inspect_indicators.py` hardcode `data/processed/inspection-20261116T161144Z-.../...parquet` mà `.gitignore` loại `data/processed/*`; `pyproject.toml` chỉ khai báo khoảng phiên bản | Kết quả kiểm toán gắn được với một commit; script chạy lại được | Test kiểm tra file/hash đầu vào được ghi vào metadata | Commit (hoặc tag) trước khi nghiên cứu, truyền đường dẫn qua tham số CLI, thêm lock file |

---

## D. Test còn thiếu

1. Prefix-invariance với `check_exact=True`, tham số mặc định, giá quanh $1{,}08$, bước `1e-5`, có `NaN` (**#4**).
2. Quy ước nhãn thời gian của hàm phiên: nhãn `open` và `close` cho kết quả khác nhau (**#1**).
3. Cửa sổ phẳng với giá không biểu diễn chính xác: CCI, Bollinger, VHF, Choppiness (**#5**).
4. Fixture có biến động hai chiều cho ADX (`minus_di`), RSI (`loss`), SAR/SuperTrend phía sell. So với một ví dụ tham chiếu độc lập đã công bố, không chỉ chuỗi đơn điệu.
5. `NaN` một phần (chỉ `close` hoặc chỉ `high` thiếu). Test hiện tại chỉ làm `NaN` cả hàng.
6. Test tương đương trước/sau khi tối ưu **#2** và **#3** (oracle, `check_exact` hoặc `rtol=1e-12`).
7. Test quy mô hoặc thời gian (đánh dấu `slow`) cho SAR và `structure_breaks`.
8. Pivot thứ Hai sau Chủ nhật mảnh (**#6**) và tuần có thiếu ngày.
9. Tham số float `NaN`/`inf` và numpy integer (**#7**).
10. Đối chiếu SAR với một chuỗi tham chiếu công bố qua nhiều lần đảo chiều. Test hiện tại chỉ ghim hai giá trị đầu và hướng ở bar cuối.

---

## E. Điểm thiết kế đúng, nên giữ

* Test prefix-invariance bao phủ mọi hàm public (đối chiếu danh sách API với `CASES`), kèm kiểm tra không mutate và tái lập. Chỉ cần siết dung sai.
* Không có shift âm hay cửa sổ căn giữa. Ichimoku không xuất Chikou dịch ngược; `lagging_close` là close quá khứ.
* Swing, structure và liquidity-sweep chỉ phát tại bar xác nhận, mỗi mức bị phá một lần, mức chỉ khả dụng từ bar kế tiếp.
* Pivot, ngày trước và tuần trước dùng `.shift()` trên kỳ đã đóng. `volatility_regime` loại bar hiện tại khỏi ngưỡng.
* `dominant_cycle` dùng cửa sổ quá khứ từng bar, không Hilbert toàn chuỗi.
* `session_vwap` đòi `volume_kind` tường minh và không có fallback volume bằng 1. `annualization` do người gọi cung cấp.
* Fail-closed ở `_utils`: index phải UTC, duy nhất, tăng dần; từ chối `inf` và OHLC sai quan hệ. Không tự điền `NaN`, EMA/RMA khởi tạo lại sau `NaN`.
* Chia cho 0 trả `NaN` thay vì `inf` ở nhiều hàm. Tài liệu ghi rõ seed EMA khác RMA và không tuyên bố khớp TA-Lib.
* Tôi đối chiếu tay các công thức: warm-up `stochastic_rsi`, `vortex`, `VHF`, `ADX` ($+\text{DM}/-\text{DM}$ và seed), giá trị SAR đầu tiên, `cloud_a` của Ichimoku, SuperTrend bar đầu. Tất cả khớp với mã và test.

---

## F. Chưa thể kết luận

* **Toàn bộ engine và dòng tiền:** Bid/Ask, spread, slippage, gap SL/TP, hoa hồng, tick rounding, P/L, equity, quy đổi tiền tệ, vị thế mở cuối dữ liệu. Thiếu `engine`, `execution`, `cost_model`, `portfolio`, `models`, test `05A–05C`.
* **Look-ahead giữa chỉ báo và engine:** Nhãn thời gian nến (mở hay đóng), cách `BaseStrategy` căn tín hiệu cuối nến với khớp lệnh mở nến kế tiếp, và `core/causality.py`.
* **Loader và validator:** Có thực thi quy tắc "thiếu nến cùng ngày UTC" và từ chối timestamp trùng/sai thứ tự/`NaN` hay không. Thiếu `data_loader.py`, `data_validator.py`, `07_TEST_RESULTS.md`.
* **Thời gian chạy thực tế và các nghi ngờ số học #5:** Cần chạy mã để xác nhận hoặc bác bỏ.
* `"296 passed"` chưa được tôi kiểm chứng.
* Nội dung `00A_SOURCE_INVENTORY.md`, `00B_PROJECT_RULES.md`, `01*`, `02*`, `04*`, `06*`.

> **Lưu ý:** Chưa thể khẳng định gì về kiểm toán toàn bộ dự án.

---

## G. Kế hoạch sửa theo thứ tự ưu tiên

1. Gửi các file engine, loader, validator và metadata dữ liệu để kết luận **#1**. Chốt một quy ước nhãn và ghim bằng test.
2. Siết test nhân quả: `check_exact=True`, tham số mặc định, có `NaN` (**#4**). Đây là bước rẻ, làm trước khi tối ưu để có lưới an toàn.
3. Sửa **#2** ($O(n^2)$) bằng mảng numpy. Đối chiếu bản cũ làm oracle.
4. Sửa **#3** (vòng lặp chậm) với cùng phương pháp oracle, đo thời gian trước/sau trên dữ liệu thật.
5. Kiểm chứng **#5** bằng chạy mã, rồi thêm ngưỡng epsilon.
6. Quyết định chính sách cho **#6** (`min_bars` hoặc rollover), ghi vào tài liệu.
7. Dọn **P2**: validate tham số, `stack()`, import chéo, `README`, sơ đồ, commit và lock phụ thuộc, tham số hóa đường dẫn script smoke.

---

## H. Kết luận

**`PASS WITH LIMITATIONS`**, chỉ cho lớp indicators và test của chúng, dựa trên đọc mã.

* Không phát hiện look-ahead đã xác nhận trong các chỉ báo.
* **#1** có thể nâng thành **P0** nếu engine/dữ liệu xác nhận lệch nhãn.
* `parabolic_sar` và `structure_breaks` chưa đạt yêu cầu hiệu năng cho $1{,}44$ triệu nến.
* Không có kết luận về engine, loader và validator vì thiếu file.