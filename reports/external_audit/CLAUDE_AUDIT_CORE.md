# BÁO CÁO KIỂM TOÁN ĐỘC LẬP — QUANT BACKTEST SYSTEM

**Phạm vi:** đọc tĩnh mã nguồn và bài test trong hồ sơ. **Tôi không chạy code, test hay benchmark nào.** Con số "296 passed" lấy từ `00_PROJECT_OVERVIEW.md`, tôi chưa kiểm chứng.

**Cách trích dòng mã:** các gói Markdown không đánh số dòng, nên tôi neo bằng tên hàm và đoạn mã trích thay vì số dòng. Nếu bạn gửi `Get-Content … | % {$i++; "$i`: $_"}`, tôi sẽ ánh xạ lại.

**Mã đọc được toàn văn:** `core/{models,execution,cost_model,portfolio,engine}.py`, `strategies/base_strategy.py`, `core/BACKTEST_ENGINE.md`, README, pyproject và toàn bộ test thuộc 05A–05D.

**Chỉ thấy qua test hoặc mô tả, chưa thấy mã:** `data_loader`, `data_validator`, `causality`, toàn bộ `indicators/*`, `benchmark_engine.py`, `configs/*`, `.clinerules`.

---

## A. Kết luận tổng quan

- **Không phát hiện lỗi P0 nào được xác nhận** trong phần mã đã đọc. Tôi đã kiểm tra thủ công các điểm sau:
  - **Thời điểm khớp:** tín hiệu tạo ở cuối nến i, khớp ở giá mở nến có dữ liệu kế tiếp, kèm kiểm tra `opening < order.submitted_at`.
  - **Bid/Ask:** công thức suy ra từ một luồng giá đúng cho cả ba loại `Mid`, `Bid`, `Ask`.
  - **Chi phí:** spread và slippage nằm trong giá khớp, không trừ lần hai. Commission trừ mỗi phía.
  - **SL/TP:** điều kiện long/short đúng chiều. SL ưu tiên khi cùng chạm. Gap SL dùng giá mở. Gap TP bị chặn ở mức target.
  - **Tỷ giá:** `searchsorted(side="right") - 1`, không dùng tỷ giá tương lai.
  - **Kế toán:** P/L, balance, equity và vốn dự trữ nhất quán. Tôi đã tính lại tay các ví dụ trong test.
- **Rủi ro lớn nhất là hiệu năng ở quy mô 1,44 triệu nến.** Đường mặc định (strategy cũ, `signal_history_limit=None`) có độ phức tạp O(n²). Đường gia tăng khả thi ở mức vài phút mỗi lần chạy theo số liệu trong tài liệu, nhưng chưa được kiểm chứng.
- **Rủi ro lớn thứ hai là độ nhạy của các phép so sánh "chạm giá" với nhiễu dấu phẩy động** (SUSPECTED, cần test).
- **Một số nhánh kết quả được ghi nhận nhưng không được định lượng.** Ví dụ lệnh bị từ chối vì gap làm SL/TP không còn bao quanh giá khớp: nó bị bỏ qua thay vì ghi nhận lỗ, và kết quả không có bộ đếm tổng hợp.
- **Provenance của kết quả chưa đủ** để tái lập nghiên cứu (không có hash dữ liệu, commit, params chiến lược).

---

## B. Danh sách vấn đề (P0 → P1 → P2)

