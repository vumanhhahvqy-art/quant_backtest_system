# Thư viện chỉ báo — Giai đoạn 3

Các hàm độc lập nằm trong cùng thư mục tài liệu này. Không có strategy/engine.
Ví dụ: `from indicators.moving_averages import sma`, `sma(data.close, 20)`.

## Quy ước chung

- Đầu vào là Series số hoặc DataFrame có `open, high, low, close` viết thường.
- Giữ nguyên index, số dòng và thứ tự; không sửa dữ liệu nguồn. Index phải
  duy nhất, tăng dần, không NaT. Nếu dùng DatetimeIndex, phải UTC có timezone.
- Dữ liệu giá phải hữu hạn hoặc NaN, OHLC phải hợp lệ. Không tự điền NaN.
- Giá trị nến chỉ khả dụng sau khi nến đóng. Với hàm phiên, index phải là
  **thời điểm khả dụng/đóng nến**. Dữ liệu ghi thời gian mở phải được chuyển
  bằng độ dài nến đã xác nhận trước khi gọi hàm phiên.
- Rolling cần đủ mẫu liên tiếp; NaN trong cửa sổ khiến kết quả NaN. EMA/RMA
  khởi tạo lại sau NaN. Các hàm chỉ so sánh hai mốc (ROC/MOM) cần hai mốc đó
  hợp lệ, không đòi hỏi các giá trị trung gian.
- Mẫu boolean dùng `pd.NA` khi chưa đủ dữ liệu; mức giá không tồn tại dùng NaN.
  Chia cho 0 trả NaN. Không thay thống kê không xác định bằng 0.
- Các hàm stateful có quy ước riêng ghi dưới đây; không suy ra dữ liệu thiếu
  thành nến mới. Cần chạy lớp data validator trước khi nghiên cứu dữ liệu thật.
- `n` dưới đây là `window`; warm-up ghi bằng **số mẫu tối thiểu để có giá trị
  đầu tiên**, không phải số dòng NaN. Có thể cần lâu hơn nếu mẫu không xác định.

## Moving averages (`moving_averages.py`)

| Hàm | Tham số | Phương pháp / khởi tạo | Warm-up |
|---|---|---|---|
| `sma` | `window` bắt buộc | Trung bình cộng | n |
| `ema` | `window`, `adjust=False` | alpha=2/(n+1), seed mẫu đầu; `adjust=True` chuẩn hóa trọng số hữu hạn | n |
| `wma` | `window` | Trọng số 1..n, mẫu mới nhất n | n |
| `rma`, alias `smma` | `window` | Seed SMA(n), sau đó y += (x-y)/n | n |

EMA khác với biến thể seed SMA của một số thư viện; không kỳ vọng trùng số
đầu chuỗi với biến thể đó. RMA dùng seed SMA của Wilder, không dùng seed EMA.

## Xu hướng (`trend.py`)

| Hàm | Tham số mặc định | Phương pháp | Warm-up |
|---|---|---|---|
| `adx` | n=14 | +DM/-DM chọn chuyển động trội dương; DI=100*RMA(DM)/RMA(TR); ADX=RMA(DX) | DI n+1; ADX 2n |
| `supertrend` | n=10, multiplier=3 | (H+L)/2 +/- multiplier*ATR, band trailing; seed bullish; NaN reset state | n |
| `aroon` | n=25 | Vị trí extreme trên n+1 mẫu / n *100; tie chọn mới nhất | n+1 |
| `parabolic_sar` | step=.02, maximum=.2 | Wilder SAR; hướng từ hai close đầu, clamp hai nến trước; reversal dùng extreme cũ | 3 |
| `ichimoku` | conversion=9, base=26, span=52, displacement=26 | Midpoint cực trị; span A=(conversion+base)/2; B=midpoint(span) | Theo từng cửa sổ; cloud thêm displacement |
| `vortex` | n=14 | Tổng abs(H-L trước), abs(L-H trước) / tổng TR | n+1 |
| `choppiness` | n=14, n>=2 | 100*log10(sum TR / (max H-min L))/log10(n) | n |
| `vhf` | n=28 | Range close(n) / tổng abs(change)(n) | n+1 |
| `linear_regression_slope` | n=20, n>=2 | OLS x=0..n-1, đơn vị giá/nến | n |
| `linear_regression_channel` | n=20, deviations=2 | Endpoint OLS +/- deviations*population residual std | n |

