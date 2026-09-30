"""Codex Stop Hook adapter: save progress, then show current Project Pulse status."""

import json
import sys

from .cli import inspect, save_report
from .localization import label, language
from .renderer import render


def main():
    lang = "en"
    try:
        lang = language()
        raw = sys.stdin.read(128 * 1024)
        event = json.loads(raw) if raw else {}
        if not isinstance(event, dict) or event.get("hook_event_name") != "Stop" or not isinstance(event.get("cwd"), str):
            raise ValueError("invalid Stop event")
        cwd = event["cwd"]
        root, report, status_raw = inspect(cwd)
        if report["vcs"] == "none" and not report["known_files"] and status_raw is None:
            prefix = "保存：已跳过（未找到项目）" if lang == "zh" else "SAVE: SKIPPED (no project found)"
            message = prefix + "\n" + render(report, compact=True, language=lang)
        else:
            save_report(root, report, status_raw, create_config=False)
            _, saved_report, _ = inspect(root)
            if saved_report["status"] != "FRESH":
                raise ValueError("saved status could not be verified")
            prefix = "保存：已保存" if lang == "zh" else "SAVE: SAVED"
            message = prefix + "\n" + render(saved_report, compact=True, language=lang)
    except Exception as exc:  # A status hook must never block the user's turn.
        prefix = "保存：失败" if lang == "zh" else "SAVE: FAILED"
        message = prefix + " (" + str(exc) + ")\nPROJECT PULSE\n" + label("unavailable", lang)
    output = {"continue": True, "systemMessage": message[:12000], "suppressOutput": False}
    sys.stdout.write(json.dumps(output, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
