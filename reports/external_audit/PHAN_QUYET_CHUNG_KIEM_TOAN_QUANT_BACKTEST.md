# PHÁN QUYẾT CHUNG — KIỂM TOÁN `quant_backtest_system`

**Ngày đối chiếu:** 18/11/2026  
**Nguồn:** `OPUS_AUDIT_INTEGRATION.md` (552 dòng) và `CLAUDE_AUDIT_INTEGRATION.md` (805 dòng), cùng các file core/test đã tải lên trong cuộc trò chuyện trước.  
**Phạm vi:** Đánh giá chất lượng bằng chứng, hòa giải phát hiện, xác định mức ưu tiên và điều kiện nghiệm thu. **Không phải** một lần chạy lại toàn bộ repository hiện hành.

## 1. Phán quyết cuối

**Lõi Backtest Engine: PASS WITH LIMITATIONS cho mô phỏng thử nghiệm.**  
**Hệ thống end-to-end phục vụ kết quả nghiên cứu chính thức: NOT READY / CHƯA NGHIỆM THU.**  
**Có thể tiếp tục phát triển sau khi khóa baseline và xử lý các vấn đề ảnh hưởng đúng/sai. Không cần viết lại toàn bộ engine.**

Cả hai báo cáo đều không cho phép kết luận PASS toàn hệ thống. Opus có bằng chứng mạnh hơn vì báo cáo đã chạy các probe, pytest và benchmark; Sonnet chỉ tổng hợp tĩnh và tự ghi rõ chưa chạy mã. Các probe Opus dẫn tới file `C:\Users\...\scratch\...`, **không đính kèm** ở bộ tài liệu này, nên bằng chứng thực thi chỉ được coi là **đã được Opus báo cáo**, chưa được bên thứ ba kiểm chứng độc lập từ file thô.

## 2. Bằng chứng mạnh nhất theo Opus

- Báo cáo chạy **296/296 pytest**; thử chuỗi **20.000 nến giả lập**, **904 giao dịch**, không phát hiện sai bất biến kế toán trong probe.
- Báo cáo thử sửa nến quá khứ và kiểm tra output trước điểm sửa; kiểm tra hash kết quả ở hai tiến trình.
- Lõi khớp lệnh next-bar, mô hình chi phí, gap SL/TP và P/L được mô tả phù hợp trong các trường hợp đã kiểm.
- Chế độ gia tăng: báo cáo đo **1.000.000 nến trong 554 giây, peak RAM 1,31 GB** (môi trường của người kiểm toán; không phải thời gian máy người dùng).
- Đường full-prefix có thiết kế lặp lại tính toán, có rủi ro độ phức tạp gần **O(N²)**; ước lượng **19 giờ/1,44 triệu nến** chỉ là ngoại suy, không phải lần đo thực tế.

**Chú ý phiên bản:** Hai báo cáo có cùng Git HEAD `7af3b774...` nhưng mô tả working tree dirty/untracked. Git HEAD giống nhau **không đảm bảo** các nội dung đang kiểm toán giống nhau. Các file `engine.py`/`base_strategy.py` đã gửi ở các lượt trước cũng không chứa một số API `signal_history_limit` và `generate_signal` được nhắc tới trong báo cáo mới. Phải khóa snapshot trước khi sửa hoặc xác nhận lại.

## 3. Hòa giải 5 mục P0 của Sonnet với 3 mục P0 của Opus

