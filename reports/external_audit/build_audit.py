"""Build verbatim, hash-verified Markdown audit packages from local files."""

import ast
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
E = json.loads((OUT / 'evidence.json').read_text(encoding='utf-8'))
FILES = {i['path']: i for i in E['source_files']}
PACKAGES = {}
ASSIGN = {}
BLOCKS = []
SECRET_PATTERNS = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                   r'\bAKIA[0-9A-Z]{16}\b', r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}',
                   r'\bgh[pousr]_[A-Za-z0-9]{30,}',
                   r'(?im)^\s*(?:api_key|password|secret_key|access_token)\s*[:=]\s*[\"\x27][^\"\x27\n]{8,}[\"\x27]']


def safe(text, name):
    if any(re.search(pattern, text) for pattern in SECRET_PATTERNS):
        raise ValueError('Potential secret detected; packaging stopped: ' + name)


def put(name, text):
    safe(text, name)
    PACKAGES[name] = text


def block(path, package):
    if path in ASSIGN:
        raise ValueError('Duplicate source: ' + path)
    raw = (ROOT / path).read_bytes()
    item = FILES[path]
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    text = raw.decode('utf-8')
    safe(text, path)
    fence = '`' * max(3, max((len(m.group())+1 for m in re.finditer(r'`+', text)), default=3))
    lang = {'.py': 'python', '.md': 'markdown', '.toml': 'toml', '.yaml': 'yaml', '.json': 'json'}.get(Path(path).suffix, 'text')
    prefix = (f'\n## File gốc: `{path}`\n\n'
              f'Đường dẫn tuyệt đối: `{ROOT / path}`\n\n'
              f'Số dòng: {item["lines"]}; kích thước: {item["bytes"]} bytes; SHA256: `{item["sha256"]}`.\n\n'
              f'<!-- SOURCE_BEGIN {path} -->\n{fence}{lang}\n')
    suffix = ('' if text.endswith('\n') or not text else '\n') + fence + f'\n<!-- SOURCE_END {path} -->\n'
    ASSIGN[path] = package
    BLOCKS.append(dict(path=path, package=package, prefix=prefix, suffix=suffix,
                       content_bytes=len(raw), sha256=item['sha256']))
    return prefix + text + suffix


def package(name, intro, paths):
    put(name, intro + ''.join(block(p, name) for p in paths))


def table(headers, rows):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', '<br>').replace('\r', '')
    return '\n' + '| ' + ' | '.join(headers) + ' |\n|' + '|'.join('---' for _ in headers) + '|\n' + ''.join('| ' + ' | '.join(cell(v) for v in row) + ' |\n' for row in rows) + '\n'


def module_name(path):
    return path.removesuffix('.py').replace('/', '.').removesuffix('.__init__')


MODULES = {module_name(p): p for p in FILES if p.endswith('.py')}
EDGES = defaultdict(set)
for path, item in FILES.items():
    for imp in item.get('imports', []):
        if imp['module'] is not None or imp['level']:
            base = imp['module'] or ''
            if imp['level']:
                parts = module_name(path).split('.')[:-1]
                base = '.'.join(parts[:len(parts)-imp['level']+1] + ([base] if base else []))
            candidates = [base] + [base + '.' + n for n in imp['names']]
        else:
            candidates = imp['names']
        for name in candidates:
            if name in MODULES:
                EDGES[path].add(MODULES[name])
            elif name.startswith('test_') and 'tests/' + name + '.py' in FILES:
                EDGES[path].add('tests/' + name + '.py')


def reachable(path):
    seen = set()
    pending = list(EDGES[path])
    while pending:
        current = pending.pop()
        if current not in seen:
            seen.add(current)
            pending.extend(EDGES[current])
    return seen


