"""Optional project-local configuration."""

import json

from .paths import read_text
from .redact import display


def load_config(root):
    raw = read_text(root, "project-pulse.json", 16 * 1024)
    if raw is None:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return {}
    name = data.get("name")
    return {"name": display(name, 80)} if isinstance(name, str) and name.strip() else {}
