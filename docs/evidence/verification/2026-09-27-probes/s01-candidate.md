I'll find where that material is set up.


<invoke name="Grep">
<parameter name="pattern">positionNode</parameter>
<parameter name="output_mode">content</parameter>
<parameter name="-n">true</parameter>
</invoke>

<invoke name="Bash">
<parameter name="command">ls -la; cat package.json 2>/dev/null</parameter>
</invoke>
<function_results>No matches found</function_results>
<function_results>total 0
drwx------   2 sergey  staff   64 Sep 27 10:12 .
drwx------  18 sergey  staff  576 Sep 27 10:12 ..</function_results>
<details>
<summary>Thinking</summary>

Empty directory. Give the fix directly.
</details>

The working directory is empty, so I can't edit your file. Here's the fix to apply.

## Why every sphere is a dot

`positionNode` replaces the vertex position after instancing is applied. Setting it to `positions.element(instanceIndex)` gives every vertex of a sphere the same point: its instance's center. The sphere's own geometry is gone, so it collapses to a dot.

## Fix

Add the per-instance offset to the sphere's own vertices, and pass the buffer to the vertex stage with `toAttribute()`:

```js
import { positionLocal } from 'three/tsl';

// before: material.positionNode = positions.element(instanceIndex);
material.positionNode = positionLocal.add(positions.toAttribute());
```

This assumes `positions` is an `instancedArray(COUNT, 'vec3')` (or a storage buffer) that your compute pass writes into.

## Two things to check alongside it

- **The mesh's instance matrices.** `positionLocal` already includes `instanceMatrix`. If you also set those matrices to the particle positions, each offset is applied twice. Either keep them at identity, or drop the storage-buffer offset and write the matrices instead. Using the storage buffer is the better choice for GPU-driven particles.
- **Per-instance scale.** If spheres vary in size, scale before adding: `positionLocal.mul(scales.toAttribute()).add(positions.toAttribute())`.

I couldn't run this here. It needs a WebGPU browser to confirm the spheres render with full geometry. If you point me at the project directory, I'll make the edit in place.
