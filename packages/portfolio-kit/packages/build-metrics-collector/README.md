# Build Metrics Collector

Build Metrics Collector turns local build evidence into reproducible portfolio metrics: elapsed build time, commits, tests, retries, artifacts, and human interventions. Events remain inspectable in a hash-chained JSON Lines store; summaries expose provenance and freshness; the optional HTML report is accessible, responsive, and entirely offline.

No account, service, telemetry, or runtime dependency is required.

## Install

Python 3.11 or newer is required.

```bash
python -m pip install .
build-metrics --version
```

For isolated command-line use:

```bash
pipx install .
```

## Quick demo

Start with a disposable event store:

```bash
build-metrics import-event examples/commit-event.json --store /tmp/build-events.jsonl
build-metrics ingest-junit examples/junit.xml --store /tmp/build-events.jsonl --project synthetic-demo --suite unit
build-metrics artifact examples/artifact.txt --root . --store /tmp/build-events.jsonl --project synthetic-demo --kind demo
build-metrics record \
  --store /tmp/build-events.jsonl \
  --project synthetic-demo \
  --type human_intervention \
  --occurred-at 2026-08-15T10:05:00Z \
  --idempotency-key human-review-1 \
  --data '{"category":"review","minutes":12,"description":"Synthetic release review"}'
build-metrics summarize /tmp/build-events.jsonl --project synthetic-demo --format json
build-metrics summarize /tmp/build-events.jsonl --project synthetic-demo --format html --output /tmp/build-metrics.html
build-metrics replay /tmp/build-events.jsonl --json
```

Every fixture is synthetic. Open `/tmp/build-metrics.html` locally to inspect the mobile-ready view and download its normalized JSON.

## Automatic collectors

### Git commits

```bash
build-metrics collect-git . \
  --store .build-metrics/events.jsonl \
  --project my-public-project \
  --timeout 10 \
  --max-commits 1000
```

The adapter executes one bounded, non-shell `git log` command and records commit SHA plus Git's timezone-aware commit time. Repeating collection is idempotent by SHA.

### JUnit XML

```bash
build-metrics ingest-junit test-results.xml \
  --store .build-metrics/events.jsonl \
  --project my-public-project \
  --suite unit
```

The adapter records totals, pass/fail/skip counts, and duration. XML and artifact inputs are capped at 64 MiB.

### Build artifacts

```bash
build-metrics artifact dist/package.whl \
  --root . \
  --store .build-metrics/events.jsonl \
  --project my-public-project \
  --kind wheel
```

Artifact paths must remain inside the resolved root. Evidence includes safe relative path, size, kind, and SHA-256 digest.

## Manual evidence

Use `record` for sessions, retries, and human interventions. `--data` must match the selected event type.

```bash
build-metrics record --store events.jsonl --project demo \
  --type session_started --occurred-at 2026-08-15T10:00:00Z \
  --idempotency-key session-7-start --data '{"session_id":"session-7"}'

build-metrics record --store events.jsonl --project demo \
  --type retry --occurred-at 2026-08-15T10:03:00Z \
  --idempotency-key retry-tests-2 \
  --data '{"operation":"unit tests","attempt":2,"reason":"Synthetic flaky fixture"}'

build-metrics record --store events.jsonl --project demo \
  --type session_ended --occurred-at 2026-08-15T10:06:00Z \
  --idempotency-key session-7-end --data '{"session_id":"session-7"}'
```

`import-event` accepts a complete version 1.0 event JSON file for automation that already emits the contract.

## Event contract

Seven event types are supported:

| Type | Required data |
|---|---|
| `session_started` | `session_id` |
| `session_ended` | `session_id` |
| `commit` | hexadecimal `sha`; optional additions/deletions |
| `test_run` | total, passed, failed, skipped, duration; optional suite |
| `retry` | operation, attempt ≥ 2, reason |
| `artifact` | safe path, size, SHA-256, kind |
| `human_intervention` | category, minutes, description |

All timestamps require an explicit timezone. Unknown fields, unsafe paths, inconsistent test totals, negative measurements, and unknown event types are rejected.

## Normalized adapter states

Collectors return one of five states and never paint an error green:

| State | Meaning | CLI exit |
|---|---|---:|
| `success` | Evidence collected and validated | 0 |
| `empty` | Source was valid but contained no events | 0 |
| `degraded` | Some evidence collected; diagnostics remain | 2 |
| `timeout` | Reviewed time bound exceeded | 2 |
| `error` | Source, bounds, or parsing failed | 2 |

Invocation, event, store, and output errors use exit code 3.

## Derived metrics

`summarize` computes unique commits, line deltas when available, test totals and pass rate, retries and retries per commit, artifact count and bytes, human interventions and minutes, completed sessions, and session-derived build seconds.

An incomplete session changes the summary state to `degraded`; it does not invent elapsed time. Multiple projects require an explicit `--project` selection. Every summary includes event count, first/freshest event timestamps, source kinds, and the event-store head hash.

## Accessible report

The standalone HTML has:

- semantic header/main/section/footer landmarks;
- a keyboard skip link and visible focus treatment;
- responsive four-, two-, and one-column layouts;
- explicit `loading`, `empty`, `degraded`, `timeout`, `error`, and success copy;
- a live status region without a false completion claim;
- provenance, freshness, diagnostics, and a working normalized-JSON download;
- no JavaScript and no inert visible buttons;
- reduced-motion support and system color-scheme compatibility.

The synchronous CLI emits finalized states. `loading` is available in the view contract for host shells that embed the renderer.

## Integrity and idempotency

Each JSON Lines record contains a one-based sequence, previous hash, validated event, and canonical SHA-256 record hash. Replay rejects content edits, reordering, gaps, invalid events, and duplicate identities. Repeating an identical idempotency key returns the stored record; changing its meaning is a conflict.

The store is single-writer and tamper-evident, not signed. Persist a trusted head hash elsewhere when stronger audit assurance is required.

See [SPEC.md](SPEC.md), [VIEW_CONTRACT.json](VIEW_CONTRACT.json), [SECURITY.md](SECURITY.md), and [AI_ASSISTANCE.md](AI_ASSISTANCE.md).

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Contributions are welcome under Apache-2.0. Use only synthetic fixtures and public, standalone examples.

