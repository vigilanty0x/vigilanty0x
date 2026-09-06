# Multi-tool projects for dependable AI and software workflows

I group related public tools into a small set of canonical projects. Each project owns a coherent problem area, one primary product identity, compatibility paths for absorbed tools, and evidence that can be checked again.

The portfolio is deliberately **evidence-first**. A green README is not a release. A project is not called stable until its release, installed-artifact smoke, compatibility contract, provenance, and rollback evidence agree.

## Bound public portfolio evidence

[`docs/index.html`](docs/index.html) is **generated**, not manually curated. Its program status, PR counts, consolidation load, stop reasons, and freshness still come from the preserved bounded extract of the read-only public-portfolio snapshot produced by `.github` workflow run `32163118044`. Its six featured projects come from [`PORTFOLIO.json`](PORTFOLIO.json).

The source binding is recorded in [`data/public-portfolio-live.manifest.json`](data/public-portfolio-live.manifest.json): upstream snapshot SHA-256 `1d7fb8cb01232accecc8b26df356e8e263df506f56a54938144c790e252eef0f`, exact source head `178c80653eb4ccba32768b32497c60fafb6ec558`, artifact id `9334368066`, and registry expiry `2026-09-17T23:59:59Z`.

The generator fails closed if the bounded source changes without its manifest, if the page drifts from the generated output, if the source stops being read-only, or if automatic mutation appears. The page also marks itself **STALE** in the browser after the registry TTL, and scheduled CI requires current evidence. This profile refresh does not rewrite those operational metrics to make them look newer.

Current bound source status: **STOPPED**. That is intentionally not rewritten to look healthier.

## Six concrete projects

These are product destinations, not GitHub Projects boards. Each row keeps one
public product identity while absorbing related tools behind compatibility
paths. The source counts come from the prepared 112-repository mapping. The CI
links prove the named remote `main` baseline only; the larger consolidation is
still local preparation.

