#
# Gramps - a GTK+/GNOME based genealogy program
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

"""Mantis 14014 — XML importer must not crash on a compound date with an
empty bound.

A Gramps XML backup can legitimately carry a ``<daterange>`` / ``<datespan>``
whose ``start`` or ``stop`` attribute is the empty string (e.g. a "Range"
date entered with only the begin date filled in, exported as
``<daterange start="1911-09-01" stop=""/>``).  Before commit 1c411ea3ed
("Catch IndexError in importxml"), ``GrampsParser.start_compound_date`` did
``if stop[0] == "-":`` with no guard, so an empty bound raised
``IndexError: string index out of range`` and aborted the *entire* import.

The fix guards each bound (``if stop and stop[0] == "-":`` etc.,
``gramps/plugins/importer/importxml.py`` lines 2553 / 2573 / 2658) so the
import completes: the reported case (empty ``stop``) imports as the
corresponding open-ended range, and the empty-``start`` case is handled
gracefully (Gramps' data model rejects an open lower bound, so it degrades
to a text-only date preserving the XML) — either way, no ``IndexError``.

This regression test drives the real production import path via
:func:`gramps.gen.db.utils.import_as_dict`."""

import os
import tempfile
import time
import unittest

from gramps.cli.user import User as CliUser
from gramps.gen.db.utils import import_as_dict
from gramps.gen.lib import Date
from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.version import VERSION


def _gramps_xml(event_date_xml):
    """Return a minimal, well-formed .gramps document carrying a single
    Residence event whose date is the supplied ``<daterange>`` /
    ``<datespan>`` element."""
    created = time.localtime(time.time())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<database xmlns="http://gramps-project.org/xml/%s/">\n'
        "<header>\n"
        '<created date="%04d-%02d-%02d" version="%s"/>\n'
        "<researcher/>\n"
        "</header>\n"
        "<events>\n"
        '<event handle="_e0000" id="E0000">\n'
        "<type>Residence</type>\n"
        "%s\n"
        "</event>\n"
        "</events>\n"
        "</database>\n"
        % (
            GRAMPS_XML_VERSION,
            created[0],
            created[1],
            created[2],
            VERSION,
            event_date_xml,
        )
    )


class ImportXmlEmptyBoundDateTest(unittest.TestCase):
    """A compound date with an empty bound must import without IndexError."""

    def _import(self, event_date_xml):
        fd, path = tempfile.mkstemp(suffix=".gramps", text=True)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(_gramps_xml(event_date_xml))
            # Pre-fix this raised IndexError out of start_compound_date and
            # aborted the import; import_as_dict would propagate it.
            db = import_as_dict(path, CliUser())
        finally:
            os.unlink(path)
        self.assertIsNotNone(db, "import_as_dict returned None — import failed")
        handles = list(db.get_event_handles())
        self.assertEqual(len(handles), 1, "expected exactly one imported event")
        return db.get_event_from_handle(handles[0]).get_date_object()

    def test_daterange_empty_stop_imports_as_open_ended_range(self):
        # The reported case: <daterange start="1911-09-01" stop=""/>.
        date = self._import('<daterange start="1911-09-01" stop=""/>')
        self.assertEqual(date.get_modifier(), Date.MOD_RANGE)
        self.assertTrue(date.is_compound())
        # Begin bound preserved ...
        self.assertEqual(
            (date.get_year(), date.get_month(), date.get_day()), (1911, 9, 1)
        )
        # ... stop bound open-ended (unset), not crashed, not text-only.
        self.assertEqual(date.get_stop_year(), 0)
        self.assertEqual(date.get_text(), "")

    def test_datespan_empty_stop_imports_as_open_ended_span(self):
        date = self._import('<datespan start="1911-09-01" stop=""/>')
        self.assertEqual(date.get_modifier(), Date.MOD_SPAN)
        self.assertTrue(date.is_compound())
        self.assertEqual(
            (date.get_year(), date.get_month(), date.get_day()), (1911, 9, 1)
        )
        self.assertEqual(date.get_stop_year(), 0)
        self.assertEqual(date.get_text(), "")

    def test_daterange_empty_start_imports_without_indexerror(self):
        # Empty begin bound: pre-fix raised IndexError at start[0]. Post-fix
        # the import completes; Gramps' data model rejects an open lower
        # bound, so the date degrades to a text-only date preserving the XML.
        date = self._import('<daterange start="" stop="1900"/>')
        self.assertEqual(date.get_modifier(), Date.MOD_TEXTONLY)
        self.assertIn('start=""', date.get_text())


if __name__ == "__main__":
    unittest.main()
