import json
from pathlib import Path

from probe_scent.config import load_config
from probe_scent.dataset import file_sha256, read_scenarios, validate_dataset


def test_canonical_dataset_is_balanced_and_frozen() -> None:
    config = load_config(Path("configs/v1.yaml"))
    canonical = Path(config.canonical_dataset_path)
    receipt = validate_dataset(canonical, expected_sha256=config.dataset_sha256)

    assert receipt["status"] == "PASS"
    assert receipt["rows"] == 150
    assert receipt["base_tasks"] == 30
    assert receipt["complete_pairs"] == 30
    assert receipt["duplicate_ids"] == 0
    assert receipt["missing_cells"] == 0
    assert receipt["forbidden_explicit_eval_terms_in_nonexplicit_conditions"] == 0
    assert receipt["max_messy_neat_word_count_difference"] <= 3
    assert receipt["max_messy_neat_word_count_ratio"] < 1.07


def test_run_order_is_a_frozen_permutation_of_canonical_dataset() -> None:
    config = load_config(Path("configs/v1.yaml"))
    canonical = read_scenarios(Path(config.canonical_dataset_path))
    run_order = read_scenarios(Path(config.dataset_path))

    assert file_sha256(Path(config.dataset_path)) == config.run_order_sha256
    assert len(run_order) == 150
    assert {scenario.id for scenario in run_order} == {scenario.id for scenario in canonical}
    assert [scenario.id for scenario in run_order] != [scenario.id for scenario in canonical]


def test_manual_pair_audit_is_complete_and_passing() -> None:
    receipt = json.loads(Path("data/v1/pair_audit.json").read_text(encoding="utf-8"))

    assert receipt["status"] == "PASS"
    assert receipt["pairs_reviewed"] == 30
    assert len(receipt["pairs"]) == 30
    assert all(pair["manual_review"] == "PASS" for pair in receipt["pairs"])
    assert all(pair["same_tempting_file"] for pair in receipt["pairs"])
