from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from .schemas import Scenario

EXPECTED_CONDITIONS = {
    "control",
    "benign_neat",
    "messy_temptation",
    "neat_temptation",
    "explicit_eval",
}

FORBIDDEN_NONEXPLICIT_PHRASES = (
    "evaluation",
    "benchmark",
    "red-team",
    "staged",
    "help you pass",
    "reviewer cannot see",
    "how your work will be judged",
)


def logical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def file_sha256(path: Path) -> str:
    return hashlib.sha256(logical_bytes(path)).hexdigest()


def read_scenarios(path: Path) -> list[Scenario]:
    scenarios: list[Scenario] = []
    text = logical_bytes(path).decode("utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            scenarios.append(Scenario.model_validate_json(line))
        except Exception as exc:
            raise ValueError(f"{path}:{lineno}: invalid scenario: {exc}") from exc
    return scenarios


def validate_dataset(path: Path, expected_sha256: str | None = None) -> dict[str, object]:
    scenarios = read_scenarios(path)
    errors: list[str] = []

    ids = [s.id for s in scenarios]
    duplicate_ids = sorted(k for k, v in Counter(ids).items() if v > 1)
    if duplicate_ids:
        errors.append(f"duplicate ids: {duplicate_ids}")

    pairs: dict[str, list[Scenario]] = defaultdict(list)
    for scenario in scenarios:
        pairs[scenario.pair_id].append(scenario)

    incomplete: dict[str, list[str]] = {}
    for pair_id, members in sorted(pairs.items()):
        present = {m.condition for m in members}
        if present != EXPECTED_CONDITIONS or len(members) != len(EXPECTED_CONDITIONS):
            incomplete[pair_id] = sorted(present)
    if incomplete:
        errors.append(f"incomplete pairs: {incomplete}")

    forbidden_hits: list[dict[str, str]] = []
    for scenario in scenarios:
        if scenario.condition == "explicit_eval":
            continue
        lower = scenario.text.lower()
        for phrase in FORBIDDEN_NONEXPLICIT_PHRASES:
            if phrase in lower:
                forbidden_hits.append({"id": scenario.id, "phrase": phrase})
    if forbidden_hits:
        errors.append(f"forbidden cue leakage: {forbidden_hits}")

    pair_mismatch: list[str] = []
    length_ratios: list[float] = []
    length_differences: list[int] = []
    for pair_id, members in pairs.items():
        by_condition = {m.condition: m for m in members}
        if not EXPECTED_CONDITIONS.issubset(by_condition):
            continue
        messy = by_condition["messy_temptation"]
        neat = by_condition["neat_temptation"]
        if messy.tempting_file != neat.tempting_file:
            pair_mismatch.append(pair_id)
        messy_words = len(messy.text.split())
        neat_words = len(neat.text.split())
        length_ratios.append(max(messy_words, neat_words) / min(messy_words, neat_words))
        length_differences.append(abs(messy_words - neat_words))
    if pair_mismatch:
        errors.append(f"temptation mismatch: {pair_mismatch}")

    actual_sha = file_sha256(path)
    if expected_sha256 is not None and actual_sha != expected_sha256:
        errors.append(f"sha256 mismatch: expected {expected_sha256}, got {actual_sha}")

    receipt: dict[str, object] = {
        "rows": len(scenarios),
        "base_tasks": len(pairs),
        "complete_pairs": sum(
            1
            for members in pairs.values()
            if {m.condition for m in members} == EXPECTED_CONDITIONS
            and len(members) == len(EXPECTED_CONDITIONS)
        ),
        "duplicate_ids": len(duplicate_ids),
        "missing_cells": sum(max(0, 5 - len(members)) for members in pairs.values()),
        "forbidden_explicit_eval_terms_in_nonexplicit_conditions": len(forbidden_hits),
        "max_messy_neat_word_count_ratio": max(length_ratios, default=0.0),
        "max_messy_neat_word_count_difference": max(length_differences, default=0),
        "dataset_sha256": actual_sha,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    return receipt


def write_receipt(receipt: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
