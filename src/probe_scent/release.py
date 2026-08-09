from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

import yaml

from .artifact import verify_artifact

REQUIRED_RELEASE_FILES = (
    "README.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements-lock.txt",
    "configs/v1.yaml",
    "docs/V1_PROTOCOL.md",
    "docs/DATASET_CARD.md",
    "docs/RESULTS.md",
    "docs/CLAIMS.md",
    "docs/LIMITATIONS.md",
    "docs/REPRODUCIBILITY.md",
    "docs/RELEASE_CHECKLIST.md",
    "data/v1/pair_audit.json",
    "data/v1/validation.json",
    "results/v1/raw/attempts.jsonl",
    "results/v1/summary.json",
    "results/v1/claims.json",
    "results/v1/MANIFEST.json",
    "results/v1/verification.json",
)

CANONICAL_WORKFLOWS = (
    ".github/workflows/run-canonical.yml",
    ".github/workflows/run-canonical-parallel.yml",
)


def _text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(_text(root, relative))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {relative}")
    return value


def _check_required_files(root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_RELEASE_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing release file: {relative}")


def _check_versions(root: Path, errors: list[str]) -> dict[str, str]:
    pyproject = tomllib.loads(_text(root, "pyproject.toml"))
    project_version = str(pyproject["project"]["version"])

    init_match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        _text(root, "src/probe_scent/__init__.py"),
        flags=re.MULTILINE,
    )
    if init_match is None:
        errors.append("src/probe_scent/__init__.py does not expose __version__")
        package_version = "MISSING"
    else:
        package_version = init_match.group(1)

    citation_raw: Any = yaml.safe_load(_text(root, "CITATION.cff"))
    if not isinstance(citation_raw, dict):
        errors.append("CITATION.cff is not a mapping")
        citation_version = "MISSING"
    else:
        citation_version = str(citation_raw.get("version", "MISSING"))

    config_raw: Any = yaml.safe_load(_text(root, "configs/v1.yaml"))
    if not isinstance(config_raw, dict):
        errors.append("configs/v1.yaml is not a mapping")
        protocol_version = "MISSING"
    else:
        protocol_version = str(config_raw.get("version", "MISSING"))

    expected_protocol = f"v{project_version}"
    if package_version != project_version:
        errors.append(
            f"version mismatch: package={package_version} pyproject={project_version}"
        )
    if citation_version != project_version:
        errors.append(
            f"version mismatch: citation={citation_version} pyproject={project_version}"
        )
    if protocol_version != expected_protocol:
        errors.append(
            f"version mismatch: protocol={protocol_version} expected={expected_protocol}"
        )
    if f"## {project_version} -" not in _text(root, "CHANGELOG.md"):
        errors.append(f"CHANGELOG.md has no release heading for {project_version}")

    return {
        "project": project_version,
        "package": package_version,
        "citation": citation_version,
        "protocol": protocol_version,
    }


def _check_lock(root: Path, errors: list[str]) -> int:
    lines = [
        line.strip()
        for line in _text(root, "requirements-lock.txt").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        errors.append("requirements-lock.txt contains no pinned dependencies")
        return 0
    for line in lines:
        if "==" not in line or any(operator in line for operator in (">=", "<=", "~=", ">", "<")):
            errors.append(f"dependency is not exactly pinned: {line}")
    return len(lines)


def _check_workflows(root: Path, errors: list[str]) -> None:
    for relative in CANONICAL_WORKFLOWS:
        content = _text(root, relative)
        header = content.split("permissions:", maxsplit=1)[0]
        if "workflow_dispatch:" not in header:
            errors.append(f"canonical workflow is not manually dispatchable: {relative}")
        if re.search(r"^\s*pull_request\s*:", header, flags=re.MULTILINE):
            errors.append(f"canonical workflow still runs on pull requests: {relative}")
        if re.search(r"^\s*push\s*:", header, flags=re.MULTILINE):
            errors.append(f"canonical workflow still runs on pushes: {relative}")


def _check_stale_documentation(root: Path, errors: list[str]) -> None:
    stale_targets = (
        "README.md",
        "docs/REPRODUCIBILITY.md",
        "results/v1/README.md",
    )
    forbidden = ("OPENAI_API_KEY", "requires an OpenAI API key", "Until a canonical API run")
    for relative in stale_targets:
        content = _text(root, relative)
        for phrase in forbidden:
            if phrase in content:
                errors.append(f"stale pre-Ollama instruction in {relative}: {phrase}")

    results_text = _text(root, "docs/RESULTS.md")
    if "H2 is `NOT_SUPPORTED`" not in results_text:
        errors.append("docs/RESULTS.md does not retain the H2 null result")
    if "ceiling effect" not in results_text.lower():
        errors.append("docs/RESULTS.md does not foreground the canonical ceiling effect")


def audit_release(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    _check_required_files(root, errors)
    if errors:
        return {"status": "FAIL", "errors": errors}

    versions = _check_versions(root, errors)
    pinned_dependencies = _check_lock(root, errors)
    _check_workflows(root, errors)
    _check_stale_documentation(root, errors)

    verification = _json(root, "results/v1/verification.json")
    if verification.get("status") != "PASS":
        errors.append("committed verification receipt is not PASS")
    if verification.get("canonical_rows") != 150:
        errors.append("committed verification receipt does not contain 150 canonical rows")

    artifact_receipt = verify_artifact(
        root / "configs/v1.yaml",
        root / "results/v1",
        regenerate=False,
    )
    if artifact_receipt.get("status") != "PASS":
        errors.append(f"artifact verifier failed: {artifact_receipt.get('errors')}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "versions": versions,
        "pinned_dependencies": pinned_dependencies,
        "canonical_rows": verification.get("canonical_rows"),
        "artifact_status": artifact_receipt.get("status"),
        "workflows_manual_only": not any("workflow" in error for error in errors),
    }
