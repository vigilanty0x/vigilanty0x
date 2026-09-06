"""Deterministic aggregation of bounded, public repository snapshots."""

import argparse
import hashlib
import json
import re

NAME = re.compile(r"[A-Za-z0-9_.-]{1,100}")
METRICS = ("stars", "forks", "open_issues")
MAX_REPOSITORIES = 500
MAX_METRIC = 1_000_000_000


def _metric(value):
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= MAX_METRIC


def dashboard(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {"repositories"}:
        return {"ok": False, "errors": ["invalid_snapshot"]}
    repositories = snapshot["repositories"]
    if not isinstance(repositories, list) or len(repositories) > MAX_REPOSITORIES:
        return {"ok": False, "errors": ["repository_bound"]}
    parsed, names = [], set()
    allowed = {"name", "visibility", *METRICS}
    for repository in repositories:
        if (not isinstance(repository, dict) or not {"name", "visibility"} <= set(repository)
                or not set(repository) <= allowed):
            return {"ok": False, "errors": ["invalid_repository"]}
        name = repository["name"]
        if (not isinstance(name, str) or not NAME.fullmatch(name) or name in names
                or repository["visibility"] != "public"
                or any(not _metric(repository.get(metric, 0)) for metric in METRICS)):
            return {"ok": False, "errors": ["invalid_or_non_public_repository"]}
        names.add(name)
        parsed.append({"name": name, **{metric: repository.get(metric, 0) for metric in METRICS}})
    totals = {metric: sum(repository[metric] for repository in parsed) for metric in METRICS}
    if any(value > MAX_METRIC for value in totals.values()):
        return {"ok": False, "errors": ["aggregate_metric_bound"]}
    rows = sorted(({"name": item["name"], "stars": item["stars"], "forks": item["forks"]}
                   for item in parsed), key=lambda item: (-item["stars"], item["name"]))
    body = {"repository_count": len(rows), **totals, "repositories": rows,
            "scope": "declared_public_snapshot_only"}
    return {"ok": True, **body,
            "snapshot_sha256": hashlib.sha256(json.dumps(body, sort_keys=True,
                                                           separators=(",", ":")).encode()).hexdigest()}


def probe():
    good = dashboard({"repositories": [{"name": "x", "visibility": "public", "stars": 1}]})
    bad = dashboard({"repositories": [{"name": "x", "visibility": "private"}]})
    return {"ok": good["ok"] and not bad["ok"], "counter_proof": not bad["ok"]}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "probe"))
    parser.add_argument("--input")
    args = parser.parse_args(argv)
    try:
        data = json.load(open(args.input, encoding="utf-8")) if args.input else None
        out = probe() if args.command == "probe" else dashboard(data)
    except (OSError, UnicodeError, json.JSONDecodeError):
        out = {"ok": False, "errors": ["input_unreadable"]}
    print(json.dumps(out, sort_keys=True))
    return 0 if out["ok"] else 2
