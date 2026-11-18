# BÁO CÁO KIỂM TOÁN ĐỘC LẬP — PHẠM VI GIỚI HẠN

**Lưu ý trước:** không có mã hay test nào được thực thi trong cuộc kiểm toán này. Mọi mục "kết quả hiện tại" bên dưới đều là suy luận từ việc đọc mã và cần chạy xác nhận.

Ngày kiểm toán: 2026-11-17 · Commit nền: `7af3b774b1721e091e2527a00563912255d44702` · File đã nhận: `00_PROJECT_OVERVIEW.md`, `04_STRATEGIES_AUDIT.md`, `06_VALIDATION_AUDIT.md`

---

## A. Kết luận tổng quan

**Phạm vi nhận được.** Ba file chứa mã thật của `core/causality.py`, `benchmark_engine.py`, `run_backtest.py`, `pyproject.toml`, `README.md` và `.gitignore`. Các file còn lại chỉ là stub hoặc docstring (`metrics.py`, `first_strategy.py`).

**Không nhận được** mã của `engine`, `execution`, `cost_model`, `portfolio`, `models`, `data_loader`, `data_validator`, `indicators/*` và `tests/*`. Vì vậy chưa thể kiểm toán bất kỳ hạng mục P0 nào: look-ahead trong engine, khớp lệnh ở nến kế tiếp, Bid/Ask, SL/TP/gap, P/L, equity. Việc không thấy P0 ở đây nghĩa là không có bằng chứng, không phải không có lỗi.

**Điểm đáng chú ý nhất trong phần đọc được:**

- `check_prefix_invariance` mạnh về ý tưởng nhưng có thể cho PASS giả (dung sai ngầm, input rỗng, trạng thái bắt qua closure) và không chạy được ở quy mô thật.
- Benchmark không chứng minh được gì về 1,44 triệu nến, và bước đối chiếu kết quả yếu.
- Mã được audit chưa nằm trong commit nào, và phụ thuộc chưa khóa.
- Con số "296 passed" là tự báo cáo. Không có `07_TEST_RESULTS.md` để đối chiếu, và số test đạt không chứng minh tính đúng.

---

## B. Vấn đề quan trọng (không có P0 xác lập được)

### P1-01 — Dung sai ngầm trong so sánh prefix · SUSPECTED

`assert_frame_equal` / `assert_series_equal` được gọi không đặt `check_exact`/`rtol`/`atol`. Theo mặc định đã biết của pandas (rtol 1e-5, atol 1e-8, cần xác nhận trên pandas 3.1.1), rò rỉ tương lai cỡ 0,1 pip trên giá ~1,1 có thể không bị phát hiện.

*Sửa tối thiểu:* mặc định so sánh chính xác, chỉ cho phép dung sai khi truyền tường minh.

### P1-02 — Không phát hiện rò rỉ qua trạng thái bên ngoài hoặc cột tính sẵn · DESIGN LIMITATION (rủi ro quy trình)

Chuẩn hóa toàn lịch sử đặt trong closure, hoặc cột z-score tính sẵn trên toàn bộ dữ liệu, cho kết quả giống hệt ở mọi prefix nên luôn PASS. Docstring có cảnh báo một phần ("recompute from raw inputs") nhưng không có gì cưỡng chế.

*Sửa:* test cấp pipeline, dựng toàn bộ feature, gồm cả tham số chuẩn hóa, bên trong builder từ dữ liệu thô.

### P1-03 — Đầu vào bất hợp lệ → PASS rỗng · CONFIRMED

`len(data) < 2` hoặc `cutoffs=[]` khiến vòng lặp không chạy và hàm trả `None` như thể đạt. Hàm không kiểm tra index tăng dần, duy nhất, tz-aware, nên "prefix" có thể không phải prefix theo thời gian. Ngoài ra `np.int64` bị từ chối vì `isinstance(cutoff, int)`, và cutoff sai chỉ bị phát hiện muộn, sau các phép tính tốn kém.

### P1-04 — Mặc định kiểm tra mọi prefix: O(n²) và không có chốt chặn · CONFIRMED (độ phức tạp từ mã)

