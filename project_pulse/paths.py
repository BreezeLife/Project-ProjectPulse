"""Safe project path selection and bounded file reads."""

from pathlib import Path
import os
import stat

MAX_FILE_BYTES = 128 * 1024
MAX_ENTRIES = 512
SECRET_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "credentials.json", "secrets.json", ".npmrc", ".pypirc"}


def project_path(value=None):
    path = Path(value or os.getcwd()).expanduser()
    if not path.is_dir():
        raise ValueError("project path is not a directory")
    if path.is_symlink():
        raise ValueError("project path must not be a symlink")
    return path.resolve()


def safe_child(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("invalid relative path")
    parts = Path(relative).parts
    if any(part in (".", "..", "") for part in parts):
        raise ValueError("path traversal rejected")
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink rejected")
    if current.resolve() != root.resolve() and root.resolve() not in current.resolve().parents:
        raise ValueError("path escapes project")
    return current


def read_text(root, name, limit=MAX_FILE_BYTES):
    if name in SECRET_NAMES or name.startswith(".env"):
        return None
    path = safe_child(root, name)
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            return None
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            return None
        return raw.decode("utf-8", errors="replace")
    except (OSError, ValueError):
        return None


def root_entries(root):
    result = []
    with os.scandir(root) as iterator:
        for index, entry in enumerate(iterator):
            if index >= MAX_ENTRIES:
                break
            if entry.is_file(follow_symlinks=False) and entry.name not in SECRET_NAMES and not entry.name.startswith(".env"):
                result.append(entry.name)
    return sorted(result)
