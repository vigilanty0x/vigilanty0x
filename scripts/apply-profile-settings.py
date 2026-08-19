#!/usr/bin/env python3
"""Apply and verify the bounded A01 public GitHub profile settings contract.

The token is read only from PROFILE_ADMIN_TOKEN and is never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
API_VERSION = "2026-03-10"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "profile-settings.json"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def request_json(method: str, path: str, token: str, payload: Any | None = None, allowed: tuple[int, ...] = (200,)) -> tuple[int, Any]:
    url = path if path.startswith("https://") else f"{API}{path}"
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "vigilanty0x-a01-profile-settings",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8")) if raw else None
            if response.status not in allowed:
                raise RuntimeError(f"Unexpected HTTP status {response.status} for {method} {path}")
            return response.status, data
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        if exc.code in allowed:
            data = json.loads(raw) if raw else None
            return exc.code, data
        try:
            parsed = json.loads(raw)
            message = parsed.get("message", "GitHub API request failed")
        except json.JSONDecodeError:
            message = "GitHub API request failed"
        raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {message}") from exc


def require_token() -> str:
    token = os.environ.get("PROFILE_ADMIN_TOKEN", "").strip()
    if not token:
        raise RuntimeError("PROFILE_ADMIN_TOKEN is not configured")
    return token


def merge_topics(owner: str, repository: str, required: list[str], token: str) -> list[str]:
    _, current = request_json("GET", f"/repos/{owner}/{repository}/topics", token)
    existing = current.get("names", []) if isinstance(current, dict) else []
    merged = sorted(set(existing) | set(required))
    if len(merged) > 20:
        raise RuntimeError(f"Topic merge for {repository} would exceed GitHub's 20-topic limit")
    request_json("PUT", f"/repos/{owner}/{repository}/topics", token, {"names": merged}, allowed=(200,))
    return merged


def ensure_pages(owner: str, repository: str, build_type: str, token: str) -> None:
    status, current = request_json("GET", f"/repos/{owner}/{repository}/pages", token, allowed=(200, 404))
    if status == 404:
        request_json("POST", f"/repos/{owner}/{repository}/pages", token, {"build_type": build_type}, allowed=(201,))
        return
    if not isinstance(current, dict) or current.get("build_type") != build_type:
        request_json("PUT", f"/repos/{owner}/{repository}/pages", token, {"build_type": build_type}, allowed=(204,))


def apply(config: dict[str, Any], token: str) -> dict[str, Any]:
    owner = config["owner"]
    profile = config["profile"]
    pages = config["pages"]

    _, viewer = request_json("GET", "/user", token)
    if not isinstance(viewer, dict) or viewer.get("login") != owner:
        raise RuntimeError("PROFILE_ADMIN_TOKEN does not authenticate as the configured owner")

    ensure_pages(owner, pages["repository"], pages["buildType"], token)

    request_json(
        "PATCH",
        "/user",
        token,
        {"bio": profile["bio"], "blog": profile["website"]},
        allowed=(200,),
    )
    request_json(
        "PATCH",
        f"/repos/{owner}/{pages['repository']}",
        token,
        {"homepage": profile["website"]},
        allowed=(200,),
    )

    topic_result: dict[str, list[str]] = {}
    for repository, required in config["topics"].items():
        topic_result[repository] = merge_topics(owner, repository, required, token)

    return {
        "status": "APPLIED",
        "owner": owner,
        "profileWebsite": profile["website"],
        "pagesRepository": pages["repository"],
        "topics": topic_result,
        "tokenValueIncluded": False,
    }


def graphql_pins(owner: str, token: str) -> list[str]:
    query = """
    query($login: String!) {
      repositoryOwner(login: $login) {
        ... on User {
          pinnedItems(first: 6) {
            nodes {
              __typename
              ... on Repository { nameWithOwner }
            }
          }
        }
      }
    }
    """
    _, response = request_json(
        "POST",
        f"{API}/graphql",
        token,
        {"query": query, "variables": {"login": owner}},
        allowed=(200,),
    )
    if response.get("errors"):
        raise RuntimeError("GitHub GraphQL returned errors while reading pinned items")
    nodes = (((response.get("data") or {}).get("repositoryOwner") or {}).get("pinnedItems") or {}).get("nodes") or []
    return [node["nameWithOwner"].split("/", 1)[1] for node in nodes if node.get("__typename") == "Repository" and node.get("nameWithOwner", "").startswith(f"{owner}/")]


def verify(config: dict[str, Any], token: str) -> dict[str, Any]:
    owner = config["owner"]
    profile = config["profile"]
    pages = config["pages"]
    findings: list[str] = []

    _, public_user = request_json("GET", f"/users/{owner}", token)
    if public_user.get("bio") != profile["bio"]:
        findings.append("profile-bio")
    if public_user.get("blog") != profile["website"]:
        findings.append("profile-website")

    _, profile_repo = request_json("GET", f"/repos/{owner}/{pages['repository']}", token)
    if profile_repo.get("homepage") != profile["website"]:
        findings.append("repository-homepage")
    if profile_repo.get("has_pages") is not True:
        findings.append("pages-enabled")

    _, page_state = request_json("GET", f"/repos/{owner}/{pages['repository']}/pages", token, allowed=(200, 404))
    if not isinstance(page_state, dict) or page_state.get("build_type") != pages["buildType"]:
        findings.append("pages-build-type")

    for repository, required in config["topics"].items():
        _, current = request_json("GET", f"/repos/{owner}/{repository}/topics", token)
        names = set(current.get("names", [])) if isinstance(current, dict) else set()
        if not set(required).issubset(names):
            findings.append(f"topics:{repository}")

    actual_pins = graphql_pins(owner, token)
    if actual_pins != config["pins"]:
        findings.append("pinned-repositories")

    result = {
        "status": "PASS" if not findings else "FAIL",
        "owner": owner,
        "findings": findings,
        "expectedPins": config["pins"],
        "observedPins": actual_pins,
        "expectedWebsite": profile["website"],
        "tokenValueIncluded": False,
    }
    if findings:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("apply", "verify"))
    args = parser.parse_args()
    config = load_config()
    token = require_token()
    result = apply(config, token) if args.mode == "apply" else verify(config, token)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed without ever printing the token
        print(f"profile-settings-error: {exc}", file=sys.stderr)
        raise SystemExit(1)
