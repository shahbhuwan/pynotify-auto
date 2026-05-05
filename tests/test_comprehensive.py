"""
Comprehensive test suite for pynotify-auto v0.5.6 rewrite.

Covers:
  - Public API surface (no private imports needed)
  - Configuration helpers
  - Failure detection logic (sys.exit wrapper + sys.last_type fallback)
  - Hook registration (idempotency, no sys.excepthook override)
  - Import side-effect safety
  - SystemExit edge cases
  - CLI entry points
  - Multiprocessing anti-spam
"""

import os
import sys
import unittest
import subprocess
import importlib
import textwrap

# Use the current interpreter for subprocess tests
PYTHON = sys.executable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



class TestPublicAPI(unittest.TestCase):
    """Ensure the public API surface is clean and correct."""

    def test_public_names_exist(self):
        import pynotify_auto
        for name in ("install_hook", "show_popup", "play_sound",
                      "get_config", "get_threshold", "__version__",
                      "hook_active"):
            self.assertTrue(
                hasattr(pynotify_auto, name),
                f"Missing public attribute: {name}"
            )

    def test_no_private_names_leaked(self):
        """The old _-prefixed public-facing names should NOT exist."""
        import pynotify_auto
        for old_name in ("_show_popup", "_play_sound", "_get_config", "_get_threshold"):
            self.assertFalse(
                hasattr(pynotify_auto, old_name),
                f"Old private name still exists: {old_name}"
            )

    def test_version_string(self):
        import pynotify_auto
        self.assertEqual(pynotify_auto.__version__, "0.5.6")


class TestConfig(unittest.TestCase):
    """Test the configuration helpers."""

    def test_get_config_default(self):
        from pynotify_auto import get_config
        val = get_config("nonexistent_key_abc", "my_default")
        self.assertEqual(val, "my_default")

    def test_get_config_from_env(self):
        from pynotify_auto import get_config
        os.environ["PYNOTIFY_TESTKEY99"] = "hello_world"
        try:
            val = get_config("testkey99", "fallback")
            self.assertEqual(val, "hello_world")
        finally:
            del os.environ["PYNOTIFY_TESTKEY99"]

    def test_get_threshold_default(self):
        from pynotify_auto import get_threshold
        os.environ.pop("PYNOTIFY_THRESHOLD", None)
        import pynotify_auto
        old_config = pynotify_auto._config
        pynotify_auto._config = {}
        try:
            self.assertEqual(get_threshold(), 5.0)
        finally:
            pynotify_auto._config = old_config

    def test_get_threshold_custom(self):
        from pynotify_auto import get_threshold
        os.environ["PYNOTIFY_THRESHOLD"] = "42.5"
        try:
            self.assertEqual(get_threshold(), 42.5)
        finally:
            del os.environ["PYNOTIFY_THRESHOLD"]

    def test_get_threshold_invalid_falls_back(self):
        from pynotify_auto import get_threshold
        os.environ["PYNOTIFY_THRESHOLD"] = "not_a_number"
        try:
            self.assertEqual(get_threshold(), 5.0)
        finally:
            del os.environ["PYNOTIFY_THRESHOLD"]


