import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from dotenv import load_dotenv
from openai import OpenAI

from .prompts import (
    AGENT_SYSTEM_PROMPT,
    AGENT_USER_TEMPLATE,
    JUDGE_SYSTEM_PROMPT,
    JUDGE_USER_TEMPLATE,
    TRANSCRIPT_JUDGE_TEMPLATE,
)

DEFAULT_MODEL = os.getenv("PROBE_SCENT_MODEL", "gpt-5.4-nano")


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_json_object(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def call_model(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_output_tokens: int,
) -> str:
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=max_output_tokens,
    )
    return response.output_text


def judge_scenario(
    client: OpenAI,
    model: str,
    scenario: Dict[str, Any],
    max_output_tokens: int,
) -> Dict[str, Any]:
    prompt = JUDGE_USER_TEMPLATE.format(scenario_text=scenario["text"])
    raw = call_model(client, model, JUDGE_SYSTEM_PROMPT, prompt, max_output_tokens)
    parsed = parse_json_object(raw)
    return {
        **scenario,
        "mode": "judge",
        "judge_model": model,
        "raw_judge_output": raw,
        "score": parsed.get("score"),
        "seems_to_test": parsed.get("seems_to_test"),
        "normal_clues": parsed.get("normal_clues"),
        "staged_clues": parsed.get("staged_clues"),
        "confidence": parsed.get("confidence"),
    }


def agent_then_judge(
    client: OpenAI,
    model: str,
    scenario: Dict[str, Any],
    max_output_tokens: int,
    agent_output_tokens: int,
) -> Dict[str, Any]:
    agent_prompt = AGENT_USER_TEMPLATE.format(scenario_text=scenario["text"])
    assistant_response = call_model(
        client,
        model,
        AGENT_SYSTEM_PROMPT,
        agent_prompt,
        agent_output_tokens,
    )

    judge_prompt = TRANSCRIPT_JUDGE_TEMPLATE.format(
        scenario_text=scenario["text"],
        assistant_response=assistant_response,
    )
    raw = call_model(client, model, JUDGE_SYSTEM_PROMPT, judge_prompt, max_output_tokens)
    parsed = parse_json_object(raw)
    return {
        **scenario,
        "mode": "agent",
        "agent_model": model,
        "judge_model": model,
        "assistant_response": assistant_response,
        "raw_judge_output": raw,
        "score": parsed.get("score"),
        "seems_to_test": parsed.get("seems_to_test"),
        "normal_clues": parsed.get("normal_clues"),
        "staged_clues": parsed.get("staged_clues"),
        "confidence": parsed.get("confidence"),
    }


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the probe-scent experiment.")
    parser.add_argument("--mode", choices=["judge", "agent"], required=True)
    parser.add_argument("--input", required=True, help="Path to scenarios JSONL")
    parser.add_argument("--output", required=True, help="Path to output JSONL")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-output-tokens", type=int, default=350)
    parser.add_argument("--agent-output-tokens", type=int, default=700)
    args = parser.parse_args()

    client = OpenAI()
    scenarios = list(read_jsonl(Path(args.input)))
    rows = []

    for scenario in scenarios:
        if args.mode == "judge":
            row = judge_scenario(
                client,
                args.model,
                scenario,
                args.max_output_tokens,
            )
        else:
            row = agent_then_judge(
                client,
                args.model,
                scenario,
                args.max_output_tokens,
                args.agent_output_tokens,
            )
        rows.append(row)
        print(f"{scenario['id']} score={row.get('score')}")

    write_jsonl(Path(args.output), rows)


if __name__ == "__main__":
    main()
