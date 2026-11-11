#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Unit test verifying repository compliance with .gitattributes rules.
"""

# ------------------------
# Python modules
# ------------------------
from __future__ import annotations

import os
import subprocess
import unittest

# ------------------------
# Gramps modules
# ------------------------

# ------------------------
# Gramps specific
# ------------------------


# ------------------------------------------------------------
#
# GitAttributesTest
#
# ------------------------------------------------------------
class GitAttributesTest(unittest.TestCase):
    """
    Test suite verifying tracked files comply with .gitattributes in the branch.
    """

    repo_root: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Locate the git repository root. Skip tests if not running in git.

        :returns: None
        :rtype: None
        """
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )
        except (FileNotFoundError, OSError):
            raise unittest.SkipTest("git executable not found")

        if res.returncode != 0 or not res.stdout.strip():
            raise unittest.SkipTest("Not running inside a git repository")

        cls.repo_root = os.path.normpath(res.stdout.strip())

    @staticmethod
    def _evaluate_compliance(i_eol: str, attrs: list[str]) -> str | None:
        """
        Determine whether index line endings violate the given git attributes.

        :param i_eol: Line ending in git index (e.g., 'i/lf', 'i/crlf').
        :type i_eol: str
        :param attrs: List of attributes parsed from git ls-files --eol.
        :type attrs: list[str]
        :returns: Error message describing the violation, or None if compliant.
        :rtype: str | None
        """
        if i_eol in ("i/none", "i/-text"):
            return None

        if "-text" in attrs or "binary" in attrs:
            return None

        requires_crlf = "eol=crlf" in attrs
        requires_lf = "eol=lf" in attrs or (
            any(a in ("text", "text=auto") for a in attrs) and not requires_crlf
        )

        if requires_lf and i_eol in ("i/crlf", "i/mixed"):
            return (
                f"requires LF line endings per attributes ({' '.join(attrs)}), "
                f"but repository index has {i_eol}"
            )

        if requires_crlf and i_eol == "i/lf":
            return (
                f"requires CRLF line endings per attributes ({' '.join(attrs)}), "
                f"but repository index has {i_eol}"
            )

        return None

    def _get_tracked_eol_info(
        self,
    ) -> list[tuple[str, str, list[str], str]]:
        """
        Query git ls-files --eol for all tracked files.

        :returns: List of tuples (i_eol, w_eol, attrs_list, file_path).
        :rtype: list[tuple[str, str, list[str], str]]
        """
        try:
            res = subprocess.run(
                ["git", "ls-files", "--eol"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            self.skipTest(f"Failed to run 'git ls-files --eol': {exc}")

        entries: list[tuple[str, str, list[str], str]] = []
        for line in res.stdout.splitlines():
            if not line or "\t" not in line:
                continue
            meta, path = line.split("\t", 1)
            parts = meta.split(None, 2)
            if len(parts) < 3:
                continue
            i_eol = parts[0]
            w_eol = parts[1]
            attr_part = parts[2].strip()
            attr_str = (
                attr_part[len("attr/") :] if attr_part.startswith("attr/") else ""
            )
            attrs = attr_str.split()
            entries.append((i_eol, w_eol, attrs, path))

        return entries

    def test_gitattributes_file_exists(self) -> None:
        """
        Verify that a .gitattributes file exists at the repository root.

        :returns: None
        :rtype: None
        """
        gitattributes_path = os.path.join(self.repo_root, ".gitattributes")
        self.assertTrue(
            os.path.isfile(gitattributes_path),
            f".gitattributes file not found at {gitattributes_path}",
        )

    def test_tracked_files_comply_with_gitattributes(self) -> None:
        """
        Verify all tracked files comply with the active .gitattributes rules.

        :returns: None
        :rtype: None
        """
        entries = self._get_tracked_eol_info()
        self.assertGreater(len(entries), 0, "No tracked files found by git ls-files")

        violations: list[str] = []
        for i_eol, _w_eol, attrs, path in entries:
            err = self._evaluate_compliance(i_eol, attrs)
            if err:
                violations.append(f"{path}: {err}")

        if violations:
            msg = (
                f"Found {len(violations)} files violating .gitattributes rules:\n"
                + "\n".join(f"  - {v}" for v in violations)
            )
            self.fail(msg)

    def test_compliance_evaluator(self) -> None:
        """
        Verify the compliance evaluation logic with synthetic test cases.

        :returns: None
        :rtype: None
        """
        self.assertIsNone(self._evaluate_compliance("i/lf", ["eol=lf"]))
        self.assertIsNone(self._evaluate_compliance("i/none", ["eol=lf"]))
        self.assertIsNone(self._evaluate_compliance("i/-text", ["eol=lf"]))
        self.assertIsNone(self._evaluate_compliance("i/crlf", ["-text", "eol=lf"]))
        self.assertIsNone(self._evaluate_compliance("i/crlf", ["binary"]))
        self.assertIsNone(self._evaluate_compliance("i/crlf", []))
        self.assertIsNone(self._evaluate_compliance("i/crlf", ["text", "eol=crlf"]))

        self.assertIsNotNone(self._evaluate_compliance("i/crlf", ["eol=lf"]))
        self.assertIsNotNone(self._evaluate_compliance("i/mixed", ["eol=lf"]))
        self.assertIsNotNone(self._evaluate_compliance("i/crlf", ["text"]))
        self.assertIsNotNone(self._evaluate_compliance("i/crlf", ["text=auto"]))
        self.assertIsNotNone(self._evaluate_compliance("i/lf", ["text", "eol=crlf"]))


if __name__ == "__main__":
    unittest.main()
