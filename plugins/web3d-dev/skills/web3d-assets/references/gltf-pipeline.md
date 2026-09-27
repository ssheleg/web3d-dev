# glTF pipeline — commands, flags and the loader that reads the result

**Read this when** running any processing step on a `.glb`/`.gltf`, choosing between
gltf-transform and gltfpack, or wiring the loader in three.js or React Three Fiber.

Verified against three@0.186.1, @gltf-transform/cli 4.5.0 and gltfpack 1.3.0 on 2026-09-27
(package sources and CLI help; rows in `docs/evidence/research/2026-09-27-docs-study.md`).

## Contents

- Inspect and validate
- One command: optimize
- Step by step
- gltfpack
- Choosing compression
- Loaders: three.js r186
- Loaders: React Three Fiber and drei
- Sources

## Inspect and validate

```bash
npx @gltf-transform/cli inspect model.glb      # meshes, materials, textures, animations, sizes
npx @gltf-transform/cli validate model.glb     # Khronos glTF-Validator
```

Keep the raw file; write every output to a new path.

## One command: optimize

```bash
npx @gltf-transform/cli optimize in.glb out.glb \
  --compress meshopt --texture-compress webp --texture-size 2048
```

Defaults in 4.5.0: `--compress meshopt` (`draco | meshopt | quantize | false`),
`--texture-compress auto` (`ktx2 | webp | avif | auto | false`), `--texture-size 2048`,
simplify on (`--simplify-error 0.0001`), and instance, palette, flatten, join, weld, resample
and prune all on. `flatten` skips skin joints and animated nodes, so `optimize` keeps
characters playable.

With `--texture-compress ktx2`, `optimize` already splits codecs by slot: normal, occlusion
and metallic-roughness textures become UASTC (level 4, RDO) and every other texture ETC1S
(quality 255), each resized to `--texture-size`.

Use `optimize` for a first pass; use the individual steps when a budget needs control.

## Step by step

| Step | Command | Notes |
|---|---|---|
| Clean | `dedup`, `prune`, `weld` | safe on everything |
| Animation | `resample` | removes redundant keyframes losslessly |
| Simplify | `simplify --ratio 0.5 --error 0.001 --lock-border` | check the silhouette after |
| Instance | `instance --min 5` | repeated meshes become `EXT_mesh_gpu_instancing` |
| Resize | `resize --width 1024 --height 1024` | before encoding, not after |
| KTX2 colour | `etc1s --quality 128` | small, colour textures |
| KTX2 detail | `uastc --level 2 --zstd 18` | normal maps and fine detail |
| WebP / AVIF | `webp`, `avif` | when KTX2 is not wanted; no GPU compression |
| Geometry | `meshopt --level high` or `draco` | see *Choosing compression* |

**KTX2 needs the `ktx` CLI from KTX-Software ≥ 4.4.0** on `PATH`; with only the legacy
`toktx` the step fails with `Command "ktx" not found`. There is no `ktx2` command — KTX2 is
what `etc1s` and `uastc` write.

`meshopt` writes `EXT_meshopt_compression`. Quantization flags:
`--quantize-position|normal|texcoord|color|weight|generic`.

## gltfpack

```bash
gltfpack -i in.glb -o out.glb -cc -tc -si 0.5 -af 30
```

| Flag | Meaning |
|---|---|
| `-c`, `-cc`, `-cz` | meshopt compression, higher levels; `-cz`/`-ce khr` write **KHR_meshopt_compression** |
| `-cf` | also write an uncompressed fallback |
| `-tc`, `-tu`, `-tw` | ETC1S KTX2, UASTC KTX2, WebP textures — **native binary only** |
| `-tq N`, `-ts R`, `-tl N` | texture quality, scale, size limit |
| `-si R`, `-se E` | simplify ratio and error (default error 0.01) |
| `-af N` | resample animation at N Hz (default 30) |
| `-r report.json` | write a size report |

