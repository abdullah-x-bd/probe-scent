import json
from pathlib import Path

from probe_scent.run import load_latest_attempts, parse_json_object


def test_parser_accepts_wrapped_json() -> None:
    parsed = parse_json_object(
        'prefix {"score": 42, "label": "possibly staged", '
        '"primary_cue": "unusual convenience", "confidence": 91} suffix'
    )
    assert parsed.score == 42
    assert parsed.confidence == 91


def test_latest_attempt_is_selected(tmp_path: Path) -> None:
    path = tmp_path / "attempts.jsonl"
    rows = [
        {"scenario_id": "a", "attempt_no": 1, "retry_index": 0, "status": "error", "score": None},
        {"scenario_id": "a", "attempt_no": 2, "retry_index": 0, "status": "ok", "score": 10},
    ]
    path.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
    latest = load_latest_attempts(path)
    assert latest["a"]["attempt_no"] == 2
    assert latest["a"]["status"] == "ok"
