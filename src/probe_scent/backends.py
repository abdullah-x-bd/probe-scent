from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .schemas import JudgeOutput, Scenario


@dataclass(frozen=True)
class BackendIdentity:
    backend: str
    backend_version: str
    model: str
    model_digest: str
    model_size_bytes: int | None


@dataclass(frozen=True)
class BackendResponse:
    content: str
    model: str
    created_at: str | None
    total_duration_ns: int | None
    prompt_eval_count: int | None
    eval_count: int | None


class OllamaBackend:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        timeout: float = 900.0,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Ollama request failed for {path}: {exc}") from exc

    def identity(self, model: str, digest_prefix: str) -> BackendIdentity:
        version_payload = self._request("GET", "/api/version", timeout=30.0)
        tags_payload = self._request("GET", "/api/tags", timeout=30.0)
        models = tags_payload.get("models", [])
        matching = [row for row in models if row.get("name") == model or row.get("model") == model]
        if len(matching) != 1:
            available = [row.get("name") or row.get("model") for row in models]
            raise RuntimeError(f"Expected exactly one pulled model {model!r}; available={available!r}")
        row = matching[0]
        digest = str(row.get("digest") or "")
        if not digest.startswith(digest_prefix):
            raise RuntimeError(
                f"Model digest mismatch for {model}: expected prefix {digest_prefix}, got {digest}"
            )
        size = row.get("size")
        return BackendIdentity(
            backend="ollama",
            backend_version=str(version_payload.get("version") or "unknown"),
            model=model,
            model_digest=digest,
            model_size_bytes=int(size) if isinstance(size, int) else None,
        )

    def judge(
        self,
        *,
        scenario: Scenario,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
        temperature: float,
        seed: int,
        context_length: int,
        think: bool,
    ) -> BackendResponse:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": think,
            "format": JudgeOutput.model_json_schema(),
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "seed": seed,
                "num_predict": max_output_tokens,
                "num_ctx": context_length,
            },
        }
        result = self._request("POST", "/api/chat", payload=payload)
        message = result.get("message") or {}
        content = str(message.get("content") or "")
        if not content.strip():
            raise RuntimeError(
                f"Ollama returned no final content for {scenario.id}; done_reason={result.get('done_reason')}"
            )
        return BackendResponse(
            content=content,
            model=str(result.get("model") or model),
            created_at=str(result.get("created_at")) if result.get("created_at") else None,
            total_duration_ns=(
                int(result["total_duration"]) if isinstance(result.get("total_duration"), int) else None
            ),
            prompt_eval_count=(
                int(result["prompt_eval_count"])
                if isinstance(result.get("prompt_eval_count"), int)
                else None
            ),
            eval_count=(
                int(result["eval_count"]) if isinstance(result.get("eval_count"), int) else None
            ),
        )
