# TASK 0 — Baseline và xác minh độc lập

Ngày thực thi: **18/11/2026**, bắt đầu khóa snapshot lúc **10:35:59 UTC**. Gốc dự án: `C:\Users\Admin\Documents\quant_backtest_system`.

**Kết luận: đủ bằng chứng kỹ thuật để bắt đầu nhiệm vụ sửa P0 tiếp theo. TASK 0 không sửa lỗi. Hệ thống vẫn chưa đủ điều kiện nghiệm thu nghiên cứu.** QBS-01, QBS-02, QBS-03 và QBS-07 đều được tái hiện trên mã hiện tại; không dùng kết luận Claude thay cho kết quả chạy.

Đã đọc toàn bộ bốn file `.clinerules/`, hai báo cáo tích hợp và phán quyết chung. Các đường dẫn tương đối trong báo cáo này tính từ gốc dự án hoặc từ thư mục báo cáo khi là liên kết Markdown.

## A. Git HEAD, working tree và nhận diện snapshot

- HEAD: **`7af3b774b1721e091e2527a00563912255d44702`**, nhánh **`main`**.
- Không có thay đổi staged. Có **6 file tracked đã sửa**: `README.md`, `core/cost_model.py`, `core/engine.py`, `indicators/__init__.py`, `pyproject.toml`, `strategies/base_strategy.py`.
- Diff tracked: 324 dòng thêm, 7 dòng xóa. Những thay đổi này đã tồn tại trước TASK 0; phần lớn engine/cost/strategy là triển khai chưa commit so với khung tại HEAD.
- Nhiều file sản phẩm và test còn untracked, gồm execution/models/portfolio/causality, data loader/validator, indicators, benchmark, inspection scripts và các test tương ứng. Thư mục kiểm toán cũng untracked. Danh sách **toàn bộ từng đường dẫn**, không rút gọn theo thư mục: [git_status_before.txt](task0_evidence/git_status_before.txt), [git_untracked_files.txt](task0_evidence/git_untracked_files.txt).
- Đã lưu toàn bộ diff tracked và index: [git_diff_before.patch](task0_evidence/git_diff_before.patch), [git_diff_cached_before.patch](task0_evidence/git_diff_cached_before.patch); danh sách tracked: [git_tracked_files.txt](task0_evidence/git_tracked_files.txt).
- Git cảnh báo LF sẽ chuyển CRLF khi Git chạm `indicators/__init__.py`. SHA256 trong lần này tính từ **bytes trên đĩa**, không chuẩn hóa xuống dòng.

**Đối chiếu phiên bản:** HEAD trùng hai báo cáo nhưng riêng điều đó không chứng minh snapshot trùng nhau. Đã đối chiếu SHA256 từng file với manifest ngày `2026-11-17T09:33:31.742505+00:00`: **54/54 MATCH**, không có VERSION MISMATCH trong tập manifest. `core/engine.py` hiện có `signal_history_limit` và gọi `generate_signal`; `BaseStrategy` có cả hai API. Điều này giải quyết nghi ngờ về những bản engine/strategy cũ từng được gửi riêng.

Bằng chứng: [manifest_comparison.json](task0_evidence/manifest_comparison.json). Giới hạn: chứng minh khớp **54 file của gói kiểm toán trước**, không thể chứng minh toàn bộ working tree tại thời điểm Opus chạy vì Opus không lưu một manifest riêng cho thời điểm đó. Các probe gốc và môi trường hiện tại tương thích, kết quả chính tái hiện. Phán quyết chung là tài liệu đối chiếu, không có snapshot thực thi độc lập để hash.

Đã khóa SHA256 **87 file ngoài thư mục kiểm toán**, gồm source/test/config, raw/processed và file kết quả hiện có: [snapshot_before.json](task0_evidence/snapshot_before.json). So sánh cuối nhiệm vụ: [snapshot_after.json](task0_evidence/snapshot_after.json), [scope_verification.json](task0_evidence/scope_verification.json). **Không có file ngoài thư mục kiểm toán thay đổi; HEAD, diff tracked và diff index giữ nguyên.** Không commit, tag, cập nhật dependency hay chỉnh dữ liệu Forex. Chính sách gap theo ngày UTC giữ nguyên.

### Kiểm tra `.gitignore` và bí mật