def main():
    commit = E['git_head']['stdout'].strip()
    stamp = E['created_utc']
    suites = ET.parse(OUT / 'pytest_results.xml').getroot().findall('.//testsuite')
    totals = {k: sum(int(s.get(k, 0)) for s in suites) for k in ('tests', 'failures', 'errors', 'skipped')}
    passed = totals['tests'] - totals['failures'] - totals['errors'] - totals['skipped']
    status = E['git_status_before']['stdout']
    overview = f'''# Tổng quan hồ sơ kiểm toán Quant Backtest System

Thời điểm thu thập UTC: {stamp}. Commit nền: `{commit}`.
Snapshot là toàn bộ file hiện tại trong working tree, gồm thay đổi chưa commit và file untracked, không phải bản xuất riêng commit.
Phạm vi khảo sát: {len(FILES)} file văn bản liên quan, trong đó {sum(p.endswith('.py') for p in FILES)} file Python.
Mục tiêu dự án: nghiên cứu, mô phỏng và đánh giá Forex lịch sử; kết quả mô phỏng là giả định.

## Kiến trúc quan sát từ mã

```mermaid
flowchart TD
  Inspect[inspect_data.py] --> Loader[core.data_loader]
  Inspect --> Validator[core.data_validator]
  Validator --> Loader
  Models[core.models] --> Loader
  Engine[core.engine] --> Models
  Engine --> Validator
  Engine --> Costs[core.cost_model]
  Engine --> Execution[core.execution]
  Engine --> Portfolio[core.portfolio]
  Engine --> Strategy[strategies.base_strategy]
  Costs --> Models
  Execution --> Models
  Portfolio --> Models
  Sessions[indicators.sessions] --> Trend[indicators.trend]
  Sessions --> Volatility[indicators.volatility]
  Trend --> Volatility
  Volatility --> MA[indicators.moving_averages]
  MA --> Utils[indicators._utils]
```

Đồ thị trên thể hiện các cạnh chính. Danh sách import đầy đủ và API từng module nằm ở `00A_SOURCE_INVENTORY.md`.
Engine triển khai mô phỏng một công cụ, tối đa một vị thế, market BUY/SELL/EXIT ở nến có dữ liệu kế tiếp;
SL/TP trên phía giá thực thi, SL trước khi cả hai cùng chạm, gap stop dùng open và gap TP dùng target.
Chi phí tập trung trong CostModel; spread/slippage nằm trong giá fill, commission thu mỗi phía.
Portfolio dùng tài sản bảo đảm toàn notional, không leverage, quy đổi quote/account bằng tỷ giá đã công bố.
State cuối nến đánh dấu vị thế còn mở; không cưỡng bức đóng cuối mẫu.

## Trạng thái thực tế

- Có implementation loader/validator, indicators, engine/execution/costs/portfolio/models và kiểm tra nhân quả theo prefix.
- `core/data_manager.py`, `core/metrics.py`, `indicators/custom_indicators.py`, `strategies/first_strategy.py` chỉ có docstring/import.
- `core/__init__.py`, `strategies/__init__.py` rỗng; đây là file khởi tạo package, không tự coi là lỗi.
- `BaseStrategy.generate_signals` cố ý raise NotImplementedError để lớp con định nghĩa.
- `run_backtest.py` chỉ in thông báo; chưa nối cấu hình, simulation và xuất research report.
- Không tồn tại `validation/`, walk-forward, sensitivity hay chiến lược nghiên cứu hoàn chỉnh trong `strategies/`.
- README còn mô tả giai đoạn đầu; phiên bản và kết quả test hiện tại lấy từ lần chạy mới bên dưới.

## Quy tắc gap được chấp nhận cho cuộc kiểm toán này

Chỉ yêu cầu cảnh báo khoảng thiếu nến giữa hai timestamp liên tiếp cùng ngày UTC.
Khoảng qua ngày UTC, cuối tuần và lễ được bỏ qua trong chế độ mặc định. Không yêu cầu lịch Forex đầy đủ;
không xếp thiếu lịch đó là lỗi nghiêm trọng. Timestamp trùng, sai thứ tự, NaN/Infinity, giá không hợp lệ và OHLC sai vẫn phải bị phát hiện.
`expected_timestamps` là chế độ lịch độc lập tùy chọn, chặt hơn yêu cầu mặc định.
Quy tắc này là chỉ thị cụ thể của người yêu cầu, ưu tiên khi đọc các quy tắc tổng quát gốc ở `00B_PROJECT_RULES.md`.

## Môi trường và kiểm chứng

Python: `{E['python']}`. Interpreter: `{E['executable']}`.
Pytest: {passed} passed, {totals['failures']} failed, {totals['errors']} errors, {totals['skipped']} skipped.
39 file Python biên dịch trong bộ nhớ thành công. Coverage và các static analyzer phổ biến không có sẵn.
Chi tiết, lệnh thực tế, stdout/stderr nguyên vẹn: `07_TEST_RESULTS.md`.
Không chạy các CLI xử lý dữ liệu thật hoặc benchmark dài. Báo cáo cũ trong reports/runs không được dùng làm bằng chứng thực thi mới.

## Thư viện hiện có
'''
    overview += table(['Distribution', 'Version'], E['packages'])
    overview += '\n## Trạng thái Git trước kiểm tra\n\n```text\n' + status + '```\n'
    package('00_PROJECT_OVERVIEW.md', overview + '\n## Tài liệu và entry point gốc\n',
            ['README.md', 'pyproject.toml', 'run_backtest.py', '.gitignore', '.vscode/settings.json'])
    package('00B_PROJECT_RULES.md', '# Toàn bộ quy tắc dự án gốc\n\nĐọc cùng chính sách gap trong 00_PROJECT_OVERVIEW.md.\n',
            [p for p in FILES if p.startswith('.clinerules/')])
    core = ['core/models.py', 'core/execution.py', 'core/cost_model.py', 'core/portfolio.py',
            'core/engine.py', 'strategies/base_strategy.py', 'core/BACKTEST_ENGINE.md', 'core/__init__.py']
    package('01_CORE_AUDIT.md', '# Core và hợp đồng chiến lược\n\nĐọc cùng 02_DATA_AUDIT.md, 05A/05B_TESTS và 06_VALIDATION_AUDIT.md.\n', core)
    package('02_DATA_AUDIT.md', '''# Data loader, validator, manager, cấu hình và metadata

Metadata schema hiện được thể hiện qua template YAML và các hàm read_metadata/metadata_blockers, không có JSON Schema riêng.
Registry ghi nhiều trường confirmed=false; không suy ra nguồn/timezone/price side từ tên file.
symbols.json là metadata legacy; Instrument.from_metadata dùng metadata xác nhận và không tự đọc file legacy này.
Không kèm CSV, Parquet hoặc cache JSON giá. inspect_data.py được đóng gói để đọc, không thực thi trong nhiệm vụ này.
''', ['core/data_loader.py', 'core/data_validator.py', 'core/data_manager.py', 'inspect_data.py'] +
            [p for p in FILES if p.startswith(('configs/', 'data/metadata/'))])
    groups = {
        '03A_INDICATORS_TREND.md': ['indicators/moving_averages.py', 'indicators/trend.py'],
        '03B_INDICATORS_MOMENTUM.md': ['indicators/momentum.py'],
        '03C_INDICATORS_VOLATILITY.md': ['indicators/volatility.py'],
        '03D_INDICATORS_STRUCTURE.md': ['indicators/market_structure.py'],
        '03E_INDICATORS_PRICE_ACTION.md': ['indicators/price_action.py'],
        '03F_INDICATORS_SESSIONS_VOLUME.md': ['indicators/sessions.py'],
        '03G_INDICATORS_DIAGNOSTICS.md': ['inspect_indicators.py'],
    }
    intro = '''# Thư viện chỉ báo: sơ đồ, API, công thức và quy ước

```mermaid
flowchart LR
  sessions --> trend
  sessions --> volatility
  trend --> volatility
  trend --> moving_averages
  momentum --> moving_averages
  volatility --> moving_averages
  moving_averages --> _utils
  market_structure --> _utils
  price_action --> _utils
```

Mỗi nhóm 03A–03G chứa nguyên file tương ứng, đọc cùng `_utils.py` trong gói này và tests/test_indicators.py tại 05D.
Chức năng volume hiện có là session_vwap trong sessions.py (03F); không có volume.py riêng.
Tham chiếu công thức và URL bên dưới là tài liệu đã có trong repository, chưa truy cập web hoặc kiểm chứng nguồn bên ngoài trong nhiệm vụ này.
Chú ý khác biệt seed EMA/RMA, warm-up/NaN, swing chỉ phát sau xác nhận, pivot dùng kỳ trước đã hoàn tất;
session đòi timestamp khả dụng/đóng nến trong khi engine có thể nhận nhãn open.
Không có tự động đổi nhãn thời gian cho chỉ báo session trong BaseStrategy.
VWAP tick volume là proxy; annualization phải được người gọi cung cấp.
inspect_indicators.py hardcode đường dẫn artifact cũ và đưa ra giả thuyết diagnostic, không phải bằng chứng metadata đã xác nhận.

## Danh mục API tự trích từ AST
'''
    intro += table(['Module', 'Hàm public được định nghĩa'],
                   [(p, ', '.join(d['name'] for d in i.get('definitions', []) if not d['name'].startswith('_')))
                    for p, i in FILES.items() if p.startswith('indicators/') and p.endswith('.py')])
    package('03_INDICATORS_AUDIT.md', intro,
            ['indicators/INDICATORS.md', 'indicators/_utils.py', 'indicators/__init__.py', 'indicators/custom_indicators.py'])
    for name, paths in groups.items():
        package(name, '# ' + name.removesuffix('.md') + '\n\nĐọc cùng 03_INDICATORS_AUDIT.md và 05D_TESTS_INDICATORS.md.\n', paths)
    package('04_STRATEGIES_AUDIT.md', '''# Chiến lược và ví dụ trực tiếp

BaseStrategy nằm nguyên văn tại 01_CORE_AUDIT.md, không lặp lại.
first_strategy.py chỉ import BaseStrategy, chưa có lớp chiến lược hoặc quy tắc vào/ra.
benchmark_engine.py có BatchMean/IncrementalMean dùng dữ liệu tổng hợp cho benchmark;
đây là ví dụ API, không là chiến lược đã kiểm định lợi thế. Script benchmark không chạy lại trong hồ sơ này.
Các lớp chiến lược fixture khác nằm trong test_engine.py và test_stage4_review.py, xem 05B.
''', ['strategies/__init__.py', 'strategies/first_strategy.py', 'benchmark_engine.py'])
    test_groups = {
        '05A_TESTS_MODELS_COSTS_PORTFOLIO.md': ['tests/test_backtest_models.py', 'tests/test_cost_model.py', 'tests/test_execution.py', 'tests/test_portfolio.py'],
        '05B_TESTS_ENGINE_REVIEW.md': ['tests/test_engine.py', 'tests/test_stage4_review.py'],
        '05C_TESTS_DATA.md': ['tests/test_data_loader.py', 'tests/test_data_validator.py', 'tests/test_intraday_gaps.py'],
        '05D_TESTS_INDICATORS.md': ['tests/test_indicators.py'],
        '05E_TESTS_ENVIRONMENT.md': ['tests/test_environment.py'],
    }
    for name, paths in test_groups.items():
        package(name, '# ' + name.removesuffix('.md') + '\n\nToàn văn test; các fixture import qua module test khác cần đọc đồng thời 05A/05B/05C.\n', paths)
    tests = [p for p in FILES if p.startswith('tests/') and p.endswith('.py')]
    mapping = []
    for p in FILES:
        if p.endswith('.py') and p not in tests:
            direct = [t for t in tests if p in EDGES[t]]
            indirect = [t for t in tests if p in reachable(t) and t not in direct]
            mapping.append((p, ', '.join(direct) or 'Không có import trực tiếp', ', '.join(indirect) or 'Không có'))
    text = '''# Ánh xạ module và kiểm thử

Ánh xạ được suy ra từ AST import: trực tiếp và bắc cầu. Đây là liên hệ tĩnh,
không phải coverage theo dòng/nhánh và không chứng minh tất cả hàm đã được kiểm tra.
Dynamic import, getattr và khả năng gọi thực tế cần đọc test; coverage chưa đo được.
Các entry point run_backtest.py, inspect_data.py, inspect_indicators.py và benchmark_engine.py không có test import trực tiếp.
Các module placeholder chưa có kiểm thử hành vi vì chưa triển khai; không suy ra chúng hoàn thiện từ test toàn bộ pass.
'''
    text += table(['Module', 'Test import trực tiếp', 'Liên hệ import bắc cầu'], mapping)
    text += '''## Kiểm thử integrity cần đọc

- Timing, PnL tính tay, deterministic replay, prefix isolation, quy đổi FX, insolvency: test_engine.py (05B).
- Bid/Ask, tick rounding, commission, swap bị từ chối: test_cost_model.py (05A).
- SL/TP cùng nến và gap: test_execution.py (05A), test_engine.py (05B).
- Timestamp trùng/sai thứ tự, invalid OHLC, raw preservation trên fixture, lỗi ghi Parquet: 05C.
- Gap chỉ cảnh báo trong cùng ngày UTC và nến có dữ liệu kế tiếp: test_intraday_gaps.py (05C).
- Indicator alignment, prefix invariance, công thức tính tay, previous-period pivots, DST: 05D.
- Prefix leakage shift(-1)/centered rolling/full-sample normalization và incremental equivalence: test_stage4_review.py (05B).
- Chưa có pipeline đa khung thời gian hoàn chỉnh; test previous-period feature không thay thế kiểm thử toàn hệ thống MTF.

## Kết quả theo file từ JUnit lần chạy mới
'''
    cases = ET.parse(OUT/'pytest_results.xml').getroot().findall('.//testcase')
    counts = defaultdict(lambda: [0, 0, 0])
    for case in cases:
        key = case.get('classname', '')
        counts[key][0 if case.find('failure') is None and case.find('error') is None and case.find('skipped') is None else 2 if case.find('skipped') is not None else 1] += 1
    text += table(['Test module', 'Passed', 'Failed/errors', 'Skipped'], [(k, *v) for k, v in sorted(counts.items())])
    put('05_TESTS_AUDIT.md', text)
    package('06_VALIDATION_AUDIT.md', '''# Kiểm định, thống kê và báo cáo

Không có thư mục validation/ tại thời điểm khảo sát. Không tìm thấy module walk-forward,
sensitivity, chronological train/validation/test orchestration, multiple-testing correction hay tối ưu OOS trong danh mục source.
core/metrics.py chỉ có docstring, chưa tính Winrate, Profit Factor, Sharpe hoặc drawdown.
core/causality.py có code thực: kiểm tra kết quả có đổi khi thêm phần dữ liệu tương lai trên các prefix của mẫu.
Đây là bằng chứng trên mẫu, không chứng minh nhân quả cho mọi đầu vào và không thay thế đánh giá OOS.
Các writer JSON/Parquet có code thật ở 02_DATA_AUDIT.md; inspect_data.py ghi báo cáo data quality.
Engine trả BacktestResult trong bộ nhớ; chưa có bộ xuất report backtest/config snapshot/checksum end-to-end.
inspect_indicators.py là smoke-check diagnostic ở 03G, chưa chạy trong nhiệm vụ này.
Không đóng gói báo cáo nghiên cứu cũ có khả năng chứa mẫu giá; không dùng kết quả cũ làm kết quả kiểm tra mới.
''', ['core/causality.py', 'core/metrics.py'])
    result = f'''# Kết quả kỹ thuật thực thi thực tế

Thu thập UTC: {stamp}. Commit nền: `{commit}`; working tree có thay đổi sẵn.
Interpreter: `{E['executable']}`. Python: `{E['python']}`.

Pytest: **{passed} passed / {totals['failures']} failed / {totals['errors']} errors / {totals['skipped']} skipped**.
Không có test thất bại nên không có traceback thất bại để ghi; bật --tb=long trong lệnh thực tế.
JUnit XML đầy đủ có tại pytest_results.xml và được nhúng dưới đây để gói tự chứa.
Compile: {len(E['checks']['compile']['passed'])} file thành công, {len(E['checks']['compile']['failures'])} lỗi.
Biên dịch dùng compile(bytes, absolute_path, 'exec') trong bộ nhớ, không viết pyc và không chạy top-level của script.
Không phải kiểm tra type hay chứng minh import/runtime mọi entry point.

Coverage: CHƯA THỰC HIỆN, coverage và pytest-cov không cài.
Static analysis: CHƯA THỰC HIỆN với các analyzer không có sẵn trong bảng dưới.
Không cài dependency, không fetch web, không chạy pipeline dữ liệu thật hoặc benchmark.
git diff --check chỉ kiểm tra diff tracked, không bao phủ nội dung file untracked; mã untracked vẫn được compile và đóng gói.
Git có cảnh báo LF sẽ đổi sang CRLF ở indicators/__init__.py; return code diff check vẫn bằng 0.
pip check chỉ xác minh quan hệ dependency đang cài, không là security audit.

## Khả dụng công cụ
'''
    result += table(['Tool', 'Module có sẵn', 'Executable trong PATH'],
                    [(k, v['module_available'], v['executable'] or 'Không') for k, v in E['tools'].items()])
    for name, check in E['checks'].items():
        result += f'\n## {name}\n\n'
        if name == 'compile':
            result += '```json\n' + json.dumps(check, ensure_ascii=False, indent=2) + '\n```\n'
        else:
            result += f'Lệnh: `{check["command"]}`\n\nExit code: {check["returncode"]}; thời gian wall-clock: {check["seconds"]} giây.\n\n'
            for stream in ('stdout', 'stderr', 'error'):
                if stream in check:
                    result += f'{stream}:\n\n```text\n' + check[stream] + '\n```\n'
    result += '\n## JUnit XML nguyên vẹn\n\n```xml\n' + (OUT/'pytest_results.xml').read_text(encoding='utf-8') + '\n```\n'
    result += '\n## Giới hạn bảo toàn dữ liệu\n\nSHA256 của mọi source đã khảo sát không thay đổi sau kiểm tra.\n'
    result += f'Đối chiếu size/mtime của {len(E["data_file_stats_before"])} file trong data/, download/ và cache không phát hiện thay đổi. '
    result += 'Không đọc/hash toàn bộ dữ liệu giá lớn; size/mtime không phải chứng minh byte-for-byte cho dữ liệu lịch sử.\n'
    put('07_TEST_RESULTS.md', result)
    assert set(ASSIGN) == set(FILES), sorted(set(FILES)-set(ASSIGN))
    inventory = '# Danh mục nguồn và API\n\nDanh mục toàn bộ file thuộc phạm vi, không gồm hồ sơ kiểm toán tự sinh.\n'
    inventory += table(['File', 'Bytes', 'Dòng', 'Trạng thái', 'Gói chính'],
                       [(p, i['bytes'], i['lines'], i.get('status', 'document/config'), ASSIGN[p]) for p, i in sorted(FILES.items())])
    inventory += '\n## API, vai trò và import từng module Python\n\nDocstring vai trò bên dưới là trích từ file gốc. Trạng thái implementation chỉ có nghĩa AST có thân thực thi; không là chứng nhận hoàn thiện.\n'
    for p, item in sorted(FILES.items()):
        if not p.endswith('.py'):
            continue
        inventory += '\n### ' + p + '\n\n' + (item.get('docstring') or '(Không có docstring module)') + '\n\n'
        inventory += 'Trạng thái AST: ' + item['status'] + '.\n\n'
        tree = ast.parse((ROOT/p).read_text(encoding='utf-8-sig'))
        definitions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.append(f'{node.name} (dòng {node.lineno})')
                if isinstance(node, ast.ClassDef):
                    definitions.extend(f'{node.name}.{m.name} (dòng {m.lineno})' for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
        inventory += 'Hàm/class/method: ' + (', '.join(definitions) or 'Không có') + '.\n\n'
        inventory += 'Imports:\n\n```python\n' + '\n'.join(i['text'] for i in item.get('imports', [])) + '\n```\n'
        if item.get('review_markers'):
            inventory += table(['Dòng', 'Marker cần đọc ngữ cảnh'], [(m['line'], m['text']) for m in item['review_markers']])
    put('00A_SOURCE_INVENTORY.md', inventory)
    handoff = f'''# Hướng dẫn bàn giao Claude

Commit nền `{commit}`. Snapshot thu thập UTC {stamp}; tạo tài liệu UTC {datetime.now(timezone.utc).isoformat()}.
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

Không có file source trong danh mục bị bỏ sót: toàn bộ {len(FILES)} file đều được đóng gói.
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
'''
    descriptions = {
        '00_PROJECT_OVERVIEW.md': 'Kiến trúc, môi trường, README, pyproject và entry point',
        '00A_SOURCE_INVENTORY.md': 'Toàn bộ file, trạng thái, API/method và import',
        '00B_PROJECT_RULES.md': 'Toàn văn .clinerules/',
        '01_CORE_AUDIT.md': 'Models, costs, execution, portfolio, engine, BaseStrategy và tài liệu engine',
        '02_DATA_AUDIT.md': 'Loader/validator/manager, data CLI, configs và metadata',
        '03_INDICATORS_AUDIT.md': 'Công thức/tài liệu gốc, danh mục chỉ báo, shared utils và initializer',
        '04_STRATEGIES_AUDIT.md': 'Strategy skeleton và ví dụ benchmark',
        '05_TESTS_AUDIT.md': 'Ánh xạ module→test và kết quả từng file',
        '06_VALIDATION_AUDIT.md': 'Causality implementation, metrics placeholder và phần validation chưa có',
        '07_TEST_RESULTS.md': 'Lệnh, stdout/stderr đầy đủ, JUnit và giới hạn kiểm thử',
        '08_AUDIT_HANDOFF.md': 'Hướng dẫn, ghép gói, giả định, điểm rủi ro và loại trừ',
        'MANIFEST.md': 'Mỗi source→gói, số dòng/byte/SHA256 và hash gói',
    }
    handoff += table(['Gói', 'Phạm vi'], [(name, descriptions.get(name, name.removesuffix('.md').replace('_', ' ')))
                                          for name in sorted([*PACKAGES, '08_AUDIT_HANDOFF.md', 'MANIFEST.md'])])
    put('08_AUDIT_HANDOFF.md', handoff)
    for name, text in PACKAGES.items():
        with (OUT/name).open('x', encoding='utf-8', newline='') as stream:
            stream.write(text)
    verified = []
    for b in BLOCKS:
        payload = (OUT/b['package']).read_bytes()
        prefix = b['prefix'].encode('utf-8')
        start = payload.index(prefix) + len(prefix)
        copied = payload[start:start+b['content_bytes']]
        original = (ROOT/b['path']).read_bytes()
        assert copied == original, b['path']
        assert payload[start+b['content_bytes']:].startswith(b['suffix'].encode('utf-8')), b['path']
        verified.append(dict(path=b['path'], package=b['package'], bytes=len(copied), sha256=hashlib.sha256(copied).hexdigest(), exact_match=True))
    manifest = f'# Manifest hồ sơ kiểm toán\n\nSnapshot UTC: {stamp}; commit nền: `{commit}`.\n\n'
    manifest += f'{len(FILES)} source, {len(verified)} bản sao byte-for-byte khớp; không có source bị bỏ sót hoặc lặp toàn văn.\n'
    manifest += 'SHA256 dùng bytes gốc, bảo toàn CRLF/BOM/trailing newline; nội dung block không thêm line numbers.\n'
    manifest += table(['File nguồn', 'Gói chứa toàn văn', 'Bytes', 'Dòng', 'SHA256'],
                      [(p, ASSIGN[p], i['bytes'], i['lines'], i['sha256']) for p, i in sorted(FILES.items())])
    manifest += '\n## Kích thước và SHA256 từng gói\n\nKhông tự hash MANIFEST để tránh tham chiếu vòng.\n'
    manifest += table(['Gói', 'Bytes', 'SHA256'], [(n, (OUT/n).stat().st_size, hashlib.sha256((OUT/n).read_bytes()).hexdigest()) for n in sorted(PACKAGES)])
    manifest += '\n## File ngoài phạm vi\n\nKhông có source thuộc danh mục chưa đóng gói. Lịch sử giá, cache, bí mật, môi trường, Git và báo cáo cũ bị loại theo chỉ thị; xem 08_AUDIT_HANDOFF.md.\n'
    safe(manifest, 'MANIFEST.md')
    (OUT/'MANIFEST.md').write_text(manifest, encoding='utf-8', newline='')
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  source_count=len(FILES), verbatim_blocks_verified=len(verified),
                  uncovered_sources=sorted(set(FILES)-set(ASSIGN)), duplicate_sources=[],
                  sources=verified,
                  packages=[dict(path=p.name, bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.glob('*.md'))])
    (OUT/'package_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for p in OUT.iterdir():
        if p.is_file():
            safe(p.read_text(encoding='utf-8'), p.name)
    print(json.dumps({k: report[k] for k in ('source_count', 'verbatim_blocks_verified', 'uncovered_sources')}, indent=2))
    for item in report['packages']:
        print(item['path'], item['bytes'])


if __name__ == '__main__':
    main()