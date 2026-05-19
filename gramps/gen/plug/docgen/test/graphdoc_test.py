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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Unit tests for ``gramps.gen.plug.docgen.graphdoc``.

Bug 0006556: report generation through the graphviz pipeline used to
fail silently when the output file could not be written (typically
because another process held a lock on it, but also under
permission-denied / disk-full / missing-binary). The fix routes every
``os.system`` call in graphdoc.py through ``_check_rc``, which raises
:class:`ReportError` on a non-zero return code so the user gets the
same "Could not create %s" message they already see from the other
report backends.

The 11 callsites are exercised indirectly here by verifying that
``_check_rc`` raises with the canonical message; a separate static
assertion guards against new ``os.system`` calls slipping back in
unchecked.
"""

import re
import unittest

from gramps.gen.errors import ReportError
from gramps.gen.plug.docgen import graphdoc
from gramps.gen.plug.docgen.graphdoc import _check_rc


class CheckRcTest(unittest.TestCase):
    """``_check_rc`` is the single funnel that turns a non-zero exit
    into a :class:`ReportError`."""

    def test_zero_rc_is_silent(self):
        # Returning None (i.e. no exception) is the contract on success.
        self.assertIsNone(_check_rc(0, "/tmp/out.svg"))

    def test_nonzero_rc_raises_report_error(self):
        with self.assertRaises(ReportError):
            _check_rc(1, "/tmp/out.svg")

    def test_nonzero_rc_message_names_the_target(self):
        target = "/tmp/locked-output.pdf"
        with self.assertRaises(ReportError) as ctx:
            _check_rc(127, target)
        # ReportError exposes the message via ``.value`` and ``str()``;
        # match the "Could not create <file>" pattern used uniformly
        # across the other docgen backends (rtfdoc, svgdrawdoc, odfdoc).
        message = str(ctx.exception)
        self.assertIn("Could not create", message)
        self.assertIn(target, message)

    def test_any_nonzero_rc_raises(self):
        # POSIX exit-status encodings can produce values other than 1
        # (e.g. os.system's high-byte exit code, or signal-encoded
        # negatives). Anything non-zero must raise.
        for rc in (1, 2, 127, 256, -1, 32512):
            with self.subTest(rc=rc):
                with self.assertRaises(ReportError):
                    _check_rc(rc, "/tmp/out.png")


class GraphdocStaticAssertions(unittest.TestCase):
    """Static checks that guard the wiring of ``_check_rc`` across
    every ``os.system`` callsite in graphdoc.py."""

    @classmethod
    def setUpClass(cls):
        with open(graphdoc.__file__, encoding="utf-8") as fh:
            cls.source = fh.read()

    def test_no_bare_os_system_callsites(self):
        """Every ``os.system(...)`` callsite must capture its return
        code into ``rc`` (the convention used by the fix). A bare
        ``os.system(command)`` call would silently regress bug 6556.

        Matches statements of the form ``    os.system(...)`` -- i.e.
        without an ``rc =`` assignment on the same line.
        """
        bare = re.findall(
            r"^[ \t]+os\.system\(",
            self.source,
            flags=re.MULTILINE,
        )
        self.assertEqual(
            bare,
            [],
            "graphdoc.py contains bare os.system(...) callsites; every "
            "invocation must capture rc and pass it to _check_rc",
        )

    def test_every_rc_assignment_is_checked(self):
        """Every ``rc = os.system(...)`` must be followed eventually
        by a ``_check_rc(rc, ...)`` call in the same function.

        Approximate check: the number of ``rc = os.system`` assignments
        must equal the number of ``_check_rc(rc,`` invocations.
        """
        assigns = re.findall(r"rc\s*=\s*os\.system\(", self.source)
        checks = re.findall(r"_check_rc\(rc,", self.source)
        self.assertEqual(
            len(assigns),
            len(checks),
            f"{len(assigns)} `rc = os.system` assignments but "
            f"{len(checks)} `_check_rc(rc, ...)` checks -- bug 6556 "
            "guard slipped",
        )


if __name__ == "__main__":
    unittest.main()
