import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_acceptance.py"
SPEC = importlib.util.spec_from_file_location("run_acceptance", SCRIPT)
RUN_ACCEPTANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN_ACCEPTANCE)


class TestRunAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_required_spawn_failure_is_logged(self):
        result = RUN_ACCEPTANCE.run_step(
            "missing-command",
            [str(self.root / "does-not-exist")],
            self.root,
            required=True,
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["returncode"], 127)
        self.assertIn("FileNotFoundError", result["spawn_error"])
        self.assertIn(
            "Unable to start command",
            (self.root / "missing-command.log").read_text(encoding="utf-8"),
        )

    def test_optional_spawn_failure_does_not_become_required(self):
        result = RUN_ACCEPTANCE.run_step(
            "missing-optional",
            [str(self.root / "does-not-exist")],
            self.root,
            required=False,
        )

        self.assertEqual(result["status"], "OPTIONAL_FAIL")
        self.assertFalse(result["required"])

    @mock.patch.object(RUN_ACCEPTANCE.subprocess, "run")
    def test_timeout_is_reported_with_a_log(self, run):
        run.side_effect = subprocess.TimeoutExpired(
            cmd=[sys.executable, "slow.py"],
            timeout=1,
            output="partial output",
        )

        result = RUN_ACCEPTANCE.run_step(
            "timeout",
            [sys.executable, "slow.py"],
            self.root,
            timeout=1,
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["returncode"], 124)
        self.assertTrue(result["timed_out"])
        self.assertIn(
            "Timed out after 1 seconds",
            (self.root / "timeout.log").read_text(encoding="utf-8"),
        )

    def test_environment_report_contains_reproduction_metadata(self):
        report = RUN_ACCEPTANCE.write_environment(self.root, argv=["--skip-core-tests"])
        saved = json.loads((self.root / "environment.json").read_text(encoding="utf-8"))

        self.assertEqual(saved, report)
        self.assertTrue(report["captured_at_utc"].endswith("+00:00"))
        self.assertEqual(report["command"][-1], "--skip-core-tests")
        self.assertIn("git_dirty", report)
        self.assertIn("PYTHONUTF8", report["environment"])


if __name__ == "__main__":
    unittest.main()
