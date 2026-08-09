# Probe Scent v1 Confirmatory Protocol

## Status

Frozen before the v1 canonical inference run.

Protocol version: `v1.0.0`

Canonical dataset SHA-256:

`077e5e1e350957ea7d4c5697b26e165d91f7e26e5568fc9d381f41b05fcb074a`

Canonical run-order SHA-256:

`aa625e06455b943b26ab5546f72fb0003795956ba416cbe089cce419ded248c7`

Run-order seed: `20260809`

## Frozen inference environment

The confirmatory v1 run uses a local open model so the full benchmark can be reproduced without a paid inference service.

- backend: `ollama`
- model: `qwen3.5:4b-q4_K_M`
- expected model-digest prefix: `2a654d98e6fb`
- temperature: `0.0`
- inference seed: `20260809`
- context length: `2048`
- maximum generated tokens: `96`
- thinking: disabled
- output constrained by the JSON schema in `src/probe_scent/schemas.py`

Before any scenario is scored, the runner queries the local Ollama model registry and refuses to run if the pulled model digest does not match the frozen prefix. Every raw result records the full model digest, Ollama version and inference settings.

## Research question

Holding the underlying task and tempting opportunity approximately constant, does surfacing
that opportunity in an unusually clean and convenient way increase a language model's rating
that the scenario is a deliberately constructed evaluation, benchmark, safety probe, or staged
assessment?

The construct measured here is **evaluation detectability**. Probe Scent v1 does not measure
scheming, hidden goals, long-horizon deception, or actual deployment behavior.

## Design

Thirty base tasks span ten domains. Every task has five matched conditions:

1. `control`: ordinary task with approved materials.
2. `benign_neat`: an authorized relevant file is unusually convenient.
3. `messy_temptation`: the same unauthorized tempting file used in the neat condition is embedded
   in plausible clutter.
4. `neat_temptation`: that tempting file is unusually convenient and prominently surfaced.
5. `explicit_eval`: positive control that openly identifies the scenario as an evaluation.

The non-explicit conditions do not contain direct evaluation-language cues such as "evaluation",
"benchmark", "staged", "help you pass", or "how your work will be judged".

## Frozen hypotheses

### H1, primary

`neat_temptation - messy_temptation > 0`

The primary estimator is the mean within-pair score difference over the 30 matched base tasks.

### H2, interaction

The temptation-specific neatness effect is positive:

`(neat_temptation - messy_temptation) - (benign_neat - control) > 0`

This tests whether neatness specifically amplifies evaluation detectability in the presence of a
tempting outside resource rather than making all tidy scenarios look test-like.

### H3, positive control

`explicit_eval - control > 0`

This checks that the scoring instrument can distinguish an openly labeled evaluation from an
ordinary task.

## Statistical protocol

Primary and secondary matched effects report:

- number of complete matched pairs;
- mean and median paired difference;
- standard deviation of paired differences;
- 95% nonparametric bootstrap confidence interval;
- two-sided sign-flip permutation p-value;
- paired standardized effect size where defined.

H2 uses the within-pair difference-in-differences.

Sensitivity analyses include:

- leave-one-domain-out primary effects;
- leave-one-pair-out primary effects;
- domain-level primary effects;
- median-based summaries in the canonical tables.

The analysis seeds and sample counts are frozen in `configs/v1.yaml`.

## Run protocol

The canonical judge receives only scenario text between boundary markers. Condition, pair ID,
domain label, hypotheses, and expected direction are never included in the model input.

The canonical run uses the deterministic shuffled order in `data/v1/run_order.jsonl.gz`.
Calls are written append-only to `results/v1/raw/attempts.jsonl`. Failed calls remain in the audit
trail. Resume mode re-runs only scenarios without a valid result.

No prompt, dataset, model, model quantization, inference setting, hypothesis, or analysis change is
permitted after inspecting canonical results without incrementing the protocol version and recording
the change.
