#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
Tests for the referents utilities in gramps.gen.utils.db.
"""

import unittest

from ...db import DbTxn
from ...db.utils import make_database
from ...lib import (
    Citation,
    DNAMatch,
    DNATest,
    Media,
    MediaRef,
    Note,
    Person,
    Source,
)
from ..db import get_citation_referents, get_media_referents, get_note_referents


def _make_db():
    """Create and return a fresh in-memory SQLite database."""
    db = make_database("sqlite")
    db.load(":memory:")
    return db


def _attach(obj, citation_handle, note_handle, media_handle):
    """Attach a citation, a note and a media reference to obj."""
    obj.add_citation(citation_handle)
    obj.add_note(note_handle)
    media_ref = MediaRef()
    media_ref.set_reference_handle(media_handle)
    obj.add_media_reference(media_ref)


class ReferentsTest(unittest.TestCase):
    """
    A citation, note and media object referenced from every primary type are
    reported by the matching get_*_referents helper.
    """

    @classmethod
    def setUpClass(cls):
        cls.db = _make_db()
        with DbTxn("build", cls.db) as trans:
            source = Source()
            cls.db.add_source(source, trans)

            citation = Citation()
            citation.set_reference_handle(source.handle)
            cls.citation_handle = cls.db.add_citation(citation, trans)

            note = Note("a note")
            cls.note_handle = cls.db.add_note(note, trans)

            media = Media()
            media.set_path("/dev/null")
            cls.media_handle = cls.db.add_media(media, trans)

            person = Person()
            _attach(person, cls.citation_handle, cls.note_handle, cls.media_handle)
            cls.person_handle = cls.db.add_person(person, trans)

            dnatest = DNATest()
            _attach(dnatest, cls.citation_handle, cls.note_handle, cls.media_handle)
            cls.dnatest_handle = cls.db.add_dnatest(dnatest, trans)

            dnamatch = DNAMatch()
            _attach(dnamatch, cls.citation_handle, cls.note_handle, cls.media_handle)
            cls.dnamatch_handle = cls.db.add_dnamatch(dnamatch, trans)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_citation_referents(self):
        """DNATest and DNAMatch appear in the citation referent lists."""
        refs = get_citation_referents(self.citation_handle, self.db)
        # Person, Family, Event, Place, Source, Media, Repository,
        # DNATest, DNAMatch
        self.assertEqual(len(refs), 9)
        self.assertEqual(refs[0], [self.person_handle])
        self.assertEqual(refs[7], [self.dnatest_handle])
        self.assertEqual(refs[8], [self.dnamatch_handle])

    def test_media_referents(self):
        """DNATest and DNAMatch appear in the media referent lists."""
        refs = get_media_referents(self.media_handle, self.db)
        # Person, Family, Event, Place, Source, Citation, DNATest, DNAMatch
        self.assertEqual(len(refs), 8)
        self.assertEqual(refs[0], [self.person_handle])
        self.assertEqual(refs[6], [self.dnatest_handle])
        self.assertEqual(refs[7], [self.dnamatch_handle])

    def test_note_referents(self):
        """DNATest and DNAMatch appear in the note referent lists."""
        refs = get_note_referents(self.note_handle, self.db)
        # Person, Family, Event, Place, Source, Citation, Media, Repository,
        # DNATest, DNAMatch
        self.assertEqual(len(refs), 10)
        self.assertEqual(refs[0], [self.person_handle])
        self.assertEqual(refs[8], [self.dnatest_handle])
        self.assertEqual(refs[9], [self.dnamatch_handle])


if __name__ == "__main__":
    unittest.main()