| ID | Mức | Trạng thái | Vấn đề |
|---|---|---|---|
| — | P0 | — | Không có phát hiện P0 được xác nhận trong phạm vi đã đọc |
| F1 | P1 | CONFIRMED (phân tích độ phức tạp từ mã) | Đường mặc định O(n²); chi phí mỗi nến và bộ nhớ kết quả không phù hợp 1,44M nến |
| F2 | P1 | SUSPECTED | So sánh chạm SL/TP và làm tròn tick dựa trên float, không chuẩn hóa theo lưới tick |
| F3 | P1 | DESIGN LIMITATION + SUSPECTED thiên lệch | Lệnh vào bị từ chối khi gap phá SL/TP, không có bộ đếm trong kết quả |
| F4 | P1 | CONFIRMED (thiếu cơ chế) | Không có vòng đời strategy (reset) và không phản hồi vị thế/fill cho strategy |
| F5 | P1 | CONFIRMED (thiếu dữ liệu) | `assumptions` thiếu provenance; snapshot là working tree chưa commit |
| F6 | P2 | DESIGN LIMITATION | Nhãn thời gian `AccountState`/`Fill intrabar` dễ gây lệch một nến ở lớp tiêu thụ |
| F7 | P2 | CONFIRMED | `except ValueError` làm luồng điều khiển; lỗi giá thực thi âm không có ngữ cảnh |
| F8 | P2 | CONFIRMED | Tài liệu không khớp implementation và cấu hình |

---

## C. Bảng bằng chứng

### F1 — Hiệu năng O(n²) và bộ nhớ (P1, CONFIRMED)

1. **Vị trí:** `engine.py::BacktestEngine.run`, `strategies/base_strategy.py::generate_signal`.
2. **Mã:**
   ```python
   bar = {c: float(frame.iloc[i][c]) for c in columns}          # tạo Series mỗi nến
   prefix = frame.iloc[start:i + 1].copy(deep=True)             # start=0 khi limit=None
   row = strategy.generate_signal(prefix)                       # mặc định gọi generate_signals(prefix)
   # base: signals.index.equals(completed_data.index)           # O(i) mỗi nến
   ```
3. **Vì sao là rủi ro:**
   - Với `limit=None`, tổng số dòng sao chép là Σi ≈ n²/2 ≈ **1,04×10¹²** dòng khi n = 1,44M. Với 5 cột float64 thì khoảng 40 TB lưu lượng bộ nhớ, **chưa tính** việc strategy tính lại chỉ báo trên toàn prefix.
   - Ngoại suy tuyến tính từ hai điểm trong benchmark của tài liệu (2.000 và 10.000 nến, chưa tái lập) cho ≈ 4–5 giờ cho **một** lần chạy.
   - Đường gia tăng: tài liệu ghi ≈ 251 µs/nến, tức ≈ 6 phút mỗi run. Quét 100 cấu hình sẽ là ≈ 10 giờ.
   - Kết quả giữ `AccountState` (kèm `Timestamp`) cho mỗi nến, cộng `events` và `orders`. Ước tính hàng trăm MB đến >1 GB (ước lượng, chưa đo).
   - Strategy kiểu mức (`close > x` trả 1 liên tục) tạo một `Order` và một event "rejected" cho mỗi nến khi đang giữ vị thế, làm danh sách phình theo O(n).
4. **Đầu vào tái hiện tối thiểu:** chuỗi n = 5k, 10k, 20k nến H1 ngẫu nhiên và strategy `generate_signals` vector hóa. So tổng số dòng truyền vào strategy.
5. **Kỳ vọng:** thời gian và bộ nhớ gần tuyến tính theo n ở đường được hỗ trợ chính thức.
6. **Hiện tại:** đường mặc định tăng bậc hai.
7. **Regression test (đề xuất, chưa chạy):** đăng ký marker `slow` trong `pyproject` vì đang bật `--strict-markers`.
   ```python
   import time, numpy as np, pandas as pd, pytest
   from core.cost_model import CostModel
   from core.engine import BacktestEngine
   from strategies.base_strategy import BaseStrategy

   class Inc(BaseStrategy):
       signal_history_limit = 1
       def generate_signal(self, d):
           return pd.Series({"signal": 0, "exit": False})

   def walk(n):
       c = 100 + np.cumsum(np.random.default_rng(0).normal(0, .1, n))
       o = np.r_[c[0], c[:-1]]
       return pd.DataFrame({"open": o, "high": np.maximum(o, c) + .05,
                            "low": np.minimum(o, c) - .05, "close": c, "volume": 1.},
                           index=pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC"))

   @pytest.mark.slow
   def test_incremental_path_scales_near_linearly(simulation_metadata):
       model = BacktestEngine(simulation_metadata, CostModel(0, 0, 0),
                              initial_capital=1e6, account_currency="USD", quantity=1)
       def timed(n):
           t = time.perf_counter(); model.run(walk(n), Inc()); return time.perf_counter() - t
       assert timed(40_000) / timed(20_000) < 2.6
   ```
