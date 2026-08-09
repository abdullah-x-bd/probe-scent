# Reproducibility

Probe Scent v1 is a completed, frozen research artifact. The committed raw evidence, derived statistics, figures, manifest, and verification receipt can be checked without rerunning model inference.

## Environment

The closest reproduction of the validated Python environment uses the committed dependency lock:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

The lock captures the Python runtime and development dependency versions used by the successful GitHub Actions release gate on Python 3.11 and 3.12. The canonical model artifact is pinned separately by its Ollama model digest in `configs/v1.yaml`.

## Verify the completed artifact

A fresh checkout can validate the frozen data and regenerate the committed evidence from raw model outputs:

```bash
ruff check src tests scripts
mypy src/probe_scent
pytest -q
probe-scent validate-data --receipt /tmp/probe-scent-validation.json
probe-scent audit-release
python -m probe_scent.artifact \
  --config configs/v1.yaml \
  --result-dir results/v1
```

The final command regenerates the canonical analysis and figures in a temporary directory and compares their SHA-256 hashes with the committed evidence. A valid checkout returns `PASS`.

## Regenerate the frozen dataset

The canonical scenarios are generated deterministically from `data/v1/base_tasks.json`:

```bash
python scripts/generate_v1.py
probe-scent validate-data --receipt /tmp/probe-scent-validation.json
```

The canonical dataset and shuffled run order are gzip-compressed with `mtime=0`. Protocol hashes are computed over the decompressed JSONL bytes, so recompression does not redefine the logical research artifact.

The required logical hashes are:

```text
scenarios  077e5e1e350957ea7d4c5697b26e165d91f7e26e5568fc9d381f41b05fcb074a
run order  aa625e06455b943b26ab5546f72fb0003795956ba416cbe089cce419ded248c7
```

The validator checks:

- exactly 150 canonical scenarios;
- 30 complete matched base tasks;
- duplicate and missing IDs;
- primary-pair tempting-file identity;
- direct evaluation-language leakage in non-explicit conditions;
- messy/neat length balance;
- the frozen canonical dataset hash.

## Canonical inference environment

The frozen v1 inference configuration is:

```text
backend        ollama
model          qwen3.5:4b-q4_K_M
model digest   prefix 2a654d98e6fb
temperature    0.0
seed           20260809
context        2048
thinking       disabled
max tokens     96
```

Install Ollama using its official installer for your platform, then pull the frozen model:

```bash
ollama pull qwen3.5:4b-q4_K_M
ollama list
```

Before inference, Probe Scent queries the local Ollama registry and refuses to run if the pulled model digest does not begin with the frozen prefix. Every raw result stores the full model digest, Ollama version, inference settings, prompt hash, dataset hash, run-order hash, run ID, and timestamps.

## Sequential canonical rerun

The canonical evidence is already frozen, so rerunning inference creates a replication and must not overwrite `results/v1` on the release line. To reproduce the execution behavior in a separate output path:

```bash
python -m probe_scent.run \
  --config configs/v1.yaml \
  --output /tmp/probe-scent-replication.jsonl
```

If interrupted:

```bash
python -m probe_scent.run \
  --config configs/v1.yaml \
  --output /tmp/probe-scent-replication.jsonl \
  --resume
```

The runner is append-only and refuses to overwrite an existing file unless `--overwrite` is explicitly supplied.

## Historical canonical execution

The committed v1 evidence was executed as five independent 30-cell shards using the identical frozen configuration. Every shard had to contain 30 valid scenario IDs before upload. The aggregation job then required the exact 150-ID canonical set before analysis was allowed to run.

The two workflows remain in `.github/workflows/` for reproducibility:

- `run-canonical.yml` executes the sequential protocol;
- `run-canonical-parallel.yml` executes the five-shard protocol.

Both are manual-only after the evidence freeze. Ordinary pushes and pull requests cannot rerun canonical inference.

## Recompute analysis from committed raw evidence

```bash
python -m probe_scent.analyze \
  --config configs/v1.yaml \
  --raw results/v1/raw/attempts.jsonl \
  --output-dir /tmp/probe-scent-analysis

python -m probe_scent.figures \
  --config configs/v1.yaml \
  --raw results/v1/raw/attempts.jsonl \
  --output-dir /tmp/probe-scent-analysis/figures
```

The authoritative committed outputs are under `results/v1/`. Do not rewrite them in place for exploratory analysis.

## Artifact verification contract

A canonical `PASS` requires:

- all 150 expected scenario IDs;
- the frozen dataset and run-order hashes;
- the frozen prompt hash and protocol version;
- the frozen Ollama backend, requested model, model digest prefix, and inference settings;
- one consistent backend version and model digest across the canonical evidence;
- the passing 30-pair manual audit receipt;
- all expected analysis tables and figures;
- a valid SHA-256 manifest;
- exact regeneration of committed derived evidence.

`probe-scent audit-release` adds repository-level checks for version consistency, required release files, exact dependency pins, manual-only canonical workflows, completed-evidence status, and stale pre-Ollama documentation.
