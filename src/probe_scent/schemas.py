from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

Condition = Literal[
    "control",
    "benign_neat",
    "messy_temptation",
    "neat_temptation",
    "explicit_eval",
]

AttemptStatus = Literal["ok", "error"]


class Scenario(BaseModel):
    id: str
    pair_id: str
    base_task_id: str
    domain: str
    condition: Condition
    approved_file: str
    tempting_file: str | None = None
    text: str


class JudgeOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    label: str = Field(min_length=1, max_length=80)
    primary_cue: str = Field(min_length=1, max_length=160)
    confidence: int = Field(ge=0, le=100)


class AttemptRecord(BaseModel):
    scenario_id: str
    pair_id: str
    base_task_id: str
    domain: str
    condition: Condition
    attempt_no: int = Field(ge=1)
    retry_index: int = Field(ge=0)
    status: AttemptStatus
    score: int | None = Field(default=None, ge=0, le=100)
    label: str | None = None
    primary_cue: str | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    judge_backend: str
    backend_version: str
    requested_model: str
    response_model: str | None
    model_digest: str
    model_size_bytes: int | None = Field(default=None, ge=0)
    response_created_at: str | None
    total_duration_ns: int | None = Field(default=None, ge=0)
    prompt_eval_count: int | None = Field(default=None, ge=0)
    eval_count: int | None = Field(default=None, ge=0)
    raw_output: str | None
    prompt_sha256: str
    dataset_sha256: str
    run_order_sha256: str
    protocol_version: str
    temperature: float
    inference_seed: int
    context_length: int = Field(ge=1)
    think: bool
    run_id: str
    started_at_utc: str
    finished_at_utc: str
    run_error: str | None

    @model_validator(mode="after")
    def validate_status_fields(self) -> Self:
        if self.status == "ok":
            required = {
                "score": self.score,
                "label": self.label,
                "primary_cue": self.primary_cue,
                "confidence": self.confidence,
                "response_model": self.response_model,
                "raw_output": self.raw_output,
            }
            missing = [name for name, value in required.items() if value is None]
            if missing:
                raise ValueError(f"successful attempt is missing fields: {missing}")
            if self.run_error is not None:
                raise ValueError("successful attempt cannot contain run_error")
        elif self.run_error is None:
            raise ValueError("error attempt must contain run_error")
        return self
