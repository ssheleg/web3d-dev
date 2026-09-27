I have no tool access in this session (no file, shell or MCP tools are listed), so I can't inspect the file, run the pipeline or check for Asset Foundry. Below is the exact run for your setup. Paste the `inspect` output back and I'll size the budget and flags.

## The drei constraint that decides the tools

`useGLTF` uses three-stdlib's GLTFLoader, which **does not read `KHR_meshopt_compression`**. So:

- Use **gltf-transform**, which writes `EXT_meshopt_compression`. drei reads that.
- Don't use `gltfpack -cz` or `-ce khr`.
- KTX2 needs the **`ktx` CLI from KTX-Software ≥ 4.4** on `PATH`. The old `toktx` fails with `Command "ktx" not found`.

## 1. Inspect first (the source stays untouched)

```bash
mkdir -p raw && cp model.glb raw/model.glb        # keep the original
npx @gltf-transform/cli validate raw/model.glb
npx @gltf-transform/cli inspect  raw/model.glb    # paste this back to me
ktx --version                                      # must be ≥ 4.4
```

An 80 MB file is almost always textures (4K/8K PNGs), not geometry. `inspect` will confirm this and tell us whether simplifying is worth it.

## 2. Process

```bash
T="npx @gltf-transform/cli"
$T dedup   raw/model.glb   out/1.glb
$T prune   out/1.glb       out/2.glb
$T weld    out/2.glb       out/3.glb
$T resample out/3.glb      out/4.glb
$T resize  out/4.glb       out/5.glb --width 2048 --height 2048
# colour → ETC1S (small); normals/data → UASTC (keeps detail)
$T etc1s   out/5.glb out/6.glb --quality 128 --slots "{baseColorTexture,emissiveTexture}"
$T uastc   out/6.glb out/7.glb --level 2 --zstd 18 \
           --slots "{normalTexture,occlusionTexture,metallicRoughnessTexture}"
$T meshopt out/7.glb model.glb --level high        # → EXT_meshopt_compression
$T validate model.glb && $T inspect model.glb
```

About the steps:
- If `inspect` shows a heavy triangle count, add `simplify --ratio 0.5 --error 0.001 --lock-border` before `resize`, then check the silhouette.
- Drop `resize` to 1024 if the model never fills the screen.
- The quick alternative is a single command, `optimize raw/model.glb model.glb --compress meshopt --texture-compress ktx2 --texture-size 2048`. It uses one codec for all textures, though.

## 3. Loader: KTX2 must be added to useGLTF

`useGLTF` turns meshopt on by default but **does not set up KTX2**. Without the change below, the textures won't load.

```jsx
import { useGLTF } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { KTX2Loader } from 'three-stdlib'

useGLTF.setDecoderPath('/vendor/three/draco/gltf/')   // avoid the gstatic CDN default (CSP/offline)

let ktx2
function Model(props) {
  const gl = useThree((s) => s.gl)
  const { scene } = useGLTF('/models/model.glb', true, true, (loader) => {
    ktx2 ??= new KTX2Loader().setTranscoderPath('/vendor/three/basis/').detectSupport(gl)
    loader.setKTX2Loader(ktx2)
  })
  return <primitive object={scene} {...props} />
}
```

Setup notes:
- Copy `node_modules/three/examples/jsm/libs/basis/` to `public/vendor/three/basis/`. There is no working default transcoder path.
- This works on R3F's default **WebGL** renderer. On WebGPURenderer, `detectSupport` breaks inside three-stdlib. In that case, use three's own `KTX2Loader`, configured after `await renderer.init()`.

## 4. Record it

Write a `model.manifest.json` beside the output with:
- the source and licence
- the steps run
- before and after sizes
- the validator verdict

**Next action:** run step 1 and paste the `inspect` output and `ktx --version`.
