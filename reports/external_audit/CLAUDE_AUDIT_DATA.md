# BÁO CÁO KIỂM TOÁN ĐỘC LẬP: LỚP DỮ LIỆU CỦA QUANT BACKTEST SYSTEM

**Phương pháp và giới hạn.**
- Toàn bộ kết luận dưới đây đến từ đọc tĩnh mã nguồn. **Tôi chưa chạy code, chưa chạy pytest và chưa thấy dữ liệu thật.** Con số "296 passed" là bằng chứng do hồ sơ cung cấp, không phải do tôi xác minh.
- Phần "kết quả hiện tại" của từng phát hiện là **dự đoán từ mã**, không phải kết quả thực thi.
- Văn bản đính kèm không có số dòng, nên tôi chỉ nêu file, hàm và trích đoạn.
- Tôi chỉ nhận được `00_PROJECT_OVERVIEW.md` (README, pyproject, run_backtest, .gitignore) và `02_DATA_AUDIT.md`. Phần mã đọc được gồm `data_loader.py`, `data_validator.py`, `inspect_data.py`, các file cấu hình và metadata. Đó là khoảng 13 trên 54 file.
- Chưa có `engine.py`, `execution.py`, `cost_model.py`, `portfolio.py`, `models.py`, `causality.py`, `indicators/*`, `tests/*`, `00A`, `00B`, `07`, nên **phạm vi kiểm toán chỉ là lớp nạp và kiểm tra dữ liệu**.

---

## A. Kết luận tổng quan

- Lớp dữ liệu được thiết kế thận trọng: metadata phải được xác nhận kèm bằng chứng, không sắp xếp, xóa hay điền dữ liệu, và có cơ chế phát hiện lỗi.
- Tôi **không xác nhận được lỗi P0 nào** trong phạm vi này. Các rủi ro P0 trong đề bài (look-ahead, khớp lệnh, P/L, equity) nằm ở các file chưa được cung cấp.
- Có 3 vấn đề P1, chủ yếu là các "cổng chặn" còn lỏng, và 5 vấn đề P2.
- Dữ liệu hiện bị chặn nghiên cứu bởi metadata chưa xác nhận (price_type, timestamp_kind, timeframe, tick_size...). Đó là hành vi đúng.

---

## B. Các vấn đề quan trọng nhất

| # | Mức | Trạng thái | Vấn đề |
|---|---|---|---|
| 1 | P1 | CONFIRMED (hành vi), mức nghiêm trọng tùy chính sách của bạn | Timestamp lệch lưới (off-grid) chỉ là cảnh báo, không chặn `ready_for_research` |
| 2 | P1 | SUSPECTED (phụ thuộc nơi gọi) | `load_csv(diagnostic=False)` trả về NaN/NaT mà không raise |
| 3 | P1 | CONFIRMED (mâu thuẫn dữ liệu); tác động SUSPECTED | Hai nguồn sự thật mâu thuẫn cho XAUUSD; confirmations từng trường không được đọc |
| 4 | P2 | CONFIRMED | `write_json` không atomic, có thể để lại file JSON cụt |
| 5 | P2 | CONFIRMED | `config.yaml` lệch phạm vi và quy ước (swap, timeframe, ngày) |
| 6 | P2 | SUSPECTED | Epoch phân số và float64 làm mất độ chính xác với `unix_ns` |
| 7 | P2 | SUSPECTED (chưa đo) | Parse trùng lặp và sao chép toàn bộ chuỗi ở 1,44 triệu dòng; danh sách gap không giới hạn |
| 8 | P2 | CONFIRMED | `save_parquet`: chốt chặn `"raw" in path.parts` yếu, `os.link` không di động |

---

## C. Bảng bằng chứng

### #1 — `core/data_validator.py::validate_data` (CONFIRMED)

- **Trích đoạn:**
  ```python
  irregular = np.flatnonzero(positive_pairs & (delta % interval != pd.Timedelta(0)))
  ...
  warnings.append("Some timestamp intervals are not multiples ...")
  report["ready_for_research"] = not bool(errors or blockers)
  ```

- **Lý do:** `irregular` chỉ sinh cảnh báo. Nó cũng chỉ xét cặp liên tiếp cùng ngày, nên không bắt được trường hợp **toàn bộ** timestamp lệch cùng một offset (ví dụ luôn có giây = 30). Nến M1 lệch lưới thường là dấu hiệu sai `timestamp_kind`, sai đơn vị hoặc dữ liệu hỏng, chứ không phải "gap" theo chính sách bạn đã chấp nhận.

- **Đầu vào tối thiểu:** 3 nến lúc 00:00:00, 00:01:30, 00:03:00 với timeframe `1min` và metadata đã xác nhận đầy đủ.

