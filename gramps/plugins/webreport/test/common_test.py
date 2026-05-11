#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Unittest for webreport/common.py module-load resilience."""

import subprocess
import sys
import textwrap
import unittest


# ------------------------------------------------------------
#
# TestCommonImportsWithoutICU
#
# ------------------------------------------------------------
class TestCommonImportsWithoutICU(unittest.TestCase):
    """Regression: ``gramps.plugins.webreport.common`` must import
    cleanly even when neither ``icu`` nor ``PyICU`` is available.

    Historically the module's import-fallback chain only bound
    ``localAlphabeticIndex`` in the *middle* two fallback paths
    (icu-but-no-AlphabeticIndex, PyICU-but-no-AlphabeticIndex).
    The bottom-most fallback — neither icu nor PyICU available —
    was an empty ``pass``, leaving ``localAlphabeticIndex``
    undefined. The module's later ``else`` branch then raised
    ``NameError: name 'localAlphabeticIndex' is not defined`` at
    module load.

    The April 19 plugin-registration smoke test in addons-source CI
    surfaced this through ``TimePedigreeHTML``, which imports
    ``get_gendex_data`` from this module.
    """

    def test_imports_without_icu_or_pyicu(self):
        """Block both ``icu`` and ``PyICU`` in a subprocess and
        verify ``gramps.plugins.webreport.common`` still imports
        with ``AlphabeticIndex`` defined."""
        script = textwrap.dedent("""
            import sys

            # Block both icu bindings before any gramps import so the
            # try/except chain in common.py routes into the bottom
            # ``except ImportError`` branch — the one that used to be
            # an empty ``pass``.
            sys.modules['icu'] = None
            sys.modules['PyICU'] = None

            from gramps.plugins.webreport import common

            # AlphabeticIndex must be a usable class regardless of
            # which fallback branch was taken.
            assert hasattr(common, 'AlphabeticIndex'), (
                "AlphabeticIndex must be defined after module load"
            )
            # HAVE_ICU and HAVE_ALPHABETICINDEX should both be False
            # when both bindings are blocked.
            assert common.HAVE_ICU is False, (
                "HAVE_ICU should be False without icu/PyICU"
            )
            assert common.HAVE_ALPHABETICINDEX is False, (
                "HAVE_ALPHABETICINDEX should be False without icu/PyICU"
            )
            """)
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode,
            0,
            "Importing common.py with icu/PyICU blocked must succeed.\n"
            "stderr:\n%s\nstdout:\n%s" % (result.stderr, result.stdout),
        )


if __name__ == "__main__":
    unittest.main()
