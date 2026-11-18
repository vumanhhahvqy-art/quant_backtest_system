# Backtest engine — Giai đoạn 4

Đây là mô phỏng lịch sử giả định. API hiện trả kết quả trong bộ nhớ, chưa tích hợp
chạy cấu hình qua `run_backtest.py` hoặc xuất báo cáo nghiên cứu.

## Phạm vi và giao diện

- Một công cụ, một vị thế tối đa. Không cộng dồn, đảo chiều tự động hoặc đóng một phần.
- Lệnh `market` BUY/SELL/EXIT. Lệnh limit, stop-entry và trailing stop chưa hỗ trợ.
  `Order` từ chối loại lệnh ngoài phạm vi này.
- `BaseStrategy.generate_signals` nhận bản sao dữ liệu từ đầu mẫu đến hết nến vừa
  đóng, trả DataFrame cùng index, có `signal` bằng `1/-1/0`, tùy chọn `exit` kiểu
  boolean và `sl/tp` là mức giá tuyệt đối. Warm-up phát `0`. `0` tiếp tục giữ vị thế.
- `exit=True` là yêu cầu đóng toàn bộ vị thế. Không gửi EXIT đồng thời BUY/SELL.
- BUY/SELL khi đã có vị thế và EXIT khi không có vị thế bị từ chối, có event.
- Chiến lược phải thuần theo dữ liệu đầu vào, không tự tải dữ liệu tương lai. Các cột
  đặc trưng do người gọi cung cấp cũng phải được kiểm tra tính nhân quả. Engine
  giới hạn prefix nhưng không thể kiểm soát mã chiến lược tự truy cập nguồn ngoài.

### Cập nhật tín hiệu và kiểm tra nhân quả

Engine gọi `generate_signal(completed_data)` mỗi nến. Mặc định phương thức này
gọi `generate_signals` và giữ kiểm tra index/cột như trước, nên chiến lược cũ
không cần thay đổi. Chiến lược muốn cập nhật gia tăng có thể override
`generate_signal`, trả một Series gồm `signal` và các trường tùy chọn.

`signal_history_limit=None` vẫn truyền toàn prefix. Chiến lược gia tăng có thể
chủ động đặt một số nguyên dương (ví dụ 1) để chỉ sao chép các nến gần nhất;
chiến lược chịu trách nhiệm quản lý state, warm-up và khởi tạo lại cho mỗi run.
Không tự cắt lịch sử của chiến lược cũ và không tính tín hiệu trước trên toàn mẫu.

`core.causality.check_prefix_invariance(builder, raw_data)` tính lại đặc trưng
trên các prefix rồi so với phần tương ứng của kết quả toàn mẫu. Test phát hiện
`shift(-1)`, rolling đặt giữa và chuẩn hóa theo cực đại toàn mẫu. Đây là kiểm tra
trên mẫu cung cấp, không chứng minh tính nhân quả cho mọi dữ liệu. Phải truyền
hàm tính lại từ OHLC gốc; cắt cột đặc trưng đã tính sẵn không phát hiện được rò rỉ.

## Chu trình thời gian

1. Tại đầu nến: xử lý lệnh gửi sau nến trước, tại giá mở phía thực thi.
2. Kiểm tra SL/TP cho vị thế đang giữ, kể cả vị thế mới mở tại đầu nến này.
3. Tại cuối nến: đánh dấu P/L chưa thực hiện bằng giá đóng phía thanh lý.
4. Gọi chiến lược trên prefix đã đóng và tạo lệnh cho đầu nến kế tiếp có dữ liệu.

Timestamp nội bộ UTC; hỗ trợ nhãn nến `open` và `close`, timeframe cố định.
Thời gian đặt lệnh sau đóng nến có thể bằng thời gian mở nến kế tiếp.
Không dùng giá đóng nến tín hiệu để khớp. Không tạo nến bù. Nến chồng lấn,
sai OHLC, NaN/Infinity, timestamp trùng/không tăng và các lỗi dữ liệu bắt buộc
khác vẫn bị từ chối. Có hai chế độ kiểm tra khoảng trống:

