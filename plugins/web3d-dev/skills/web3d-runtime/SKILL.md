---
name: web3d-runtime
description: >-
  Use when building or fixing a realtime 3D scene on the web with three.js or React Three
  Fiber — WebGPURenderer and its WebGL2 fallback, TSL node materials and shaders, GPU compute
  and particles, post-processing, device loss, the frame loop, profiling and frame-time
  budgets, and degrading to a calm static state. Leads with the silent failures of r186 before
  the API. Triggers - "three.js WebGPU", "TSL", "WGSL", "compute shader" / "компьют-шейдер",
  "particles collapsed" / "частицы схлопнулись", "device lost" / "потеря устройства", "the 3D
  scene is slow" / "3D-сцена тормозит", "React Three Fiber", "R3F", "post-processing" /
  "постобработка", "WebGL fallback". NOT for landing-page heroes and scroll motion
  (sheleg-design), asset files and budgets (web3d-assets), character animation
  (web3d-animation), or a Quest headset session (xr-dev).
license: MIT
compatibility: >-
  Any agent host. Facts pinned to three@0.186.1 (r186), @react-three/fiber 9.8.1 and
  @react-three/drei 10.7.9. A browser with WebGPU (or a headless GPU run) is needed to call a
  visual result verified; without one the verdict is NOT_RUN.
metadata:
  author: ssheleg
  version: "0.1.1"
---

# web3d-runtime — the scene runs, on every GPU it meets, and you can prove how fast

three.js on WebGPU moves quickly: r186 throws where r180 warned, renamed the post-processing
entry point, deprecated `Clock`, and still ships a WebGL2 backend underneath the same API.
Most bugs here are silent — the scene renders, just wrongly. So this skill leads with the
failures, then the patterns.

## First action — inspect, then report

1. **Versions.** `three`, `@react-three/fiber`, `@react-three/drei` from `package.json`. Facts
   here are pinned to r186; on another release, check `references/renderer-and-loop.md` →
   *Version notes* before trusting a name.
2. **Renderer.** `WebGPURenderer` from `three/webgpu`, or the classic `WebGLRenderer`? Custom
   `ShaderMaterial`, `RawShaderMaterial` or `onBeforeCompile` anywhere? Those do not run on
   WebGPU (gotchas).
3. **Loop.** Who owns the frame: `setAnimationLoop`, R3F's `useFrame`, or several `requestAnimationFrame`s
   (a bug — one clock per scene).
4. **Evidence of speed.** Is there any measurement (Inspector, timestamps, fps under load on
   the weakest target), or only a feeling?

Report a table — *area · now · problem · fix* — and exactly ONE next action.

## The capability ladder

Choose the rung per scene, top down; every rung must still be a working page.

1. **WebGPU** — `new WebGPURenderer()` then `await renderer.init()`.
2. **WebGL2 backend of the same renderer** — automatic when WebGPU is unavailable (it logs
   `running under WebGL2 backend`); forced with `forceWebGL: true`. Compute-heavy features
   need a lighter path here: detect with `renderer.backend.isWebGPUBackend` after `init()`.
3. **Calm** — no WebGL at all, reduced motion, or a device loss that could not recover: a
   static image or CSS/SVG still, fully legible. This is `sheleg-design`'s degrade-to-calm
   rule applied to a 3D scene.

## Gotchas — r186, each one silent or surprising

- **`render()` throws before `await renderer.init()`** (so do `clear()`, `hasFeature()`,
  `initTexture()`); `setAnimationLoop` awaits init itself. `renderAsync` and friends are
  deprecated since r181.
- **`positionNode` replaces the position after skinning, morphs and instancing.**
  `positionLocal.add(offset)` keeps them; `positionGeometry.add(...)` or
  `buffer.element(instanceIndex)` alone collapses every instance to a point. For particles
  use the official pattern: `positionNode = buffer.toAttribute()` on a sprite or point material.
- **JS reassignment is not a shader store.** Inside `Fn`, `a = a.add(1)` rebinds a JS name and
  emits nothing; use `.toVar()` then `.assign()`/`.addAssign()`. A JS `if` or ternary on a node
  is the same bug — use `If`/`select`.
- **Atomics need `storage(buf, 'uint', n).toAtomic()`** before `atomicAdd`.
- **`computeAsync()` does not wait for the GPU.** Only `renderer.getArrayBufferAsync()` reads
  results back to the CPU (with a reusable `THREE.ReadbackBuffer` in r186).
- **`ShaderMaterial`, `RawShaderMaterial` and `onBeforeCompile` have no WebGPU mapping** — the
  object renders as a plain node material with a "not compatible" error. Port to TSL. About
  twenty drei components are built on them and fail the same way.
- **The adapter is requested in compatibility mode**; on a device that only offers it, MSAA is
  silently disabled.
- **`alpha` defaults to `true`** on WebGPURenderer (false on WebGLRenderer): a port that relied
  on an opaque canvas shows the page through it.
- **`PostProcessing` is now `RenderPipeline`**; **`Clock` is deprecated — use `Timer`** (core);
  **`PCFSoftShadowMap` is removed** on WebGPU (`PCFShadowMap` is soft since r183);
  **`renderer.dispose()` is async**.
- **Device loss:** use `renderer.onDeviceLost` (and `renderer.onError` for validation and
  out-of-memory errors). It exists on both backends; hooking the WebGPU device directly breaks
  under the WebGL2 fallback.
- **R3F 9.8.1 defaults differ from three's:** ACES tone mapping on, `shadows={true}` selects
  the removed soft shadow map (use `shadows="percentage"`), and `useFrame` delta is unclamped.

## The procedure

1. **Renderer and loop** — one renderer, `await init()`, one `setAnimationLoop`, one `Timer`
   (`references/renderer-and-loop.md`).
2. **Materials and shaders** in TSL; compute for anything per-particle or per-instance
   (`references/tsl-and-compute.md`).
3. **Prewarm:** `await renderer.compileAsync(scene, camera)` (and `compileComputeAsync` for
   compute) before the first visible frame, so the first interaction does not hitch.
4. **Measure on the weakest target** with the Inspector or timestamp queries, then spend the
   budget (`references/performance-and-r3f.md`).
5. **Degrade:** reduced motion, no WebGPU, device loss and hidden tab each have a written
   branch — and each branch was seen working.
6. **Tear down:** dispose geometries, materials, textures and render targets;
   `await renderer.dispose()`.

## When something is missing

- **No browser or GPU in this host** → build, type-check and review; report visual and
  frame-time gates as `NOT_RUN` with the page and the device a person must use. Never report
  "smooth" from reading code.
- **The project is on an older three.js** → name the release gap; do not apply r186 names
  blindly, and do not upgrade the dependency without the operator.
- **R3F project, WebGPU wanted** → the async `gl` factory pattern in
  `references/performance-and-r3f.md`; list the drei components the scene uses that will not
  run on WebGPU before switching.

## References

| Read | When |
|---|---|
| `references/renderer-and-loop.md` | creating the renderer, the fallback, the loop and clock, colour and tone mapping, post-processing, device loss, disposal |
| `references/tsl-and-compute.md` | writing a TSL material or shader, a compute pass, particles, atomics, readback, or porting GLSL |
| `references/performance-and-r3f.md` | measuring or fixing frame time, draw calls and memory; running React Three Fiber on WebGPU; drei on WebGPU |

Asset files and budgets are `web3d-assets`; making things move is `web3d-animation`. The
public `webgpu-threejs-tsl` skill (dgreenheck) informed the gotcha-first shape of this one;
the errata found when re-verifying its examples against r186 are among the gotchas above.
