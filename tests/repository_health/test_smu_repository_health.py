#!/usr/bin/env python3

import os
import subprocess
import tempfile
import unittest

import smu


def _init_git_repo_with_commit(path, filename="README.md", content="seed"):
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", path], check=True)
    subprocess.run(["git", "-C", path, "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", path, "config", "user.name", "Test"], check=True)
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)
    subprocess.run(["git", "-C", path, "add", filename], check=True)
    subprocess.run(["git", "-C", path, "commit", "--quiet", "-m", "seed"], check=True)


class TestSmuRepositoryHealth(unittest.TestCase):
    def test_git_upstream_sync_treats_pinned_submodule_as_current(self):
        with tempfile.TemporaryDirectory() as tempdir:
            sub_repo = os.path.join(tempdir, "sub")
            _init_git_repo_with_commit(sub_repo)

            superproject = os.path.join(tempdir, "super")
            _init_git_repo_with_commit(superproject)
            subprocess.run(
                ["git", "-C", superproject, "-c", "protocol.file.allow=always",
                 "submodule", "add", "--quiet", sub_repo, "mysub"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", superproject, "commit", "--quiet", "-m", "add submodule"],
                check=True,
            )

            # A fresh clone + `submodule update --init` is how installer
            # checkouts actually get created, and always leaves the
            # submodule on a detached HEAD pinned to the recorded commit.
            clone = os.path.join(tempdir, "clone")
            subprocess.run(["git", "clone", "--quiet", superproject, clone], check=True)
            subprocess.run(
                ["git", "-C", clone, "-c", "protocol.file.allow=always",
                 "submodule", "update", "--init", "--quiet"],
                check=True,
            )

            result = smu.git_upstream_sync(os.path.join(clone, "mysub"))

            self.assertIsNone(result["branch"])
            self.assertEqual(result["status"], "current")

    def test_git_upstream_sync_still_flags_plain_detached_checkout(self):
        with tempfile.TemporaryDirectory() as tempdir:
            repo = os.path.join(tempdir, "plain")
            _init_git_repo_with_commit(repo)
            first_sha = subprocess.run(
                ["git", "-C", repo, "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()

            with open(os.path.join(repo, "README.md"), "a") as f:
                f.write("\nmore")
            subprocess.run(["git", "-C", repo, "commit", "--quiet", "-am", "second"], check=True)
            subprocess.run(["git", "-C", repo, "checkout", "--quiet", first_sha], check=True)

            result = smu.git_upstream_sync(repo)

            self.assertIsNone(result["branch"])
            self.assertEqual(result["status"], "detached")


if __name__ == "__main__":
    unittest.main()
