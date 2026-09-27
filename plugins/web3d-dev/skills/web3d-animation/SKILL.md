---
name: web3d-animation
description: >-
  Use when something must move in a realtime 3D web scene with three.js or React Three Fiber —
  character rigs and clips, blending and state transitions, retargeting, root motion and foot
  sliding, morph targets, crowds and instanced animation, vertex-animation textures,
  procedural or GPU-driven motion. Carries a two-sided animation protocol: the asset half (rig,
  clip canon, export, budgets) and the runtime half (clock, mixer, blending, GPU paths, pause,
  reduced motion). Triggers - "animate the character" / "анимируй персонажа", "blend idle walk
  run" / "переход между анимациями", "retarget Mixamo" / "ретаргетинг", "foot sliding" / "ноги
  скользят", "crowd of characters" / "толпа персонажей", "AnimationMixer", "morph targets" /
  "морф-таргеты". NOT for scroll or UI motion on a page (sheleg-design), rendered video
  (hyperframes, remotion), or Unity and Unreal animators.
license: MIT
compatibility: >-
  Any agent host. Facts are pinned to three@0.186.1 (r186). Uses @gltf-transform/cli through
  npx when present for inspection; without it, reads the glTF JSON directly. A browser run is
  needed to call motion verified — without one the verdict is NOT_RUN, never PASS.
metadata:
  author: ssheleg
  version: "0.1.1"
---

# web3d-animation — decide how it moves, then make both halves agree

An animated scene fails at the seam between two people who never met: whoever made the
clip and whoever plays it. The clip is named `Armature|mixamo.com|Layer0`, the code asks for
`run`, the character slides, the death pose snaps back to a T-pose. This skill is the
contract across that seam — the **asset half** and the **runtime half**, and the canon they
share (`references/clip-canon.md`).

## First action — inspect, then report

1. **Version.** Read `three` in `package.json`. Every API fact here is verified against
   three@0.186.1; on an older release, check `references/runtime-patterns.md` → *Version notes*
   before trusting a name.
2. **What moves.** List each moving thing and what drives it now: a clip, code, a shader,
   physics, nothing yet.
3. **What exists.** For every `.glb`/`.gltf`: `npx @gltf-transform/cli inspect <file>` —
   animations (names, duration, channels), skins (joint count), morph targets, and whether the
   file is compressed. Compare clip names against the canon.
4. **Where assets will come from.** An Asset Foundry tool (`foundry_capabilities`) or the
   `asset-foundry` skill in this session → ordering goes through it; otherwise
   `web3d-assets` decides the source.

Report one table — *object · technique now · technique needed · gap* — and exactly ONE next
action. Detect; do not ask what you can read.

## Step 1 — choose the technique before touching an asset

| What moves | Technique | Why this and not the next row |
|---|---|---|
| Rigid objects: doors, props, cameras, 3D UI | transforms in the frame loop, or a keyframe clip if authored | a skeleton for a rigid body is pure cost |
| Ambient surface motion: foliage, cloth sway, water, pulse | TSL on the material: `time`, `positionLocal.add(offset)` | GPU-only, no CPU per instance |
| Faces, blendshapes, corrective shapes | morph targets | skinning cannot express a smile |
| A character with authored motion | `SkinnedMesh` + clips through `AnimationMixer` | the standard path; everything below is an optimisation of it |
| Many copies, **same pose** | skinned instancing, one mixer update for all | one skeleton evaluation drives every instance |
| Many copies, **individual timing** | per-instance `mixer.setTime` + one compute skinning pass | CPU cost grows with instance count — measure, then stop |
| Thousands, no interaction, fixed motion | vertex-animation texture (VAT) in TSL | no skeleton at runtime; not built into three.js — you write it |
| Reaction to forces: falls, hits, ragdolls | physics on a fixed step | authored clips cannot react |
| Particles, flocks, simulations | compute (`web3d-runtime`) | not animation data at all |

**`BatchedMesh` cannot skin.** Batch the props, never the characters.

## Step 2 — the asset half

Work this list per character; each line is a check, not advice.

1. **Rig.** T-pose or A-pose, metres, +Y up, facing +Z. Auto-rigging services rig
   **humanoids**; a non-humanoid gets locomotion at best — decide procedural/morph/VAT for it
   in Step 1 instead of ordering a rig that cannot be made.
2. **Canon.** Every clip gets a canonical name, loop mode and displacement rule from
   `references/clip-canon.md`. Provider names are mapped once, at import.
3. **Source.** Order through Asset Foundry when present (check rig feasibility first — a rig
   check is cheaper than a rig of a sphere); otherwise the provider table and licence rules in
   `references/asset-animation.md`. Motion data licences differ from mesh licences — record
   both.
4. **Retarget** clips made for another skeleton (`references/asset-animation.md` →
   *Retargeting*), or at runtime with `SkeletonUtils.retargetClip`.
