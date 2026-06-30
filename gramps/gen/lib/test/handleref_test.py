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

"""Tests for get_referenced_handles_recursively() and remove_handle_references()."""

import unittest

from .. import (
    ChildRef,
    EventRef,
    Family,
    Person,
    PersonRef,
    Place,
    PlaceRef,
    Source,
    Citation,
    Repository,
    RepoRef,
)


def _handles_of(handle_list, classname):
    """Return the list of handles for a given classname from a (classname, handle) list."""
    return [h for cls, h in handle_list if cls == classname]


class PersonGetReferencedHandlesRecursivelyTest(unittest.TestCase):
    """Person.get_referenced_handles_recursively() returns each handle exactly once."""

    def test_event_ref_handle_appears_once(self):
        person = Person()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        person.add_event_ref(evtref)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Event").count("e0001"), 1)

    def test_person_ref_handle_appears_once(self):
        person = Person()
        personref = PersonRef()
        personref.set_reference_handle("i0002")
        person.add_person_ref(personref)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Person").count("i0002"), 1)

    def test_note_on_event_ref_appears_once(self):
        """A note attached to an EventRef should appear exactly once."""
        person = Person()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        evtref.add_note("n0001")
        person.add_event_ref(evtref)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)

    def test_note_shared_between_person_and_event_ref_appears_once(self):
        """A note referenced at both person level and on an EventRef appears once."""
        person = Person()
        person.add_note("n0001")
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        evtref.add_note("n0001")
        person.add_event_ref(evtref)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)

    def test_note_shared_between_two_event_refs_appears_once(self):
        """A note referenced on two different EventRefs on the same person appears once."""
        person = Person()
        evtref1 = EventRef()
        evtref1.set_reference_handle("e0001")
        evtref1.add_note("n0001")
        evtref2 = EventRef()
        evtref2.set_reference_handle("e0002")
        evtref2.add_note("n0001")
        person.add_event_ref(evtref1)
        person.add_event_ref(evtref2)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)

    def test_citation_shared_between_person_and_event_ref_appears_once(self):
        """A citation referenced at both person level and on an EventRef appears once."""
        person = Person()
        person.add_citation("c0001")
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        evtref.add_citation("c0001")
        person.add_event_ref(evtref)
        handles = person.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Citation").count("c0001"), 1)


class FamilyGetReferencedHandlesRecursivelyTest(unittest.TestCase):
    """Family.get_referenced_handles_recursively() returns each handle exactly once."""

    def test_child_handle_appears_once(self):
        """
        A child person handle must appear exactly once.

        Bug: Family.get_referenced_handles() already includes ("Person", child_ref.ref)
        for each child, but Family.get_handle_referents() also returns child_ref_list,
        and each ChildRef.get_referenced_handles() returns ("Person", self.ref) again.
        This causes the handle to be reported twice.
        """
        family = Family()
        childref = ChildRef()
        childref.set_reference_handle("i0001")
        family.add_child_ref(childref)
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Person").count("i0001"), 1)

    def test_father_handle_appears_once(self):
        family = Family()
        family.set_father_handle("i0001")
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Person").count("i0001"), 1)

    def test_mother_handle_appears_once(self):
        family = Family()
        family.set_mother_handle("i0002")
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Person").count("i0002"), 1)

    def test_event_ref_handle_appears_once(self):
        family = Family()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        family.add_event_ref(evtref)
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Event").count("e0001"), 1)

    def test_note_on_child_ref_appears_once(self):
        """A note attached to a ChildRef appears exactly once."""
        family = Family()
        childref = ChildRef()
        childref.set_reference_handle("i0001")
        childref.add_note("n0001")
        family.add_child_ref(childref)
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)

    def test_note_shared_between_family_and_child_ref_appears_once(self):
        """A note referenced at both family level and on a ChildRef appears once."""
        family = Family()
        family.add_note("n0001")
        childref = ChildRef()
        childref.set_reference_handle("i0001")
        childref.add_note("n0001")
        family.add_child_ref(childref)
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)

    def test_note_shared_between_two_child_refs_appears_once(self):
        """A note referenced on two different ChildRefs appears once."""
        family = Family()
        childref1 = ChildRef()
        childref1.set_reference_handle("i0001")
        childref1.add_note("n0001")
        childref2 = ChildRef()
        childref2.set_reference_handle("i0002")
        childref2.add_note("n0001")
        family.add_child_ref(childref1)
        family.add_child_ref(childref2)
        handles = family.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Note").count("n0001"), 1)