8. **Sửa tối thiểu:**
   - Lấy OHLC từ mảng NumPy dựng một lần ngoài vòng lặp.
   - Tính Bid/Ask theo vector hoặc theo từng nến bằng số học thuần.
   - Dùng `frame.iloc[a:b]` không deep-copy khi pandas ≥ 3 (Copy-on-Write mặc định). Với pandas 2.x thì bật CoW hoặc giữ `.copy()`.
   - Đặt `signal_history_limit` thành bắt buộc cho strategy dùng cho dữ liệu lớn.
   - Không tạo `Order` hay event cho tín hiệu bị bỏ qua khi đã có vị thế (hoặc gộp bộ đếm).
   - **Cách đối chiếu trước/sau:** golden-master. Chạy bản cũ và bản mới trên ≥ 50 chuỗi ngẫu nhiên (seed cố định, có gap, SL/TP, tỷ giá) và so `old == new` bằng đẳng thức chính xác trên `orders/fills/trades/states/events`. Không dùng `approx`, vì các phép tính float giống hệt nhau thì kết quả phải bằng nhau từng bit.

---

### F2 — So sánh "chạm" và tick rounding dựa trên float (P1, SUSPECTED)

1. **Vị trí:** `execution.py::protective_exit`, `cost_model.py::side_bar` và `fill`.
2. **Mã:**
   ```python
   stop_hit = sl is not None and (bar["low"] <= sl if direction == 1 else bar["high"] >= sl)
   result = {name: float(value) + offset ...}        # Bid = Mid - s/2 trong float
   rounded = (ceil(ticks - 1e-9) if side == 1 else floor(ticks + 1e-9))
   ```
3. **Vì sao là rủi ro:**
   - Giá FX nằm trên lưới tick và SL/TP thường đặt đúng lưới. Trường hợp "chạm đúng" khi `Bid_low = Mid_low − s/2` là phổ biến.
   - `low <= sl` có thể sai lệch 1 ulp, khiến SL/TP bị bỏ lỡ hoặc kích hoạt ngẫu nhiên ở đúng biên. Kết quả vẫn tất định nhưng không đúng theo lưới.
   - Dung sai `1e-9` tính theo **tick** không co giãn. Với BTC (giá 10⁵, tick 0,01 → 10⁷ tick), ulp của `ticks` ≈ 1,9×10⁻⁹ > 1e-9. Giá đã nằm trên lưới có thể bị `ceil` đẩy thêm **1 tick bất lợi** dù slippage = 0.
   - Việc này thuộc nhóm "Sai Bid/Ask, tick rounding". Tôi chưa chạy nên chưa nêu được giá trị cụ thể bị lệch.
