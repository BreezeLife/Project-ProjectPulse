"""Explicit, guarded project-local persistence."""

import json
import os
from pathlib import Path
import tempfile

from .paths import safe_child


def _atomic(path, content):
    descriptor, temporary = tempfile.mkstemp(prefix=".pulse-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def persist(root, data, markdown, expected_raw=None, initialize=False):
    directory = safe_child(root, ".project-pulse")
    config = safe_child(root, "project-pulse.json")
    status = safe_child(root, ".project-pulse/status.json")
    dashboard = safe_child(root, "STATUS.md")
    if directory.exists() and (directory.is_symlink() or not directory.is_dir()):
        raise ValueError("unsafe state directory")
    for path in (config, status, dashboard):
        if path.exists() and (path.is_symlink() or not path.is_file()):
            raise ValueError("unsafe output path")
    if initialize and (status.exists() or dashboard.exists()):
        raise ValueError("Project Pulse state already exists")
    if not initialize and not status.exists():
        raise ValueError("project is not initialized; use init")
    directory.mkdir(exist_ok=True)
    lock = directory / "write.lock"
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError("concurrent or interrupted Project Pulse writer detected") from exc
    try:
        os.close(lock_fd)
        current = status.read_text(encoding="utf-8") if status.exists() else None
        if current != expected_raw:
            raise ValueError("status changed concurrently; inspect and retry")
        if initialize and not config.exists():
            _atomic(config, json.dumps({"schema_version": 1, "name": root.name}, indent=2) + "\n")
        _atomic(status, json.dumps(data, indent=2, sort_keys=True) + "\n")
        _atomic(dashboard, markdown)
    finally:
        lock.unlink(missing_ok=True)
