# Probe Scent v1 canonical evidence

This directory contains the completed frozen v1 evidence bundle.

## Verification status

`results/v1/verification.json` reports **PASS**.

The verified bundle contains all **150 / 150** canonical scenario results across **30 complete matched pairs**, with no duplicate IDs, no missing cells, no non-explicit direct evaluation-cue violations, and exact frozen dataset, run-order, prompt, model, backend and protocol provenance.

Canonical backend: `ollama`

Canonical model: `qwen3.5:4b-q4_K_M`

Protocol: `v1.0.0`

## Pre-specified findings

- H1 neat temptation minus messy temptation: **+3.33**, 95% CI **[1.00, 5.67]**, permutation p **0.0218**, mechanically `SUPPORTED`.
- H2 temptation-specific neatness interaction: **+0.33**, 95% CI **[-5.00, 4.67]**, permutation p **1.0**, `NOT_SUPPORTED`.
- H3 explicit evaluation minus control: **+4.00**, 95% CI **[0.67, 9.00]**, permutation p **0.0308**, mechanically `SUPPORTED`.

The canonical judge exhibits a major ceiling effect: controls average **91/100** and explicit evaluations **95/100**. This limits the substantive interpretation of the absolute score scale and is treated as a first-class construct-validity result rather than hidden.

See `../../docs/RESULTS.md` for interpretation.

## Evidence layout

- `raw/attempts.jsonl` contains canonical raw model attempts and provenance.
- `canonical_results.jsonl` contains the selected valid canonical result for each scenario.
- `summary.json` contains generated hypothesis and completeness summaries.
- `claims.json` contains the frozen mechanical claim decisions.
- `model_identity.json` records canonical backend/model identity.
- `tables/` contains condition summaries, paired effects, domain effects and sensitivity analyses.
- `figures/` contains deterministic SVG figures.
- `MANIFEST.json` records SHA-256 hashes of canonical evidence files.
- `verification.json` is the final PASS receipt.

The artifact verifier regenerates the derived evidence from the raw file and rejects provenance, completeness, hash or regeneration mismatches.
