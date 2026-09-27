# Evaluations

Three layers, kept apart because they prove different things.

| Layer | File | What it proves | What it does not |
|---|---|---|---|
| Trigger definitions | `triggers.json` | which requests should and should not select this pack, split into train and validation halves | that an agent actually routes that way |
| Scenario definitions | `scenarios.json` | the behaviour a correct answer must show, per scenario | that any model produced it |
| Executed probes | `RESULTS.md` | baseline (no skill) against candidate (skill text supplied) on frozen prompts, with the rubric verdicts | runtime routing among installed neighbours, or that the code runs in a browser |

`python3 test/evals_validate.py` checks the shape of the first two (both classes present in
each half, ids unique, at least three expected behaviours per scenario).
