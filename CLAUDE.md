# CLAUDE.md — web3d-dev

House rules for **this repository only**. Family doctrine (language, quality bar, routing)
loads from `~/.claude/CLAUDE.md` in the same session; a second copy here would drift.

## What this repo is

Three agent skills for realtime 3D on the web, split by **the question being answered**:
how the scene runs (`web3d-runtime`), how an asset reaches the frame within budget
(`web3d-assets`), how things move (`web3d-animation`). three.js changes monthly, so every
fact is pinned to one release and the gate checks it.

## The gate

```bash
npm test               # test/validate.py: structure, versions, budgets, references, the pin, code blocks
npm run test:negatives # plant each defect and require the validator to refuse it
node test/installer_test.js
python3 test/evals_validate.py
claude plugin validate . --strict && claude plugin validate plugins/web3d-dev --strict
```

All green or the change does not land.

## Invariants — each one has a check that has been watched failing

- **One three.js pin.** `THREE_PIN` in `test/validate.py`; every `three@x.y.z` in the payload
  must equal it, and every reference carries a `Verified against` line.
- **Code blocks resolve.** Each three.js import and `THREE.*` / namespace member in a shipped
  code block must exist in `test/fixtures/three-exports.json`, the snapshot of the pinned
  release written by `test/gen_three_exports.py`. Moving the pin means regenerating it.
- **One contract, two homes.** `references/clip-canon.md` ships identically in
  `web3d-assets` and `web3d-animation`; edit both in one change.
- **A body names every reference it ships, and ships every reference it names.**
- **Descriptions stay under the 500-character family cap** (target 400). Claude Code
  shares one skill-listing budget across every installed skill, and on 2026-10-20 a full
  budget left 81 skills with no description. A description is a router: "Use when",
  "NOT for" with the sibling skill, the opt-out phrase and a few EN/RU triggers. Further
  trigger phrases live in the body's `## Triggers`.
- **Prose is English.** Russian survives only inside trigger phrases.
- **The asset service is never named.** It is an optional private service of the operator's
  machine: detect it by its `foundry_*` tools, delegate, or work by its principles; never name
  the product or tell a user to install it (operator, 2026-10-22: no private project names in
  public skills).

## Coordination

`docs/AGENT_SYNC.md` — generated from `.claude/agent-sync.json`, describing how coordination
is wired here and which files are guarded. Regenerate with `agent_sync.py setup`; never
hand-edit it.
