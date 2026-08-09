from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .analyze import analyze, canonicalize_attempts, read_attempts
from .config import load_config
from .dataset import file_sha256, read_scenarios, validate_dataset
from .figures import make_figures
from .prompts import prompt_sha256

REQUIRED_DERIVED = (
    "summary.json",
    "claims.json",
    "canonical_results.jsonl",
    "tables/condition_summary.csv",
    "tables/paired_effects.csv",
    "tables/domain_effects.csv",
    "tables/sensitivity.csv",
    "figures/figure_1_conditions.svg",
    "figures/figure_2_paired.svg",
    "figures/figure_3_domains.svg",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(result_dir: Path, output: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in REQUIRED_DERIVED:
        path = result_dir / rel
        if not path.exists():
            raise FileNotFoundError(f"Cannot build manifest; missing {path}")
        files[rel] = sha256(path)
    raw = result_dir / "raw/attempts.jsonl"
    if not raw.exists():
        raise FileNotFoundError(f"Cannot build manifest; missing {raw}")
    files["raw/attempts.jsonl"] = sha256(raw)
    output.write_text(json.dumps(files, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return files


def _require_column_value(
    canonical: Any,
    column: str,
    expected: str,
    errors: list[str],
) -> None:
    if column not in canonical.columns:
        errors.append(f"raw results missing required provenance column: {column}")
        return
    values = canonical[column].dropna().astype(str)
    if len(values) != len(canonical):
        errors.append(f"raw results contain missing provenance values: {column}")
        return
    if bool((values != expected).any()):
        errors.append(f"raw results contain wrong {column}; expected {expected}")


def verify_artifact(config_path: Path, result_dir: Path, regenerate: bool = True) -> dict[str, Any]:
    config = load_config(config_path)
    errors: list[str] = []
    canonical_dataset = Path(config.canonical_dataset_path)
    dataset_receipt = validate_dataset(
        canonical_dataset, expected_sha256=config.dataset_sha256
    )
    if dataset_receipt["status"] != "PASS":
        errors.append("dataset validation failed")

    pair_audit_path = canonical_dataset.with_name("pair_audit.json")
    if not pair_audit_path.exists():
        errors.append("manual pair-audit receipt missing")
    else:
        pair_audit = json.loads(pair_audit_path.read_text(encoding="utf-8"))
        if pair_audit.get("status") != "PASS" or pair_audit.get("pairs_reviewed") != 30:
            errors.append("manual pair-audit receipt is not a 30-pair PASS")

    run_order = Path(config.dataset_path)
    if file_sha256(run_order) != config.run_order_sha256:
        errors.append("run-order hash mismatch")

    raw = result_dir / "raw/attempts.jsonl"
    if not raw.exists():
        return {
            "status": "INCOMPLETE",
            "errors": ["canonical raw attempts are not present"],
            "dataset": dataset_receipt,
            "pair_audit": str(pair_audit_path),
        }

    canonical = canonicalize_attempts(read_attempts(raw))
    expected_ids = {s.id for s in read_scenarios(canonical_dataset)}
    actual_ids = set(canonical["scenario_id"].astype(str))
    if actual_ids != expected_ids:
        errors.append(
            f"canonical result ids mismatch: missing={len(expected_ids-actual_ids)} "
            f"extra={len(actual_ids-expected_ids)}"
        )

    _require_column_value(canonical, "dataset_sha256", config.dataset_sha256, errors)
    _require_column_value(canonical, "run_order_sha256", config.run_order_sha256, errors)
    _require_column_value(canonical, "prompt_sha256", prompt_sha256(), errors)
    _require_column_value(canonical, "protocol_version", config.version, errors)
    _require_column_value(canonical, "requested_model", config.judge_model, errors)

    missing = [rel for rel in REQUIRED_DERIVED if not (result_dir / rel).exists()]
    if missing:
        errors.append(f"missing derived evidence: {missing}")

    manifest_path = result_dir / "MANIFEST.json"
    if not manifest_path.exists():
        errors.append("MANIFEST.json missing")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rel, expected_hash in manifest.items():
            path = result_dir / rel
            if not path.exists():
                errors.append(f"manifest file missing: {rel}")
            elif sha256(path) != expected_hash:
                errors.append(f"manifest hash mismatch: {rel}")

    if regenerate and not missing:
        with tempfile.TemporaryDirectory(prefix="probe-scent-verify-") as tmp:
            temp_result = Path(tmp) / "v1"
            (temp_result / "raw").mkdir(parents=True)
            (temp_result / "raw/attempts.jsonl").write_bytes(raw.read_bytes())
            analyze(
                raw_path=temp_result / "raw/attempts.jsonl",
                dataset_path=canonical_dataset,
                output_dir=temp_result,
                bootstrap_samples=config.analysis.bootstrap_samples,
                bootstrap_seed=config.analysis.bootstrap_seed,
                permutation_samples=config.analysis.permutation_samples,
                permutation_seed=config.analysis.permutation_seed,
            )
            make_figures(
                temp_result / "raw/attempts.jsonl",
                canonical_dataset,
                temp_result / "figures",
            )
            for rel in REQUIRED_DERIVED:
                if sha256(temp_result / rel) != sha256(result_dir / rel):
                    errors.append(f"regeneration mismatch: {rel}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "dataset": dataset_receipt,
        "pair_audit": str(pair_audit_path),
        "canonical_rows": int(len(canonical)),
        "expected_rows": int(len(expected_ids)),
        "canonical_model": config.judge_model,
        "protocol_version": config.version,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify or manifest Probe Scent v1 evidence.")
    parser.add_argument("--config", default="configs/v1.yaml")
    parser.add_argument("--result-dir", default="results/v1")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--no-regenerate", action="store_true")
    args = parser.parse_args()
    result_dir = Path(args.result_dir)
    if args.write_manifest:
        manifest = build_manifest(result_dir, result_dir / "MANIFEST.json")
        print(json.dumps({"manifest_files": len(manifest)}, indent=2))
        return
    receipt = verify_artifact(
        Path(args.config), result_dir=result_dir, regenerate=not args.no_regenerate
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if receipt["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
