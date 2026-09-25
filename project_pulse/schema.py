"""Validate bounded portable status input."""

import json

from .paths import read_text
from .redact import display


def load_status(root):
    raw = read_text(root, ".project-pulse/status.json", 512 * 1024)
    if raw is None:
        return None, None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None, raw
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("items"), list):
        return None, raw
    items = []
    for item in data["items"][:200]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        clean = {"id": display(item["id"], 80), "title": display(item.get("title", ""), 160),
                 "implementation": item.get("implementation"), "verification": item.get("verification"),
                 "blocked": item.get("blocked") is True, "deferred": item.get("deferred") is True,
                 "evidence": item.get("evidence", [])}
        if clean["id"] and clean["title"]:
            items.append(clean)
    data["items"] = items
    return data, raw
