# Asset animation — getting a rig and clips made, bought or retargeted

**Read this when** a character needs a rig or clips and none exist yet, when choosing an
auto-rigging or motion provider, when motion data's licence matters, when clips made for one
skeleton must play on another, or when exporting and checking an animated file.

Verified against three@0.186.1 and the providers' public documentation, re-stated
2026-09-27 from reads recorded on 2026-09-19. Provider prices and limits move — re-read the
provider's page before quoting one to a person.

## Contents

- Order of work
- Auto-rigging providers
- Motion sources and their licences
- Retargeting offline
- Export
- The animation QA gate
- Sources

## Order of work

1. **Decide the technique first** (the table in this skill's body). A rig ordered for a body
   that should have been morph or VAT work is money spent on the wrong question.
2. **Check riggability before paying for a rig.** A body that is not a clean humanoid in a
   T/A pose fails auto-rigging, or produces a rig nobody can animate.
3. **Rig once, clip many.** Clips are ordered against the rig's task or file; a new rig
   invalidates every clip made for the old one.
4. **Map every clip to the canon** (`clip-canon.md` in this skill) at import.
5. **Export, then run the QA gate below.** Nothing is "done" at delivery; it is done when it
   plays correctly in the target runtime.

With Asset Foundry present, steps 2–4 are one order on its animated-character recipe, and
riggability is checked by the service before it spends; follow its skill rather than calling
a provider. The rest of this file is how the same work is done, or judged, without it.

## Auto-rigging providers

| Provider | What it rigs | Input requirements | Output | Recorded cost |
|---|---|---|---|---|
| Meshy API | **humanoid biped only** (non-humanoid → `422 Pose estimation failed`); quadruped and "Smart Rig" exist in its web app only | textured **GLB**, humanoid, facing **+Z**, ≤300 000 faces, `height_meters` | rigged GLB/FBX plus basic walking/running | 5 credits rig (API needs a paid plan; ~$0.02/credit on Pro) |
| Tripo API | 7 skeleton types: biped, quadruped, hexapod, octopod, avian, serpentine, aquatic; bone naming `tripo` or `mixamo` | a Tripo model task; run its **free rig-check** first — it reports riggability and the recommended rig type | GLB with baked animation, or FBX; several clips per call | 25 credits rig, 10 per clip (~$0.01/credit) |
| Mixamo (Adobe) | humanoid, auto-rig in the browser | upload FBX/OBJ, place markers by hand | FBX with a Mixamo skeleton | browser-only, no API — a human step |
| Blender (headless) | whatever a script builds; Rigify metarig for humanoids | a scripted pipeline | anything Blender exports | local compute only |

Limits worth knowing before an order: Meshy keeps generated results for a limited period
(re-download and store them), queues concurrent tasks per account tier, and returns textures
of at least 2k; Tripo's rig v2.5 gives non-biped skeletons locomotion presets only.

## Motion sources and their licences

| Source | What you get | The licence question to answer before shipping |
|---|---|---|
| Provider presets (Meshy library, Tripo presets) | canned clips on the provider's rig | the provider's terms for generated output on your plan |
| Meshy text-to-motion | a clip from a prompt (FBX or BVH, 2–10 s) | the provider's output terms; the only text-to-motion of the two |
| Mixamo | a large humanoid clip library | Adobe's terms for Mixamo content, read for your use |
| Mocap libraries and marketplaces | high-quality clips | per-pack licence: redistribution in a web build is often a separate right |
| Research motion models | generated clips | models trained on research-only mocap datasets inherit that restriction; record it and ask before shipping commercially |
| Hand-keyed | exactly what you need | yours |

Record for every clip: source, licence, the four uses it permits (evaluation, internal,
redistribution, commercial) and who decided. An unknown answer is a refusal, not permission.

## Retargeting offline

Retarget once at build time rather than every session at runtime when the clip set is fixed:

1. Load both skeletons in Blender (or three.js in Node with `SkeletonUtils.retargetClip`).
2. Map bones source → target by name; the hips carry translation, everything else rotation.
3. Drop horizontal hip translation for locomotion (in place); keep vertical bob.
4. Bake to the target skeleton at 30 fps and export into the character's GLB.
5. Play it next to a clip authored on the target: feet, hands and spine should read the same.

Runtime retargeting (`SkeletonUtils.retargetClip`) is in `runtime-patterns.md` in this skill.

## Export

- glTF binary, metres, +Y up, facing +Z; clips baked, 30 fps.
- **Four influences per vertex**, renormalised — three.js drops a second weight set.
- In place unless the clip is an `_rm` clip.
- Optimisation keeps skins: `gltf-transform optimize` does not flatten skinned or animated
  nodes; `gltf-transform resample` removes redundant keyframes losslessly;
  `gltfpack -af 30` resamples.
- Name clips canonically in the file when you own it; otherwise map at import.

## The animation QA gate

| Check | How | Verdict |
|---|---|---|
| File is valid glTF | `npx @gltf-transform/cli validate model.glb` | exit status and messages |
| Clips present and named | `npx @gltf-transform/cli inspect model.glb` → animations table vs the canon | a diff of names |
| Influences ≤ 4 | inspect: no `JOINTS_1`/`WEIGHTS_1` attributes | present = fail |
| Every clip plays | load in the target runtime or a glTF viewer; watch each once | seen by whom, when |
| Loops have no seam | watch two cycles of each looping clip | pop = fail |
| No bind-pose snap | watch the end of every one-shot, `death` clamped | snap = fail |
| No foot sliding | move at gameplay speed with `timeScale` derived from authored speed | slide = fail |

Every row that needs eyes and did not get them is `NOT_RUN`, stated as such.

## Sources

- Meshy: <https://docs.meshy.ai/en/api/rigging>, <https://docs.meshy.ai/en/api/animation>,
  <https://docs.meshy.ai/en/api/text-to-motion>, <https://docs.meshy.ai/en/api/pricing>,
  <https://help.meshy.ai/en/articles/16231707-how-to-create-3d-animation-with-auto-rigging>.
- Tripo: <https://developers.tripo3d.ai/en/docs/animations-rig-check>,
  <https://developers.tripo3d.ai/en/docs/animations-rig>,
  <https://developers.tripo3d.ai/en/docs/animations-retarget>,
  <https://developers.tripo3d.ai/en/pricing>.
- three.js r186: GLTFLoader attribute map (`JOINTS_0`/`WEIGHTS_0` only);
  `examples/jsm/utils/SkeletonUtils.js` (`retargetClip`).
- gltf-transform 4.5.0 (`flatten` skips skinned and animated nodes; `resample`); gltfpack 1.3.0
  (`-af`).
