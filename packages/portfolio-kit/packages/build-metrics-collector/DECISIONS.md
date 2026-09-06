# Decision log

## D-001 — Events before dashboards

Versioned local events are the source of truth. The dashboard is a deterministic projection, so presentation changes cannot rewrite history and every number remains reproducible.

## D-002 — Human interventions are first-class

Human review, arbitration, and correction are recorded beside automated activity. This prevents the portfolio from implying that generated work required no human judgment.

## D-003 — Offline standard-library implementation

The first release has no service, account, telemetry, runtime dependency, or model call. This maximizes portability and makes the public demo safe and reproducible.

## D-004 — State is not color

Every loading, empty, degraded, timeout, error, and current state has explicit text. Color only reinforces it. Static reports expose no fake loading transition; host shells may use the loading contract before final HTML is available.

## D-005 — Idempotency conflicts are visible

Repeating an identical event is safe. Reusing its identity for changed meaning raises a conflict instead of silently replacing evidence.

## D-006 — No individual ranking

The core captures project construction evidence. It does not score people. Human-minute metrics require context and must not be used as a standalone productivity ranking.

