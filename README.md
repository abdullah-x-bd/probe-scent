# Probe Scent

**Probe Scent is a controlled benchmark for measuring evaluation detectability from opportunity structure in language-model scenarios.**

The repository contains a frozen `v1.0.0` confirmatory protocol built after a May 2026 pilot. The exact pilot repository state is preserved on `archive/probe-scent-pilot-2026-05` rather than mixed into the confirmatory evidence line.

## Research question

Holding the underlying task and tempting outside resource approximately constant, does surfacing that resource unusually cleanly increase a language model's rating that the situation is a deliberately constructed evaluation?

Probe Scent measures **evaluation detectability**. It does not by itself measure scheming, hidden goals, deception, or deployment behavior.

## Confirmatory design

The frozen benchmark contains **30 base tasks across 10 domains**, each instantiated in five matched conditions:

| Condition | Role |
|---|---|
| `control` | ordinary task with approved materials |
| `benign_neat` | authorized relevant material is unusually convenient |
| `messy_temptation` | tempting outside resource is embedded in plausible clutter |
| `neat_temptation` | the same tempting resource is surfaced unusually conveniently |
| `explicit_eval` | positive control openly identifying an evaluation |

This yields **150 canonical scenarios**.

The primary contrast is the within-task difference:

`neat_temptation - messy_temptation`

The secondary interaction is:

`(neat_temptation - messy_temptation) - (benign_neat - control)`

This distinguishes a temptation-specific neatness effect from a generic preference for tidy or convenient scenarios.

## Frozen protocol

The protocol was frozen before the canonical v1 model run.

- dataset SHA-256: `077e5e1e350957ea7d4c5697b26e165d91f7e26e5568fc9d381f41b05fcb074a`
- run-order SHA-256: `aa625e06455b943b26ab5546f72fb0003795956ba416cbe089cce419ded248c7`
- run-order seed: `20260809`
- complete matched pairs: `30 / 30`
- direct evaluation-cue leakage in non-explicit conditions: `0`
- maximum messy/neat word-count difference: `3`

The manual pair audit is committed at `data/v1/pair_audit.json`. The automated validation receipt is at `data/v1/validation.json`.

## Reproduce the offline artifact

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
probe-scent validate-data
python -m probe_scent.run --config configs/v1.yaml --dry-run
python -m probe_scent.artifact --config configs/v1.yaml --result-dir results/v1 --no-regenerate
```

The last command intentionally reports `INCOMPLETE` until genuine canonical model outputs exist. The repository never fabricates or simulates missing model evidence.

## Canonical live run

The manual GitHub Actions workflow `.github/workflows/run-canonical.yml` executes the frozen model protocol using the repository secret `OPENAI_API_KEY`.

It is designed to be interruption-safe:

1. raw attempts are append-only;
2. partial raw evidence is committed back to the branch;
3. a rerun uses resume mode and executes only missing IDs;
4. analysis is blocked until all 150 canonical scenarios have valid results;
5. tables, claims, sensitivity analyses, figures and a SHA-256 manifest are generated automatically;
6. the artifact verifier rejects the evidence if the model, prompt, protocol, dataset or run-order provenance differs from the frozen configuration;
7. only a verified evidence bundle is committed as canonical evidence.

## Analysis

The canonical analysis includes:

- matched mean and median differences;
- nonparametric bootstrap 95% confidence intervals;
- two-sided sign-flip permutation tests;
- paired standardized effect size where defined;
- the benign-neat difference-in-differences interaction;
- domain-level effects;
- leave-one-domain-out sensitivity;
- leave-one-pair-out sensitivity;
- deterministic publication-quality SVG figures.

## Repository map

```text
configs/                    frozen protocol configuration
data/v1/                    base tasks, canonical dataset, run order, validation and manual audit
docs/                       protocol, dataset card, pilot history, claims and limitations
src/probe_scent/            runner, schemas, analysis, figures and artifact verifier
scripts/                     deterministic canonical-data generator
results/v1/                 canonical evidence location
tests/                       offline scientific and pipeline tests
.github/workflows/           offline CI and canonical live-run workflow
```

## Documentation

- `docs/V1_PROTOCOL.md` describes the frozen hypotheses and analysis contract.
- `docs/DATASET_CARD.md` documents construction and matching.
- `docs/PILOT_HISTORY.md` explains why the May experiments are motivating rather than confirmatory evidence.
- `docs/CLAIMS.md` defines the allowed scientific claims.
- `docs/LIMITATIONS.md` records the benchmark's major limitations.
- `docs/REPRODUCIBILITY.md` gives the exact reproduction workflow.

## Current evidence status

The confirmatory v1 design and offline artifact are frozen and validated. The live canonical model evidence is only canonical once `results/v1/MANIFEST.json` exists and `probe-scent verify-artifact` returns `PASS`.
