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

"""Mantis 8362 — GEDCOM export of an event place must not depend on the
place TYPE, and an accented place title must round-trip as UTF-8.

Reported on 4.1.1 (2015): the marriage ``PLAC`` line a GEDCOM export
produced differed depending on the place type ("Città" vs "Town"), which
the reporter blamed on the accented "à".  Under the pre-5.0 place model
the exporter mapped place parts into the GEDCOM ADDR/CITY structure by
matching the (translated) place type against English "City"/"Town", and
the Python-2 handling of the accented character interacted with that
mapping.

The 5.0 place-model rewrite removed the type→ADDR/CITY mapping for event
places: :meth:`GedcomWriter._place` now emits ``PLAC = <display name>``
(plus MAP / notes) independent of the place type, and Python-3 / UTF-8
carries the accent intact.  This test pins that behaviour:

  * an accented place title round-trips as UTF-8 in the ``PLAC`` line, and
  * the ``PLAC`` output is byte-identical whether the place type is the
    accented "Città" or the English "Town" — the type no longer drives
    the place export.

Import-light: the test stubs the two ``gramps.gui`` symbols that
``exportgedcom`` (and the db plugin layer it pulls) reference at import
time, so it runs headless (no display / GTK widget realisation) while
still exercising the real production export path
(:meth:`GedcomWriter._place` / ``_writeln`` / the place displayer)."""

import os
import sys
import tempfile
import types
import unittest

# ---------------------------------------------------------------------------
# Headless import shims.
#
# ``exportgedcom`` does ``from gramps.gui.plug.export import WriterOptionBox``
# at module load (kept "even though not obviously used"), and the db plugin
# layer pulled in by ``gramps.gen.db`` imports ``gramps.gui.dbguielement``.
# Neither symbol is used on the export path under test, but importing the real
# ``gramps.gui`` package realises GTK widget classes, which is exactly what
# crashes a no-display unit runner.  Register lightweight stand-ins BEFORE the
# gramps imports so the unit stays import-light yet drives the real writer.
# ---------------------------------------------------------------------------
for _name in (
    "gramps.gui",
    "gramps.gui.plug",
    "gramps.gui.plug.export",
    "gramps.gui.dbguielement",
):
    if _name not in sys.modules:
        _mod = types.ModuleType(_name)
        _mod.__path__ = []  # advertise as a package so submodule imports resolve
        sys.modules[_name] = _mod


class _WriterOptionBox:  # stand-in for gramps.gui.plug.export.WriterOptionBox
    pass


class _DbGUIElement:  # stand-in for gramps.gui.dbguielement.DbGUIElement
    pass


sys.modules["gramps.gui.plug.export"].WriterOptionBox = _WriterOptionBox
sys.modules["gramps.gui.dbguielement"].DbGUIElement = _DbGUIElement

from gramps.cli.user import User
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (
    Event,
    EventRef,
    EventType,
    Family,
    Place,
    PlaceName,
    PlaceType,
)
from gramps.plugins.export.exportgedcom import GedcomWriter

# Accented marriage-place title — the "à"/"ì" the 2015 reporter blamed.
PLACE_TITLE = "Forlì à la Côte"
# UTF-8 byte sequences for the accented characters, asserted explicitly so a
# regression to a non-UTF-8 / mangled encoding is caught.
ACCENT_BYTES = (
    "ì".encode("utf-8"),  # b"\xc3\xac"
    "à".encode("utf-8"),  # b"\xc3\xa0"
    "ô".encode("utf-8"),  # b"\xc3\xb4"
)


def _export_marriage_place(place_type):
    """Build a one-family tree whose marriage event has a place titled
    ``PLACE_TITLE`` and typed ``place_type``, export it to GEDCOM, and return
    ``(raw_bytes, [PLAC lines])``."""
    db = make_database("sqlite")
    db.load(":memory:")

    place = Place()
    name = PlaceName()
    name.set_value(PLACE_TITLE)
    place.set_name(name)
    place.set_title(PLACE_TITLE)
    place.set_type(PlaceType(place_type))

    event = Event()
    event.set_type(EventType(EventType.MARRIAGE))

    family = Family()

    with DbTxn("8362 fixture", db) as trans:
        place_handle = db.add_place(place, trans)
        db.commit_place(place, trans)
        event.set_place_handle(place_handle)
        event_handle = db.add_event(event, trans)
        db.commit_event(event, trans)
        eref = EventRef()
        eref.set_reference_handle(event_handle)
        family.add_event_ref(eref)
        db.add_family(family, trans)
        db.commit_family(family, trans)

    fd, path = tempfile.mkstemp(suffix=".ged")
    os.close(fd)
    try:
        GedcomWriter(db, User()).write_gedcom_file(path)
        with open(path, "rb") as handle:
            raw = handle.read()
    finally:
        os.unlink(path)

    plac_lines = [line for line in raw.decode("utf-8").splitlines() if " PLAC " in line]
    return raw, plac_lines


class GedcomExportPlaceTypeAccentTest(unittest.TestCase):
    def test_accented_title_roundtrips_as_utf8(self):
        raw, plac_lines = _export_marriage_place("Città")
        self.assertEqual(
            plac_lines,
            ["2 PLAC " + PLACE_TITLE],
            "marriage place must export as a single PLAC line carrying the "
            "accented title intact",
        )
        # The file is valid UTF-8 and the accented bytes survive verbatim.
        for accent in ACCENT_BYTES:
            self.assertIn(accent, raw)

    def test_place_type_does_not_drive_place_export(self):
        raw_citta, plac_citta = _export_marriage_place("Città")
        raw_town, plac_town = _export_marriage_place(PlaceType.TOWN)
        # Same title, only the type differs → the PLAC output is identical.
        self.assertEqual(plac_citta, plac_town)
        self.assertEqual(plac_citta, ["2 PLAC " + PLACE_TITLE])
        # And not via an empty/missing line on either side.
        self.assertTrue(plac_citta)


if __name__ == "__main__":
    unittest.main()
