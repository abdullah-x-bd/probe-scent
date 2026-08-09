# Probe Scent v1 evidence

This directory is reserved for the frozen canonical v1 evidence bundle.

The live model run is intentionally not simulated. The canonical workflow writes append-only raw
attempts to `raw/attempts.jsonl`, then derives tables, claims, figures, `summary.json`, and
`MANIFEST.json`. The artifact verifier only returns `PASS` when all 150 canonical scenario IDs
have valid results and the committed derived evidence regenerates exactly.

Until a canonical API run has been executed, this directory is intentionally incomplete.
