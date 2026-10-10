# Skill Card — web3d-dev

## Identity

| Field | Value |
|---|---|
| Pack | `web3d-dev` |
| Version | `0.1.3` |
| Skills | `web3d-runtime`, `web3d-assets`, `web3d-animation` |
| License | MIT |
| Source | https://github.com/ssheleg/web3d-dev |

## Job and boundary

Realtime 3D on the web with three.js and React Three Fiber: the renderer and its fallback,
TSL and compute, performance; the glTF asset pipeline, budgets, sourcing and licences; and
the animation protocol. Landing-page heroes and scroll motion belong to `sheleg-design`, a
Quest headset product to `xr-dev`, rendered video to HyperFrames or Remotion, engine work to
the engines' own skills.

## Inputs and outputs

Inputs: a web project (or an empty one), its `package.json`, its `.glb`/`.gltf` files,
optionally an Asset Foundry service on the machine. Outputs: code changes, processed asset
files with a manifest each, target profiles, and verification tables with PASS / FAIL /
NOT_RUN per check. Nothing is bought, ordered or published without an explicit instruction.

## Runtime and trust

No hooks, no MCP server, no background process, no network fetch at load time. The bodies
name `npx @gltf-transform/cli`, `gltfpack`, `ktx` and `npm` commands an agent may run; a paid
asset order is an outward action that needs a person's budget and say-so, and goes through
Asset Foundry when it is present rather than to a provider directly.

## Risk table

| Risk | Rating | Why |
|---|---|---|
| Executes code on install | Low | `bin/web3d-dev.js` copies directories; refuses when the plugin is present |
| Reads credentials | None | nothing here reads or stores a secret |
| Network at runtime | Low | `npx` fetches gltf-transform when an agent runs it; nothing fetches on load |
| Spends money | Gated | generation providers and Asset Foundry orders are paid; the skills require a cap and an idempotency key, and stop for the operator above budget |
| Stale content | Medium | three.js moves every month; every fact is pinned to r186 and the gate checks code blocks against that release's exports |

## Maintenance

Moving the three.js pin: update `THREE_PIN` in `test/validate.py`, run
`python3 test/gen_three_exports.py`, fix what `npm test` then refuses, and re-verify the docs
study rows the release notes touch.
