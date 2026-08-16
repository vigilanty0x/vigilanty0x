# Evidence-first tools for dependable AI and software workflows

I build small, inspectable open-source tools around provenance, model routing,
repository diagnostics, delivery evidence, local AI, and agent operations.

The portfolio is being consolidated from many focused prototypes into a smaller
set of maintained products. No project below is presented as stable until it has
a tagged release, an install-and-smoke proof, a documented support window, and a
reproducible artifact chain.

## Six projects to inspect first

| Area | Project | What is implemented | Maturity | Verification |
|---|---|---|---|---|
| Provenance | [ai-assistance-manifest](https://github.com/vigilanty0x/ai-assistance-manifest) | Validate and render bounded AI-assistance manifests | Prototype | Offline source checks pass |
| Routing | [model-router](https://github.com/vigilanty0x/model-router) | Route tasks from declared capabilities, constraints, and state | Prototype | Offline source checks pass |
| Diagnostics | [repo-doctor-ai](https://github.com/vigilanty0x/repo-doctor-ai) | Inspect repository evidence and produce bounded findings | Prototype; consolidation planned | Tests pass; artifact build is blocked in the offline verifier |
| Delivery evidence | [safe-merge-gate](https://github.com/vigilanty0x/safe-merge-gate) | Evaluate merge evidence with explicit failure states | Prototype; consolidation planned | Offline source checks pass |
| Local AI | [local-ai-stack](https://github.com/vigilanty0x/local-ai-stack) | Inspect and coordinate declared local-model endpoints | Prototype | Offline source checks pass |
| Dashboard | [agent-dashboard](https://github.com/vigilanty0x/agent-dashboard) | Render bounded agent-run snapshots and evidence views | Prototype | Dependency-free checks pass; full locked build is not yet verified offline |

The exact tested commits and residual verification gaps are recorded in
[`PORTFOLIO.json`](PORTFOLIO.json).

## Maturity language

- **Prototype**: the behavior is inspectable and tested at source, but no support
  or compatibility promise is made.
- **Preview**: a tagged prerelease, clean-install proof, migration notes, and
  limited support window exist.
- **Stable**: reproducible artifacts, provenance, a supported compatibility
  contract, release runbook, and rollback proof exist.

At this baseline, all six highlighted repositories remain prototypes.

## What this portfolio does not claim

- No hosted service, uptime promise, or support SLA.
- No claim that multiple model outputs create truth or safety by themselves.
- No production-readiness claim based only on a README, a workflow, or test-file
  presence.
- No adoption or performance claim without a dated, reproducible measurement.

## Public-data boundary

Examples and fixtures are synthetic. Credentials, customer identifiers,
non-public prompts, service coordinates, and production-derived datasets do not
belong in these repositories. The profile gate detects an excluded marker by a
one-way digest without logging the matched value.

## Current consolidation direction

The active rehearsal reduces the audited portfolio to 18 product targets plus
this profile entry point. Source repositories will not be archived until target
releases, compatibility, redirections, consumer checks, rollback, and human
approval are all proven.

