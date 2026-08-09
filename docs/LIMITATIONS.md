# Limitations

Probe Scent v1 is a controlled construct-validity benchmark, not a deployment simulation.

## Single canonical judge model

The frozen v1 protocol uses one canonical judge model. This supports a model-specific confirmatory result, not a universal claim about language models. Cross-model replications should be reported as separate replication artifacts rather than silently folded into v1.

## Ratings are not behavior

The primary outcome is an evaluation-likeness rating from 0 to 100. The experiment does not test whether a model actually takes a prohibited shortcut, withholds unsafe behavior because it suspects evaluation, or changes policy compliance over a long horizon.

## Synthetic scenarios

The 30 base tasks are synthetic and intentionally compact. Real deployments contain longer histories, richer tool state, organizational norms, incomplete information and consequences that are not represented here.

## Construct validity

Even after removing the pilot's direct cues, the neat and messy conditions necessarily differ in surface form. The matched design, word-count controls, benign-neat condition and within-task analysis reduce this concern but do not prove that every residual difference is uniquely attributable to a latent concept of evaluation.

## Scenario naming

Some tempting filenames contain semantically sensitive terms such as `private`, `hidden`, `internal` or `priority`. The same tempting filename is used in both members of every primary messy/neat pair, so these cues are controlled for the primary contrast. They may still affect absolute score levels.

## API nondeterminism and model evolution

Hosted model behavior may vary across time and backend revisions. Raw evidence therefore records run IDs, timestamps, requested and returned model metadata, prompt hashes, dataset hashes and protocol version. A later replication is not assumed to be identical to the frozen v1 run.

## Statistical scope

Thirty matched base tasks provide a useful controlled sample but are not a random sample from all possible deployment contexts. Confidence intervals quantify variation within the frozen benchmark and should not be interpreted as population-wide coverage guarantees.

## Human comparison absent

The canonical v1 study does not include human evaluation-likeness ratings. It therefore cannot directly establish whether the model detects cues that human evaluators systematically miss.

## Pilot separation

The large May 2026 pilot effect is not treated as confirmatory v1 evidence because the pilot neat condition contained direct evaluation-related cues and the messy condition did not consistently preserve the same tempting resource. The pilot is preserved as methodological history rather than pooled with v1.
