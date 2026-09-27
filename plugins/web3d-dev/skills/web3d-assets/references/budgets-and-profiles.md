# Budgets and target profiles — the numbers every gate reads

**Read this when** a project has no written target profile, when setting or checking a
budget for a model, texture or scene, or when deciding between LOD, instancing and batching.

Verified against three@0.186.1 and @gltf-transform/cli 4.5.0 on 2026-09-27. The profile
fields mirror what Asset Foundry's target profiles gate on, so one profile serves both paths.

## Contents

- The profile file
- Deriving the numbers — measure, then divide
- Starting assumptions (replace them)
- Checking an asset against the profile
- LOD, instancing, batching
- Sources

## The profile file

Keep one per target in the project, e.g. `docs/3d/target-profiles/web-mobile.json`:

```json
{
  "id": "web-mobile",
  "measured_on": "Pixel 7, Chrome 140, 2026-09-27",
  "frame_budget_ms": 16.6,
  "scene": { "max_triangles": 0, "max_draw_calls": 0, "max_texture_memory_mb": 0 },
  "asset": {
    "max_triangles": 0,
    "max_file_mb": 0,
    "max_texture_px": 1024,
    "materials_max": 1,
    "pbr_channels": ["base_color", "normal", "metallic_roughness"]
  },
  "loader": {
    "reader": "three GLTFLoader r186",
    "extensions_allowed": ["KHR_texture_basisu", "EXT_meshopt_compression", "KHR_mesh_quantization"]
  },
  "animation": { "skinning": true, "max_joints": 0, "max_influences": 4, "fps": 30, "vat_supported": false },
  "scale": "real_metres"
}
```

Zeros mean *not measured yet* — a gate reading a zero must report `NOT_RUN`, never pass.
`extensions_allowed` is the loader's truth, not a wish: drei's `useGLTF` and three's own
GLTFLoader differ (see `gltf-pipeline.md` in this skill).

## Deriving the numbers — measure, then divide

1. Pick the weakest device the product must run on, and its browser.
2. Build a representative scene: the real camera, lights, post-processing and the expected
   number of objects, with placeholder assets.
3. Measure frame time (the renderer's Inspector or timestamp queries — `web3d-runtime`) while
   raising triangles and draw calls until the frame budget is spent with ~20% headroom.
4. That ceiling is the **scene** budget. Divide it by the expected visible count per asset
   class for the **asset** budget; texture memory the same way.
5. Record the device, browser and date in `measured_on`. A budget without its measurement is a
   guess that looks like a standard.

## Starting assumptions (replace them)

Until a measurement exists, these are placeholders to start work with — not standards, not
verified, and not to be quoted as either:

| Class | Placeholder triangles | Placeholder texture |
|---|---|---|
| Hero character, desktop | tens of thousands | 2048 px |
| Hero character, mobile | under ~15k | 1024 px |
| Prop, repeated | hundreds to low thousands | 512–1024 px, atlased |
| Background set piece | budgeted from the scene total | tiled materials |

gltf-transform's `optimize` defaults textures to 2048 px — often too large for mobile, which is
why the profile, not the tool default, sets `--texture-size`.

## Checking an asset against the profile

```bash
npx @gltf-transform/cli inspect asset.glb > asset.inspect.txt
```

Compare, and record each as PASS / FAIL / NOT_RUN with the measured value:

- triangles ≤ `asset.max_triangles`; file size ≤ `asset.max_file_mb`
- every texture ≤ `max_texture_px`; colour textures sRGB, data textures linear
- every extension used ∈ `loader.extensions_allowed`
- skinned only if `animation.skinning`; joints ≤ `max_joints`; no second weight set
- scale in metres when `scale` says so — a normalised radius is a different profile

## LOD, instancing, batching

| Situation | Use | Note |
|---|---|---|
| Same mesh many times | `InstancedMesh` (or `instance` in gltf-transform) | lower `.count` at runtime to draw fewer; call `computeBoundingSphere()` after moving instances or culling is wrong |
| Many different static meshes, one material | `BatchedMesh` | per-object culling and sorting on by default; **no skinning** |
| Big object seen near and far | `THREE.LOD` with `addLevel(object, distance, hysteresis)` | simplify offline (`simplify`) per level |
| Characters in a crowd | see `web3d-animation` | skinning and batching do not combine |

Remember the scene budget counts every instance: sixteen instances of a 5k-triangle prop are
80k triangles at the vertex stage.

## Sources

- three@0.186.1: `src/objects/InstancedMesh.js:113,149-164`, `src/objects/BatchedMesh.js`
  (no skin code; `perObjectFrustumCulled`, `sortObjects`), `src/objects/LOD.js:64-83`.
- @gltf-transform/cli 4.5.0 `src/cli.ts` (`optimize --texture-size` default 2048; `inspect`).
- Asset Foundry target-profile fields (budgets per asset and scene, allowed loader extensions,
  skinning, joints and influences, VAT support) — the private service's profile schema,
  mirrored here by field name only.