- **Kết quả mong đợi:** `errors` khác rỗng, `ready_for_research=False`.

- **Hiện tại (dự đoán):** `errors` rỗng, `ready_for_research=True`, chỉ có warnings.

- **Regression test:**
  ```python
  def test_off_grid_timestamps_block_research(confirmed_metadata):  # timeframe "1min"
      idx = pd.DatetimeIndex(["2024-01-02 00:00:00", "2024-01-02 00:01:30",
                              "2024-01-02 00:03:00"], tz="UTC")
      df = pd.DataFrame({"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.1}, index=idx)
      assert validate_data(df, confirmed_metadata)["ready_for_research"] is False
  ```

- **Sửa tối thiểu:** Thêm kiểm tra tuyệt đối `(index - index.floor(timeframe)) != 0` ghi vào `errors["off_grid_timestamps"]`, kiểm tra toàn bộ dòng, không phụ thuộc vào cặp liên tiếp. Không đụng đến chính sách gap cùng ngày.

---

### #2 — `core/data_loader.py::load_csv` (SUSPECTED)

- **Trích đoạn:** Nhánh không diagnostic chỉ kiểm tra `encoding_info.get("confirmed") is not True`. Token lỗi vẫn thành NaN/NaT (`errors="coerce"`) và hàm trả về `LoadResult`.

- **Lý do:** Tham số `diagnostic=False` gợi ý chế độ nghiên cứu, nhưng hàm vẫn trả dữ liệu lỗi. Hàm cũng không gọi `metadata_blockers`. Mọi bảo vệ nằm ở `validate_data`. Nếu `engine.py` hoặc code gọi nó không bắt buộc `ready_for_research`, dữ liệu lỗi có thể vào mô phỏng. Tôi **chưa thấy** `engine.py` nên chưa kết luận được.

- **Đầu vào tối thiểu:** CSV một dòng có `close="abc"`, metadata `unix_ms` đã xác nhận, `diagnostic=False`.

- **Kết quả mong đợi:** `ValueError`.

- **Hiện tại (dự đoán):** Trả `LoadResult` với `close=NaN`.

- **Regression test:**
  ```python
  def test_research_mode_rejects_bad_tokens(tmp_path, confirmed_metadata):
      p = tmp_path / "x.csv"
      p.write_text("timestamp,open,high,low,close\n1704153600000,1.1,1.2,1.0,abc\n")
      with pytest.raises(ValueError):
          load_csv(p, confirmed_metadata, diagnostic=False)
  ```

- **Sửa tối thiểu:** Ở chế độ không diagnostic, raise nếu `invalid_timestamps.count` hoặc bất kỳ `numeric_parsing[*].count` lớn hơn 0.

---

### #3 — `data/metadata/symbols.json` vs `datasets.json`, `metadata_blockers` (CONFIRMED mâu thuẫn)

- **Bằng chứng:** XAUUSD trong `symbols.json` có `point_value: 1e-05`, `pip_value: 0.0001`, `contract_size: 100000`. `datasets.json` (đã được người dùng xác nhận) ghi `point_size: 0.001`, `pip_size: 0.01`. Chênh nhau 100 lần về point. `instrument_specification_confirmations` không được đọc ở bất kỳ hàm nào trong phần đã cung cấp. `point_size` không nằm trong `SPECIFICATION_FIELDS`. `config.yaml` có `slippage_points: 2` với `default_symbol: XAUUSD`, nên giá trị trượt giá phụ thuộc hoàn toàn vào point_size nào được dùng.

- **Lý do:** Nếu bất kỳ code nào đọc `symbols.json`, trượt giá và P/L của XAUUSD sai theo bậc 100 đến 1000. Tổng quan nói `Instrument.from_metadata` không đọc file này, nhưng không có test nào cấm điều đó.

- **Regression test:**
  ```python
  def test_legacy_symbols_do_not_conflict_with_registry():
      legacy = json.load(open("data/metadata/symbols.json"))
      reg = json.load(open("data/metadata/datasets.json"))
      for d in reg["datasets"]:
          spec = d["metadata_overrides"]["instrument_specifications"]["value"]
          assert legacy[d["symbol_hint"]]["point_value"] == spec["point_size"]
  ```

- **Hiện tại (dự đoán):** EURUSD đạt, XAUUSD thất bại.

- **Sửa tối thiểu:** Xóa hoặc đánh dấu `symbols.json` là legacy kèm test trên. Thêm `point_size` vào `SPECIFICATION_FIELDS`. Quyết định rõ vai trò của `instrument_specification_confirmations` (dùng hoặc bỏ).

---

### #4 — `core/data_loader.py::write_json` (CONFIRMED)

