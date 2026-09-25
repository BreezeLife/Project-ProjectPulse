"""Read-only inspect and explicit init/update entrypoints."""

import argparse
import json
import sys

from .collector import collect
from .config import load_config
from .discovery import discover
from .fingerprint import fingerprint
from .renderer import render
from .schema import load_status
from .state import normalize_item, readiness
from .writer import persist


def inspect(project=None):
    workspace = discover(project)
    root = workspace["root"]
    collection = collect(root)
    snapshot = fingerprint(workspace, collection)
    stored, raw = load_status(root)
    config = load_config(root)
    status = "NOT INITIALIZED" if raw is None else "INVALID" if stored is None else "FRESH" if stored.get("fingerprint") == snapshot else "STALE"
    items = collection["items"]
    if stored:
        by_id = {item["id"]: item for item in stored["items"]}
        for item in items:
            previous = by_id.get(item["id"])
            if previous:
                item["verification"] = previous["verification"]
                item["evidence"] = (item["evidence"] + previous["evidence"])[:20]
                item["blocked"] = previous["blocked"]
                item["deferred"] = previous["deferred"]
                del by_id[item["id"]]
        items.extend(by_id.values())
    items = [normalize_item(item, snapshot) for item in items[:200]]
    report = {"project": config.get("name") or root.name, "vcs": workspace["vcs"],
              "branch": workspace["branch"], "head": workspace["head"], "workspace": workspace["workspace"],
              "status": status, "fingerprint": snapshot, "known_files": collection["known_files"],
              "items": items, "readiness": readiness(items), "entry_limit_reached": collection["entry_limit_reached"]}
    if status == "STALE":
        report["readiness"] = {key: "UNKNOWN" for key in report["readiness"]}
    return root, report, raw


def main(argv=None):
    parser = argparse.ArgumentParser(prog="project-pulse")
    parser.add_argument("operation", nargs="?", choices=("inspect", "init", "update"), default="inspect")
    parser.add_argument("--project", help="directory inside the target project")
    parser.add_argument("--json", action="store_true", help="emit machine-readable report")
    args = parser.parse_args(argv)
    try:
        root, report, raw = inspect(args.project)
        if args.operation == "init" and raw is not None:
            raise ValueError("Project Pulse state already exists")
        if args.operation == "update" and raw is None:
            raise ValueError("project is not initialized; use init")
        if args.operation != "inspect":
            state = {"schema_version": 1, "project": report["project"], "fingerprint": report["fingerprint"],
                     "vcs": report["vcs"], "branch": report["branch"], "head": report["head"],
                     "items": [{key: item[key] for key in ("id", "title", "implementation", "verification", "evidence", "blocked", "deferred")}
                               for item in report["items"]]}
            report["status"] = "FRESH"
            persist(root, state, render(report), expected_raw=raw, initialize=args.operation == "init")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(render(report), end="")
        return 0
    except (OSError, ValueError) as exc:
        print("project-pulse: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
