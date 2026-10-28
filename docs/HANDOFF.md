## v0.2.5: web3d-assets names a 3D model (2026-10-28)

- **Done.** web3d-assets names a 3D model: the family member gate (`test/family_gate.py`, with its shared-mechanism
  declaration) and the documentation merged since v0.2.4, released.
- **Next task.** After merge: tag `v0.2.5`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

## v0.2.4: descriptions within a 300-character budget (2026-10-25)

- **Done.** Every skill description cut to at most 300 characters (hub B-255 (a)); total 1339 → 884
  characters, whitespace collapsed. Dropped quoted triggers moved to each body's `## Triggers`.
  Per-skill numbers are in CHANGELOG.md.
- **Next task.** After merge: tag `v0.2.4`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

## v0.2.3: the family member gate (2026-10-24)

- **Done.** the family member gate: the family member gate (`test/family_gate.py`, with its shared-mechanism
  declaration) and the documentation merged since v0.2.2, released.
- **Next task.** After merge: tag `v0.2.3`, watch the release, then the sshlg-skills pin bump; then
  the highest open board row.

# web3d-dev: handoff

## 0.2.2 released and pinned (2026-10-22)

- **State.** web3d-dev 0.2.2 is tagged, on npm and pinned by sshlg-skills 1.73.2; installed on the operator machine (every addressable scope).
- **Next task.** Board empty. Next work comes from the operator's planning; none is assigned here by the hub's M2 plan (`ssheleg/sshlg-skills` `docs/runs/2026-10-22-m2-subscription-growth-plan.md`).

## v0.2.2: a shorter router description and a current ledger (2026-10-22)

- **Objective.** Bring the description back under the family budget and record the shipped version in the ledger.
- **Done.** Description trimmed; ledger entry v0.2.2.
- **Next task.** After merge: tag `v0.2.2`, watch the release run, then the sshlg-skills pin bump.

## v0.2.1: the asset service is not named (2026-10-22)

- **Objective.** Remove a private service's product name from shipped skills and public pages (operator, 2026-10-22).
- **Done.** Generic "asset service" wording across skills, references, evals and public pages; detection by `foundry_*` tools kept; version 0.2.1.
- **Next task.** After merge: tag `v0.2.1`, watch the release run, then the sshlg-skills pin bump (its `skills.json` desc mirrors this description).

## 2026-10-20: v0.2.0, short router descriptions

Objective: free Claude Code's shared skill-listing budget (about 30,000 chars; 81 of
134 skills showed no description on 2026-10-20). The three descriptions are now
435-455 chars (2,570 to 1,340 in total); removed trigger phrases moved verbatim into
each body's `## Triggers`. `test/validate.py` caps a description at 500 chars. Checks:
`npm test`, `npm run test:negatives`, `node test/installer_test.js`,
`python3 test/evals_validate.py` and both `claude plugin validate --strict` runs exit 0.
Open: the umbrella's advertised-trigger check still reads descriptions only and
reports 10 body-only triggers until its context-diet change lands; the umbrella
re-pin is the umbrella's task, not this release's. Exact next task: none in this
repository for this change.

## Earlier: evidence navigation

The [verification index](evidence/verification.md) routes to existing evidence for
published version 0.1.4. The [FW00 packet](evidence/fw00-verification-index-20261013/README.md)
owns this docs-only change, its source ledger, checks and remaining gates.

Completed in the earlier source/publication wave: the [release packet](evidence/releases/2026-10-13-member-gates/README.md#published-readback)
records the original tag, successful run and package readback. This navigation
change does not rerun those historical events or assert installed/native quality.

Exact next task: integrate the frozen docs-only candidate through genuine required
checks and normal merge. Independent navigation/payload review and the owner's
local command set passed; the [subsequent gate receipt](evidence/fw00-verification-index-20261013/owner-gates.json)
preserves their exact sources. A successor containing only these receipts receives
final structural, link and package-conservation checks before promotion. No new
version, tag, publication, provider call or host-profile update belongs here.
