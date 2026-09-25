"""Portable snapshot fingerprint without absolute paths or secret contents."""

import hashlib
import json

from .paths import read_text


def fingerprint(discovery, collection):
    root = discovery["root"]
    tracked = {}
    for name in collection["known_files"]:
        if name in ("STATUS.md",):
            continue
        content = read_text(root, name)
        if content is not None:
            tracked[name] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    source = {"vcs": discovery["vcs"], "branch": discovery["branch"], "head": discovery["head"],
              "workspace": discovery["workspace"], "files": tracked}
    return hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
