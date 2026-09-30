"""Human-readable detailed and Stop Hook status reports."""

import html
import itertools
import re
import unicodedata

from .localization import label, language as report_language, next_action, value
from .priority import rank as priority_rank, without_marker
from .redact import display

GROUPS = ("blocked", "active", "implemented_unverified", "planned",
          "verified", "deferred", "unknown")
ATTENTION = ("blocked", "active", "implemented_unverified", "planned", "unknown")
ICONS = {"verified": "✓", "implemented_unverified": "◐", "active": "▶",
         "blocked": "!", "planned": "○", "deferred": "↷", "unknown": "?"}
SHORT_LABELS = {
    "en": {"verified": "verified", "implemented_unverified": "unverified", "active": "active",
           "blocked": "blocked", "planned": "remaining", "deferred": "deferred", "unknown": "unknown"},
    "zh": {"verified": "已验证", "implemented_unverified": "待验证", "active": "进行中",
           "blocked": "阻塞", "planned": "待完成", "deferred": "已推迟", "unknown": "未知"},
}
BAR_LIMIT = 20
FOCUS_LIMIT = 5


def _counts(items):
    return {key: sum(item["derived"] == key for item in items) for key in GROUPS}


def _ordered_keys(counts):
    """Show states with work first, while keeping the fixed priority within each set."""
    return sorted(GROUPS, key=lambda key: counts[key] == 0)


def _priority(item):
    return priority_rank(item["title"])


def _priority_sort(item):
    rank = _priority(item)
    return (rank is None, rank if rank is not None else 4)


def _focus(items):
    """Rank explicit priorities, then attention states and original source order."""
    candidates = [(index, item) for index, item in enumerate(items)
                  if item["derived"] in ATTENTION]
    return [item for _, item in sorted(candidates, key=lambda pair:
            _priority_sort(pair[1]) + (ATTENTION.index(pair[1]["derived"]), pair[0]))]


def _focus_title(item):
    return without_marker(item["title"])


def _priority_label(item):
    rank = _priority(item)
    return "P" + str(rank) if rank is not None else "—"


def _bar(count):
    if count == 0:
        return "—"
    bar = "█" * min(count, BAR_LIMIT)
    return bar + ("…" if count > BAR_LIMIT else "")


def _width(text):
    return sum(2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in text)


def _pad(text, width):
    return text + " " * max(0, width - _width(text))


def _markdown(value, limit=160):
    """Keep untrusted names and task titles inert in generated Markdown."""
    value = html.escape(display(value, limit), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|])", r"\\\1", value)


def _evidence_lines(checks, readiness, lang):
    evidence = (("build", "build"), ("tests", "tests"), ("manual_test", "manual"))
    gates = (("manual_test", "manual"), ("integration", "integration"),
             ("review", "review"), ("release", "release"))
    lines = [_pad(label("evidence", lang).upper(), 31) + label("readiness", lang).upper()]
    for check, gate in itertools.zip_longest(evidence, gates):
        left = _pad(label(check[1], lang), 13) + value(checks[check[0]], lang) if check else ""
        right = _pad(label(gate[1], lang), 13) + value(readiness[gate[0]], lang) if gate else ""
        lines.append(_pad(left, 31) + right)
    return lines


def render(report, compact=False, language=None):
    """Render a full report, or a bounded summary for the Stop Hook."""
    lang = report_language(language)
    items = report["items"]
    counts = _counts(items)
    project = display(report["project"], 80)
    snapshot = report["status"]
    checks = report["checks"]
    readiness = report["readiness"]
    action = next_action(counts, bool(items), lang)
    focus = _focus(items)
    status_line = value(snapshot, lang) + " · " + value(report["workspace"], lang)

    if compact:
        lines = ["PROJECT PULSE · " + project,
                 status_line + " · " + label("tasks", lang) + " " + str(len(items))]
        for keys in (GROUPS[:4], GROUPS[4:]):
            lines.append("  ".join(ICONS[key] + str(counts[key]) + " " +
                                   SHORT_LABELS[lang][key] for key in keys))
        if focus:
            lines.append(label("focus", lang).upper())
            for item in focus[:2]:
                rank = _priority_label(item)
                prefix = (rank + " · ") if rank != "—" else ""
                lines.append("- " + prefix + ICONS[item["derived"]] + " " + display(_focus_title(item), 100))
            if len(focus) > 2:
                lines.append("  + " + str(len(focus) - 2) + " " + label("more", lang))
        elif not items:
            lines.append(label("empty", lang))
        lines.extend([
            label("evidence", lang).upper() + "  " + " · ".join(
                label(name, lang) + " " + value(checks[key], lang)
                for key, name in (("build", "build"), ("tests", "tests"), ("manual_test", "manual"))),
            label("readiness", lang).upper() + "  " + " · ".join(
                label(name, lang) + " " + value(readiness[key], lang)
                for key, name in (("manual_test", "manual"), ("integration", "integration"),
                                  ("review", "review"), ("release", "release"))),
            label("next", lang).upper() + "  " + action,
        ])
    else:
        vcs_line = report["vcs"].upper() + " " + display(report.get("branch") or "N/A", 80)
        if report.get("head"):
            vcs_line += " @ " + display(report["head"][:12])
        lines = ["PROJECT PULSE · " + project,
                 label("snapshot", lang) + ": " + status_line + " · " + vcs_line,
                 "", label("tasks", lang).upper() + " (" + str(len(items)) + ")"]
        for key in _ordered_keys(counts):
            lines.append(ICONS[key] + " " + _pad(label(key, lang), 20) + " " +
                         str(counts[key]).rjust(3) + "  " + _bar(counts[key]))
        lines.extend([label("bar_note", lang), "",
                      label("focus", lang).upper() + " (" + str(len(focus)) + ")"])
        if focus:
            for item in focus[:FOCUS_LIMIT]:
                lines.append(_pad(_priority_label(item), 3) + " " + ICONS[item["derived"]] + " " +
                             _pad(label(item["derived"], lang), 20) + " " +
                             display(_focus_title(item), 100))
            if len(focus) > FOCUS_LIMIT:
                lines.append("  + " + str(len(focus) - FOCUS_LIMIT) + " " + label("more_details", lang))
            lines.append(label("focus_note", lang))
        else:
            lines.append(label("focus_empty", lang))
        lines.extend(["",
                      label("details", lang).upper() + " (" + str(len(items)) + ")"])
        for key in GROUPS:
            matches = [item for item in items if item["derived"] == key]
            if matches:
                matches.sort(key=_priority_sort)
                lines.extend(["", ICONS[key] + " " + label(key, lang) + " (" + str(len(matches)) + ")"])
                lines.extend("- " + display(item["title"], 160) for item in matches)
        if not items:
            lines.extend(["", label("empty", lang)])
        lines.extend(["", *_evidence_lines(checks, readiness, lang), "",
                      label("next", lang).upper() + "  " + action])
    if snapshot == "STALE":
        lines.append(label("stale", lang))
    return "\n".join(lines) + "\n"


