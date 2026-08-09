from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .artifact import build_manifest, verify_artifact
from .config import load_config
from .dataset import validate_dataset, write_receipt
from .figures import make_figures
from .release import audit_release


def main() -> None:
    parser = argparse.ArgumentParser(prog="probe-scent")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-data")
    validate.add_argument("--config", default="configs/v1.yaml")
    validate.add_argument("--receipt", default="data/v1/validation.json")
    run = sub.add_parser("run")
    run.add_argument("args", nargs=argparse.REMAINDER)
    analyze_cmd = sub.add_parser("analyze")
    analyze_cmd.add_argument("args", nargs=argparse.REMAINDER)
    figures = sub.add_parser("make-figures")
    figures.add_argument("--config", default="configs/v1.yaml")
    figures.add_argument("--raw", default="results/v1/raw/attempts.jsonl")
    figures.add_argument("--output-dir", default="results/v1/figures")
    verify = sub.add_parser("verify-artifact")
    verify.add_argument("--config", default="configs/v1.yaml")
    verify.add_argument("--result-dir", default="results/v1")
    verify.add_argument("--write-manifest", action="store_true")
    verify.add_argument("--no-regenerate", action="store_true")
    audit = sub.add_parser("audit-release")
    audit.add_argument("--root", default=".")
    args = parser.parse_args()
    if args.command == "validate-data":
        config = load_config(Path(args.config))
        receipt = validate_dataset(
            Path(config.canonical_dataset_path), expected_sha256=config.dataset_sha256
        )
        receipt["protocol_version"] = config.version
        receipt["run_order_seed"] = config.run_order_seed
        write_receipt(receipt, Path(args.receipt))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        if receipt["status"] != "PASS":
            raise SystemExit(1)
        return
    if args.command == "run":
        raise SystemExit(subprocess.call([sys.executable, "-m", "probe_scent.run", *args.args]))
    if args.command == "analyze":
        raise SystemExit(
            subprocess.call([sys.executable, "-m", "probe_scent.analyze", *args.args])
        )
    if args.command == "make-figures":
        config = load_config(Path(args.config))
        make_figures(Path(args.raw), Path(config.canonical_dataset_path), Path(args.output_dir))
        return
    if args.command == "verify-artifact":
        result_dir = Path(args.result_dir)
        if args.write_manifest:
            manifest = build_manifest(result_dir, result_dir / "MANIFEST.json")
            print(json.dumps({"manifest_files": len(manifest)}, indent=2))
            return
        receipt = verify_artifact(
            Path(args.config), result_dir, regenerate=not args.no_regenerate
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        if receipt["status"] == "FAIL":
            raise SystemExit(1)
        return
    if args.command == "audit-release":
        receipt = audit_release(Path(args.root))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        if receipt["status"] != "PASS":
            raise SystemExit(1)
        return


if __name__ == "__main__":
    main()
