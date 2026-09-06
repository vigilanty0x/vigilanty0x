#!/usr/bin/env python3
import json
import sys
from pathlib import Path

EXPECTED_ACTIVE = {
    ".github",
    "automation-control-plane",
    "promptops",
    "proofgate",
    "rag-lab",
    "repo-doctor",
    "shipcheck",
    "vigilanty0x",
}
EXPECTED_ENTITY_KINDS = {
    "automation-control-plane": "PRODUCT",
    "promptops": "PRODUCT",
    "rag-lab": "PRODUCT",
    "shipcheck": "PRODUCT",
    "repo-doctor": "PRODUCT",
    "proofgate": "PRODUCT",
    "community-governance": "SUPPORT",
    "portfolio-profile": "SUPPORT",
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
    if data.get("schemaVersion") != 2:
        errors.append("schemaVersion must be 2")
    if data.get("state") != "PREPARED":
        errors.append("state must remain PREPARED until release gates pass")
    if data.get("implementationState") != "LOCAL_ONLY":
        errors.append("implementationState must remain LOCAL_ONLY")
    if data.get("githubMigrationState") != "NOT_APPLIED":
        errors.append("githubMigrationState must remain NOT_APPLIED")
    if data.get("scope") != "PUBLIC_ONLY":
        errors.append("scope must remain PUBLIC_ONLY")
    if data.get("deletionAuthorized") is not False:
        errors.append("deletion must remain unauthorized")

    governance = data.get("governance", {})
    profile = data.get("profile", {})
    if governance.get("repository") != ".github" or not is_sha(governance.get("commit")) or governance.get("binding") != "LOCAL_ONLY":
        errors.append("governance must bind .github to an exact local-only 40-character SHA")
    if profile.get("repository") != "vigilanty0x" or not is_sha(profile.get("commit")) or profile.get("binding") != "PUBLIC_MAIN_BASELINE":
        errors.append("profile must bind vigilanty0x to an exact 40-character SHA")

    architecture = data.get("architecture", {})
    if architecture.get("transitionalTargetCount") != 18:
        errors.append("transitionalTargetCount must be 18")
    if architecture.get("sourcePublicRepositoryCount") != 112:
        errors.append("sourcePublicRepositoryCount must be 112")
    if architecture.get("finalEntityCount") != 8:
        errors.append("finalEntityCount must be 8")
    if architecture.get("productRepositoryCount") != 6:
        errors.append("productRepositoryCount must be 6")
    if architecture.get("supportRepositoryCount") != 2:
        errors.append("supportRepositoryCount must be 2")
    if architecture.get("activeRepositoryCount") != 8:
        errors.append("activeRepositoryCount must be 8")
    if architecture.get("privateRepositoryCount") != 1:
        errors.append("privateRepositoryCount must be the aggregate value 1")
    if architecture.get("connectedRepositoryCount") != 9:
        errors.append("connectedRepositoryCount must be 9")
    if architecture.get("activeRepositoryCount", 0) + architecture.get("privateRepositoryCount", 0) != architecture.get("connectedRepositoryCount"):
        errors.append("connectedRepositoryCount must equal public and private aggregate counts")

    active = architecture.get("activeRepositories")
    if not isinstance(active, list) or len(active) != 8 or len(set(active)) != 8:
        errors.append("activeRepositories must contain exactly 8 unique public repositories")
    elif set(active) != EXPECTED_ACTIVE:
        errors.append("activeRepositories does not match the prepared canonical set")

    entities = architecture.get("entities")
    if not isinstance(entities, list) or len(entities) != 8:
        errors.append("entities must contain exactly 8 entries")
    else:
        ids = [entry.get("id") for entry in entities]
        if len(set(ids)) != 8 or set(ids) != set(EXPECTED_ENTITY_KINDS):
            errors.append("entity ids must be unique")
        mapped = []
        for entry in entities:
            if entry.get("kind") != EXPECTED_ENTITY_KINDS.get(entry.get("id")):
                errors.append(f"entity {entry.get('id')} has the wrong kind")
            repositories = entry.get("repositories")
            if not isinstance(repositories, list) or not repositories:
                errors.append(f"entity {entry.get('id')} must map to at least one repository")
                continue
            mapped.extend(repositories)
        if set(mapped) != EXPECTED_ACTIVE or len(mapped) != 8:
            errors.append("entity-to-repository mapping must resolve to the exact 8-repository public canonical set")

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
    if archive.get("deletionAuthorized") is not False:
        errors.append("archive contract must not authorize deletion")
    if archive.get("repositoryMutationAuthorized") is not False:
        errors.append("archive contract must not authorize repository mutation")
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
    print("PASS: Portfolio Kit maps six products plus two supports; target is eight public/nine connected; GitHub migration and deletion remain blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
