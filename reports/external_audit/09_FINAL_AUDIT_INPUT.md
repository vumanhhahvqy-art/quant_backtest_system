# Hồ sơ đầu vào kiểm toán tổng hợp cuối cùng

Ngày chuẩn bị: 2026-11-17. Đây là hồ sơ bàn giao và kiểm tra tính đầy đủ của tài liệu; không đưa ra phán quyết chất lượng toàn hệ thống. Các phát hiện và kết luận độc lập vẫn thuộc về bốn báo cáo Claude gốc, không được sửa hoặc nâng/hạ mức trong hồ sơ này.

Gốc dự án: `C:/Users/Admin/Documents/quant_backtest_system/`. Gốc hồ sơ: `C:/Users/Admin/Documents/quant_backtest_system/reports/external_audit/`. Các định danh file tương đối trong bảng đều được tính từ hai gốc này như chỉ rõ ở từng phần. `L` chỉ dòng trong file gốc, không phải dòng trong block Markdown đóng gói.

## 1. Tài liệu nền đã đọc

- Toàn bộ bốn file trong `.clinerules/`: `01-project.md`, `02-architecture.md`, `03-backtest-rules.md`, `04-coding-standards.md`.
- `README.md`, `core/BACKTEST_ENGINE.md`, `indicators/INDICATORS.md`.
- Hồ sơ kiến trúc quan sát và danh mục: `00_PROJECT_OVERVIEW.md`, `00A_SOURCE_INVENTORY.md`, `MANIFEST.md`, `08_AUDIT_HANDOFF.md`, cùng dữ liệu định danh trong `baseline.json`.
- Bốn báo cáo Claude bên dưới và mã nguồn các API tại ranh giới tích hợp.
- Phần đầu `07_TEST_RESULTS.md` để nhận diện bằng chứng thực thi cũ và giới hạn của nó.

Kiến trúc trong `.clinerules/02-architecture.md` là kiến trúc mục tiêu, không phải danh sách chức năng đã triển khai. Theo phạm vi đã ghi trong `00_PROJECT_OVERVIEW.md` L49–55 và `08_AUDIT_HANDOFF.md` L31–39, chế độ gap mặc định chỉ cảnh báo giữa hai timestamp liên tiếp cùng ngày UTC; lịch độc lập là tùy chọn. Cần giữ bối cảnh này khi đọc các kiến nghị của Claude, không tự sửa quy tắc hoặc kết luận trong báo cáo gốc.

## 2. Bốn báo cáo độc lập và tính đầy đủ

Các tên file trong phần này nằm dưới gốc hồ sơ. “Có” nghĩa là có nội dung trong báo cáo, không có nghĩa phát hiện đã được tái hiện hoặc xác minh đúng.

| Nhóm / báo cáo | Phạm vi thực tế được Claude khai báo | P0/P1/P2 và trạng thái gốc | Bằng chứng | File/hàm/dòng mã nguồn | Chưa xác minh | Kết luận riêng |
|---|---|---|---|---|---|---|
| CORE — `CLAUDE_AUDIT_CORE.md` | L3–9: models, execution, costs, portfolio, engine, BaseStrategy, tài liệu engine, README/pyproject, tests 05A–05D; đọc tĩnh | Mục B L29–41: không có P0 được xác nhận; F1–F5 là 5 P1; F6–F8 là 3 P2; giữ CONFIRMED/SUSPECTED/DESIGN LIMITATION | Mục C L45–270: trích mã, phân tích, ví dụ và test đề xuất; không có kết quả thực thi mới | Có file/hàm/đoạn neo; **thiếu số dòng nguồn chính xác**, đã khai báo tại L5; F8 có phần dẫn qua tài liệu chưa nhận | Mục F L309–317; mục D L274–290 | Mục H L338–345 |
| DATA — `CLAUDE_AUDIT_DATA.md` | L3–8: loader, validator, inspect_data, config và metadata; khoảng 13/54 file theo báo cáo | Mục B L21–32: không xác nhận P0; #1–#3 là 3 P1; #4–#8 là 5 P2; có cả xác nhận và nghi ngờ | Mục C L36–174: đoạn mã, mẫu đầu vào, dự đoán và test đề xuất | Có file/hàm ở nhiều phát hiện; **thiếu số dòng nguồn chính xác** (L6); #3/#5 là đối chiếu cấu hình, #7 mô tả thao tác chưa neo dòng | Mục F L211–218; danh sách test cần bổ sung L182–193 | Mục H L233–242 |
| INDICATORS — `CLAUDE_AUDIT_INDICATORS.md` | L3–5: 7 module, utils/init/stub, inspect_indicators, test_indicators, tài liệu nền; không có engine/BaseStrategy | Mục B L18–31: #1 P0 có điều kiện, **SUSPECTED**; #2–#6 là 5 P1; #7–#10 là 4 P2 | Mục C L35–124: bảng trích mã, ví dụ và đề xuất; thời gian/sai số nghi ngờ chưa đo | Có tên file/hàm và đoạn neo; **thiếu số dòng nguồn chính xác** (L5); #7–#10 gộp nhiều vị trí | Mục F L157–166; mục D L126–139 | Mục H L182–189 |
| STRATEGIES/VALIDATION — `CLAUDE_AUDIT_STRATEGIES.md` | L5, L11–13: causality, benchmark và scaffolding từ 00/04/06; **không nhận BaseStrategy**, engine hay tests | Mục B L24–73: không có P0 xác lập; P1-01–06 là 6 P1; P2-07–08 là 2 P2 | Mục C L77–88: file/dòng/đoạn mã và đầu vào; mục D là test đề xuất chưa chạy | Có số dòng cho nhiều mục; **chưa đầy đủ/chính xác cho mọi vị trí**: README dùng ≈L60/72; mục 05 dẫn L19–21 trong khi class bắt đầu L18 và method L19–22 ở snapshot hiện tại; cần neo toàn bộ vị trí #06–08 liên quan Git/runner | Mục F L173–182 | Mục H L198–202 |

