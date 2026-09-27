The working directory is empty, so I can't see your code. These are the usual causes and fixes for both symptoms.

## 1. T-pose after the death animation

The default `loopMode` is `LoopRepeat`. If you set `LoopOnce` without `clampWhenFinished`, the action disables itself when it ends. The mixer then stops writing to the bones, and they fall back to their bind pose, which is the T-pose.

```js
const death = mixer.clipAction(deathClip);
death.reset();
death.setLoop(THREE.LoopOnce, 1);
death.clampWhenFinished = true;   // hold the last frame
death.play();

// Optional: react when it ends (e.g. stop AI, show UI)
mixer.addEventListener('finished', (e) => {
  if (e.action === death) { /* ... */ }
});
```

Also check for these:
- **Something calls `stop()` or `stopAllAction()` on death**, such as a state machine that stops the previous state's action. `stop()` resets the action and releases its bindings, which also produces the T-pose. Crossfade into death instead: `run.crossFadeTo(death, 0.2, false)`, or `death.crossFadeFrom(run, 0.2)`.
- **`mixer.uncacheAction` or `uncacheRoot` is called** while the corpse is still visible.
- **The death clip is shorter than its tracks.** Some exporters leave extra keyframes at the end, including a bind-pose frame. Trim the clip in Blender, or use `THREE.AnimationUtils.subclip(clip, 'death', startFrame, endFrame, fps)`.

## 2. Foot sliding while running

The run cycle is authored to cover a fixed distance per loop, and your code moves the character at a speed that doesn't match. There are two fixes.

**A. Scale playback speed to movement speed.** This is the simple, common approach:

```js
// Measure once: how far the character travels in one run cycle
// (from the DCC tool, or root bone start/end positions).
const RUN_CYCLE_DISTANCE = 3.2;            // meters per loop
const runAuthoredSpeed = RUN_CYCLE_DISTANCE / runClip.duration; // m/s

function update(dt) {
  const speed = velocity.length();         // your actual movement speed
  runAction.timeScale = speed / runAuthoredSpeed;
  character.position.addScaledVector(velocity, dt);
  mixer.update(dt);
}
```

For walk and run blends, give both actions the same normalized phase with `action.syncWith(other)`, and set their weights from speed.

**B. Root motion.** Take the translation off the root/hips bone and apply it to the character object yourself. If the clip already includes forward motion on the hips *and* your code also moves the object, the character is moved twice. That causes sliding or skating. Remove the root translation track:

```js
const hipsName = 'mixamorigHips'; // check your skeleton
runClip.tracks = runClip.tracks.filter(
  t => t.name !== `${hipsName}.position`
);
// or keep only the Y (bob) component by editing the track's values
```

Other things that cause sliding:
- **The model's scale doesn't match the scale the clip was authored for.** Examples are Mixamo in cm versus your scene in m, or a scale set on the scene root. Scale the model, not the per-frame movement.
- **`mixer.update()` gets the wrong delta.** Pass the same `dt` (seconds, from `THREE.Clock` or `THREE.Timer`) that you use for movement. Don't pass milliseconds, and don't call it twice per frame.
- **Crossfades that last too long** between idle and run make the feet look like they skate during the blend. Keep them around 0.15–0.25s.

If you paste your animation and movement code, especially where the death state is triggered and where position is updated, I can point to the exact line.
