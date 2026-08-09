from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analyze import canonicalize_attempts, read_attempts
from .config import load_config
from .dataset import read_scenarios

matplotlib.rcParams["svg.hashsalt"] = "probe-scent-v1"

ORDER = [
    "control",
    "benign_neat",
    "messy_temptation",
    "neat_temptation",
    "explicit_eval",
]


def load_merged(raw_path: Path, dataset_path: Path) -> pd.DataFrame:
    canonical = canonicalize_attempts(read_attempts(raw_path))
    dataset = pd.DataFrame([s.model_dump() for s in read_scenarios(dataset_path)])
    return dataset.merge(
        canonical[["scenario_id", "score"]],
        left_on="id",
        right_on="scenario_id",
        how="left",
        validate="one_to_one",
    )


def make_figures(raw_path: Path, dataset_path: Path, output_dir: Path) -> None:
    df = load_merged(raw_path, dataset_path)
    if df["score"].isna().any():
        missing = int(df["score"].isna().sum())
        raise ValueError(f"Canonical figures require complete results; {missing} rows are missing.")
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [df.loc[df["condition"] == condition, "score"].to_numpy() for condition in ORDER]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data, tick_labels=[x.replace("_", " ") for x in ORDER], showmeans=True)
    for x, values in enumerate(data, start=1):
        ax.scatter([x] * len(values), values, alpha=0.45, s=14)
    ax.set_ylabel("Evaluation-likeness score")
    ax.set_ylim(-5, 105)
    ax.set_title("Probe Scent v1: score distributions by condition")
    fig.tight_layout()
    fig.savefig(output_dir / "figure_1_conditions.svg", metadata={"Date": None})
    plt.close(fig)

    wide = df.pivot(index="pair_id", columns="condition", values="score")
    fig, ax = plt.subplots(figsize=(7, 7))
    for _, row in wide.iterrows():
        ax.plot([0, 1], [row["messy_temptation"], row["neat_temptation"]], marker="o", alpha=0.45)
    ax.set_xticks([0, 1], ["messy temptation", "neat temptation"])
    ax.set_ylabel("Evaluation-likeness score")
    ax.set_ylim(-5, 105)
    ax.set_title("Matched primary contrast")
    fig.tight_layout()
    fig.savefig(output_dir / "figure_2_paired.svg", metadata={"Date": None})
    plt.close(fig)

    pair_meta = df[["pair_id", "domain"]].drop_duplicates()
    pair_scores = wide.reset_index().merge(pair_meta, on="pair_id", how="left")
    pair_scores["effect"] = pair_scores["neat_temptation"] - pair_scores["messy_temptation"]
    domains = pair_scores.groupby("domain")["effect"].mean().sort_values()
    domain_labels = [str(value) for value in domains.index]
    domain_values = np.asarray(domains.to_numpy(), dtype=float)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(domain_labels, domain_values)
    ax.axvline(0, linewidth=1)
    ax.set_xlabel("Mean neat minus messy score")
    ax.set_title("Primary effect by domain")
    fig.tight_layout()
    fig.savefig(output_dir / "figure_3_domains.svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Probe Scent v1 figures.")
    parser.add_argument("--config", default="configs/v1.yaml")
    parser.add_argument("--raw", default="results/v1/raw/attempts.jsonl")
    parser.add_argument("--output-dir", default="results/v1/figures")
    args = parser.parse_args()
    config = load_config(Path(args.config))
    make_figures(Path(args.raw), Path(config.canonical_dataset_path), Path(args.output_dir))


if __name__ == "__main__":
    main()
