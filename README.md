# Evidence-first tools for dependable AI and software workflows

I build public tools that make software and AI work easier to inspect, reproduce, and challenge: repository diagnostics, evidence gates, model routing, local AI, provenance, and bounded learning systems.

The portfolio is deliberately **evidence-first**. A green README is not a release. A project is not called stable until its release, installed-artifact smoke, compatibility contract, provenance, and rollback evidence agree.

## Start here

| Project | Problem it tackles | Current maturity | Evidence snapshot |
|---|---|---|---|
| [Apprentice AI](https://github.com/vigilanty0x/apprentice-ai) | Learn bounded procedures from permitted events while remaining local-first and preview-only | Prototype | 88 source + installed-wheel tests; hosted Linux/Windows release checks recorded on the merged 0.1.0 change |
| [Repo Doctor](https://github.com/vigilanty0x/repo-doctor) | Audit repositories without executing their code and return reproducible findings | Prototype | 115 tests plus source/wheel/sdist release gate and Linux/Windows matrix recorded on the merged 0.3.0 change |
| [ProofGate](https://github.com/vigilanty0x/proofgate) | Refuse `DONE` when declared evidence is missing, invalid, stale, or contradictory | Prototype | 87 tests from source, installed wheel and installed sdist on the merged evidence-orchestration change |
| [AI Assistance Manifest](https://github.com/vigilanty0x/ai-assistance-manifest) | Describe AI assistance, human control, and verification in a bounded machine-readable format | Prototype | Exact main SHA remains the previously verified profile snapshot |
| [Model Router](https://github.com/vigilanty0x/model-router) | Route tasks from declared capabilities and constraints instead of opaque preference | Prototype | Exact main SHA remains the previously verified profile snapshot |
| [Local AI Stack](https://github.com/vigilanty0x/local-ai-stack) | Inspect and coordinate declared local-model endpoints without pretending health equals correctness | Prototype | Exact main SHA remains the previously verified profile snapshot |

Machine-readable SHAs, evidence references, and residual limits live in [`PORTFOLIO.json`](PORTFOLIO.json).

## Portfolio architecture

The governance decision is now merged in [`vigilanty0x/.github`](https://github.com/vigilanty0x/.github). It distinguishes two states on purpose:

- **18 transitional targets** remain the safe review registry while migrations are incomplete.
- **16 final entities / 17 active repositories** are the prepared end state.

The final topology is **not activated by changing a number in a JSON file**. Every absorption still requires current migration evidence, compatibility, consumer inventory, redirect/transition handling, rollback, and explicit human approval.

The canonical portfolio presentation is split intentionally:

- [`vigilanty0x/vigilanty0x`](https://github.com/vigilanty0x/vigilanty0x) — the human-facing profile and evidence snapshot;
- [`portfolio-kit`](https://github.com/vigilanty0x/portfolio-kit) — the reusable portfolio/catalogue product target;
- [`.github`](https://github.com/vigilanty0x/.github) — governance, policy, state vocabulary, and reusable CI.

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
