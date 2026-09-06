"""Render bounded, public-only repository metadata as safe Markdown."""

import argparse
import hashlib
import html
import json
import re

NAME = re.compile(r"[A-Za-z0-9_.-]{1,100}")
MAX_REPOSITORIES = 500
MAX_STARS = 1_000_000_000
MARKDOWN = re.compile(r"([\\`*_{}\[\]()#+.!|>~-])")


def _text(value, maximum, *, allow_empty=False):
    if (not isinstance(value, str) or len(value) > maximum or not allow_empty and not value
            or any(ord(char) < 32 for char in value)):
        return None
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return None
    return MARKDOWN.sub(r"\\\1", html.escape(value, quote=False))


def generate(profile):
    if not isinstance(profile, dict) or not {"repositories"} <= set(profile) or not set(profile) <= {
            "display_name", "repositories"}:
        return {"ok": False, "errors": ["invalid_profile"]}
    repositories = profile["repositories"]
    display_name = _text(profile.get("display_name", "Open-source portfolio"), 100)
    if display_name is None or not isinstance(repositories, list) or len(repositories) > MAX_REPOSITORIES:
        return {"ok": False, "errors": ["invalid_repositories"]}
    parsed, names = [], set()
    for repository in repositories:
        if (not isinstance(repository, dict) or not {"name", "visibility"} <= set(repository)
                or not set(repository) <= {"name", "visibility", "description", "stars"}):
            return {"ok": False, "errors": ["invalid_repository"]}
        name, stars = repository["name"], repository.get("stars", 0)
        description = _text(repository.get("description", ""), 500, allow_empty=True)
        if (not isinstance(name, str) or not NAME.fullmatch(name) or name in names
                or repository["visibility"] != "public" or description is None
                or not isinstance(stars, int) or isinstance(stars, bool)
                or not 0 <= stars <= MAX_STARS):
            return {"ok": False, "errors": ["invalid_or_non_public_repository"]}
        names.add(name)
        parsed.append({"name": name, "safe_name": _text(name, 100),
                       "description": description, "stars": stars})
    ordered = sorted(parsed, key=lambda item: (-item["stars"], item["name"]))
    lines = [f"# {display_name}", ""]
    for repository in ordered:
        lines.extend([f"## {repository['safe_name']}", repository["description"],
                      f"Stars: {repository['stars']}", ""])
    body = "\n".join(lines)
    return {"ok": True, "markdown": body, "repository_count": len(ordered),
            "scope": "declared_public_metadata_only",
            "sha256": hashlib.sha256(body.encode()).hexdigest()}


def probe():
    good = generate({"repositories": [{"name": "demo", "visibility": "public"}]})
    bad = generate({"repositories": [{"name": "secret", "visibility": "private"}]})
    return {"ok": good["ok"] and not bad["ok"], "private_counter_proof": not bad["ok"]}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "probe"))
    parser.add_argument("--input")
    args = parser.parse_args(argv)
    try:
        data = json.load(open(args.input, encoding="utf-8")) if args.input else None
        out = probe() if args.command == "probe" else generate(data)
    except (OSError, UnicodeError, json.JSONDecodeError):
        out = {"ok": False, "errors": ["input_unreadable"]}
    print(json.dumps(out, sort_keys=True))
    return 0 if out["ok"] else 2