Tất cả bốn báo cáo có phạm vi, phân hạng, bằng chứng tĩnh, phần chưa thể kết luận và kết luận riêng. Chưa báo cáo nào cung cấp bằng chứng chạy mới từ chính phiên Claude. Không được coi các regression test đề xuất là test đã tồn tại hoặc đã đạt.

### 2.1. Kết luận riêng — trích nguyên văn, không phải kết luận tổng hợp

CORE, L340:

> **PASS WITH LIMITATIONS** cho phạm vi đã kiểm tra: logic mô phỏng lõi (`models`, `cost_model`, `execution`, `portfolio`, `engine`, `base_strategy`), đọc tĩnh cùng đối chiếu với test.

Điều kiện gốc tại L342–345 vẫn áp dụng: giới hạn đường full-prefix 1,44M nến; F2/F4/F5 cần xử lý hoặc kiểm chứng; không mở rộng kết luận sang loader, validator, indicators hoặc toàn dự án. Đọc toàn bộ mục H trong bản gốc khi viện dẫn.

DATA, L235–237:

> **PASS WITH LIMITATIONS — chỉ cho lớp nạp và kiểm tra dữ liệu và metadata.**
>
> Không có lỗi P0 được xác nhận trong phạm vi này, nhưng có 3 mục P1 cần xử lý. **Chưa thể ra phán quyết** cho Backtest Engine, chỉ báo hay toàn hệ thống vì chưa nhận được mã nguồn tương ứng.

INDICATORS, L184:

> **`PASS WITH LIMITATIONS`**, chỉ cho lớp indicators và test của chúng, dựa trên đọc mã.

Các giới hạn nguyên bản L186–189 vẫn áp dụng: #1 có thể nâng thành P0 nếu xác nhận lệch nhãn; giới hạn hiệu năng SAR/structure_breaks; không kết luận engine/loader/validator. Đọc toàn bộ mục H trong bản gốc khi viện dẫn.

STRATEGIES/VALIDATION, L200–202:

> **PASS WITH LIMITATIONS** — chỉ cho phạm vi đã đọc: `core/causality.py`, `benchmark_engine.py` và phần scaffolding. Không phát hiện lỗi P0 trong phạm vi này, nhưng có 6 vấn đề P1 và 2 vấn đề P2.
>
> Với Backtest Engine, mô phỏng giao dịch và dữ liệu, **không đưa ra kết luận PASS/FAIL** vì thiếu mã nguồn. Chưa nên dùng kết quả backtest nào làm bằng chứng nghiên cứu cho đến khi hoàn tất bước 1 của kế hoạch sửa.

### 2.2. Nội dung còn thiếu phải giữ trong bàn giao