Đã thực thi `git check-ignore -v --no-index` trên các đường dẫn giả định, không tạo file bí mật. Raw cả thư mục con, processed, reports/runs, `.venv`, `venv`, `.env`, `.env.local`, `*.pem`, `*.key` đều được ignore. `.env.example` được ngoại lệ cho phép theo dõi. Không có raw data hay virtualenv được tracked; `data/raw/.gitkeep` là placeholder hợp lệ.

**Chưa thể kết luận cơ chế ignore bảo vệ mọi secrets/API key.** Các tên `secrets.json`, `credentials.json`, `api_keys.yaml`, `secrets/token.txt` hiện **không được ignore**. `.gitignore` cũng không thể bảo vệ key được ghi trực tiếp vào một file source được phép theo dõi, và không ngăn `git add -f`.

Quét heuristic tracked và untracked không bị ignore, file text tối đa 2 MB, loại thư mục kiểm toán: không có mẫu credential ứng viên. Không in giá trị secret. Đây không phải chứng minh tuyệt đối không tồn tại secret, cũng không phải kiểm tra toàn bộ lịch sử Git. Chi tiết quy tắc và phạm vi: [gitignore_check.json](task0_evidence/gitignore_check.json). Cần bổ sung quy tắc tên file secrets và kiểm tra trước commit ở nhiệm vụ sau; chưa sửa `.gitignore` trong TASK 0.

## B. Pytest thực tế và môi trường

Interpreter: **`.venv\Scripts\python.exe`**, Python **3.15.2**, pandas **3.1.1**, NumPy **2.5.5**, pytest **9.2.0**, PyYAML **6.0.3**, pyarrow **26.0.1**. Các phiên bản chính trùng mô tả Opus. Chi tiết: [environment.json](task0_evidence/environment.json).

Lệnh thực tế, cwd là gốc dự án:

```powershell
& 'C:\Users\Admin\Documents\quant_backtest_system\.venv\Scripts\python.exe' -B -m pytest -vv -p no:cacheprovider --basetemp 'C:\Users\Admin\Documents\quant_backtest_system\reports\external_audit\task0_evidence\pytest_tmp' --junitxml 'C:\Users\Admin\Documents\quant_backtest_system\reports\external_audit\task0_evidence\pytest_results.xml'
```

Kết quả: **296 passed in 4.87s**, exit code **0**; không có failed/skipped trong tổng kết. Thực thi từ `10:36:11.707639 UTC` đến `10:36:17.693325 UTC` (thời gian tiến trình khác thời gian pytest tự báo).

- Stdout đầy đủ: [pytest.stdout.txt](task0_evidence/pytest.stdout.txt).
- Stderr riêng: [pytest.stderr.txt](task0_evidence/pytest.stderr.txt).
- JUnit: [pytest_results.xml](task0_evidence/pytest_results.xml).
- Lệnh, exit code và environment overrides: [pytest.execution.json](task0_evidence/pytest.execution.json).

Đặt `PYTHONDONTWRITEBYTECODE=1`, `-B`, tắt cacheprovider; `TEMP`, `TMP` và `--basetemp` đều nằm trong thư mục kiểm toán. Không sửa test hiện có để đạt kết quả. Bộ test xanh **không phủ đủ các trường hợp lỗi được tái hiện bên dưới**.

## C. SHA256 mã nguồn quan trọng và bằng chứng gốc

Hash dưới đây là bytes hiện tại, đã tính lại và **MATCH manifest**, không chỉ chép giá trị từ báo cáo cũ:

| File | SHA256 |
|---|---|
| `core/execution.py` | `fdd5262964943c0b9e817f3857b088af6b675dc0026f5dd853d10c0bcff1628e` |
| `core/cost_model.py` | `b8e12db3ae11c56f9ca9c0521e8ab24d6bda4595c4f9b24db07149f72a1178fc` |
| `core/causality.py` | `fe7fa61ef157e6ec5df20932e917380a144dba932e42c5f14f03af4c14b82afc` |
| `core/engine.py` | `b2e35f439025d9b932dec9a8a94c00e94b3317df965c282cfe4c6335bc46880b` |
| `core/models.py` | `81c2b36789871376a1e39f68dc0980f1bb676be14c153fa2bee2f3f1b14df79d` |
| `core/portfolio.py` | `7f5c0d55cd3b454fdf1e34101b40cbcf398de0a06d1ef1104c93860cf01c3d24` |
| `core/data_loader.py` | `82973a19cc0fca229accd3517c331d99983cdf076b4d786f4f2a14c28e793d11` |
| `core/data_validator.py` | `99d379352c38a509765d0e0fc7a73b77508bde9e2946cb3f7b467aad749449c4` |
| `core/metrics.py` | `1bda281456baf27201e2cc167010aa01b2feb35b5f107b0ed2be9e80b0412317` |
| `.gitignore` | `be0d2f36340d702fbc07a7480d90153cf4d8c90953753674dec5e1799759b325` |

