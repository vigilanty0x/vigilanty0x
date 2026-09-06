# Multi-tool projects for dependable AI and software workflows

I group related public tools into a small set of canonical projects. Each project owns a coherent problem area, one primary product identity, compatibility paths for absorbed tools, and evidence that can be checked again.

The portfolio is deliberately **evidence-first**. A green README is not a release. A project is not called stable until its release, installed-artifact smoke, compatibility contract, provenance, and rollback evidence agree.

## Bound public portfolio evidence

[`docs/index.html`](docs/index.html) is **generated**, not manually curated. Its program status, PR counts, consolidation load, stop reasons, and freshness still come from the preserved bounded extract of the read-only public-portfolio snapshot produced by `.github` workflow run `32163118044`. Its six featured projects come from [`PORTFOLIO.json`](PORTFOLIO.json).

The source binding is recorded in [`data/public-portfolio-live.manifest.json`](data/public-portfolio-live.manifest.json): upstream snapshot SHA-256 `1d7fb8cb01232accecc8b26df356e8e263df506f56a54938144c790e252eef0f`, exact source head `178c80653eb4ccba32768b32497c60fafb6ec558`, artifact id `9334368066`, and registry expiry `2026-09-17T23:59:59Z`.

The generator fails closed if the bounded source changes without its manifest, if the page drifts from the generated output, if the source stops being read-only, or if automatic mutation appears. The page also marks itself **STALE** in the browser after the registry TTL, and scheduled CI requires current evidence. This profile refresh does not rewrite those operational metrics to make them look newer.

Current bound source status: **STOPPED**. That is intentionally not rewritten to look healthier.

## Start with a project

| Canonical project | Multi-tool scope | Current maturity | Exact hosted evidence |
|---|---|---|---|
| [Automation Control Plane](https://github.com/vigilanty0x/automation-control-plane) | Governed jobs, DAGs, approvals, budgets, recovery, operator views, and AgentOps/AgentMesh compatibility | Prototype | `main` [`f2c3919926ac723fe41f79a960ef6e56aff149a8`](https://github.com/vigilanty0x/automation-control-plane/commit/f2c3919926ac723fe41f79a960ef6e56aff149a8), tree `16b9bae2745e9428ec7cef5ed49df3966b7ebf4a`; [CI run 34038834426](https://github.com/vigilanty0x/automation-control-plane/actions/runs/34038834426) passed 2 jobs |
| [Shipcheck](https://github.com/vigilanty0x/shipcheck) | Merge readiness, release readiness, CI diagnostics, risk, test evidence, and rollback tooling | Prototype | `main` [`a90a3795a17b15283c731297a6dc340dd98553d9`](https://github.com/vigilanty0x/shipcheck/commit/a90a3795a17b15283c731297a6dc340dd98553d9), tree `b8144fc3911a0eff11c5085ace3831cac9bd737d`; [CI run 34040636204](https://github.com/vigilanty0x/shipcheck/actions/runs/34040636204) passed 20 jobs |
| [Repo Doctor](https://github.com/vigilanty0x/repo-doctor) | Repository, dependency, configuration, container, database, and runtime diagnostics | Prototype | `main` [`a8dfdd4dfb0c2bc229b19f9e5519f7951552ff23`](https://github.com/vigilanty0x/repo-doctor/commit/a8dfdd4dfb0c2bc229b19f9e5519f7951552ff23), tree `d1cd218f6ecfb5463a26329cc00be507db6fb1b0`; [CI run 34040750195](https://github.com/vigilanty0x/repo-doctor/actions/runs/34040750195) passed 32 jobs |
| [PromptOps](https://github.com/vigilanty0x/promptops) | Prompt evaluation, regression, scorecards, failure corpora, routing, and multi-model decisions | Prototype | `main` [`d1b76b180d64b655d1fcd76df13427f66e5a8ce0`](https://github.com/vigilanty0x/promptops/commit/d1b76b180d64b655d1fcd76df13427f66e5a8ce0), tree `07bd894be8d2ec12791781853ac8a775f8b73d69`; [CI run 34040771133](https://github.com/vigilanty0x/promptops/actions/runs/34040771133) passed 41 jobs |
| [RAG Lab](https://github.com/vigilanty0x/rag-lab) | Retrieval, citation, corpus quality, freshness, datasets, indexing, and offline evaluation | Prototype | `main` [`939ffd41af0c35802ed8a99067750b8414eb10fd`](https://github.com/vigilanty0x/rag-lab/commit/939ffd41af0c35802ed8a99067750b8414eb10fd), tree `b2e28531eec8ea4e3e2f6a43c6ad6bddbb903e32`; [CI run 34041117357](https://github.com/vigilanty0x/rag-lab/actions/runs/34041117357) passed 29 jobs |
| [ProofGate](https://github.com/vigilanty0x/proofgate) | Evidence contracts, audit trails, ledgers, replay, status truth, and structured-output guards | Prototype | `main` [`83e05a0e94e54853dc70b4fbed082d6c8c9287ba`](https://github.com/vigilanty0x/proofgate/commit/83e05a0e94e54853dc70b4fbed082d6c8c9287ba), tree `c6aaf1702a0d335a2aaf093f640bc81ff9305593`; [CI run 34040756618](https://github.com/vigilanty0x/proofgate/actions/runs/34040756618) passed 32 jobs |

Machine-readable SHAs, evidence references, and residual limits live in [`PORTFOLIO.json`](PORTFOLIO.json).

## Portfolio architecture

The governance decision lives in [`vigilanty0x/.github`](https://github.com/vigilanty0x/.github). It distinguishes two states on purpose:

- **18 transitional targets** remain the safe review registry while migrations are incomplete.
- **16 final entities / 17 active repositories** are the prepared end state now being activated in bounded waves.

The first operational archive wave moved nine historical PromptOps source repositories into [`promptops/packages`](https://github.com/vigilanty0x/promptops/tree/main/packages). Those nine repositories are **archived read-only, not deleted**; their history and compatibility evidence remain in the canonical project. This records the GitHub disposition, not a completed governance gate: the central register remains `OBSERVED_NONCOMPLIANT` until repeatable rollback and complete transition notices are evidenced. The rest of the 16-entity topology is still being activated safely, one bounded wave at a time.

The canonical portfolio presentation is split intentionally:

- [`vigilanty0x/vigilanty0x`](https://github.com/vigilanty0x/vigilanty0x) — the human-facing profile and generated evidence dashboard;
- [`portfolio-kit`](https://github.com/vigilanty0x/portfolio-kit) — the reusable portfolio/catalogue product target;
- [`.github`](https://github.com/vigilanty0x/.github) — governance, policy, state vocabulary, and reusable CI.

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

## Public-data boundary

Public examples and fixtures are synthetic. Credentials, customer identifiers, non-public prompts, service coordinates, and production-derived datasets do not belong in this portfolio. The repository gate scans the public tree without printing the excluded token it is designed to detect.

## Contributing

Choose a project above, reproduce the smallest useful behavior, and open an issue or pull request with the command, expected result, actual result, and a synthetic fixture when possible. Security reports should follow the repository security policy rather than a public issue.
