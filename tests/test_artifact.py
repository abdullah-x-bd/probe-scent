from pathlib import Path

from probe_scent.artifact import verify_artifact


def test_verifier_reports_incomplete_without_live_raw_results(tmp_path: Path) -> None:
    receipt = verify_artifact(Path("configs/v1.yaml"), tmp_path / "v1", regenerate=False)
    assert receipt["status"] == "INCOMPLETE"
    assert "canonical raw attempts are not present" in receipt["errors"]
