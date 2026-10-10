# Annotated-tag release gate — 2026-10-10

`0.1.3` adds one step to `release.yml`: right after checkout, `git cat-file -t` on the tag
must print `tag`, or the release job fails before anything is published (umbrella plan
2026-10-10, T5 / REQ-6).

| Step | Evidence |
|---|---|
| Refusal planted | The step's `run:` body, extracted by YAML parse from `release.yml`, replayed in a scratch repository: lightweight `v9.9.9` → `::error::v9.9.9 is a commit, not an annotated tag object…`, exit 1; annotated `v9.9.10` → exit 0 |
| Merge | [PR 4](https://github.com/ssheleg/web3d-dev/pull/4), squash `5f7c3273163cff05e73707159805fb3e6592def1`; tip subject carries `(#4)` |
| Tag | `v0.1.3` annotated (`git cat-file -t v0.1.3` → `tag`), dereferences to the merge commit |
| Release run | [38075437837](https://github.com/ssheleg/web3d-dev/actions/runs/38075437837): validate, house audit, release and **publish** all `success`; the new step printed `v0.1.3 is annotated` |
| Registry | `npm view @ssheleg/web3d-dev version` → `0.1.3`; integrity `sha512-1jnWncadV7Dd7PX5VF9TYjb7D3ObM0JqEpWiKo1+Cb2RrGcv8xj6WAIWqqlMQSUz8f83TFiTG7TAbPmHx6EbvA==` recomputed from the downloaded tarball; all 20 files byte-equal to `git show <gitHead>:<path>`; SLSA provenance advertised |

Installation in a host and the umbrella re-pin are outside this record.
