import json
from pathlib import Path
from typing import Any

from probe_scent.artifact import verify_artifact
from probe_scent.config import load_config
from probe_scent.dataset import read_scenarios
from probe_scent.prompts import prompt_sha256


def _raw_row(config: Any, scenario_id: str) -> dict[str, object]:
    return {
        "scenario_id": scenario_id,
        "attempt_no": 1,
        "retry_index": 0,
        "status": "ok",
        "score": 50,
        "confidence": 90,
        "judge_backend": config.judge_backend,
        "backend_version": "0.12.0-test",
        "requested_model": config.judge_model,
        "response_model": config.judge_model,
        "model_digest": f"{config.judge_model_digest_prefix}abcdef",
        "model_size_bytes": 123,
        "response_created_at": "2026-08-09T00:00:00Z",
        "total_duration_ns": 100,
        "prompt_eval_count": 10,
        "eval_count": 8,
        "prompt_sha256": prompt_sha256(),
        "dataset_sha256": config.dataset_sha256,
        "run_order_sha256": config.run_order_sha256,
        "protocol_version": config.version,
        "temperature": config.temperature,
        "inference_seed": config.inference_seed,
        "context_length": config.context_length,
        "think": config.think,
        "run_id": "test-run",
    }


def _write_complete_raw(config: Any, raw_path: Path, mutation: Any) -> None:
    rows = []
    for scenario in read_scenarios(Path(config.canonical_dataset_path)):
        row = _raw_row(config, scenario.id)
        mutation(row)
        rows.append(row)
    raw_path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_verifier_rejects_wrong_canonical_model(tmp_path: Path) -> None:
    config = load_config(Path("configs/v1.yaml"))
    result_dir = tmp_path / "v1"
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True)

    def mutate(row: dict[str, object]) -> None:
        row["requested_model"] = "wrong-model"
        row["response_model"] = "wrong-model"

    _write_complete_raw(config, raw_dir / "attempts.jsonl", mutate)
    receipt = verify_artifact(Path("configs/v1.yaml"), result_dir, regenerate=False)

    assert receipt["status"] == "FAIL"
    assert any("wrong requested_model" in error for error in receipt["errors"])


def test_verifier_rejects_wrong_protocol_version(tmp_path: Path) -> None:
    config = load_config(Path("configs/v1.yaml"))
    result_dir = tmp_path / "v1"
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True)

    def mutate(row: dict[str, object]) -> None:
        row["protocol_version"] = "v0-bad"

    _write_complete_raw(config, raw_dir / "attempts.jsonl", mutate)
    receipt = verify_artifact(Path("configs/v1.yaml"), result_dir, regenerate=False)

    assert receipt["status"] == "FAIL"
    assert any("wrong protocol_version" in error for error in receipt["errors"])


def test_verifier_rejects_wrong_model_digest(tmp_path: Path) -> None:
    config = load_config(Path("configs/v1.yaml"))
    result_dir = tmp_path / "v1"
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True)

    def mutate(row: dict[str, object]) -> None:
        row["model_digest"] = "deadbeef"

    _write_complete_raw(config, raw_dir / "attempts.jsonl", mutate)
    receipt = verify_artifact(Path("configs/v1.yaml"), result_dir, regenerate=False)

    assert receipt["status"] == "FAIL"
    assert any("wrong model_digest" in error for error in receipt["errors"])
