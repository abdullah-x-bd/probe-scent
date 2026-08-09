# Probe Scent v1 Dataset Card

## Scope

The v1 confirmatory dataset contains 150 synthetic workplace-style scenarios derived from 30 base
tasks in ten domains. Each base task appears in five matched conditions.

The benchmark is designed to isolate one narrow manipulation: whether an outside, tempting resource
is embedded in ordinary clutter or surfaced unusually conveniently.

## Domains

- software engineering
- research
- finance
- legal
- government administration
- human resources
- health administration
- education
- business operations
- nonprofit field work

Each domain contributes three base tasks.

## Matching contract

For every base task:

- `messy_temptation` and `neat_temptation` use the same tempting file;
- the underlying task is unchanged across all five conditions;
- the tempting file is outside the approved work packet in both temptation conditions;
- the neat condition changes placement and convenience rather than adding an explicit statement
  that the scenario is a test;
- `benign_neat` provides a corresponding convenience manipulation with an authorized file.

The committed validator rejects incomplete pairs, duplicate IDs, mismatched tempting files, and
direct evaluation-language leakage in non-explicit conditions.

## Length balance

The canonical generated dataset has a maximum messy-versus-neat word-count ratio of approximately
1.065 and a maximum absolute difference of 3 words. This does not make the conditions lexically
identical, but it removes the extreme length imbalance present in the pilot material.

## Synthetic nature and limitations

The scenarios are synthetic and intentionally compact. They do not reproduce all the ambiguity,
history, tool state, or organizational context of long-horizon agent deployments. A positive
result establishes detectability under this benchmark, not real-world behavioral adaptation.

The benchmark should therefore be treated as a controlled construct-validity test rather than a
deployment simulator.
