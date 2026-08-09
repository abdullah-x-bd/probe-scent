import json
from pathlib import Path

from probe_scent.artifact import verify_artifact
from probe_scent.config import load_config
from probe_scent.dataset import read_scenarios
from probe_scent.prompts import prompt_sha256


def test_verifier_rejects_wrong_canonical_model(tmp_path: Path) -> None:
    config = load_config(Path("configs/v1.yaml"))
    result_dir = tmp_path / "v1"
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True)

    rows = []
    for scenario in read_scenarios(Path(config.canonical_dataset_path)):
        rows.append({
            "scenario_id": scenario.id,
            "attempt_no": 1,
            "retry_index": 0,
            "status": "ok",
            "score": 50,
            "confidence": 90,
            "requested_model": "wrong-model",
            "response_model": "wrong-model",
            "response_id": f"response-{scenario.id}",
            "prompt_sha256": prompt_sha256(),
            "dataset_sha256": config.dataset_sha256,
            "run_order_sha256": config.run_order_sha256,
            "protocol_version": config.version,
            "run_id": "test-run",
        })

    (raw_dir / "attempts.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )

    receipt = verify_artifact(Path("configs/v1.yaml"), result_dir, regenerate=False)

    assert receipt["status"] == "FAIL"
    assert any("wrong requested_model" in error for error in receipt["errors"])


def test_verifier_rejects_wrong_protocol_version(tmp_path: Path) -> None:
    config = load_config(Path("configs/v1.yaml"))
    result_dir = tmp_path / "v1"
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True)

    rows = []
    for scenario in read_scenarios(Path(config.canonical_dataset_path)):
        rows.append({
            "scenario_id": scenario.id,
            "attempt_no": 1,
            "retry_index": 0,
            "status": "ok",
            "score": 50,
            "confidence": 90,
            "requested_model": config.judge_model,
            "response_model": config.judge_model,
            "response_id": f"response-{scenario.id}",
            "prompt_sha256": prompt_sha256(),
            "dataset_sha256": config.dataset_sha256,
            "run_order_sha256": config.run_order_sha256,
            "protocol_version": "v0-bad",
            "run_id": "test-run",
        })

    (raw_dir / "attempts.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )

    receipt = verify_artifact(Path("configs/v1.yaml"), result_dir, regenerate=False)

    assert receipt["status"] == "FAIL"
    assert any("wrong protocol_version" in error for error in receipt["errors"])
