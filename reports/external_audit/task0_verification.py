"""Capture and independently verify an existing dirty research snapshot.

All generated files are confined to the audit directory. Product code is imported
without bytecode generation; pytest temporary files are confined here as well.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "reports" / "external_audit"
OUT = AUDIT / "task0_evidence"
ORIGINAL = Path(r"C:\Users\Admin\.gemini\antigravity\brain\7022fcc8-43b1-4837-9f65-458cfcebf9d9\scratch")
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def git(*args):
    return subprocess.run(["git", "--no-pager", *args], cwd=ROOT, capture_output=True).stdout.decode("utf-8", errors="replace")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    excluded = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".dukascopy-cache", "download"}
    result = {}
    for directory, dirs, files in os.walk(ROOT):
        relative = Path(directory).relative_to(ROOT).as_posix()
        dirs[:] = [d for d in dirs if d not in excluded and not (relative == "reports" and d == "external_audit")]
        for filename in files:
            path = Path(directory) / filename
            key = path.relative_to(ROOT).as_posix()
            result[key] = {"bytes": path.stat().st_size, "sha256": sha(path)}
    return result


def capture():
    OUT.mkdir(exist_ok=False)
    for name, args in {
        "git_status_before.txt": ("status", "--porcelain=v2", "--branch", "--untracked-files=all"),
        "git_diff_before.patch": ("diff", "--no-ext-diff", "--binary"),
        "git_diff_cached_before.patch": ("diff", "--cached", "--no-ext-diff", "--binary"),
        "git_tracked_files.txt": ("ls-files",),
        "git_untracked_files.txt": ("ls-files", "--others", "--exclude-standard"),
        "git_head.txt": ("rev-parse", "HEAD"),
    }.items():
        (OUT / name).write_text(git(*args), encoding="utf-8")
    before = inventory()
    dump("snapshot_before.json", before)
    manifest = (AUDIT / "MANIFEST.md").read_text(encoding="utf-8")
    comparisons = []
    for path, expected in re.findall(r"^\| ([^|]+?) \| [^|]+ \| \d+ \| \d+ \| ([0-9a-f]{64}) \|$", manifest, re.M):
        current = before.get(path.strip(), {}).get("sha256")
        comparisons.append({"path": path.strip(), "expected": expected, "actual": current,
                            "status": "MATCH" if current == expected else "VERSION MISMATCH"})
    dump("manifest_comparison.json", comparisons)
    evidence = {}
    copied = OUT / "opus_original"
    copied.mkdir()
    for name in ("probes.py", "probes2.py", "probe_results.json", "perf.py", "perf_results.jsonl", "perf_results_large.jsonl"):
        source = ORIGINAL / name
        if source.is_file():
            shutil.copyfile(source, copied / name)
            evidence[name] = {"original_path": str(source), "sha256": sha(source), "copy_sha256": sha(copied / name)}
        else:
            evidence[name] = {"missing": True}
    dump("opus_original_hashes.json", evidence)
    paths = ["data/raw/task0_probe.csv", "data/raw/nested/task0_probe.csv", "data/processed/task0_probe.parquet",
             "reports/runs/task0_probe.json", ".venv/Scripts/python.exe", "venv/x", ".env", ".env.local",
             "private.key", "private.pem", "secrets.json", "credentials.json", "api_keys.yaml", "secrets/token.txt", ".env.example"]
    ignored = {}
    for path in paths:
        process = subprocess.run(["git", "check-ignore", "-v", "--no-index", "--", path], cwd=ROOT, capture_output=True, text=True)
        ignored[path] = {"exit_code": process.returncode, "rule": process.stdout.strip()}
    tracked = git("ls-files").splitlines()
    suspicious = [p for p in tracked if re.search(r"(^|/)(raw|\.venv|venv|secrets?)(/|$)|(^|/)(\.env($|\.)|credentials|api[_-]?keys)|\.(pem|key)$", p, re.I)]
    # Only report file names and line numbers, never matched credential content.
    credential_matches = []
    patterns = [re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
                re.compile(r'''(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[=:]\s*["'][^"'\s]{12,}["']''')]
    for name in tracked + git("ls-files", "--others", "--exclude-standard").splitlines():
        path = ROOT / name
        if name.startswith("reports/external_audit/") or not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in patterns):
                credential_matches.append({"path": name, "line": number})
    dump("gitignore_check.json", {"paths": ignored, "tracked_sensitive_path_candidates": suspicious,
                                  "credential_pattern_candidates_no_values": credential_matches,
                                  "scan_scope": "tracked and nonignored untracked text <=2MB, excluding audit evidence; heuristic, not proof of absence"})
    dump("environment.json", {"utc": datetime.now(timezone.utc).isoformat(), "executable": sys.executable,
                             "python": sys.version, "packages": {name: importlib.metadata.version(name) for name in ("pandas", "numpy", "pytest", "PyYAML", "pyarrow")}})
    print(f"Captured {len(before)} files including raw/processed/run artifacts; manifest matches {sum(x['status'] == 'MATCH' for x in comparisons)}/{len(comparisons)}")


def command(name, args):
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    environment["TEMP"] = environment["TMP"] = str(OUT)
    start = datetime.now(timezone.utc)
    with (OUT / f"{name}.stdout.txt").open("wb") as stdout, (OUT / f"{name}.stderr.txt").open("wb") as stderr:
        completed = subprocess.run([sys.executable, "-B", *args], cwd=ROOT, env=environment, stdout=stdout, stderr=stderr)
    dump(f"{name}.execution.json", {"command": [sys.executable, "-B", *args], "cwd": str(ROOT),
                                    "started_utc": start.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(),
                                    "exit_code": completed.returncode, "environment_overrides": {k: environment[k] for k in ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "PYTHONUTF8", "TEMP", "TMP")}})
    print(f"{name}: exit={completed.returncode}")


def reuse_opus():
    """Run reviewed selected original AST nodes, without unrelated probe side effects."""
    path = OUT / "opus_original" / "probes.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    selected = {"CORE-F2a_exact_touch_float", "CORE-F4_strategy_reuse", "CORE-F5_provenance_keys", "IND-4_default_tolerance_masks_1tick_leak"}
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "R" for t in node.targets):
            nodes.append(node)
        elif isinstance(node, ast.ClassDef) and node.name == "Scripted":
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef):
            if node.name in {"probe", "meta", "bars4", "eng"}:
                nodes.append(node)
            elif any(isinstance(d, ast.Call) and d.args and isinstance(d.args[0], ast.Constant) and d.args[0].value in selected for d in node.decorator_list):
                nodes.append(node)
    namespace = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    dump("opus_selected_rerun.json", namespace["R"])
    assert len(namespace["R"]) == 4


def independent():
    import pandas as pd
    from dataclasses import fields
    from core.cost_model import CostModel
    from core.engine import BacktestEngine
    from core.execution import protective_exit
    from core.models import Fill, Position
    from core.causality import check_prefix_invariance
    from strategies.base_strategy import BaseStrategy
    from benchmark_engine import IncrementalMean

    timestamp = pd.Timestamp("2024-01-01", tz="UTC")
    tick = 0.00001
    cost = CostModel(4 * tick, 0, 0)
    cases = []
    for direction, level_kind in ((1, "sl"), (1, "tp"), (-1, "sl"), (-1, "tp")):
        misses = []
        miss_count = 0
        for m in range(100_000, 130_000, 7):
            # Integer tick arithmetic is the oracle, independent of float offsets.
            level_tick = m - 2 * direction
            level = level_tick * tick
            trigger = "low" if (direction == 1) == (level_kind == "sl") else "high"
            bar = {"open": (m + (10 if trigger == "low" else -10)) * tick,
                   "high": (m + 20) * tick, "low": (m - 20) * tick, "close": m * tick}
            bar[trigger] = m * tick
            side_bar = cost.side_bar(bar, "Mid", -direction)
            fill = Fill(1, timestamp, direction, 1, (level_tick + direction * (10 if level_kind == "sl" else -10)) * tick, 0, 0, 0, "entry")
            position = Position(direction, 1, fill, level if level_kind == "sl" else None,
                                level if level_kind == "tp" else None, 100)
            actual = protective_exit(position, side_bar)
            if actual is None:
                miss_count += 1
                if len(misses) < 2:
                    misses.append({"m": m, "level_tick": level_tick, "level": repr(level),
                                   "executable_extreme": repr(side_bar[trigger]),
                                   "difference": side_bar[trigger] - level, "source_bar": bar,
                                   "actual": None, "expected": "stop_loss" if level_kind == "sl" else "take_profit"})
        cases.append({"direction": direction, "level_kind": level_kind,
                      "tested": len(range(100_000, 130_000, 7)), "miss_count": miss_count,
                      "status": "VERIFIED" if miss_count else "NOT REPRODUCED",
                      "sample_misses": misses})
    data = pd.DataFrame({"close": [1.08] * 10}, index=pd.date_range(timestamp, periods=10, freq="min"))
    causal = {}
    probes = {
        "one_tick_leak_series": (lambda d: d.close + tick * (len(d) % 2), data, None),
        "one_tick_leak_frame": (lambda d: (d.close + tick * (len(d) % 2)).to_frame(), data, None),
        "large_leak_control": (lambda d: d.close + .001 * (len(d) % 2), data, None),
        "empty_data": (lambda d: d.close, data.iloc[:0], None),
        "single_row": (lambda d: d.close, data.iloc[:1], None),
        "empty_cutoffs": (lambda d: d.close, data, []),
        "reverse_index": (lambda d: d.close, data.iloc[::-1], None),
        "duplicate_index": (lambda d: d.close, data.set_axis([timestamp] * 10), None),
        "invalid_cutoff_control": (lambda d: d.close, data, [0]),
        "causal_control": (lambda d: d.close.rolling(2).mean(), data, None),
    }
    for name, (builder, sample, cutoffs) in probes.items():
        try:
            check_prefix_invariance(builder, sample, cutoffs=cutoffs)
            causal[name] = {"actual": "PASS (returned None)"}
        except ValueError as error:
            causal[name] = {"actual": "REJECT", "message": str(error)}
    full = data.close + tick * (len(data) % 2)
    prefix = data.iloc[:1].close + tick
    causal["one_tick_leak_evidence"] = {"full_first": float(full.iloc[0]), "prefix_first": float(prefix.iloc[0]),
                                         "difference": float(prefix.iloc[0] - full.iloc[0]),
                                         "exact_equal": full.iloc[:1].equals(prefix)}
    values = {"source": "independent synthetic audit", "symbol": "TESTUSD", "source_timezone": "UTC",
              "timestamp_encoding": "aware", "timestamp_kind": "open", "price_type": "Mid", "timeframe": "1min",
              "instrument_specifications": {"tick_size": .01, "pip_size": .01, "contract_size": 1,
                                             "quantity_unit": "units", "quote_currency": "USD", "minimum_quantity_increment": 1}}
    metadata = {k: {"value": v, "confirmed": True, "evidence": "Synthetic audit fixture"} for k, v in values.items()}
    model = BacktestEngine(metadata, CostModel(0, 0, 0), initial_capital=10000, account_currency="USD", quantity=1)
    close = [100.0 + i * .01 for i in range(40)]
    frame = pd.DataFrame({"open": close, "high": [v + 1 for v in close], "low": [v - 1 for v in close], "close": close},
                         index=pd.date_range(timestamp, periods=40, freq="min"))
    stateful = IncrementalMean()
    first = model.run(frame, stateful)
    second = model.run(frame, stateful)
    fresh = model.run(frame, IncrementalMean())
    class NoTrade(BaseStrategy):
        def generate_signals(self, d):
            return pd.DataFrame({"signal": 0, "exit": False}, index=d.index)
    no_trade_a = model.run(frame, NoTrade({"label": "A"}))
    changed = frame.copy(deep=True)
    changed["high"] += 1
    no_trade_b = model.run(changed, NoTrade({"label": "B"}))
    import core.metrics as metrics
    report_files = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "reports" / "runs").rglob("*") if p.is_file())
    result = {
        "QBS-01": cases, "QBS-02": causal,
        "QBS-03": {"result_fields": [f.name for f in fields(no_trade_a)], "assumptions_keys": list(no_trade_a.assumptions),
                   "different_dataset_high_and_strategy_params_same_result": no_trade_a == no_trade_b,
                   "dataset_a_high_first": float(frame.high.iloc[0]), "dataset_b_high_first": float(changed.high.iloc[0]),
                   "strategy_a_params": {"label": "A"}, "strategy_b_params": {"label": "B"}},
        "QBS-07": {"strategy": "benchmark_engine.IncrementalMean (existing product benchmark)",
                   "reused_equal": first == second, "fresh_equal": first == fresh,
                   "first_orders": len(first.orders), "second_orders": len(second.orders),
                   "first_fill": first.fills[0] if first.fills else None, "second_fill": second.fills[0] if second.fills else None,
                   "first_final_equity": first.states[-1].equity, "second_final_equity": second.states[-1].equity},
        "implementation": {"metrics_public_callables": [k for k, v in vars(metrics).items() if not k.startswith("_") and callable(v)],
                           "report_run_files": report_files}}
    dump("independent_results.json", result)
    print(json.dumps(result, indent=2, default=str))
    assert any(c["sample_misses"] for c in cases), "Exact-touch finding was not reproduced"
    assert causal["large_leak_control"]["actual"] == "REJECT"
    assert causal["causal_control"]["actual"].startswith("PASS")
    assert first != second and first == fresh
    assert no_trade_a == no_trade_b


def verify_final():
    before = json.loads((OUT / "snapshot_before.json").read_text(encoding="utf-8"))
    after = inventory()
    dump("snapshot_after.json", after)
    changed = [p for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]
    (OUT / "git_status_after.txt").write_text(git("status", "--porcelain=v2", "--branch", "--untracked-files=all"), encoding="utf-8")
    dump("scope_verification.json", {"changed_outside_audit": changed, "files_compared": len(before),
                                     "head_unchanged": git("rev-parse", "HEAD").strip() == (OUT / "git_head.txt").read_text().strip(),
                                     "git_diff_unchanged": git("diff", "--no-ext-diff", "--binary") == (OUT / "git_diff_before.patch").read_text(encoding="utf-8"),
                                     "git_index_diff_unchanged": git("diff", "--cached", "--no-ext-diff", "--binary") == (OUT / "git_diff_cached_before.patch").read_text(encoding="utf-8")})
    print(f"Changed outside audit: {changed}")
    assert not changed


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "capture":
        capture()
    elif mode == "pytest":
        command("pytest", ["-m", "pytest", "-vv", "-p", "no:cacheprovider", "--basetemp", str(OUT / "pytest_tmp"), "--junitxml", str(OUT / "pytest_results.xml")])
    elif mode == "opus":
        reuse_opus()
    elif mode == "independent":
        independent()
    elif mode == "run-probes":
        command("independent", [str(Path(__file__)), "independent"])
        command("opus_selected", [str(Path(__file__)), "opus"])
    elif mode == "runner":
        command("runner", [str(ROOT / "run_backtest.py")])
    elif mode == "benchmark":
        command("benchmark_small", [str(ROOT / "benchmark_engine.py"), "--sizes", "100", "1000", "--repeats", "1"])
    elif mode == "final":
        verify_final()
    else:
        raise ValueError(mode)