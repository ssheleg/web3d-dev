# Contributing

Thanks for looking. This pack ships text an agent executes, so a change is
reviewed like code.

## Verify a change offline

```bash
npm test                 # structure, version sync, budgets, references, links
npm run test:negatives   # plants each defect; fails if a guard stays green
node test/installer_test.js
bash -n install.sh
claude plugin validate . --strict
claude plugin validate plugins/web3d-dev --strict
```

`python3 test/check_schemas.py` fetches the two `$schema` addresses and
`python3 test/gen_three_exports.py` refreshes the three.js export snapshot; both are
outside `npm test` because that suite must stay offline.

## House rules for the content

- **Every fact carries its receipt.** An API name, a flag or a number is verified
  against the pinned three.js release (or the named tool version) and cited by file
  and line or URL, dated. Claims from memory do not ship: three.js moves monthly.
- **Prose is English.** Russian appears only in trigger phrases inside a
  `description`, where the string itself is what makes the skill fire.
- A body stays under 475 lines and ~4750 tokens; depth goes to `references/`,
  one level deep, each named from the body with a "read this when" trigger.
- A skill answers one question. If a change makes a body answer two, it is two
  skills or a reference.
- Bump the version in all five places at once — the validator enforces it.

## Reporting something wrong

An out-of-date fact is a bug and worth an issue on its own: name the skill, the
claim, and the page that contradicts it.
