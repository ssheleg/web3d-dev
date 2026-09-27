# Sourcing and Asset Foundry — where an asset comes from, and who is allowed to make it

**Read this when** choosing where a model, texture or character comes from — a library,
a marketplace, a generator, a local model — when a licence decides whether an asset ships,
when writing a prompt for a 3D generator, or when deciding whether Asset Foundry should do
the work.

Verified against three@0.186.1 and the providers' public pages on 2026-09-27 (provider rows
re-stated from reads recorded 2026-09-19). Prices, limits and licences move: re-read the
provider's page before quoting one.

## Contents

- The search order
- Free libraries (CC0)
- Generators and services
- Local and open models
- Writing a prompt for a 3D generator
- Licences that stop a ship
- Asset Foundry: detect, delegate, or work by its rules
- Sources

## The search order

1. The project's own assets and catalogue.
2. CC0 libraries — free, no attribution, no redistribution question.
3. A marketplace asset with a licence that covers a public web build.
4. Generation (a service or a local model), concept image first for anything that matters.
5. Hand modelling.

Stop at the first step that meets the target profile. Each step down costs more and carries
more licence questions.

## Free libraries (CC0)

| Library | What | Licence |
|---|---|---|
| Poly Haven | HDRIs, PBR textures, models | CC0 |
| ambientCG | PBR materials, HDRIs | CC0 |

Describe a generic material generically ("weathered basalt") — it is probably in one of these
for free.

## Generators and services

| Service | Makes | Worth knowing before an order |
|---|---|---|
| Meshy | text/image/multi-image → 3D, remesh, UV, retexture, PBR maps; humanoid rig and clips; text-to-motion | API needs a paid plan and spends credits (~$0.02/credit on Pro); textures come at ≥2k (downscale for small budgets); results are kept for a limited time — download and store; concurrent tasks are capped per account tier |
| Tripo | text/image/multi-view → 3D, texture, decimate, segment; 7 rig types, presets, retarget | credits (~$0.01/credit); the API wallet is separate from the Studio subscription; a requested face count behaves as a target, not a cap — measure the result |
| fal.ai | hosted models: FLUX images (concepts), TRELLIS-family image-to-3D, video | per-call pricing; some 3D endpoints resell other providers above their direct price |
| Alpha3D | mesh, T-pose rig | access and quality unverified here |
| Blender, headless | scripted modelling, cleanup, rigging, baking, export | local; the most controllable step in any pipeline |

A generated body is a draft: it goes through the same gates as any other source.

## Local and open models

| Model | Licence note |
|---|---|
| TRELLIS (image → 3D with PBR) | MIT code and weights; heavy — measured on one Apple M4 Pro machine at ~3 min 20 s and ~18 GB peak per body. Its usual background-removal step (RMBG-2.0) is **non-commercial** — swap it for a commercially licensed remover before shipping |
| Hunyuan3D | its community licence **excludes the EU, the UK and South Korea** — check where the product ships |
| GET3D | non-commercial licence — research only |

## Writing a prompt for a 3D generator

Three rules learned across dozens of generated bodies:

1. **Shape first.** Lead with the silhouette and proportions; style and material after.
2. **Nothing around the body.** No base, pedestal, ground plane, frame or text — generators
   fuse them into the mesh. Put them in the negative list.
3. **Relief is a surface property.** Fine carving, cracks and engraving belong in textures and
   normal maps, not in geometry you will then have to decimate away.

Concept first for anything visible: generate cheap concept images, pick one, then image-to-3D
from the picked image. It is cheaper to reject a picture than a mesh.

## Licences that stop a ship

Answer four questions per asset, each with the sentence of the licence it rests on:

| Use | Question |
|---|---|
| Evaluation | may we try it at all? |
| Internal | may we use it in private builds? |
| Redistribution | may the file ship inside a public web build, where anyone can download it? |
| Commercial | may the product that contains it make money? |

A web build **is** redistribution: every visitor downloads the GLB. Marketplace licences that
allow use "in a game" but forbid redistributing the source file need a reading, not a guess.
An unknown answer is a no.

## Asset Foundry: detect, delegate, or work by its rules

Asset Foundry is an optional service some machines run to make assets on request — 3D bodies,
textures, rigs and clips, concept images, sound — through a set of `foundry_*` MCP tools and
its own `asset-foundry` skill. It is not a public package; do not tell a user to install it.

**Detect.** The session's tool list contains `foundry_capabilities` (possibly under a host
prefix), or an `asset-foundry` skill is installed. Neither → it is absent; use the rest of
this skill.

**Delegate.** Load the `asset-foundry` skill and follow it. The call order it enforces:
search the catalogue → plan → estimate → order with an idempotency key → poll → answer the
choice stage → delivery with one manifest per file. Pass this project's target profile. Read
its health output before assuming a provider is available — a listed tool is not a working
route, and paid routes may be disabled on a given machine.

**Its rules, by hand.** Without the service, keep what it enforces: catalogue before spend,
the profile decides, gate twice, raw files are never overwritten, one manifest per file,
rights in four areas, capped and idempotent spend. They are the principles in this skill's
body — the service only makes them mechanical.

Never call a provider directly from a project that has the service: that path has no ledger,
no catalogue and no gate, and it is how the same asset gets paid for twice.

## Sources

- Poly Haven <https://polyhaven.com/license>; ambientCG <https://docs.ambientcg.com/license/>.
- Meshy <https://docs.meshy.ai/en/api/pricing>, <https://docs.meshy.ai/en/api/rate-limits>,
  <https://docs.meshy.ai/en/api/asset-retention>.
- Tripo <https://developers.tripo3d.ai/en/pricing>, <https://developers.tripo3d.ai/en/docs/billing>.
- TRELLIS <https://github.com/microsoft/TRELLIS> (MIT); RMBG-2.0
  <https://huggingface.co/briaai/RMBG-2.0> (CC BY-NC 4.0); Hunyuan3D licence
  <https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/LICENSE>; GET3D
  <https://github.com/nv-tlabs/GET3D> (NVIDIA non-commercial licence).
- Measurements (TRELLIS timing, Tripo face-count behaviour, prompt rules): Asset Foundry's
  provider research and runs on this estate, 2026-09-19 to 2026-09-24.