4. **Đầu vào tái hiện:** `CostModel(spread=k·1e-5, 0, 0)`; Mid low = m·1e-5; SL = (m − k/2)·1e-5 với k chẵn. Và `CostModel(0,0,0).fill` với giá = j·0,01, j ∈ [10⁷, 10⁷+2000].
5. **Kỳ vọng:** chạm đúng biên thì kích hoạt (`low_ticks <= sl_ticks` theo số nguyên tick). Giá trên lưới giữ nguyên khi slippage = 0.
6. **Hiện tại có thể:** một số biên không kích hoạt; một số giá BTC lệch +1 tick.
7. **Test (đề xuất):**
   ```python
   @pytest.mark.parametrize("k", [2, 4, 10, 16])
   def test_exact_touch_is_grid_exact(k):
       tick = 1e-5; costs = CostModel(k * tick, 0, 0)
       bad = []
       for m in range(100_000, 130_000, 7):
           bar = {"open": m*tick, "high": m*tick, "low": m*tick, "close": m*tick}
           low = costs.side_bar(bar, "Mid", -1)["low"]
           if not low <= (m - k // 2) * tick:
               bad.append(m)
       assert not bad

   def test_on_grid_price_not_moved_for_large_tick_counts(instrument):
       costs = CostModel(0, 0, 0)
       for j in range(10_000_000, 10_002_000):
           f = costs.fill(instrument=instrument, order_id=1, side=1, quantity=0.2,
                          timestamp=pd.Timestamp("2024-01-01", tz="UTC"),
                          price=j * 0.01, conversion_rate=1, reason="BUY")
           assert abs(f.price - j * 0.01) < 5e-3
   ```
8. **Sửa tối thiểu:**
   - Chuẩn hóa về số nguyên tick: `n = round(x / tick)`. Nếu `abs(x/tick − n) <= max(1e-9, 4·eps·abs(n))` thì dùng `n`.
   - So sánh chạm bằng số nguyên tick, hoặc dùng `isclose` có dung sai theo tick.
   - **Đối chiếu:** chạy differential test bản cũ/mới. Mọi khác biệt chỉ được xuất hiện ở các biên mà test liệt kê.

---

### F3 — Lệnh vào bị từ chối khi gap làm SL/TP không còn bao quanh giá khớp (P1, DESIGN LIMITATION + SUSPECTED)

1. **Vị trí:** `portfolio.py::open` (kiểm tra bracket) và `engine.py` (nhánh `except ValueError`).
2. **Mã:**
   ```python
   if level is not None and direction * (level - fill.price) * sign <= 0:
       raise ValueError("SL/TP must bracket the actual entry price.")
   ...
   try: portfolio.open(order, fill, rate)
   except ValueError as exc: rejection = str(exc)
   ```
3. **Vì sao là rủi ro:**
   - Giới hạn này đã được tài liệu hóa nên không phải bug.
   - Hệ quả định lượng: một lệnh BUY mà giá mở đã gap xuống dưới SL bị bỏ qua, không ghi nhận khoản lỗ. Đây là các kịch bản đuôi xấu nhất, nên kết quả có thể lạc quan.
   - `BacktestResult` chỉ có danh sách event, không có bộ đếm từ chối theo nguyên nhân. Người đọc kết quả khó biết tỷ lệ này.
4. **Đầu vào:** `bars.iloc[1] = [98, 99, 97, 98]`, BUY tại cuối nến 0 với `sl=99.5, tp=110`.
5. **Kỳ vọng:** hoặc lệnh được khớp rồi dừng lỗ theo chính sách rõ ràng, hoặc từ chối nhưng có mã lý do cấu trúc và bộ đếm tổng hợp trong kết quả.
6. **Hiện tại:** event `rejected` với chuỗi văn bản tự do, không có bộ đếm; PnL = 0 cho lệnh đó.
7. **Test (đề xuất):**
   ```python
   def test_gapped_entry_rejection_is_structured_and_counted(simulation_metadata, bars):
       bars.iloc[1] = [98., 99., 97., 98.]
       r = run(engine(simulation_metadata), bars, {1: {"signal": 1, "sl": 99.5, "tp": 110}})
       rej = [e for e in r.events if e["status"] == "rejected"]
       assert rej and rej[0]["code"] == "invalid_bracket"
       assert r.assumptions["rejected_orders"]["invalid_bracket"] == 1
   ```
8. **Sửa tối thiểu:** thêm trường `code` cho event, thêm `assumptions["rejected_orders"]` (đếm theo mã). Tùy chọn `bracket_policy="reject"|"fill_and_stop"`, mặc định giữ hành vi hiện tại.

---

