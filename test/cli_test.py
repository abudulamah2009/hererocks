#!/usr/bin/env python

import os
import shutil
import subprocess
import time
import unittest
import sys


skip_if_win = unittest.skipIf(sys.platform.startswith("win"), "requires POSIX")


class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.check_call(["coverage", "erase"])

    def setUp(self):
        if os.name == "nt":
            # On Windows tests randomly fail here with errors such as 'can not remove here\bin: directory not empty'.
            # Supposedly this happens because a file in the directory is still open, and on NFS
            # deleting an open file leaves a file in the same directory. Waiting before attempting
            # to remove directories seems to help.
            time.sleep(1)

        for subdir in ["here", "builds"]:
            if os.path.exists(os.path.join("test", subdir)):
                shutil.rmtree(os.path.join("test", subdir))

    def assertSuccess(self, args, expected_output_lines=None, from_prefix=True):
        if from_prefix:
            args[0] = os.path.join("test", "here", "bin", args[0])

            if os.name == "nt" and not os.path.exists(args[0]) and not os.path.exists(args[0] + ".exe"):
                args[0] += ".bat"

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = process.communicate()[0]

        if process.returncode != 0:
            raise AssertionError("Error running command '{}': code {}, output:\n{}".format(
                " ".join(args), process.returncode, output))

        if expected_output_lines is not None:
            actual_output_lines = output.splitlines()

            for expected_output_line in expected_output_lines:
                expected_output_line = expected_output_line.encode("UTF-8")

                if not any(expected_output_line in actual_output_line for actual_output_line in actual_output_lines):
                    raise AssertionError("Expected to see '{}' in output of command '{}', got output:\n{}".format(
                        expected_output_line, " ".join(args), output))

    def assertHererocksSuccess(self, args, expected_output_lines=None, location="here"):
        self.assertSuccess([
            "coverage", "run", "-a",
            "hererocks.py", os.path.join("test", location)] + args, expected_output_lines, from_prefix=False)

    def test_install_latest_lua_with_luarocks_from_git(self):
        self.assertHererocksSuccess(["--lua", "latest", "--luarocks", "https://github.com/luarocks/luarocks@f162d2ec"])
        self.assertSuccess(["luarocks", "--version"])

if __name__ == '__main__':
    unittest.main(verbosity=2)
