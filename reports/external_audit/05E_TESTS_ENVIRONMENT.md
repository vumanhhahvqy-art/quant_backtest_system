# 05E_TESTS_ENVIRONMENT

Toàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.

## File gốc: `tests/test_environment.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\tests\test_environment.py`

Số dòng: 22; kích thước: 759 bytes; SHA256: `880c51eaf356d9be1c8f8157a2f2ecc2335b64f98cc9fc9b2d1b7ab4b164aa6f`.

<!-- SOURCE_BEGIN tests/test_environment.py -->
```python
"""Smoke test for the isolated Python research environment."""

import sys

import numpy as np
import pandas as pd
import pytest
import yaml


def test_research_environment() -> None:
    """Verify library interoperability and timezone-aware data handling."""
    assert sys.version_info >= (3, 11)
    assert sys.prefix != sys.base_prefix, "Run tests inside the project virtual environment."

    config = yaml.safe_load("prices: [1.0, 2.0, 3.0]")
    timestamps = pd.date_range("2026-01-01", periods=3, freq="h", tz="UTC")
    prices = pd.Series(np.array(config["prices"], dtype=float), index=timestamps)

    assert prices.mean() == pytest.approx(2.0)
    assert prices.index.equals(timestamps)
    assert str(prices.index.tz) == "UTC"
```
<!-- SOURCE_END tests/test_environment.py -->