### F4 — Vòng đời strategy và phản hồi vị thế (P1, CONFIRMED thiếu cơ chế; ảnh hưởng tùy strategy)

1. **Vị trí:** `strategies/base_strategy.py` (không có `reset`), `engine.py::run` (không gọi reset, không truyền trạng thái vị thế/fill).
2. **Mã:** `engine.run` gọi `strategy.generate_signal(prefix)` trực tiếp; `BaseStrategy.__init__` chỉ lưu `params`.
3. **Vì sao là rủi ro:**
   - Tài liệu giao cho strategy gia tăng việc "quản lý state, warm-up, khởi tạo lại cho mỗi run", nhưng engine không đảm bảo điều đó.
   - Dùng lại cùng một instance cho hai lần chạy làm state rò sang lần sau, và kết quả hai lần khác nhau dù cùng dữ liệu.
   - Strategy không biết vị thế đã đóng bởi SL/TP. Strategy giữ cờ "đang vào lệnh" nội bộ sẽ lệch trạng thái với engine.
4. **Đầu vào:** strategy với `self.n` tăng mỗi lần gọi, chạy hai lần trên cùng instance.
5. **Kỳ vọng:** hai lần chạy cho kết quả bằng nhau.
6. **Hiện tại:** lần hai khác lần một.
7. **Test (đề xuất):**
   ```python
   def test_rerun_same_strategy_instance_is_identical(simulation_metadata, bars):
       class Stateful(BaseStrategy):
           signal_history_limit = 1
           def __init__(self): super().__init__(); self.n = 0
           def generate_signal(self, d):
               self.n += 1
               return pd.Series({"signal": int(self.n == 1), "exit": False})
       model, s = engine(simulation_metadata), Stateful()
       a = model.run(bars, s, expected_timestamps=bars.index)
       b = model.run(bars, s, expected_timestamps=bars.index)
       assert a == b
   ```
8. **Sửa tối thiểu:** engine gọi `strategy = copy.deepcopy(strategy)` ở đầu `run`, hoặc thêm hook `reset()` mặc định no-op và gọi trước vòng lặp. Cân nhắc truyền `position_state` (direction, entry) cho strategy gia tăng như một tham số tùy chọn.

---

### F5 — Provenance và khả năng tái lập (P1, CONFIRMED thiếu dữ liệu)

1. **Vị trí:** `engine.py`, dict `assumptions` ở cuối `run`; `pyproject.toml`; trạng thái Git.
2. **Mã:** `assumptions` chứa `metadata, costs, quantity, initial_capital, execution, …`. Không có hash dữ liệu, tên lớp và params strategy, commit hay phiên bản thư viện, hash chuỗi tỷ giá.
3. **Vì sao là rủi ro:**
   - Một kết quả nghiên cứu không thể truy ngược chính xác đến dữ liệu, mã và môi trường tạo ra nó.
   - Mã được kiểm toán là working tree chưa commit (nhiều file `??` và `M`).
   - Không có file khóa phụ thuộc. `pyproject` cho phép `pandas>=2.2,<4`, `numpy<3`, nhưng chỉ được kiểm trên một tổ hợp (Python 3.15.2 / pandas 3.1.1 / numpy 2.5.5).
4. **Đầu vào:** bất kỳ lần chạy nào.
5. **Kỳ vọng:** kết quả mang đủ thông tin để tái lập.
6. **Hiện tại:** thiếu.
7. **Test (đề xuất):**
   ```python
   def test_result_records_provenance(simulation_metadata, bars):
       r = run(engine(simulation_metadata), bars, {})
       assert {"data_sha256", "strategy", "strategy_params", "library_versions"} <= r.assumptions.keys()
   ```
8. **Sửa tối thiểu:**
   - Ghi `hashlib.sha256(pd.util.hash_pandas_object(frame).values.tobytes())`.
   - Ghi `type(strategy).__qualname__` và `strategy.params`.
   - Ghi `importlib.metadata.version` của numpy/pandas/pyyaml.
   - Commit mã trước khi xuất kết quả nghiên cứu, và thêm lock file hoặc ma trận CI.

