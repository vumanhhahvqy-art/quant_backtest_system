# Kiểm định, thống kê và báo cáo

Không có thư mục validation/ tại thời điểm khảo sát. Không tìm thấy module walk-forward,
sensitivity, chronological train/validation/test orchestration, multiple-testing correction hay tối ưu OOS trong danh mục source.
core/metrics.py chỉ có docstring, chưa tính Winrate, Profit Factor, Sharpe hoặc drawdown.
core/causality.py có code thực: kiểm tra kết quả có đổi khi thêm phần dữ liệu tương lai trên các prefix của mẫu.
Đây là bằng chứng trên mẫu, không chứng minh nhân quả cho mọi đầu vào và không thay thế đánh giá OOS.
Các writer JSON/Parquet có code thật ở 02_DATA_AUDIT.md; inspect_data.py ghi báo cáo data quality.
Engine trả BacktestResult trong bộ nhớ; chưa có bộ xuất report backtest/config snapshot/checksum end-to-end.
inspect_indicators.py là smoke-check diagnostic ở 03G, chưa chạy trong nhiệm vụ này.
Không đóng gói báo cáo nghiên cứu cũ có khả năng chứa mẫu giá; không dùng kết quả cũ làm kết quả kiểm tra mới.

## File gốc: `core/causality.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\causality.py`

Số dòng: 40; kích thước: 1945 bytes; SHA256: `fe7fa61ef157e6ec5df20932e917380a144dba932e42c5f14f03af4c14b82afc`.

<!-- SOURCE_BEGIN core/causality.py -->
```python
"""Finite-sample prefix checks for indicator and feature builders."""

from collections.abc import Callable, Iterable

import pandas as pd


def check_prefix_invariance(
    builder: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
    data: pd.DataFrame,
    *,
    cutoffs: Iterable[int] | None = None,
) -> None:
    """Raise ValueError when a feature revises past output after seeing future rows.

    The builder must be deterministic and pure. Recompute features from raw
    inputs, rather than slicing already computed feature columns. Passing this
    check is evidence on supplied samples, not a proof for arbitrary inputs.
    By default every nonempty proper prefix is checked; use small fixtures.
    """
    def calculate(frame):
        result = builder(frame.copy(deep=True))
        if not isinstance(result, (pd.Series, pd.DataFrame)) or not result.index.equals(frame.index):
            raise ValueError("Feature builder must preserve its input index.")
        return result

    complete = calculate(data)
    for cutoff in range(1, len(data)) if cutoffs is None else cutoffs:
        if isinstance(cutoff, bool) or not isinstance(cutoff, int) or not 1 <= cutoff < len(data):
            raise ValueError("Causality cutoffs must be integers inside the sample.")
        prefix = calculate(data.iloc[:cutoff])
        try:
            if isinstance(complete, pd.DataFrame) and isinstance(prefix, pd.DataFrame):
                pd.testing.assert_frame_equal(complete.iloc[:cutoff], prefix)
            elif isinstance(complete, pd.Series) and isinstance(prefix, pd.Series):
                pd.testing.assert_series_equal(complete.iloc[:cutoff], prefix)
            else:
                raise ValueError("Feature builder changed output type.")
        except AssertionError as exc:
            raise ValueError(f"Future-dependent feature detected at prefix length {cutoff}.") from exc
```
<!-- SOURCE_END core/causality.py -->

## File gốc: `core/metrics.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\metrics.py`

Số dòng: 1; kích thước: 93 bytes; SHA256: `1bda281456baf27201e2cc167010aa01b2feb35b5f107b0ed2be9e80b0412317`.

<!-- SOURCE_BEGIN core/metrics.py -->
```python
"""Module tính toán hiệu suất: Winrate, Profit Factor, Sharpe Ratio, Max Drawdown."""
```
<!-- SOURCE_END core/metrics.py -->