class PlaceGetReferencedHandlesRecursivelyTest(unittest.TestCase):
    """Place.get_referenced_handles_recursively() returns each handle exactly once."""

    def test_placeref_handle_appears(self):
        place = Place()
        placeref = PlaceRef()
        placeref.set_reference_handle("p0001")
        place.add_placeref(placeref)
        handles = place.get_referenced_handles_recursively()
        self.assertIn("p0001", _handles_of(handles, "Place"))

    def test_placeref_handle_appears_once(self):
        place = Place()
        placeref = PlaceRef()
        placeref.set_reference_handle("p0001")
        place.add_placeref(placeref)
        handles = place.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Place").count("p0001"), 1)


class SourceGetReferencedHandlesRecursivelyTest(unittest.TestCase):
    """Source.get_referenced_handles_recursively() returns each handle exactly once."""

    def test_reporef_handle_appears_once(self):
        source = Source()
        reporef = RepoRef()
        reporef.set_reference_handle("r0001")
        source.add_repo_reference(reporef)
        handles = source.get_referenced_handles_recursively()
        self.assertEqual(_handles_of(handles, "Repository").count("r0001"), 1)


class PersonRemoveHandleReferencesTest(unittest.TestCase):
    def test_remove_event_ref(self):
        """Removing an event handle removes it from event_ref_list."""
        person = Person()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        person.add_event_ref(evtref)
        person.remove_handle_references("Event", ["e0001"])
        self.assertEqual(person.get_event_ref_list(), [])

    def test_remove_event_ref_preserves_others(self):
        """Removing one event handle leaves other event refs intact."""
        person = Person()
        evtref1 = EventRef()
        evtref1.set_reference_handle("e0001")
        evtref2 = EventRef()
        evtref2.set_reference_handle("e0002")
        person.add_event_ref(evtref1)
        person.add_event_ref(evtref2)
        person.remove_handle_references("Event", ["e0001"])
        remaining = [ref.ref for ref in person.get_event_ref_list()]
        self.assertEqual(remaining, ["e0002"])

    def test_remove_birth_event_clears_birth_ref(self):
        """Removing the birth event should clear the birth ref index."""
        person = Person()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        person.add_event_ref(evtref)
        person.set_birth_ref(evtref)
        self.assertIsNotNone(person.get_birth_ref())
        person.remove_handle_references("Event", ["e0001"])
        self.assertIsNone(person.get_birth_ref())

    def test_remove_family_handle(self):
        """Removing a family handle removes it from family_list."""
        person = Person()
        person.add_family_handle("f0001")
        person.remove_handle_references("Family", ["f0001"])
        self.assertNotIn("f0001", person.get_family_handle_list())

    def test_remove_parent_family_handle(self):
        """Removing a family handle removes it from parent_family_list."""
        person = Person()
        person.add_parent_family_handle("f0001")
        person.remove_handle_references("Family", ["f0001"])
        self.assertNotIn("f0001", person.get_parent_family_handle_list())

    def test_remove_note_from_person(self):
        """Removing a note handle removes it from person's note_list."""
        person = Person()
        person.add_note("n0001")
        person.remove_handle_references("Note", ["n0001"])
        self.assertNotIn("n0001", person.get_note_list())

    def test_remove_note_from_event_ref(self):
        """Removing a note handle also removes it from child event refs."""
        person = Person()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        evtref.add_note("n0001")
        person.add_event_ref(evtref)
        person.remove_handle_references("Note", ["n0001"])
        self.assertNotIn("n0001", person.get_event_ref_list()[0].get_note_list())

    def test_remove_person_ref(self):
        """Removing a person handle removes the person ref."""
        person = Person()
        personref = PersonRef()
        personref.set_reference_handle("i0001")
        person.add_person_ref(personref)
        person.remove_handle_references("Person", ["i0001"])
        self.assertEqual(person.get_person_ref_list(), [])


