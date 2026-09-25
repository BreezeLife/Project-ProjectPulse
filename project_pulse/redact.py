"""Limit untrusted text to printable, single-line display data."""

import re


def display(value, limit=120):
    value = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]
