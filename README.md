# Quant Backtest System

Hệ thống nghiên cứu và mô phỏng chiến lược trên dữ liệu Forex lịch sử.
Kết quả mô phỏng mang tính giả định và không bảo đảm lợi nhuận tương lai.

Giai đoạn 1 thiết lập môi trường Python, quản lý phụ thuộc và kiểm tra môi trường.
Giai đoạn 4 bổ sung engine mô phỏng một công cụ với lệnh thị trường ở nến kế tiếp,
SL/TP, chi phí và sổ tài khoản. Xem [quy ước engine](core/BACKTEST_ENGINE.md) để
biết giao diện API, công thức tính tay và các giới hạn hỗ trợ.

## Yêu cầu

- Python 3.11 trở lên và môi trường ảo riêng `.venv`.
- Thực hiện các lệnh PowerShell bên dưới tại thư mục gốc dự án.
- Cần kết nối kho gói Python khi cài thư viện lần đầu.

## Chuẩn bị môi trường

Kiểm tra Python và môi trường hiện có:

```powershell
python --version
Test-Path .\.venv\Scripts\python.exe
```

Chỉ tạo môi trường nếu chưa có `.venv`:

```powershell
python -m venv .venv
```

Nếu `.venv` đã tồn tại, kiểm tra trước khi sử dụng; không tạo đè hoặc xóa môi trường cũ:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.version); print(sys.executable); print(sys.prefix != sys.base_prefix)"
```

Cài dự án ở chế độ chỉnh sửa cùng công cụ kiểm thử:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -e ".[dev]"
```

Chế độ chỉnh sửa giúp thay đổi mã nguồn được nhận ngay trong môi trường.
Tùy chọn `--only-binary=:all:` yêu cầu các phụ thuộc có gói dựng sẵn,
tránh biên dịch NumPy hoặc pandas trên máy. Nếu không có gói tương thích,
hãy kiểm tra hỗ trợ phiên bản Python trước khi thay đổi môi trường.
Không cần kích hoạt `.venv` khi gọi trực tiếp trình thông dịch như trên.

Trong lần thiết lập trên máy này, lệnh chỉ dùng gói dựng sẵn không tìm thấy
PyYAML phù hợp. Lệnh sau đã cài thành công bằng cách cho phép riêng PyYAML
sử dụng mã nguồn hoặc gói trong bộ nhớ đệm:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --no-binary=PyYAML -e ".[dev]"
```

Môi trường đã kiểm tra: Python 3.15.2, NumPy 2.5.5, pandas 3.1.1,
PyYAML 6.0.3 và pytest 9.2.0. Kiểm tra import thành công,
`pip check` không phát hiện phụ thuộc lỗi và pytest có 1 bài test đạt.

## Thư viện ban đầu

| Thư viện | Mục đích |
| --- | --- |
| NumPy | Xử lý mảng và tính toán số |
| pandas | Dữ liệu dạng bảng và chuỗi thời gian |
| PyYAML | Đọc cấu hình YAML bằng `safe_load` |
| pytest | Chạy kiểm thử, thuộc nhóm phụ thuộc `dev` |

Phụ thuộc được khai báo tập trung trong `pyproject.toml`, với giới hạn phiên bản
chính để giảm nâng cấp ngoài dự kiến. Chưa cần SciPy, matplotlib, pyarrow hay
framework backtest trong giai đoạn này.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, yaml, pytest; print(numpy.__version__, pandas.__version__, yaml.__version__, pytest.__version__)"
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
```

Bài test `tests/test_environment.py` kiểm tra môi trường ảo, khả năng phối hợp
NumPy/pandas/PyYAML, phép tính đơn giản và chỉ mục thời gian UTC.
Đây là kiểm tra môi trường, chưa xác nhận tính đúng đắn của thuật toán backtest.
Cấu hình pytest nằm trong `pyproject.toml`; không cần `pytest.ini` riêng.

Để ghi nhận phiên bản đang cài:

```powershell
.\.venv\Scripts\python.exe -m pip list
```

Các khoảng phiên bản trong `pyproject.toml` chưa phải tệp khóa phụ thuộc.
Cài đặt ở thời điểm khác có thể chọn phiên bản khác; cần khóa phiên bản và
ghi nhận môi trường trước khi thực hiện các nghiên cứu cần tái lập chính xác.

## Sử dụng trong VS Code

Mở Command Palette bằng `Ctrl+Shift+P`, chọn **Python: Select Interpreter**,
rồi chọn `.venv\Scripts\python.exe` của dự án. Để chạy test trong giao diện,
chọn **Python: Configure Tests**, chọn **pytest** và thư mục **tests**.
Cấu hình VS Code có sẵn được giữ nguyên.

## Cấu trúc và nguyên tắc

- `.clinerules/`: bốn file quy tắc của dự án.
- `configs/`: cấu hình nghiên cứu.
- `core/`, `indicators/`, `strategies/`: các file khung hiện có.
- `data/raw/`, `data/processed/`, `data/metadata/`: dữ liệu và thông tin nguồn.
- `reports/runs/`: kết quả nghiên cứu theo từng lần chạy.
- `tests/`: kiểm thử tự động.

Dữ liệu gốc và báo cáo cũ phải được bảo toàn. Thời gian nội bộ sử dụng UTC
có múi giờ. Các bước sau cần kiểm tra dữ liệu và ngăn việc dùng thông tin tương lai
trước khi triển khai mô phỏng. Dự án chỉ phục vụ nghiên cứu lịch sử.