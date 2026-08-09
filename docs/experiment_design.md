# Experiment design

Probe Scent v1 is a frozen matched-condition experiment for evaluation detectability.

The complete preregistered-style protocol is in [`V1_PROTOCOL.md`](V1_PROTOCOL.md), and the
dataset construction rules are in [`DATASET_CARD.md`](DATASET_CARD.md).

## Primary question

Holding the underlying task and tempting outside resource approximately constant, does surfacing
that resource unusually cleanly increase a language model's evaluation-likeness rating?

## Five conditions

- `control`
- `benign_neat`
- `messy_temptation`
- `neat_temptation`
- `explicit_eval`

The primary contrast is `neat_temptation - messy_temptation`.

The secondary interaction is:

`(neat_temptation - messy_temptation) - (benign_neat - control)`

The explicit-evaluation condition is a positive control.

## Claim boundary

Probe Scent v1 measures evaluation detectability. It does not by itself establish scheming,
deception, hidden goals, or behavioral adaptation.
