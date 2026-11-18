"""Collect local audit evidence without editing project sources or dependencies."""

import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SKIP = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
        '.dukascopy-cache', 'download', 'raw', 'processed', 'runs',
        'external_audit', 'build', 'dist', 'node_modules'}
EXTENSIONS = {'.py', '.md', '.toml', '.yaml', '.yml', '.json', '.ini', '.cfg', '.txt', '.ipynb'}


def sources():
    for base, directories, files in os.walk(ROOT):
        directories[:] = sorted(d for d in directories if d not in SKIP
                                and not d.endswith(('_cache', '.egg-info')))
        for name in sorted(files):
            p = Path(base) / name
            if name.startswith('.env') or p.suffix in {'.key', '.pem'}:
                continue
            if p.suffix.lower() in EXTENSIONS or name == '.gitignore':
                yield p


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(args, timeout=60):
    start = time.monotonic()
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
               PYTHONUTF8='1', NO_COLOR='1', GIT_OPTIONAL_LOCKS='0')
    try:
        p = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                           timeout=timeout)
        return dict(command=subprocess.list2cmdline(args), returncode=p.returncode,
                    seconds=round(time.monotonic()-start, 3),
                    stdout=p.stdout.decode('utf-8', errors='replace'),
                    stderr=p.stderr.decode('utf-8', errors='replace'))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(command=subprocess.list2cmdline(args), returncode=None,
                    seconds=round(time.monotonic()-start, 3), error=str(exc))


def main():
    if (OUT / 'evidence.json').exists():
        raise FileExistsError('Preserve previous audit evidence.')
    records = []
    for p in sources():
        raw = p.read_bytes()
        text = raw.decode('utf-8-sig')
        item = dict(path=p.relative_to(ROOT).as_posix(), bytes=len(raw),
                    lines=len(text.splitlines()), sha256=sha(raw))
        if p.suffix == '.py':
            tree = ast.parse(text, filename=str(p))
            item['docstring'] = ast.get_docstring(tree)
            item['definitions'] = [dict(name=n.name, line=n.lineno,
                                       kind=type(n).__name__, docstring=ast.get_docstring(n))
                                   for n in tree.body
                                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            item['imports'] = [dict(line=n.lineno, text=ast.unparse(n),
                                    module=n.module if isinstance(n, ast.ImportFrom) else None,
                                    level=n.level if isinstance(n, ast.ImportFrom) else 0,
                                    names=[a.name for a in n.names])
                               for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
            body = [n for n in tree.body if not (isinstance(n, ast.Expr)
                    and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))
                    and not isinstance(n, (ast.Import, ast.ImportFrom))]
            item['status'] = 'empty' if not text.strip() else 'placeholder' if not body else 'implementation'
            item['review_markers'] = [dict(line=i, text=line.strip())
                                      for i, line in enumerate(text.splitlines(), 1)
                                      if any(k in line for k in ('TODO', 'FIXME', 'NotImplementedError'))
                                      or line.strip() in ('pass', '...')]
        records.append(item)
    data_stats = {}
    for folder in ('data', 'download', '.dukascopy-cache'):
        for base, directories, files in os.walk(ROOT / folder):
            for name in files:
                p = Path(base) / name
                s = p.stat()
                data_stats[p.relative_to(ROOT).as_posix()] = [s.st_size, s.st_mtime_ns]
    evidence = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    root=str(ROOT), python=sys.version, executable=sys.executable,
                    packages=sorted(set((d.metadata['Name'], d.version)
                                        for d in importlib.metadata.distributions())),
                    source_files=records, data_file_stats_before=data_stats,
                    git_head=run(['git', 'rev-parse', 'HEAD']),
                    git_status_before=run(['git', '-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--untracked-files=all']),
                    checks={})
    (OUT / 'baseline.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    checks = evidence['checks']
    checks['pytest'] = run([sys.executable, '-B', '-m', 'pytest', '-vv', '--tb=long',
                            '-p', 'no:cacheprovider', '--color=no',
                            '--junitxml=' + str(OUT / 'pytest_results.xml')])
    print('pytest:', checks['pytest']['returncode'], checks['pytest'].get('stdout', '')[-1200:], flush=True)
    checks['git_diff_check'] = run(['git', 'diff', '--check'])
    checks['git_diff_cached_check'] = run(['git', 'diff', '--cached', '--check'])
    checks['pip_check'] = run([sys.executable, '-B', '-m', 'pip', 'check'])
    compiled, failures = [], []
    for item in records:
        if item['path'].endswith('.py'):
            try:
                compile((ROOT / item['path']).read_bytes(), str(ROOT / item['path']), 'exec')
                compiled.append(item['path'])
            except (SyntaxError, ValueError) as exc:
                failures.append(dict(path=item['path'], error=str(exc)))
    checks['compile'] = dict(method='Python compile(bytes, absolute_path, exec), in memory; no pyc files',
                             passed=compiled, failures=failures)
    evidence['tools'] = {}
    for name in ('coverage', 'pytest_cov', 'ruff', 'mypy', 'pylint', 'flake8', 'bandit', 'pyright'):
        module = importlib.util.find_spec(name) is not None
        executable = shutil.which(name)
        evidence['tools'][name] = dict(module_available=module, executable=executable)
        arguments = {'ruff': ['check', '--no-cache'], 'mypy': ['--no-incremental'],
                     'pylint': ['--persistent=n'], 'flake8': [], 'bandit': ['-r'], 'pyright': []}
        if name in arguments and (module or executable):
            prefix = [sys.executable, '-B', '-m', name] if module else [executable]
            targets = [i['path'] for i in records if i['path'].endswith('.py')]
            checks[name] = run(prefix + arguments[name] + targets)
    source_changes = [i['path'] for i in records if sha((ROOT/i['path']).read_bytes()) != i['sha256']]
    data_changes = [name for name, stats in data_stats.items()
                    if not (ROOT/name).exists() or [(ROOT/name).stat().st_size, (ROOT/name).stat().st_mtime_ns] != stats]
    evidence['preservation'] = dict(source_sha256_changes=source_changes,
                                   data_size_mtime_changes=data_changes,
                                   data_check_limitation='Size and mtime only; not full-content hashes of historical datasets.')
    evidence['git_status_after'] = run(['git', '-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--untracked-files=all'])
    (OUT / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, result in checks.items():
        (OUT / (name + '.log')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('sources:', len(records), 'compile:', len(compiled), 'failures:', failures,
          'preservation:', evidence['preservation'], flush=True)


if __name__ == '__main__':
    main()