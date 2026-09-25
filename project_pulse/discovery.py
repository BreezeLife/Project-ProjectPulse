"""Resolve the current workspace and collect bounded Git metadata."""

from pathlib import Path
import os
import subprocess

from .paths import project_path

GIT_ENV = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
GIT_BASE = ["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", "-c", "submodule.recurse=false"]


def git_read(directory, *args):
    try:
        done = subprocess.run(GIT_BASE + ["-C", str(directory), *args], env=GIT_ENV,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              timeout=3, check=False)
        if done.returncode == 0 and len(done.stdout) <= 256 * 1024:
            return done.stdout.decode("utf-8", "replace").strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def discover(value=None):
    selected = project_path(value)
    git_root_text = git_read(selected, "rev-parse", "--show-toplevel")
    root = Path(git_root_text).resolve() if git_root_text else selected
    if git_root_text and root != selected and root not in selected.parents:
        raise ValueError("Git root is outside selected directory ancestry")
    git = git_root_text is not None
    branch = git_read(root, "symbolic-ref", "--quiet", "--short", "HEAD") if git else None
    head = git_read(root, "rev-parse", "--verify", "HEAD") if git else None
    porcelain = git_read(root, "status", "--porcelain=v1", "--untracked-files=normal") if git else None
    if porcelain is not None:
        lines = [line for line in porcelain.splitlines() if line[3:] not in
                 ("STATUS.md", "project-pulse.json", ".project-pulse/")]
        porcelain = "\n".join(lines)
    return {"root": root, "vcs": "git" if git else "none", "branch": branch or None,
            "head": head or None, "workspace": "DIRTY" if porcelain else "CLEAN" if porcelain is not None else "UNKNOWN"}