SAR reset sau NaN và khởi tạo lại với hai nến hợp lệ; SuperTrend seed lại tại
ATR hợp lệ kế tiếp. Ichimoku không xuất Chikou dịch ngược (gây rò rỉ tương lai).
`lagging_close` là close quá khứ dịch dương; raw spans khả dụng hiện tại,
`cloud_a/b` là raw spans dịch dương để so sánh cloud tại thời điểm hiện tại.
ADX không xác định khi không có chuyển động ở cả hai phía.

## Động lượng (`momentum.py`)

| Hàm | Tham số mặc định | Phương pháp | Warm-up |
|---|---|---|---|
| `rsi` | n=14 | 100-100/(1+RMA(gain)/RMA(loss)); seed SMA thay đổi | n+1 |
| `macd` | fast=12, slow=26, signal=9 | EMA fast-slow, EMA signal, histogram | slow; signal slow+signal-1 |
| `stochastic` | n=14, smooth=3 | Fast K=100*(C-min L)/(max H-min L); D=SMA K | n; D n+smooth-1 |
| `stochastic_rsi` | rsi_window=14, stoch_window=14, smooth=3 | Stochastic của RSI, K=SMA raw; D=SMA K | K rsi_window+stoch_window+smooth-1; D thêm smooth-1 |
| `roc` | n=12 | 100*(C / C.shift(n) - 1) | n+1 |
| `momentum` | n=10 | C-C trước n | n+1 |
| `cci` | n=20 | (typical-SMA typical)/(0.015*mean absolute deviation cùng cửa sổ) | n |
| `williams_r` | n=14 | -100*(max H-C)/(max H-min L) | n |
| `ppo` | fast=12, slow=26, signal=9 | 100*(EMA fast-EMA slow)/EMA slow | như MACD |
| `tsi` | long=25, short=13 | 100*double EMA(change)/double EMA(abs(change)) | long+short |
| `awesome_oscillator` | fast=5, slow=34 | SMA fast-SMA slow của (H+L)/2 | slow |

RSI không loss và có gain ->100; không gain và có loss ->0; cả hai bằng 0 ->NaN.
MACD/PPO/AO yêu cầu fast<slow. EMA lồng nhau giữ nguyên các warm-up NaN.

## Biến động (`volatility.py`)

| Hàm | Tham số mặc định | Phương pháp | Warm-up |
|---|---|---|---|
| `atr` | n=14 | RMA(TR), TR=max(H-L,abs(H-C trước),abs(L-C trước)); đầu đoạn dùng H-L | n |
| `natr` | n=14 | 100*ATR/C | n |
| `rolling_std` | n=20, ddof=0 | Population std; có thể chọn ddof | n |
| `bollinger_bands` | n=20, deviations=2, ddof=0 | SMA +/- deviations*std | n |
| `bollinger_bandwidth` | n=20, deviations=2 | 100*(upper-lower)/middle | n |
| `bollinger_percent_b` | n=20, deviations=2 | (C-lower)/(upper-lower), đơn vị phần | n |
| `keltner_channels` | n=20, atr_window=10, multiplier=2 | EMA close +/- multiplier*ATR | max(n,atr_window) |
| `donchian_channels` | n=20, lag=0 | max H, min L, midpoint; lag=1 cho mức trước nến hiện tại | n+lag |
| `historical_volatility` | n=20, ddof=1, periods_per_year bắt buộc | std(log returns)*sqrt(annualization) | n+1 |
| `realized_volatility` | n=20, periods_per_year bắt buộc | sqrt(mean(log returns²)*annualization), không trừ mean | n+1 |
| `parkinson_volatility` | n=20, periods_per_year bắt buộc | sqrt(mean(log(H/L)²)/(4 log2)*annualization) | n |
| `garman_klass_volatility` | n=20, periods_per_year bắt buộc | sqrt(mean(.5 log(H/L)²-(2log2-1)log(C/O)²)*annualization) | n |

Volatility annualized trả tỷ lệ phần (0.2=20%), không tự suy luận tần suất Forex.
Các estimator log yêu cầu giá dương; Parkinson/GK không tính gap qua đêm.
ATR không cộng dữ liệu qua giá close thiếu; nến đầu đoạn hợp lệ dùng H-L.

## Cấu trúc (`market_structure.py`)

