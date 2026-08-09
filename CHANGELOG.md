# Changelog

## 1.0.0 - 2026-08-09

### Scientific protocol

- Preserves the May 2026 experiments as pilot evidence on a separate archive branch.
- Introduces a 30-task, five-condition matched confirmatory benchmark across 10 domains.
- Removes direct evaluation-language leakage from non-explicit canonical conditions.
- Freezes H1, the temptation-specific H2 interaction, and H3 before canonical inference.
- Freezes deterministic dataset generation, shuffled run order, hashes, model identity, prompt, inference settings, and statistical seeds.

### Canonical evidence

- Executes all 150 canonical scenarios with the frozen local Ollama `qwen3.5:4b-q4_K_M` backend.
- Records 150 / 150 valid canonical results across 30 / 30 complete matched base tasks.
- H1 `neat_temptation - messy_temptation`: +3.33, 95% CI [1.00, 5.67], permutation p = 0.0218, mechanically supported under the frozen rule.
- H2 temptation-specific neatness interaction: +0.33, 95% CI [-5.00, 4.67], p = 1.0, not supported.
- H3 `explicit_eval - control`: +4.00, 95% CI [0.67, 9.00], p = 0.0308, mechanically supported under the frozen rule.
- Records the canonical judge ceiling/calibration failure as a first-class result: controls average 91/100 and explicit evaluations 95/100.
- Commits raw attempts, canonical selections, tables, sensitivity analyses, figures, machine-readable claims, model identity, manifest, and PASS verification receipt.

### Analysis and verification

- Adds paired bootstrap intervals, sign-flip permutation tests, standardized effects, interaction analysis, domain effects, and leave-one-domain/pair-out sensitivity.
- Adds deterministic SVG figures.
- Adds artifact verification for exact data, run order, prompt, model, digest, inference settings, protocol, evidence completeness, manifest integrity, and deterministic regeneration.
- Adds a machine-enforced `probe-scent audit-release` repository-level release contract.

### Software and reproducibility

- Adds installable `probe-scent` 1.0.0 package and CLI.
- Adds an exact Python dependency lock derived from the validated release environment.
- Adds Ruff, strict mypy enforcement, scientific/pipeline/provenance/release tests, and wheel-build smoke testing in CI on Python 3.11 and 3.12.
- Makes canonical inference workflows manual-only after evidence freeze.
- Adds contribution, security, release-checklist, claim-boundary, limitation, protocol, dataset-card, results, and reproducibility documentation.
- Corrects reproduction instructions to the frozen local Ollama/Qwen execution path.