---

### F6 — Ngữ nghĩa nhãn thời gian (P2, DESIGN LIMITATION)

1. **Vị trí:** `engine.py`: `states.append(portfolio.mark(closing, …))`; fill intrabar dùng `opening`.
2. **Vì sao là rủi ro:**
   - Với nến nhãn `open` liền kề, `states[i].timestamp == data.index[i+1]`. Ghép theo timestamp với `data.index` dễ lệch một nến.
   - Fill SL/TP intrabar mang timestamp đầu nến, nhưng thời điểm thật không xác định. Lớp metrics hoặc chuỗi thời gian về sau không được dùng nó như thời điểm sự kiện.
   - Hiện `metrics.py` chưa triển khai, nên đây là rủi ro cho giai đoạn sau, không phải lỗi hiện tại.
3. **Test (đề xuất):** khóa hành vi `assert r.states[0].timestamp == bars.index[0] + pd.Timedelta("1h")`.
4. **Sửa tối thiểu:** thêm `bar_index` vào `AccountState` và `Fill`, để lớp tiêu thụ ghép theo chỉ số nguyên.

---

### F7 — Xử lý ngoại lệ (P2, CONFIRMED)

1. **Vị trí:** `engine.py` (`except ValueError`), `cost_model.py::side_bar` (`positive(value, "executable price")`).
2. **Vì sao là rủi ro:**
   - Mọi `ValueError` từ `portfolio.open` đều bị coi là "bị từ chối nghiệp vụ". Lỗi lập trình hoặc lỗi cấu hình có thể bị che thành event, và test đang khớp theo chuỗi văn bản ("Insufficient", "bracket").
   - `side_bar` ném `ValueError` chung chung nếu giá Bid/Ask ≤ 0 (spread lớn hơn giá). Run bị hủy giữa chừng, không nêu nến nào.
3. **Đầu vào:** `CostModel(250, 0, 0)` trên fixture bars, BUY tại cuối nến 0.
4. **Kỳ vọng:** lỗi nêu rõ timestamp/chỉ số nến, hoặc cấu hình bị chặn trước khi chạy.
5. **Test (đề xuất):**
   ```python
   def test_excess_spread_error_names_the_bar(simulation_metadata, bars):
       with pytest.raises(ValueError, match="2024-01-01"):
           run(engine(simulation_metadata, CostModel(250, 0, 0)), bars, {1: {"signal": 1}})
   ```
6. **Sửa tối thiểu:** lớp `OrderRejected(ValueError)` có thuộc tính `code`, chỉ bắt lớp này; bọc `side_bar` kèm timestamp.

---

### F8 — Tài liệu và cấu hình không khớp (P2, CONFIRMED / một phần chưa kiểm chứng)

- README nói `pyarrow` chưa cần và pytest có 1 bài, nhưng `pyproject.toml` đã yêu cầu `pyarrow>=23` và có 296 test.
- README khẳng định Python 3.11+, nhưng chỉ có bằng chứng chạy trên 3.15.2.
- `Instrument.pip_size` bắt buộc nhưng không dùng ở đâu trong phần mã đã đọc.
- Theo `08_AUDIT_HANDOFF.md`, `configs/config.yaml` có `include_swap=true` trong khi `CostModel` từ chối swap khác 0, và `slippage_points` cần quy đổi sang đơn vị giá. Tôi không đọc được file này nên chưa kết luận.
- Số benchmark trong `BACKTEST_ENGINE.md` chưa được tái lập (xem F1).
- `positive()` ném `TypeError` thay vì `ValueError` với kiểu không phải số (ví dụ chuỗi). Mức độ thấp.

---

## D. Những test còn thiếu

**Nhánh nghiệp vụ quan trọng chưa được kiểm thử** (xếp ở mức P1; theo mô tả test hiện có):