| Hàm | Tham số mặc định | Định nghĩa / khả dụng |
|---|---|---|
| `confirmed_swings` | left=2, right=2 | Extreme nghiêm ngặt, loại tie; phát giá pivot ở bar xác nhận sau right nến; cần left+right+1 |
| `swing_structure` | left=2,right=2 | HH/LH/HL/LL so hai pivot cùng loại đã xác nhận; chưa có pivot trước ->NA |
| `structure_breaks` | left=2,right=2,displacement_ratio=.6 | Close vượt mức chưa bị phá; hướng đầu/same trend=BOS; opposite=CHoCH; CHoCH có body/range>=threshold=MSS |
| `support_resistance_zones` | left=2,right=2,tolerance=.001 | Pivot xác nhận gần nhất +/- tolerance tương đối; chưa có pivot ->NaN |
| `previous_period_levels` | period='day',timezone='UTC' | H/L/C kỳ đã quan sát trước, week bắt đầu thứ Hai; kỳ đầu NaN |
| `daily_pivots` | method='traditional',timezone='UTC' | Pivot từ H/L/C ngày trước; method traditional/fibonacci/camarilla/cpr |
| `fibonacci_retracement` | left=2,right=2,ratios=(0,.236,.382,.5,.618,.786,1) | Hai pivot xác nhận gần nhất; high mới H-r*(H-L), low mới L+r*(H-L); cần cả hai |
| `equal_high_low` | left=2,right=2,tolerance=.001 | Hai pivot cùng loại cách nhau <= abs(pivot trước)*tolerance |
| `liquidity_sweep` | left=2,right=2 | Wick vượt mức pivot trước, close trở lại phía trong nghiêm ngặt |
| `fair_value_gap` | không | Low hiện tại>High hai bar trước hoặc High hiện tại<Low hai bar trước; công bố bar thứ ba |

Structure dùng mức được xác nhận trước bar hiện tại; mỗi mức bị phá một lần.
Mức pivot được giữ qua NaN (không phát event tại bar thiếu); NaN trong cửa sổ
swing không tạo pivot. Mức không tự hết hạn. Zone là vùng một pivot, không
clustering hồi cứu. Nếu một bar xác nhận cả high và low, Fibonacci ưu tiên
low; đây là quy ước xác định, không khẳng định thứ tự intrabar.

Pivot: P=(H+L+C)/3. Traditional R1=2P-L, S1=2P-H, R2/S2=P±(H-L),
R3=H+2(P-L), S3=L-2(H-P). Fibonacci P±(.382,.618,1)*(H-L).
Camarilla C±1.1*(H-L)/(12,6,4,2). CPR có hai biên (H+L)/2 và
2P-(H+L)/2, được sắp xếp bottom<=top.

Previous day/week là **kỳ quan sát trước**, không tự thêm ngày nghỉ. Coverage
phải được xác nhận đầy đủ ở lớp dữ liệu; ngày đầu bị cắt vẫn có thể tạo mức
không đầy đủ cho ngày sau. Session timezone/ngày broker cần khai báo đúng.

## Nến (`price_action.py`)

| Hàm | Tham số | Định nghĩa / warm-up |
|---|---|---|
| `candle_features` | không | body=abs(C-O), range=H-L, wick trên/dưới, wick/range và body/range; 1 bar |
| `inside_bar`, `outside_bar` | không | H/L nằm trong hoặc bao ngoài bar trước, strict; 2 bars |
| `engulfing` | không | Hai màu đối nhau, body phủ body trước inclusive; loại doji; 2 bars |
| `pin_bar` | wick_ratio=.6,max_opposite_ratio=.2 | Wick dài/range>=threshold, wick đối/range<=threshold; 1 bar |
| `doji` | max_body_ratio=.1 | body/range<=threshold; range=0 ->NA; 1 bar |
| `hammer_shooting_star` | wick_to_body=2,max_opposite_ratio=.1 | Wick dài>=factor*body, wick đối nhỏ; body>0; không lọc trend; 1 bar |
| `morning_evening_star` | small_body_ratio=.3,penetration=.5 | Body giữa<=ratio*body đầu, màu đầu/cuối ngược nhau, close cuối xuyên body đầu; không bắt buộc gap; 3 bars |
| `marubozu` | min_body_ratio=.9 | body/range>=threshold và có hướng; 1 bar |
| `heikin_ashi` | không | C=OHLC/4; seed O=(O+C)/2, sau đó O=(HA O trước+HA C trước)/2; H/L gồm HA O/C; 1 bar |
| `narrow_range` | n=4 (chọn 7 cho NR7) | range=min range(n), tie được tính; n bars |
| `consecutive_candles` | không | Run tăng dương, giảm âm; doji=0; NaN reset; 1 bar |
| `range_expansion` | n=20,multiplier=1.5 | range hiện tại>multiplier*mean range của n bar trước; n+1 bars |