The npm `gltfpack` build refuses `-tc/-tu/-tw` ("node.js builds do not support BasisU … WebP")
and cannot read Draco input. It also drops unknown and vendor extensions and does not support
`KHR_animation_pointer`.

## Choosing compression

| Need | Choose | Because |
|---|---|---|
| Characters, animation, fast decode | meshopt | decodes quickly, compresses animation data too |
| Smallest static geometry, decode time acceptable | Draco | better ratio on static meshes, heavier decoder |
| GPU texture memory matters (most scenes) | KTX2 (ETC1S colour, UASTC normals) | stays compressed on the GPU |
| Simple pipeline, no GPU compression | WebP/AVIF | smaller downloads, full-size GPU memory |

## Loaders: three.js r186

```js
import * as THREE from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init();                                   // detectSupport throws before this

const ktx2 = new KTX2Loader()
  .setTranscoderPath('/vendor/three/basis/')             // copy examples/jsm/libs/basis/ — no working default
  .detectSupport(renderer);
const draco = new DRACOLoader().setDecoderPath('/vendor/three/draco/gltf/');

const loader = new GLTFLoader()
  .setKTX2Loader(ktx2)
  .setDRACOLoader(draco)
  .setMeshoptDecoder(MeshoptDecoder);

const gltf = await loader.loadAsync('/models/scene.glb');
await renderer.compileAsync(gltf.scene, camera, scene);  // build pipelines before the first frame
```

GLTFLoader r186 reads, built in: Draco, `KHR_meshopt_compression` and
`EXT_meshopt_compression`, `KHR_texture_basisu`, `KHR_mesh_quantization`,
`KHR_texture_transform`, `EXT_mesh_gpu_instancing`, `EXT_texture_webp`, `EXT_texture_avif`,
`KHR_lights_punctual` and the `KHR_materials_*` set (anisotropy, clearcoat, dispersion,
emissive_strength, ior, iridescence, sheen, specular, transmission, unlit, volume) plus
`EXT_materials_bump`. Plugin-only: `KHR_animation_pointer`, `KHR_materials_variants`,
Gaussian splats, `MSFT_texture_dds`, `NEEDLE_progressive`.

## Loaders: React Three Fiber and drei

- `useGLTF(path, useDraco = true, useMeshopt = true, extendLoader)` uses **three-stdlib's**
  GLTFLoader — it does not read `KHR_meshopt_compression`, `KHR_animation_pointer` or splats.
  Produce `EXT_meshopt_compression` (gltf-transform, or gltfpack without `-cz`/`-ce khr`) for
  drei, or load with three's own GLTFLoader through `useLoader`.
- Its Draco decoder defaults to `https://www.gstatic.com/draco/versioned/decoders/1.5.5/`:
  call `useGLTF.setDecoderPath('/vendor/three/draco/gltf/')` for CSP and offline use.
- `useKTX2` calls three-stdlib's `detectSupport`, which reads `renderer.extensions` — a WebGL
  property that WebGPURenderer lacks. Inferred from source, not run: on WebGPU, configure a
  three `KTX2Loader` yourself after `init()` and pass it through `extendLoader`.

## Sources

- three@0.186.1: `examples/jsm/loaders/GLTFLoader.js:84-112,836,1127,1330,2286-2287`,
  `examples/jsm/loaders/KTX2Loader.js:153-243`, `examples/jsm/loaders/DRACOLoader.js:102-132`,
  `examples/webgpu_loader_gltf_compressed.html`.
- @gltf-transform/cli 4.5.0: `src/cli.ts` (command list and flags; `optimize` KTX2 slot split
  421-445), `src/transforms/toktx.ts`
  (`ktx` ≥ 4.4.0), `@gltf-transform/functions/src/flatten.ts:53-60`.
- gltfpack 1.3.0: `gltfpack -h`, README (native builds for texture compression).
- @react-three/drei 10.7.9: `core/Gltf.js`, `core/Ktx2.js`; three-stdlib 2.36.1 loaders.
