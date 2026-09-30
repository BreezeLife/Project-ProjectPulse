"""Optional task priority markers in human-authored checkbox titles."""

import re


MARKER = re.compile(r"^\s*\[P([0-3])\]\s*", re.IGNORECASE)


def rank(title):
    match = MARKER.match(title)
    return int(match.group(1)) if match else None


def without_marker(title):
    stripped = MARKER.sub("", title, count=1)
    return stripped or title