5. **Export.** GLB, 30 fps, in place, **≤4 influences per vertex** (three.js reads one
   `JOINTS_0`/`WEIGHTS_0` set and drops the rest silently), stable bone names.
6. **Budget.** Joints, influences, clip count and file size against the target profile
   (`web3d-assets`). r186 lifts the uniform-buffer bone cap, so the budget is performance, not
   a hard limit.
7. **Gate.** `npx @gltf-transform/cli validate` passes; every clip plays in a viewer; loops
   have no seam; the feet stay planted at the clip's intended speed; no clip ends in bind pose.
   A gate nobody ran is `NOT_RUN`.

## Step 3 — the runtime half

1. **One clock.** `new Timer()` (core in r186; `Clock` is deprecated), `timer.connect(document)`
   so a hidden tab does not return a giant delta, `timer.update()` once per frame, and a
   clamped `dt` (a pattern — e.g. `Math.min(dt, 0.1)`) for the mixer. Physics runs on its own
   fixed-step accumulator fed by the same clock.
2. **Frame order:** `mixer.update(dt)` → compute passes → render. A compute skinning pass
   reads bone matrices the mixer just wrote.
3. **One mixer per character root.** Copies come from `SkeletonUtils.clone` — a plain
   `.clone()` leaves the skeleton bound to the original's bones. A retargeted clip plays on a
   mixer rooted at the `SkinnedMesh` itself.
4. **Transitions.** Locomotion changes crossfade (`crossFadeTo(next, duration, warp)`);
   `syncWith` keeps cycle phase when switching walk↔run. One-shots are `LoopOnce`; listen for
   `'finished'` **on the mixer**, not the action. `death` sets `clampWhenFinished = true`.
5. **Layers.** Breathing, aiming and upper-body gestures are additive clips
   (`AnimationUtils.makeClipAdditive`) over the base locomotion, weighted, not a second state.
6. **Root motion and sliding.** In-place clips + code-driven movement; drive `timeScale` from
   actual speed over the clip's authored speed, or feet slide. A `_rm` clip's hip translation is
   extracted by code — three.js has no root motion.
7. **Do less off screen.** Skip or thin `mixer.update` for characters outside the frustum or
   far away; the tab-hidden case is already handled by `Timer`.
8. **Reduced motion.** Under `prefers-reduced-motion`, stop decorative motion (ambient loops,
   camera drift, idle flourishes) and keep motion that carries meaning (a hit, a state change).
   The page-level rule is `sheleg-design`'s degrade-to-calm; a 3D scene reads the same signal.
9. **Tear down.** `stopAllAction`, `uncacheRoot`, then dispose geometry and materials.

Code for each step: `references/runtime-patterns.md`.

## Gotchas — each one silent until someone looks

- A finished `LoopOnce` action with `clampWhenFinished = false` **disables itself**: the body
  snaps to bind pose. Death and final poses need the clamp.
- `'finished'` and `'loop'` fire on the **mixer**, the only event dispatcher here —
  `AnimationAction` has no `addEventListener`, so attaching one to an action throws.
- `positionNode = …` replaces the position **after** skinning, morphs and instancing were
  applied. `positionLocal.add(x)` keeps the animation; `positionGeometry.add(x)` throws it away.
- A second set of skin weights in the glTF is **dropped**, not merged — renormalise to 4.
- drei's `useAnimations` and R3F's `useFrame` pass an **unclamped** delta from a deprecated
  `Clock`; after a hidden tab, every character jumps. Clamp inside your frame callback.
- `KHR_animation_pointer` (animating material or light properties from glTF) is **not built
  into** GLTFLoader — it needs a separately registered plugin.
- `sheleg-design` bans crossfades between **scroll sections**. That rule is about page motion;
  crossfading **character clips** is the correct, standard transition.

## When something is missing

- **No browser or headless GPU in this host** → implement and validate structure, then state
  the visual gates as `NOT_RUN` with what a person must look at. Never report motion verified
  from reading code.
- **`@gltf-transform/cli` unavailable (no network, no npx)** → read the glTF JSON (`.gltf`
  directly; `.glb` chunk 0) for `animations`, `skins` and `targets`; say which checks that
  cannot do (validation, compression-aware inspection).
- **Asset Foundry absent** → source by hand through `web3d-assets`; its principles still apply.
- **The operator's decision is needed** (a paid order over budget, a licence of unknown scope) →
  stop at that line and name it; do not route around it.

## References

| Read | When |
|---|---|
| `references/clip-canon.md` | naming, looping or loading any clip; mapping provider names — the shared contract with `web3d-assets` |
| `references/runtime-patterns.md` | writing the loop, the mixer, transitions, layers, retargeting, crowds, morph instancing, VAT, R3F |
| `references/asset-animation.md` | getting a rig or clips made or bought: providers, rig checks, motion licences, retargeting pipeline, export and QA |

The runtime (renderer, TSL, compute, performance) is `web3d-runtime`; the file pipeline and
budgets are `web3d-assets`. This skill owns motion only.
