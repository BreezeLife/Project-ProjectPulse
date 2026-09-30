"""Generate the two localized, dependency-free README infographics."""

from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parent

COPY = {
    "en": {
        "file": "project-pulse-guide.en.svg",
        "lang": "en",
        "badge": "ENGLISH GUIDE",
        "eyebrow": "PROJECT PULSE  /  QUICK GUIDE",
        "title": "Your project, at a glance",
        "subtitle": "Install once  ·  ask for status  ·  follow the evidence",
        "flow": "01  GET STARTED",
        "steps": [
            ("01", "Install once", "From this repository root", "python3 -m pip install --user .", "Copy the Skill to ~/.codex/skills/"),
            ("02", "Open any project", "Git repository or plain folder", "cd /path/to/project", "No per-project installation"),
            ("03", "Ask Codex", "In the desktop app or CLI", None, None),
        ],
        "commands": [("project pulse", "inspect"), ("project pulse init", "first save"), ("project pulse update", "refresh")],
        "signals": "02  UNDERSTAND THE DASHBOARD",
        "features": [
            ("Snapshot", "FRESH / STALE", ["See when a saved status no longer", "matches the workspace."], "01"),
            ("Tasks + focus", "P0 → P3", ["Exact counts, short bars, and", "ranked next tasks."], "02"),
            ("Evidence", "PRESENT / UNKNOWN", ["Build, test, and manual proof;", "missing proof stays unknown."], "03"),
            ("Readiness", "4 checks", ["Manual, integration, review,", "and release readiness."], "04"),
        ],
        "footer_label": "OPTIONAL AUTO SAVE",
        "footer_top": "Trust the Stop Hook in Settings → Hooks.",
        "footer_bottom": "Each turn updates only .project-pulse/status.json and STATUS.md.",
        "note": "Inspect is read-only. Init and update save only when requested.",
        "description": "A three-step guide to install Project Pulse once, use it from any project in Codex, read four dashboard signals, and optionally enable the Stop Hook.",
    },
    "zh-CN": {
        "file": "project-pulse-guide.zh-CN.svg",
        "lang": "zh-CN",
        "badge": "简体中文指南",
        "eyebrow": "PROJECT PULSE  /  快速指南",
        "title": "一眼看清项目进度",
        "subtitle": "全局安装一次  ·  随时查看状态  ·  根据证据推进",
        "flow": "01  开始使用",
        "steps": [
            ("01", "一次安装", "在本仓库根目录执行", "python3 -m pip install --user .", "再将 Skill 复制到 ~/.codex/skills/"),
            ("02", "打开任意项目", "Git 仓库或普通目录均可", "cd /path/to/project", "目标项目无需重复安装"),
            ("03", "在 Codex 中调用", "桌面版或 CLI 输入", None, None),
        ],
        "commands": [("project pulse", "查看"), ("project pulse init", "首次保存"), ("project pulse update", "刷新")],
        "signals": "02  看懂仪表板",
        "features": [
            ("快照", "FRESH / STALE", ["工作区发生变化后，", "识别旧状态。"], "01"),
            ("任务与重点", "P0 → P3", ["准确数量、短条形图，", "以及按优先级排列的待办。"], "02"),
            ("验证证据", "PRESENT / UNKNOWN", ["构建、测试、人工证据；", "缺失时保持未知。"], "03"),
            ("就绪度", "4 项检查", ["人工测试、集成、审查", "和发布就绪度。"], "04"),
        ],
        "footer_label": "可选自动保存",
        "footer_top": "在 Codex 的「设置 → Hooks」中信任 Stop Hook。",
        "footer_bottom": "每回合仅更新 .project-pulse/status.json 与 STATUS.md。",
        "note": "Inspect 只读；init 和 update 仅在明确请求时保存。",
        "description": "Project Pulse 三步使用指南：一次安装、在任意项目的 Codex 中调用、查看四类仪表板信号，并可选启用 Stop Hook。",
    },
}