Với n = 1,44e6 và builder O(n), tổng khoảng n²/2 ≈ 1,0e12 lượt đọc hàng, cộng một `deep copy` cho mỗi prefix. Docstring chỉ dặn "use small fixtures".

*Sửa:* từ chối khi `cutoffs is None` và n vượt ngưỡng; cung cấp bộ cutoff lấy mẫu có tính tất định (ranh giới cửa sổ ±1, đổi ngày UTC, đầu phiên, mẫu ngẫu nhiên có seed).

### P1-05 — Đường chiến lược "batch": an toàn nhân quả và hiệu năng chưa rõ · SUSPECTED

`BatchMean.generate_signals(data)` nhận toàn bộ DataFrame. Hoặc engine tin chiến lược (có thể rò rỉ tương lai), hoặc engine gọi lại trên từng prefix (O(n²)). Benchmark gợi ý khả năng thứ hai: `generate_signal(completed_data)`, `signal_history_limit = 1`, và chỉ số "speedup = Batch/Incremental". Đây chỉ là suy đoán từ cấu trúc benchmark vì `engine.py` không được cung cấp.

*Cần:* mã engine, rồi đo tại 10k/50k/100k/200k nến kèm `tracemalloc` và độ dốc log-log (≈2 nghĩa là O(n²)).

### P1-06 — Tái lập: mã audit chưa gắn với commit, phụ thuộc chưa khóa · CONFIRMED

Commit nền `7af3b77` không chứa `engine/execution/models/portfolio/data_loader/validator`: phần lớn là `??` untracked, còn `engine.py` và `cost_model.py` ở trạng thái `M` (sửa chưa commit). `numpy>=1.26,<3` và `pandas>=2.2,<4`, không có lock file. `requires-python>=3.11` nhưng bằng chứng chỉ có Python 3.15.2.

### P2-07 — Benchmark: bước kiểm chứng yếu và phạm vi hẹp · CONFIRMED

- `assert` bị bỏ qua khi chạy `python -O`, còn `"outputs_identical": True` là hằng số cố định.
- Chỉ so kết quả của lần lặp cuối, không kiểm tra các lần lặp có giống nhau không.
- `results[0] == results[1]` phụ thuộc `BacktestResult.__eq__` (chưa thấy). Nếu chứa DataFrame, phép `==` có thể ném lỗi hoặc so sai.
- Dữ liệu `open == close`, `CostModel(0,0,0)`, không SL/TP, kích thước mặc định tối đa 10.000, nên không chạm nhánh chi phí, SL/TP hay gap.
- Script chưa từng được chạy trong hồ sơ.

### P2-08 — Tài liệu không khớp · CONFIRMED

- README (≈dòng 72) nói "chưa cần pyarrow", nhưng `pyproject.toml` dòng 15 yêu cầu `pyarrow>=23`.
- README (≈dòng 60) nói "pytest có 1 bài test", trong khi overview báo 296.
- `run_backtest.py` in "đã sẵn sàng" dù chưa nối engine.
- Overview đã thừa nhận README cũ, nhưng chưa được sửa.

*Không tính là lỗi (phạm vi mục 7):* `metrics.py`, validation/walk-forward và `run_backtest.py` còn trống thuộc giai đoạn sau.

---

## C. Bảng bằng chứng

