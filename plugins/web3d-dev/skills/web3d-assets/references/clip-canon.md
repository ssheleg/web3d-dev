# Clip canon — the contract between an animated asset and the code that plays it

**Read this when** ordering, sourcing, exporting, renaming or loading animation clips, or
when code looks a clip up by name. This file ships identically in `web3d-assets` and
`web3d-animation`; the validator fails if the two copies differ — edit both in one change.

Verified against three@0.186.1 and the rigging providers' public documentation on
2026-09-27 (sources at the end).

## Contents

- Names
- Loop, clamp and root motion per clip
- Skeleton and export floor
- Provider name mapping
- Sources

## Names

One name per role, lowercase snake case: `<verb>[_<variant>][_<direction>]`.
Code looks clips up by these names only; a provider's own name is mapped once, at import.

| Role | Canonical name | Notes |
|---|---|---|
| Rest | `idle` | variants `idle_alert`, `idle_breath` |
| Locomotion | `walk`, `run`, `sprint` | `strafe_left`, `strafe_right`, `walk_back` |
| Turning | `turn_left`, `turn_right` | in place |
| Jump | `jump_start`, `jump_loop`, `jump_land` | split so air time is code-driven |
| Fall | `fall_loop` | |
| Attack | `attack`, `attack_02`, … | numbered, never named after a weapon the design may change |
| Hit reaction | `hit`, `hit_head`, `hit_body` | |
| Death | `death` | |
| Emote | `emote_<name>` | `emote_wave`, `emote_dance` |

## Loop, clamp and root motion per clip

| Clip | Loop | On finish | Displacement |
|---|---|---|---|
| `idle*`, `walk`, `run`, `sprint`, `strafe_*`, `walk_back`, `jump_loop`, `fall_loop` | `LoopRepeat` | — | **in place** — code or physics moves the character |
| `turn_*`, `jump_start`, `jump_land`, `attack*`, `hit*`, `emote_*` | `LoopOnce` | return to locomotion by crossfade | in place |
| `death` | `LoopOnce` | `clampWhenFinished = true` — otherwise the action disables and the body snaps back to bind pose | in place |

- **In place is the default.** A clip with authored displacement is suffixed `_rm`
  (`attack_lunge_rm`) and its root/hip translation is extracted by code; three.js has no
  built-in root motion.
- A looping clip's first and last pose are equal, or the loop pops.
- Author and resample at **30 fps**. It is the common default of the rigging providers and of
  `gltfpack -af` resampling; mixed rates inside one character make blending jitter.

## Skeleton and export floor

- glTF 2.0 binary (`.glb`), metres, +Y up, character facing **+Z**, rigged in T-pose or A-pose.
- **At most 4 bone influences per vertex.** three.js reads only `JOINTS_0`/`WEIGHTS_0`; a second
  set is dropped silently, so weights must be renormalised to 4 before export.
- Bone names stable across every clip of one character — a clip bound to a renamed bone plays
  nothing and raises no error.
- Every clip of one character lives in the same file as its skinned mesh, or in files that
  share its exact skeleton; otherwise it needs retargeting.

## Provider name mapping

Provider names are data, never code. Map once at import (a table or a rename step), then
use the canonical name everywhere.

| Canonical | Tripo rig v2.5 preset | Tripo rig v1.0 preset | Meshy |
|---|---|---|---|
| `idle` | `preset:idle` | `preset:biped:idle` | numeric `action_id` from its library |
| `walk` / `run` | `preset:walk` / `preset:run` | biped presets of the same names | numeric `action_id`; rigging also returns basic walking/running |
| `jump_*` | `preset:jump` (single clip — split in code or keep as `jump_start`) | — | numeric `action_id` |
| `attack` | `preset:slash`, `preset:shoot` | `preset:biped:slash`, `…:chop`, `…:box_01` | numeric `action_id` (e.g. "Attack") |
| `hit` | `preset:hurt` | `…:hurt`, `…:hit_to_body_01` | numeric `action_id` |
| `death` | **none** — no death preset in v2.5 | nearest is `…:defeat_02` / `defeat_03` | numeric `action_id` |
| `fall_loop` | `preset:fall` | — | numeric `action_id` |
| non-biped | `preset:quadruped:walk`, `preset:hexapod:walk`, `preset:serpentine:march`, `preset:aquatic:march` — locomotion only | — | not supported: rigging is humanoid-only |

Two consequences worth stating before an order is placed:

- A brief asking a provider for `attack` or `death` by that literal name asks for something its
  preset list does not contain. Ask by the provider's name and map it to the canon.
- A non-humanoid creature gets locomotion at best from auto-rigging. Floating, orbiting or
  shape-shifting creatures are procedural, morph-target or VAT work, not a rig order.

## Sources

- three.js r186: `examples/jsm/loaders/GLTFLoader.js:2286-2287` (only `JOINTS_0`/`WEIGHTS_0`),
  `src/animation/AnimationAction.js:771-772` (unclamped finish disables the action); root motion
  absent from `src` and `examples/jsm`.
- Tripo rigging and presets: <https://developers.tripo3d.ai/en/docs/animations-rig>,
  <https://developers.tripo3d.ai/en/docs/animations-rig-check>,
  <https://developers.tripo3d.ai/en/docs/animations-retarget> — read 2026-09-19, re-stated 2026-09-27.
- Meshy rigging and animation: <https://docs.meshy.ai/en/api/rigging>, <https://docs.meshy.ai/en/api/animation>, read as
  recorded on 2026-09-19 and re-stated 2026-09-27 — humanoid-only rigging, numeric `action_id`
  per task, fps 24/25/30/60 with 30 the default.
- gltfpack 1.3.0 `-af` (resample rate, default 30): `gltfpack -h`.
