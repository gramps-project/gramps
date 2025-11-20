# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       David Straub
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

"""Unittest for types.py protocols"""

import unittest


class ProtocolTest(unittest.TestCase):
    """Test that actual Gramps classes match their protocol definitions."""

    def test_person_matches_personlike(self):
        """Test that a Person instance matches the PersonLike protocol."""
        from ..lib.person import Person
        from ..types import PersonLike
        
        person = Person()
        self.assertIsInstance(person, PersonLike)

    def test_person_datadict_matches_personlike(self):
        """Test that a DataDict from Person has PersonLike attributes."""
        from ..lib.person import Person
        from ..lib.json_utils import object_to_data
        from ..types import PersonLike
        
        person = Person()
        data_dict: PersonLike = object_to_data(person)

    def test_family_matches_familylike(self):
        """Test that a Family instance matches the FamilyLike protocol."""
        from ..lib.family import Family
        from ..types import FamilyLike
        
        family = Family()
        self.assertIsInstance(family, FamilyLike)

    def test_family_datadict_matches_familylike(self):
        """Test that a DataDict from Family has FamilyLike attributes."""
        from ..lib.family import Family
        from ..lib.json_utils import object_to_data
        from ..types import FamilyLike
        
        family = Family()
        data_dict: FamilyLike = object_to_data(family)

    def test_event_matches_eventlike(self):
        """Test that an Event instance matches the EventLike protocol."""
        from ..lib.event import Event
        from ..types import EventLike
        
        event = Event()
        self.assertIsInstance(event, EventLike)

    def test_event_datadict_matches_eventlike(self):
        """Test that a DataDict from Event has EventLike attributes."""
        from ..lib.event import Event
        from ..lib.json_utils import object_to_data
        from ..types import EventLike
        
        event = Event()
        data_dict: EventLike = object_to_data(event)

    def test_source_matches_sourcelike(self):
        """Test that a Source instance matches the SourceLike protocol."""
        from ..lib.src import Source
        from ..types import SourceLike
        
        source = Source()
        self.assertIsInstance(source, SourceLike)

    def test_source_datadict_matches_sourcelike(self):
        """Test that a DataDict from Source has SourceLike attributes."""
        from ..lib.src import Source
        from ..lib.json_utils import object_to_data
        from ..types import SourceLike
        
        source = Source()
        data_dict: SourceLike = object_to_data(source)

    def test_citation_matches_citationlike(self):
        """Test that a Citation instance matches the CitationLike protocol."""
        from ..lib.citation import Citation
        from ..types import CitationLike
        
        citation = Citation()
        self.assertIsInstance(citation, CitationLike)

    def test_citation_datadict_matches_citationlike(self):
        """Test that a DataDict from Citation has CitationLike attributes."""
        from ..lib.citation import Citation
        from ..lib.json_utils import object_to_data
        from ..types import CitationLike
        
        citation = Citation()
        data_dict: CitationLike = object_to_data(citation)

    def test_media_matches_medialike(self):
        """Test that a Media instance matches the MediaLike protocol."""
        from ..lib.media import Media
        from ..types import MediaLike
        
        media = Media()
        self.assertIsInstance(media, MediaLike)

    def test_media_datadict_matches_medialike(self):
        """Test that a DataDict from Media has MediaLike attributes."""
        from ..lib.media import Media
        from ..lib.json_utils import object_to_data
        from ..types import MediaLike
        
        media = Media()
        data_dict: MediaLike = object_to_data(media)

    def test_place_matches_placelike(self):
        """Test that a Place instance matches the PlaceLike protocol."""
        from ..lib.place import Place
        from ..types import PlaceLike
        
        place = Place()
        self.assertIsInstance(place, PlaceLike)

    def test_place_datadict_matches_placelike(self):
        """Test that a DataDict from Place has PlaceLike attributes."""
        from ..lib.place import Place
        from ..lib.json_utils import object_to_data
        from ..types import PlaceLike
        
        place = Place()
        data_dict: PlaceLike = object_to_data(place)

    def test_repository_matches_repositorylike(self):
        """Test that a Repository instance matches the RepositoryLike protocol."""
        from ..lib.repo import Repository
        from ..types import RepositoryLike
        
        repository = Repository()
        self.assertIsInstance(repository, RepositoryLike)

    def test_repository_datadict_matches_repositorylike(self):
        """Test that a DataDict from Repository has RepositoryLike attributes."""
        from ..lib.repo import Repository
        from ..lib.json_utils import object_to_data
        from ..types import RepositoryLike
        
        repository = Repository()
        data_dict: RepositoryLike = object_to_data(repository)

    def test_note_matches_notelike(self):
        """Test that a Note instance matches the NoteLike protocol."""
        from ..lib.note import Note
        from ..types import NoteLike
        
        note = Note()
        self.assertIsInstance(note, NoteLike)

    def test_note_datadict_matches_notelike(self):
        """Test that a DataDict from Note has NoteLike attributes."""
        from ..lib.note import Note
        from ..lib.json_utils import object_to_data
        from ..types import NoteLike
        
        note = Note()
        data_dict: NoteLike = object_to_data(note)

    def test_tag_matches_taglike(self):
        """Test that a Tag instance matches the TagLike protocol."""
        from ..lib.tag import Tag
        from ..types import TagLike
        
        tag = Tag()
        self.assertIsInstance(tag, TagLike)

    def test_tag_datadict_matches_taglike(self):
        """Test that a DataDict from Tag has TagLike attributes."""
        from ..lib.tag import Tag
        from ..lib.json_utils import object_to_data
        from ..types import TagLike
        
        tag = Tag()
        data_dict: TagLike = object_to_data(tag)

    def test_date_matches_datelike(self):
        """Test that a Date instance matches the DateLike protocol."""
        from ..lib.date import Date
        from ..types import DateLike
        
        date = Date()
        self.assertIsInstance(date, DateLike)

    def test_name_matches_namelike(self):
        """Test that a Name instance matches the NameLike protocol."""
        from ..lib.name import Name
        from ..types import NameLike
        
        name = Name()
        self.assertIsInstance(name, NameLike)

    def test_grampstype_matches_grampstypelike(self):
        """Test that GrampsType instances match the GrampsTypeLike protocol."""
        from ..lib.grampstype import GrampsType
        from ..lib.nametype import NameType
        from ..lib.eventtype import EventType
        from ..types import GrampsTypeLike
        
        # Test with base GrampsType and subclasses
        gt = GrampsType()
        self.assertIsInstance(gt, GrampsTypeLike)
        
        nt = NameType()
        self.assertIsInstance(nt, GrampsTypeLike)
        
        et = EventType()
        self.assertIsInstance(et, GrampsTypeLike)


if __name__ == "__main__":
    unittest.main()
