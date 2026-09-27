# TSL and compute — materials, shaders, particles, atomics, readback, porting GLSL

**Read this when** writing a TSL material or effect, a compute pass, a particle system,
anything that uses atomics or reads GPU results back, or when porting a `ShaderMaterial` or
`onBeforeCompile` shader to WebGPU.

Verified against three@0.186.1 on 2026-09-27 (published `build/three.tsl.js` export list,
`src/nodes/*`, and the r186 compute examples).

## Contents

- The mental model
- Assignment semantics — the bug everyone writes once
- Uniforms and time
- Vertex displacement without losing skinning
- Compute: buffers, kernels, the frame
- Particles — the official pattern
- Atomics
- Reading results back
- Porting GLSL
- Sources

## The mental model

TSL is JavaScript that **builds a shader graph**; it is not JavaScript that runs per pixel.
Every call returns a node. The graph compiles to WGSL on the WebGPU backend and to GLSL on the
WebGL2 backend — one source, both rungs of the ladder.

```js
import * as THREE from 'three/webgpu';
import { Fn, uniform, time, sin, positionLocal, normalLocal, color, mix, uv } from 'three/tsl';

const material = new THREE.MeshStandardNodeMaterial();
const tint = uniform(new THREE.Color('#ff6a00'));
material.colorNode = mix(color('#101010'), tint, uv().y);
```

## Assignment semantics — the bug everyone writes once

Inside `Fn`, a JavaScript assignment rebinds a JavaScript name and emits **no** shader code.
Declare a shader variable with `.toVar()` and mutate it with `.assign()` / `.addAssign()`.

```js
import { Fn, float, If, Loop } from 'three/tsl';

const wrong = Fn(() => { let a = float(0); a = a.add(1); return a; });   // stores nothing
const right = Fn(() => {
  const a = float(0).toVar();
  Loop(8, () => { a.addAssign(0.125); });
  If(a.greaterThan(0.5), () => { a.assign(1); });
  return a;
});
```

The same trap in control flow: a JS `if` or ternary on a node is decided once, in JavaScript,
while building the graph. Use `If(...).ElseIf(...).Else(...)`, `select(cond, a, b)` and
`Loop(count, ({ i }) => {})`.

## Uniforms and time

- `uniform(value)` — change `.value` from JS; or attach an updater:
  `.onFrameUpdate(fn)` (once per frame), `.onRenderUpdate(fn)`, `.onObjectUpdate(fn)`.
- `time` and `deltaTime` are built-in per-frame uniforms. `timerLocal`, `timerGlobal` and
  `timerDelta` no longer exist.
- `oscSine(t = time)`, `oscSquare`, `oscTriangle`, `oscSawtooth` return 0..1.

## Vertex displacement without losing skinning

`positionNode` replaces the position **after** morphs, skinning, batching and instancing were
applied. Build on `positionLocal` to keep them:

```js
import { positionLocal, normalLocal, sin, time } from 'three/tsl';

material.positionNode = positionLocal.add(normalLocal.mul(sin(time.mul(3)).mul(0.02)));
```

`positionGeometry` is the raw, pre-deformation position — using it throws away the skeleton
and the instance matrix.

## Compute: buffers, kernels, the frame

```js
import * as THREE from 'three/webgpu';
import { Fn, instancedArray, instanceIndex, uniform, hash, vec3, deltaTime } from 'three/tsl';

const COUNT = 100_000;
const positions = instancedArray(COUNT, 'vec3');   // per-instance storage buffer
const velocities = instancedArray(COUNT, 'vec3');
const gravity = uniform(-9.8);

const init = Fn(() => {
  const i = instanceIndex;
  positions.element(i).assign(vec3(hash(i).sub(0.5), hash(i.add(1)), hash(i.add(2)).sub(0.5)).mul(10));
})().compute(COUNT);

const update = Fn(() => {
  const p = positions.element(instanceIndex);
  const v = velocities.element(instanceIndex);
  v.y.addAssign(gravity.mul(deltaTime));
  p.addAssign(v.mul(deltaTime));
})().compute(COUNT);

await renderer.init();
renderer.compute(init);                            // once
renderer.setAnimationLoop(() => {
  renderer.compute(update);                        // every frame, before render
  renderer.render(scene, camera);
});
```

