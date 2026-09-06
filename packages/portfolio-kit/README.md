# Portfolio Kit

Portfolio Kit is the reusable catalogue and evidence layer for the Vigilanty0x public portfolio. It turns a large repository collection into a smaller, inspectable product map without pretending that consolidation is complete before migration gates pass.

This repository currently contains three imported source modules with preserved history:

- `packages/open-source-portfolio-generator` — generate deterministic portfolio views from structured input;
- `packages/github-profile-dashboard` — render a bounded public dashboard from declared portfolio state;
- `packages/build-metrics-collector` — collect and summarize reproducible build/project evidence.

The modules remain individually testable. Portfolio Kit adds a **root contract** above them so the suite tells one product story instead of three unrelated tools.

## Architecture contract

The current public governance decision distinguishes the observed transition
state from the locally prepared destination:

- **18 transitional targets / 112 public repositories** remain reviewable while migrations are incomplete;
- **6 product repositories + 2 support repositories** are the prepared public topology;
- the connected-account target is **9 repositories**, adding one private repository represented only by an aggregate count;
- the GitHub migration is **NOT_APPLIED** and deletion is not authorized.

The root machine-readable contract is [`PORTFOLIO_KIT.json`](PORTFOLIO_KIT.json). It is bound to:

- the exact local-only governance commit and exact public profile baseline commit recorded in the contract;
- exact imported source SHAs and tree-match/history-preservation evidence from the consolidation rehearsal.

`python scripts/check_portfolio_kit.py` fails closed when the six-product/two-support
topology drifts, the eight-public/nine-connected arithmetic changes, an expected
canonical repository disappears, an imported module is promoted into the final
active set, source history/tree evidence is weakened, GitHub migration is
claimed, or archive/deletion becomes authorized.

## What Portfolio Kit is for

1. **Catalogue** — keep one canonical list of the final public product identities.
2. **Presentation** — generate profile/dashboard views from structured state instead of hand-maintained claims.
3. **Evidence** — attach exact SHAs, verification state, and dated measurements to public claims.
4. **Transition safety** — show source modules and migrations without presenting them as final active products.
5. **Adoption** — make the path from profile → project → quickstart → evidence short and reproducible.

## Current state

**LOCAL PREPARATION / REHEARSAL.** The imported module histories and source
trees are preserved. The containing profile repository tests this contract and
its counter-proofs, but the prepared topology is not yet merged or applied on
GitHub. This work does not authorize source archival, deletion, transfer, or
redirect.

The archive gate stays **BLOCKED** until release, compatibility, consumer inventory, redirect/transition handling, rollback, and explicit human approval are all satisfied.

## Verification

The CI pipeline uses an explicit `ubuntu-24.04` runner, SHA-pinned external Actions, pinned Python build tooling, wheel installation, unit tests, compilation, outside-checkout import smoke, module CLI scenarios, and the root Portfolio Kit contract/counter-proof suite.

## Relationship to the public profile

The human-facing profile lives at [`vigilanty0x/vigilanty0x`](https://github.com/vigilanty0x/vigilanty0x).
In the prepared topology, Portfolio Kit lives under that repository's
`packages/portfolio-kit` directory as the reusable catalogue layer; it does not
remain a ninth public destination or duplicate the account profile itself.

Public examples remain synthetic. No release, redirect, archive, deletion, or irreversible repository setting is performed by the root contract.
