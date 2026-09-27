## 0.1.2 — 2026-09-28

- **npm releases armed.** The package is on npm (`@ssheleg/web3d-dev`, first publish by the
  owner), GitHub trusted publishing is configured for `release.yml`, and this version is the
  first published by the tag alone. Record: `docs/evidence/releases/2026-09-28-npm/`.
- **No tools, no results.** Every skill's *When something is missing* now says: with no tools
  in the host, write commands and code, never their results — a size, a pass or "done" that
  nothing measured is fabricated evidence. Both probe runs caught a model narrating commands
  and measurements it could not have made.
- Candidate probes re-run after the 0.1.0 fixes; results in `test/evals/RESULTS.md`.

## 0.1.1 — 2026-09-27

- Coordination on: `.claude/agent-sync.json` guards the release surfaces and the three.js
  export snapshot, and `docs/AGENT_SYNC.md` is generated from it and linked from `CLAUDE.md`.
  The family umbrella refuses a member whose coordination config is not committed — found
  when this pack joined it.

## 0.1.0 — 2026-09-27

First release. Three skills for realtime 3D on the web, split by the question each answers:

- **web3d-runtime** — how the scene runs: WebGPURenderer and its WebGL2 fallback, TSL and
  compute, post-processing, device loss, the frame loop, profiling, React Three Fiber on WebGPU,
  and the calm fallback. Leads with the silent failures of three.js r186.
- **web3d-assets** — how an asset gets from a source to the frame within a budget: the glTF
  pipeline (gltf-transform, gltfpack, KTX2, meshopt, Draco), target profiles, loaders and colour
  spaces, sourcing and licences, and Asset Foundry — delegate when present, work by its
  principles when not.
- **web3d-animation** — how things move: a two-sided animation protocol (asset half and runtime
  half) with a shared clip canon, technique choice, retargeting, root motion, crowds, morph
  instancing and vertex-animation textures.

Every API fact is verified against three@0.186.1; `test/validate.py` checks each code block's
imports and `THREE.*` members against a snapshot of that release's exports.