1. CORE/DATA/INDICATORS: ánh xạ từng phát hiện sang số dòng nguồn chính xác; STRATEGIES: hoàn thiện các neo gần đúng/thiếu như bảng trên. Không chèn lại số dòng vào các bản Claude gốc.
2. Từng phiên Claude: hash của gói đầu vào thực nhận, định danh phiên/model và bản xác nhận danh sách file đầu vào có hash. Hiện chỉ có lời khai phạm vi và tên gói. Ngày audit của CORE/DATA/INDICATORS: UNKNOWN; STRATEGIES ghi 2026-11-17.
3. Từng phiên: kết quả tái hiện các mục SUSPECTED, benchmark thời gian/bộ nhớ, coverage và chứng cứ runtime: chưa có. Không suy diễn từ nhãn CONFIRMED khi bằng chứng chỉ là đọc mã.
4. CORE: mã loader/validator/causality/indicators/config và manifest/rules/results chưa nhận; DATA: mã core mô phỏng, indicators/causality và tests chưa nhận; INDICATORS: core/BaseStrategy/causality/data/metadata và results chưa nhận; STRATEGIES: core/BaseStrategy/data/indicators/tests/rules/results chưa nhận. Xem chính xác từng mục F của bốn bản gốc. Các gói hiện có trong thư mục hồ sơ, nhưng việc có trên máy không có nghĩa phiên Claude trước đã đọc.
5. Bằng chứng kiểm toán tích hợp từ đầu đến cuối giữa các nhóm, bao gồm nhãn thời gian, trạng thái strategy, metadata/specs/đơn vị chi phí và đầu ra nghiên cứu: chưa có kết luận chung. Những phần chưa triển khai được kê riêng bên dưới.

## 3. Phiên bản và chuỗi truy xuất bằng chứng

| Thông tin | Giá trị / mức độ biết được |
|---|---|
| Git HEAD tại lần chuẩn bị này | `7af3b774b1721e091e2527a00563912255d44702` |
| Commit nền của snapshot cũ | Cùng hash đầy đủ, được ghi tại MANIFEST L3 và overview L3 |
| Thời điểm snapshot cũ | `2026-11-17T09:33:31.742505+00:00` theo MANIFEST/baseline |
| Commit chứa đầy đủ mã được kiểm toán | **UNKNOWN**; HEAD nền không đại diện cho working tree có sửa đổi và file untracked |
| Hash toàn snapshot mà từng Claude thực nhận | **UNKNOWN** cho cả bốn; không báo cáo nào ghi SHA256 gói đã nhận |
| CORE: định danh phiên bản trong báo cáo | F5 nhắc working tree chưa commit; không ghi commit/hash snapshot cụ thể: **UNKNOWN** |
| DATA: định danh phiên bản trong báo cáo | Không ghi commit/hash snapshot cụ thể: **UNKNOWN** |
| INDICATORS: định danh phiên bản trong báo cáo | #10 ghi commit nền ngắn `7af3b77`; commit/hash của mã đã audit: **UNKNOWN** |
| STRATEGIES: định danh phiên bản trong báo cáo | L5 ghi commit nền đầy đủ; L19/L56 ghi mã chưa commit; commit/hash của toàn bộ mã đã audit: **UNKNOWN** |
| Đối chiếu hiện tại → baseline | Đã tính SHA256 bytes: **54/54 file nguồn khớp**, không thiếu/khác |
| Đối chiếu hiện tại → manifest gói | Đã kiểm bytes và SHA256: **23/23 gói Markdown khớp**, không thiếu/khác |
| Ý nghĩa của đối chiếu | Nguồn hiện tại khớp snapshot đóng gói có sẵn; không chứng minh gói nào đã được tải vào từng phiên Claude hoặc tính đúng của kết luận |

Trạng thái Git trước tạo hồ sơ: 6 tracked file có sửa đổi (`README.md`, `core/cost_model.py`, `core/engine.py`, `indicators/__init__.py`, `pyproject.toml`, `strategies/base_strategy.py`); nhiều source/test và toàn bộ hồ sơ audit là untracked. Không tạo commit/tag, không reset hay chuẩn hóa line endings trong công việc này.

SHA256 bốn bản Claude, tính trên bytes gốc trước tạo hồ sơ (hash này nhận diện báo cáo, **không phải hash phiên bản mã được kiểm toán**):

