#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Ian Davis
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

"""Validates sample Gramps XML files against the current RelaxNG schema."""

import gzip
import os
import unittest

from gramps.gen.const import ROOT_DIR

try:
    from lxml import etree as _etree

    _LXML_AVAILABLE = True
except ImportError:
    _LXML_AVAILABLE = False

_SRC_ROOT = os.path.dirname(ROOT_DIR)
_RNG_PATH = os.path.join(_SRC_ROOT, "data", "grampsxml.rng")
_EXAMPLE_DIR = os.path.join(_SRC_ROOT, "example", "gramps")


def _read_gramps(path):
    """Return the raw bytes of a .gramps file, decompressing if gzipped."""
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        with gzip.open(path, "rb") as fh:
            return fh.read()
    with open(path, "rb") as fh:
        return fh.read()


def _all_sample_files():
    """Return sorted paths of all *.gramps files in example/gramps/."""
    return [
        os.path.join(_EXAMPLE_DIR, name)
        for name in sorted(os.listdir(_EXAMPLE_DIR))
        if name.endswith(".gramps")
    ]


@unittest.skipUnless(_LXML_AVAILABLE, "lxml not available")
class TestSampleFilesValid(unittest.TestCase):
    """Validate all example/*.gramps files against the current RelaxNG schema."""

    @classmethod
    def setUpClass(cls):
        rng_doc = _etree.parse(_RNG_PATH)
        cls.schema = _etree.RelaxNG(rng_doc)

    def _validate(self, path):
        parser = _etree.XMLParser(
            load_dtd=False, no_network=True, resolve_entities=False
        )
        data = _read_gramps(path)
        doc = _etree.fromstring(data, parser=parser).getroottree()
        if not self.schema.validate(doc):
            errors = "\n".join(str(e) for e in self.schema.error_log)
            self.fail(
                "%s failed RelaxNG validation:\n%s" % (os.path.basename(path), errors)
            )

    def test_sample_files_are_valid(self):
        for path in _all_sample_files():
            with self.subTest(file=os.path.basename(path)):
                self._validate(path)


if __name__ == "__main__":
    unittest.main()
