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
- **Descriptions keep the 60-character reserve** below the 970 house cap.
- **Prose is English.** Russian survives only inside trigger phrases.
- **Asset Foundry is described, never advertised.** It is an optional private service:
  detect, delegate, or work by its principles — never tell a user to install it.