class FamilyRemoveHandleReferencesTest(unittest.TestCase):
    def test_remove_child_ref(self):
        """Removing a child person handle removes the child ref."""
        family = Family()
        childref = ChildRef()
        childref.set_reference_handle("i0001")
        family.add_child_ref(childref)
        family.remove_handle_references("Person", ["i0001"])
        self.assertEqual(family.get_child_ref_list(), [])

    def test_remove_child_ref_preserves_others(self):
        """Removing one child handle leaves other child refs intact."""
        family = Family()
        childref1 = ChildRef()
        childref1.set_reference_handle("i0001")
        childref2 = ChildRef()
        childref2.set_reference_handle("i0002")
        family.add_child_ref(childref1)
        family.add_child_ref(childref2)
        family.remove_handle_references("Person", ["i0001"])
        remaining = [ref.ref for ref in family.get_child_ref_list()]
        self.assertEqual(remaining, ["i0002"])

    def test_remove_father_handle(self):
        """Removing the father handle clears father_handle."""
        family = Family()
        family.set_father_handle("i0001")
        family.remove_handle_references("Person", ["i0001"])
        self.assertIsNone(family.get_father_handle())

    def test_remove_mother_handle(self):
        """Removing the mother handle clears mother_handle."""
        family = Family()
        family.set_mother_handle("i0002")
        family.remove_handle_references("Person", ["i0002"])
        self.assertIsNone(family.get_mother_handle())

    def test_remove_event_ref(self):
        """Removing an event handle removes the event ref."""
        family = Family()
        evtref = EventRef()
        evtref.set_reference_handle("e0001")
        family.add_event_ref(evtref)
        family.remove_handle_references("Event", ["e0001"])
        self.assertEqual(family.get_event_ref_list(), [])

    def test_remove_note_from_child_ref(self):
        """Removing a note handle also removes it from child refs."""
        family = Family()
        childref = ChildRef()
        childref.set_reference_handle("i0001")
        childref.add_note("n0001")
        family.add_child_ref(childref)
        family.remove_handle_references("Note", ["n0001"])
        self.assertNotIn("n0001", family.get_child_ref_list()[0].get_note_list())


class PlaceRemoveHandleReferencesTest(unittest.TestCase):
    def test_remove_placeref(self):
        """
        Removing a place handle should remove it from placeref_list.

        Bug: Place._remove_handle_references() is not implemented, so this
        call silently does nothing and the reference is never cleaned up.
        """
        place = Place()
        placeref = PlaceRef()
        placeref.set_reference_handle("p0001")
        place.add_placeref(placeref)
        place.remove_handle_references("Place", ["p0001"])
        self.assertEqual(place.get_placeref_list(), [])

    def test_remove_placeref_preserves_others(self):
        """Removing one place ref leaves other place refs intact."""
        place = Place()
        placeref1 = PlaceRef()
        placeref1.set_reference_handle("p0001")
        placeref2 = PlaceRef()
        placeref2.set_reference_handle("p0002")
        place.add_placeref(placeref1)
        place.add_placeref(placeref2)
        place.remove_handle_references("Place", ["p0001"])
        remaining = [ref.ref for ref in place.get_placeref_list()]
        self.assertEqual(remaining, ["p0002"])


class CitationRemoveHandleReferencesTest(unittest.TestCase):
    def test_remove_source_ref(self):
        """Removing a source handle should clear the citation's source reference."""
        citation = Citation()
        citation.set_reference_handle("s0001")
        citation.remove_handle_references("Source", ["s0001"])
        self.assertIsNone(citation.get_reference_handle())


class SourceRemoveHandleReferencesTest(unittest.TestCase):
    def test_remove_repo_ref(self):
        """Removing a repository handle should remove it from reporef_list."""
        source = Source()
        reporef = RepoRef()
        reporef.set_reference_handle("r0001")
        source.add_repo_reference(reporef)
        source.remove_handle_references("Repository", ["r0001"])
        self.assertEqual(source.get_reporef_list(), [])


if __name__ == "__main__":
    unittest.main()