| Báo cáo | SHA256 |
|---|---|
| `CLAUDE_AUDIT_CORE.md` | `a7531ac5b716098f69dba17c40cfbd22ac2dfae1798f1b099357c732e7de5a96` |
| `CLAUDE_AUDIT_DATA.md` | `d1b40da6bed2de2073c2b3fbac4be51b4645c48e825ab372d46e1a63647b4b0a` |
| `CLAUDE_AUDIT_INDICATORS.md` | `2d9ecb7a9f2d5627427d18fda8765e709128ef9c5c646a80dd6f2805d041725a` |
| `CLAUDE_AUDIT_STRATEGIES.md` | `3301ec70c454cf2ca29278f49eb364c3376f9a30ede2f54d8926aec31a2b1467` |

Manifest cũ không bao gồm bốn báo cáo Claude và file 09 này; không cập nhật manifest cũ để tránh làm thay đổi bằng chứng trước đó. Gói chứa source giữ nguyên CRLF/BOM theo manifest; không thêm số dòng vào nội dung source đóng gói.

## 4. Mã thật, file khung và phần chưa triển khai

Các file sau nằm dưới gốc dự án. “Mã thật” chỉ xác nhận có implementation, không xác nhận tính đúng hoặc mức bao phủ kiểm thử.

| Thành phần | Trạng thái quan sát |
|---|---|
| `core/data_loader.py`, `core/data_validator.py` | Mã thật: CSV/Parquet, metadata, diagnostics, validation/gap và xuất JSON dữ liệu |
| `core/models.py`, `core/cost_model.py`, `core/execution.py`, `core/portfolio.py`, `core/engine.py` | Mã thật: records/specs, chi phí, protective exit, sổ tài khoản, điều phối mô phỏng một công cụ/một vị thế |
| `core/causality.py` | Mã thật: `check_prefix_invariance`; không phải walk-forward/validation thống kê |
| `indicators/moving_averages.py`, `trend.py`, `momentum.py`, `volatility.py`, `market_structure.py`, `price_action.py`, `sessions.py`, `_utils.py`, `__init__.py` | Mã thật: hàm tái sử dụng, helper và exports; chi tiết API/công thức ở 00A và INDICATORS.md |
| `strategies/base_strategy.py` | Có giao diện thật và adapter `generate_signal`; `generate_signals` yêu cầu lớp con triển khai |
| `benchmark_engine.py` | Mã benchmark với `BatchMean`/`IncrementalMean`; ví dụ tổng hợp, không phải chiến lược nghiên cứu hoàn chỉnh |
| `inspect_data.py`, `inspect_indicators.py` | Mã chẩn đoán thật; có ghi artifact chẩn đoán, không phải runner backtest tích hợp |
| `run_backtest.py` L4–6 | Chỉ in thông báo/thư mục; chưa nạp config, tạo engine, chạy mô phỏng hoặc lưu kết quả |
| `configs/config.yaml`, `configs/data_pipeline.yaml`; ba file dưới `data/metadata/` | Có cấu hình/metadata thật; config backtest chưa nối runner; data_pipeline được inspect_data sử dụng |
| 11 file `tests/test_*.py` | Có mã test thật; kết quả cũ nằm trong 07, không chạy lại trong lần chuẩn bị hồ sơ này |
| `core/data_manager.py`, `core/metrics.py`, `indicators/custom_indicators.py`, `strategies/first_strategy.py` | File khung/docstring/import, chưa có logic chức năng tương ứng |
| `core/__init__.py`, `strategies/__init__.py` | Rỗng, dùng khởi tạo package |
| `strategies/trend_following.py`, `strategies/mean_reversion.py` | Chưa có file; chưa có chiến lược nghiên cứu hoàn chỉnh trong strategies |
| `validation/`, `validation/walk_forward.py`, `validation/sensitivity.py` | Chưa tồn tại |
| Metrics hiệu suất/rủi ro; xuất trade log/equity/metrics và manifest run từ BacktestResult | Chưa triển khai pipeline; engine chỉ trả kết quả trong bộ nhớ; JSON chẩn đoán dữ liệu không thay thế báo cáo backtest |
| Backtest runner/config validation/sizing theo risk_per_trade | Chưa nối/triển khai đầy đủ; không coi các giá trị YAML là hành vi thực thi |

## 5. Phạm vi giao nhau và khoảng trống kiểm toán

“Đọc toàn văn” theo lời khai báo cáo; “tham chiếu” qua test/mô tả không được tính thành kiểm toán implementation.