SHA256 đầy đủ cho **strategy, runner, benchmark, pyproject, toàn bộ tests/indicators/config/rules** có trong [manifest_comparison.json](task0_evidence/manifest_comparison.json) và [snapshot_before.json](task0_evidence/snapshot_before.json).

Probe gốc Opus có tại `C:\Users\Admin\.gemini\antigravity\brain\7022fcc8-43b1-4837-9f65-458cfcebf9d9\scratch`. Đã lưu bản sao byte-for-byte của `probes.py`, `probes2.py`, `probe_results.json`, `perf.py`, hai file kết quả performance vào [opus_original](task0_evidence/opus_original/). Hash nguồn/bản sao: [opus_original_hashes.json](task0_evidence/opus_original_hashes.json). Kết quả cũ được giữ làm tài liệu lịch sử, không coi là kết quả chạy mới.

Sau khi đọc probe, chạy lại đúng các function gốc liên quan QBS-01/02/03/07 bằng cách chọn AST cùng các import/helper cần thiết, không chỉnh thân hàm. Không thực thi các probe ngoài phạm vi có ghi tệp tạm hay benchmark lớn. Bằng chứng lần chạy mới: [opus_selected_rerun.json](task0_evidence/opus_selected_rerun.json), [opus_selected.stdout.txt](task0_evidence/opus_selected.stdout.txt), [opus_selected.execution.json](task0_evidence/opus_selected.execution.json).

## D. Bảng phán quyết trên mã hiện tại

| Mục | Trạng thái | Kết quả thực thi độc lập |
|---|---|---|
| QBS-01 — chạm SL/TP đúng biên tick | **VERIFIED** | Probe gốc: bỏ sót 1.752/4.286 với spread 4 tick. Gọi trực tiếp `protective_exit` tái hiện SL long, TP long, SL short. TP short **NOT REPRODUCED trong dải đã thử**. |
| QBS-02 — prefix checker PASS giả | **VERIFIED** | Sai lệch 1 tick được PASS cho cả Series/DataFrame; input rỗng, 1 dòng, cutoffs rỗng, index đảo/duplicate được PASS. Control lệch lớn bị chặn. |
| QBS-03 — thiếu provenance | **VERIFIED** | Result thiếu hash dữ liệu, strategy/params, code snapshot/Git và library versions; hai dataset/params khác nhau có thể trả result bằng nhau, không phân biệt được nguồn. |
| QBS-07 — tái sử dụng strategy stateful | **VERIFIED** | Probe gốc: fills 1 rồi 0. Strategy hiện hữu `IncrementalMean`: orders 21 rồi 25; equity cuối 10000.19 rồi 10000.23; instance mới tái lập lần đầu. |

Không có mục nào cần gán VERSION MISMATCH trong bốn mục trên vì mã liên quan khớp manifest và hành vi tái hiện. Giới hạn đối chiếu toàn snapshot Opus được ghi riêng tại A.

## E. Điều kiện, expected, actual và vị trí mã

### QBS-01 — so sánh float làm mất exact-touch

Điều kiện: tick `0.00001`, spread `4 * tick`, giá Mid trên lưới nguyên tick, chuyển sang Bid cho thoát long và Ask cho thoát short. Oracle dùng số tick nguyên: extreme thực thi phải bằng mức SL/TP. Open được đặt cách mức để tránh nhánh gap; vì vậy probe độc lập đi qua nhánh intrabar thực sự.

Expected: SL/TP chạm đúng biên phải trả `ExitDecision` tương ứng. Actual: trả `None`, do sai số float ở phép cộng spread rồi so sánh trực tiếp.

| Nhánh | Số bỏ sót / số thử | Ví dụ mức / extreme thực thi |
|---|---:|---|
| Long SL | 1752 / 4286 | `1.00054` / `1.0005400000000002` |
| Long TP | 1 / 4286 | `0.9999800000000001` / `0.99998` |
| Short SL | 1759 / 4286 | `1.0000200000000001` / `1.00002` |
| Short TP | 0 / 4286 | **NOT REPRODUCED** trên dải này; không suy ra nhánh luôn đúng |