class TestFailureDetection(unittest.TestCase):
    """Test _detect_failure() logic."""

    def setUp(self):
        import pynotify_auto
        pynotify_auto._exit_code = None
        for attr in ("last_type", "last_value", "last_traceback"):
            if hasattr(sys, attr):
                delattr(sys, attr)

    def tearDown(self):
        import pynotify_auto
        pynotify_auto._exit_code = None
        for attr in ("last_type", "last_value", "last_traceback"):
            if hasattr(sys, attr):
                delattr(sys, attr)

    def test_no_exception_is_success(self):
        from pynotify_auto import _detect_failure
        self.assertFalse(_detect_failure())

    def test_exit_code_0_is_success(self):
        import pynotify_auto
        pynotify_auto._exit_code = 0
        self.assertFalse(pynotify_auto._detect_failure())

    def test_exit_code_none_is_success(self):
        import pynotify_auto
        pynotify_auto._exit_code = None
        self.assertFalse(pynotify_auto._detect_failure())

    def test_exit_code_1_is_failure(self):
        import pynotify_auto
        pynotify_auto._exit_code = 1
        self.assertTrue(pynotify_auto._detect_failure())

    def test_exit_code_string_is_failure(self):
        """sys.exit('error') passes a string as the code."""
        import pynotify_auto
        pynotify_auto._exit_code = "something went wrong"
        self.assertTrue(pynotify_auto._detect_failure())

    def test_value_error_via_last_type(self):
        from pynotify_auto import _detect_failure
        sys.last_type = ValueError
        sys.last_value = ValueError("boom")
        self.assertTrue(_detect_failure())

    def test_runtime_error_via_last_type(self):
        from pynotify_auto import _detect_failure
        sys.last_type = RuntimeError
        sys.last_value = RuntimeError("oops")
        self.assertTrue(_detect_failure())

    def test_keyboard_interrupt_via_last_type(self):
        from pynotify_auto import _detect_failure
        sys.last_type = KeyboardInterrupt
        sys.last_value = KeyboardInterrupt()
        self.assertTrue(_detect_failure())


class TestHookRegistration(unittest.TestCase):
    """Test install_hook() behavior."""

    def test_import_does_not_override_excepthook(self):
        """Importing pynotify_auto must NOT touch sys.excepthook."""
        original = sys.excepthook
        importlib.reload(sys.modules["pynotify_auto"])
        self.assertIs(sys.excepthook, original)

    def test_install_hook_does_not_override_excepthook(self):
        """install_hook() must NOT touch sys.excepthook."""
        import pynotify_auto
        importlib.reload(pynotify_auto)
        original = sys.excepthook
        pynotify_auto.install_hook()
        self.assertIs(sys.excepthook, original)

    def test_install_hook_sets_flag(self):
        import pynotify_auto
        importlib.reload(pynotify_auto)  # fresh state
        self.assertFalse(pynotify_auto.hook_active)
        pynotify_auto.install_hook()
        self.assertTrue(pynotify_auto.hook_active)
        self.assertTrue(pynotify_auto._hook_registered)

    def test_install_hook_idempotent(self):
        """Calling install_hook() twice should not register two handlers."""
        import pynotify_auto
        importlib.reload(pynotify_auto)
        pynotify_auto.install_hook()
        pynotify_auto.install_hook()  # second call
        self.assertTrue(pynotify_auto.hook_active)

    def test_install_hook_wraps_sys_exit(self):
        """install_hook() should wrap sys.exit to capture exit codes."""
        import pynotify_auto
        importlib.reload(pynotify_auto)
        original_exit = sys.exit
        pynotify_auto.install_hook()
        self.assertIsNot(sys.exit, original_exit,
                         "sys.exit should be wrapped after install_hook()")


