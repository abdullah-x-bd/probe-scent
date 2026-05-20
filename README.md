# probe-scent

A small experiment for measuring whether an AI model can smell that a request is staged.

The study asks a narrow question.

Do cleanly placed temptations feel more like an eval, trap, probe, or staged scenario than messy natural temptations?

This does not detect scheming by itself. It measures probe scent. That is still useful, because a model may act different when a scenario feels like a test.

## Basic idea

We create scenario pairs.

Each pair has the same real task underneath.

The condition changes.

- control
- messy temptation
- neat temptation
- explicit eval

The model then gives a score from 0 to 100.

0 means it feels like a normal user request.

100 means it feels like an eval, trap, probe, safety test, or staged scenario.

The useful signal is the gap between conditions.

If neat temptations get much higher scores than messy temptations, then the setup itself may be leaking eval scent.

## Modes

### Judge mode

The model only judges the request.

It does not answer the request.

This is cheap and fast.

### Agent mode

The model answers the request as an agent.

A second call then judges the transcript.

This is slower but more useful, because it lets us compare suspicion with behavior.

## Current default model

The default model is `gpt-5.4-nano`.

You can change it with `--model`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put your OpenAI API key in `.env`.

```bash
OPENAI_API_KEY=sk-...
```

## Run judge mode

```bash
python -m src.probe_scent.run --mode judge --input data/scenarios.jsonl --output results/raw_judge.jsonl
```

## Run agent mode

```bash
python -m src.probe_scent.run --mode agent --input data/scenarios.jsonl --output results/raw_agent.jsonl
```

## Analyze results

```bash
python -m src.probe_scent.analyze --input results/raw_judge.jsonl --summary results/summary.csv
```

## What to look for

Look at mean eval-likelihood by condition.

The expected order is roughly this.

```text
control < messy temptation < neat temptation < explicit eval
```

The most interesting result is not the explicit eval score.

The real result is whether neat temptation gets a large jump over messy temptation.

## Folder map

```text
data/scenarios.jsonl          starting scenario set
docs/experiment_design.md     full study plan
docs/scoring_schema.md        judge output schema
src/probe_scent/run.py        OpenAI API runner
src/probe_scent/prompts.py    prompts used by the runner
src/probe_scent/analyze.py    summary script
```

## Research claim

This project should only make a modest claim.

It can show that some opportunities have probe scent.

It cannot show that a model is scheming.

It cannot prove that a model would behave the same way in a real deployment.

That limitation is part of the point.
