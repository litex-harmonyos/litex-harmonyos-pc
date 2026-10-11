import importlib.util
from pathlib import Path
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/probe_core_host.py"
SPEC = importlib.util.spec_from_file_location("probe_core_host", SCRIPT)
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class TestPermissionPrecondition(unittest.TestCase):
    def tearDown(self):
        PROBE.results.clear()

    def test_both_allowed_is_blocked_and_not_exercised(self):
        with mock.patch.object(Path, "write_text"), mock.patch.object(PROBE.Builder, "_export_write"):
            PROBE.check("builder_write_permission", PROBE.denied_write)
        result = PROBE.results[-1]
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["detail"]["exercised"])
        self.assertEqual(result["detail"]["native_write"], "ALLOWED")

    def test_both_denied_preserves_actual_permission_pass(self):
        with mock.patch.object(Path, "write_text", side_effect=PermissionError("native denied")), \
             mock.patch.object(PROBE.Builder, "_export_write", side_effect=PermissionError("builder denied")):
            PROBE.check("builder_write_permission", PROBE.denied_write)
        result = PROBE.results[-1]
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["detail"]["exercised"])
        self.assertTrue(result["detail"]["permission_error_propagated"])

    def test_builder_allowing_after_native_denial_is_a_failure(self):
        with mock.patch.object(Path, "write_text", side_effect=PermissionError("native denied")), \
             mock.patch.object(PROBE.Builder, "_export_write"):
            PROBE.check("builder_write_permission", PROBE.denied_write)
        self.assertEqual(PROBE.results[-1]["status"], "FAIL")
        self.assertIn("permission mismatch", PROBE.results[-1]["traceback"])

    def test_unexpected_error_is_a_failure_not_an_environment_exception(self):
        with mock.patch.object(Path, "write_text", side_effect=OSError("unexpected I/O error")):
            PROBE.check("builder_write_permission", PROBE.denied_write)
        self.assertEqual(PROBE.results[-1]["status"], "FAIL")
        self.assertIn("unexpected I/O error", PROBE.results[-1]["traceback"])


if __name__ == "__main__":
    unittest.main()