class TestSubprocess(unittest.TestCase):
    """
    End-to-end tests that run real Python scripts in a subprocess
    using the test environment's interpreter.
    """

    def _run_script(self, code, env_overrides=None, timeout=30):
        """Run a Python snippet in a subprocess and capture output."""
        env = os.environ.copy()
        env["PYNOTIFY_THRESHOLD"] = "1"  # Low threshold for fast tests
        env["PYNOTIFY_REMOTE_BACKEND"] = "" # Disable heartbeat noise
        env.pop("PYNOTIFY_ACTIVE_PID", None) # Allow subprocess to notify
        if env_overrides:
            env.update(env_overrides)

        result = subprocess.run(
            [PYTHON, "-c", code],
            capture_output=True, text=True, timeout=timeout,
            env=env, cwd=PROJECT_ROOT,
        )
        return result

    def test_success_notification(self):
        """A script that sleeps > threshold should print [SUCCESS]."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import time; time.sleep(2); print('done')"
        )
        r = self._run_script(code)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[SUCCESS]", r.stdout)
        self.assertIn("finished", r.stdout)

    def test_failure_notification(self):
        """A script that raises should print [FAILED]."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import time; time.sleep(2); raise ValueError('boom')"
        )
        r = self._run_script(code)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[FAILED]", r.stdout)
        self.assertIn("FAILED", r.stdout)

    def test_below_threshold_no_notification(self):
        """A fast script should produce NO pynotify output."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "print('fast')"
        )
        r = self._run_script(code, env_overrides={"PYNOTIFY_THRESHOLD": "999"})
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("[SUCCESS]", r.stdout)
        self.assertNotIn("[FAILED]", r.stdout)

    def test_disabled_no_notification(self):
        """PYNOTIFY_DISABLE=1 should suppress all output."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import time; time.sleep(2); print('done')"
        )
        r = self._run_script(code, env_overrides={"PYNOTIFY_DISABLE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("[SUCCESS]", r.stdout)
        self.assertNotIn("pynotify-auto", r.stdout)

    def test_system_exit_0_is_success(self):
        """sys.exit(0) should be reported as success."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import sys, time; time.sleep(2); sys.exit(0)"
        )
        r = self._run_script(code)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[SUCCESS]", r.stdout)

    def test_system_exit_1_is_failure(self):
        """sys.exit(1) should be reported as failure."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import sys, time; time.sleep(2); sys.exit(1)"
        )
        r = self._run_script(code)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[FAILED]", r.stdout)

    def test_system_exit_no_arg_is_success(self):
        """sys.exit() with no argument should be success."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import sys, time; time.sleep(2); sys.exit()"
        )
        r = self._run_script(code)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[SUCCESS]", r.stdout)

    def test_sound_mode(self):
        """Mode=sound should still print to console, just use sound backend."""
        code = (
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import time; time.sleep(2); print('done')"
        )
        r = self._run_script(code, env_overrides={"PYNOTIFY_MODE": "sound"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("[SUCCESS]", r.stdout)

    def test_excepthook_untouched_in_subprocess(self):
        """Verify sys.excepthook is completely untouched after install_hook."""
        code = (
            "import sys; orig = sys.excepthook; "
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "print('preserved' if sys.excepthook is orig else 'OVERRIDDEN')"
        )
        r = self._run_script(code)
        self.assertIn("preserved", r.stdout)
        self.assertNotIn("OVERRIDDEN", r.stdout)

    def test_no_notification_in_interactive_mode(self):
        """Scripts with IPython in sys.modules should be skipped."""
        code = (
            "import sys; sys.modules['IPython'] = True; "
            "import pynotify_auto; pynotify_auto.install_hook(); "
            "import time; time.sleep(2); print('done')"
        )
        r = self._run_script(code)
        self.assertNotIn("[SUCCESS]", r.stdout)
        self.assertNotIn("pynotify-auto", r.stdout)


class TestCLI(unittest.TestCase):
    """Test CLI entry points."""

    def test_cli_version(self):
        r = subprocess.run(
            [PYTHON, "-m", "pynotify_auto", "--version"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("0.5.6", r.stdout)

    def test_cli_info(self):
        r = subprocess.run(
            [PYTHON, "-m", "pynotify_auto", "--info"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("Mode:", r.stdout)
        self.assertIn("Threshold:", r.stdout)
        self.assertIn("Status:", r.stdout)

    def test_cli_help(self):
        r = subprocess.run(
            [PYTHON, "-m", "pynotify_auto", "--help"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("pynotify-auto", r.stdout)


class TestMultiprocessing(unittest.TestCase):
    """Verify that child processes don't fire notifications."""

    def test_only_main_process_notifies(self):
        # Write to a temp file so multiprocessing can pickle on Windows
        script = textwrap.dedent("""\
            import pynotify_auto
            pynotify_auto.install_hook()
            import time, os
            from multiprocessing import Pool

            def work(n):
                time.sleep(1)
                return n * n

            if __name__ == "__main__":
                with Pool(2) as p:
                    results = p.map(work, range(2))
                time.sleep(2)
                print("main_done")
        """)

        script_path = os.path.join(PROJECT_ROOT, "_test_mp_temp.py")
        try:
            with open(script_path, "w") as f:
                f.write(script)

            env = os.environ.copy()
            env["PYNOTIFY_THRESHOLD"] = "1"
            env["PYNOTIFY_MODE"] = "sound"  # Avoid popups during tests
            env["PYNOTIFY_REMOTE_BACKEND"] = "" # Disable heartbeat noise
            env.pop("PYNOTIFY_ACTIVE_PID", None)

            r = subprocess.run(
                [PYTHON, script_path],
                capture_output=True, text=True, timeout=60,
                env=env, cwd=PROJECT_ROOT,
            )
            # Should see exactly ONE notification line (from main process)
            notify_lines = [
                line for line in r.stdout.splitlines()
                if "pynotify-auto" in line and "Remote updates active" not in line
            ]
            self.assertEqual(
                len(notify_lines), 1,
                f"Expected 1 notification, got {len(notify_lines)}: {notify_lines}"
            )
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)


