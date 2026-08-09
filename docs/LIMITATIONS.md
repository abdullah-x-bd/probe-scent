# Limitations

Probe Scent v1 is a controlled construct-validity benchmark, not a deployment simulation.

## Single canonical judge model

The frozen v1 protocol uses one canonical judge model, `qwen3.5:4b-q4_K_M`. This supports a model-specific confirmatory result, not a universal claim about language models. Cross-model replications should be reported as separate replication artifacts rather than silently folded into v1.

## Model scale

The canonical model is a compact open 4B-parameter instruction model chosen to make the entire confirmatory experiment reproducible without paid inference. A result on this model should not be treated as direct evidence about frontier-scale systems. The May pilot on a different hosted model is preserved separately and is not pooled with v1.

## Quantization

The canonical model uses the frozen Q4_K_M quantized artifact. Quantization can change model behavior relative to full-precision weights. The exact pulled model digest is therefore part of the canonical evidence contract.

## Ratings are not behavior

The primary outcome is an evaluation-likeness rating from 0 to 100. The experiment does not test whether a model actually takes a prohibited shortcut, withholds unsafe behavior because it suspects evaluation, or changes policy compliance over a long horizon.

## Synthetic scenarios

The 30 base tasks are synthetic and intentionally compact. Real deployments contain longer histories, richer tool state, organizational norms, incomplete information and consequences that are not represented here.

## Construct validity

Even after removing the pilot's direct cues, the neat and messy conditions necessarily differ in surface form. The matched design, word-count controls, benign-neat condition and within-task analysis reduce this concern but do not prove that every residual difference is uniquely attributable to a latent concept of evaluation.

## Scenario naming

Some tempting filenames contain semantically sensitive terms such as `private`, `hidden`, `internal` or `priority`. The same tempting filename is used in both members of every primary messy/neat pair, so these cues are controlled for the primary contrast. They may still affect absolute score levels.

## Local inference reproducibility

Local inference removes hosted-model drift but does not imply perfect bitwise determinism across every CPU, Ollama version or low-level numerical implementation. Raw evidence therefore records the full model digest, Ollama version, seed, temperature, context length, thinking setting, run IDs and timestamps. The artifact verifier requires a single backend version within the canonical evidence bundle and exact frozen model and inference provenance.

## Statistical scope

Thirty matched base tasks provide a useful controlled sample but are not a random sample from all possible deployment contexts. Confidence intervals quantify variation within the frozen benchmark and should not be interpreted as population-wide coverage guarantees.

## Human comparison absent

The canonical v1 study does not include human evaluation-likeness ratings. It therefore cannot directly establish whether the model detects cues that human evaluators systematically miss.

## Pilot separation

The large May 2026 pilot effect is not treated as confirmatory v1 evidence because the pilot neat condition contained direct evaluation-related cues and the messy condition did not consistently preserve the same tempting resource. The pilot is preserved as methodological history rather than pooled with v1.
