# Spec — web3d-dev 0.1.0

*Written 2026-09-27, before the skills. Operator request (verbatim intent): work
through `dgreenheck/webgpu-claude-skill`; put everything we know about 3D — the
Asset Foundry services and principles, the tools — into the family's skills, so an
agent knows it can use Asset Foundry when present and knows the principles when
not; and look separately at how to work with 3D animation. "Plan in detail and do
it to the end autonomously."*

## Contents

- The problem
- Baseline failures (measured, not imagined)
- Decisions
- Contract with target projects
- Requirements
- Out of scope

## The problem

The family has no owner for realtime 3D on the web. `sheleg-design` owns one
particle-field pattern for landing-page heroes; `xr-dev` owns the Quest product
lifecycle and carries 3D only as checklists. Three.js on WebGPU, TSL shaders, the
glTF asset pipeline, character animation and web physics have no lane — measured by
reading every member (source ledger below), not assumed.

Asset Foundry — the operator's local asset-generation service — is known to one
private skill whose endpoint, status and animation guidance have drifted from the
service itself.

## Baseline failures (measured, not imagined)

| # | Observed 2026-09-27 | Answered by |
|---|---|---|
| B1 | A popular public WebGPU skill (1.2k stars) teaches `material.positionNode = buffer.element(instanceIndex)` for instanced particles — the instance geometry collapses to a point; the working form adds the buffer to the geometry position | `web3d-runtime` |
| B2 | The same skill reads storage buffers back with a render-target readback call, uses atomics on a plain array without the atomic conversion, and hooks the backend device directly for device loss (absent on the WebGL2 fallback) | `web3d-runtime` |
| B3 | The same skill has zero content on AnimationMixer, skinning, morph targets or glTF clips; its Cursor rules contradict its own docs (deprecated compute and post-processing names) | `web3d-animation`, drift test |
| B4 | Asset Foundry's animated-enemy recipe requests clip names (`attack`, `defeat`) the rigging provider's preset list does not contain; joint, influence, root-motion and sample-rate limits are declared in profiles and read by no code; a VAT bake is produced for a consumer that cannot decode it | `web3d-animation`, `asset-foundry` skill |
| B5 | The asset-foundry skill names a server `foundry` behind "the configured gateway"; the registration is `asset-foundry` on a gateway that is down while the service itself answers `/health` on another port; the skill says nothing about checking or starting it | `asset-foundry` skill |
| B6 | No family skill says what to do when Asset Foundry is absent — the principles it enforces (target profile, gate twice, manifest, rights, spend caps) exist only inside the service | `web3d-assets` |
| B7 | The family's only animation doctrine (`sheleg-design`) bans crossfades — correctly, for scroll-section morphs; an agent applying it to character clips would forbid the standard AnimationMixer transition | `web3d-animation` boundary |

Sources for B1–B3: clone of the public repo at `af2319b` read in full on 2026-09-27,
checked against three.js docs. B4–B5: `~/DATA/asset-foundry` read on 2026-09-27
(`pipelines/enemy-animated.yaml`, `foundry/shared/profiles.py`, `docs/REMOTE-MAC.md`,
`skills/asset-foundry/SKILL.md`). B7: `sheleg-design` `SKILL.md` motion principles.

## Decisions

1. **A new member, `web3d-dev`, three skills split by the question.**
   `web3d-runtime` — *how the scene runs* (renderer, shaders, compute, frame loop,
   performance, fallback). `web3d-assets` — *how a 3D asset gets from a source to
   the frame within budget* (glTF pipeline, compression, budgets, loading, sourcing,
   Asset Foundry). `web3d-animation` — *how a thing moves* (the animation protocol:
   asset half and runtime half). Not a router: the family measured that an eleventh
   router widens routing across all ten (`lib/packs.js`).
2. **Original text only.** The public skill's README claims MIT but ships no LICENSE
   file; its ideas are used, its prose is not. Its verified errors become our
   gotchas, which is the most useful thing it teaches.
3. **Asset Foundry is optional and private.** The public pack states the principles
   and the public facts about providers; it tells an agent to delegate to the
   `asset-foundry` skill and its `foundry_*` tools when they are present, and how to
   work without them. The service's internals stay in its private skill. The family
   brand rule stands: Foundry is never presented as a released product.
