"""Bounded collection of metadata and task claims."""

import hashlib
import re

from .paths import read_text, root_entries
from .redact import display

COMMON = {"AGENTS.md", "PROJECT.md", "TASKS.md", "STATUS.md", "ROADMAP.md", "TODO.md", "WORKLOG.md", "MEMORY.md", "README.md", "CONTRIBUTING.md", "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Makefile"}
TASK_FILES = ("TASKS.md", "TODO.md", "ROADMAP.md")
CHECKBOX = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+)$")


def collect(root):
    entries = root_entries(root)
    known = [name for name in entries if name in COMMON or name.endswith((".sln", ".csproj"))]
    items = []
    for name in TASK_FILES:
        raw = read_text(root, name, 64 * 1024)
        if raw is None:
            continue
        for line_number, line in enumerate(raw.splitlines()[:1000], 1):
            match = CHECKBOX.match(line[:500])
            if not match or len(items) >= 200:
                continue
            title = display(match.group(2), 160)
            if not title:
                continue
            identity = hashlib.sha256((name + ":" + title.casefold()).encode()).hexdigest()[:16]
            items.append({"id": identity, "title": title, "implementation": "implemented" if match.group(1).strip() else "not_started",
                          "verification": "not_run", "evidence": [{"type": "task", "source": name, "line": line_number}],
                          "blocked": False, "deferred": False})
    return {"known_files": known[:100], "items": items, "entry_limit_reached": len(entries) >= 512}
