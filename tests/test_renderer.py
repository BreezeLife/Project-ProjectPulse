import tempfile
import unittest
from pathlib import Path

from project_pulse.cli import inspect
from project_pulse.renderer import _width, render, render_markdown


class RendererTests(unittest.TestCase):
    def test_detailed_report_separates_snapshot_tasks_and_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Login\n- [x] Search\n- [ ] Payments\n", encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, language="en")

        self.assertIn("Snapshot:", output)
        self.assertIn("TASK DETAILS (3)", output)
        self.assertIn("Needs verification (2)", output)
        self.assertIn("Remaining (1)", output)
        self.assertIn("NEXT ACTION", output)
        self.assertIn("Verify completed work", output)
        self.assertNotIn("1. Login", output)

    def test_detailed_report_shows_counted_task_bars(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Login\n- [x] Search\n- [ ] Payments\n", encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, language="en")

        self.assertIn("TASKS (3)", output)
        self.assertIn("◐ Needs verification", output)
        self.assertIn("2  ██", output)
        self.assertIn("○ Remaining", output)
        self.assertIn("1  █", output)
        self.assertLess(output.index("◐ Needs verification"), output.index("! Blocked"))

    def test_hook_summary_is_bounded_and_prioritizes_attention(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = "\n".join("- [x] Finished task " + str(number) for number in range(6))
            (root / "TASKS.md").write_text(tasks + "\n", encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, compact=True, language="en")

        self.assertIn("NOT INITIALIZED ·", output)
        self.assertIn("!0 blocked  ▶0 active  ◐6 unverified", output)
        self.assertIn("FOCUS", output)
        self.assertIn("4 more", output)
        self.assertIn("EVIDENCE  Build UNKNOWN · Tests UNKNOWN · Manual test UNKNOWN", output)
        self.assertIn("READINESS  Manual test UNKNOWN · Integration UNKNOWN · Review UNKNOWN · Release UNKNOWN", output)
        self.assertIn("NEXT ACTION  Verify completed work", output)
        self.assertNotIn("Finished task 5", output)

    def test_next_action_uses_singular_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Login\n", encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, compact=True, language="en")

        self.assertIn("NEXT ACTION  Verify completed work with current evidence (1 task).", output)

    def test_chinese_dashboard_aligns_bars_and_keeps_task_titles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Login\n- [x] Search\n- [ ] Payments\n", encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, language="zh")
            markdown = render_markdown(report, language="zh")

        chart = output.split("任务概览 (3)\n", 1)[1].splitlines()[:7]
        bars = [line for line in chart if "█" in line]
        self.assertEqual(len({_width(line[:line.index("█")]) for line in bars}), 1)
        self.assertLess(output.index("◐ 已实现·待验证"), output.index("! 阻塞"))
        self.assertIn("验证证据", output)
        self.assertIn("下一步", output)
        self.assertIn("- Login", output)
        self.assertIn("| ◐ 已实现·待验证 | 2 | ██ |", markdown)
        self.assertIn("| 验证证据 | 状态 | 就绪状态 | 状态 |", markdown)

    def test_explicit_priority_ranks_focus_without_changing_task_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text(
                "- [x] Ordinary work\n- [x] [P2] Polish docs\n"
                "- [ ] [P0] Fix checkout | [link](https://example.com)\n",
                encoding="utf-8")
            _, report, _ = inspect(root)
            full = render(report, language="en")
            compact = render(report, compact=True, language="en")
            markdown = render_markdown(report, language="en")

        focus = full.split("FOCUS (3)\n", 1)[1].split("TASK DETAILS", 1)[0]
        self.assertLess(focus.index("P0"), focus.index("P2"))
        self.assertLess(focus.index("P2"), focus.index("Ordinary work"))
        self.assertIn("- P0 · ○ Fix checkout", compact)
        self.assertIn("| P0 | ○ Remaining | Fix checkout \\| \\[link\\]", markdown)
        self.assertEqual(next(item for item in report["items"] if "P0" in item["title"])["derived"], "planned")

    def test_focus_is_short_but_full_details_include_later_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text(
                "\n".join("- [x] Task " + str(index) for index in range(25)) + "\n",
                encoding="utf-8")
            _, report, _ = inspect(root)
            output = render(report, language="en")
            markdown = render_markdown(report, language="en")

        self.assertIn("FOCUS (25)", output)
        self.assertIn("+ 20 more in task details", output)
        self.assertIn("- Task 24", output)
        self.assertIn("- Task 24", markdown)


if __name__ == "__main__":
    unittest.main()
