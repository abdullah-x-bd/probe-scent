# Contributing

Probe Scent is a research artifact with a frozen canonical v1 evidence line. Contributions are welcome, but changes must preserve the distinction between immutable evidence and future work.

## Canonical v1 is frozen

Do not edit the following in-place to improve, reinterpret, or replace the published v1 result:

- `configs/v1.yaml`;
- `data/v1/scenarios.jsonl.gz`;
- `data/v1/run_order.jsonl.gz`;
- `data/v1/pair_audit.json`;
- `results/v1/raw/attempts.jsonl`;
- generated v1 claims, summaries, tables, figures, verification receipts, or manifest.

A correction to a genuine clerical or integrity error must be explicitly documented in the changelog and must not silently preserve the same protocol version.

## New experiments

Substantive extensions should create a new protocol namespace such as `v1.1`, `v2`, or a clearly named replication directory. Do not pool new model runs into v1 after inspecting the canonical result.

Examples of valid extensions include:

- cross-model replications;
- alternative judge calibration studies;
- human-rating comparisons;
- agentic behavioral follow-ups;
- new domains or longer-horizon tasks.

Each extension should freeze its own configuration, data hashes, model identity, prompts, analysis decisions, and evidence directory before canonical inference.

## Development setup

For the closest reproduction of the validated Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

Run the full local gate before opening a pull request:

```bash
ruff check src tests scripts
mypy src/probe_scent
pytest -q
probe-scent validate-data --receipt /tmp/probe-scent-validation.json
probe-scent audit-release
python -m probe_scent.artifact --config configs/v1.yaml --result-dir results/v1
```

## Pull requests

A pull request should explain:

1. whether it changes code, documentation, or a scientific protocol;
2. whether canonical evidence is touched;
3. which tests or verification gates were run;
4. whether claims or reproducibility instructions change.

Changes that modify scientific meaning require an explicit protocol/version decision rather than an unannounced edit to v1.
