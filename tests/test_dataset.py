from pathlib import Path

from probe_scent.dataset import validate_dataset


def test_canonical_dataset_is_balanced_and_frozen() -> None:
    receipt = validate_dataset(
        Path("data/v1/scenarios.jsonl.gz"),
        expected_sha256="077e5e1e350957ea7d4c5697b26e165d91f7e26e5568fc9d381f41b05fcb074a",
    )
    assert receipt["status"] == "PASS"
    assert receipt["rows"] == 150
    assert receipt["base_tasks"] == 30
    assert receipt["complete_pairs"] == 30
    assert receipt["duplicate_ids"] == 0
    assert receipt["forbidden_explicit_eval_terms_in_nonexplicit_conditions"] == 0
    assert receipt["max_messy_neat_word_count_difference"] <= 3
    assert receipt["max_messy_neat_word_count_ratio"] < 1.07
