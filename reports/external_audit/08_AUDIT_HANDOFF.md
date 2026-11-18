# Hướng dẫn bàn giao Claude

Commit nền `7af3b774b1721e091e2527a00563912255d44702`. Snapshot thu thập UTC 2026-11-17T09:33:31.742505+00:00; tạo tài liệu UTC 2026-11-17T09:37:17.201604+00:00.
Đánh giá working tree đã đóng gói, không coi commit nền là snapshot sạch.

## Cách tải và đọc

Tải Markdown trực tiếp, bắt đầu bằng 00_PROJECT_OVERVIEW.md, 08_AUDIT_HANDOFF.md và MANIFEST.md.
Sau đó kiểm toán từng nhóm với test liên quan; không cần tải toàn bộ cùng một lượt.
Không có giới hạn upload/token Claude miễn phí cố định được kiểm chứng trong phiên này; kích thước byte không bảo đảm mọi tài khoản nhận cùng số gói.
Gói lớn nhất giữ nguyên các file core được yêu cầu trong 01; các phần khác đã tách theo module/nhóm.
Các đường dẫn repository tương đối trong bảng là định danh; mỗi block source còn ghi đường dẫn tuyệt đối, số dòng, byte và SHA256.
Một source chỉ xuất hiện toàn văn ở một gói chính. File rỗng có block rỗng. Fenced block không thêm số dòng vào nội dung code.
SHA256 tính trên bytes gốc gồm CRLF/BOM nếu có; xem MANIFEST và package_verification.json.

## Thứ tự đối chiếu

1. 01 core + 02 data + 04 strategies + 05A/05B tests + 06 causality.
2. 02 data + 05C data tests; fixture metadata dùng chung với 05A/05B.
3. 03 tổng quan/_utils + từng gói 03A–03F + 05D tests. 03G là diagnostic CLI.
4. 00B quy tắc + 00A API/import inventory + 05 ánh xạ + 07 kết quả thực thi.

## Điểm cần kiểm toán, chưa phải kết luận có lỗi

- Kiểm tra timing signal-close/next-observed-open, nhãn open/close và timestamp intrabar đại diện khoảng nến.
- Đối chiếu fill Bid/Ask giả lập từ một stream, spread/slippage/tick rounding và commission để loại double-charge.
- Đối chiếu SL/TP cùng chạm, thứ tự EXIT pending trước protective exit, gap và event log.
- Kiểm tra FX as-of, tỷ giá intrabar dùng đầu nến, độ cũ tỷ giá chưa giới hạn; PnL realized/unrealized và collateral.
- Kiểm tra strategy state gia tăng khi tái dùng instance, warm-up và signal_history_limit; engine không tự reset state lớp con.
- Kiểm tra rò rỉ từ cột feature đã tính sẵn/nguồn ngoài; prefix input tự nó không bảo đảm toàn pipeline nhân quả.
- sessions yêu cầu timestamp khả dụng, engine có thể dùng nhãn open; người gọi cần chuyển đúng.
- Quy tắc gap bắt buộc chỉ cảnh báo trong cùng ngày UTC; thiếu lịch nghỉ đầy đủ là giới hạn đã chấp nhận, không nâng thành lỗi nghiêm trọng.
- Metadata thật chưa xác nhận đầy đủ; file symbols.json legacy không là nguồn specs được engine tự tin cậy.
- configs/config.yaml có include_swap=true nhưng CostModel từ chối swap khác 0; slippage_points cần chuyển sang đơn vị giá;
  run_backtest.py chưa đọc cấu hình. Không coi risk_per_trade là sizing đã thực thi.
- core/metrics.py, data_manager.py, custom_indicators.py, first_strategy.py còn khung; validation/walk-forward/sensitivity chưa có.
- README còn mô tả giai đoạn cũ; pyproject hiện có pyarrow và môi trường thực tế ghi ở 00/07.
- git working tree bẩn có sẵn; dependency chưa có lock; coverage/type/lint chưa đo.
- 296 test pass là bằng chứng trên fixture hiện có, không chứng minh lợi thế chiến lược hay độ chính xác toàn dữ liệu thật.