Vòng quét: `m in range(100000, 130000, 7)`. Probe gốc cũng thử spread 2, 10, 16 tick: mỗi trường hợp **0/4286** bỏ sót phép so sánh SL long. Không khái quát tỷ lệ 1752/4286 thành tỷ lệ lỗi trên dữ liệu thật.

Nguồn: `core/cost_model.py:28–37` (`side_bar`, offset float); `core/execution.py:18–37`, đặc biệt **31–32** (so sánh intrabar), **27–30** (so sánh gap cần regression sau sửa); `core/engine.py:163–177` là đoạn gọi và xử lý protective exit. Bằng chứng số/fixture: [independent_results.json](task0_evidence/independent_results.json), mục `QBS-01`.

### QBS-02 — dung sai ngầm và phép kiểm không có bằng chứng

Điều kiện sai lệch nhỏ: 10 dòng close `1.08`, builder `d.close + 0.00001 * (len(d) % 2)`. Prefix 1 dòng trả `1.0800100000000001`, full sample tại cùng timestamp trả `1.08`. Output quá khứ thay đổi khi biết độ dài tương lai.

Expected: báo future-dependent feature vì sai khác một tick; input không đủ hai dòng, cutoffs rỗng hoặc index không hợp lệ cần bị từ chối hoặc báo rõ không có phép so sánh hợp lệ. Actual: helper trả **None/PASS**, cho Series và DataFrame, input rỗng, 1 dòng, cutoffs rỗng, index đảo và duplicate.

Control: sai lệch `.001` bị `ValueError` tại prefix 1; cutoff `[0]` bị từ chối; rolling mean nhân quả PASS. Như vậy probe thực sự gọi helper và phân biệt được các hành vi, không chỉ ghi nhận mọi đầu vào đều PASS.

Nguồn: `core/causality.py:21–25` chỉ kiểm loại/index output; **27–30** cho phép vòng kiểm rỗng và không xác thực lịch sử thời gian; **33–36** gọi pandas assert không ép `check_exact=True` hay đặt dung sai rõ. Sai lệch một tick rơi vào dung sai mặc định đối với giá float đang thử. Không kết luận indicator sản phẩm thực sự bị look-ahead từ lỗi helper này. Builder có captured future state còn là giới hạn giả định pure/deterministic, không phải thứ strict float comparison tự giải quyết được.

Bằng chứng: `QBS-02` trong [independent_results.json](task0_evidence/independent_results.json) và probe Opus đã chạy lại.

### QBS-03 — BacktestResult thiếu hồ sơ truy xuất

Điều kiện: chạy engine hợp lệ trên dữ liệu tổng hợp, kiểm tra dataclass fields/assumptions; chạy chiến lược không giao dịch với params A/B và thay high toàn bộ dataset thêm 1, giữ close/OHLC hợp lệ.

Expected: result hoặc run artifact phân biệt được dataset, strategy và params; lưu hash dữ liệu đầu vào và conversion rates khi dùng, phiên bản strategy/code (bao gồm dirty tree), cấu hình và môi trường thực thi. Actual: hai result **bằng nhau** dù high đầu tiên `101.0` so với `102.0` và params `label=A` so với `label=B`. Việc không giao dịch và giữ close khiến output kế toán bằng nhau là hợp lý; thiếu nhận diện nguồn trong result mới là phát hiện ở đây.

Result có 7 trường `orders/fills/trades/states/events/open_position/assumptions`. Assumptions đã có metadata, costs, quantity, capital, account currency, execution, ambiguity, warning/gap và chính sách open position. **Không phải hoàn toàn không lưu giả định.** Các khóa `data_sha256`, `strategy`, `strategy_params`, `library_versions`, `git_commit` đều thiếu trong probe gốc, và không có hồ sơ provenance riêng ở các trường khác khi kiểm source.

Nguồn: `core/engine.py:23–33` và **214–229**; `strategies/base_strategy.py:9–10` có params nhưng result không lưu. `core/data_loader.py:44–50` đã có `sha256_file`, là thành phần nên xem xét tái sử dụng khi sửa. HEAD hiện tại không chứa phần lớn triển khai trên working tree, nên chỉ ghi HEAD vào result sau này sẽ vẫn chưa đủ.

Bằng chứng: mục `QBS-03` của [independent_results.json](task0_evidence/independent_results.json), probe `CORE-F5_provenance_keys` đã chạy lại và trạng thái Git tại A.

