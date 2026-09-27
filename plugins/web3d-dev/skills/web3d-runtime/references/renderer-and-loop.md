# Renderer and loop — creation, fallback, clock, colour, post-processing, loss, disposal

**Read this when** creating or reviewing a WebGPURenderer, its WebGL2 fallback, the frame
loop and clock, colour management and tone mapping, the post-processing pipeline, device
loss handling, or teardown.

Verified against three@0.186.1 on 2026-09-27 (published package source and the r186
examples; rows in `docs/evidence/research/2026-09-27-docs-study.md`).

## Contents

- Imports
- Create and initialise
- Backend detection and the fallback
- The loop and the clock
- Colour and tone mapping
- Post-processing
- Device loss and GPU errors
- Disposal
- Version notes
- Sources

## Imports

`three`, `three/webgpu` and `three/tsl` share one core module, so class identity is shared;
`three/webgpu` re-exports all of core plus node materials, `WebGPURenderer` and
`RenderPipeline`. Addons live under `three/addons/*`. The CommonJS build is deprecated in r186
and the minified builds are gone — ESM only.

```js
import * as THREE from 'three/webgpu';
import { pass, Fn, uniform } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';   // effects are addons, not three/tsl
```

## Create and initialise

```js
const renderer = new THREE.WebGPURenderer({
  antialias: true,          // default false; samples 4 when true
  alpha: false,             // default TRUE on WebGPURenderer — set it if the canvas must be opaque
  powerPreference: 'high-performance',
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
document.body.append(renderer.domElement);
await renderer.init();      // idempotent; render()/clear()/hasFeature() throw before it
```

Other constructor options: `forceWebGL`, `samples`, `depth`, `stencil`,
`logarithmicDepthBuffer`, `reversedDepthBuffer`, `outputBufferType` (default
`HalfFloatType`; renamed from `colorBufferType` in r183), `multiview`, `requiredLimits`,
`device`, `trackTimestamp`.

## Backend detection and the fallback

- Without `forceWebGL`, a failed WebGPU init (no `navigator.gpu`, null adapter) falls back to
  the WebGL2 backend automatically and logs `WebGPU is not available, running under WebGL2
  backend.`
- After `init()`: `renderer.backend.isWebGPUBackend` / `renderer.backend.isWebGLBackend`.
- `WebGPU.isAvailable()` from `three/addons/capabilities/WebGPU.js` is only for UX messaging —
  it awaits an adapter **at import time**, and the renderer falls back by itself anyway.
- The adapter is requested with `featureLevel: 'compatibility'`; on a compatibility-only device
  MSAA is turned off silently. If edges matter, check it rather than assuming `antialias`.
- The backend requests every feature the adapter offers; pass `requiredLimits` only for limits
  you checked the adapter has.

## The loop and the clock

```js
const timer = new THREE.Timer();   // core since r183; Clock warns "Please use THREE.Timer"
timer.connect(document);           // Page Visibility: no giant delta after a hidden tab

renderer.setAnimationLoop((time) => {
  timer.update(time);
  const dt = Math.min(timer.getDelta(), 0.1);   // clamp: a pattern, not an API
  update(dt);
  renderer.render(scene, camera);                // or pipeline.render()
});
```

One loop per page. `setAnimationLoop(null)` stops it; on a page that shows the scene only
part of the time, stop the loop when it is off screen rather than rendering to nobody.

## Colour and tone mapping

- three's defaults: `outputColorSpace = SRGBColorSpace`, `toneMapping = NoToneMapping`,
  working space linear sRGB with `ColorManagement.enabled = true`.
- R3F's defaults differ: ACES filmic tone mapping unless `flat`/`linear` is set.
- Textures you load yourself default to `NoColorSpace`; set colour textures to
  `SRGBColorSpace`. GLTFLoader already does this for base colour and emissive.

## Post-processing

```js
const pipeline = new THREE.RenderPipeline(renderer);   // PostProcessing is a deprecated alias
const scenePass = pass(scene, camera);
const color = scenePass.getTextureNode('output');
pipeline.outputNode = color.add(bloom(color, 0.8, 0.2, 0.9));
renderer.setAnimationLoop(() => pipeline.render());      // replaces renderer.render
```

`outputColorTransform` is on by default — the pipeline applies tone mapping and colour-space
conversion at the end. `DirectRenderPipeline` is new in r186. Bloom import path and
parameters: `bloom(node, strength, radius, threshold)` from `examples/jsm/tsl/display/BloomNode.js`;
the other effects (depth of field, GTAO/SSAO, SSGI, SMAA/FXAA, outline, …) sit beside it in
`three/addons/tsl/display/`.

## Device loss and GPU errors

```js
renderer.onDeviceLost = (info) => {   // { api, message, reason, originalEvent }
  showStaticFallback();               // the calm rung: a still image, fully legible
  scheduleRebuild();                  // a new renderer + reload GPU resources, if worth it
};
renderer.onError = (err) => log('gpu-error', err);   // validation, out-of-memory, internal
```

- The default handler logs and marks the renderer lost; afterwards `compute()` does nothing.
- It does **not** fire when the device is destroyed on purpose (`reason === 'destroyed'`).
- Both handlers are renderer properties, so they work under the WebGL2 fallback too — unlike a
  listener on the WebGPU device itself.
- Test it: Chrome's `about:gpucrash` loses the GPU process for the whole browser.

## Disposal

```js
scene.traverse((o) => { o.geometry?.dispose(); [o.material].flat().forEach((m) => m?.dispose()); });
texture.dispose(); renderTarget.dispose();
await renderer.dispose();         // async in r186
```

`Object3D.dispose()` is new in r186; an override must call `super.dispose()`. Image bitmaps
from GLTFLoader are released only by disposing their textures.

## Version notes

| Release | Change |
|---|---|
| r181 | `*Async` render/clear/feature methods deprecated |
| r183 | `Clock` deprecated → `Timer` in core; `PostProcessing` → `RenderPipeline`; `colorBufferType` → `outputBufferType`; `PCFShadowMap` soft |
| r186 | `render()` throws before `init()`; `dispose()` async; `PCFSoftShadowMap` removed on WebGPU; CommonJS deprecated; `compileComputeAsync`; `ReadbackBuffer`; `onError` |

## Sources

three@0.186.1: `src/renderers/common/Renderer.js` (init 784-812, render guard 1496-1500,
loop 2067-2071, device loss 1348-1362, dispose 2696-2725), `src/renderers/webgpu/WebGPURenderer.js:34-67`,
`src/renderers/webgpu/WebGPUBackend.js:217-281`, `src/core/Timer.js`, `src/core/Clock.js`,
`src/renderers/common/RenderPipeline.js`, `examples/jsm/capabilities/WebGPU.js`;
examples `webgpu_postprocessing_bloom`, `webgpu_loader_gltf_compressed`; three.js Migration
Guide 181→186; r186 release notes.