def generate(data):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1020" viewBox="0 0 1280 1020" '
        f'role="img" aria-labelledby="title description" xml:lang="{data["lang"]}">',
        f'<title id="title">Project Pulse — {escape(data["title"])}</title>',
        f'<desc id="description">{escape(data["description"])}</desc>',
        '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101B30"/>'
        '<stop offset="1" stop-color="#07101D"/></linearGradient>'
        '<linearGradient id="accent"><stop stop-color="#51E3D4"/>'
        '<stop offset="1" stop-color="#68B7FF"/></linearGradient></defs>',
        '<rect width="1280" height="1020" fill="url(#bg)"/>',
        '<circle cx="1150" cy="90" r="260" fill="#17334B" opacity=".3"/>',
        '<circle cx="74" cy="950" r="230" fill="#17334B" opacity=".16"/>',
    ]

    def rect(x, y, w, h, fill, radius=0, stroke=None, stroke_width=1):
        border = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{border}/>')

    def text(x, y, value, size=22, color="#E8F2F7", weight=400, family="sans", extra=""):
        font = ("'SFMono-Regular',Consolas,'Liberation Mono',monospace" if family == "mono" else
                "Inter,'SF Pro Display','PingFang SC','Noto Sans CJK SC',Arial,sans-serif")
        parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
                     f'font-family="{font}" {extra}>{escape(value)}</text>')

    # Brand / masthead.
    rect(40, 42, 10, 23, "#51E3D4", 5)
    rect(58, 49, 10, 16, "#68B7FF", 5)
    rect(76, 35, 10, 30, "#F5C777", 5)
    text(105, 58, data["eyebrow"], 18, "#9CB8CA", 700, extra='letter-spacing="2"')
    rect(1052, 34, 188, 40, "#17334B", 20, "#315C6D")
    text(1146, 61, data["badge"], 16, "#BEE9E8", 700, extra='text-anchor="middle"')
    text(40, 133, data["title"], 50, "#F5F8F9", 760)
    text(42, 172, data["subtitle"], 23, "#AFC6D0", 400)
    rect(40, 197, 1200, 2, "#294156")

    # Three large cards keep the install → open → invoke sequence obvious.
    text(40, 235, data["flow"], 19, "#51E3D4", 750, extra='letter-spacing="1.5"')
    x_positions = [40, 447, 854]
    for (number, title, description, command, hint), x in zip(data["steps"], x_positions):
        rect(x, 256, 386, 282, "#142438", 18, "#315064")
        rect(x + 24, 280, 54, 38, "#264B57", 19)
        text(x + 51, 306, number, 20, "#64E4D7", 750, family="mono", extra='text-anchor="middle"')
        text(x + 24, 361, title, 29, "#F3F7F8", 720)
        text(x + 24, 395, description, 21, "#B5CBD4")
        if command:
            rect(x + 24, 418, 338, 53, "#0B1728", 10)
            text(x + 39, 452, command, 18, "#9BEEE2", 500, family="mono")
            text(x + 24, 508, hint, 19, "#A7BFCB")
        else:
            for row, (value, meaning) in enumerate(data["commands"]):
                y = 411 + row * 39
                rect(x + 24, y, 338, 34, "#0B1728", 8)
                text(x + 35, y + 24, value, 18, "#9BEEE2", 500, family="mono")
                text(x + 349, y + 23, meaning, 16, "#A7BFCB", 600, extra='text-anchor="end"')
    for x in [428, 835]:
        rect(x, 371, 18, 32, "#1E4253", 9)
        text(x + 9, 394, "›", 27, "#5DE3D7", 700, extra='text-anchor="middle"')

    # Four evenly spaced signals: factual state, tasks, proof, and readiness.
    text(40, 579, data["signals"], 19, "#51E3D4", 750, extra='letter-spacing="1.5"')
    for x, (title, hero, lines, number) in zip([40, 345, 650, 955], data["features"]):
        rect(x, 600, 285, 226, "#142438", 18, "#315064")
        text(x + 22, 636, number, 16, "#5AA8BB", 700, family="mono")
        text(x + 22, 679, title, 25, "#F3F7F8", 700)
        text(x + 22, 718, hero, 20, "#74E6D8", 720, family="mono" if number != "04" else "sans")
        text(x + 22, 765, lines[0], 17, "#B5CBD4")
        text(x + 22, 791, lines[1], 17, "#B5CBD4")

    # Stop Hook is clearly optional and its write scope is explicit.
    rect(40, 850, 1200, 118, "#1A3947", 17, "#347B82")
    rect(40, 850, 8, 118, "url(#accent)", 4)
    text(66, 882, data["footer_label"], 16, "#6AEBDE", 750, extra='letter-spacing="1.4"')
    text(66, 918, data["footer_top"], 25, "#F4F8F9", 680)
    text(66, 949, data["footer_bottom"], 19, "#B7D0D5")
    text(40, 996, data["note"], 17, "#91AEBB")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    for locale, data in COPY.items():
        target = OUT / data["file"]
        target.write_text(generate(data), encoding="utf-8")
        print(f"{locale}: {target}")
