# Security policy

## Supported versions

Security fixes are provided for the latest tagged minor release.

## Boundary

Build Metrics Collector reads only explicitly selected local Git metadata, JUnit XML, artifacts, and event JSON. It does not run tests, build source, execute a shell, call a model, send telemetry, or upload project data.

Controls include:

- strict closed event schemas and timezone-aware timestamps;
- safe resolved artifact paths and size limits;
- bounded non-shell Git subprocesses;
- standard-library XML parsing with file limits;
- atomic report writes;
- idempotency conflicts instead of silent replacement;
- append-only records with sequence and SHA-256 chain verification;
- HTML escaping for project, state, provenance, and diagnostics;
- no runtime dependencies or client-side JavaScript.

Metrics and descriptions can still reveal sensitive engineering context. Use neutral descriptions, avoid personal data, and apply repository-appropriate access control to event stores and reports. A hash chain detects changes relative to a trusted head; it is not a digital signature and does not stop an attacker from replacing the entire file.

## Reporting

Use GitHub's private security advisory interface for this repository. Include the version, a minimal synthetic reproduction, impact, and mitigation. Do not submit live credentials, private source, personal data, or proprietary build logs.