| Module/tài liệu | Nhóm đã đọc theo báo cáo | Vùng giao nhau hoặc khoảng trống |
|---|---|---|
| `strategies/base_strategy.py` | CORE | Thuộc kiến trúc STRATEGIES nhưng không được phiên STRATEGIES nhận; cần ghép với engine và indicator outputs |
| `core/causality.py` | STRATEGIES/VALIDATION | Nằm dưới core nhưng CORE chưa đọc; nhóm INDICATORS kiểm tra prefix riêng trong test/diagnostics, không đọc helper này |
| Core models/costs/execution/portfolio/engine | CORE | DATA/INDICATORS/STRATEGIES chỉ tham chiếu hoặc chưa có mã; các hợp đồng liên nhóm chưa được kiểm toán đồng thời |
| Loader/validator/inspect_data/config/metadata | DATA | CORE đọc tests 05C nhưng chưa đọc implementation data; cần phân biệt test coverage với phạm vi nguồn |
| 7 module chỉ báo/utils/init/inspect_indicators | INDICATORS | CORE đọc test 05D nhưng chưa đọc implementation indicators |
| `tests/test_indicators.py` (05D) | CORE và INDICATORS | Giao nhau toàn văn test theo lời khai; chưa có lần chạy từ hai phiên |
| README/pyproject và nội dung chung trong 00 | Cả bốn | Giao nhau tài liệu; phạm vi run_backtest/.gitignore được DATA/INDICATORS/STRATEGIES khai báo qua 00; CORE không khai báo rõ đã đọc hai file này |
| `tests/test_stage4_review.py` | CORE qua 05B | Có liên kết SMA/causality/BaseStrategy/engine/portfolio; phiên STRATEGIES không nhận, cần đưa vào audit tích hợp |
| `tests/test_environment.py` (05E) | Không nhóm nào khai báo rõ đã đọc toàn văn | Khoảng trống trong bốn phiên; gói có sẵn |
| Bốn file `.clinerules/` | Không nhóm nào khai báo đã đọc toàn văn; các mục F nói thiếu 00B | Khoảng trống về đối chiếu quy tắc, dù quy tắc đã được đóng gói |
| `core/data_manager.py` | DATA nhận gói chứa file; không có đánh giá riêng rõ ràng | Chỉ là stub, không được tính thành chức năng data manager đã audit |
| `core/metrics.py`, `strategies/first_strategy.py`, `indicators/custom_indicators.py` | Nhóm tương ứng có nhận/nhận diện stub | Chưa có logic để audit tính toán hoặc chiến lược |
| `core/__init__.py`, `strategies/__init__.py` | Gói CORE/STRATEGIES chứa file rỗng | Không có logic; không có bằng chứng nhận xét riêng cho từng initializer |
| Runner → toàn hệ thống; Portfolio → metrics/research reports; walk-forward/sensitivity | Chưa có implementation hoàn chỉnh | Khoảng trống chức năng, không tự suy thành lỗi đã xác nhận |
| `.vscode/settings.json` | Có trong 00; không có xác nhận đọc riêng | UNKNOWN về phạm vi đọc riêng, không phải module tài chính |

Không có module Python sản phẩm nào ngoài danh mục 54 file được tìm thấy trong các thư mục core/indicators/strategies/tests và các script gốc đã kiểm kê. `download/` hiện có các JSON dữ liệu; dữ liệu lịch sử, cache, môi trường, Git và reports/runs nằm ngoài phạm vi gói cũ. `build_audit.py`/`audit_evidence.py` trong thư mục hồ sơ là công cụ tạo hồ sơ, không thuộc bốn nhóm kiểm toán mã sản phẩm; không coi là đã được bốn phiên audit.

## 6. Bảng đối chiếu API liên kết

Neo dòng dưới đây được đối chiếu từ mã hiện tại khớp SHA256 baseline; đây là mô tả hợp đồng và câu hỏi bàn giao, không đóng các phát hiện Claude.

