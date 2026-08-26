import importlib.util
import io
import os
import sys
import unittest
import unittest.mock


def load_output():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "smu_parts", "output.py")
    spec = importlib.util.spec_from_file_location("smu_output", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OutputTests(unittest.TestCase):
    def setUp(self):
        self.output = load_output()
        self._env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)

    def test_ohai_uses_brew_prefix(self):
        buf = io.StringIO()
        self.output.ohai("Pulling blueprint", file=buf)
        self.assertIn("==> Pulling blueprint", buf.getvalue())

    def test_opoo_uses_warning_label(self):
        buf = io.StringIO()
        self.output.opoo("blocked repo", file=buf)
        self.assertIn("Warning: blocked repo", buf.getvalue())

    def test_no_emoji_fallback(self):
        os.environ["SMU_NO_EMOJI"] = "1"
        buf = io.StringIO()
        with unittest.mock.patch.object(sys.stderr, "isatty", return_value=True), \
                unittest.mock.patch.object(sys.stdout, "isatty", return_value=True):
            self.output.pretty_ok("installer", file=buf)
        self.assertIn("(ok)", buf.getvalue())
        self.assertNotIn("✔", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
