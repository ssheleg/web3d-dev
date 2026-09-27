The working directory is empty, so I can't see your code or `.glb`. These are two well-known issues with standard fixes.

## 1. Death pops back to T-pose

A `LoopOnce` action with the default `clampWhenFinished = false` **disables itself** when it ends. With no active action, the skeleton falls back to bind pose, which is your T-pose.

```js
const death = mixer.clipAction(clips.get('death'));
death.reset();
death.setLoop(THREE.LoopOnce, 1);
death.clampWhenFinished = true;   // hold the last frame instead of disabling
currentAction.crossFadeTo(death, 0.2, false);
death.play();
```

Two related traps:
- `'finished'` fires on the **mixer**, not the action. Use `mixer.addEventListener('finished', e => { if (e.action === death) … })`. A listener on the action never runs.
- If something else calls `stopAllAction()` or fades death out afterward, you'll get the same pop. Once dead, leave that action alone.

If it still snaps with the clamp set, check the clip itself. Its last keyframe might be the bind pose, which happens with some exporters. Scrub it in a viewer (e.g. gltf-viewer.donmccurdy.com) to see.

## 2. Feet slide while running

The clip's stride is authored for one ground speed, and your code moves the character at another. three.js has no root motion, so you have to match the two yourself.

**Case A: the run clip is in place** (the hips don't travel). Scale playback to the actual speed:

```js
const RUN_AUTHORED_SPEED = 3.5; // m/s the clip was authored for; measure it (below)

// every frame, after computing the character's actual horizontal speed:
runAction.setEffectiveTimeScale(currentSpeed / RUN_AUTHORED_SPEED);
```

To find the authored speed, pick a foot's plant frame and the same foot's next plant frame. Measure how far the body would have moved between them and divide by the time. Or take it from the provider (for example, Mixamo's non-in-place version of the same clip).

**Case B: the clip has root motion** (the hips translate forward, e.g. Mixamo without "In Place"). The body drifts *and* your code moves it, so it double-moves and snaps back every loop. Strip the horizontal hip translation and use the distance it covered as the authored speed:

```js
function stripRootXZ(clip, hipTrack = 'mixamorigHips.position') {
  const t = clip.tracks.find((k) => k.name === hipTrack);
  if (!t) return null;
  const v = t.values, x0 = v[0], z0 = v[2];
  const dx = v[v.length - 3] - x0, dz = v[v.length - 1] - z0;
  for (let i = 0; i < v.length; i += 3) { v[i] = x0; v[i + 2] = z0; }
  return Math.hypot(dx, dz) / clip.duration; // authored m/s → use in Case A
}
```

Log `clip.tracks.map(t => t.name)` to get the real hip track name.

**Also check:**
- **Walk↔run transitions:** crossfade with `warp = true` and match the phase so the same foot is down during the blend:
  ```js
  run.time = walk.time * (run.getClip().duration / walk.getClip().duration);
  walk.crossFadeTo(run, 0.25, true);
  ```
- **Clamp the delta:** `mixer.update(Math.min(dt, 0.1))`, using `THREE.Timer` with `timer.connect(document)`. `Clock` is deprecated in r186. Without the clamp, a hitch or a return from a hidden tab makes the animation jump ahead of movement. If you're on R3F/drei `useAnimations`, the delta is unclamped, so clamp inside your own `useFrame`.
- **Scale mismatch:** if the model is scaled (e.g. Mixamo in cm with `scale = 0.01`), the authored speed must be in the same units as your movement code.

## Next step

Share your animation setup code (mixer creation, the death trigger, the movement/run logic) and the `.glb` path, or drop them into this directory. I can then confirm which case applies and patch it directly. I can also run `npx @gltf-transform/cli inspect` on the file to check whether the run clip carries hip translation.
