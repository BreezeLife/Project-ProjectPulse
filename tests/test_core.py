import subprocess
import tempfile
import unittest
from pathlib import Path

from project_pulse.cli import inspect, main
from project_pulse.paths import safe_child


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
