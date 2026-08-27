#!/usr/bin/env python3

import os
import subprocess
import tempfile
import unittest
import unittest.mock

import smu


class TestSmuWorktreeIgnores(unittest.TestCase):
    def _init_repo(self, tempdir):
        subprocess.run(["git", "-C", tempdir, "init", "-b", "main"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tempdir, "config", "user.email", "test@example.com"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tempdir, "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tempdir, "config", "commit.gpgsign", "false"], check=True, capture_output=True)

    def test_ignored_paths_filter_untracked_local_dotfiles(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._init_repo(tempdir)
            local_dir = os.path.join(tempdir, "dotfiles", "local", "shell")
            os.makedirs(local_dir)
            with open(os.path.join(local_dir, "zshrc"), "w") as f:
                f.write("# local only\n")

            ignored = ("dotfiles/local",)
            self.assertFalse(smu.git_has_worktree_changes(tempdir, ignored_paths=ignored))

    def test_non_ignored_tracked_changes_still_block(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._init_repo(tempdir)
            tracked = os.path.join(tempdir, "README.md")
            with open(tracked, "w") as f:
                f.write("tracked\n")
            subprocess.run(["git", "-C", tempdir, "add", "README.md"], check=True, capture_output=True)
            subprocess.run(["git", "-C", tempdir, "commit", "-m", "init"], check=True, capture_output=True)
            with open(tracked, "a") as f:
                f.write("local edit\n")

            self.assertTrue(smu.git_has_worktree_changes(tempdir, ignored_paths=("dotfiles/local",)))

    def test_local_init_creates_ignored_paths_without_dirtying_blueprint(self):
        with tempfile.TemporaryDirectory() as tempdir:
            home = os.path.join(tempdir, "home")
            blueprint = os.path.join(tempdir, "set-me-up")
            config_dir = os.path.join(home, ".config", "set-me-up")
            os.makedirs(blueprint)
            self._init_repo(blueprint)
            tracked = os.path.join(blueprint, "README.md")
            with open(tracked, "w") as f:
                f.write("clean\n")
            subprocess.run(["git", "-C", blueprint, "add", "README.md"], check=True, capture_output=True)
            subprocess.run(["git", "-C", blueprint, "commit", "-m", "init"], check=True, capture_output=True)

            with unittest.mock.patch.object(smu, "smu_home_dir", blueprint), \
                    unittest.mock.patch.object(smu, "config_dir", config_dir), \
                    unittest.mock.patch.object(smu, "local_config_path", os.path.join(config_dir, "local.env")), \
                    unittest.mock.patch.object(smu, "local_dotfiles_dir", os.path.join(blueprint, "dotfiles", "local")), \
                    unittest.mock.patch.object(smu, "rcrc", os.path.join(blueprint, "dotfiles", "rcrc")):
                exit_code = smu.local_init_command(json_output=True)
                self.assertEqual(exit_code, 0)
                self.assertFalse(smu.git_has_worktree_changes(blueprint))


if __name__ == "__main__":
    unittest.main()
