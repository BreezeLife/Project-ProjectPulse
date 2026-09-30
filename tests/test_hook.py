import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class HookTests(unittest.TestCase):
    def setUp(self):
        locale_patch = patch.dict(os.environ, {"PROJECT_PULSE_LANG": "en"})
        locale_patch.start()
        self.addCleanup(locale_patch.stop)

    def test_stop_hook_returns_non_blocking_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("prototype", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            output = json.loads(process.stdout)
            self.assertTrue(output["continue"])
            self.assertTrue(output["systemMessage"].startswith("SAVE: SAVED\nPROJECT PULSE"))
            self.assertIn("PROJECT PULSE", output["systemMessage"])
            self.assertIn("FRESH ·", output["systemMessage"])
            self.assertIn("Tasks", output["systemMessage"])
            self.assertIn("◐", output["systemMessage"])
            self.assertNotIn("VISUAL:", output["systemMessage"])
            self.assertNotIn("TASK STATUS", output["systemMessage"])
            self.assertTrue((root / "STATUS.md").exists())
            self.assertTrue((root / ".project-pulse/status.json").exists())
            self.assertFalse((root / "project-pulse.json").exists())

    def test_stop_hook_refreshes_saved_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "TASKS.md"
            tasks.write_text("- [x] First\n", encoding="utf-8")
            event = json.dumps({"cwd": str(root), "hook_event_name": "Stop"})
            command = [sys.executable, "-m", "project_pulse.hook"]
            subprocess.run(command, input=event, text=True, capture_output=True, check=True)
            first_state = json.loads((root / ".project-pulse/status.json").read_text(encoding="utf-8"))
            tasks.write_text("- [x] First\n- [ ] Second\n", encoding="utf-8")
            second = subprocess.run(command, input=event, text=True, capture_output=True, check=True)
            second_state = json.loads((root / ".project-pulse/status.json").read_text(encoding="utf-8"))

            self.assertNotEqual(first_state["fingerprint"], second_state["fingerprint"])
            self.assertEqual(len(second_state["items"]), 2)
            self.assertIn("FRESH ·", json.loads(second.stdout)["systemMessage"])
            self.assertIn("| ○ Remaining | 1 | █ |", (root / "STATUS.md").read_text(encoding="utf-8"))

    def test_repeated_stop_does_not_duplicate_task_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Same task\n", encoding="utf-8")
            event = json.dumps({"cwd": str(root), "hook_event_name": "Stop"})
            command = [sys.executable, "-m", "project_pulse.hook"]
            for _ in range(3):
                subprocess.run(command, input=event, text=True, capture_output=True, check=True)
            state = json.loads((root / ".project-pulse/status.json").read_text(encoding="utf-8"))

            self.assertEqual(len(state["items"][0]["evidence"]), 1)

    def test_stop_hook_stays_fresh_when_status_files_are_tracked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "TASKS.md"
            tasks.write_text("- [x] First\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run([sys.executable, "-m", "project_pulse.cli", "init", "--project", str(root)],
                           text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com",
                            "-c", "user.name=Test", "commit", "-qm", "initial"], check=True)
            tasks.write_text("- [x] First\n- [ ] Second\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "TASKS.md"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com",
                            "-c", "user.name=Test", "commit", "-qm", "tasks"], check=True)
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True, capture_output=True, check=True)

            self.assertIn("SAVE: SAVED", json.loads(process.stdout)["systemMessage"])
            self.assertIn("FRESH ·", json.loads(process.stdout)["systemMessage"])

    def test_stop_hook_refuses_unowned_dashboard_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] Feature\n", encoding="utf-8")
            dashboard = root / "STATUS.md"
            dashboard.write_text("Personal status notes", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True, capture_output=True, check=True)
            output = json.loads(process.stdout)

            self.assertTrue(output["continue"])
            self.assertIn("SAVE: FAILED", output["systemMessage"])
            self.assertNotIn("FRESH ·", output["systemMessage"])
            self.assertEqual(dashboard.read_text(encoding="utf-8"), "Personal status notes")
            self.assertFalse((root / ".project-pulse/status.json").exists())

    def test_stop_hook_skips_directory_without_project_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True, capture_output=True, check=True)

            self.assertIn("SAVE: SKIPPED", json.loads(process.stdout)["systemMessage"])
            self.assertEqual(list(root.iterdir()), [])

    def test_stop_hook_reports_locked_save_without_claiming_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [ ] Feature\n", encoding="utf-8")
            state_dir = root / ".project-pulse"
            state_dir.mkdir()
            (state_dir / "write.lock").write_text("held", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True, capture_output=True, check=True)

            self.assertIn("SAVE: FAILED", json.loads(process.stdout)["systemMessage"])
            self.assertFalse((state_dir / "status.json").exists())
            self.assertFalse((root / "STATUS.md").exists())

    def test_stop_hook_uses_chinese_environment_for_human_output_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text("- [x] [P0] Login\n", encoding="utf-8")
            env = dict(os.environ, PROJECT_PULSE_LANG="zh_CN.UTF-8")
            process = subprocess.run(
                [sys.executable, "-m", "project_pulse.hook"],
                input=json.dumps({"cwd": str(root), "hook_event_name": "Stop"}),
                text=True, capture_output=True, check=True, env=env)
            message = json.loads(process.stdout)["systemMessage"]
            dashboard = (root / "STATUS.md").read_text(encoding="utf-8")
            state = json.loads((root / ".project-pulse/status.json").read_text(encoding="utf-8"))

        self.assertIn("保存：已保存", message)
        self.assertIn("任务概览", message)
        self.assertIn("P0 · ◐ Login", message)
        self.assertIn("## 任务概览", dashboard)
        self.assertIn("| P0 | ◐ 已实现·待验证 | Login |", dashboard)
        self.assertEqual(state["items"][0]["verification"], "not_run")