| Sonnet | Opus | Phán quyết độc lập |
|---|---|---|
| `SYS-001` nhãn thời gian open/close: P0 gate | `QBS-08`: P1, đã đo sai lệch hợp đồng nhãn phiên, **chưa chứng minh future leakage** | **P1 kỹ thuật**, nhưng **điều kiện bắt buộc trước khi chạy dữ liệu thật**: xác nhận `timestamp_kind` và test biên phiên |
| `SYS-002` provenance: P0 gate | `QBS-03`: P0 | **P0 cổng nghiên cứu/tái lập**, không phải lỗi P/L; commit, lock, hash dữ liệu & tham số |
| `SYS-003` so sánh giá float: nghi ngờ P0 | `QBS-01`: đã probe lỗi exact-touch; `QBS-20`: BTC tick rounding không tái hiện | **P0 tính đúng đắn** cho trường hợp chạm SL/TP đúng biên; giữ riêng BTC rounding là chưa chứng minh |
| `SYS-004` dung sai kiểm tra causal: nghi ngờ P0 | `QBS-02`: helper PASS với sai lệch 1e-5, input rỗng | **P0 độ tin cậy của cổng kiểm chứng causal**; chưa chứng minh chính indicator thật bị rò rỉ |
| `SYS-005` metadata chưa xác nhận, engine chặn chưa rõ: P0 gate | `QBS-17`: thiếu 15 trường/blocker; engine đã chứng minh chặn | **P1 điều kiện chuẩn bị dữ liệu thật**, không phải bug của engine. Không tự điền metadata |

Vì vậy **3 P0** của Opus là nhóm P0 ưu tiên về cơ chế khớp, kiểm chứng nhân quả và truy xuất kết quả. Ngoài ra **2 cổng bắt buộc trước khi chạy thật** là xác nhận nhãn thời gian/đơn vị và metadata nguồn.

## 4. Kiểm tra độc lập giới hạn cho lỗi float

Đã thử riêng bằng Python số học IEEE-754 (không import repository hiện hành). Ví dụ khi giá Mid biểu diễn thành `1.0000200000000001`, trừ nửa spread `0.00002`, ta nhận `Bid = 1.0000000000000002`. Mức dừng lỗ chuẩn hóa có thể là `1.00000`, nên `Bid <= SL` cho **False** dù hai mức biểu diễn cùng một điểm giá trên lưới tick theo ý định. Trong phép thử riêng 20.000 mức giá M1 giả định tick `1e-5`, có 8.198 trường hợp so sánh Bid tính từ Mid với giá chuẩn hóa lệch về phía không kích hoạt. **Không được hiểu đây là tỷ lệ lỗi của dữ liệu EURUSD thật**; con số 1.752/4.286 trong Opus cũng chỉ là tỷ lệ của probe do Opus thiết kế.

Cần có test hồi quy xây trên dữ liệu của chính engine. Giải pháp có thể so sánh bằng integer ticks **nếu** tick alignment của Bid/Ask, spread và các mức SL/TP được xác nhận; không được làm tròn tùy tiện mức SL/TP off-grid vì có thể vô tình thay đổi ngữ nghĩa khớp. Hãy bảo toàn hướng slippage bất lợi và quy tắc gap.

## 5. Các bất đồng quan trọng khác

