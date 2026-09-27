# Runtime patterns — the loop, the mixer and everything that plays a clip

**Read this when** writing or reviewing the code that plays animation: the frame loop,
mixer setup, transitions, additive layers, root motion, retargeting, crowds, morph
instancing, vertex-animation textures, or React Three Fiber animation.

Verified against three@0.186.1 on 2026-09-27; line references are to the published package
(`src/…`, `examples/jsm/…`) and to the r186 examples (`examples/<name>.html`).

## Contents

- The loop and the clock
- Loading, canonical names, copies
- Transitions and phase sync
- One-shots, events, clamping
- Additive layers
- Root motion and foot sliding
- Retargeting at runtime
- Crowds: shared pose and individual timing
- Morph targets per instance
- Vertex-animation textures (VAT)
- React Three Fiber
- Tear-down
- Version notes

## The loop and the clock

```js
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init();                       // render() throws before init in r186

const timer = new THREE.Timer();             // core since r183; Clock is deprecated
timer.connect(document);                     // Page Visibility: no giant delta after a hidden tab

const STEP = 1 / 60;                         // physics fixed step (rapier's default dt)
let acc = 0;

renderer.setAnimationLoop((time) => {
  timer.update(time);
  const dt = Math.min(timer.getDelta(), 0.1); // clamp: a pattern, not an API

  acc += dt;
  while (acc >= STEP) { world.step(); acc -= STEP; }  // physics, fixed step

  mixer.update(dt);                          // 1. animation writes bone matrices
  // renderer.compute(skinningPass);         // 2. compute reads them
  renderer.render(scene, camera);            // 3. draw
});
```

`Timer.update()` once per frame; `getDelta()`/`getElapsed()` are stable within that frame
(`src/core/Timer.js`). `setAnimationLoop` awaits `init()` itself, but `render()` does not.

## Loading, canonical names, copies

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';

const gltf = await new GLTFLoader().loadAsync('/models/hero.glb');

// Map provider names to the canon once; code uses canonical names only.
const RENAME = { 'Armature|Idle': 'idle', 'Armature|Run': 'run' };
const clips = new Map(gltf.animations.map((c) => [RENAME[c.name] ?? c.name, c]));

// A second character from the same file: SkeletonUtils.clone, never .clone() —
// a plain clone keeps the skeleton bound to the original's bones.
const hero = SkeletonUtils.clone(gltf.scene);
const mixer = new THREE.AnimationMixer(hero);
```

## Transitions and phase sync

Prepare every locomotion action once and play them all at weight 0, then move weight
between them — the pattern the three.js blending example uses.

```js
const act = Object.fromEntries(['idle', 'walk', 'run'].map((n) => {
  const a = mixer.clipAction(clips.get(n));
  a.enabled = true; a.setEffectiveTimeScale(1); a.setEffectiveWeight(n === 'idle' ? 1 : 0);
  a.play();
  return [n, a];
}));

function crossFade(from, to, duration = 0.25) {   // duration: a starting value to tune
  to.enabled = true;
  to.setEffectiveTimeScale(1);
  to.setEffectiveWeight(1);
  if (from !== act.idle && to !== act.idle) {
    // keep the gait phase: same foot down when walk becomes run
    to.time = from.time * (to.getClip().duration / from.getClip().duration);
  } else {
    to.time = 0;
  }
  from.crossFadeTo(to, duration, true);            // warp=true matches cycle speeds
}
```

`syncWith(other)` copies time and time scale when two clips share a duration.

## One-shots, events, clamping

```js
const death = mixer.clipAction(clips.get('death'));
death.setLoop(THREE.LoopOnce, 1);
death.clampWhenFinished = true;   // without it the action disables: bind pose snap