- Mặc định `expected_timestamps=None`: không cần lịch Forex bên ngoài. Chỉ so
  hai timestamp liên tiếp thuộc **cùng ngày UTC**. Khoảng cách lớn hơn timeframe
  được ghi vào `interval_analysis.intraday_gaps`, gồm đầu/cuối khoảng quan sát,
  độ dài giây và `candidate_missing_slots`. Đây chỉ là cảnh báo, không chặn chạy.
  Mỗi cặp khác ngày UTC bị bỏ qua, kể cả cuối tuần, ngày lễ và qua nửa đêm;
  không cố xác định nguyên nhân nghỉ. Không kiểm tra thiếu nến trước/sau mẫu.
- Truyền `expected_timestamps`: đối chiếu toàn bộ với lịch độc lập đã xác nhận,
  bao gồm đầu/cuối mẫu; nến thiếu hoặc ngoài lịch là lỗi chặn như trước.

Số nến có khả năng thiếu là số điểm trên lưới `timestamp_trước + k*timeframe`
nằm hoàn toàn giữa hai đầu mút. Ví dụ timeframe H1: 10:00→14:00 có 3 điểm;
10:00→12:30 có 2 điểm và thêm cảnh báo khoảng không chia hết timeframe.
Đây là ứng viên thiếu, không khẳng định dữ liệu thực sự đã mất.

`intraday_gap_check_passed=True` nghĩa là timestamp hợp lệ, có thứ tự và không
phát hiện khoảng bất thường trong ngày theo quy ước này. Không đồng nghĩa dữ
liệu hoàn chỉnh. `full_calendar_verified` luôn False khi không truyền lịch;
chỉ True khi lịch cung cấp khớp dữ liệu và timestamp hợp lệ. Không dùng chính
`data.index` làm bằng chứng lịch hoàn chỉnh. `ready_for_research` chỉ yêu cầu
các kiểm tra bắt buộc và metadata đạt; cảnh báo vẫn lưu trong báo cáo/kết quả.

`validate_expected_timestamps` kiểm tra UTC, thứ tự, duy nhất, không rỗng và
không chồng lấn. Lịch dùng cùng quy ước nhãn `open/close` như dữ liệu, không dịch
timestamp thêm một lần. Cần dựng lịch độc lập từ nguồn/lịch phiên và ranh giới
khoảng nghiên cứu đã xác nhận, rồi đối chiếu toàn bộ, kể cả nến đầu và cuối.
Không tự suy ra lịch Forex/broker từ khoảng cách nến; dãy timestamp đơn thuần
không chứng minh được nguồn lịch. Lịch tổng hợp trong test định nghĩa trước
các thời điểm phải có và được giữ nguyên khi cố ý xóa nến.

Lệnh cuối mẫu ghi `unfilled/end_of_data`. Vị thế còn mở được giữ và định giá,
không ép đóng tại cuối mẫu. Không có giả định về thanh khoản, khối lượng khớp,
độ trễ hoặc khớp một phần: lệnh thị trường hợp lệ khớp toàn bộ tại nến kế tiếp.

Lệnh luôn chờ **nến thực tế tiếp theo**, dù cách nhiều giờ/ngày: BUY sau đóng
nến thứ Sáu có thể khớp tại giá mở nến đầu Chủ nhật/thứ Hai nếu đó là dòng dữ
liệu tiếp theo. Cảnh báo thiếu nến trong ngày cũng không tạo nến hay giá giả;
gap giá, SL/TP, chi phí và kế toán tiếp tục áp dụng trên dữ liệu thực tế.

## Giá, SL/TP và chi phí

- Metadata phải được xác nhận theo schema dữ liệu hiện có. Không suy đoán từ
  `symbols.json` cũ. Hỗ trợ một dòng OHLC đã xác định `Mid`, `Bid` hoặc `Ask`.
