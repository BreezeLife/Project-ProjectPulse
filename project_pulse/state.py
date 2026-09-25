"""Derived state and verification invariants."""

IMPLEMENTATION = {"unknown", "not_started", "in_progress", "implemented"}
VERIFICATION = {"unknown", "not_run", "partial", "passed", "failed", "not_applicable"}
VERIFY_EVIDENCE = {"build", "test", "human"}


def normalize_item(item, current_fingerprint):
    result = dict(item)
    implementation = result.get("implementation", "unknown")
    verification = result.get("verification", "unknown")
    if implementation not in IMPLEMENTATION:
        implementation = "unknown"
    if verification not in VERIFICATION:
        verification = "unknown"
    evidence = result.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = []
    valid_pass = any(isinstance(record, dict) and record.get("type") in VERIFY_EVIDENCE and
                     record.get("fingerprint") == current_fingerprint for record in evidence)
    if verification == "passed" and not valid_pass:
        verification = "not_run"
    result["implementation"] = implementation
    result["verification"] = verification
    result["evidence"] = evidence[:20]
    result["derived"] = derive(result)
    return result


def derive(item):
    if item.get("blocked") is True:
        return "blocked"
    if item.get("deferred") is True:
        return "deferred"
    implementation = item["implementation"]
    verification = item["verification"]
    if implementation == "implemented" and verification == "passed":
        return "verified"
    if implementation == "implemented":
        return "implemented_unverified"
    if implementation == "in_progress":
        return "active"
    if implementation == "not_started":
        return "planned"
    return "unknown"


def readiness(items):
    # v0.1 has no universal release or review policy.
    manual = "UNKNOWN"
    if items and all(item["derived"] == "verified" for item in items):
        manual = "READY"
    elif any(item["derived"] == "blocked" for item in items):
        manual = "NOT READY"
    return {"manual_test": manual, "integration": "UNKNOWN", "review": "UNKNOWN", "release": "UNKNOWN"}