## Phạm vi loại trừ và giới hạn

Không có file source trong danh mục bị bỏ sót: toàn bộ 54 file đều được đóng gói.
Loại trừ .git, .venv, cache, egg-info/build/dist, .env/keys, dữ liệu lịch sử CSV/Parquet/JSON,
download/, data/raw/, data/processed/, reports/runs/ và reports/external_audit/ khỏi danh mục source.
Metadata dưới data/metadata được kèm; không kèm rows giá. Không chạy lại pipeline trên dữ liệu thật.
Quét mẫu bí mật phổ biến trước xuất và trên artifact; không đọc .env. Quét mẫu không là chứng nhận DLP toàn diện.
Các script build_audit.py/audit_evidence.py là công cụ tạo bằng chứng mới trong thư mục hồ sơ, không thuộc mã dự án cần kiểm toán.
baseline/evidence/log/XML là bằng chứng phụ, nội dung thực thi cần đọc đã được nhúng trong gói Markdown.
Không có coverage hoặc analyzer cài sẵn nên không có tỷ lệ coverage hay kết luận lint/type.

## Yêu cầu đối với kết quả kiểm toán

Gắn mỗi phát hiện với file, dòng, hành vi và test/bằng chứng. Phân biệt lỗi xác nhận,
rủi ro cần tái hiện, chức năng chưa triển khai và giới hạn đã chấp nhận. Không tự sửa source.
Không suy luận lợi nhuận thực từ fixture. Đề xuất test bổ sung dưới dạng kiến nghị, không đổi expected result.

## Danh sách gói và phạm vi

| Gói | Phạm vi |
|---|---|
| 00A_SOURCE_INVENTORY.md | Toàn bộ file, trạng thái, API/method và import |
| 00B_PROJECT_RULES.md | Toàn văn .clinerules/ |
| 00_PROJECT_OVERVIEW.md | Kiến trúc, môi trường, README, pyproject và entry point |
| 01_CORE_AUDIT.md | Models, costs, execution, portfolio, engine, BaseStrategy và tài liệu engine |
| 02_DATA_AUDIT.md | Loader/validator/manager, data CLI, configs và metadata |
| 03A_INDICATORS_TREND.md | 03A INDICATORS TREND |
| 03B_INDICATORS_MOMENTUM.md | 03B INDICATORS MOMENTUM |
| 03C_INDICATORS_VOLATILITY.md | 03C INDICATORS VOLATILITY |
| 03D_INDICATORS_STRUCTURE.md | 03D INDICATORS STRUCTURE |
| 03E_INDICATORS_PRICE_ACTION.md | 03E INDICATORS PRICE ACTION |
| 03F_INDICATORS_SESSIONS_VOLUME.md | 03F INDICATORS SESSIONS VOLUME |
| 03G_INDICATORS_DIAGNOSTICS.md | 03G INDICATORS DIAGNOSTICS |
| 03_INDICATORS_AUDIT.md | Công thức/tài liệu gốc, danh mục chỉ báo, shared utils và initializer |
| 04_STRATEGIES_AUDIT.md | Strategy skeleton và ví dụ benchmark |
| 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 05A TESTS MODELS COSTS PORTFOLIO |
| 05B_TESTS_ENGINE_REVIEW.md | 05B TESTS ENGINE REVIEW |
| 05C_TESTS_DATA.md | 05C TESTS DATA |
| 05D_TESTS_INDICATORS.md | 05D TESTS INDICATORS |
| 05E_TESTS_ENVIRONMENT.md | 05E TESTS ENVIRONMENT |
| 05_TESTS_AUDIT.md | Ánh xạ module→test và kết quả từng file |
| 06_VALIDATION_AUDIT.md | Causality implementation, metrics placeholder và phần validation chưa có |
| 07_TEST_RESULTS.md | Lệnh, stdout/stderr đầy đủ, JUnit và giới hạn kiểm thử |
| 08_AUDIT_HANDOFF.md | Hướng dẫn, ghép gói, giả định, điểm rủi ro và loại trừ |
| MANIFEST.md | Mỗi source→gói, số dòng/byte/SHA256 và hash gói |

