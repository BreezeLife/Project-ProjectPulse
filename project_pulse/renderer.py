"""Compact human-readable status rendering."""

from .redact import display

GROUPS = (("verified", "Verified"), ("implemented_unverified", "Implemented / Unverified"),
          ("active", "Active"), ("blocked", "Blocked"), ("planned", "Remaining"),
          ("deferred", "Deferred"), ("unknown", "Unknown"))


def render(report):
    lines = ["PROJECT PULSE", "", "Project: " + display(report["project"], 80),
             "VCS: " + report["vcs"].upper(), "Branch: " + display(report.get("branch") or "N/A", 80),
             "HEAD: " + display((report.get("head") or "N/A")[:12]),
             "Workspace: " + report["workspace"], "Status: " + report["status"], "", "WORK"]
    items = report["items"]
    for key, label in GROUPS:
        matches = [item for item in items if item["derived"] == key]
        if matches:
            lines.extend(["", label.upper()])
            lines.extend("- " + display(item["title"], 160) for item in matches[:20])
    if not items:
        lines.extend(["", "Task state: UNKNOWN (no task claims or persistent items)"])
    lines.extend(["", "CHECKS", "Build: UNKNOWN", "Tests: UNKNOWN", "Manual test: UNKNOWN", "", "READINESS"])
    for key, label in (("manual_test", "Manual test"), ("integration", "Integration"), ("review", "Review"), ("release", "Release")):
        lines.append(label + ": " + report["readiness"][key])
    lines.extend(["", "NEXT"])
    next_items = [item for item in items if item["derived"] in ("blocked", "implemented_unverified", "active", "planned")][:3]
    if next_items:
        lines.extend(str(number) + ". " + display(item["title"], 160) for number, item in enumerate(next_items, 1))
    else:
        lines.append("1. Gather current verification evidence" if items else "1. Identify current project tasks and verification evidence")
    if report["status"] == "STALE":
        lines.extend(["", "Stored status differs from this workspace; verification claims are historical."])
    return "\n".join(lines) + "\n"
