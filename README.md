# web3d-dev — realtime 3D on the web, three skills

Agent skills for building 3D on the web with three.js and React Three Fiber: getting the
scene to run on every GPU it meets, getting assets into it within a budget, and making things
in it move. Every API fact is verified against **three.js r186** (`three@0.186.1`), and the
repository's gate checks each code block against that release's exports.

| Skill | The question it answers |
|---|---|
| [web3d-runtime](plugins/web3d-dev/skills/web3d-runtime/SKILL.md) | How does the scene run — WebGPU and its WebGL2 fallback, TSL and compute, post-processing, device loss, the frame loop, profiling, R3F on WebGPU — and what does it fall back to? |
| [web3d-assets](plugins/web3d-dev/skills/web3d-assets/SKILL.md) | How does a model, texture or character get from a source to the frame within a budget — the glTF pipeline, target profiles, loaders, sourcing and licences, Asset Foundry when present? |
| [web3d-animation](plugins/web3d-dev/skills/web3d-animation/SKILL.md) | How does it move — the technique, the asset half (rig, clip canon, export, QA) and the runtime half (clock, mixer, blending, crowds, reduced motion)? |

Each skill leads with the failures that are silent in r186 — `render()` before `init()`,
`positionNode` collapsing instances, `computeAsync` not waiting for the GPU, drei components
that do not run on WebGPU, a second skin-weight set dropped without a word — and then the
patterns. References live inside their owning skill and load on demand.

## Start

Invoke the skill for the question you have: `/web3d-runtime`, `/web3d-assets` or
`/web3d-animation` from a skills directory, or `/web3d-dev:<skill>` from the plugin. Each one
inspects the project first (versions, renderer, loader, assets) and reports a table plus one
next action.

**Asset Foundry.** `web3d-assets` and `web3d-animation` detect the `foundry_*` tools or the
`asset-foundry` skill of a machine that runs that service and delegate asset orders to it;
without it they work by the same principles by hand — target profile, gate twice, one
manifest per file, licences in four areas, capped spend.

**Neighbours.** Landing-page heroes and scroll motion are `sheleg-design`; a Quest headset
product is `xr-dev`; rendered video is HyperFrames or Remotion; engine work is Unity's,
Unreal's or Godot's own skills.

## Install

Claude Code plugin:

```text
/plugin marketplace add ssheleg/web3d-dev
/plugin install web3d-dev@web3d-dev
```

Portable Agent Skills:

```bash
npx skills add ssheleg/web3d-dev
```

Use one channel per agent. For a family installation, update through
`npx sshlg-skills update`. Restart the agent after updates so skills reload.

## Verifying a change

<!-- commands-run-in: a clone -->
The repository carries tests; the payload carries the skills and references.

```bash
npm test
npm run test:negatives
node test/installer_test.js
python3 test/evals_validate.py
claude plugin validate . --strict
claude plugin validate plugins/web3d-dev --strict
python3 test/gen_three_exports.py   # online: refresh the three.js export snapshot after a pin move
```

[Evaluation documentation](test/evals/README.md) separates trigger and scenario definitions
from executed probes. The facts behind every reference are in
[the docs study](docs/evidence/research/2026-09-27-docs-study.md), and the requirements and
decisions in [the spec](docs/evidence/specs/web3d-dev-0.1.0.md).

## Provenance

The gotcha-first shape was informed by the public
[webgpu-threejs-tsl skill](https://github.com/dgreenheck/webgpu-claude-skill). No text was
copied from it; each fact here was re-verified against the r186 package, and several of its
examples' failure modes appear as gotchas.

## Releases

Push a `vX.Y.Z` tag after its versioned commit reaches the default branch. GitHub Actions
validates the pack, creates the GitHub release and publishes to npm with provenance through
trusted publishing. See [release setup and recovery](docs/RELEASING.md).

## License

MIT for this pack. Third-party tools, assets and models keep their own licences — the skills
say how to check them before shipping.
