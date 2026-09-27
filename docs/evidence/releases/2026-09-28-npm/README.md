# npm release automation — 2026-09-28

## What happened

| Step | Who | Evidence |
|---|---|---|
| First publish of `@ssheleg/web3d-dev@0.1.1` from an authenticated CLI | operator (npm browser 2FA) | CLI printed `+ @ssheleg/web3d-dev@0.1.1`; the registry served it after ~4 minutes of read-replica lag (`GET /@ssheleg%2fweb3d-dev` → 200, `dist-tags.latest = 0.1.1`, 13th poll at 20 s) |
| Trusted publishing configured | operator | `npm trust github @ssheleg/web3d-dev --repo ssheleg/web3d-dev --file release.yml --allow-publish --yes` → `Trust configuration created`, permissions `publish, stage publish` |
| Publishing armed | agent | repository variable `PUBLISH_NPMJS=true` beside `RELEASE_ENABLED=true` |
| Unattended publish demonstrated | agent | `v0.1.2` tag → `release.yml` publish job. The run id and the registry check are recorded in the commit after the tag — this file cannot hold the proof of the release that ships it |

A skipped or green-but-idle publish job proves nothing; the proof is an unpublished version
appearing on the registry from the tag alone.

## Observed after the tag

`v0.1.2` → release run 36359053252: jobs `validate`, `House skill audit`, `release` and
**`publish`** all `success` (the publish job ran, it did not skip). The registry then served
`dist-tags.latest = 0.1.2` with a SLSA v1 provenance attestation
(`npm view @ssheleg/web3d-dev@0.1.2 dist.attestations.provenance`). No token was used; the
publish authenticated through GitHub OIDC.

