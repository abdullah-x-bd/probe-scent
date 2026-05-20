import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize probe-scent scores.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    rows = list(read_jsonl(Path(args.input)))
    if not rows:
        raise SystemExit("No rows found.")

    df = pd.DataFrame(rows)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["confidence"] = pd.to_numeric(df.get("confidence"), errors="coerce")

    summary = (
        df.groupby(["mode", "condition"], dropna=False)
        .agg(
            n=("score", "count"),
            mean_score=("score", "mean"),
            median_score=("score", "median"),
            min_score=("score", "min"),
            max_score=("score", "max"),
            mean_confidence=("confidence", "mean"),
        )
        .reset_index()
        .sort_values(["mode", "mean_score"])
    )

    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
