from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import load_config
from .dataset import read_scenarios


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


CONTRASTS = {
    "primary_neat_minus_messy": ("neat_temptation", "messy_temptation"),
    "benign_neat_minus_control": ("benign_neat", "control"),
    "explicit_minus_control": ("explicit_eval", "control"),
}


def read_attempts(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    if not rows:
        raise ValueError("No raw attempts found.")
    return pd.DataFrame(rows)


def canonicalize_attempts(attempts: pd.DataFrame) -> pd.DataFrame:
    required = {"scenario_id", "attempt_no", "retry_index", "status", "score"}
    missing = required - set(attempts.columns)
    if missing:
        raise ValueError(f"Missing required raw-result columns: {sorted(missing)}")
    ordered = attempts.sort_values(["scenario_id", "attempt_no", "retry_index"], kind="stable")
    valid = ordered[
        (ordered["status"] == "ok") & pd.to_numeric(ordered["score"], errors="coerce").notna()
    ].copy()
    valid["score"] = pd.to_numeric(valid["score"], errors="raise").astype(float)
    canonical = valid.groupby("scenario_id", as_index=False, sort=True).tail(1)
    return canonical.sort_values("scenario_id").reset_index(drop=True)


def bootstrap_ci(values: np.ndarray, samples: int, seed: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    batch = 1000
    means: list[np.ndarray] = []
    remaining = samples
    while remaining > 0:
        n = min(batch, remaining)
        idx = rng.integers(0, len(values), size=(n, len(values)))
        means.append(values[idx].mean(axis=1))
        remaining -= n
    dist = np.concatenate(means)
    low, high = np.quantile(dist, [0.025, 0.975])
    return float(low), float(high)


def sign_flip_pvalue(values: np.ndarray, samples: int, seed: int) -> float:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return float("nan")
    observed = abs(values.mean())
    rng = np.random.default_rng(seed)
    exceed = 1
    total = 1
    batch = 2000
    remaining = samples
    while remaining > 0:
        n = min(batch, remaining)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(n, len(values)))
        permuted = np.abs((signs * values).mean(axis=1))
        exceed += int(np.count_nonzero(permuted >= observed))
        total += n
        remaining -= n
    return exceed / total


def paired_effect(
    wide: pd.DataFrame,
    high: str,
    low: str,
    bootstrap_samples: int,
    bootstrap_seed: int,
    permutation_samples: int,
    permutation_seed: int,
) -> dict[str, float | int]:
    subset = wide[[high, low]].dropna()
    diffs = (subset[high] - subset[low]).to_numpy(dtype=float)
    ci_low, ci_high = bootstrap_ci(diffs, bootstrap_samples, bootstrap_seed)
    p = sign_flip_pvalue(diffs, permutation_samples, permutation_seed)
    sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else float("nan")
    dz = float(np.mean(diffs) / sd) if sd and np.isfinite(sd) else float("nan")
    return {
        "n_pairs": len(diffs),
        "mean_difference": float(np.mean(diffs)) if len(diffs) else float("nan"),
        "median_difference": float(np.median(diffs)) if len(diffs) else float("nan"),
        "std_difference": sd,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "permutation_p": float(p),
        "cohens_dz": dz,
    }


def analyze(
    raw_path: Path,
    dataset_path: Path,
    output_dir: Path,
    bootstrap_samples: int,
    bootstrap_seed: int,
    permutation_samples: int,
    permutation_seed: int,
) -> dict[str, Any]:
    attempts = read_attempts(raw_path)
    canonical = canonicalize_attempts(attempts)
    dataset = pd.DataFrame([s.model_dump() for s in read_scenarios(dataset_path)])
    merged = dataset.merge(
        canonical[[
            "scenario_id", "score", "confidence", "requested_model", "response_model",
            "response_id", "prompt_sha256", "dataset_sha256", "run_order_sha256",
            "protocol_version", "run_id",
        ]],
        left_on="id", right_on="scenario_id", how="left", validate="one_to_one",
    )
    merged["score"] = pd.to_numeric(merged["score"], errors="coerce")
    complete_rows = int(merged["score"].notna().sum())
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = output_dir / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    canonical.to_json(output_dir / "canonical_results.jsonl", orient="records", lines=True)

    summary = merged.groupby("condition", observed=False)["score"].agg(
        ["count", "mean", "std", "median", "min", "max"]
    ).reset_index()
    q = merged.groupby("condition", observed=False)["score"].quantile([0.25, 0.75]).unstack()
    q.columns = ["q25", "q75"]
    summary = summary.merge(q.reset_index(), on="condition", how="left")
    summary["iqr"] = summary["q75"] - summary["q25"]
    summary.to_csv(tables / "condition_summary.csv", index=False)

    wide = merged.pivot(index="pair_id", columns="condition", values="score")
    effects: dict[str, Any] = {}
    for index, (name, (high, low)) in enumerate(CONTRASTS.items()):
        effects[name] = paired_effect(
            wide, high, low, bootstrap_samples, bootstrap_seed + index,
            permutation_samples, permutation_seed + index,
        )

    interaction_rows = wide[[
        "neat_temptation", "messy_temptation", "benign_neat", "control"
    ]].dropna()
    interaction_values = (
        interaction_rows["neat_temptation"] - interaction_rows["messy_temptation"]
        - interaction_rows["benign_neat"] + interaction_rows["control"]
    ).to_numpy(dtype=float)
    int_low, int_high = bootstrap_ci(interaction_values, bootstrap_samples, bootstrap_seed + 99)
    effects["interaction"] = {
        "n_pairs": len(interaction_values),
        "mean_difference_in_differences": float(np.mean(interaction_values))
        if len(interaction_values) else float("nan"),
        "median_difference_in_differences": float(np.median(interaction_values))
        if len(interaction_values) else float("nan"),
        "ci95_low": int_low,
        "ci95_high": int_high,
        "permutation_p": sign_flip_pvalue(
            interaction_values, permutation_samples, permutation_seed + 99
        ),
    }
    pd.DataFrame.from_dict(effects, orient="index").reset_index(
        names="contrast"
    ).to_csv(tables / "paired_effects.csv", index=False)

    pair_meta = merged[["pair_id", "domain"]].drop_duplicates()
    pair_scores = wide.reset_index().merge(pair_meta, on="pair_id", how="left")
    pair_scores["primary_effect"] = (
        pair_scores["neat_temptation"] - pair_scores["messy_temptation"]
    )
    domain_effects = pair_scores.groupby("domain", observed=False)["primary_effect"].agg(
        ["count", "mean", "std", "median", "min", "max"]
    ).reset_index().sort_values("domain")
    domain_effects.to_csv(tables / "domain_effects.csv", index=False)

    sensitivity_rows: list[dict[str, Any]] = []
    for domain in sorted(pair_scores["domain"].dropna().unique()):
        vals = pair_scores.loc[
            pair_scores["domain"] != domain, "primary_effect"
        ].dropna().to_numpy()
        sensitivity_rows.append({
            "analysis": "leave_one_domain_out", "excluded": domain,
            "n_pairs": len(vals),
            "mean_primary_effect": float(np.mean(vals)) if len(vals) else float("nan"),
        })
    for pair_id in pair_scores["pair_id"]:
        vals = pair_scores.loc[
            pair_scores["pair_id"] != pair_id, "primary_effect"
        ].dropna().to_numpy()
        sensitivity_rows.append({
            "analysis": "leave_one_pair_out", "excluded": pair_id,
            "n_pairs": len(vals),
            "mean_primary_effect": float(np.mean(vals)) if len(vals) else float("nan"),
        })
    pd.DataFrame(sensitivity_rows).to_csv(tables / "sensitivity.csv", index=False)

    claims = {
        "H1_neat_vs_messy": {
            "status": "SUPPORTED" if effects["primary_neat_minus_messy"]["ci95_low"] > 0
            else "NOT_SUPPORTED",
            **effects["primary_neat_minus_messy"],
        },
        "H2_neatness_by_temptation_interaction": {
            "status": "SUPPORTED" if effects["interaction"]["ci95_low"] > 0
            else "NOT_SUPPORTED",
            **effects["interaction"],
        },
        "H3_positive_control": {
            "status": "SUPPORTED" if effects["explicit_minus_control"]["ci95_low"] > 0
            else "NOT_SUPPORTED",
            **effects["explicit_minus_control"],
        },
    }
    result: dict[str, Any] = {
        "rows_expected": len(dataset),
        "rows_complete": complete_rows,
        "pairs_expected": int(dataset["pair_id"].nunique()),
        "pairs_with_primary_contrast": int(
            wide[["neat_temptation", "messy_temptation"]].dropna().shape[0]
        ),
        "effects": effects,
        "claims": claims,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(json_safe(result), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "claims.json").write_text(
        json.dumps(json_safe(claims), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Probe Scent v1 raw attempts.")
    parser.add_argument("--config", default="configs/v1.yaml")
    parser.add_argument("--raw", default="results/v1/raw/attempts.jsonl")
    parser.add_argument("--output-dir", default="results/v1")
    args = parser.parse_args()
    config = load_config(Path(args.config))
    result = analyze(
        raw_path=Path(args.raw), dataset_path=Path(config.canonical_dataset_path),
        output_dir=Path(args.output_dir),
        bootstrap_samples=config.analysis.bootstrap_samples,
        bootstrap_seed=config.analysis.bootstrap_seed,
        permutation_samples=config.analysis.permutation_samples,
        permutation_seed=config.analysis.permutation_seed,
    )
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