| Liên kết | Producer → consumer và dữ liệu | Trạng thái thực tế / vị trí | Điểm cần kiểm toán tổng hợp, bằng chứng liên quan |
|---|---|---|---|
| Data Loader → Data Validator | `load_csv(path, metadata, diagnostic=False, column_map=None, delimiter=',') -> LoadResult(data, diagnostics)`; `load_parquet(path) -> DataFrame`; `validate_data(data, metadata, load_diagnostics=None, expected_timestamps=None) -> dict` | `core/data_loader.py` L37/L108/L189–192/L231; validator L45–51/L191–194; lời gọi thật tại `inspect_data.py` L89–90. Loader không tự gọi validator | UTC DatetimeIndex, cột OHLC chữ thường, bảo toàn dòng; token lỗi thành NaN/NaT; báo cáo có errors/metadata_blockers/ready_for_research. DATA #2 nghi ngờ nơi gọi; engine L94–96 có chặn errors/blockers. Cần kiểm chứng hợp đồng trên mọi entry point, không tự đổi trạng thái #2 |
| Data Validator → Indicators | Validator trả **báo cáo**, không trả DataFrame đã biến đổi; caller chuyển DataFrame/Series/index vào các hàm indicators | Không có lời gọi trực tiếp validator → indicators. `indicators/_utils.py` L9/L21/L35/L42 kiểm đầu vào riêng; `INDICATORS.md` L8–21 yêu cầu validate trước nghiên cứu. `inspect_indicators.py` L49–50 chỉ load_parquet + ohlc | Kiểm tra metadata gate có được duy trì khi rời pipeline; helper indicators cho phép NaN và cả index không phải DatetimeIndex nếu hợp lệ, không tương đương validator nghiên cứu. DATA #1/#2/#3; INDICATORS #1/#4 |
| Indicators → BaseStrategy | Hàm chỉ báo trả Series/DataFrame cùng index; lớp con tự import và dùng để phát tín hiệu | `BaseStrategy` L12/L21 không tự tính/import indicators. Ví dụ SMA trong `benchmark_engine.py` (`BatchMean` L18, `generate_signals` L19; `IncrementalMean` L24) và `tests/test_stage4_review.py` L60–78 | Chưa có strategy nghiên cứu hoàn chỉnh. Cần kiểm warm-up/NaN và alignment; đặc biệt sessions yêu cầu availability/close index (`INDICATORS.md` L12–14), trong khi engine giữ nhãn input khi truyền prefix. INDICATORS #1 là P0 có điều kiện/SUSPECTED, chưa đóng |
| BaseStrategy → BacktestEngine | Engine gọi `strategy.generate_signal(completed_data) -> Series`; adapter mặc định gọi `generate_signals -> DataFrame` cùng index, lấy dòng cuối. `signal=1/-1/0`, `exit` boolean tùy chọn, `sl/tp` giá tuyệt đối | BaseStrategy L7/L9/L12–33; engine L103–107/L186–209. Prefix đã đóng, có thể giới hạn `signal_history_limit`; timestamp index đầu vào giữ nguyên | 0 không đóng vị thế; exit và entry không cùng lúc; tạo Order tại closing và chờ open nến quan sát kế tiếp. Cần kiểm reset/tái dùng state, full-prefix/bounded history, cột tính sẵn. CORE F1/F4; STRATEGIES P1-02/P1-05; tests 05B |
| BacktestEngine → Execution/CostModel | `side_bar(bar, price_type, side) -> dict`; `protective_exit(Position, executable_bar) -> ExitDecision hoặc None`; `CostModel.fill(...) -> Fill` | Engine L124–129/L149–155/L163–177; CostModel L29/L40; execution L11/L18 | Market timing ở engine; protective decision ở execution; fill và chi phí ở CostModel. BUY Ask, SELL Bid; trigger theo phía thanh lý. Spread/slippage đơn vị giá; commission theo quantity khai báo, tiền tài khoản/mỗi phía; swap khác 0 bị từ chối. Kiểm tick/exact-touch, gap, SL trước TP, EXIT pending trước protective exit. CORE F2/F3/F7; DATA #3/#5 |
| Execution → Portfolio | Execution trả ExitDecision(price, reason, ambiguous, timing); **engine** tạo Fill qua CostModel rồi gọi `Portfolio.open(order, fill, rate)` hoặc `close(fill, rate)` | Không có import/call trực tiếp execution → portfolio. `core/execution.py` L18–37; engine L151–155/L167–174; portfolio L17/L39 | Fill chứa timestamp/quantity/side/commission/cost diagnostics; FX là account currency trên 1 quote currency. Kiểm ID, thứ tự thời gian, bracket actual fill, đối soát chi phí một lần và gap rejection. CORE F3/F6/F7; 05A/05B |
| Portfolio → Metrics/Reports | `open` cập nhật vị thế; `close -> Trade`; `mark -> AccountState`; engine gom vào `BacktestResult` (orders/fills/trades/states/events/open_position/assumptions) | Portfolio L17/L39/L58; models L138/L146; engine L24–33/L181/L214–229. `core/metrics.py` chỉ docstring | Chưa có consumer metrics/report backtest. Cần phân biệt balance/equity/net/gross, vị thế mở cuối mẫu, timestamp close/intrabar và provenance; CORE F5/F6. Không coi output JSON chẩn đoán data là report của BacktestResult |
| Runner/Config → toàn hệ thống | API engine có metadata, costs, initial_capital, account_currency, quantity; `run` nhận data/strategy/lịch/FX. YAML backtest chưa chuyển thành các đối tượng này | `run_backtest.py` L4–6 chỉ print; config.yaml L2–14 chưa được runner đọc. `inspect_data.py` L41–47 đọc data_pipeline.yaml và chỉ chạy diagnostic; benchmark tự khởi tạo đối tượng | Chưa có pipeline config → loader → validation → indicators/strategy → engine → metrics/report. Chưa có config schema validation backtest hoặc sizing risk_per_trade. DATA #5, CORE F8, STRATEGIES P2-08; không coi include_swap/slippage_points/H1 là tham số engine đã thực thi |

