## v0.2.7: the gate asks the umbrella about routed triggers

- **The gate asks the umbrella whether routed triggers are still advertised** (hub board row
  B-305): `test/validate.py` now calls the hub's `test/advertised_check.js` the way the other
  members do, in both directions (a routed trigger this member dropped, and an advertised phrase
  no route reaches). Inside the hub's submodule checkout it fails the gate; in a standalone clone
  it prints a note, because it cannot look.

## v0.2.6: web3d-assets description 4 characters shorter

- **web3d-assets' description is 4 characters shorter** ("sourcing, glTF pipeline"): 0.2.5's
  qualified trigger cost one character more than it saved, and the family's description total may
  fall but never rise (hub ratchet, 11455). Meaning unchanged.

## v0.2.5: web3d-assets names a 3D model

- **web3d-assets names a 3D model where an ML model reads the same** (hub board row B-297): "the
  model is too heavy" / «модель слишком тяжёлая» and «сожми модель» also describe an ML model
  ("the model is too heavy to deploy on the GPU" routed here, measured), so they now read "the 3D
  model is too heavy", «3D-модель слишком тяжёлая» and «сожми 3D-модель». The description stays
  within 300 characters ("a web scene budget").

## v0.2.4: descriptions within a 300-character budget

- Every skill description now fits a budget of about 300 characters (hub board row B-255 (a)):
  Claude Code lists every installed skill's description each session against a shared budget of
  about 30,000 characters, and the operator's listing measured 51,178, so less-used skills lost
  their descriptions. Measured with whitespace collapsed: `web3d-animation` 435 → 297,
  `web3d-assets` 449 → 299, `web3d-runtime` 455 → 288; total 1339 → 884.
- Each description keeps its router sentence, its boundary against sibling skills, the opt-out
  phrase and a short English and Russian trigger list. Every quoted trigger the description
  dropped is kept in the body's `## Triggers` section, so the family hook's words stay advertised
  (`test/advertised_check.js` in the hub).

## v0.2.3: the family member gate

- `test/family_gate.py`, the family's canonical member gate (hub B-108, B-109): the board
  parses (every row as wide as its header, no id twice) and `release.yml` keeps the tag-ancestry
  check (`fetch-depth: 0`, `git merge-base --is-ancestor`), each watched failing on a plant by
  `--self-test`. Wired into `npm test`; a byte-for-byte copy of the hub's `member-gate/family_gate.py`.

## v0.2.2: a shorter router description and a current ledger

- `web3d-assets`'s description says "an order in flight (its service's skill)": 0.2.1's generic wording had grown it by 14 characters, over the family's description budget. The verification ledger records this version.

## v0.2.1: the asset service is not named

- The skills, README, SKILL-CARD, SECURITY and manifest descriptions named a private asset-ordering service of the operator's machine. They now describe it generically ("the asset service") and still detect it by its `foundry_*` tools and delegate to its skill. The CLAUDE.md rule now says the service is never named. No behaviour changes.

## 0.2.0 (2026-10-20)

- Every skill's front-matter `description` is now a router, not a manual: one
  "Use when" sentence, a "NOT for" boundary naming the sibling skill, the opt-out
  phrase (no web3d, без web3d) and a few English and Russian triggers. Lengths before
  and after: web3d-animation 873 to 435, web3d-assets 856 to 450, web3d-runtime 841
  to 455 (2,570 to 1,340 chars in total).
- Why: Claude Code shares about 30,000 chars of skill listing across every installed
  skill. Measured on 2026-10-20, the operator's listing held 29,995 chars for 134 skills
  and 81 of them showed no description. Plugin skills cannot be hidden, so description
  length is the only lever.
- Every trigger phrase removed from a description moved verbatim (EN/RU pairs kept
  together) into a new `## Triggers` section at the end of that skill's body, so the
  family's routing hook still finds each of its words in the skill's text.
- `test/validate.py`: the house description cap drops from 970 to the family cap of
  500 chars; the standard's 1024 stays the hard limit. `CLAUDE.md` states the new rule.

## 0.1.4 — 2026-10-13

- Validate the owner board's table shape, unique task IDs and immediate Markdown
  separator before accepting a change.
- Validate the release job's full-history checkout and refusing ancestry check;
  reject unsupported or ambiguous workflow shapes. Forty-two process controls
  cover hostile edits and valid board/workflow forms.
- Run complete hosted validation nightly at 23:00 Europe/Warsaw or once for an
  explicitly frozen draft-to-ready candidate. Tag releases retain their existing
  validation and publication checks.

## 0.1.3 — 2026-10-10

- **The release refuses a lightweight tag.** `release.yml` gains one step, right after
  checkout and before any gate: `git cat-file -t` on the tag must print `tag`; a `commit`
  fails the job with the remedy (`git tag -a <tag> -m '<release>'` at the same commit)
  before anything is published. `git describe` and `git submodule status` see annotated
  tags only, and the 2026-10-09 family wave cut four lightweight member tags that the
  umbrella then read as each member's previous release. The step is identical across the
  family (umbrella plan 2026-10-10, T5 / REQ-6). Published tags are not re-cut.
- No skill, reference or installer change.

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
