from probe_scent.prompts import JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE


def test_prompt_does_not_reveal_condition_labels_or_hypothesis() -> None:
    combined = (JUDGE_SYSTEM_PROMPT + JUDGE_USER_TEMPLATE).lower()
    assert "neat_temptation" not in combined
    assert "messy_temptation" not in combined
    assert "benign_neat" not in combined
    assert "primary hypothesis" not in combined
