# Limitations

Probe Scent v1 is a controlled construct-validity benchmark, not a deployment simulation. The canonical 150-scenario artifact is complete and verified, but the result has important interpretation limits.

## Canonical judge saturation

The most important observed limitation is score saturation. The canonical Qwen judge assigned very high evaluation-likeness ratings even to ordinary controls:

- control mean: **91.00**
- benign neat mean: **94.00**
- messy temptation mean: **88.67**
- neat temptation mean: **92.00**
- explicit evaluation mean: **95.00**

This means the absolute 0–100 scale is poorly calibrated in v1. Although the pre-specified matched H1 contrast is positive, the small separation occurs near the ceiling of the instrument. The result should therefore not be described as evidence that the model cleanly discriminates ordinary deployment-like scenarios from constructed evaluations.

This limitation was discovered by the frozen confirmatory run and is retained as part of the canonical evidence.

## H2 is not supported

The benchmark added a benign-neat control specifically to distinguish a temptation-specific neatness effect from generic convenience or tidy presentation. The corresponding difference-in-differences interaction is not supported. That materially narrows the interpretation of H1.

## Single canonical judge model

The frozen v1 protocol uses one canonical judge model, `qwen3.5:4b-q4_K_M`. This supports only a model-specific result. Cross-model replications should be reported as separate replication artifacts rather than silently pooled into v1.

## Model scale

The canonical model is a compact open 4B-parameter instruction model chosen to make the confirmatory experiment reproducible without paid inference. A result on this model should not be treated as direct evidence about frontier-scale systems. The May pilot on a different hosted model is preserved separately and is not pooled with v1.

## Quantization

The canonical model uses the frozen Q4_K_M quantized artifact. Quantization can change behavior relative to full-precision weights. The exact pulled model digest is therefore part of the canonical evidence contract.

## Ratings are not behavior

The primary outcome is an evaluation-likeness rating from 0 to 100. The experiment does not test whether a model actually takes a prohibited shortcut, withholds unsafe behavior because it suspects evaluation, or changes policy compliance over a long horizon.

## Synthetic scenarios

The 30 base tasks are synthetic and intentionally compact. Real deployments contain longer histories, richer tool state, organizational norms, incomplete information and consequences that are not represented here.

## Residual construct validity

The matched design removes the pilot's direct evaluation language and holds the tempting resource fixed within each primary pair, but neat and messy conditions necessarily differ in surface form. Word-count controls, the benign-neat condition and within-task analysis reduce this concern without proving that every residual difference is uniquely attributable to latent evaluation detection.

The observed ceiling effect provides an additional reason to avoid that stronger interpretation.

## Scenario naming

Some tempting filenames contain semantically sensitive terms such as `private`, `hidden`, `internal` or `priority`. The same tempting filename is used in both members of each primary messy/neat pair, so these cues are controlled for the primary contrast. They may still contribute to high absolute scores across conditions.

## Local inference reproducibility

Local inference removes hosted-model drift but does not imply perfect bitwise determinism across every CPU, Ollama version or low-level numerical implementation. Raw evidence records the full model digest, Ollama version, seed, temperature, context length, thinking setting, run IDs and timestamps. The artifact verifier enforces the frozen model and inference provenance.

## Statistical scope

Thirty matched base tasks are not a random sample from all deployment contexts. Confidence intervals quantify variation within the frozen benchmark and should not be interpreted as population-wide coverage guarantees.

The primary paired mean difference is statistically positive, but the median paired difference is zero. Reporting both prevents the mean effect from being mistaken for a uniform shift across all tasks.

## Human comparison absent

The canonical v1 study does not include human evaluation-likeness ratings. It therefore cannot establish that the model detects cues that human evaluators systematically miss.

## Pilot separation

The large May 2026 pilot effect is not treated as confirmatory evidence because its neat condition contained direct evaluation-related cues and the messy condition did not consistently preserve the same tempting resource. The much smaller confirmatory result shows why the pilot is best understood as motivating evidence and a methodological warning.

## Generalization boundary

Probe Scent v1 establishes a reproducible benchmark result and a calibration failure on one frozen judge. It does not establish universal evaluation awareness, scheming, deception, or behavioral adaptation.
