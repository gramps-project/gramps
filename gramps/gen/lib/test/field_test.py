#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Gramps Development Team
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

""" Tests for using database fields """

import unittest

from gramps.gen.db import make_database

from  ..import (Person, Surname, Name, NameType, Family, FamilyRelType,
                Event, EventType, Source, Place, PlaceName, Citation, Date,
                Repository, RepositoryType, Media, Note, NoteType,
                StyledText, StyledTextTag, StyledTextTagType, Tag,
                ChildRef, ChildRefType, Attribute, MediaRef, AttributeType,
                Url, UrlType, Address, EventRef, EventRoleType, RepoRef,
                FamilyRelType, LdsOrd, MediaRef, PersonRef, PlaceType,
                SrcAttribute, SrcAttributeType)

class FieldBaseTest(unittest.TestCase):

    def setUp(self):
        db = make_database("inmemorydb")
        db.load(None)
        with db.get_transaction_class()("Test", db) as trans:
            # Add some people:
            person1 = Person()
            person1.primary_name = Name()
            person1.primary_name.surname_list.append(Surname())
            person1.primary_name.surname_list[0].surname = "Smith"
            person1.gramps_id = "I0001"
            db.add_person(person1, trans) # person gets a handle

            # Add some families:
            family1 = Family()
            family1.father_handle = person1.handle
            family1.gramps_id = "F0001"
            db.add_family(family1, trans)
        self.db = db

    def test_field_access01(self):
        person = self.db.get_person_from_gramps_id("I0001")
        self.assertEqual(person.get_field("primary_name.surname_list.0.surname"), 
                         "Smith")

    def test_field_join01(self):
        family = self.db.get_family_from_gramps_id("F0001")
        self.assertEqual(family.get_field("father_handle.primary_name.surname_list.0.surname", self.db), 
                         "Smith")

if __name__ == "__main__":
    unittest.main()
