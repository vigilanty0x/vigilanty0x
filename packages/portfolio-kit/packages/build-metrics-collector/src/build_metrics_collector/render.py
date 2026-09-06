"""Accessible, responsive, dependency-free HTML rendering."""

from __future__ import annotations

from html import escape
import json
from typing import Any
from urllib.parse import quote

from .models import Summary

STATE_COPY = {
    "success": ("Current", "All recorded events were summarized successfully."),
    "loading": ("Loading", "Metrics are being collected and no completion claim is shown yet."),
    "empty": ("No data", "No events are available for this project yet."),
    "degraded": ("Degraded", "Metrics are available, but one or more sessions or sources are incomplete."),
    "timeout": ("Timed out", "Collection exceeded its reviewed time limit."),
    "error": ("Error", "Metrics could not be normalized into a trustworthy view."),
}

METRIC_LABELS = {
    "commits": "Commits",
    "tests_total": "Tests",
    "test_pass_rate": "Test pass rate",
    "retries": "Retries",
    "artifacts": "Artifacts",
    "human_interventions": "Human interventions",
    "human_minutes": "Human minutes",
    "build_seconds": "Build time",
}


def _format_metric(name: str, value: Any) -> str:
    if value is None:
        return "Not available"
    if name == "test_pass_rate":
        return f"{value}%"
    if name == "build_seconds":
        return f"{round(float(value), 1)} s"
    if name == "human_minutes":
        return f"{round(float(value), 1)} min"
    return str(value)


def render_html(summary: Summary) -> str:
    payload = summary.as_dict()
    title, description = STATE_COPY.get(summary.state, STATE_COPY["error"])
    cards = []
    for key, label in METRIC_LABELS.items():
        cards.append(
            '<article class="metric">'
            f'<h3>{escape(label)}</h3><p>{escape(_format_metric(key, summary.metrics.get(key)))}</p>'
            "</article>"
        )
    provenance = summary.provenance
    last_event = provenance.get("last_event_at")
    freshness = (
        f'<time datetime="{escape(str(last_event), quote=True)}">{escape(str(last_event))}</time>'
        if last_event
        else "Not available"
    )
    source_kinds = provenance.get("source_kinds", [])
    sources = ", ".join(str(item) for item in source_kinds) if source_kinds else "None"
    diagnostics = (
        "".join(f"<li><code>{escape(item)}</code></li>" for item in summary.diagnostics)
        if summary.diagnostics
        else "<li>None</li>"
    )
    raw_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    download_uri = "data:application/json;charset=utf-8," + quote(raw_json)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{escape(summary.project)} build metrics</title>
  <style>
    :root {{ --bg:#07111f; --panel:#111f31; --text:#eef6ff; --muted:#a9b8ca; --line:#29405c; --accent:#58d6c7; --warn:#ffc857; --bad:#ff6b81; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font:16px/1.55 system-ui,sans-serif; background:var(--bg); color:var(--text); }}
    a {{ color:var(--accent); }}
    a:focus-visible, summary:focus-visible {{ outline:3px solid var(--warn); outline-offset:3px; border-radius:3px; }}
    .skip {{ position:absolute; left:-999px; top:0; }}
    .skip:focus {{ left:1rem; top:1rem; background:var(--panel); padding:.75rem; z-index:2; }}
    header, main, footer {{ width:min(70rem, calc(100% - 2rem)); margin:auto; }}
    header {{ padding:3rem 0 1.5rem; }}
    h1 {{ font-size:clamp(2rem,7vw,4.5rem); line-height:1; margin:.25rem 0 1rem; }}
    .eyebrow {{ color:var(--accent); font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
    .status {{ border:1px solid var(--line); border-left:.45rem solid var(--accent); background:var(--panel); padding:1rem 1.2rem; border-radius:.7rem; }}
    .status[data-state="loading"], .status[data-state="degraded"], .status[data-state="timeout"] {{ border-left-color:var(--warn); }}
    .status[data-state="error"] {{ border-left-color:var(--bad); }}
    .status strong {{ display:block; font-size:1.2rem; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin:2rem 0; }}
    .metric {{ background:var(--panel); border:1px solid var(--line); border-radius:.7rem; padding:1rem; min-height:8rem; }}
    .metric h3 {{ color:var(--muted); font-size:.9rem; margin:0; }}
    .metric p {{ font-size:1.8rem; font-weight:750; margin:.6rem 0 0; overflow-wrap:anywhere; }}
    section {{ margin:2rem 0; }}
    dl {{ display:grid; grid-template-columns:max-content 1fr; gap:.55rem 1rem; }}
    dt {{ color:var(--muted); }} dd {{ margin:0; overflow-wrap:anywhere; }}
    details {{ border:1px solid var(--line); border-radius:.7rem; padding:1rem; }}
    summary {{ cursor:pointer; font-weight:700; }}
    footer {{ color:var(--muted); border-top:1px solid var(--line); padding:1.5rem 0 3rem; }}
    @media (max-width:52rem) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
    @media (max-width:32rem) {{ header {{ padding-top:2rem; }} .grid {{ grid-template-columns:1fr; }} dl {{ grid-template-columns:1fr; }} dd {{ margin-bottom:.5rem; }} }}
    @media (prefers-reduced-motion:reduce) {{ *,*::before,*::after {{ scroll-behavior:auto!important; }} }}
  </style>
</head>
<body>
  <a class="skip" href="#metrics">Skip to metrics</a>
  <header>
    <p class="eyebrow">Build Metrics Collector</p>
    <h1>{escape(summary.project)}</h1>
    <div class="status" data-state="{escape(summary.state, quote=True)}" role="status" aria-live="polite">
      <strong>{escape(title)}</strong>{escape(description)}
    </div>
  </header>
  <main id="metrics" tabindex="-1">
    <section aria-labelledby="metrics-heading">
      <h2 id="metrics-heading">Build overview</h2>
      <div class="grid">{''.join(cards)}</div>
    </section>
    <section id="provenance" aria-labelledby="provenance-heading">
      <h2 id="provenance-heading">Provenance and freshness</h2>
      <dl>
        <dt>View state</dt><dd>{escape(summary.state)}</dd>
        <dt>Events</dt><dd>{escape(str(provenance.get('event_count', 0)))}</dd>
        <dt>Freshest event</dt><dd>{freshness}</dd>
        <dt>Sources</dt><dd>{escape(sources)}</dd>
        <dt>Store head hash</dt><dd><code>{escape(str(provenance.get('store_head_hash') or 'Not available'))}</code></dd>
      </dl>
      <p><a href="{escape(download_uri, quote=True)}" download="build-metrics.json">Download normalized JSON</a></p>
    </section>
    <section aria-labelledby="diagnostics-heading">
      <h2 id="diagnostics-heading">Diagnostics</h2>
      <ul>{diagnostics}</ul>
    </section>
    <details>
      <summary>Method and limits</summary>
      <p>Metrics are derived only from versioned local events. Missing or incomplete sessions are reported as degraded; no value is inferred from absent evidence.</p>
    </details>
  </main>
  <footer>Generated offline. No account, telemetry, or remote source upload.</footer>
</body>
</html>
"""
