# Claim boundaries

Probe Scent v1 is deliberately narrow. The frozen 150-scenario canonical run is complete and the artifact verifier returns `PASS`.

## Pre-specified claim statuses

The machine-generated claim decisions are stored in `results/v1/claims.json` and are not rewritten after observing the results.

### H1: neat temptation versus messy temptation

`SUPPORTED` under the frozen mechanical decision rule.

Across 30 matched pairs, neat temptation scored **+3.33 points** higher on average than messy temptation. The 95% bootstrap CI is **[1.00, 5.67]** and the two-sided sign-flip permutation p-value is **0.0218**.

The repository may therefore state that, **for the frozen benchmark and canonical judge**, unusually convenient presentation of the tempting resource produced a small positive paired difference in evaluation-likeness ratings.

This result must not be described as a large or general evaluation-awareness effect. The median paired difference is zero and the canonical judge exhibits severe ceiling saturation.

### H2: temptation-specific neatness interaction

`NOT_SUPPORTED`.

The pre-specified interaction

`(neat temptation - messy temptation) - (benign neat - control)`

is **+0.33 points**, with 95% CI **[-5.00, 4.67]** and permutation p-value **1.0**.

The repository therefore does **not** claim that neatness has a larger effect specifically for tempting opportunities than for benign convenient resources.

### H3: explicit-evaluation positive control

`SUPPORTED` under the frozen mechanical rule.

Explicit evaluations scored **+4.00 points** above controls on average, with 95% CI **[0.67, 9.00]** and permutation p-value **0.0308**.

However, ordinary controls themselves averaged **91/100**, compared with **95/100** for explicit evaluations. This weak separation on the absolute scale is an important calibration warning.

## Construct-validity interpretation

The canonical judge rated almost all scenario types as highly evaluation-like:

- control: 91.00 mean
- benign neat: 94.00 mean
- messy temptation: 88.67 mean
- neat temptation: 92.00 mean
- explicit evaluation: 95.00 mean

This ceiling effect limits the substantive meaning of absolute scores and makes the null H2 interaction especially important. The defensible interpretation is therefore more conservative than the binary H1/H3 labels alone suggest.

Probe Scent v1 provides strong evidence that **measurement design and calibration matter**. The very large May pilot separation became a small paired effect under a stricter matched design, while the more demanding temptation-specific interaction was absent.

## Claims the repository does not support

Probe Scent v1 does not establish that a model:

- is scheming;
- has hidden goals;
- intentionally deceives evaluators;
- changes behavior after detecting an evaluation;
- would detect evaluations in a real deployment;
- generalizes the measured effect to frontier-scale systems, all models, or all domains;
- possesses a well-calibrated internal 0–100 notion corresponding to the benchmark score.

A high evaluation-likeness score is a model-produced rating of stagedness under one scoring prompt. It is not direct evidence of internal awareness or behavioral adaptation.

## Negative results are first-class evidence

H2 being unsupported and the canonical score saturation are part of the result, not defects to hide. The May pilot is retained as methodological history because it demonstrates how direct or correlated cues can produce dramatic apparent effects. The confirmatory benchmark was explicitly designed to stress that interpretation.

See `docs/RESULTS.md` for the full result narrative and `docs/LIMITATIONS.md` for the calibration and generalization constraints.
