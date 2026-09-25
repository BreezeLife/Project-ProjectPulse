import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class HookTests(unittest.TestCase):
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
            self.assertIn("PROJECT PULSE", output["systemMessage"])
            self.assertFalse((root / "STATUS.md").exists())