1. **Gap SHORT ở cấp engine.** Chỉ có test đơn vị `protective_exit` (không chi phí). Chưa có engine-level với slippage và tick rounding.
2. **Gap phá SL ngay nến vào lệnh,** gồm cả trường hợp SL nằm giữa Bid-open và giá vào, dẫn tới khớp và thoát cùng timestamp.
3. **EXIT pending cùng nến với SL/TP:** thứ tự xử lý và việc không đóng hai lần.
4. **EXIT pending khi giá mở gap qua TP:** EXIT lấy giá mở tốt hơn, còn TP gap bị chặn ở target. Cần test khóa hành vi này.
5. **Tín hiệu sau nến SL.** Strategy phát lệnh vào ngay sau khi vừa bị SL, kiểm tra đúng khớp ở nến kế tiếp.
6. **FX khác đồng tiền với nến nhãn `close`,** và thoát intrabar với tỷ giá thay đổi giữa nến.
7. **Bất biến đối soát kế toán trên chuỗi dài ngẫu nhiên:** `balance − vốn đầu = Σ gross_pnl(đã đóng) − Σ commission(đã trả, kể cả vị thế mở)`; `equity = balance + unrealized`; không có fill trước `submitted_at`. Nên dùng seed cố định hoặc `hypothesis`.
8. **Nhiều giao dịch liên tiếp** (hiện hầu hết test engine dùng fixture 4 nến và tối đa một giao dịch).
9. **Chế độ mặc định không lịch (production)** với nhiều nến và nhiều giao dịch. Phần lớn test engine truyền `expected_timestamps=bars.index`, tức là chạy chế độ lịch nghiêm ngặt với lịch tự suy từ dữ liệu. `test_intraday_gaps` chỉ dùng 2 nến và 1 lệnh BUY.
10. **Tick rounding ở giá lớn** (BTC) và exact-touch (F2).
11. **Đường 1,44M nến:** smoke test hiệu năng (F1) và golden-master tối ưu.
12. **Tái dùng strategy** (F4) và provenance (F5).
13. **Test nhân quả của engine yếu:** `test_future_candles_do_not_change_earlier_outputs` chỉ sửa **nến cuối**. Nên sửa nến k ngẫu nhiên và khẳng định mọi output thuộc nến < k không đổi.

---

## E. Những điểm thiết kế đã đúng, nên giữ nguyên

- Tách bạch tín hiệu cuối nến và khớp mở nến có dữ liệu kế tiếp, kèm chốt chặn `opening < order.submitted_at`.
- Strategy chỉ nhận **bản sao** của prefix đã hoàn tất; có test chống thay đổi đầu vào.
- Suy Bid/Ask từ một luồng giá với công thức đúng, chi phí chỉ nằm trong giá khớp. Các trường cost trong `Fill` chỉ để đối chiếu.
- Tick rounding theo hướng bất lợi và commission mỗi phía, tính theo đơn vị khai báo.
- SL ưu tiên khi cùng chạm kèm cờ `ambiguous`; gap SL ở giá mở; gap TP bị chặn ở target; SL/TP kiểm tra trên giá phía thanh lý (Bid cho long, Ask cho short).
- FX as-of, không nội suy và không lấy dữ liệu tương lai; thoát intrabar dùng tỷ giá đầu nến.
- Kế toán dự trữ 100% notional, không đòn bẩy; vị thế cuối mẫu giữ nguyên và được đánh giá, không ép đóng.
- Từ chối đầu vào xấu từ sớm (`Order`, `Fill`, `Position`, `ConversionRates`) bằng dataclass bất biến có kiểm tra.
- Tính tất định: không dùng ngẫu nhiên, có test replay `==`.
- Test với số tính tay (ví dụ 103,1 / 108,9 → net 52) và đối xứng long/short.

---

## F. Chưa thể kết luận

