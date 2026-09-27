The working directory is empty, so I can't edit your file directly. Here's the cause and the fix.

## Why every sphere is a dot

`material.positionNode` sets the **vertex position** in local space. It runs once per vertex of every instance. When you assign `positions.element(instanceIndex)` to it, every vertex of a sphere gets the same value: that instance's center. So all the sphere's vertices collapse to one point, which renders as a dot.

In the old GLSL setup, the instance offset was **added** to the vertex position (`position + offset`). You need to do the same in TSL.

## Fix

Add the instance offset to `positionLocal` instead of replacing it:

```js
import { positionLocal, instanceIndex } from 'three/tsl';

material.positionNode = positionLocal.add( positions.element( instanceIndex ) );
```

If you also need per-instance scale (for example, from a `scales` storage buffer):

```js
material.positionNode = positionLocal
  .mul( scales.element( instanceIndex ) )
  .add( positions.element( instanceIndex ) );
```

## Things to check

- **Double transforms:** If you're using an `InstancedMesh` and also setting its `instanceMatrix`, Three.js already applies that matrix. Leave those matrices as identity so you don't offset twice. If the positions come only from your storage buffer, a plain `Mesh` with `mesh.count = N` works too. On older three versions, use an `InstancedMesh` with `count = N`.
- **Buffer type:** Make sure `positions` is a `vec3` buffer, e.g. `instancedArray(N, 'vec3')` or `storage(attr, 'vec3', N)`. If it's a `vec4`, use `positions.element(instanceIndex).xyz`.
- **Normals:** Translation alone doesn't affect normals, so lighting stays correct. If you add non-uniform scale or rotation, set `material.normalNode` to match.

If you share the actual file path, I can apply the change there.
