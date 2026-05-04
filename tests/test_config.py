import os
import unittest
from pynotify_auto import get_config, get_threshold

class TestPyNotifyConfig(unittest.TestCase):
    def test_get_config_default(self):
        # Ensure default value is returned when env var is missing
        val = get_config("nonexistent_key", "default_val")
        self.assertEqual(val, "default_val")

    def test_get_config_env(self):
        # Ensure env var is correctly picked up
        os.environ["PYNOTIFY_TEST_KEY"] = "hello"
        val = get_config("test_key", "default")
        self.assertEqual(val, "hello")
        del os.environ["PYNOTIFY_TEST_KEY"]

    def test_get_threshold_default(self):
        # Default threshold should be 5.0
        if "PYNOTIFY_THRESHOLD" in os.environ:
            del os.environ["PYNOTIFY_THRESHOLD"]
        import pynotify_auto
        old_config = pynotify_auto._config
        pynotify_auto._config = {}
        try:
            self.assertEqual(get_threshold(), 5.0)
        finally:
            pynotify_auto._config = old_config

    def test_get_threshold_custom(self):
        os.environ["PYNOTIFY_THRESHOLD"] = "10.5"
        self.assertEqual(get_threshold(), 10.5)
        del os.environ["PYNOTIFY_THRESHOLD"]

    def test_get_threshold_invalid(self):
        # Should fallback to default on invalid input
        os.environ["PYNOTIFY_THRESHOLD"] = "invalid"
        import pynotify_auto
        old_config = pynotify_auto._config
        pynotify_auto._config = {}
        try:
            self.assertEqual(get_threshold(), 5.0)
        finally:
            pynotify_auto._config = old_config
            del os.environ["PYNOTIFY_THRESHOLD"]

if __name__ == "__main__":
    unittest.main()
