import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from project_pulse.cli import inspect, main
from project_pulse.paths import safe_child
from project_pulse.renderer import render


class PulseTests(unittest.TestCase):
    def make_project(self, git=False):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        (root / "TASKS.md").write_text("# Tasks\n- [x] Login\n- [ ] Payments\n", encoding="utf-8")
        (root / "README.md").write_text("prototype", encoding="utf-8")
        if git:
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=Test", "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-qm", "init"], check=True)
        return directory, root

    def test_non_git_inspect_is_read_only(self):
        temporary, root = self.make_project()
        try:
            before = sorted(path.name for path in root.iterdir())
            _, report, raw = inspect(root)
            self.assertEqual(report["vcs"], "none")
            self.assertIsNone(raw)
            self.assertEqual(before, sorted(path.name for path in root.iterdir()))
        finally:
            temporary.cleanup()

    def test_init_update_and_stale(self):
        temporary, root = self.make_project(git=True)
        try:
            self.assertEqual(main(["init", "--project", str(root)]), 0)
            self.assertTrue((root / ".project-pulse/status.json").exists())
            _, fresh, _ = inspect(root)
            self.assertEqual(fresh["status"], "FRESH")
            (root / "README.md").write_text("changed", encoding="utf-8")
            _, stale, _ = inspect(root)
            self.assertEqual(stale["status"], "STALE")
            self.assertEqual(stale["readiness"]["review"], "UNKNOWN")
            self.assertEqual(main(["update", "--project", str(root)]), 0)
        finally:
            temporary.cleanup()

    def test_symlink_and_secret_are_not_read(self):
        temporary, root = self.make_project()
        outside = root.parent / "outside.txt"
        try:
            (root / ".env").write_text("TOP_SECRET", encoding="utf-8")
            outside.write_text("outside", encoding="utf-8")
            (root / "link.txt").symlink_to(outside)
            with self.assertRaises(ValueError):
                safe_child(root, "link.txt")
            _, report, _ = inspect(root)
            self.assertNotIn(".env", report["known_files"])
        finally:
            outside.unlink(missing_ok=True)
            temporary.cleanup()

    def test_inference_is_not_verification(self):
        temporary, root = self.make_project()
        try:
            _, report, _ = inspect(root)
            login = next(item for item in report["items"] if item["title"] == "Login")
            self.assertEqual(login["derived"], "implemented_unverified")
        finally:
            temporary.cleanup()

    def test_priority_marker_keeps_task_identity_and_historical_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tasks = root / "TASKS.md"
            tasks.write_text("- [x] Login\n", encoding="utf-8")
            self.assertEqual(main(["init", "--project", str(root)]), 0)
            state_path = root / ".project-pulse/status.json"
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            original_id = saved["items"][0]["id"]
            saved["items"][0]["verification"] = "passed"
            saved["items"][0]["evidence"].append(
                {"type": "human", "fingerprint": saved["fingerprint"]})
            state_path.write_text(json.dumps(saved), encoding="utf-8")

            tasks.write_text("- [x] [P0] Login\n", encoding="utf-8")
            _, report, _ = inspect(root)

        self.assertEqual(len(report["items"]), 1)
        self.assertEqual(report["items"][0]["id"], original_id)
        self.assertEqual(report["items"][0]["title"], "[P0] Login")
        self.assertTrue(any(record.get("type") == "human" for record in report["items"][0]["evidence"]))
        self.assertEqual(report["items"][0]["verification"], "not_run")

    def test_current_test_evidence_appears_in_report(self):
        temporary, root = self.make_project()
        try:
            self.assertEqual(main(["init", "--project", str(root)]), 0)
            status_path = root / ".project-pulse/status.json"
            state = json.loads(status_path.read_text(encoding="utf-8"))
            login = next(item for item in state["items"] if item["title"] == "Login")
            login["verification"] = "passed"
            login["evidence"].extend({"type": kind, "fingerprint": state["fingerprint"]}
                                     for kind in ("build", "test", "human"))
            status_path.write_text(json.dumps(state), encoding="utf-8")

            _, report, _ = inspect(root)
            self.assertEqual(report["status"], "FRESH")
            self.assertEqual(report.get("checks", {}).get("build"), "PRESENT")
            self.assertEqual(report.get("checks", {}).get("tests"), "PRESENT")
            self.assertEqual(report.get("checks", {}).get("manual_test"), "PRESENT")
            self.assertIn("Build        PRESENT", render(report, language="en"))
            self.assertIn("Tests        PRESENT", render(report, language="en"))
            self.assertIn("Manual test  PRESENT", render(report, language="en"))
            self.assertIn("EVIDENCE  Build PRESENT · Tests PRESENT · Manual test PRESENT",
                          render(report, compact=True, language="en"))
        finally:
            temporary.cleanup()

    def test_stale_test_evidence_is_not_current(self):
        temporary, root = self.make_project()
        try:
            self.assertEqual(main(["init", "--project", str(root)]), 0)
            status_path = root / ".project-pulse/status.json"
            state = json.loads(status_path.read_text(encoding="utf-8"))
            login = next(item for item in state["items"] if item["title"] == "Login")
            login["verification"] = "passed"
            login["evidence"].extend({"type": kind, "fingerprint": state["fingerprint"]}
                                     for kind in ("build", "test", "human"))
            status_path.write_text(json.dumps(state), encoding="utf-8")
            (root / "README.md").write_text("changed", encoding="utf-8")

            _, report, _ = inspect(root)
            self.assertEqual(report["status"], "STALE")
            self.assertEqual(report.get("checks", {}).get("build"), "UNKNOWN")
            self.assertEqual(report.get("checks", {}).get("tests"), "UNKNOWN")
            self.assertEqual(report.get("checks", {}).get("manual_test"), "UNKNOWN")
            self.assertIn("Tests        UNKNOWN", render(report, language="en"))
        finally:
            temporary.cleanup()

    def test_init_writes_safe_markdown_dashboard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TASKS.md").write_text(
                "- [x] [Open](https://example.com) | <script>\n- [ ] Payments\n", encoding="utf-8")
            self.assertEqual(main(["init", "--project", str(root)]), 0)
            dashboard = (root / "STATUS.md").read_text(encoding="utf-8")

        self.assertTrue(dashboard.startswith("# Project Pulse"))
        self.assertIn("| State | Count | Chart |", dashboard)
        self.assertIn("◐ Needs verification", dashboard)
        self.assertIn("█", dashboard)
        self.assertNotIn("[Open](https://example.com)", dashboard)
        self.assertNotIn("<script>", dashboard)
