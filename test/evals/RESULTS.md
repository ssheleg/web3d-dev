# Evaluation results

## 2026-09-27: isolated planning probes (n = 1 per arm)

Inputs, outputs and the runner are in
[`docs/evidence/verification/2026-09-27-probes/`](../../docs/evidence/verification/2026-09-27-probes/)
(`run_probes.sh`). Local Claude CLI, default host model, run from an empty directory with
`--tools "" --disable-slash-commands --strict-mcp-config --setting-sources ""`. Baseline received
the scenario query only; candidate received the same query with the skill body and one named
reference appended to the system prompt. This measures the answer's content, **not** runtime
routing among installed neighbours and **not** that any code runs in a browser.

Graded by an independent reader (a separate agent, not the author) against each
`expected_behavior` line in `scenarios.json` and against the docs study rows.

| Arm | MET | PARTIAL | MISSED | Factual errors |
|---|---|---|---|---|
| Baseline (no skill) | 5 | 5 | 2 | 3 (Clock offered as current in r186; `ktx` ≥ 4.3 instead of 4.4; a garbled drei signature note) |
| Candidate (skill text) | 10 | 1 | 1 | 1 (claimed `optimize` uses one codec for all KTX2 textures) + 1 imprecise (an action listener "never runs" — it throws) |

Per scenario, MET out of 4: s01 runtime 2 → 3; s02 animation 3 → 4; s03 assets 0 → 3.
Both arms missed the sprite particle pattern (s01) and the npm-gltfpack texture limitation (s03).

**Integrity caveats, stated by the grader.** Tools were disabled in every arm, yet one candidate
output (s01) and one baseline output (s03) narrated tool calls and results that could not have
happened, and three outputs asserted an "empty working directory" they could not have checked.
With one run per arm this is a signal, not a measured improvement.

**What changed because of it.** Both candidate errors were facts the skill did not state:
`gltf-pipeline.md` now says `optimize --texture-compress ktx2` splits UASTC (normal, occlusion,
metallic-roughness) from ETC1S (the rest), and `web3d-animation` now says an `AnimationAction`
has no `addEventListener` (docs study rows 3.24 and 4.25, both read from source). The probes
were not re-run after these edits.

## 2026-09-28: candidate arms re-run after the fixes

Same method as above, candidate arm only (the baseline had not changed), one draw per
scenario; the first s03 draw was discarded because it contained no answer — two tool-call
blocks emitted as text and an invented tool result — and is kept as
`s03-candidate.draw1-tool-hallucination.md`. Graded by an independent reader.

| Scenario | MET out of 4 (was) | What moved |
|---|---|---|
| s01 runtime | 3 (3) | sprite pattern still missed |
| s02 animation | 3 (4) | never said three.js has no built-in root motion (docs row 3.19) |
| s03 assets | 2 (3) | npm-gltfpack limitation still missed; validation "after" was fabricated |
| **Total** | **8 MET / 3 PARTIAL / 1 MISSED** (10 / 1 / 1) | |

The two errors fixed after the first run did not recur: the KTX2 codec split now matches docs
row 4.25, and the event wording matches row 3.24. New imprecisions: `getDelta()` shown without
`timer.update()` (row 1.26) and `toAttribute()` called "the" official instanced pattern (rows
2.13, 2.15).

**Integrity got worse, and it is the finding of this run.** With tools disabled, all three
outputs claimed to have observed an environment, and the s03 answer is a complete fabricated
execution report ("80 MB → 30 MB", "validates clean", "no `ktx` CLI on this machine"). These
draws were made on 0.1.1's text, **before** 0.1.2 added the rule to every skill's *When
something is missing* — with no tools, write commands and code, never their results. Whether
that rule changes the behaviour is not measured yet; n = 1 per arm is a signal, not a
regression measurement.
