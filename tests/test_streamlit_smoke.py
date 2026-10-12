"""Exercise smoke-runner lifecycle without Streamlit, sockets, or a live app."""
from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, call, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "smoke_streamlit.py"
spec = importlib.util.spec_from_file_location("rowspect_smoke_under_test", SCRIPT)
assert spec is not None and spec.loader is not None
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class StreamlitSmokeLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.process = Mock()
        self.process.communicate.return_value = ("server diagnostic\n", None)
        self.process.stdout.read.side_effect = AssertionError(
            "Reading the live child's stdout before stopping it can hang."
        )
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.enterContext(redirect_stdout(self.stdout))
        self.enterContext(redirect_stderr(self.stderr))
        self.enterContext(patch.dict(sys.modules, {"streamlit": ModuleType("streamlit")}))
        self.enterContext(patch.object(smoke, "_free_port", return_value=8765))
        self.wait_for = self.enterContext(
            patch.object(smoke, "_wait_for", side_effect=[b"ok", b"<html>ok</html>"])
        )
        self.popen = self.enterContext(
            patch.object(smoke.subprocess, "Popen", return_value=self.process)
        )

    def test_success_stops_and_drains_child_before_reporting_pass(self) -> None:
        self.assertEqual(smoke.main(), 0)
        self.assertEqual(
            self.process.method_calls,
            [call.terminate(), call.communicate(timeout=5)],
        )
        self.assertIn("UI smoke PASS", self.stdout.getvalue())
        self.assertEqual(self.stderr.getvalue(), "")
        command = self.popen.call_args.args[0]
        self.assertIn("--server.address=127.0.0.1", command)
        self.assertIn("--browser.gatherUsageStats=false", command)

    def test_health_failure_returns_diagnostic_without_unbounded_read(self) -> None:
        self.wait_for.side_effect = RuntimeError("health check timed out")
        self.process.communicate.return_value = ("OMITTED_PREFIX" + "x" * 4200 + "DIAGNOSTIC_TAIL", None)
        self.assertEqual(smoke.main(), 1)
        self.assertEqual(
            self.process.method_calls,
            [call.terminate(), call.communicate(timeout=5)],
        )
        output = self.stderr.getvalue()
        self.assertIn("health check timed out", output)
        self.assertIn("DIAGNOSTIC_TAIL", output)
        self.assertNotIn("OMITTED_PREFIX", output)
        self.assertNotIn("PASS", self.stdout.getvalue())

    def test_empty_root_is_a_failure_and_still_cleans_up(self) -> None:
        self.wait_for.side_effect = [b"ok", b""]
        self.assertEqual(smoke.main(), 1)
        self.assertIn("empty response", self.stderr.getvalue())
        self.process.terminate.assert_called_once_with()
        self.process.communicate.assert_called_once_with(timeout=5)

    def test_root_request_failure_is_not_a_pass(self) -> None:
        self.wait_for.side_effect = [b"ok", RuntimeError("root unavailable")]
        self.assertEqual(smoke.main(), 1)
        self.assertIn("root unavailable", self.stderr.getvalue())
        self.assertNotIn("PASS", self.stdout.getvalue())
        self.process.communicate.assert_called_once_with(timeout=5)

    def test_stubborn_child_is_killed_after_bounded_grace_period(self) -> None:
        self.wait_for.side_effect = RuntimeError("not ready")
        self.process.communicate.side_effect = [
            subprocess.TimeoutExpired("streamlit", 5),
            ("diagnostic after kill", None),
        ]
        self.assertEqual(smoke.main(), 1)
        self.assertEqual(
            self.process.method_calls,
            [call.terminate(), call.communicate(timeout=5), call.kill(), call.communicate(timeout=5)],
        )
        self.assertIn("diagnostic after kill", self.stderr.getvalue())

    def test_interruption_propagates_after_child_cleanup(self) -> None:
        self.wait_for.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            smoke.main()
        self.process.terminate.assert_called_once_with()
        self.process.communicate.assert_called_once_with(timeout=5)
        self.assertNotIn("PASS", self.stdout.getvalue())

    def test_missing_streamlit_does_not_start_a_child(self) -> None:
        with patch.dict(sys.modules, {"streamlit": None}):
            self.assertEqual(smoke.main(), 2)
        self.popen.assert_not_called()
        self.assertIn("not installed", self.stderr.getvalue())

    def test_cleanup_timeout_cannot_report_success(self) -> None:
        self.process.communicate.side_effect = subprocess.TimeoutExpired("streamlit", 5)
        with self.assertRaises(subprocess.TimeoutExpired):
            smoke.main()
        self.process.kill.assert_called_once_with()
        self.assertEqual(self.process.communicate.call_count, 2)
        self.assertNotIn("PASS", self.stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
