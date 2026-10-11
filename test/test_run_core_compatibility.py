import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_core_compatibility.py"
SPEC = importlib.util.spec_from_file_location("run_core_compatibility", SCRIPT)
RUNNER = importlib.util.module_from_spec(SPEC)
with mock.patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
    SPEC.loader.exec_module(RUNNER)


class TestCoreCompatibilityReport(unittest.TestCase):
    def test_acceptance_rejects_empty_or_skipped_reports(self):
        for report in ({}, {"status": "PASS", "required_passed": 0, "required_total": 0},
                       {"status": "PASS", "required_passed": 4, "required_total": 4}):
            self.assertFalse(RUNNER.acceptance_complete(report))

    def test_acceptance_requires_actual_required_steps(self):
        names = ("pip-check", "imports", "litex-cli-help", "portable-core-tests", "minimal-soc")
        report = dict(status="PASS", required_passed=5, required_total=5,
                      steps=[dict(name=name, required=True, status="PASS") for name in names])
        self.assertTrue(RUNNER.acceptance_complete(report))
        report["steps"][-1]["status"] = "FAIL"
        self.assertFalse(RUNNER.acceptance_complete(report))

    def test_permission_probe_must_have_exercised_the_check(self):
        names = ("vcd_tempfile_and_cleanup", "builder_unicode_path_and_encoding",
                 "builder_write_permission", "filtered_subprocess_argv_and_exit")
        report = dict(checks=[dict(name=name, status="PASS", detail={}) for name in names])
        self.assertFalse(RUNNER.host_probe_complete(report))
        report["checks"][2]["detail"]["exercised"] = True
        self.assertTrue(RUNNER.host_probe_complete(report))

    @mock.patch.object(RUNNER, "has_native_marker", return_value=False)
    @mock.patch.object(RUNNER, "git_value", return_value="test-source")
    @mock.patch.object(RUNNER, "run_step")
    def test_native_request_on_other_host_is_refused(self, run, git, marker):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new-result"
            argv = [str(SCRIPT), "--scope", "native", "--operator", "test", "--output-dir", str(output)]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(RUNNER.main(), 2)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["status"], "REFUSED")
            run.assert_not_called()

    def test_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "original.txt"
            marker.write_text("keep")
            argv = [str(SCRIPT), "--scope", "supplementary", "--operator", "test", "--output-dir", directory]
            with mock.patch.object(sys, "argv", argv), mock.patch("sys.stderr"):
                with self.assertRaises(SystemExit) as error:
                    RUNNER.main()
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(marker.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
