# Probe Scent

Probe Scent is a controlled benchmark for measuring whether the structure of an opportunity makes
a language-model scenario appear more like a deliberately constructed evaluation.

This branch contains the frozen `v1.0.0` confirmatory protocol. The May 2026 pilot is preserved on
`archive/probe-scent-pilot-2026-05`.

## Canonical question

Holding the underlying task and tempting outside resource approximately constant, does surfacing
that resource unusually cleanly increase evaluation-likeness ratings?

The v1 benchmark uses 30 base tasks across ten domains and five matched conditions per task:

- control
- benign neat
- messy temptation
- neat temptation
- explicit evaluation

The primary contrast is matched `neat temptation - messy temptation`. The secondary
difference-in-differences tests whether neatness has a larger effect in the presence of a tempting
outside resource than for an authorized relevant resource.

## Reproducibility gates

```bash
pip install -e ".[dev]"
pytest -q
probe-scent validate-data
python -m probe_scent.run --config configs/v1.yaml --dry-run
```

The live canonical model run is not simulated. After it is executed through the manual GitHub
Actions workflow, the analysis and verifier generate and audit the complete `results/v1` bundle.

See `docs/V1_PROTOCOL.md`, `docs/DATASET_CARD.md`, and `docs/PILOT_HISTORY.md`.
