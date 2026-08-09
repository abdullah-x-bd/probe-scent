from __future__ import annotations

import argparse
import json
import random
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .backends import BackendIdentity, OllamaBackend
from .config import load_config
from .dataset import file_sha256, read_scenarios
from .prompts import JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE, prompt_sha256
from .schemas import JudgeOutput, Scenario


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def parse_json_object(text: str) -> JudgeOutput:
    candidate = text.strip()
    try:
        return JudgeOutput.model_validate_json(candidate)
    except ValidationError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end <= start:
            raise
        return JudgeOutput.model_validate_json(candidate[start : end + 1])


def load_latest_attempts(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        scenario_id = str(row["scenario_id"])
        latest[scenario_id] = row
    return latest


def transient_error(exc: Exception) -> bool:
    text = repr(exc).lower()
    markers = (
        "timeout",
        "temporarily",
        "connection",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504",
    )
    return any(marker in text for marker in markers)


def _backend_identity(config: Any) -> tuple[OllamaBackend, BackendIdentity]:
    if config.judge_backend != "ollama":
        raise RuntimeError(f"Unsupported frozen judge backend: {config.judge_backend}")
    backend = OllamaBackend()
    identity = backend.identity(config.judge_model, config.judge_model_digest_prefix)
    return backend, identity


def run_one(
    backend: OllamaBackend,
    scenario: Scenario,
    config: Any,
) -> tuple[JudgeOutput, dict[str, Any]]:
    user_prompt = JUDGE_USER_TEMPLATE.format(scenario_text=scenario.text)
    response = backend.judge(
        scenario=scenario,
        model=config.judge_model,
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperature,
        seed=config.inference_seed,
        context_length=config.context_length,
        think=config.think,
    )
    parsed = parse_json_object(response.content)
    meta: dict[str, Any] = {
        "response_model": response.model,
        "response_created_at": response.created_at,
        "raw_output": response.content,
        "total_duration_ns": response.total_duration_ns,
        "prompt_eval_count": response.prompt_eval_count,
        "eval_count": response.eval_count,
    }
    return parsed, meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the frozen Probe Scent v1 judge protocol.")
    parser.add_argument("--config", default="configs/v1.yaml")
    parser.add_argument("--output", default="results/v1/raw/attempts.jsonl")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()

    config = load_config(Path(args.config))
    input_path = Path(config.dataset_path)
    actual_run_sha = file_sha256(input_path)
    if actual_run_sha != config.run_order_sha256:
        raise SystemExit(
            f"Run-order hash mismatch. Expected {config.run_order_sha256}, got {actual_run_sha}."
        )

    scenarios = read_scenarios(input_path)
    scenarios = scenarios[args.offset :]
    if args.limit is not None:
        scenarios = scenarios[: args.limit]

    output_path = Path(args.output)
    if output_path.exists() and not args.resume and not args.overwrite:
        raise SystemExit(
            f"{output_path} already exists. Use --resume to continue or --overwrite to restart."
        )
    if args.overwrite:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("", encoding="utf-8")

    latest = load_latest_attempts(output_path) if args.resume else {}
    completed = {
        scenario_id
        for scenario_id, row in latest.items()
        if row.get("status") == "ok" and isinstance(row.get("score"), int)
    }

    if args.dry_run:
        pending = [scenario.id for scenario in scenarios if scenario.id not in completed]
        print(
            json.dumps(
                {
                    "protocol_version": config.version,
                    "dataset_sha256": config.dataset_sha256,
                    "run_order_sha256": actual_run_sha,
                    "backend": config.judge_backend,
                    "model": config.judge_model,
                    "model_digest_prefix": config.judge_model_digest_prefix,
                    "temperature": config.temperature,
                    "inference_seed": config.inference_seed,
                    "context_length": config.context_length,
                    "think": config.think,
                    "selected_rows": len(scenarios),
                    "already_completed": len(completed),
                    "pending": len(pending),
                    "pending_ids": pending[:20],
                },
                indent=2,
            )
        )
        return

    backend, identity = _backend_identity(config)
    run_id = f"{config.version}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    p_hash = prompt_sha256()

    for scenario in scenarios:
        if scenario.id in completed:
            continue
        previous = latest.get(scenario.id)
        attempt_no = int(previous.get("attempt_no", 0)) + 1 if previous else 1

        last_error: str | None = None
        for retry_index in range(config.retry.max_attempts):
            started = datetime.now(UTC).isoformat()
            try:
                parsed, response_meta = run_one(backend, scenario, config)
                row: dict[str, Any] = {
                    "scenario_id": scenario.id,
                    "pair_id": scenario.pair_id,
                    "base_task_id": scenario.base_task_id,
                    "domain": scenario.domain,
                    "condition": scenario.condition,
                    "attempt_no": attempt_no,
                    "retry_index": retry_index,
                    "status": "ok",
                    "score": parsed.score,
                    "label": parsed.label,
                    "primary_cue": parsed.primary_cue,
                    "confidence": parsed.confidence,
                    "judge_backend": identity.backend,
                    "backend_version": identity.backend_version,
                    "requested_model": identity.model,
                    "response_model": response_meta["response_model"],
                    "model_digest": identity.model_digest,
                    "model_size_bytes": identity.model_size_bytes,
                    "response_created_at": response_meta["response_created_at"],
                    "total_duration_ns": response_meta["total_duration_ns"],
                    "prompt_eval_count": response_meta["prompt_eval_count"],
                    "eval_count": response_meta["eval_count"],
                    "raw_output": response_meta["raw_output"],
                    "prompt_sha256": p_hash,
                    "dataset_sha256": config.dataset_sha256,
                    "run_order_sha256": actual_run_sha,
                    "protocol_version": config.version,
                    "temperature": config.temperature,
                    "inference_seed": config.inference_seed,
                    "context_length": config.context_length,
                    "think": config.think,
                    "run_id": run_id,
                    "started_at_utc": started,
                    "finished_at_utc": datetime.now(UTC).isoformat(),
                    "run_error": None,
                }
                append_jsonl(output_path, row)
                latest[scenario.id] = row
                print(f"{scenario.id} score={parsed.score}")
                break
            except Exception as exc:  # noqa: BLE001
                last_error = repr(exc)
                row = {
                    "scenario_id": scenario.id,
                    "pair_id": scenario.pair_id,
                    "base_task_id": scenario.base_task_id,
                    "domain": scenario.domain,
                    "condition": scenario.condition,
                    "attempt_no": attempt_no,
                    "retry_index": retry_index,
                    "status": "error",
                    "score": None,
                    "label": None,
                    "primary_cue": None,
                    "confidence": None,
                    "judge_backend": identity.backend,
                    "backend_version": identity.backend_version,
                    "requested_model": identity.model,
                    "response_model": None,
                    "model_digest": identity.model_digest,
                    "model_size_bytes": identity.model_size_bytes,
                    "response_created_at": None,
                    "total_duration_ns": None,
                    "prompt_eval_count": None,
                    "eval_count": None,
                    "raw_output": None,
                    "prompt_sha256": p_hash,
                    "dataset_sha256": config.dataset_sha256,
                    "run_order_sha256": actual_run_sha,
                    "protocol_version": config.version,
                    "temperature": config.temperature,
                    "inference_seed": config.inference_seed,
                    "context_length": config.context_length,
                    "think": config.think,
                    "run_id": run_id,
                    "started_at_utc": started,
                    "finished_at_utc": datetime.now(UTC).isoformat(),
                    "run_error": last_error,
                }
                append_jsonl(output_path, row)
                latest[scenario.id] = row
                print(f"{scenario.id} ERROR {last_error}")
                if not transient_error(exc) or retry_index + 1 >= config.retry.max_attempts:
                    break
                delay = config.retry.base_delay_seconds * (2**retry_index)
                delay *= 0.9 + 0.2 * random.random()
                time.sleep(delay)

        if latest.get(scenario.id, {}).get("status") != "ok":
            print(f"{scenario.id} remains incomplete after retries: {last_error}")

    valid = sum(
        1
        for row in load_latest_attempts(output_path).values()
        if row.get("status") == "ok" and isinstance(row.get("score"), int)
    )
    print(f"valid_latest_results={valid}/{len(read_scenarios(input_path))}")


if __name__ == "__main__":
    main()
