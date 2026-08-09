import json
from typing import Any

from probe_scent.backends import OllamaBackend
from probe_scent.schemas import Scenario


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_ollama_identity_and_structured_judge_payload(monkeypatch: Any) -> None:
    observed_chat: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> _FakeResponse:
        assert timeout > 0
        if request.full_url.endswith("/api/version"):
            return _FakeResponse({"version": "0.12.0"})
        if request.full_url.endswith("/api/tags"):
            return _FakeResponse({
                "models": [{
                    "name": "qwen3.5:4b-q4_K_M",
                    "model": "qwen3.5:4b-q4_K_M",
                    "digest": "2a654d98e6fbabcdef",
                    "size": 3400000000,
                }]
            })
        if request.full_url.endswith("/api/chat"):
            observed_chat.update(json.loads(request.data.decode("utf-8")))
            return _FakeResponse({
                "model": "qwen3.5:4b-q4_K_M",
                "created_at": "2026-08-09T00:00:00Z",
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "score": 73,
                        "label": "possibly staged",
                        "primary_cue": "unusually convenient outside file",
                        "confidence": 91,
                    }),
                },
                "total_duration": 123,
                "prompt_eval_count": 42,
                "eval_count": 17,
            })
        raise AssertionError(request.full_url)

    monkeypatch.setattr("probe_scent.backends.urlopen", fake_urlopen)
    backend = OllamaBackend("http://example.test")
    identity = backend.identity("qwen3.5:4b-q4_K_M", "2a654d98e6fb")

    assert identity.backend == "ollama"
    assert identity.backend_version == "0.12.0"
    assert identity.model_digest == "2a654d98e6fbabcdef"

    scenario = Scenario(
        id="s1",
        pair_id="p1",
        base_task_id="b1",
        domain="software engineering",
        condition="neat_temptation",
        approved_file="approved.txt",
        tempting_file="outside.txt",
        text="A short scenario.",
    )
    response = backend.judge(
        scenario=scenario,
        model="qwen3.5:4b-q4_K_M",
        system_prompt="system",
        user_prompt="user",
        max_output_tokens=96,
        temperature=0.0,
        seed=20260809,
        context_length=2048,
        think=False,
    )

    assert response.model == "qwen3.5:4b-q4_K_M"
    assert json.loads(response.content)["score"] == 73
    assert observed_chat["stream"] is False
    assert observed_chat["think"] is False
    assert observed_chat["options"]["temperature"] == 0.0
    assert observed_chat["options"]["seed"] == 20260809
    assert observed_chat["options"]["num_ctx"] == 2048
    assert observed_chat["options"]["num_predict"] == 96
    assert observed_chat["format"]["properties"]["score"]["minimum"] == 0
