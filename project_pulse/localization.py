"""Presentation language for human reports; canonical state stays language neutral."""

import locale
import os
import plistlib
import sys
from pathlib import Path


LABELS = {
    "en": {
        "snapshot": "Snapshot", "workspace": "Workspace", "tasks": "Tasks",
        "details": "Task details", "evidence": "Evidence", "readiness": "Readiness",
        "focus": "Focus", "priority": "Priority", "item": "Item",
        "focus_note": "[P0]–[P3] sort first (P0 highest); — means unmarked, sorted by state and source order.",
        "focus_empty": "No tasks currently need attention.",
        "more_details": "more in task details",
        "next": "Next action", "state": "State", "count": "Count", "chart": "Chart",
        "build": "Build", "tests": "Tests", "manual": "Manual test",
        "integration": "Integration", "review": "Review", "release": "Release",
        "blocked": "Blocked", "active": "Active",
        "implemented_unverified": "Needs verification", "planned": "Remaining",
        "verified": "Verified", "deferred": "Deferred", "unknown": "Unknown",
        "bar_note": "Each █ = 1 task; chart stops at 20. Counts are exact.",
        "empty": "No task claims or persistent items; task state is UNKNOWN.",
        "stale": "Stored status differs from this workspace; verification claims are historical.",
        "more": "more", "attention": "Attention", "no_project": "no project found",
        "saved": "saved", "skipped": "skipped", "failed": "failed",
        "unavailable": "Status unavailable.",
    },
    "zh": {
        "snapshot": "快照", "workspace": "工作区", "tasks": "任务概览",
        "details": "任务明细", "evidence": "验证证据", "readiness": "就绪状态",
        "focus": "重点事项", "priority": "优先级", "item": "事项",
        "focus_note": "[P0]–[P3] 优先（P0 最高）；— 表示未标注，按状态及原文件顺序排列。",
        "focus_empty": "当前没有需要关注的任务。",
        "more_details": "项见任务明细",
        "next": "下一步", "state": "状态", "count": "数量", "chart": "图表",
        "build": "构建", "tests": "测试", "manual": "手动测试",
        "integration": "集成", "review": "审查", "release": "发布",
        "blocked": "阻塞", "active": "进行中",
        "implemented_unverified": "已实现·待验证", "planned": "待完成",
        "verified": "已验证", "deferred": "已推迟", "unknown": "未知",
        "bar_note": "每个 █ 代表 1 项任务；图表最多显示 20 格，数量保持准确。",
        "empty": "没有任务记录或持久化任务；任务状态未知。",
        "stale": "已保存状态与当前工作区不一致；验证记录仅供历史参考。",
        "more": "项未显示", "attention": "需关注", "no_project": "未找到项目",
        "saved": "已保存", "skipped": "已跳过", "failed": "失败",
        "unavailable": "无法读取状态。",
    },
}

VALUES = {
    "zh": {
        "FRESH": "已同步", "STALE": "已过期", "INVALID": "无效",
        "NOT INITIALIZED": "未初始化", "DIRTY": "有改动", "CLEAN": "无改动",
        "UNKNOWN": "未知", "PRESENT": "有证据", "READY": "就绪",
        "NOT READY": "未就绪", "N/A": "无",
    }
}


def language(preferred=None):
    """Use a meaningful process locale, then macOS preferences or system locale."""
    if preferred is None:
        candidates = (os.environ.get("PROJECT_PULSE_LANG"), os.environ.get("LC_ALL"),
                      os.environ.get("LC_MESSAGES"), os.environ.get("LANG"))
        preferred = next((item for item in candidates if item and item.split(".")[0].upper() not in ("C", "POSIX")), None)
        if preferred is None:
            if sys.platform == "darwin":
                preferences = Path.home() / "Library/Preferences/.GlobalPreferences.plist"
                try:
                    if preferences.is_file() and not preferences.is_symlink() and preferences.stat().st_size <= 65536:
                        settings = plistlib.loads(preferences.read_bytes())
                        languages = settings.get("AppleLanguages", ()) if isinstance(settings, dict) else ()
                        if isinstance(languages, (list, tuple)) and languages and isinstance(languages[0], str):
                            preferred = languages[0]
                except (OSError, ValueError, TypeError, plistlib.InvalidFileException):
                    pass
            if preferred is None:
                try:
                    preferred = locale.getlocale()[0]
                except (ValueError, TypeError):
                    preferred = None
    return "zh" if str(preferred or "").lower().replace("-", "_").startswith("zh") else "en"


def label(key, lang):
    return LABELS[lang][key]


def value(raw, lang):
    return VALUES.get(lang, {}).get(raw, raw)


def next_action(counts, has_items, lang):
    for key in ("blocked", "active", "implemented_unverified", "planned"):
        count = counts[key]
        if count:
            if lang == "zh":
                return {
                    "blocked": "处理 {n} 项阻塞任务。", "active": "继续 {n} 项进行中的任务。",
                    "implemented_unverified": "为 {n} 项已实现任务补充当前验证证据。",
                    "planned": "开始 {n} 项待完成任务。",
                }[key].format(n=count)
            noun = "task" if count == 1 else "tasks"
            return {
                "blocked": "Resolve blocked work ({n} {noun}).",
                "active": "Continue active work ({n} {noun}).",
                "implemented_unverified": "Verify completed work with current evidence ({n} {noun}).",
                "planned": "Start remaining work ({n} {noun}).",
            }[key].format(n=count, noun=noun)
    if not has_items:
        return "识别当前项目任务与验证证据。" if lang == "zh" else "Identify current project tasks and verification evidence."
    return "检查就绪要求并记录下一步任务。" if lang == "zh" else "Check readiness requirements and record the next project tasks."
