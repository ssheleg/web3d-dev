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