- Spread cố định `s` theo đơn vị giá. Từ Mid suy ra Bid=Mid-s/2, Ask=Mid+s/2;
  từ Bid suy ra Ask=Bid+s; từ Ask suy ra Bid=Ask-s.
- BUY dùng Ask, SELL dùng Bid; long thoát dùng Bid, short thoát dùng Ask.
  SL/TP kiểm tra trên OHLC phía thoát, không trên giá Mid.
- Hai SL/TP cùng chạm: SL trước, `ambiguous=True`. Nếu giá mở đã qua một mức,
  xử lý sự kiện đầu nến trước khi xét high/low của nến.
- Gap qua SL: dùng giá mở. Gap qua TP: dùng giá mục tiêu, không hưởng cải thiện
  giá qua gap. TP là trigger cho thoát thị trường bảo thủ, không phải limit đảm
  bảo giá. Slippage bất lợi và làm tròn tick có thể làm giá thoát xấu hơn TP.
- `Fill.timing=intrabar` chỉ xác định khoảng nến; `timestamp` là đầu khoảng đó,
  không phải khẳng định thời điểm chạm chính xác. Không suy diễn đường giá nội nến.
- Slippage cố định theo đơn vị giá, cộng cho BUY, trừ cho SELL, làm tròn theo
  tick về phía bất lợi. Commission tính theo mỗi phía, mỗi đơn vị quantity đã
  khai báo, bằng đồng tiền tài khoản. Mức commission phải được cấu hình rõ.
- Spread/slippage nằm trong giá khớp. Các trường cost trong Fill chỉ phục vụ
  kiểm tra, không trừ tiền lần hai. `spread_cost` là nửa spread tham chiếu Mid.
- Chưa hỗ trợ OHLC Bid/Ask đồng thời, spread biến thiên, commission theo phần
  trăm/notional, swap hoặc rollover. Swap khác 0 bị từ chối. Chạy qua đêm với
  swap=0 là giả định không tính chi phí tài trợ, không đại diện chi phí thực tế.
- SL/TP không còn bao quanh giá khớp sau gap/slippage: từ chối lệnh và ghi lý do.

## Quy cách và tài khoản

`Instrument` lấy tick, pip, contract size, quantity unit, bước khối lượng và quote
currency từ metadata đã xác nhận. `lots`: units=quantity*contract_size;
`units`: contract_size phải bằng 1. Khối lượng phải đúng bước tăng.

Đây là sổ tài khoản ký quỹ giả lập dự trữ 100% notional lúc vào, không đòn bẩy.
Không phải sổ mua/bán tài sản spot. Entry không trừ notional khỏi balance;
notional được ghi là `reserved_capital`, cố định đến khi đóng.

- P/L trước commission = direction*(exit-entry)*units*FX tại thời điểm thoát.
  Con số này đã bao gồm ảnh hưởng spread/slippage trong giá khớp.
- Commission trừ ngay mỗi lần khớp; net P/L trừ cả hai commission.
- Balance = vốn đầu + P/L đã chốt - commission đã trả (kể cả phí vị thế mở).
- Unrealized P/L dùng giá đóng phía thanh lý và FX tại cuối nến, chưa tính
  commission/slippage thoát giả định. Equity=balance+unrealized P/L.
- Free capital=equity-reserved capital; realized P/L của state=balance-vốn đầu.
- Thiếu vốn cho notional+phí mở: từ chối mà không thu phí.
- Không có margin call/stop-out. Short hoặc gap lớn có thể tạo equity/balance âm;
  engine ghi event `insolvent` và cảnh báo log, không tự xóa lỗ hoặc bù tiền.

