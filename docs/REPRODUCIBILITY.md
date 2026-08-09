# Reproducibility

## Offline validation

A fresh checkout can verify the complete frozen research design without network access or an API key after dependencies are installed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
probe-scent validate-data
python -m probe_scent.run --config configs/v1.yaml --dry-run
```

The dataset validator checks pair completeness, duplicate IDs, direct evaluation-cue leakage, primary-pair tempting-file identity and the frozen logical dataset hash.

The canonical dataset and shuffled run order are reproducibly compressed with gzip `mtime=0`. Their protocol hashes are computed over the decompressed JSONL bytes, so recompression does not redefine the logical research artifact.

Regenerate the frozen data from the 30 structured base tasks with:

```bash
python scripts/generate_v1.py
```

The resulting logical hashes must be:

```text
scenarios  077e5e1e350957ea7d4c5697b26e165d91f7e26e5568fc9d381f41b05fcb074a
run order  aa625e06455b943b26ab5546f72fb0003795956ba416cbe089cce419ded248c7
```

## Live canonical run

The live run requires an OpenAI API key and uses the model frozen in `configs/v1.yaml`.

```bash
export OPENAI_API_KEY=...
python -m probe_scent.run \
  --config configs/v1.yaml \
  --output results/v1/raw/attempts.jsonl
```

If interrupted, continue without re-running valid scenarios:

```bash
python -m probe_scent.run \
  --config configs/v1.yaml \
  --output results/v1/raw/attempts.jsonl \
  --resume
```

The runner refuses to overwrite an existing evidence file unless `--overwrite` is explicitly supplied.

## Analysis

Only after all 150 canonical scenario IDs have valid raw outputs:

```bash
python -m probe_scent.analyze \
  --config configs/v1.yaml \
  --raw results/v1/raw/attempts.jsonl \
  --output-dir results/v1

python -m probe_scent.figures \
  --config configs/v1.yaml \
  --raw results/v1/raw/attempts.jsonl \
  --output-dir results/v1/figures

python -m probe_scent.artifact \
  --result-dir results/v1 \
  --write-manifest
```

## Final verification

```bash
python -m probe_scent.artifact \
  --config configs/v1.yaml \
  --result-dir results/v1
```

A canonical `PASS` requires:

- all 150 expected scenario IDs;
- the frozen dataset hash;
- the frozen shuffled run-order hash;
- the frozen prompt hash;
- the frozen protocol version;
- the frozen requested model;
- a passing 30-pair manual audit receipt;
- all expected analysis tables and figures;
- a valid SHA-256 manifest;
- exact regeneration of the committed derived evidence.

Before live evidence exists, the verifier returns `INCOMPLETE`. It never interprets absent model outputs as a successful artifact.

## GitHub Actions

`.github/workflows/ci.yml` runs the offline gates on Python 3.11 and 3.12.

`.github/workflows/run-canonical.yml` performs the canonical live run. It commits partial append-only raw attempts back to the selected branch so reruns genuinely resume only missing scenarios. Once all 150 scenarios are valid, it generates and verifies the evidence bundle and commits the verified result.
