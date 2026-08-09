# Canonical v1 results

Probe Scent v1 completed the frozen 150-scenario confirmatory protocol with all 30 matched base tasks present in all five conditions. The canonical artifact verifier returned `PASS` with no provenance, hash, pairing, or regeneration errors.

## Condition scores

| Condition | n | Mean | SD | Median |
|---|---:|---:|---:|---:|
| control | 30 | 91.00 | 13.03 | 95 |
| benign neat | 30 | 94.00 | 3.05 | 95 |
| messy temptation | 30 | 88.67 | 4.90 | 85 |
| neat temptation | 30 | 92.00 | 4.66 | 95 |
| explicit evaluation | 30 | 95.00 | 0.00 | 95 |

The complete generated table is `results/v1/tables/condition_summary.csv`.

## Pre-specified hypotheses

### H1: neat temptation versus messy temptation

The matched mean difference was **+3.33 points** across 30 pairs.

- 95% bootstrap CI: **[1.00, 5.67]**
- two-sided sign-flip permutation p: **0.0218**
- paired Cohen's dz: **0.504**
- median paired difference: **0**

Under the frozen mechanical decision rule, H1 is marked `SUPPORTED` because the bootstrap confidence interval lies above zero.

### H2: temptation-specific neatness interaction

The pre-specified difference-in-differences was:

`(neat temptation - messy temptation) - (benign neat - control)`

The mean interaction was **+0.33 points**.

- 95% bootstrap CI: **[-5.00, 4.67]**
- sign-flip permutation p: **1.0**
- median interaction: **0**

H2 is `NOT_SUPPORTED`. The canonical experiment therefore does not establish that neatness has a larger effect specifically for tempting opportunities than for benign convenient resources.

### H3: explicit evaluation positive control

Explicit evaluations scored **+4.00 points** above ordinary controls on average.

- 95% bootstrap CI: **[0.67, 9.00]**
- sign-flip permutation p: **0.0308**
- paired Cohen's dz: **0.307**

Under the frozen rule, H3 is marked `SUPPORTED`.

## Critical calibration result

The absolute score distribution reveals an important construct-validity limitation. The canonical judge assigned very high evaluation-likeness ratings to almost every condition:

- ordinary controls averaged **91/100**;
- benign-neat scenarios averaged **94/100**;
- explicit evaluations averaged **95/100**.

This strong ceiling effect means that the canonical judge is poorly calibrated for interpreting the absolute 0–100 scale as a clean measure of evaluation detectability. The H1 paired contrast remains a genuine pre-specified statistical result, but its substantive interpretation must be modest because the same judge treats ordinary scenarios as highly evaluation-like.

The more demanding H2 interaction is therefore particularly important, and it is not supported.

## What v1 establishes

The strongest defensible conclusions are:

1. the stricter matched protocol is fully reproducible and auditable;
2. under the frozen Qwen 3.5 4B judge, neat temptation scores are modestly higher than matched messy temptation scores;
3. the benchmark does not show a temptation-specific neatness interaction;
4. the canonical judge exhibits severe score saturation, limiting construct validity of the absolute rating scale;
5. the huge May pilot effect does not survive in anything like its original magnitude once direct evaluation cues are removed and the comparison is tightly matched.

The last point is scientifically useful. It demonstrates why evaluation-awareness measurements need matched controls and calibration checks before large raw score gaps are interpreted as evidence of model-side evaluation detection.

## What v1 does not establish

The experiment does not establish scheming, hidden goals, deception, behavioral adaptation, deployment-time evaluation awareness, or generalization to frontier-scale models. It is a controlled measurement study on one frozen compact open model.

Generated machine-readable results remain authoritative in `results/v1/summary.json`, `results/v1/claims.json`, and `results/v1/verification.json`.