FX là số đơn vị account currency cho một đơn vị quote currency. Cùng đồng tiền
dùng 1. Khác đồng tiền bắt buộc truyền Series tỷ giá dương, hữu hạn, index UTC
tăng và duy nhất. Index là thời điểm tỷ giá **đã được công bố và có thể sử dụng**.
Lấy giá mới nhất không muộn hơn sự kiện, không nội suy hoặc lấy dữ liệu tương lai.
Thoát intrabar dùng tỷ giá đã biết tại đầu nến do không biết thời điểm chạm.
Chưa giới hạn tuổi tỷ giá; người gọi chịu trách nhiệm về độ mới và nguồn tỷ giá.

## Ví dụ API

```python
from core.cost_model import CostModel
from core.engine import BacktestEngine

# metadata, data and strategy are supplied by the caller.
engine = BacktestEngine(
    metadata,
    CostModel(spread=0.0002, slippage=0.00001, commission_per_quantity=3.5),
    initial_capital=10000,
    account_currency="USD",
    quantity=0.01,
)
result = engine.run(data, strategy)  # Simple intraday gap checks, no calendar.
# Optional strict calendar check with an independently verified schedule:
# result = engine.run(data, strategy, expected_timestamps=confirmed_schedule)
```

Giá trị ví dụ là giả định minh họa, không phải thông số broker. Quantity phải phù
hợp metadata. `BacktestResult` lưu orders, fills, trades, states, events, vị thế
còn mở và snapshot giả định; không ghi dữ liệu hoặc ghi đè báo cáo.

## Kiểm chứng tính tay

Fixture có contract_size=10, quantity=1 lot, giá Mid mở nến vào=102 và nến
thoát=110. Spread=2, slippage=0.1 và commission=3 mỗi phía:

- BUY=102+1+0.1=103.1; EXIT=110-1-0.1=108.9.
- P/L trước commission=(108.9-103.1)*10=58; net=58-3-3=52.
- Vốn 10000 thành balance/equity 10052 sau đóng.

Bộ test còn kiểm tra long/short, gap, SL/TP cùng chạm, Bid/Ask, tỷ giá,
không khớp cuối mẫu, thiếu vốn, thời điểm khớp và tính tái lập.

`Fill` từ chối giá/quantity không dương, chi phí âm/không hữu hạn, hướng sai,
timestamp thiếu UTC và timing không hỗ trợ. Portfolio kiểm tra ID/thời gian
lệnh vào, hướng/quantity và thời gian thoát không trước lần vào.

Lưu Parquet ghi vào file tạm cùng thư mục, flush/fsync, rồi công bố bằng hard
link không ghi đè. Lỗi ghi hoặc công bố dọn file tạm và không để lại file đích
dở dang. Filesystem phải hỗ trợ hard link; nếu không, thao tác báo lỗi thay vì
hạ xuống ghi trực tiếp không an toàn. Không bảo đảm dọn file tạm nếu tiến trình
bị kill hoặc mất điện giữa lúc ghi.

### Benchmark tổng hợp sau rà soát

Chạy `benchmark_engine.py --sizes 2000 10000 --repeats 3`, đo toàn run với cùng
tín hiệu so close với SMA20. So sánh kết quả đầy đủ của hai cách cập nhật trước
khi báo tốc độ. Python 3.15.2, pandas 3.1.1, NumPy 2.5.5, Windows 10:

| Số nến | Toàn prefix, trung vị (s) | Gia tăng, trung vị (s) | Tỷ lệ |
|---|---:|---:|---:|
| 2.000 | 0,9761 | 0,5048 | 1,93 lần |
| 10.000 | 5,4972 | 2,5152 | 2,19 lần |

Đây là số đo dữ liệu tổng hợp, không phải backtest lịch sử dài hạn hoặc bảo đảm
tốc độ của chiến lược khác. Hai đường dùng chung engine sau rà soát; đường
toàn prefix giữ cách tính tín hiệu trước đây, không phải benchmark binary cũ.
API không tự tối ưu chiến lược cũ; muốn hưởng lợi cần triển khai state gia tăng.

Chạy bằng PowerShell tại thư mục dự án:

```powershell
& 'c:/Users/Admin/Documents/quant_backtest_system/.venv/Scripts/python.exe' -m pytest -q
```