| Canonical project | Prepared multi-tool scope | Sources | State | Exact hosted baseline evidence |
|---|---|---:|---|---|
| [Automation Control Plane](https://github.com/vigilanty0x/automation-control-plane) | Governed agent/software automation, worktrees, budgets, handoffs, routing, and recovery | 23 | Local preparation | `main` [`f2c3919926ac723fe41f79a960ef6e56aff149a8`](https://github.com/vigilanty0x/automation-control-plane/commit/f2c3919926ac723fe41f79a960ef6e56aff149a8); [CI 34038834426](https://github.com/vigilanty0x/automation-control-plane/actions/runs/34038834426) passed |
| [PromptOps](https://github.com/vigilanty0x/promptops) | Prompt/model evaluation, regressions, local model operations, scorecards, and routing | 15 | Local preparation | `main` [`d1b76b180d64b655d1fcd76df13427f66e5a8ce0`](https://github.com/vigilanty0x/promptops/commit/d1b76b180d64b655d1fcd76df13427f66e5a8ce0); [CI 34040771133](https://github.com/vigilanty0x/promptops/actions/runs/34040771133) passed |
| [RAG Lab](https://github.com/vigilanty0x/rag-lab) | Retrieval, citations, corpora, datasets, freshness, indexing, and RAG evaluation | 10 | Local preparation | `main` [`939ffd41af0c35802ed8a99067750b8414eb10fd`](https://github.com/vigilanty0x/rag-lab/commit/939ffd41af0c35802ed8a99067750b8414eb10fd); [CI 34041117357](https://github.com/vigilanty0x/rag-lab/actions/runs/34041117357) passed |
| [Shipcheck](https://github.com/vigilanty0x/shipcheck) | CI, merge/release readiness, risk, test evidence, deployment truth, and rollback | 15 | Local preparation | `main` [`a90a3795a17b15283c731297a6dc340dd98553d9`](https://github.com/vigilanty0x/shipcheck/commit/a90a3795a17b15283c731297a6dc340dd98553d9); [CI 34040636204](https://github.com/vigilanty0x/shipcheck/actions/runs/34040636204) passed |
| [Repo Doctor](https://github.com/vigilanty0x/repo-doctor) | Repository/runtime diagnostics, dependency/configuration health, developer docs, and provenance | 26 | Local preparation | `main` [`a8dfdd4dfb0c2bc229b19f9e5519f7951552ff23`](https://github.com/vigilanty0x/repo-doctor/commit/a8dfdd4dfb0c2bc229b19f9e5519f7951552ff23); [CI 34040750195](https://github.com/vigilanty0x/repo-doctor/actions/runs/34040750195) passed |
| [ProofGate](https://github.com/vigilanty0x/proofgate) | Evidence/audit/replay plus TrustKit security and Contract Lab API/schema checks | 16 | Local preparation | `main` [`83e05a0e94e54853dc70b4fbed082d6c8c9287ba`](https://github.com/vigilanty0x/proofgate/commit/83e05a0e94e54853dc70b4fbed082d6c8c9287ba); [CI 34040756618](https://github.com/vigilanty0x/proofgate/actions/runs/34040756618) passed |

Machine-readable SHAs, evidence references, and residual limits live in [`PORTFOLIO.json`](PORTFOLIO.json).

## Portfolio architecture

The prepared governance contract is pinned to local `.github` commit
`8a9aebeae578becf987d9a7143cdb6a2f3294551`. That commit has not been pushed;
the linked [`vigilanty0x/.github`](https://github.com/vigilanty0x/.github)
repository still shows the prior public baseline. The prepared contract
distinguishes two states on purpose:

- **18 transitional targets / 112 public repositories** remain the observed review registry while migrations are incomplete.
- **6 product repositories + 2 public support repositories** cover those 112 public source identities in the locally prepared destination map.
- The connected-account target is **9 repositories** because it adds one private repository represented only as an aggregate count.
- The GitHub migration state is **NOT_APPLIED** and deletion is **not authorized**.

Nine historical PromptOps source repositories are **archived read-only, not deleted**, with their source and compatibility evidence preserved under [`promptops/packages`](https://github.com/vigilanty0x/promptops/tree/main/packages). These archives record the current GitHub disposition; they do not activate the PromptOps absorption or any part of the prepared topology. The central register remains `OBSERVED_NONCOMPLIANT` until repeatable rollback and complete transition notices are evidenced. Its earlier 16-entity plan is historical input; this local contract supersedes it with eight public destinations without claiming activation.

The two public support repositories are split intentionally:

- [`vigilanty0x/vigilanty0x`](https://github.com/vigilanty0x/vigilanty0x) — the human-facing profile, generated evidence dashboard, and locally imported Portfolio Kit package;
- [`.github`](https://github.com/vigilanty0x/.github) — governance, policy, state vocabulary, and reusable CI.

Portfolio Kit and its three tools are prepared under
`packages/portfolio-kit`; workflow templates are prepared under `.github`.
Their existing GitHub repositories remain part of the observed state until a
separately approved transition is verified.

[`profile-settings.json`](profile-settings.json) declares these six umbrella repositories as the intended profile pins. It does not claim that GitHub account pins were applied; that remains a separate owner-only operation.

## Maturity vocabulary

- **Prototype** — behavior is inspectable and tested, but no compatibility or support promise is implied.
- **Preview** — a tagged prerelease, clean-install proof, migration notes, and bounded support window exist.
- **Stable** — reproducible artifacts, provenance, compatibility, release runbook, rollback proof, and post-publication verification all agree.

The six projects above are intentionally shown as **Prototype** here even when they have versioned release work. The profile does not promote maturity from a version string alone.

## What I optimize for

- fail-closed behavior instead of fake green states;
- deterministic outputs and stable error semantics;
- negative tests and counter-proofs, not only happy paths;
- clean installation outside the source checkout;
- source SHA, tree SHA, artifacts, and release claims that can be tied together;
- local-first or no-network defaults where that meaningfully reduces risk;
- explicit boundaries around AI assistance and human approval.

## What this profile does not claim

- No hosted-service uptime or support SLA is implied.
- No model vote or multi-agent consensus is treated as truth by itself.
- No project is called production-ready because a workflow file exists or a test count is large.
- No adoption, benchmark, latency, or quality claim is made without a dated reproducible measurement.
- Transitional repositories are not presented as final products merely because they still exist publicly.
- The local `codex/consolidate-six` work is not presented as merged, pushed, or applied to GitHub.
- The prepared count of nine is not presented as the current visible GitHub repository count.
- No source deletion, archive, transfer, or redirect is authorized by this profile.

## Public-data boundary

Public examples and fixtures are synthetic. Credentials, customer identifiers, non-public prompts, service coordinates, and production-derived datasets do not belong in this portfolio. The repository gate scans the public tree without printing the excluded token it is designed to detect.

## Local verification

```bash
python scripts/check_monorepo.py
node scripts/check-profile.mjs --root .
node scripts/generate-dashboard.mjs --root . --check --require-current
cd packages/portfolio-kit
python scripts/check_portfolio_kit.py
python -m unittest discover -s tests -p 'test_*.py'
```

These commands validate the prepared repository contents. They do not inspect
or mutate GitHub repository settings and cannot prove that the visible account
count has changed.

## Contributing

Choose a project above, reproduce the smallest useful behavior, and open an issue or pull request with the command, expected result, actual result, and a synthetic fixture when possible. Security reports should follow the repository security policy rather than a public issue.