| ID | Vị trí | Mã gây vấn đề | Đầu vào tối thiểu | Mong đợi | Hiện tại (suy luận) |
|---|---|---|---|---|---|
| 01 | `causality.py` · `check_prefix_invariance` · L34,36 | `pd.testing.assert_frame_equal(complete.iloc[:cutoff], prefix)` | 10 nến, close=1.1, builder `d.close + 1e-5*(len(d)%2)` | `ValueError` | Không lỗi |
| 02 | L22 (`builder(...)`) | builder bắt biến ngoài | `G=df.close.mean()`; builder `d.close - G` | Bị cờ | Không lỗi |
| 03 | L27–28 | `range(1, len(data))` / `cutoffs` rỗng | `df.iloc[:1]` hoặc `cutoffs=[]` | `ValueError` | Trả `None` |
| 04 | L28, L22, L31 | vòng lặp mọi prefix + `copy(deep=True)` | n = 1,44e6 | Từ chối/yêu cầu cutoff | Chạy rất lâu hoặc hết RAM |
| 05 | `benchmark_engine.py` L19–21, L25, L77 | batch vs incremental | n lớn | Tăng gần tuyến tính | Chưa rõ |
| 06 | `pyproject.toml` L12–13 | `numpy>=1.26,<3`, `pandas>=2.2,<4` | — | Có lock file | Không có |
| 07 | `benchmark_engine.py` L74–75 | `assert …` rồi `"outputs_identical": True` | `python -O` | Thất bại khi khác | Ghi `True` không kiểm |
| 08 | README ≈L72, ≈L60; `pyproject` L15 | — | — | Khớp nhau | Mâu thuẫn |

---

## D. Test còn thiếu

Các test đề xuất cho 01–04 (chưa chạy):

```python
import numpy as np, pandas as pd, pytest
from core.causality import check_prefix_invariance

IDX = pd.date_range("2024-01-01", periods=10, freq="min", tz="UTC")
DF = pd.DataFrame({"close": np.full(10, 1.1)}, index=IDX)

def test_rejects_sub_tolerance_leak():                      # P1-01
    leaky = lambda d: d["close"] + 1e-5 * (len(d) % 2)
    with pytest.raises(ValueError, match="Future-dependent"):
        check_prefix_invariance(leaky, DF)

@pytest.mark.parametrize("n", [0, 1])
def test_rejects_too_short(n):                              # P1-03
    with pytest.raises(ValueError):
        check_prefix_invariance(lambda d: d["close"], DF.iloc[:n])

def test_rejects_empty_cutoffs():                           # P1-03
    with pytest.raises(ValueError):
        check_prefix_invariance(lambda d: d["close"], DF, cutoffs=[])

def test_rejects_unsorted_index():                          # P1-03
    with pytest.raises(ValueError):
        check_prefix_invariance(lambda d: d["close"], DF.iloc[::-1])

def test_accepts_numpy_integer_cutoffs():                   # P1-03
    check_prefix_invariance(lambda d: d["close"], DF, cutoffs=np.array([2, 5]))

def test_requires_cutoffs_for_large_sample():               # P1-04
    big = pd.DataFrame({"close": 1.0},
                       index=pd.date_range("2024", periods=50_000, freq="min", tz="UTC"))
    with pytest.raises(ValueError):
        check_prefix_invariance(lambda d: d["close"], big)

def test_captured_state_limitation_documented():            # P1-02 (characterization)
    g = DF["close"].mean()
    check_prefix_invariance(lambda d: d["close"] - g, DF)   # hiện PASS dù có rò rỉ; cần test pipeline từ dữ liệu thô
```

Còn thiếu:

- **Mutation test cho cutoff lấy mẫu:** rò rỉ chỉ ở một hàng (hàng *i* phụ thuộc hàng *i+1*) phải bị bộ cutoff lấy mẫu bắt được, đối chiếu với kết quả toàn bộ prefix trên fixture nhỏ.
- **Test benchmark:** monkeypatch engine để hai kết quả khác nhau, kỳ vọng exit khác 0, chạy cả bằng `subprocess` với `-O`.
- **Test run manifest:** đầu ra phải chứa git hash, cờ dirty, hash lock file và SHA256 dữ liệu.
- **Test engine (chưa xác minh có hay chưa vì thiếu `tests/`):**
  - tín hiệu ở nến *t* khớp ở nến *t+1*, không phải *t*;
  - BUY khớp theo Ask, SELL theo Bid;
  - SL ưu tiên trước TP khi cùng chạm;
  - gap qua SL/TP;
  - commission hai phía;
  - tín hiệu ở nến cuối bị bỏ;
  - vị thế mở cuối dữ liệu;
  - quy đổi quote/account không dùng tỷ giá tương lai.

---

## E. Thiết kế đúng, nên giữ