4. **Version-pinned facts.** Every API claim is verified against `three@0.186.1`
   (r186) and the pinned tool versions, recorded in
   `docs/evidence/research/2026-09-27-docs-study.md`; references carry a
   `Verified against` line and the validator requires one pin across the pack.
5. **The animation protocol has two halves with one shared contract** — the clip
   canon (names, in-place vs root motion, rate, loop flags) lives in
   `references/clip-canon.md` inside BOTH skills that need it, validator-checked
   identical (the skills CLI ships only a skill's own directory).
6. **Boundaries by neighbour.** `sheleg-design` keeps how a page looks and moves
   (heroes, scroll motion, degrade-to-calm); `xr-dev` keeps the Quest product and
   its budgets; `asset-foundry` keeps ordering from the service; `hyperframes` /
   `remotion` keep rendered video. Each boundary is a `NOT for` clause on both
   sides.
7. **npm first publish is the operator's step.** The package must exist before
   trusted publishing can be configured, and the first publish needs the owner's
   2FA (`npm whoami` → E401 on 2026-09-27). Until then the umbrella lists the
   member with `npmPublished: false`; GitHub and plugin installs work.

## Contract with target projects

Reads, never writes without being asked:

| Path | Read for |
|---|---|
| `package.json` | three / R3F / drei / physics versions — every API answer is pinned to the project's version, not ours |
| `**/*.glb`, `**/*.gltf` | inspected through `gltf-transform inspect` for budgets and extensions |
| `*.foundry.json`, `**/*.manifest.json` | Asset Foundry project file and delivered manifests, when present |
| `docs/ux/scenarios.md` | whether a scene has a user and a reduced-motion expectation |

## Requirements

| REQ | What must hold | Verified by |
|---|---|---|
| REQ-01 | Repo `ssheleg/web3d-dev` exists, public, MIT, canonical layout, validator with negative self-test, CI running both strict plugin validations | `npm test`, `npm run test:negatives`, strict validate ×2, CI green |
| REQ-02 | `web3d-runtime` covers renderer init and fallback, TSL gotchas-first (B1–B2), compute, post-processing, device loss, frame loop, profiling, R3F on WebGPU, degrade-to-calm | reference ↔ docs-study rows; eval scenarios |
| REQ-03 | `web3d-assets` covers the glTF pipeline, compression, colour spaces, budgets by target, loading and prewarm, LOD and instancing, sourcing (providers, rights, provenance), and Asset Foundry: detect → delegate, or work by its principles by hand | same |
| REQ-04 | `web3d-animation` carries the 3D animation protocol: technique choice, asset half (rig, clips, canon, retarget, budgets, QA) and runtime half (loop, mixer, blending, layering, GPU paths, instancing, pause, reduced motion) | same |
| REQ-05 | No copied text from the public skill; its verified errors appear as gotchas | provenance note in README; review |
| REQ-06 | Trigger and scenario evals exist, including routing against `sheleg-design`, `quest-webxr`, `asset-foundry`, `hyperframes` | `test/evals/*.json`, `evals_validate.py` |
| REQ-07 | `asset-foundry` skill states the real endpoint, the health check and service start, the honest provider status, and the animation recipe with its known gaps; points to `web3d-dev` | its repo's tests; diff review |
| REQ-08 | `sheleg-design` and `xr-dev` name `web3d-dev` at their 3D boundary; released | their gates; release tags |
| REQ-09 | Umbrella lists the member (catalogue, submodule, README, site, counts), `npmPublished: false` until the operator's first publish | umbrella `npm test`, CI |
| REQ-10 | This machine's installs updated: family launcher, Codex plugin, shadow check empty | commands and output |
| REQ-11 | npm publication and trusted publishing configured | **Human step** — operator `npm login` + 2FA, then `npm trust github …` |

## Out of scope

- Unity, Unreal, Godot engine work (Meta and engine-native skills own those).
- Rendered video and motion graphics (`hyperframes`, `remotion`).
- Changing Asset Foundry's service code — its defects found here become board rows
  in its own repository, not edits from this run.
- Merging the unmerged `codex/xr-creative-research` branch in the umbrella; this
  spec cites its proposal (`realtime-graphics`) as prior art only.
