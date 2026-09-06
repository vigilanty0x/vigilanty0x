# Build Metrics Collector specification 1.0

## Purpose

The collector records facts about AI-assisted software construction without relying on a private platform or unverifiable narrative. Raw events remain replayable; summaries are deterministic functions of a selected project's events.

## Event invariant

Every stored event must:

1. match the exact version 1.0 field set;
2. use a known event type and type-specific data contract;
3. contain a timezone-aware timestamp;
4. have unique event and idempotency identities in the store;
5. participate in a valid sequence and SHA-256 hash chain.

An invalid event is never partially stored.

## Adapter result contract

Adapters return state, zero or more validated events, stable diagnostics, and provenance. `success` and `empty` are complete. `degraded`, `timeout`, and `error` are blocked states with exit code 2. Events from a degraded adapter may be persisted, but the diagnostic remains visible.

## Summary contract

- `success`: selected events were summarized and every observed session paired correctly.
- `empty`: the selected project has zero events.
- `degraded`: metrics exist but one or more session boundaries are inconsistent.
- `error`: multiple projects were present without an explicit selection or normalization could not be trusted.

Metrics never substitute zero for an unknown ratio. Pass rate and retries per commit are `null` when their denominator is zero.

## Provenance

Every non-empty summary includes event count, earliest event, freshest event, sorted source kinds, and the full store head hash. The report does not use wall-clock generation time, so identical stores produce identical JSON and HTML.

## Store bounds

- Event JSON import: 1 MiB.
- Adapter XML or artifact: 64 MiB.
- Record: 512 KiB.
- Store: 128 MiB.
- Git commits per collection: 1 to 10,000; default 1,000.
- Git timeout: 1 to 300 seconds; default 10.

Larger programs should rotate stores by release and preserve trusted head hashes.

## View actions

The version 1.0 HTML exposes two interactive elements:

- a skip link that moves keyboard focus to the metrics region;
- a download link whose data URI contains the exact normalized summary JSON.

The diagnostics details element is native browser disclosure. There are no custom buttons or JavaScript actions. Loading, empty, degraded, timeout, error, and current states have distinct text and non-color cues.

## Rollback and uninstall

The collectors only append to the explicitly selected store and write explicitly selected reports. Remove the Python package and those files to uninstall. No account, daemon, database, telemetry, scheduled job, or remote data remains.

