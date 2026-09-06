# Open-source Portfolio Generator

## Purpose

Generate deterministic, context-safe Markdown from bounded public repository metadata.

## Non-goals

It does not call a hosting service, verify repository ownership, publish pages, or accept non-public entries.

## Install

Requires Python 3.11 or newer.

```console
python -m pip install .
```

## CLI and API

Run the built-in positive and negative control:

```console
portfolio-generator probe
```

Process JSON from a file:

```console
portfolio-generator generate --input examples/basic.json
```

The public Python seam is `open_source_portfolio_generator.generate`:

```python
from open_source_portfolio_generator import generate
```

Functions return structured JSON-compatible results and reject malformed input without raising validation exceptions.

## Example

A runnable input is provided at `examples/basic.json`. CLI output is deterministic and includes either a SHA-256 evidence field or an explicit validation failure.

## Security and trust model

Every repository entry is validated before rendering. A single non-public or malformed entry blocks output, and interpolated text is escaped for Markdown and HTML contexts. The tool performs no network calls.

## Limitations

Only declared metadata is represented, with at most 500 unique repositories and bounded names, descriptions, and star counts.

## Tests

Run the same local gates used by CI:

```console
python -m unittest discover -s tests -v
python scripts/check.py
python -m build --no-isolation
portfolio-generator probe
portfolio-generator generate --input examples/basic.json
```

CI tests Python 3.11 and 3.12, installs the project and rebuilt wheel, imports the installed package, and exercises both the probe and example.

## AI disclosure

AI assistance supported defensive implementation, adversarial test design, and documentation. See [AI_ASSISTANCE.md](AI_ASSISTANCE.md) for scope and review expectations.

## License

Apache-2.0. See [LICENSE](LICENSE).