Các cạnh hỗ trợ phải đưa vào cuộc kiểm toán: `Instrument.from_metadata` (`core/models.py` L41–49) gọi metadata_blockers và lấy specs đã xác nhận; `ConversionRates.at` (`core/engine.py` L59–65) lấy tỷ giá mới nhất không muộn hơn thời điểm sự kiện; engine suy openings/closings từ timestamp_kind + timeframe tại L108–113. Đây là các mối nối DATA/CORE/INDICATORS dù chưa được các phiên đọc cùng nhau.

## 7. Câu hỏi giao cho phiên tổng hợp — chưa phân xử

1. **Nhãn thời gian:** đối chiếu INDICATORS #1 với CORE F6, metadata timestamp_kind, engine openings/closings và sessions `[start,end)`. Phân biệt thời gian nhãn nến, thời gian khả dụng và thời gian khớp. Cần ví dụ ranh giới phiên/UTC/DST; chưa xác nhận P0.
2. **Cổng dữ liệu:** nối DATA #1/#2 với kiểm tra engine L94–113 và đường diagnostic trong inspect_indicators. Chứng minh entry point nghiên cứu chặn lỗi/metadata chưa xác nhận; giữ chính sách gap đã ghi, tách off-grid khỏi thiếu nến.
3. **Specs/chi phí/config:** DATA #3/#5 và CORE F8 phải đối chiếu symbols legacy, metadata dataset, Instrument, quantity/contract/tick, commission và chuyển points sang giá. Runner chưa nối nên không gán tác động thực thi cho YAML.
4. **Nhân quả và state:** ghép INDICATORS #4, STRATEGIES P1-01–05, CORE F1/F4 với test_stage4_review; phân biệt prefix-only input với bảo đảm toàn pipeline; xác minh reset và tái dùng strategy.
5. **Fill/accounting:** dùng cả DATA và CORE để xem gap → pending order → rejected/fill → SL/TP → Portfolio, exact-touch, FX và vị thế cuối mẫu; tham chiếu toàn bộ test còn thiếu ở CORE mục D.
6. **Hiệu năng:** các nhận định CORE F1, INDICATORS #2/#3 và STRATEGIES P1-04/P2-07 có giả thuyết/ước lượng khác nhau. Chưa có đo mới cho 1,44M nến; không hợp nhất ước lượng thành benchmark đã chạy. INDICATORS #2 cần xét cả hành vi copy/Copy-on-Write của đúng phiên bản pandas.
7. **Provenance và phần chưa triển khai:** ghép CORE F5, INDICATORS #10, STRATEGIES P1-06. Kiểm snapshot bằng manifest; tách báo cáo test có sẵn khỏi chứng minh runtime của Claude, và tách stub khỏi lỗi trong tính toán đã triển khai.

## 8. Bằng chứng thực thi và giới hạn lần chuẩn bị này

