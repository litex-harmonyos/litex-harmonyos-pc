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
        report["checks"][2]["detail"].update(exercised=True, permission_error_propagated=True,
                                            native_write="DENIED", builder_write="DENIED")
        self.assertTrue(RUNNER.host_probe_complete(report))

    def test_unsupported_permission_fixture_is_blocked_not_pass(self):
        names = ("vcd_tempfile_and_cleanup", "builder_unicode_path_and_encoding",
                 "filtered_subprocess_argv_and_exit")
        report = dict(checks=[dict(name=name, status="PASS") for name in names])
        permission = dict(name="builder_write_permission", status="BLOCKED",
                          detail=dict(exercised=False, native_write="ALLOWED", builder_write="ALLOWED",
                                      reason="chmod did not establish denied write"))
        report["checks"].append(permission)
        self.assertEqual(RUNNER.host_probe_status(report), "BLOCKED")
        self.assertFalse(RUNNER.host_probe_complete(report))
        permission["detail"]["native_write"] = "DENIED"
        self.assertEqual(RUNNER.host_probe_status(report), "FAIL")

    def test_another_required_failure_cannot_be_hidden_by_permission_block(self):
        report = dict(checks=[dict(name="builder_write_permission", status="BLOCKED",
                                  detail=dict(exercised=False, native_write="ALLOWED", builder_write="ALLOWED",
                                              reason="unsupported fixture"))])
        self.assertEqual(RUNNER.host_probe_status(report), "FAIL")

    def test_failed_or_blocked_native_run_is_not_ready_for_peer_review(self):
        self.assertEqual(RUNNER.completion_status(True, "BLOCKED"), "native-validation-blocked")
        self.assertEqual(RUNNER.completion_status(True, "FAIL"), "native-validation-failed")
        self.assertEqual(RUNNER.completion_status(True, "PASS"), "peer-review-pending")

    def run_with_blocked_permission(self, fail_environment=False):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result"

            def step(name, command, logs, required=True, timeout=None):
                code = 1 if name == "environment-probe" and fail_environment else 0
                if name == "core-acceptance":
                    acceptance = output / "acceptance"
                    acceptance.mkdir()
                    names = ("pip-check", "imports", "litex-cli-help", "portable-core-tests", "minimal-soc")
                    (acceptance / "acceptance-report.json").write_text(json.dumps(dict(
                        status="PASS", required_passed=5, required_total=5,
                        steps=[dict(name=n, required=True, status="PASS") for n in names])))
                if name == "host-probe":
                    code = 2
                    checks = [dict(name=n, status="PASS") for n in
                              ("vcd_tempfile_and_cleanup", "builder_unicode_path_and_encoding",
                               "filtered_subprocess_argv_and_exit")]
                    checks.append(dict(name="builder_write_permission", status="BLOCKED",
                                       detail=dict(exercised=False, native_write="ALLOWED", builder_write="ALLOWED",
                                                   reason="denied write unavailable")))
                    (logs / "host-probe.log").write_text(json.dumps(dict(checks=checks)))
                return dict(name=name, returncode=code, status="PASS" if code == 0 else "FAIL", required=required)

            argv = [str(SCRIPT), "--scope", "native", "--operator", "unit-test", "--output-dir", str(output)]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(RUNNER, "run_step", side_effect=step), \
                 mock.patch.object(RUNNER, "has_native_marker", return_value=True), \
                 mock.patch.object(RUNNER, "git_value", return_value="unit-test-source"), \
                 mock.patch.object(RUNNER, "firmware_conditions", return_value={}), mock.patch("builtins.print"):
                code = RUNNER.main()
            return code, json.loads((output / "report.json").read_text())

    def test_runner_keeps_permission_block_in_final_report(self):
        code, report = self.run_with_blocked_permission()
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertTrue(report["acceptance_complete"])
        self.assertFalse(report["host_probe_complete"])
        self.assertEqual(report["week2_completion"], "native-validation-blocked")

    def test_runner_keeps_real_failure_even_with_permission_block(self):
        code, report = self.run_with_blocked_permission(fail_environment=True)
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "FAIL")

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
