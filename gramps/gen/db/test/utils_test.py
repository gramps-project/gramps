#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  David Straub
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
Unittest for gramps.gen.db.utils.
"""

# ------------------------
# Python modules
# ------------------------
import os
import tempfile
import unittest

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.config import config
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import import_as_dict, make_database
from gramps.gen.lib import Family, Person
from gramps.gen.user import User
from gramps.plugins.export.exportxml import export_data


# ------------------------------------------------------------
#
# ImportAsDictTest
#
# ------------------------------------------------------------
class ImportAsDictTest(unittest.TestCase):
    """
    Test that import_as_dict keeps Gramps IDs as they are in the file.
    """

    def setUp(self) -> None:
        """
        Export a tree with pre-6.1 style IDs and pin the configured prefixes
        to the zero-padded 6.1 defaults.
        """
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.filename = os.path.join(self.tmpdir.name, "export.gramps")

        path = os.path.join(self.tmpdir.name, "db")
        os.makedirs(path)
        db = make_database("sqlite")
        db.load(path)
        with DbTxn("Add objects", db) as trans:
            person = Person()
            person.set_gramps_id("I0001")
            db.add_person(person, trans)
            family = Family()
            family.set_gramps_id("F0001")
            db.add_family(family, trans)
        self.assertTrue(export_data(db, self.filename, User()))
        db.close()

        for key, value in (
            ("preferences.iprefix", "I%05d"),
            ("preferences.fprefix", "F%05d"),
        ):
            self.addCleanup(config.set, key, config.get(key))
            config.set(key, value)

    def test_ids_kept_verbatim_by_default(self) -> None:
        """
        Without explicit prefixes, IDs must not be reformatted.
        """
        db = import_as_dict(self.filename, User())
        assert db is not None
        self.assertEqual(
            [p.gramps_id for p in db.iter_people()],
            ["I0001"],
        )
        self.assertEqual(
            [f.gramps_id for f in db.iter_families()],
            ["F0001"],
        )
        db.close()

    def test_explicit_prefix_reformats_ids(self) -> None:
        """
        An explicitly passed zero-padded prefix still reformats IDs.
        """
        db = import_as_dict(self.filename, User(), person_prefix="I%05d")
        assert db is not None
        self.assertEqual(
            [p.gramps_id for p in db.iter_people()],
            ["I00001"],
        )
        db.close()


if __name__ == "__main__":
    unittest.main()