HA khởi tạo lại sau NaN. Mẫu nến là đặc trưng hình học, không chứng minh xác
suất đảo chiều. Các nhóm output bullish/bearish dùng cùng một hàm canonical.

## Regime, phiên và chu kỳ (`sessions.py`)

| Hàm | Tham số / quy ước |
|---|---|
| `trend_range_regime` | n=14,trend_threshold=25; ADX>=threshold ->1, ngược lại 0; warm-up ADX |
| `volatility_regime` | n=14,reference_window=100,quantile=.5; NATR>quantile của reference_window NATR **trước** ->1; cần n+reference_window bars |
| `session_features` | timezone,start,end bắt buộc; active, session_date, minutes_since_open; phiên qua đêm thuộc ngày mở |
| `session_range` | timezone,start,end bắt buộc; high/low/range tích lũy, ngoài phiên NaN |
| `asia_session_range` | Tokyo 09:00–18:00, start/end tùy chọn; cũng cung cấp Asian session high/low |
| `london_session_range` | Europe/London 08:00–17:00, start/end tùy chọn |
| `new_york_session_range` | America/New_York 08:00–17:00, start/end tùy chọn |
| `opening_range_breakout` | timezone,start,end bắt buộc,minutes=30; freeze range trước mốc minutes, sau đó close trên/dưới ->+1/-1, trong range ->0 |
| `london_new_york_overlap` | london_start/end='08:00'/'17:00',ny_start/end tương tự; giao active theo hai timezone |
| `session_vwap` | timezone,start,end,volume_kind bắt buộc; typical=(H+L+C)/3; sum(typical*volume)/sum(volume) |
| `calendar_features` | timezone='UTC'; day_of_week Monday=0, hour_of_day=0..23 |
| `weekend_gap` | timezone='UTC'; open-close trước khi Fri->Sun/Mon sau 2..3 ngày, khác=0, bar đầu=NaN |
| `dominant_cycle` | n=64,min_period=6,max_period=32; OLS detrend trailing window, peak DFT trong khoảng chu kỳ, phase Hilbert endpoint; n bars |

Giờ phiên là giả định nghiên cứu có thể chỉnh, không là lịch broker. Interval
[open,close); thời gian ngoài phiên không dùng. DST theo IANA; mở phiên mơ hồ
hoặc không tồn tại gây lỗi. Hàm không lọc holiday/weekend bằng lịch ngầm.
Session range xử lý NaN như cummax/cummin (bar thiếu NaN, sau đó tiếp tục).
ORB chỉ dùng những bar đã quan sát trong opening range; phải xác nhận đủ
coverage và mốc đóng nến trước khi dùng. Phá vỡ là trạng thái mỗi bar, không
tự khử lặp thành lệnh.

VWAP yêu cầu volume_kind='traded' hoặc 'tick'. Tick volume chỉ là proxy;
không thay volume thiếu bằng 1. Tổng volume=0 ->NaN, volume âm lỗi, NaN
poison kết quả còn lại của phiên. Feature thời gian không có warm-up.

Chu kỳ dùng Hilbert DFT **từng cửa sổ quá khứ**, không Hilbert toàn dataset;
không phải Ehlers HT_DCPERIOD. Chuỗi phẳng/detrended gần 0 ->NaN. DFT có
độ phân giải n/k và ảnh hưởng biên; không dùng để dự báo như kết quả chắc chắn.

## Đối chiếu và kiểm thử

Các test trong `tests/test_indicators.py` dùng phép tính số học độc lập, mẫu
OHLC tổng hợp, kiểm tra cả index, không mutate, tái lập, empty/NaN và prefix
invariance. Prefix invariance so kết quả trước một mốc với kết quả khi chỉ
cung cấp dữ liệu tới mốc đó, cho mọi hàm public trong danh sách kiểm thử.

Đã đối chiếu phương pháp RSI/Wilder và Ichimoku với StockCharts ChartSchool,
EMA với tài liệu pandas và test reference trực tiếp pandas EWM. Không cài
thư viện TA ngoài dự án, không tuyên bố tất cả chỉ báo khớp TA-Lib.

- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi
- https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/ichimoku-cloud
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html

Các định nghĩa cấu trúc, pattern, regime và giờ phiên là heuristic công khai
ở đây. Chưa có lịch giao dịch hoàn chỉnh hoặc đảm bảo coverage từng phiên;
đó là trách nhiệm của pipeline dữ liệu trước khi chạy nghiên cứu.