- `instancedArray` is per-instance; `attributeArray` is per-vertex. Both accept struct types.
- `renderer.compute()` is synchronous after `init()`. `computeAsync()` is deprecated and
  **does not** wait for the GPU.
- `compileComputeAsync(nodes)` (r186) builds compute pipelines ahead of the first frame.

## Particles — the official pattern

Hand the storage buffer to the vertex stage as an attribute, on one draw call:

```js
const material = new THREE.SpriteNodeMaterial();
material.positionNode = positions.toAttribute();   // per-instance position
material.scaleNode = uniform(0.05);
const particles = new THREE.Sprite(material);
particles.count = COUNT;
scene.add(particles);
```

On an `InstancedMesh` of real geometry, **add** the instance offset to the mesh's own vertices
(`positionLocal.add(positions.toAttribute())`); assigning the buffer alone collapses every
instance to one point.

## Atomics

```js
import * as THREE from 'three/webgpu';
import { Fn, storage, atomicAdd, instanceIndex, If } from 'three/tsl';

const counterBuf = new THREE.StorageBufferAttribute(new Uint32Array(1), 1);
const counter = storage(counterBuf, 'uint', 1).toAtomic();   // required before atomic ops

const count = Fn(() => {
  If(instanceIndex.mod(2).equal(0), () => { atomicAdd(counter.element(0), 1); });
})().compute(1024);
```

## Reading results back

```js
const bytes = await renderer.getArrayBufferAsync(counterBuf);   // attribute, or a THREE.ReadbackBuffer
const value = new Uint32Array(bytes)[0];
```

`offset` and `count` arguments must be multiples of 4. For repeated reads, allocate one
`new THREE.ReadbackBuffer(maxByteLength)` and reuse it. Reading back stalls the pipeline — do
it for tools and tests, not every frame.

## Porting GLSL

| GLSL / WebGL idea | TSL / WebGPU |
|---|---|
| `ShaderMaterial` / `RawShaderMaterial` | a `*NodeMaterial` with `colorNode`, `positionNode`, `normalNode`, `emissiveNode`, `opacityNode` |
| `onBeforeCompile` string patching | assign the node slot you meant to patch; the rest of the lit material stays |
| `uniforms: { t: { value } }` | `uniform(value)` |
| varyings | `varying(node)` or `node.toVarying()` |
| a GLSL function you must keep | rewrite with `Fn`; raw WGSL through `wgslFn` (WebGPU backend only) |
| `gl_InstanceID`, `gl_VertexID` | `instanceIndex`, `vertexIndex` |

Until a custom material is ported it renders as a plain node material with a "not compatible"
error — the scene does not crash, it is just wrong.

## Sources

three@0.186.1: `build/three.tsl.js:691` (export list), `src/nodes/core/VarNode.js:372-373`,
`src/nodes/core/UniformNode.js:241`, `src/nodes/utils/Timer.js`, `src/nodes/utils/Oscillators.js`,
`src/nodes/accessors/Arrays.js:15-47`, `src/nodes/accessors/StorageBufferNode.js:267-296`,
`src/nodes/gpgpu/ComputeNode.js`, `src/materials/nodes/NodeMaterial.js:766-810`,
`src/renderers/common/Renderer.js:2097-2126,2877-2996`, `src/renderers/common/ReadbackBuffer.js`,
`src/renderers/common/nodes/NodeLibrary.js:52-72`; examples `webgpu_compute_particles`,
`webgpu_compute_reduce`; the three.js TSL wiki page.