- **Trích đoạn:**
  ```python
  with path.open("x", encoding="utf-8") as stream:
      json.dump(payload, stream, indent=2, ensure_ascii=False, allow_nan=False)
  ```

- **Lý do:** File được tạo trước, rồi `json.dump` raise giữa chừng khi gặp NaN. File cụt vẫn nằm lại và không thể ghi đè, trong khi `save_parquet` thì atomic. Ví dụ có thể xảy ra: `largest_interval_seconds` là NaN khi mọi timestamp là NaT.

- **Regression test:**
  ```python
  def test_write_json_failure_leaves_no_file(tmp_path):
      p = tmp_path / "r.json"
      with pytest.raises(ValueError):
          write_json(p, {"a": 1, "b": float("nan")})
      assert not p.exists()
  ```

- **Hiện tại (dự đoán):** File tồn tại, nội dung cụt.

- **Sửa tối thiểu:** Dump ra chuỗi trước (`json.dumps`), rồi ghi bằng cùng cơ chế temp + `os.link` như `save_parquet`.

---

### #5 — `configs/config.yaml` (CONFIRMED, tĩnh)

- `include_swap: true` trái với phạm vi đã chấp nhận (không có swap).
- `timeframe: "H1"` dùng ký hiệu khác với `pd.Timedelta(...)` mà validator yêu cầu. `pd.Timedelta("H1")` nhiều khả năng raise `ValueError`.
- Khoảng ngày kết thúc `2026-01-01`, trong khi dữ liệu đến `2026-11-15`.
- `slippage_points` không nêu đơn vị.
- `run_backtest.py` chưa đọc file này, nên hiện chưa có tác động thực thi.

- **Sửa tối thiểu:** Đặt `include_swap: false`, dùng định dạng `1h` hoặc `60min` cho timeframe, cập nhật ngày kết thúc, thêm chú thích đơn vị cho `slippage_points`.

---

### #6 — `load_csv`, nhánh `unix_*` (SUSPECTED)

- `pd.to_numeric(token, errors="coerce")` trả float64 khi có token lỗi. Với `unix_ns` (khoảng 1,7×10¹⁸, vượt 2⁵³) độ chính xác dưới ~256 ns có thể mất. Epoch phân số như `"1704153600000.5"` được chấp nhận âm thầm.
- Tác động thấp vì dữ liệu hiện tại là M1 `unix_ms`, nhưng nên có test.
- **Sửa:** Parse chuỗi sang int64 qua đường nguyên (`astype("Int64")` sau khi từ chối token có dấu `.`/`e`).

---

### #7 — Hiệu năng và bộ nhớ (SUSPECTED, chưa đo)

- `source_inferred_dtypes` gọi lại `pd.to_numeric` cho từng cột giá, nên mỗi cột giá được parse hai lần. `raw.copy()` nhân đôi toàn bộ chuỗi trước khi chuyển số.
- Báo cáo nhúng toàn bộ `intraday_gaps` không giới hạn, trái với mô tả "bounded diagnostics".
- Validator về cơ bản là vector hóa, độ phức tạp O(n); với 1,44 triệu dòng không thấy vòng lặp Python trên toàn bộ dòng — mức rủi ro thấp.
- **Đề xuất:** Tính dtype từ kết quả đã parse, giới hạn danh sách gap (giữ số đếm), và đo trước/sau bằng so sánh `assert_frame_equal` cùng JSON báo cáo.

---

### #8 — `core/data_loader.py::save_parquet` (CONFIRMED)

- Chốt chặn `"raw" in path.parts` từ chối thư mục tên `raw` bất kỳ, nhưng không bảo vệ chính `data/raw` đã cấu hình theo đường dẫn tuyệt đối.
- `os.link` sẽ lỗi `OSError` trên hệ tệp không hỗ trợ hard link (FAT/exFAT, một số ổ mạng).
- **Sửa:** So sánh với đường dẫn raw đã resolve, và xử lý `OSError` với thông báo rõ hơn, có thể fallback sang `os.replace` kèm cảnh báo.

---

> **Ghi chú — hạn chế thiết kế đã chấp nhận (không tính là bug):** Gap cắt qua ngày UTC không bị cảnh báo (chỉ đếm `cross_day_interval_count_ignored`); không kiểm tra lịch đầy đủ ở chế độ mặc định.

---

## D. Test còn thiếu

