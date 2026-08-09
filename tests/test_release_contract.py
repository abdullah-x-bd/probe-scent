from pathlib import Path

from probe_scent.release import audit_release


ROOT = Path(__file__).resolve().parents[1]


def test_release_contract_passes() -> None:
    receipt = audit_release(ROOT)
    assert receipt["status"] == "PASS", receipt["errors"]
    assert receipt["canonical_rows"] == 150
    assert receipt["artifact_status"] == "PASS"
    assert receipt["workflows_manual_only"] is True


def test_dependency_lock_is_exact() -> None:
    lines = [
        line.strip()
        for line in (ROOT / "requirements-lock.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert lines
    assert all("==" in line for line in lines)
    assert not any(">=" in line or "~=" in line for line in lines)


def test_completed_docs_do_not_revert_to_pre_ollama_instructions() -> None:
    targets = [
        ROOT / "README.md",
        ROOT / "docs/REPRODUCIBILITY.md",
        ROOT / "results/v1/README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in targets)
    assert "OPENAI_API_KEY" not in combined
    assert "Until a canonical API run" not in combined
