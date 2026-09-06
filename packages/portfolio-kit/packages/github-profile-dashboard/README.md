# GitHub Profile Dashboard

## Purpose

Aggregate a bounded declared public repository snapshot into deterministic metrics and SHA-256 evidence.

## Non-goals

It does not access GitHub, validate ownership, refresh data, or infer private repository information.

## Install

Requires Python 3.11 or newer.

```console
python -m pip install .
```

## CLI and API

Run the built-in positive and negative control:

```console
github-profile-dashboard probe
```

Process JSON from a file:

```console
github-profile-dashboard build --input examples/basic.json
```

The public Python seam is `github_profile_dashboard.dashboard`:

```python
from github_profile_dashboard import dashboard
```

Functions return structured JSON-compatible results and reject malformed input without raising validation exceptions.

## Example

A runnable input is provided at `examples/basic.json`. CLI output is deterministic and includes either a SHA-256 evidence field or an explicit validation failure.

## Security and trust model

Every repository dictionary is validated before use. Names must be unique, visibility must be public, and all metrics are strict bounded non-boolean integers. The tool performs no network calls.

## Limitations

At most 500 repositories are accepted, and results describe only the caller-supplied public snapshot.

## Tests

Run the same local gates used by CI:

```console
python -m unittest discover -s tests -v
python scripts/check.py
python -m build --no-isolation
github-profile-dashboard probe
github-profile-dashboard build --input examples/basic.json
```

CI tests Python 3.11 and 3.12, installs the project and rebuilt wheel, imports the installed package, and exercises both the probe and example.

## AI disclosure

AI assistance supported defensive implementation, adversarial test design, and documentation. See [AI_ASSISTANCE.md](AI_ASSISTANCE.md) for scope and review expectations.

## License

Apache-2.0. See [LICENSE](LICENSE).

