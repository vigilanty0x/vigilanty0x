# AI assistance disclosure

## Scope

AI assistance helped draft the initial contracts, collectors, event store, summary logic, accessible report, tests, documentation, and synthetic fixtures for Build Metrics Collector 0.1.0. The repository owner selected the scope, approved public release, and remains responsible for maintenance.

## Human-controlled decisions

- Evidence is stored as versioned local events before aggregation.
- Human interventions are visible first-class metrics.
- Unknown ratios remain null; incomplete sessions degrade the view.
- The report displays provenance and freshness and never relies on color alone.
- The project is standalone, offline, and dependency-free at runtime.
- Individual ranking is explicitly out of scope.

## Verification

- Unit and adversarial tests cover every event type, bounds, timestamp and path rejection, adapter states, Git/JUnit/artifact collection, idempotency, tampering, summaries, project selection, all view states, HTML escaping, keyboard focus, mobile layout, reduced motion, and CLI flows.
- The package is compiled, built, installed into an isolated environment, and exercised through the installed CLI.
- The synthetic end-to-end demo verifies store replay plus JSON and HTML output.
- Repository-wide scans check credential-shaped values and prohibited private references before publication.
- Pull-request and post-merge CI must pass before release tagging.

## Limits

AI-assisted code can contain defects. The collector does not prove causal productivity, execute builds, resolve identity across rewritten Git history, sign stores, provide multi-writer coordination, or validate the social interpretation of metrics. Teams must apply consent and context when recording human activity.