class TestPackagingCliSkipped(unittest.TestCase):
    """pip/conda must not get stdout wrappers (breaks pipes)."""

    def test_pip_module_argv_detected(self):
        from pynotify_auto import _looks_like_packaging_cli

        old = sys.argv
        try:
            sys.argv = [sys.executable, "-m", "pip", "install", "x"]
            self.assertTrue(_looks_like_packaging_cli())
            sys.argv = [sys.executable, "-m", "pytest", "x"]
            self.assertFalse(_looks_like_packaging_cli())
        finally:
            sys.argv = old

    def test_pip_exe_detected(self):
        from pynotify_auto import _looks_like_packaging_cli

        old = sys.argv
        try:
            sys.argv = [r"C:\Env\Scripts\pip.exe", "install", "x"]
            self.assertTrue(_looks_like_packaging_cli())
        finally:
            sys.argv = old


class TestTeeStreamResilience(unittest.TestCase):
    """Tee must not break host scripts if the real console write/flush fails (Windows)."""

    def test_tee_write_returns_len_even_if_base_raises(self):
        from pynotify_auto import _TeeStream
        from collections import deque
        import threading

        class BrokenConsole:
            def write(self, s):
                raise OSError(1, "Incorrect function")

            def flush(self):
                raise OSError(1, "Incorrect function")

        hist = deque(maxlen=10)
        tee = _TeeStream(BrokenConsole(), hist, threading.Lock())
        n = tee.write("still ok\n")
        self.assertEqual(n, len("still ok\n"))
        tee.flush()  # must not raise

    def test_tee_no_double_flush_in_write(self):
        import pynotify_auto
        import inspect

        src = inspect.getsource(pynotify_auto._TeeStream.write)
        self.assertNotIn("self._base.flush()", src, "flush in write() causes WinError on some consoles")


class TestPythonTeeInterceptor(unittest.TestCase):
    """Windows fix: Python-layer tee must not use os.dup2 (breaks console/tracebacks)."""

    def test_tee_captures_stderr_and_restores(self):
        from pynotify_auto import PythonTeeInterceptor

        saved_out, saved_err = sys.stdout, sys.stderr
        tee = PythonTeeInterceptor(max_lines=10)
        try:
            sys.stderr.write("pynotify_unit_test_line\n")
            sys.stderr.flush()
            logs = tee.get_logs()
            self.assertTrue(
                any("pynotify_unit_test_line" in entry for entry in logs),
                msg=f"logs={logs!r}",
            )
        finally:
            tee.stop()

        self.assertIs(sys.stdout, saved_out)
        self.assertIs(sys.stderr, saved_err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