### QBS-07 — state sống qua nhiều lần run

Điều kiện độc lập: dùng đúng class hiện có `benchmark_engine.IncrementalMean`, 40 nến tổng hợp tăng dần `100 + i*.01`, chạy hai lần cùng engine/data/cùng strategy object, sau đó chạy instance strategy mới.

Expected: cùng cấu hình/data cho kết quả tái lập, hoặc API phải từ chối rõ strategy đã dùng và quy định fresh instance/reset. Actual: không reset và không từ chối; orders **21 → 25**, fill đầu **00:20 / 100.20 → 00:16 / 100.16**, equity cuối **10000.19 → 10000.23**. Fresh instance cho kết quả **bằng lần đầu**. Probe gốc với một strategy stateful khác cũng tái hiện fills **1 → 0**.

Nguồn: `benchmark_engine.py:24–35` giữ deque trong instance; `strategies/base_strategy.py:5–7,21–27` cho phép state gia tăng nhưng không định nghĩa lifecycle/reset; `core/engine.py:84–119` khởi tạo portfolio mới nhưng không reset strategy; **186–188** gọi trực tiếp instance được truyền vào. Không khẳng định mọi strategy có state đều gây sai; lỗi tái lập phụ thuộc trạng thái còn lại và hợp đồng sử dụng.

Bằng chứng: mục `QBS-07` trong [independent_results.json](task0_evidence/independent_results.json), `CORE-F4_strategy_reuse` trong [opus_selected_rerun.json](task0_evidence/opus_selected_rerun.json).

### Trạng thái thực tế của metrics, runner và reports

| Thành phần | Kiểm tra mã và thực thi | Kết luận |
|---|---|---|
| `core/metrics.py:1` | Chỉ docstring; import module không có public callable | **Chưa triển khai metrics** |
| `run_backtest.py:4–9` | Thực thi exit 0, chỉ in thông báo MVP và cwd; không load config, không gọi engine/metrics/export | **Khung entry point có chạy, runner backtest chưa triển khai** |
| `reports/runs/` | Có 3 bộ quality JSON có file và 1 bộ indicator smoke; một thư mục quality khác không có file. Không thấy bộ artifact backtest trades/equity/metrics/config | **Báo cáo chất lượng dữ liệu/chỉ báo đã có; exporter báo cáo backtest chưa triển khai** |

Không gọi toàn bộ reports là chưa tồn tại. Danh sách file thực tế: `implementation.report_run_files` trong [independent_results.json](task0_evidence/independent_results.json). Stdout runner: [runner.stdout.txt](task0_evidence/runner.stdout.txt), exit/lệnh: [runner.execution.json](task0_evidence/runner.execution.json). Source inspection cho thấy `inspect_data.py` và `inspect_indicators.py` là công cụ tạo các báo cáo diagnostic hiện hữu.

Benchmark nhỏ hiện hữu, dùng fresh strategy mỗi lần, 1 repeat:

| Nến tổng hợp | BatchMean (s) | IncrementalMean (s) | Output bằng nhau |
|---:|---:|---:|---|
| 100 | 0.0548072 | 0.0289586 | Có |
| 1000 | 0.5031335 | 0.2682322 | Có |

Exit 0; bằng chứng [benchmark_small.stdout.txt](task0_evidence/benchmark_small.stdout.txt), [benchmark_small.execution.json](task0_evidence/benchmark_small.execution.json). Chỉ là kiểm tra nhỏ một lần trên máy hiện tại; không xác minh lại số liệu 1M nến hay ngoại suy 1.44M nến của Opus.

### Cách chạy lại và tính minh bạch của probe

Script chỉ nằm trong thư mục kiểm toán: [task0_verification.py](task0_verification.py). Chạy bằng interpreter `.venv`, `-B`, cwd gốc dự án, với các mode `opus`, `independent`, `run-probes`, `runner`, `benchmark`, `final`. Mode `capture` dùng `mkdir(exist_ok=False)` để không đè evidence baseline hiện tại; muốn khóa baseline khác cần thư mục evidence mới.

Mode `run-probes` chạy `independent` và `opus` trong tiến trình con, lưu stdout/stderr/command/exit code riêng. Lần chính thức cuối cả hai **exit 0**. Các file `*.execution.json` ghi đầy đủ lệnh, thời gian và environment overrides.