- **`causality.py`:**
  - `deep copy` trước khi gọi builder, chặn rò rỉ do builder sửa input;
  - kiểm tra giữ nguyên index;
  - từ chối `bool` làm cutoff;
  - so sánh nghiêm kiểu dữ liệu và coi NaN là bằng nhau;
  - `raise … from exc`;
  - docstring nói thẳng đây chỉ là bằng chứng trên mẫu, không phải chứng minh.
- **`benchmark_engine.py`:** lịch thời gian độc lập, không suy ra từ dữ liệu; dùng median; dữ liệu tất định; có ý định đối chiếu kết quả trước khi tính thời gian.
- **Overview (mô tả thiết kế):**
  - công bố trung thực các stub;
  - không dùng báo cáo cũ làm bằng chứng;
  - SHA256 từng file;
  - chi phí tập trung trong `CostModel`, spread/slippage nằm trong giá fill;
  - SL ưu tiên trước TP, gap stop dùng open (hướng thận trọng);
  - không cưỡng bức đóng vị thế cuối mẫu.
- **Cấu hình:** `.gitignore` loại dữ liệu thô và `reports/runs`; `pyproject` giới hạn gói đóng gói.

---

## F. Chưa thể kết luận

- **Thiếu file:** `01_CORE_AUDIT.md` (engine/execution/cost/portfolio/models/BaseStrategy), `02_DATA_AUDIT.md`, `03*` (indicators), `05/05B` (tests), `00A`, `00B` (quy tắc dự án) và `07_TEST_RESULTS.md`.
- **Không đánh giá được:** toàn bộ P0 ở mục 5 của đề, rò rỉ trong indicators, validator, và hiệu năng thực tế với 1,44 triệu nến (chưa có phép đo nào).
- **Chưa kiểm chứng:**
  - số 296 test đạt (không có stdout gốc);
  - phạm vi phủ nhánh (không có coverage);
  - `BacktestResult.__eq__`;
  - ngữ nghĩa `signal` và `exit`.
- **Cần xác nhận trong mã engine:** TP gap dùng giá target thay vì open. Hướng này thận trọng (đánh giá thấp lợi nhuận) nhưng bất đối xứng với SL gap. Cũng cần xác nhận "tỷ giá đã công bố" không lấy close của chính nến đó.

---

## G. Kế hoạch sửa (theo ưu tiên)

1. Commit hoặc tag toàn bộ mã đang audit, kèm stdout pytest gốc. Gửi các file còn thiếu, đặc biệt engine, execution, cost_model, portfolio, loader và validator, để mở khóa audit P0.
2. Sửa `causality.py` theo P1-01, 03, 04 (so sánh chính xác, kiểm tra input, chốt chặn cutoff cộng bộ cutoff lấy mẫu) kèm các test ở mục D.
3. Thêm test nhân quả cấp pipeline từ dữ liệu thô cho mọi indicator (P1-02).
4. Xác định cách engine xử lý chiến lược batch (P1-05), rồi benchmark nhiều quy mô kèm bộ nhớ và so băm kết quả trước/sau khi tối ưu.
5. Sửa benchmark: tính `identical` thật, `raise SystemExit` khi khác, so các lần lặp với nhau, thêm kịch bản có chi phí, SL/TP và gap.
6. Khóa phụ thuộc (lock/constraints), chạy CI ở cận dưới và cận trên của phiên bản, thêm run manifest.
7. Đồng bộ README và thông báo của `run_backtest.py`.

---

## H. Kết luận

**PASS WITH LIMITATIONS** — chỉ cho phạm vi đã đọc: `core/causality.py`, `benchmark_engine.py` và phần scaffolding. Không phát hiện lỗi P0 trong phạm vi này, nhưng có 6 vấn đề P1 và 2 vấn đề P2.

Với Backtest Engine, mô phỏng giao dịch và dữ liệu, **không đưa ra kết luận PASS/FAIL** vì thiếu mã nguồn. Chưa nên dùng kết quả backtest nào làm bằng chứng nghiên cứu cho đến khi hoàn tất bước 1 của kế hoạch sửa.
