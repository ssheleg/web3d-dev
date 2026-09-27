# Performance and React Three Fiber — measure, spend the budget, run R3F on WebGPU

**Read this when** a scene is slow or must be proven fast, when choosing where frame time
goes, or when a React Three Fiber project moves to WebGPU or uses drei on it.

Verified against three@0.186.1, @react-three/fiber 9.8.1 and @react-three/drei 10.7.9 on
2026-09-27 (package sources and the R3F canvas documentation).

## Contents

- Measure first
- Where frame time goes
- Prewarm and hitches
- React Three Fiber on WebGPU
- drei on WebGPU
- Adaptive quality
- Sources

## Measure first

```js
import { Inspector } from 'three/addons/inspector/Inspector.js';
renderer.inspector = new Inspector();   // enables GPU timestamps itself; says if unsupported
```

Or by hand:

```js
const renderer = new THREE.WebGPURenderer({ trackTimestamp: true });
await renderer.init();
// after rendering a frame:
await renderer.resolveTimestampsAsync('render');
console.log(renderer.info.render.timestamp);          // GPU ms; compute: 'compute'
```

GPU timestamps need the `timestamp-query` feature; when it is absent, say so and measure frame
time on the CPU side instead of reporting a GPU number you did not get. `renderer.info` also
counts draw calls, triangles and memory objects per frame.

Measure on the **weakest device the product must run on**, in its browser, at its pixel ratio
— a desktop number says nothing about a phone.

## Where frame time goes

| Symptom | Likely cost | Fix |
|---|---|---|
| Many objects, CPU-bound | draw calls | `InstancedMesh` for repeats, `BatchedMesh` for varied static props, merge static geometry |
| Full-screen effects slow, scales with resolution | fill rate | cap the pixel ratio (e.g. at 1.5–2), lighter post-processing, half-resolution effects |
| Particles or transparent layers | overdraw | fewer, larger particles; alpha test instead of blending where it reads the same |
| Shadows | shadow passes | fewer casting lights, smaller maps, static shadows baked |
| First use of a material or effect hitches | pipeline compilation | prewarm (below) |
| Memory grows over time | undisposed GPU resources | dispose geometry, materials, textures, targets |
| Characters | skinning, mixer updates | see `web3d-animation` — update less off screen |

Fix one row, measure again. A change that did not move the measured number did not help.

## Prewarm and hitches

```js
await renderer.compileAsync(scene, camera);           // pipelines for everything in the scene
await renderer.compileComputeAsync([update]);         // r186: compute pipelines too
```

Run both behind the loading screen, after assets are in the scene.

## React Three Fiber on WebGPU

```jsx
import * as THREE from 'three/webgpu';
import { Canvas, extend } from '@react-three/fiber';

extend(THREE);   // register the node materials as JSX elements

export function Scene() {
  return (
    <Canvas
      shadows="percentage"                           // true/'soft' selects the removed PCFSoftShadowMap
      gl={async (props) => {
        const renderer = new THREE.WebGPURenderer(props);
        await renderer.init();                       // the factory must init before returning
        return renderer;
      }}
    >
      {/* … */}
    </Canvas>
  );
}
```

- In TypeScript, extend R3F's `ThreeElements` with `ThreeToJSXElements<typeof THREE>` so node
  materials type-check.
- R3F's own defaults: ACES tone mapping and sRGB output unless `flat`/`linear`; three's default
  is no tone mapping. Decide which the art was made for.
- `useFrame((state, delta) => …)` — `delta` comes from R3F's `Clock`, deprecated in three r183
  and unclamped: clamp it yourself.
- `frameloop="demand"` renders only after `invalidate()` — right for configurators and viewers
  that sit still; `"never"` hands frames to `advance(timestamp)`.
- R3F 9.8.1 awaits r186's async `renderer.dispose()` on unmount.
- Peers: React ≥19 <19.4, three ≥0.156 (fiber); drei needs fiber ^9 and three ≥0.159.

## drei on WebGPU

Built on GLSL `ShaderMaterial`/`onBeforeCompile`, so **not** WebGPU-ready (they render as plain
node materials with an error): `MeshTransmissionMaterial`, `MeshReflectorMaterial`,
`MeshRefractionMaterial`, `MeshDistortMaterial`, `MeshWobbleMaterial`, `MeshPortalMaterial`,
`shaderMaterial()`, `Outlines`, `ContactShadows`, `AccumulativeShadows`, `SoftShadows`,
`Caustics`, `Cloud`, `Stars`, `Sparkles`, `Grid`, `Image`, `PointMaterial`, `SpotLight`, `Splat`,
`useBoxProjectedEnv`. List what the scene uses before switching renderers, and replace each
with a TSL equivalent or drop it.

Loader caveats (`useGLTF`, `useKTX2`, the Draco CDN default) are in `web3d-assets`.

Renderer-agnostic and useful: `PerformanceMonitor`, `AdaptiveDpr`, `Detailed` (LOD with
hysteresis), `Instances`/`Merged`, `Bvh` (three-mesh-bvh raycasting). This list was read from
source, not run on WebGPU — check each in the target browser.

## Adaptive quality

Step quality down on measured frame time, not on a device guess: pixel ratio first (cheapest
to change, biggest effect on fill rate), then post-processing, then shadow resolution, then
geometry LOD. `PerformanceMonitor` + `AdaptiveDpr` do the first step in R3F. At the bottom of
the ladder is the calm static state from this skill's body.

## Sources

three@0.186.1: `src/renderers/common/Renderer.js:896,1115,3018-3022` (compile, timestamps),
`src/renderers/common/Info.js:65-89`, `src/renderers/common/Backend.js:76,608`,
`examples/jsm/inspector/Inspector.js:306-329`. @react-three/fiber 9.8.1: canvas docs
("WebGPU"), store (Clock, shadows, tone mapping, dispose). @react-three/drei 10.7.9: grep of
`core/*.js` and `materials/*.js` for `ShaderMaterial`/`onBeforeCompile`/`ShaderChunk`;
`core/PerformanceMonitor.js`, `core/AdaptiveDpr.js`, `core/Detailed.js`.
