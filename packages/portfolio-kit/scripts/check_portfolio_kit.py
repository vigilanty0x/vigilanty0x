#!/usr/bin/env python3
import json
import sys
from pathlib import Path

EXPECTED_ACTIVE = {
    ".github",
    "ai-assistance-manifest",
    "ai-software-factory",
    "apprentice-ai",
    "automation-control-plane",
    "contract-lab",
    "devdocs",
    "local-ai-stack",
    "model-router",
    "portfolio-kit",
    "promptops",
    "proofgate",
    "rag-lab",
    "repo-doctor",
    "shipcheck",
    "trustkit",
    "vigilanty0x",
}
EXPECTED_MODULES = {
    "open-source-portfolio-generator",
    "github-profile-dashboard",
    "build-metrics-collector",
}
REQUIRED_ARCHIVE_GATES = {
    "release",
    "compatibility",
    "consumers",
    "redirect",
    "rollback",
    "humanApproval",
}


def is_sha(value):
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value)


def validate(data, root=Path(".")):
    errors = []
    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    if data.get("state") != "PREPARED":
        errors.append("state must remain PREPARED until release gates pass")
    if data.get("scope") != "PUBLIC_ONLY":
        errors.append("scope must remain PUBLIC_ONLY")

    governance = data.get("governance", {})
    profile = data.get("profile", {})
    if governance.get("repository") != ".github" or not is_sha(governance.get("commit")):
        errors.append("governance must bind .github to an exact 40-character SHA")
    if profile.get("repository") != "vigilanty0x" or not is_sha(profile.get("commit")):
        errors.append("profile must bind vigilanty0x to an exact 40-character SHA")

    architecture = data.get("architecture", {})
    if architecture.get("transitionalTargetCount") != 18:
        errors.append("transitionalTargetCount must be 18")
    if architecture.get("finalEntityCount") != 16:
        errors.append("finalEntityCount must be 16")
    if architecture.get("activeRepositoryCount") != 17:
        errors.append("activeRepositoryCount must be 17")

    active = architecture.get("activeRepositories")
    if not isinstance(active, list) or len(active) != 17 or len(set(active)) != 17:
        errors.append("activeRepositories must contain exactly 17 unique repositories")
    elif set(active) != EXPECTED_ACTIVE:
        errors.append("activeRepositories does not match the prepared canonical set")

    entities = architecture.get("entities")
    if not isinstance(entities, list) or len(entities) != 16:
        errors.append("entities must contain exactly 16 entries")
    else:
        ids = [entry.get("id") for entry in entities]
        if len(set(ids)) != 16:
            errors.append("entity ids must be unique")
        mapped = []
        for entry in entities:
            repositories = entry.get("repositories")
            if not isinstance(repositories, list) or not repositories:
                errors.append(f"entity {entry.get('id')} must map to at least one repository")
                continue
            mapped.extend(repositories)
        if set(mapped) != EXPECTED_ACTIVE or len(mapped) != 17:
            errors.append("entity-to-repository mapping must resolve to the exact 17-repository canonical set")
        apprentice = next((entry for entry in entities if entry.get("id") == "apprentice-ai"), None)
        if not apprentice or apprentice.get("standalone") is not True:
            errors.append("apprentice-ai must remain standalone")

    modules = data.get("modules")
    if not isinstance(modules, list) or len(modules) != 3:
        errors.append("modules must contain exactly three imported source modules")
    else:
        names = {module.get("repository") for module in modules}
        if names != EXPECTED_MODULES:
            errors.append("module set drifted from the audited three-source Portfolio Kit import")
        if names & EXPECTED_ACTIVE:
            errors.append("imported source modules must not be promoted into the final active repository set")
        for module in modules:
            name = module.get("repository", "<unknown>")
            if not is_sha(module.get("sourceHeadSha")) or not is_sha(module.get("sourceTreeSha")):
                errors.append(f"module {name} must retain exact source head/tree SHAs")
            if module.get("historyPreserved") is not True or module.get("treeMatch") is not True:
                errors.append(f"module {name} must retain historyPreserved=true and treeMatch=true")
            path = module.get("path")
            if not isinstance(path, str) or not (root / path).is_dir():
                errors.append(f"module {name} path is missing from this checkout")

    archive = data.get("archive", {})
    if archive.get("automatic") is not False:
        errors.append("archive must never be automatic")
    if archive.get("gate") != "BLOCKED":
        errors.append("archive gate must remain BLOCKED in this rehearsal")
    if set(archive.get("required", [])) != REQUIRED_ARCHIVE_GATES:
        errors.append("archive required gates must include release, compatibility, consumers, redirect, rollback, and humanApproval")

    return errors


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "PORTFOLIO_KIT.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: cannot load {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate(data, root)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print("PASS: Portfolio Kit root contract is internally consistent and archive remains blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