1. **`parabolic_sar`/`structure_breaks` O(N²):** Sonnet kế thừa suy luận tĩnh; Opus đo khoảng 2k–64k cho thời gian gần tuyến tính trên pandas 3.1.1. Vì vậy **không kết luận O(N²) như một sự thật đã chứng minh** đối với các hàm này. Nhưng vẫn rất chậm (~9 phút ngoại suy cho mỗi hàm/1,44M nến). Cần benchmark nhiều kích thước và version. Ngược lại đường engine full-prefix có chi phí lặp dữ liệu rõ ràng.
2. **296 tests:** Sonnet không có môi trường và không xác nhận; Opus báo chạy lại thành công. Đây **không phải mâu thuẫn về kết quả** mà là khác cấp độ bằng chứng. Chưa có stdout/probe thô trong hai file đính kèm.
3. **Metadata/NaN loader:** Sonnet chưa biết engine có chặn; Opus báo đã kiểm tra engine từ chối đầu vào không hợp lệ. Không xếp thành lỗi P0 engine, nhưng phải có cổng rõ ở mọi entrypoint nghiên cứu.
4. **Lỗi nhãn phiên:** Opus có lý khi hạ từ P0 look-ahead xuống P1 sai nghĩa nhãn. Nếu metadata thật bị khai báo sai, mức nghiêm trọng của kết quả thực tế lại tăng mạnh.
5. **`check_prefix_invariance`:** Dung sai ngầm và đầu vào rỗng làm bằng chứng causal yếu. Sửa helper là cần thiết **nhưng không đủ** để ngăn leak từ cột đã tính sẵn (`QBS-10`). Phải thêm test end-to-end từ OHLC thô.
6. **Stateful strategy:** Opus tái hiện 2 lần chạy trên cùng instance khác kết quả (`QBS-07`); là P1 hợp lý. `deepcopy` có thể không phù hợp mọi strategy có external resources; reset/lifecycle contract cần thiết kế rõ và test.
7. **Lệnh bị từ chối khi gap vượt SL/TP:** là quy ước đã tài liệu hóa, không tự gọi bug P0. Tuy nhiên cần ghi và đếm rejections, kiểm thử độ nhạy vì bỏ qua các kịch bản giá xấu có thể tạo thiên lệch kết quả.

## 6. Mức ưu tiên thực tế

### Cổng 0 — Khóa bằng chứng, chưa sửa
- Chụp `git status`, commit snapshot nguồn/test/cấu hình đã chọn (không commit raw data, secrets, cache), hash manifest, `pip freeze`, `pytest` stdout.
- Mang file `probes.py`, `probes2.py`, `probe_results.json`, `perf_results*.jsonl` do Opus dẫn ra vào thư mục evidence trong repo; chạy lại phép thử liên quan trên snapshot này.
- **Không sửa cả 35 mục cùng lúc.**

### Cổng 1 — Sửa các vấn đề cốt lõi có regression test
1. `QBS-01 / SYS-003` — lỗi chạm biên SL/TP; test long/short, nguồn Mid/Bid/Ask, spread 2/4/10/16 ticks, mức off-grid, và slippage/tick rounding.
2. `QBS-02 / SYS-004` — `check_prefix_invariance`: exact comparator có kiểm soát, đầu vào rỗng/không hợp lệ phải raise; test mutation and future-feature pipeline.
3. `QBS-03 / SYS-002` — provenance: nguồn dữ liệu, strategy + params, code commit/dirty, version packages, cấu hình, phí, FX, hash result.
4. `QBS-08 + QBS-17` — xác nhận timestamp_kind, price_type, timeframe, instrument specs cho ít nhất EURUSD, với bằng chứng; test biên phiên.
5. `QBS-07` — vòng đời strategy đảm bảo replay theo hợp đồng.

### Cổng 2 — Tích hợp và hiệu năng
- IT end-to-end từ dữ liệu tổng hợp CSV/Parquet → validator → indicators → strategy → engine → trades/equity, có oracle tính tay, gap, long/short, cost, no-look-ahead, cùng replay.
- Tối ưu engine **sau** khi golden master đóng băng; không tự thay tiền đề chỉ báo stateful (EMA/RMA/ADX/SAR/Supertrend) bằng cửa sổ ngắn nếu chưa chứng minh tương đương.
- Ghi rõ `rejected_orders` và `fill_delay`, giảm spam `Order`/event.
- Đo benchmark trên 10k, 100k, 1M nến tổng hợp; không đặt mốc giảm 50% tốc độ/RAM thành tiêu chuẩn tuyệt đối khi chưa biết phần cứng và kịch bản.
- Bổ sung `metrics.py`, runner YAML/CLI và xuất reports với regression test tính tay và hồ sơ từng run; đây là **giai đoạn hoàn thiện tính năng**, không phải lỗi của scope Giai đoạn 4.

