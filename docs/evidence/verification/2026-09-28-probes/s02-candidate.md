That was a runaway loop of the same command, and I never got its output. Rather than retry, here's the diagnosis. Both symptoms are well-known r186 behaviours, and I can't see your code from this empty temp directory.

## 1. Death pops back to T-pose

A `LoopOnce` action with `clampWhenFinished = false` (the default) disables itself when it finishes. With no active action left, the skeleton falls back to bind pose (your T-pose).

```js
const death = mixer.clipAction(clips.get('death'));
death.setLoop(THREE.LoopOnce, 1);
death.clampWhenFinished = true;   // hold the last frame instead of disabling
death.reset().play();
```

If you crossfade into death, also make sure nothing crossfades out of it afterward. A `'finished'` handler that returns every one-shot to idle is a common cause:

```js
mixer.addEventListener('finished', (e) => {   // on the mixer; actions have no addEventListener
  if (e.action === death) return;              // stay dead
  if (e.action === attack) crossFade(attack, act.idle);
});
```

If it still snaps, check whether the clip itself ends in bind pose. Scrub its last frame in a viewer, or use `npx @gltf-transform/cli inspect hero.glb` to look at its duration and channels. That would be an asset bug, not a runtime one.

## 2. Feet slide when running

The character moves at your gameplay speed, but the run cycle plays at its authored speed. Any mismatch looks like skating. The usual fix is to scale the clip's playback to the actual speed.

**Measure the clip's authored speed once.** If the run clip carries hip translation (root motion), strip it and get the speed at the same time:

```js
function stripRootXZ(clip, hipTrack = 'Hips.position') {  // use your hip bone's track name
  const t = clip.tracks.find((k) => k.name === hipTrack);
  if (!t) return null;
  const v = t.values, x0 = v[0], z0 = v[2];
  const dx = v[v.length - 3] - x0, dz = v[v.length - 1] - z0;
  for (let i = 0; i < v.length; i += 3) { v[i] = x0; v[i + 2] = z0; }
  return Math.hypot(dx, dz) / clip.duration;   // m/s as authored
}
const runAuthoredSpeed = stripRootXZ(clips.get('run')) ?? 3.5; // in-place clip: measure by eye, tune
```

**Drive `timeScale` from real speed every frame:**

```js
const dt = Math.min(timer.getDelta(), 0.1);             // clamp: no jump after a hidden tab
act.run.setEffectiveTimeScale(currentSpeed / runAuthoredSpeed);
mixer.update(dt);
```

Also check these:
- **Hip translation not stripped.** If the clip moves forward and your code also moves the character, the motion is counted twice. Strip it as above, or export the clip in place.
- **Walk to run transitions.** Use `from.crossFadeTo(to, 0.25, true)` (warp on) and match phase so the same foot is down after the switch.
- **Retargeted clips (e.g. Mixamo).** A different leg length changes the stride. Re-measure the authored speed on the target rig; don't reuse the source's number.
- **Unclamped delta.** In R3F/drei, `useAnimations` passes a raw delta. Clamp it in `useFrame` yourself.

## Status

Both fixes are **NOT_RUN**: I haven't seen your code or model. To verify, check that:
1. After death the body holds the final frame for several seconds.
2. At several run speeds, a planted foot stays fixed against the ground (a grid texture helps).

If you share the file that sets up the mixer and the path to the `.glb`, I'll inspect the clip names and hip track and apply the changes directly.