- Off-grid timestamp với metadata đã xác nhận đầy đủ.
- Epoch phân số (`unix_ms` với token `"1704153600000.5"`).
- `unix_ns` có token lỗi vượt 2⁵³.
- Dòng trống trong CSV (`skip_blank_lines=False` có thể tạo dòng NaN, chưa kiểm chứng).
- DST mơ hồ hoặc không tồn tại trong chế độ `local`.
- Dataset toàn NaT: kiểm tra việc ghi báo cáo JSON không để lại file cụt.
- Override metadata gõ sai khóa.
- Khứ hồi Parquet: `validate_data` trước và sau Parquet cho báo cáo giống hệt, kể cả độ phân giải thời gian pandas 3.x.
- Số dòng sai khác giữa CSV và Parquet.
- Hợp đồng với `expected_timestamps` khi `timeframe` là `None`.

---

## E. Điểm thiết kế nên giữ

- **Metadata fail-closed:** Mỗi trường cần `value`, `confirmed` (đúng kiểu `bool`) và `evidence`.
- **Không sort, drop, fill hay nội suy:** Token lỗi thành NaN/NaT kèm số dòng và token gốc.
- **`aware` bắt buộc `%z`; `local` bắt buộc timezone khai báo**, DST mơ hồ hoặc không tồn tại thành NaT và được báo cáo.
- **Băm SHA256 file raw** trước và sau, so sánh `raw_unchanged`.
- **Xuất Parquet không ghi đè, không nằm trong `raw`**, xác nhận khứ hồi bằng `assert_frame_equal`.
- **Phân tách `structural_checks_passed` với `ready_for_research`.**
- Đếm trùng timestamp cho mọi dòng tham gia; chỉ so sánh OHLC trên dòng hữu hạn.
- `expected_timestamps` là chế độ lịch độc lập, có kiểm tra nến chồng lấn.
- Báo cáo ghi **git revision, trạng thái dirty, phiên bản phần mềm và hash mã.**

---

## F. Chưa thể kết luận

- Mọi mục P0 của đề bài (look-ahead, khớp lệnh, Bid/Ask, P/L, equity, tỷ giá, SL/TP, gap, vị thế mở cuối dữ liệu) vì thiếu `engine.py`, `execution.py`, `cost_model.py`, `portfolio.py`, `models.py`.
- Nhân quả của chỉ báo (prefix và toàn phần) vì thiếu `indicators/*`, `causality.py`, `test_indicators.py`.
- Hiệu năng engine trên 1,44 triệu nến vì thiếu engine và `benchmark_engine.py`.
- **Cần kiểm tra khi có engine:** Tổng quan nói lệnh khớp "ở nến có dữ liệu kế tiếp". Nếu có gap cùng ngày, tín hiệu cuối nến có thể khớp ở open sau gap, cách rất xa thời điểm kế tiếp. Cần xem engine có từ chối hoặc gắn cờ khi `next_ts - signal_ts > timeframe` không, và `ready_for_research` có được kiểm tra trước khi chạy không.
- Dữ liệu thật: số lượng nến, `price_type` Bid (nên Ask phải được mô hình hóa bằng spread), và chất lượng dữ liệu đều chưa kiểm chứng.
- Kết quả "296 passed" chưa được đối chiếu với nội dung test; tôi chưa thấy file test nào.

---

## G. Kế hoạch sửa theo thứ tự ưu tiên

1. **Gửi các file còn thiếu** để hoàn tất P0: trước hết `engine.py`, `execution.py`, `cost_model.py`, `portfolio.py`, `models.py`, sau đó `causality.py` và các file test.
2. **Sửa #2:** Chặn dữ liệu lỗi ở chế độ không diagnostic, và đảm bảo engine bắt buộc `ready_for_research`.
3. **Sửa #1:** Đưa off-grid timestamp thành lỗi (ghi vào `errors`, không phải `warnings`).
4. **Giải quyết #3:** Loại bỏ nguồn sự thật XAUUSD mâu thuẫn, thêm test nhất quán, quyết định vai trò `instrument_specification_confirmations`.
5. **Sửa #4** (`write_json` atomic) và **#8** (`save_parquet` chốt chặn), rồi **#5** (`config.yaml`).
6. **#6 và #7** sau khi đo thực tế; mọi tối ưu phải đi kèm đối chiếu đầu ra trước và sau bằng `assert_frame_equal`.

---

## H. Kết luận

> **PASS WITH LIMITATIONS — chỉ cho lớp nạp và kiểm tra dữ liệu và metadata.**

Không có lỗi P0 được xác nhận trong phạm vi này, nhưng có 3 mục P1 cần xử lý. **Chưa thể ra phán quyết** cho Backtest Engine, chỉ báo hay toàn hệ thống vì chưa nhận được mã nguồn tương ứng.

---

*Kiểm toán tĩnh, không thực thi. Mọi "kết quả hiện tại" là dự đoán từ đọc mã.*
*Phạm vi: `data_loader.py`, `data_validator.py`, `inspect_data.py`, `configs/*`, `data/metadata/*` — 13/54 file.*
