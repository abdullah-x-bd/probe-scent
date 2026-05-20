# GitHub Actions run guide

The repo has a manual workflow.

File.

```text
.github/workflows/run-probe-scent.yml
```

It needs one repository secret.

```text
OPENAI_API_KEY
```

GitHub path.

```text
Settings > Secrets and variables > Actions > New repository secret
```

After adding it, go here.

```text
Actions > Run probe-scent > Run workflow
```

Default inputs.

```text
mode: judge
model: gpt-5.4-nano
input_file: data/scenarios.jsonl
```

The output is uploaded as a workflow artifact.

```text
results/raw_judge.jsonl
results/summary_judge.csv
```

For the slower run, set mode to agent.
