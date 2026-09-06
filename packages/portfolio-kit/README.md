# Portfolio Kit

Portfolio Kit is the reusable catalogue and evidence layer for the Vigilanty0x public portfolio. It turns a large repository collection into a smaller, inspectable product map without pretending that consolidation is complete before migration gates pass.

This repository currently contains three imported source modules with preserved history:

- `packages/open-source-portfolio-generator` — generate deterministic portfolio views from structured input;
- `packages/github-profile-dashboard` — render a bounded public dashboard from declared portfolio state;
- `packages/build-metrics-collector` — collect and summarize reproducible build/project evidence.

The modules remain individually testable. Portfolio Kit adds a **root contract** above them so the suite tells one product story instead of three unrelated tools.

## Architecture contract

The current public governance decision distinguishes the transition state from the prepared final state:

- **18 transitional targets** remain reviewable while migrations are incomplete;
- **16 final entities** are the prepared product/program topology;
- **17 active repositories** back those 16 entities because the portfolio/profile entity intentionally uses both `portfolio-kit` and the profile repository.

The root machine-readable contract is [`PORTFOLIO_KIT.json`](PORTFOLIO_KIT.json). It is bound to:

- governance main commit `b5a99b401eb26deaad7b6aa144afed64f0db70b1`;
- profile main commit `2f66106e4a9d852249483eda69c77974b2d44b7a`;
- exact imported source SHAs and tree-match/history-preservation evidence from the consolidation rehearsal.

`python scripts/check_portfolio_kit.py` fails closed when the final entity/repository counts drift, an expected canonical repository disappears, an imported module is promoted into the final active-repository set, source history/tree evidence is weakened, or archive becomes automatic.

## What Portfolio Kit is for

1. **Catalogue** — keep one canonical list of the final public product identities.
2. **Presentation** — generate profile/dashboard views from structured state instead of hand-maintained claims.
3. **Evidence** — attach exact SHAs, verification state, and dated measurements to public claims.
4. **Transition safety** — show source modules and migrations without presenting them as final active products.
5. **Adoption** — make the path from profile → project → quickstart → evidence short and reproducible.

## Current state

**PREPARED / REHEARSAL.** The imported module histories and source trees are preserved and the package matrix is CI-tested. This repository is not yet a stable release and this PR does not authorize source archival.

The archive gate stays **BLOCKED** until release, compatibility, consumer inventory, redirect/transition handling, rollback, and explicit human approval are all satisfied.

## Verification

The CI pipeline uses an explicit `ubuntu-24.04` runner, SHA-pinned external Actions, pinned Python build tooling, wheel installation, unit tests, compilation, outside-checkout import smoke, module CLI scenarios, and the root Portfolio Kit contract/counter-proof suite.

## Relationship to the public profile

The human-facing profile lives at [`vigilanty0x/vigilanty0x`](https://github.com/vigilanty0x/vigilanty0x). Portfolio Kit is the reusable product layer behind that presentation; it does not duplicate the account profile itself.

Public examples remain synthetic. No release, redirect, archive, deletion, or irreversible repository setting is performed by the root contract.
