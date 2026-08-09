from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int
    base_delay_seconds: float


@dataclass(frozen=True)
class AnalysisConfig:
    bootstrap_seed: int
    bootstrap_samples: int
    permutation_seed: int
    permutation_samples: int


@dataclass(frozen=True)
class ProtocolConfig:
    version: str
    dataset_path: Path
    canonical_dataset_path: Path
    dataset_sha256: str
    run_order_sha256: str
    run_order_seed: int
    judge_backend: str
    judge_model: str
    judge_model_digest_prefix: str
    judge_prompt_version: str
    max_output_tokens: int
    temperature: float
    inference_seed: int
    context_length: int
    think: bool
    retry: RetryConfig
    analysis: AnalysisConfig
    primary_contrast: str
    secondary_contrasts: tuple[str, ...]


def load_config(path: Path) -> ProtocolConfig:
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ProtocolConfig(
        version=str(raw["version"]),
        dataset_path=Path(raw["dataset_path"]),
        canonical_dataset_path=Path(raw["canonical_dataset_path"]),
        dataset_sha256=str(raw["dataset_sha256"]),
        run_order_sha256=str(raw["run_order_sha256"]),
        run_order_seed=int(raw["run_order_seed"]),
        judge_backend=str(raw["judge_backend"]),
        judge_model=str(raw["judge_model"]),
        judge_model_digest_prefix=str(raw["judge_model_digest_prefix"]),
        judge_prompt_version=str(raw["judge_prompt_version"]),
        max_output_tokens=int(raw["max_output_tokens"]),
        temperature=float(raw["temperature"]),
        inference_seed=int(raw["inference_seed"]),
        context_length=int(raw["context_length"]),
        think=bool(raw["think"]),
        retry=RetryConfig(**raw["retry"]),
        analysis=AnalysisConfig(**raw["analysis"]),
        primary_contrast=str(raw["primary_contrast"]),
        secondary_contrasts=tuple(raw["secondary_contrasts"]),
    )
