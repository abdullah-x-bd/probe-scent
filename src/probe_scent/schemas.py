from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Condition = Literal[
    "control",
    "benign_neat",
    "messy_temptation",
    "neat_temptation",
    "explicit_eval",
]


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
