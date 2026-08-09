import csv
import json
from pathlib import Path

from probe_scent.analyze import analyze

CONDITIONS = ["control", "benign_neat", "messy_temptation", "neat_temptation", "explicit_eval"]


def test_analysis_recovers_known_paired_effect(tmp_path: Path) -> None:
    dataset = tmp_path / "scenarios.jsonl"
    raw = tmp_path / "attempts.jsonl"
    rows = []
    attempts = []
    scores = {
        "control": 5,
        "benign_neat": 7,
        "messy_temptation": 10,
        "neat_temptation": 60,
        "explicit_eval": 95,
    }
    for pair_index in range(1, 7):
        pair_id = f"pair_{pair_index}"
        for condition in CONDITIONS:
            scenario_id = f"{pair_id}_{condition}"
            rows.append({
                "id": scenario_id, "pair_id": pair_id, "base_task_id": pair_id,
                "domain": "domain_a" if pair_index <= 3 else "domain_b",
                "condition": condition, "approved_file": "approved.txt",
                "tempting_file": "tempting.txt" if condition in {"messy_temptation", "neat_temptation", "explicit_eval"} else None,
                "text": "synthetic scenario",
            })
            attempts.append({
                "scenario_id": scenario_id, "attempt_no": 1, "retry_index": 0,
                "status": "ok", "score": scores[condition] + pair_index, "confidence": 90,
                "requested_model": "test-model", "response_model": "test-model",
                "response_id": scenario_id, "prompt_sha256": "prompt",
                "dataset_sha256": "dataset", "run_order_sha256": "order",
                "protocol_version": "test", "run_id": "run",
            })
    dataset.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
    raw.write_text("\n".join(json.dumps(x) for x in attempts) + "\n", encoding="utf-8")
    out = tmp_path / "out"
    result = analyze(raw, dataset, out, bootstrap_samples=500, bootstrap_seed=1,
                     permutation_samples=1000, permutation_seed=1)
    primary = result["effects"]["primary_neat_minus_messy"]
    assert primary["n_pairs"] == 6
    assert primary["mean_difference"] == 50.0
    interaction = result["effects"]["interaction"]
    assert interaction["mean_difference_in_differences"] == 48.0
    assert (out / "tables/condition_summary.csv").exists()
    with (out / "tables/paired_effects.csv").open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 4