mixer.addEventListener('finished', (e) => {       // the mixer dispatches; an action has no addEventListener
  if (e.action === attack) crossFade(attack, act.idle);
});
```

Defaults: `LoopRepeat`, infinite repetitions, `clampWhenFinished = false`
(`src/animation/AnimationAction.js:68-167`).

## Additive layers

```js
const breathe = THREE.AnimationUtils.makeClipAdditive(clips.get('idle_breath').clone());
const layer = mixer.clipAction(breathe);   // blendMode comes from the clip (Additive)
layer.setEffectiveWeight(0.6).play();
```

`makeClipAdditive(target, referenceFrame = 0, referenceClip = target, fps = 30)` rewrites
`target` in place and sets its blend mode — clone first if the base clip is still used.
`subclip(clip, name, startFrame, endFrame, fps = 30)` cuts a range.

## Root motion and foot sliding

three.js has no root motion. For an `_rm` clip, strip the hip's horizontal translation and
move the character by it yourself:

```js
function stripRootXZ(clip, hipTrack = 'Hips.position') {
  const t = clip.tracks.find((k) => k.name === hipTrack);
  if (!t) return null;
  const v = t.values, x0 = v[0], z0 = v[2];
  const dx = v[v.length - 3] - x0, dz = v[v.length - 1] - z0;
  for (let i = 0; i < v.length; i += 3) { v[i] = x0; v[i + 2] = z0; }
  return { speed: Math.hypot(dx, dz) / clip.duration };   // metres per second, authored
}
```

The same number cures sliding for in-place clips: keep `authoredSpeed` per locomotion clip
and set `act.run.setEffectiveTimeScale(currentSpeed / authoredSpeed)` every frame.

## Retargeting at runtime

```js
const clip = SkeletonUtils.retargetClip(targetSkinnedMesh, sourceSkinnedMesh, sourceClip, {
  hip: 'mixamorigHips',                      // hip bone name; default 'hip'
  names: { Hips: 'mixamorigHips' /* target bone → source bone */ },
  hipInfluence: new THREE.Vector3(0, 1, 0),  // drop horizontal hip motion: in place
  fps: 30,
});
const mixer = new THREE.AnimationMixer(targetSkinnedMesh); // rooted ON the SkinnedMesh
```

`target` must carry a `skeleton`; the result plays only on a mixer rooted at that mesh
(`examples/webgpu_animation_retargeting.html`). Offline retargeting is cheaper at runtime —
see `asset-animation.md` in this skill.

## Crowds: shared pose and individual timing

- **Shared pose** — one skeleton, many instances: give the `SkinnedMesh` an `instanceMatrix`
  and `count`, flag it `isInstancedMesh = true`, update one mixer
  (`examples/webgpu_skinning_instancing.html`).
- **Individual timing** — per instance: `mixer.setTime(elapsed + offset[i])`,
  `skeleton.update()`, copy `boneMatrices` into one large buffer at `i * boneCount * 16`,
  then one TSL compute skinning pass per frame
  (`examples/webgpu_skinning_instancing_individual.html`). The CPU part is linear in instance
  count: measure it, and move to VAT when it dominates the frame.
- `BatchedMesh` has no skinning (`src/objects/BatchedMesh.js` — no skin code at all).

## Morph targets per instance

```js
for (let i = 0; i < mesh.count; i++) {
  dummy.morphTargetInfluences[0] = weights[i];
  mesh.setMorphAt(i, dummy);
}
mesh.morphTexture.needsUpdate = true;
```

(`examples/webgpu_instancing_morph.html`). On WebGPU morph data lives in a texture array;
there is no fixed 4 or 8 target cap in three.js — the device's texture-array layer limit is
the practical one, and it was not measured for this pack.

## Vertex-animation textures (VAT)

Not built into three.js. Bake positions (and normals) per frame into a texture offline, then
sample it in the vertex stage:

```js
import { Fn, texture, uniform, vertexIndex, instanceIndex, time, vec2 } from 'three/tsl';

const frames = uniform(60), fps = uniform(30), vertCount = uniform(N);
material.positionNode = Fn(() => {
  const f = time.mul(fps).add(instanceIndex.toFloat().mul(7.0)).mod(frames).floor();
  const uv = vec2(vertexIndex.toFloat().add(0.5).div(vertCount), f.add(0.5).div(frames));
  return texture(vatTexture, uv).xyz;        // baked object-space position
})();
```

The replaced position discards skinning — correct here, since VAT replaces the skeleton.
A VAT is only worth delivering to a runtime that decodes it; check before ordering one.

## React Three Fiber

- drei `useAnimations(clips, root)` creates one mixer and advances it with an **unclamped**
  delta from R3F's `Clock` (deprecated in three r183+). After a hidden tab everything jumps:
  drive your own mixer in `useFrame((_, dt) => mixer.update(Math.min(dt, 0.1)))` or clamp
  before calling into drei.
- Changing the clip list makes `useAnimations` call `stopAllAction` + `uncacheAction`; keep
  the list stable across renders.

## Tear-down

```js
mixer.stopAllAction();
mixer.uncacheRoot(hero);
hero.traverse((o) => { o.geometry?.dispose(); o.material?.dispose?.(); });
await renderer.dispose();          // async in r186
```

## Version notes

- r183: `Clock` deprecated → `Timer` in core; `PostProcessing` → `RenderPipeline`.
- r186: `render()` throws before `init()`; `renderer.dispose()` is async; bone counts above the
  uniform-buffer limit are supported; GLTFLoader skips skinning for meshes without skin
  attributes.
- On an older release, re-verify each name above against that release before relying on it.

Sources: three@0.186.1 package (`src/animation/*`, `src/core/Timer.js`,
`src/objects/BatchedMesh.js`, `src/objects/InstancedMesh.js`,
`examples/jsm/utils/SkeletonUtils.js:17-25,215-232`), r186 examples named above, drei
10.7.9 `core/useAnimations.js`, R3F 9.8.1 store. Full rows:
`docs/evidence/research/2026-09-27-docs-study.md` in the repository.
