"""Inspect all raw CSVs and export selected full diagnostic Parquet datasets."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import platform
import subprocess
from uuid import uuid4

import pandas as pd
import pyarrow
import yaml

from core.data_loader import (
    load_csv, load_parquet, read_metadata, save_parquet, sha256_file, write_json,
)
from core.data_validator import validate_data

ROOT = Path(__file__).resolve().parent


def merge_metadata(template: dict, overrides: dict) -> dict:
    """Recursively apply dataset overrides to the single shared metadata template."""
    result = deepcopy(template)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_metadata(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def main() -> None:
    """Run reproducible inspection; unknown CSV metadata must be provided first."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/data_pipeline.yaml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    with args.config.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if config.get("diagnostic") is not True:
        raise ValueError("This inspection entry point requires diagnostic: true.")
    registry_path = ROOT / config["registry"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(registry.get("datasets"), list) or not registry["datasets"]:
        raise ValueError("Registry datasets must be a non-empty list.")
    filenames = [item.get("filename") for item in registry["datasets"]]
    if any(not isinstance(name, str) for name in filenames) or len(set(filenames)) != len(filenames):
        raise ValueError("Registry filenames must be unique non-empty strings.")
    entries = {item["filename"]: item for item in registry["datasets"]}
    raw_files = sorted((ROOT / config["raw_directory"]).glob("*.csv"))
    if not raw_files:
        raise ValueError("No CSV files found in configured raw directory.")
    unknown = [path.name for path in raw_files if path.name not in entries]
    if unknown:
        raise ValueError(f"Add explicit metadata registry entries for: {unknown}")
    missing_raw_entries = sorted(set(entries) - {path.name for path in raw_files})
    if missing_raw_entries:
        raise ValueError(f"Registry contains files absent from data/raw: {missing_raw_entries}")
    template_name = registry.get("metadata_template")
    if not isinstance(template_name, str):
        raise ValueError("Registry must define one metadata_template YAML file.")
    template = read_metadata(ROOT / config["metadata_directory"] / template_name)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    report_directory = ROOT / config["report_directory"] / ("data-quality-" + run_id)
    output_directory = ROOT / config["output_directory"] / ("inspection-" + run_id)
    report_directory.mkdir(parents=True, exist_ok=False)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip() or None
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    summary = {"run_id": run_id, "config": config, "registry": registry,
               "git_revision": revision, "working_tree_dirty": bool(dirty),
               "software": {"python": platform.python_version(), "pandas": pd.__version__,
                            "pyarrow": pyarrow.__version__},
               "code_sha256": {name: sha256_file(ROOT / name) for name in (
                   "inspect_data.py", "core/data_loader.py", "core/data_validator.py")},
               "datasets": []}
    for path in raw_files:
        before = sha256_file(path)
        metadata = merge_metadata(template, entries[path.name].get("metadata_overrides", {}))
        result = load_csv(path, metadata, diagnostic=True)
        report = validate_data(result.data, metadata, load_diagnostics=result.diagnostics)
        report["source_sha256"] = before
        report["metadata_snapshot"] = metadata
        # Every registered raw CSV is exported; the registry completeness
        # checks above prevent silent omissions.
        if path.name in entries:
            target = output_directory / (path.stem + ".diagnostic.parquet")
            save_parquet(result.data, target)
            pd.testing.assert_frame_equal(result.data, load_parquet(target))
            artifact = {"parquet_path": str(target), "parquet_sha256": sha256_file(target),
                        "source_path": str(path), "source_sha256": before,
                        "metadata_snapshot": metadata, "diagnostic_only": True,
                        "run_id": run_id, "ready_for_research": report["ready_for_research"],
                        "transformations": ["Explicit candidate Unix milliseconds to UTC", "Numeric parsing; no sorting, deduplication or filling"],
                        "row_count": len(result.data)}
            write_json(target.with_suffix(".metadata.json"), artifact)
            report["processed_artifact"] = artifact
        after = sha256_file(path)
        report["raw_unchanged"] = before == after
        if before != after:
            raise RuntimeError(f"Raw file changed during inspection: {path}")
        write_json(report_directory / (path.stem + ".quality.json"), report)
        summary["datasets"].append({"filename": path.name, "rows": len(result.data),
                                    "errors": report["errors"], "status": report["status"],
                                    "raw_unchanged": report["raw_unchanged"]})
        print(json.dumps(summary["datasets"][-1], ensure_ascii=False))
    write_json(report_directory / "summary.json", summary)
    print(f"Reports: {report_directory}")
    print(f"Processed: {output_directory}")


if __name__ == "__main__":
    main()