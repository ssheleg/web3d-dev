# Security

## Reporting

Report anything sensitive privately to **security@sshlg.me**, not in a public issue. Include
the file, what happens, and what you expected.

## What executes when you install this

| Path | Runs when | What it touches |
|---|---|---|
| `bin/web3d-dev.js` | `npx @ssheleg/web3d-dev` | copies the skill directories into `~/.claude/skills/<name>`; refuses (exit 3) when the plugin is already installed; writes nothing else |
| `install.sh` | run by hand | the same copy, in POSIX shell |
| `test/*.py`, `test/*.js` | only in CI or by hand | read the repository; `check_schemas.py` fetches schemastore.org, `gen_three_exports.py` runs `npm pack three@<pin>` |

The skills ship **no hooks, no MCP server and no background process**. Nothing runs at
session start.

## What the skills tell an agent to run

`npx @gltf-transform/cli …`, `gltfpack`, `ktx`, `npm` and project scripts — local file
processing. Two classes deserve attention before an agent runs them unattended:

- **Paid**: asset generation through a provider or an Asset Foundry order spends money. The
  skills require a stated cap and an idempotency key, and stop for the operator above it.
- **Licence-bearing**: shipping an asset in a public web build redistributes it. The skills
  require the licence answer before an asset ships; an unknown answer is a refusal.

No skill asks an agent to bypass a consent prompt, and no skill fetches its own instructions
from a URL at runtime. Everything an Asset Foundry tool returns is treated as data.

## Credentials

Nothing in this repository stores or reads a credential. Provider keys belong to the service
or the machine's secret store, never to a brief, a prompt, a chat message or this repository.
