# Probe Scent release checklist

This checklist defines the minimum gate for treating a Probe Scent protocol as an archival research artifact rather than a development snapshot.

## Scientific freeze

- [x] Research question and hypotheses frozen before canonical inference.
- [x] Canonical dataset and run order frozen and hashed.
- [x] Model, backend, model digest, prompt, inference settings, and analysis seeds frozen.
- [x] Manual matched-pair audit recorded.
- [x] Pilot evidence separated from confirmatory evidence.

## Canonical evidence

- [x] All 150 expected v1 scenario IDs have valid canonical results.
- [x] All 30 matched base tasks are complete in all five conditions.
- [x] Raw attempts retain provenance and failures rather than silently replacing history.
- [x] Derived tables, claims, sensitivity analyses, and figures are committed.
- [x] `results/v1/MANIFEST.json` records SHA-256 hashes for canonical evidence files.
- [x] `results/v1/verification.json` reports `PASS`.
- [x] Derived evidence regenerates exactly from committed raw results.

## Interpretation

- [x] H1, H2, and H3 statuses are machine-readable.
- [x] The H2 null result is retained and prominently documented.
- [x] The judge ceiling/calibration failure is retained and prominently documented.
- [x] Claims explicitly exclude scheming, hidden goals, deception, deployment behavior, and cross-model generalization.
- [x] Limitations include single-model scope, quantization, synthetic scenarios, construct validity, statistical scope, and absent human comparison.

## Software quality

- [x] Installable Python package with CLI.
- [x] Ruff linting.
- [x] Strict mypy configuration and CI enforcement.
- [x] Unit, pipeline, provenance, backend, artifact, and release-contract tests.
- [x] Dataset validation in CI.
- [x] Completed-artifact verification in CI.
- [x] Wheel-build smoke test in CI.
- [x] Frozen Python dependency lock tested on Python 3.11 and 3.12.
- [x] Canonical inference workflows are manual-only after evidence freeze.

## Research usability

- [x] README states the completed result and calibration caveat.
- [x] Exact reproduction guide uses the canonical Ollama/Qwen backend.
- [x] Dataset card and protocol documentation are present.
- [x] Result, claim-boundary, limitation, and pilot-history documents are present.
- [x] Contribution policy protects frozen evidence from silent mutation.
- [x] Security policy is present.
- [x] Apache-2.0 license is present.
- [x] `CITATION.cff` is present and version-aligned.
- [x] Changelog records the canonical v1 release.
- [x] `probe-scent audit-release` machine-checks the release contract.

## Final gate

A release candidate is acceptable only when all of the following return success:

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
ruff check src tests scripts
mypy src/probe_scent
pytest -q
probe-scent validate-data --receipt /tmp/probe-scent-validation.json
probe-scent audit-release
python -m probe_scent.artifact --config configs/v1.yaml --result-dir results/v1
python -m pip wheel . --no-deps --wheel-dir /tmp/probe-scent-wheel
```

If any scientific input or canonical evidence changes, this checklist must be re-evaluated under a new protocol/version decision rather than silently reusing `v1.0.0`.