- `07_TEST_RESULTS.md` ghi lần chạy cũ: 296 passed, compile 39 Python file; có lệnh/stdout/JUnit, không có coverage/type/lint và không chạy benchmark/pipeline dữ liệu thật. Bốn Claude không tự xác minh số 296.
- Lần chuẩn bị này thực hiện đọc tĩnh, Git status/HEAD, kiểm kê file, AST tên hàm và đối chiếu SHA256; **không chạy lại pytest, backtest, benchmark hay CLI dữ liệu** vì chỉ thêm tài liệu bàn giao.
- Không cài phụ thuộc hoặc dùng dịch vụ ngoài. Không sửa source/test/config/metadata/dữ liệu, không sửa báo cáo Claude và không cập nhật các gói cũ.
- Kiểm tra cuối cần xác nhận file 09 đầy đủ, liên kết upload tồn tại, hash bốn Claude và 54 source/23 gói vẫn giữ nguyên. Không dùng git diff --check đơn lẻ làm bằng chứng cho file 09 untracked.

## 9. Danh sách file cần tải lên Claude

Tất cả file ở `C:/Users/Admin/Documents/quant_backtest_system/reports/external_audit/`. Nên dùng **cùng một phiên tổng hợp** có đủ các nhóm, hoặc cung cấp nhiều lượt trong cùng phiên nếu giới hạn đính kèm. Không có kiểm chứng về giới hạn token/upload của tài khoản Claude. Các gói dưới chứa mã nguồn; chỉ tải 4 báo cáo + 09 sẽ không đủ để kiểm toán API từ mã.

### 9.1. Hồ sơ điều phối và kết luận độc lập — 10 file

1. `09_FINAL_AUDIT_INPUT.md`
2. `CLAUDE_AUDIT_CORE.md`
3. `CLAUDE_AUDIT_DATA.md`
4. `CLAUDE_AUDIT_INDICATORS.md`
5. `CLAUDE_AUDIT_STRATEGIES.md`
6. `00_PROJECT_OVERVIEW.md`
7. `00A_SOURCE_INVENTORY.md`
8. `00B_PROJECT_RULES.md`
9. `MANIFEST.md`
10. `08_AUDIT_HANDOFF.md`

### 9.2. Mã nguồn đóng gói cho đối chiếu tích hợp — 12 file

11. `01_CORE_AUDIT.md` — gồm BaseStrategy và tài liệu engine.
12. `02_DATA_AUDIT.md` — gồm config/metadata và data CLI.
13. `03_INDICATORS_AUDIT.md` — tài liệu hợp đồng, utils và exports.
14. `03A_INDICATORS_TREND.md`
15. `03B_INDICATORS_MOMENTUM.md`
16. `03C_INDICATORS_VOLATILITY.md`
17. `03D_INDICATORS_STRUCTURE.md`
18. `03E_INDICATORS_PRICE_ACTION.md`
19. `03F_INDICATORS_SESSIONS_VOLUME.md`
20. `03G_INDICATORS_DIAGNOSTICS.md`
21. `04_STRATEGIES_AUDIT.md` — skeleton và benchmark; BaseStrategy nằm trong 01.
22. `06_VALIDATION_AUDIT.md` — causality và metrics stub, không phải walk-forward đã triển khai.

### 9.3. Tests và bằng chứng thực thi — 7 file

23. `05_TESTS_AUDIT.md`
24. `05A_TESTS_MODELS_COSTS_PORTFOLIO.md`
25. `05B_TESTS_ENGINE_REVIEW.md`
26. `05C_TESTS_DATA.md`
27. `05D_TESTS_INDICATORS.md`
28. `05E_TESTS_ENVIRONMENT.md`
29. `07_TEST_RESULTS.md`

Tổng danh sách chính: **29 file Markdown**. Không cần tải trùng các source riêng lẻ nếu đã tải đầy đủ các gói khớp manifest. Có thể kèm `baseline.json`, `package_verification.json`, `pytest.log`, `pytest_results.xml`, `evidence.json`, `final_verification.json` khi cần truy xuất máy đọc/log gốc; các artifact cũ này không phải kết quả chạy mới của lần chuẩn bị file 09. Không cần tải dữ liệu raw/processed, cache, `.venv`, `.git`, bí mật hoặc công cụ build hồ sơ cho mục tiêu audit tích hợp từ source.

Yêu cầu cho Claude phiên tổng hợp: đối chiếu các phát hiện với mã và bằng chứng, giữ ID/mức/trạng thái/ngữ cảnh gốc, ghi rõ khi xác nhận hoặc bác bỏ bằng chứng mới, chỉ ra API liên nhóm và phần chưa xác minh/chưa triển khai. Không suy rộng kết luận riêng của một nhóm thành kết luận toàn hệ thống khi thiếu bằng chứng.