### Cổng 3 — Nghiệm thu nghiên cứu
- Ít nhất một dataset thật có metadata đủ và hợp lệ; chạy end-to-end cả lát nhỏ rồi mẫu dài; lưu hash/params/commit/log.
- Bắt buộc quy tắc gap theo yêu cầu người dùng: **chỉ cảnh báo khi hai timestamp liên tiếp thuộc cùng ngày UTC có khoảng cách lớn hơn timeframe**; bỏ qua gap qua ngày, không ép triển khai lịch Forex đầy đủ. Off-grid là vấn đề **canh lưới timestamp riêng biệt**, nên kiểm theo anchor đã xác nhận, không áp cứng phút tròn nếu nguồn định nghĩa khác.
- Phân biệt mô phỏng single instrument/full notional không swap với Forex CFD có leverage/swap; không diễn giải kết quả thử nghiệm thành hiệu suất broker thực tế.

## 7. Tiêu chí nghiệm thu chung

- Toàn bộ regression tests và test hiện tại đều đạt trên snapshot đã khóa; lưu stdout và hash.
- Không còn sai lệch exact-touch; causal checker không PASS giả; pipeline feature leakage có test và biện pháp kiểm soát.
- Cùng cấu hình + dataset + commit + strategy cho kết quả xác định; stateful strategy có chính sách reset rõ.
- Không sai `timestamp_kind`, loại giá và units; phí, account FX, P/L/equity khớp oracle.
- End-to-end tới metrics/reports chạy được, lưu được hồ sơ một run.
- Benchmark đủ dài chấp nhận được trên máy mục tiêu; quyết định chỉ tối ưu hotspot đã đo.
- Mọi kết luận chính thức gắn version, timestamp, metadata, warnings và assumptions.

## 8. Phán quyết theo bốn trục

| Trục | Phán quyết chung | Lý do |
|---|---|---|
| Core correctness | **PASS WITH LIMITATIONS** cho synthetic tests | Opus báo nhiều probe/tính tay pass; lỗi exact-touch ảnh hưởng một lớp trường hợp quan trọng |
| Integration | **FAIL/INCOMPLETE** cho toàn pipeline | metrics, runner, reports chưa có; chưa có E2E trên dữ liệu thật |
| Performance | **PASS WITH LIMITATIONS** cho incremental, **NOT READY** cho default full-prefix | 1M/554 s/1.31 GB theo Opus; 19h là ngoại suy, không phải phép đo |
| Reproducibility | **FAIL** ở mức nghiên cứu chính thức | Không khóa phiên bản/metadata/run artifacts; dù kết quả thực thi có thể tất định |

**KẾT LUẬN NGẮN:** Không bỏ engine; không vội bổ sung martingale/hedging hoặc tối ưu hàng nghìn cấu hình. Đóng đúng các lỗi và cổng nghiên cứu trước; sau đó tiếp tục giai đoạn runner, metrics và nghiên cứu chiến lược.

## 9. Yêu cầu bàn giao tiếp theo cho Cline

**Nhiệm vụ chỉ xác minh, chưa sửa:**

> Đọc `reports/external_audit/OPUS_AUDIT_INTEGRATION.md`, `CLAUDE_AUDIT_INTEGRATION.md` và báo cáo phán quyết chung này. Xác nhận cả ba tài liệu đang xét cùng phiên bản mã nguồn với `git status`, commit, SHA256 từng file liên quan. Sao chép lưu các probe/test thô mà Opus đã chạy và tự chạy lại `pytest`, các probe QBS-01, QBS-02, QBS-07, benchmark nhỏ. Không chỉnh sửa source/test/dataset trong nhiệm vụ này. Báo cáo từng mục VERIFIED / NOT REPRODUCED / VERSION MISMATCH, chỉ ra `source file:line`, expected vs actual, stdout/JSON, các command đã dùng. Lưu tại `reports/external_audit/CLINE_INDEPENDENT_VERIFICATION.md`. Không sửa bất kỳ code nào cho tới khi tôi chấp thuận.
