"""Codex Stop Hook adapter: read-only Project Pulse inspection."""

import json
import sys

from .cli import inspect
from .renderer import render


def main():
    try:
        raw = sys.stdin.read(128 * 1024)
        event = json.loads(raw) if raw else {}
        if not isinstance(event, dict) or event.get("hook_event_name") != "Stop" or not isinstance(event.get("cwd"), str):
            raise ValueError("invalid Stop event")
        cwd = event["cwd"]
        _, report, _ = inspect(cwd)
        message = render(report)
    except Exception as exc:  # A status hook must never block the user's turn.
        message = "PROJECT PULSE\n\nHook inspection unavailable: " + str(exc)
    output = {"continue": True, "systemMessage": message[:12000], "suppressOutput": False}
    sys.stdout.write(json.dumps(output, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