def render_markdown(report, language=None):
    """Render the explicit Init/Update handoff file as a readable dashboard."""
    lang = report_language(language)
    items = report["items"]
    counts = _counts(items)
    checks = report["checks"]
    readiness = report["readiness"]
    status = report["status"]
    focus = _focus(items)
    marker = "✓" if status == "FRESH" else "!" if status in ("STALE", "INVALID") else "○"
    lines = ["# Project Pulse · " + _markdown(report["project"], 80), "",
             "> " + marker + " **" + value(status, lang) + "** · **" +
             value(report["workspace"], lang) + "** · " + report["vcs"].upper() +
             " " + _markdown(report.get("branch") or "N/A", 80) + " @ " +
             _markdown((report.get("head") or "N/A")[:12]), "",
             "## " + label("tasks", lang) + " · " + str(len(items)), "",
             "| " + label("state", lang) + " | " + label("count", lang) + " | " + label("chart", lang) + " |",
             "| --- | ---: | --- |"]
    for key in _ordered_keys(counts):
        lines.append("| " + ICONS[key] + " " + label(key, lang) + " | " +
                     str(counts[key]) + " | " + _bar(counts[key]) + " |")
    lines.extend(["", label("bar_note", lang), "",
                  "## " + label("focus", lang) + " · " + str(len(focus)), "",
                  "| " + label("priority", lang) + " | " + label("state", lang) + " | " +
                  label("item", lang) + " |", "| --- | --- | --- |"])
    for item in focus[:FOCUS_LIMIT]:
        lines.append("| " + _priority_label(item) + " | " + ICONS[item["derived"]] + " " +
                     label(item["derived"], lang) + " | " + _markdown(_focus_title(item), 100) + " |")
    if not focus:
        lines.append("| — | — | " + label("focus_empty", lang) + " |")
    if len(focus) > FOCUS_LIMIT:
        lines.extend(["", "+ " + str(len(focus) - FOCUS_LIMIT) + " " + label("more_details", lang)])
    if focus:
        lines.extend(["", label("focus_note", lang)])
    lines.extend(["", "## " + label("details", lang)])
    if not items:
        lines.extend(["", label("empty", lang)])
    for key in GROUPS:
        matches = [item for item in items if item["derived"] == key]
        if matches:
            matches.sort(key=_priority_sort)
            lines.extend(["", "### " + ICONS[key] + " " + label(key, lang) + " (" + str(len(matches)) + ")"])
            lines.extend("- " + _markdown(item["title"]) for item in matches)
    lines.extend(["", "## " + label("evidence", lang) + " / " + label("readiness", lang), "",
                  "| " + label("evidence", lang) + " | " + label("state", lang) + " | " +
                  label("readiness", lang) + " | " + label("state", lang) + " |",
                  "| --- | --- | --- | --- |"])
    evidence = (("build", "build"), ("tests", "tests"), ("manual_test", "manual"))
    gates = (("manual_test", "manual"), ("integration", "integration"),
             ("review", "review"), ("release", "release"))
    for check, gate in itertools.zip_longest(evidence, gates):
        left = label(check[1], lang) + " | " + value(checks[check[0]], lang) if check else " | "
        right = label(gate[1], lang) + " | " + value(readiness[gate[0]], lang)
        lines.append("| " + left + " | " + right + " |")
    lines.extend(["", "## " + label("next", lang), "",
                  "> " + next_action(counts, bool(items), lang)])
    if status == "STALE":
        lines.extend(["", "⚠ " + label("stale", lang)])
    return "\n".join(lines) + "\n"
