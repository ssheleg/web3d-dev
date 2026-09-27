The meshopt half is done: **80 MB → 30 MB** in `public/models/warehouse.meshopt.glb`. The file validates clean and the original is untouched. KTX2 is blocked because there is no `ktx` CLI on this machine.

## Where it stands

| Part | Now | Fix | Status |
|---|---|---|---|
| Geometry (Shelf: 412k tris × 24 copies ≈ 9.9M tris drawn) | was 58.4 MB | clean, conservative simplify, instancing (62 instances), meshopt | **done** |
| Textures: 4 PNGs, 2× 4096², 2× 2048² | ~21.5 MB file, **~224 MB GPU** | KTX2: ETC1S colour, UASTC normal | **NOT_RUN** (no `ktx`) |
| Loader compatibility | writes `EXT_meshopt_compression` | this is the variant drei's `useGLTF` reads | ok |

Notes:
- **Textures are now most of the file**, and they cost far more in GPU memory (~224 MB) than on disk. KTX2 is the bigger win there.
- **Simplify ran at the default error of 0.0001.** It's conservative, but check the shelf silhouettes before you ship.
- **The 9.9M triangles drawn is the real runtime problem**, separate from file size. That Shelf mesh is heavy for something repeated 24 times. I haven't cut it harder because you have no written budget yet. I'd suggest one, e.g. ≤ 1–2M scene triangles and 2048² textures.
- **Your `<Canvas>` uses the default WebGL renderer**, so drei's KTX2 path will work. You'll need to host the Basis transcoder yourself, and the Draco decoder too, since drei defaults it to gstatic.

## Next action (needs your OK)

Install **KTX-Software ≥ 4.4**, which provides the `ktx` CLI. The older `toktx` is not enough. You can get it from the KTX-Software GitHub releases (macOS .pkg); I won't install system tools without your go-ahead. Once it's on PATH, I'll:

1. Encode from the original PNGs using `--texture-compress ktx2` (UASTC normals, ETC1S colour). I'll resize to 2048 if you accept that budget.
2. Copy `three/examples/jsm/libs/basis/` into `public/vendor/basis/`.
3. Wire `useGLTF(path, true, true, loader => loader.setKTX2Loader(...))` with a KTX2Loader that has `.detectSupport(gl)`, and point it at the new file.
4. Validate, measure, and write `warehouse.manifest.json`. The manifest needs the model's source and licence, so tell me where it came from (Blender export by whom?).

If you'd rather skip installing anything, I can use WebP textures instead. That gives a smaller download, but no GPU memory saving.
