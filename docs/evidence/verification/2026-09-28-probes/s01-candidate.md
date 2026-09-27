The working directory is empty, so I couldn't find your file to edit it. Here's the fix to apply wherever the material is set up.

## Why every sphere is a dot

`positionNode` **replaces** the vertex position after instancing has been applied. `positions.element(instanceIndex)` is the same value for every vertex of an instance, so all of a sphere's vertices land on one point. The sphere geometry is discarded.

## The fix

Add the per-instance offset to the mesh's own vertices, and pass the buffer to the vertex stage as an attribute:

```js
import { positionLocal } from 'three/tsl';

// was: material.positionNode = positions.element(instanceIndex);
material.positionNode = positionLocal.add(positions.toAttribute());
```

- **`positionLocal`** keeps the sphere's vertices.
- **`.toAttribute()`** is the official way to feed an `instancedArray` into the vertex stage on `InstancedMesh`.

## Things to check next to it

- **Remove any `instanceMatrix` translation.** If you also set positions with `setMatrixAt`, that offset is applied too, so each sphere moves twice. Leave the matrices as identity, or use them only for scale and rotation.
- **Scale.** If you want per-particle size, apply it before the offset, e.g. `positionLocal.mul(size).add(positions.toAttribute())`.
- **Culling.** The `InstancedMesh` bounding sphere doesn't know where compute moved the particles. Instances can vanish at screen edges. Set `mesh.frustumCulled = false` or give it a large enough `boundingSphere`.
- **Order.** Run `renderer.compute(update)` before `renderer.render(...)` in the same `setAnimationLoop`.

## Verification

I haven't run this, because there's no project or browser here. The visual result is `NOT_RUN`. To confirm, load the page in a WebGPU browser (Chrome/Edge) and in the WebGL2 fallback (`forceWebGL: true`). The spheres should show full geometry at distinct positions in both.

If you share the file path or paste the material and mesh setup, I can apply the change directly.