**Sự cố trong probe kiểm toán:** lần đầu probe độc lập assertion giả định cả bốn nhánh SL/TP phải tái hiện; short TP không tái hiện nên probe exit 1. Đã sửa **chỉ script kiểm toán** để ghi count/status từng nhánh và yêu cầu có trường hợp tái hiện; không đổi fixture/mã sản phẩm để ép lỗi. Stdout đầu đã được tool đọc và hiện trong lịch sử phiên làm việc nhưng bị lần chạy sau ghi đè cùng tên, không có bản raw riêng còn lưu. Stdout lần cuối: [independent.stdout.txt](task0_evidence/independent.stdout.txt). Kết luận dùng JSON và execution log lần cuối, cả hai probe chính thức exit 0.

## F. Các thay đổi cần thực hiện sau TASK 0

1. **P0 QBS-01:** chọn chính sách chuẩn hóa/so sánh giá theo tick có đơn vị rõ; áp dụng nhất quán SL/TP intrabar và gap; bổ sung regression exact-touch, một tick chưa chạm, xuyên biên, long/short, Mid/Bid/Ask, spread và ambiguity. Không tự thêm dung sai lớn làm thay quy tắc khớp.
2. **P0 QBS-02:** so sánh chính xác hoặc dung sai được yêu cầu tường minh; xác thực số dòng/cutoffs/index; không PASS khi chưa có phép kiểm hữu ích. Thêm regression một tick, NaN/type/alignment và invalid input; chạy lại kiểm nhân quả chỉ báo bằng helper đã sửa.
3. **P0 QBS-03:** định nghĩa hồ sơ run provenance; nhận diện dataset/strategy/params, config, conversion rates, môi trường và code snapshot gồm dirty/untracked; kết nối cơ chế hash hiện hữu. Có regression hai nguồn khác nhau và deterministic replay. Chuẩn bị baseline Git/lock dependency trong nhiệm vụ riêng theo phê duyệt, không tự commit/tag ở đây.
4. **QBS-07:** quy định fresh instance/reset lifecycle có kiểm tra rõ, thêm regression tái sử dụng và fresh replay cho strategy gia tăng; không tự deepcopy/reset tùy tiện strategy mà chưa xét hợp đồng.
5. **Git hygiene:** tăng bảo vệ file secrets phổ biến, review tracked/untracked trước commit, không đưa raw/environment/credential vào Git. TASK 0 chưa phát hiện credential qua heuristic nhưng còn lỗ hổng tên file ignore.
6. **Hoàn thiện tính năng:** metrics có định nghĩa và oracle tính tay; runner config/CLI; exporter backtest tạo run ID và lưu provenance/config/trades/equity/metrics/warnings. Đây là scope phát triển riêng.
7. **Nghiệm thu dữ liệu thật:** xác nhận metadata bằng bằng chứng nguồn rồi chạy E2E; giữ nguyên chính sách gap trong ngày UTC. TASK 0 không sửa metadata và không tự suy đoán loại giá/nhãn thời gian.

## G. Điều kiện bắt đầu sửa P0

**ĐỦ ĐIỀU KIỆN VỀ BASELINE VÀ BẰNG CHỨNG**: đã lưu HEAD + toàn bộ diff/untracked list, tính SHA256, xác nhận 54/54 file khớp gói audit, chạy 296 test, lưu probe gốc và chạy lại probe liên quan, độc lập tái hiện bốn phát hiện, có expected/actual và vị trí nguồn. Hash trước/sau xác nhận TASK 0 không sửa file ngoài thư mục kiểm toán.

Baseline này là **hồ sơ hash và bằng chứng local**, không phải commit/tag hay bản backup byte-for-byte toàn bộ dữ liệu. Với file untracked, hash và danh sách không tự khôi phục được nội dung nếu sau này bị mất; gói audit cũ có bản sao 54 source, còn snapshot nguyên trạng toàn dự án không được tạo trong TASK 0. Tính toàn vẹn bằng chứng có thể kiểm tra bằng hash nhưng không có chữ ký hay dấu thời gian bên ngoài.

**Chưa được coi là đã đóng P0 hoặc nghiệm thu nghiên cứu.** Short TP chưa tái hiện trên lưới đã thử; chưa đo tác động trên dữ liệu Forex thật; chưa kiểm toàn bộ lịch sử secrets hay hiệu năng dài. Việc sửa bắt đầu ở nhiệm vụ tiếp theo theo phạm vi người dùng giao. TASK 0 kết thúc tại báo cáo và bằng chứng này.