- **Chưa thấy mã:** `data_loader`, `data_validator` (hàm `validate_data`, `metadata_blockers`, logic gap trong ngày UTC, `interval_analysis`), `causality`, toàn bộ `indicators/*`, `benchmark_engine.py`, `configs/*`, `.clinerules` (00B), `00A`, `07_TEST_RESULTS` và `MANIFEST`. Tôi chỉ thấy các test của chúng.
- **Chưa kết luận về tính nhân quả của chỉ báo.** Test hiện cho thấy kiểm tra prefix-invariance, nhưng chưa xem mã.
- **Chưa kết luận về ngữ nghĩa nhãn thời gian của `sessions`.** `08_AUDIT_HANDOFF` nói yêu cầu timestamp khả dụng nhưng engine dùng nhãn open. Cần mã `sessions` và chiến lược dùng nó.
- **Chưa kết luận validator có kiểm tra khoảng cách chuẩn khớp `timeframe` đã khai báo hay không.** Nếu khai báo 1min mà dữ liệu thật 5min, chế độ mặc định chỉ cảnh báo.
- **Chưa thực thi:** không chạy test, benchmark, coverage hay dữ liệu thật (EURUSD M1 1,44M nến). Mọi con số về thời gian và bộ nhớ ở F1 là suy luận, chưa đo.
- **Chưa kiểm hash file** theo `MANIFEST.md`.
- **Phạm vi chưa có:** `core/metrics.py`, `data_manager.py`, `custom_indicators.py`, `first_strategy.py` chỉ là khung; validation, walk-forward và sensitivity chưa tồn tại. Tôi không tính đây là lỗi của giai đoạn hiện tại.

---

## G. Kế hoạch sửa lỗi theo thứ tự ưu tiên

1. **F1 (hiệu năng):**
   - Đo baseline thật trên 50k–200k nến.
   - Chuyển OHLC sang NumPy, bỏ `frame.iloc[i]` và deep-copy thừa, và giảm Order/event phình.
   - Chặn strategy kiểu mức khỏi spam đơn.
   - Giữ golden-master `==` đối chiếu trước/sau.
2. **F2 (float và tick):** chuẩn hóa về số nguyên tick, rồi thêm các test exact-touch và BTC (chạy test trước để xác nhận hoặc bác bỏ lỗi).
3. **F4 (vòng đời strategy):** `deepcopy` hoặc `reset()` đầu mỗi run; tùy chọn truyền trạng thái vị thế.
4. **F5 (provenance):** ghi hash dữ liệu, strategy, params, phiên bản thư viện; commit mã và thêm lock file trước khi tạo kết quả nghiên cứu.
5. **F3 (từ chối lệnh):** mã lý do cấu trúc và bộ đếm từ chối trong kết quả; cân nhắc chính sách `fill_and_stop`.
6. **Bổ sung test ở mục D** (gap SHORT, EXIT/SL cùng nến, bất biến kế toán trên chuỗi dài, chế độ không lịch nhiều lệnh).
7. **F6, F7, F8 (P2):** `bar_index` cho fill/state, `OrderRejected`, đồng bộ README/pyproject/config; thống nhất kiểu lỗi `positive()`.
8. Cung cấp mã `data_validator`, `data_loader`, `causality` và `indicators` để kiểm toán phần còn lại.

---

## H. Kết luận

**PASS WITH LIMITATIONS** cho phạm vi đã kiểm tra: logic mô phỏng lõi (`models`, `cost_model`, `execution`, `portfolio`, `engine`, `base_strategy`), đọc tĩnh cùng đối chiếu với test.

Điều kiện đi kèm:
- Đường strategy mặc định (full-prefix) **không đủ điều kiện** chạy 1,44M nến. Chỉ nên dùng đường gia tăng sau khi xử lý F1.
- F2, F4, F5 cần được xử lý hoặc kiểm chứng bằng chạy thật trước khi tin các kết quả nghiên cứu.
- Kết luận này không mở rộng sang loader, validator, indicators hay toàn dự án.
