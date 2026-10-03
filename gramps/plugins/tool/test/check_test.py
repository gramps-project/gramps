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
Unit tests for the Check and Repair tool.

Each test builds the broken state it needs in an empty SQLite database, runs
one or more methods of CheckIntegrity, and asserts on the repaired objects and
the counters. The checks that run over every primary object type are driven by
tables of those types.

Report text is checked with translations disabled, so the tests pass under any
locale. tools_test.py runs the whole tool through the command line.
"""

# ------------------------
# Python modules
# ------------------------
import gettext
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.display.name import displayer as _nd
from gramps.gen.lib import (
    Address,
    ChildRef,
    Citation,
    DNAMatch,
    DNATest,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    LdsOrd,
    Media,
    MediaRef,
    Name,
    Note,
    Person,
    PersonRef,
    Place,
    PlaceName,
    PlaceRef,
    RepoRef,
    Repository,
    SharedAncestor,
    Source,
    StyledText,
    StyledTextTag,
    StyledTextTagType,
    Surname,
    Tag,
)
from gramps.gen.utils.db import family_name
from gramps.gen.utils.file import create_checksum

try:
    import gi

    gi.require_version("Gtk", "3.0")
    from gramps.plugins.tool import check
    from gramps.plugins.tool.check import CheckIntegrity

    _CHECK_AVAILABLE = True
except (ImportError, ValueError):
    _CHECK_AVAILABLE = False

_UNTRANSLATED = gettext.NullTranslations()

# Primary object types with a gramps_id, and the key under which
# cleanup_empty_objects records each type.
ID_TYPES = [
    (Person, "persons"),
    (Family, "families"),
    (Event, "events"),
    (Source, "sources"),
    (Citation, "citations"),
    (Place, "places"),
    (Media, "media"),
    (Repository, "repos"),
    (Note, "notes"),
    (DNATest, "dnatests"),
    (DNAMatch, "dnamatches"),
]


# -------------------------------------------------------------------------
#
# Functions that attach a reference to an object
#
# -------------------------------------------------------------------------
def attach_citation(obj, handle):
    """Make the object refer to the citation handle."""
    if isinstance(obj, (Source, Citation)):
        media_ref = MediaRef()
        media_ref.add_citation(handle)
        obj.add_media_reference(media_ref)
    elif isinstance(obj, Repository):
        address = Address()
        address.add_citation(handle)
        obj.add_address(address)
    else:
        obj.add_citation(handle)


def attach_media(obj, handle):
    """Make the object refer to the media handle."""
    media_ref = MediaRef()
    media_ref.set_reference_handle(handle)
    obj.add_media_reference(media_ref)


def attach_note(obj, handle):
    """Make the object refer to the note handle."""
    obj.add_note(handle)


def attach_tag(obj, handle):
    """Make the object refer to the tag handle."""
    obj.add_tag(handle)


# The types each reference check walks, with the function that attaches a
# reference of the checked kind.
CITATION_REFERRERS = [
    Person,
    Family,
    Event,
    Place,
    Citation,
    Media,
    Repository,
    DNATest,
    DNAMatch,
]
MEDIA_REFERRERS = [Person, Family, Event, Place, Source, Citation, DNATest, DNAMatch]
NOTE_REFERRERS = [
    Person,
    Family,
    Event,
    Place,
    Source,
    Citation,
    Media,
    Repository,
    DNATest,
    DNAMatch,
]
TAG_REFERRERS = [
    Person,
    Family,
    Event,
    Place,
    Source,
    Citation,
    Media,
    Repository,
    Note,
    DNATest,
    DNAMatch,
]

REFERENCE_CHECKS = {
    "citation": (
        "check_citation_references",
        Citation,
        attach_citation,
        CITATION_REFERRERS,
        "invalid_citation_references",
    ),
    "media": (
        "check_media_references",
        Media,
        attach_media,
        MEDIA_REFERRERS,
        "invalid_media_references",
    ),
    "note": (
        "check_note_references",
        Note,
        attach_note,
        NOTE_REFERRERS,
        "invalid_note_references",
    ),
    "tag": (
        "check_tag_references",
        Tag,
        attach_tag,
        TAG_REFERRERS,
        "invalid_tag_references",
    ),
}


def make_person(first_name="", gender=Person.UNKNOWN):
    """Return a person with the given first name and gender."""
    person = Person()
    name = Name()
    name.set_first_name(first_name)
    name.add_surname(Surname())
    person.set_primary_name(name)
    person.set_gender(gender)
    return person


# -------------------------------------------------------------------------
#
# CheckTestCase
#
# -------------------------------------------------------------------------
@unittest.skipUnless(_CHECK_AVAILABLE, "GTK 3 not available for the Check tool")
class CheckTestCase(unittest.TestCase):
    """Base class providing an empty database and helpers to run the checks."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db = make_database("sqlite")
        self.db.load(self.tmpdir)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.tmpdir)

    def add(self, obj, gramps_id=None):
        """Add a primary object and return its handle."""
        add_func = self.db.method("add_%s", obj.__class__.__name__)
        with DbTxn("add", self.db) as trans:
            if isinstance(obj, Tag):
                return add_func(obj, trans)
            if gramps_id is None:
                return add_func(obj, trans)
            obj.set_gramps_id(gramps_id)
            return add_func(obj, trans, set_gid=False)

    def commit(self, obj):
        """Commit a changed primary object."""
        commit_func = self.db.method("commit_%s", obj.__class__.__name__)
        with DbTxn("commit", self.db) as trans:
            commit_func(obj, trans)

    def get(self, cls, handle):
        """Return the primary object of the class with the handle."""
        return self.db.method("get_%s_from_handle", cls.__name__)(handle)

    def has(self, cls, handle):
        """Return True if an object of the class with the handle exists."""
        return self.db.method("has_%s_handle", cls.__name__)(handle)

    def checker(self, trans, uistate=None):
        """Return a CheckIntegrity for the test database."""
        return CheckIntegrity(SimpleNamespace(db=self.db), uistate, trans)

    def run_checks(self, *checks, uistate=None):
        """Run the named checks in one transaction and return the checker."""
        with DbTxn("check", self.db) as trans:
            checker = self.checker(trans, uistate)
            for name in checks:
                getattr(checker, name)()
        return checker

    def report(self, checker):
        """Return the error count and untranslated text of the report."""
        with (
            mock.patch.object(check, "_", _UNTRANSLATED.gettext),
            mock.patch.object(check, "ngettext", _UNTRANSLATED.ngettext),
            redirect_stdout(io.StringIO()),
        ):
            errors = checker.build_report()
        return errors, checker.text.getvalue()


# -------------------------------------------------------------------------
#
# Checks over every primary object type
#
# -------------------------------------------------------------------------
class CleanupEmptyObjectsTest(CheckTestCase):
    """cleanup_empty_objects removes objects that hold no data."""

    def test_empty_object_is_removed(self):
        """An empty object is removed and an object with data is kept."""
        for cls, key in ID_TYPES:
            with self.subTest(cls.__name__):
                empty = self.add(cls())
                kept_obj = cls()
                kept_obj.set_privacy(True)
                kept = self.add(kept_obj)

                checker = self.run_checks("cleanup_empty_objects")

                self.assertEqual(checker.empty_objects[key], [empty])
                self.assertFalse(self.has(cls, empty))
                self.assertTrue(self.has(cls, kept))

    def test_empty_test_of_a_match_is_kept(self):
        """An empty DNA test that a DNA match refers to is kept."""
        test_handle = self.add(DNATest())
        dnamatch = DNAMatch()
        dnamatch.set_subject_test_handle(test_handle)
        self.add(dnamatch)

        checker = self.run_checks("cleanup_empty_objects", "check_dnamatch_references")

        self.assertEqual(checker.empty_objects["dnatests"], [])
        self.assertEqual(checker.invalid_dnatest_references, set())
        self.assertTrue(self.has(DNATest, test_handle))

    def test_report_lists_removed_objects(self):
        """The report counts the removed objects of each type."""
        labels = {
            Person: "person",
            Family: "family",
            Event: "event",
            Source: "source",
            Media: "media",
            Place: "place",
            Repository: "repository",
            Note: "note",
            DNATest: "DNA test",
            DNAMatch: "DNA match",
        }
        for cls in labels:
            self.add(cls())

        checker = self.run_checks("cleanup_empty_objects")
        errors, text = self.report(checker)

        self.assertEqual(errors, len(labels))
        self.assertIn("%d empty objects removed" % len(labels), text)
        for cls, label in labels.items():
            with self.subTest(cls.__name__):
                self.assertIn("   1 %s objects\n" % label, text)

    def test_report_lists_removed_citations(self):
        """The report counts removed citations."""
        self.add(Citation())

        checker = self.run_checks("cleanup_empty_objects")
        _errors, text = self.report(checker)

        self.assertIn("1 citation objects", text)


class DuplicatedGrampsIdTest(CheckTestCase):
    """fix_duplicated_grampsid gives each duplicated Gramps ID a new value."""

    def test_duplicated_ids_are_replaced(self):
        """One object of each duplicated pair receives a new Gramps ID."""
        handles = {}
        for cls, _key in ID_TYPES:
            gramps_id = "%s-DUP" % cls.__name__
            handles[cls] = (self.add(cls(), gramps_id), self.add(cls(), gramps_id))

        checker = self.run_checks("fix_duplicated_grampsid")

        self.assertEqual(checker.duplicated_gramps_ids, len(ID_TYPES))
        for cls, (first, second) in handles.items():
            with self.subTest(cls.__name__):
                self.assertNotEqual(
                    self.get(cls, first).get_gramps_id(),
                    self.get(cls, second).get_gramps_id(),
                )

    def test_unique_ids_are_kept(self):
        """Objects with distinct Gramps IDs are unchanged."""
        for cls, _key in ID_TYPES:
            self.add(cls(), "%s-1" % cls.__name__)
            self.add(cls(), "%s-2" % cls.__name__)

        checker = self.run_checks("fix_duplicated_grampsid")

        self.assertEqual(checker.duplicated_gramps_ids, 0)


class ReferenceChecksTest(CheckTestCase):
    """The citation, media, note and tag checks repair missing references."""

    def _check_missing(self, kind):
        """Assert that each referrer's missing reference gets a placeholder."""
        check_name, target, attach, referrers, counter = REFERENCE_CHECKS[kind]
        missing = {}
        for cls in referrers:
            obj = cls()
            handle = "missing-%s-%s" % (kind, cls.__name__)
            attach(obj, handle)
            self.add(obj)
            missing[cls] = handle

        checker = self.run_checks(check_name)

        self.assertEqual(getattr(checker, counter), set(missing.values()))
        for cls, handle in missing.items():
            with self.subTest(cls.__name__):
                self.assertTrue(self.has(target, handle))

    def _check_present(self, kind):
        """Assert that a reference to an existing object is not reported."""
        check_name, target, attach, referrers, counter = REFERENCE_CHECKS[kind]
        for cls in referrers:
            obj = cls()
            attach(obj, self.add(target()))
            self.add(obj)

        checker = self.run_checks(check_name)

        self.assertEqual(getattr(checker, counter), set())

    def test_missing_citation_gets_placeholder(self):
        """A missing citation is replaced by a placeholder citation and source."""
        self._check_missing("citation")

    def test_missing_media_gets_placeholder(self):
        """A missing media object is replaced by a placeholder."""
        self._check_missing("media")

    def test_missing_note_gets_placeholder(self):
        """A missing note is replaced by a placeholder."""
        self._check_missing("note")

    def test_missing_tag_gets_placeholder(self):
        """A missing tag is replaced by a placeholder."""
        self._check_missing("tag")

    def test_present_citation_is_kept(self):
        """A citation that exists is not reported."""
        self._check_present("citation")

    def test_present_media_is_kept(self):
        """A media object that exists is not reported."""
        self._check_present("media")

    def test_present_note_is_kept(self):
        """A note that exists is not reported."""
        self._check_present("note")

    def test_present_tag_is_kept(self):
        """A tag that exists is not reported."""
        self._check_present("tag")

    def test_citation_placeholder_has_placeholder_source(self):
        """A placeholder citation refers to a placeholder source."""
        person = Person()
        person.add_citation("missing-citation")
        self.add(person)

        checker = self.run_checks("check_citation_references")

        citation = self.get(Citation, "missing-citation")
        self.assertTrue(self.has(Source, citation.get_reference_handle()))
        self.assertEqual(
            checker.invalid_source_references, {citation.get_reference_handle()}
        )

    def test_missing_citation_on_source_gets_placeholder(self):
        """A missing citation on a source is found."""
        source = Source()
        attach_citation(source, "missing-citation")
        self.add(source)

        checker = self.run_checks("check_citation_references")

        self.assertEqual(checker.invalid_citation_references, {"missing-citation"})

    def test_missing_citation_on_shared_ancestor_gets_placeholder(self):
        """A missing citation held by a secondary object is found."""
        ancestor = SharedAncestor()
        ancestor.add_citation("missing-citation")
        dnamatch = DNAMatch()
        dnamatch.add_shared_ancestor(ancestor)
        self.add(dnamatch)

        checker = self.run_checks("check_citation_references")

        self.assertEqual(checker.invalid_citation_references, {"missing-citation"})
        self.assertTrue(self.has(Citation, "missing-citation"))

    def test_placeholder_note_explanation_is_added(self):
        """The explanation note is added when a placeholder note is made."""
        person = Person()
        person.add_note("missing-note")
        self.add(person)

        checker = self.run_checks("check_note_references")

        self.assertTrue(self.has(Note, checker.explanation.handle))


class MissingMediaTest(CheckTestCase):
    """cleanup_missing_photos handles media objects whose file is missing."""

    def setUp(self):
        super().setUp()
        self.missing_path = os.path.join(self.tmpdir, "missing.png")

    def _add_media(self, path):
        """Add a media object with the path and return its handle."""
        media = Media()
        media.set_path(path)
        return self.add(media)

    def _add_referrers(self, media_handle):
        """Add one object of each referring type and return their handles."""
        handles = {}
        for cls in MEDIA_REFERRERS:
            obj = cls()
            attach_media(obj, media_handle)
            handles[cls] = self.add(obj)
        return handles

    def _run_with_dialog(self, *actions):
        """Run the media checks, answering each dialog with the next action."""
        answers = list(actions)

        def dialog(_title, _msg, remove, keep, _select, **_kwargs):
            """Return a stand-in dialog that applies the next answer."""
            action, default = answers.pop(0)
            {"remove": remove, "keep": keep}[action]()
            return SimpleNamespace(default_action=default)

        with mock.patch.object(check, "MissingMediaDialog", dialog):
            with DbTxn("check", self.db) as trans:
                checker = self.checker(trans, SimpleNamespace(window=None))
                checker.cleanup_missing_photos(0)
                checker.check_media_references()
        return checker

    def test_cli_keeps_missing_file_reference(self):
        """From the command line a missing file is reported and kept."""
        media_handle = self._add_media(self.missing_path)

        with DbTxn("check", self.db) as trans:
            checker = self.checker(trans)
            checker.cleanup_missing_photos(1)

        self.assertEqual(checker.bad_photo, [media_handle])
        self.assertTrue(self.has(Media, media_handle))

    def test_existing_file_is_not_reported(self):
        """A media object whose file exists is not reported."""
        path = os.path.join(self.tmpdir, "present.png")
        with open(path, "wb") as handle:
            handle.write(b"data")
        self._add_media(path)

        with DbTxn("check", self.db) as trans:
            checker = self.checker(trans)
            checker.cleanup_missing_photos(1)

        self.assertEqual(checker.bad_photo, [])

    def test_url_is_not_reported(self):
        """A media object whose path is a URL is not reported."""
        self._add_media("https://example.com/image.png")

        with DbTxn("check", self.db) as trans:
            checker = self.checker(trans)
            checker.cleanup_missing_photos(1)

        self.assertEqual(checker.bad_photo, [])

    def test_remove_clears_every_reference(self):
        """Removing a missing media object clears its references from every type."""
        media_handle = self._add_media(self.missing_path)
        referrers = self._add_referrers(media_handle)

        checker = self._run_with_dialog(("remove", 0))

        self.assertEqual(checker.removed_photo, [media_handle])
        self.assertFalse(self.has(Media, media_handle))
        self.assertEqual(checker.invalid_media_references, set())
        for cls, handle in referrers.items():
            with self.subTest(cls.__name__):
                self.assertEqual(self.get(cls, handle).get_media_list(), [])

    def test_keep_leaves_references(self):
        """Keeping a missing media object leaves its references in place."""
        media_handle = self._add_media(self.missing_path)
        referrers = self._add_referrers(media_handle)

        checker = self._run_with_dialog(("keep", 0))

        self.assertEqual(checker.bad_photo, [media_handle])
        for cls, handle in referrers.items():
            with self.subTest(cls.__name__):
                self.assertEqual(len(self.get(cls, handle).get_media_list()), 1)

    def test_default_action_applies_to_later_files(self):
        """A remembered answer is applied to later missing files without asking."""
        first = self._add_media(self.missing_path)
        second = self._add_media(os.path.join(self.tmpdir, "also-missing.png"))

        checker = self._run_with_dialog(("remove", 1))

        self.assertEqual(sorted(checker.removed_photo), sorted([first, second]))

    def test_checksum_is_updated(self):
        """A media object's checksum is set from its file."""
        path = os.path.join(self.tmpdir, "present.png")
        with open(path, "wb") as handle:
            handle.write(b"data")
        media_handle = self._add_media(path)

        self.run_checks("check_checksum")

        self.assertEqual(
            self.get(Media, media_handle).get_checksum(), create_checksum(path)
        )


class NoteLinksTest(CheckTestCase):
    """check_note_links removes note links to objects that do not exist."""

    def _add_linking_note(self, *links):
        """Add a note with a link tag for each link and return its handle."""
        text = "x" * len(links)
        tags = [
            StyledTextTag(StyledTextTagType.LINK, link, [(index, index + 1)])
            for index, link in enumerate(links)
        ]
        note = Note()
        note.set_styledtext(StyledText(text, tags))
        return self.add(note)

    def test_links_to_missing_objects_are_removed(self):
        """A link to a missing object of any type is removed."""
        for cls, _key in ID_TYPES:
            with self.subTest(cls.__name__):
                kept = self.add(cls(), "%s-LINKED" % cls.__name__)
                links = [
                    "gramps://%s/handle/%s" % (cls.__name__, kept),
                    "gramps://%s/handle/missing" % cls.__name__,
                    "gramps://%s/gramps_id/%s-LINKED" % (cls.__name__, cls.__name__),
                    "gramps://%s/gramps_id/missing" % cls.__name__,
                ]
                note_handle = self._add_linking_note(*links)

                checker = self.run_checks("check_note_links")

                self.assertEqual(checker.bad_note_links, 2)
                tags = self.get(Note, note_handle).get_styledtext().get_tags()
                self.assertEqual([tag.value for tag in tags], [links[0], links[2]])

    def test_web_links_are_kept(self):
        """A link that is not a Gramps link is kept."""
        self._add_linking_note("https://example.com")

        checker = self.run_checks("check_note_links")

        self.assertEqual(checker.bad_note_links, 0)


class BacklinksTest(CheckTestCase):
    """check_backlinks finds references missing from the reference table."""

    def _clear_reference_table(self):
        """Delete every row of the reference table."""
        self.db.dbapi.execute("DELETE FROM reference")
        self.db.dbapi.commit()

    def test_missing_backlinks_are_counted(self):
        """Each reference without a backlink row is counted."""
        person_handle = self.add(Person())
        note = Note()
        self.add(note)
        family = Family()
        family.set_father_handle(person_handle)
        family.add_note(note.get_handle())
        self.add(family)
        test = DNATest()
        test.set_person_handle(person_handle)
        self.add(test)
        self._clear_reference_table()

        checker = self.run_checks("check_backlinks")

        self.assertEqual(checker.bad_backlinks, 3)

    def test_intact_backlinks_are_not_counted(self):
        """References with backlink rows are not counted."""
        person_handle = self.add(Person())
        test = DNATest()
        test.set_person_handle(person_handle)
        self.add(test)

        checker = self.run_checks("check_backlinks")

        self.assertEqual(checker.bad_backlinks, 0)


# -------------------------------------------------------------------------
#
# Checks of references held by particular types
#
# -------------------------------------------------------------------------
class PersonReferencesTest(CheckTestCase):
    """check_person_references repairs associations to missing people."""

    def test_missing_associate_gets_placeholder(self):
        """An association to a missing person gets a placeholder person."""
        person_ref = PersonRef()
        person_ref.set_reference_handle("missing-person")
        person = Person()
        person.add_person_ref(person_ref)
        person_handle = self.add(person)

        checker = self.run_checks("check_person_references")

        self.assertTrue(self.has(Person, "missing-person"))
        self.assertEqual(checker.invalid_person_references, {person_handle})

    def test_empty_associate_gets_placeholder(self):
        """An association without a handle gets a placeholder person."""
        person = Person()
        person.add_person_ref(PersonRef())
        person_handle = self.add(person)

        self.run_checks("check_person_references")

        ref = self.get(Person, person_handle).get_person_ref_list()[0].ref
        self.assertTrue(ref)
        self.assertTrue(self.has(Person, ref))


class FamilyReferencesTest(CheckTestCase):
    """check_family_references repairs LDS ordinances naming missing families."""

    def test_missing_ordinance_family_gets_placeholder(self):
        """An ordinance naming a missing family gets a placeholder family."""
        ordinance = LdsOrd()
        ordinance.set_family_handle("missing-family")
        person = Person()
        person.add_lds_ord(ordinance)
        person_handle = self.add(person)

        checker = self.run_checks("check_family_references")

        self.assertTrue(self.has(Family, "missing-family"))
        self.assertEqual(checker.invalid_family_references, {person_handle})


class RepositoryReferencesTest(CheckTestCase):
    """check_repo_references repairs sources naming missing repositories."""

    def test_missing_repository_gets_placeholder(self):
        """A repository reference to a missing repository gets a placeholder."""
        repo_ref = RepoRef()
        repo_ref.set_reference_handle("missing-repository")
        source = Source()
        source.add_repo_reference(repo_ref)
        source_handle = self.add(source)

        checker = self.run_checks("check_repo_references")

        self.assertTrue(self.has(Repository, "missing-repository"))
        self.assertEqual(checker.invalid_repo_references, {source_handle})

    def test_empty_repository_reference_gets_placeholder(self):
        """A repository reference without a handle gets a placeholder."""
        source = Source()
        source.add_repo_reference(RepoRef())
        source_handle = self.add(source)

        self.run_checks("check_repo_references")

        ref = self.get(Source, source_handle).get_reporef_list()[0].ref
        self.assertTrue(ref)
        self.assertTrue(self.has(Repository, ref))


class PlaceReferencesTest(CheckTestCase):
    """check_place_references repairs references to missing places."""

    def test_missing_enclosing_place_gets_placeholder(self):
        """A place enclosed by a missing place gets a placeholder."""
        place_ref = PlaceRef()
        place_ref.set_reference_handle("missing-place")
        place = Place()
        place.add_placeref(place_ref)
        place_handle = self.add(place)

        checker = self.run_checks("check_place_references")

        self.assertTrue(self.has(Place, "missing-place"))
        self.assertEqual(checker.invalid_place_references, {place_handle})

    def test_missing_ordinance_place_gets_placeholder(self):
        """An ordinance of a person or family at a missing place gets a placeholder."""
        handles = set()
        for cls in (Person, Family):
            ordinance = LdsOrd()
            ordinance.set_place_handle("missing-place-%s" % cls.__name__)
            obj = cls()
            obj.add_lds_ord(ordinance)
            handles.add(self.add(obj))

        checker = self.run_checks("check_place_references")

        self.assertEqual(checker.invalid_place_references, handles)
        for cls in (Person, Family):
            with self.subTest(cls.__name__):
                self.assertTrue(self.has(Place, "missing-place-%s" % cls.__name__))

    def test_missing_event_place_gets_placeholder(self):
        """An event at a missing place gets a placeholder."""
        event = Event()
        event.set_place_handle("missing-place")
        event_handle = self.add(event)

        checker = self.run_checks("check_place_references")

        self.assertTrue(self.has(Place, "missing-place"))
        self.assertEqual(checker.invalid_place_references, {event_handle})


class SourceReferencesTest(CheckTestCase):
    """check_source_references repairs citations of missing sources."""

    def test_missing_source_gets_placeholder(self):
        """A citation of a missing source gets a placeholder source."""
        citation = Citation()
        citation.set_reference_handle("missing-source")
        citation_handle = self.add(citation)

        checker = self.run_checks("check_source_references")

        self.assertTrue(self.has(Source, "missing-source"))
        self.assertEqual(checker.invalid_source_references, {citation_handle})

    def test_citation_without_source_gets_placeholder(self):
        """A citation without a source gets a placeholder source."""
        citation_handle = self.add(Citation())

        self.run_checks("check_source_references")

        source_handle = self.get(Citation, citation_handle).get_reference_handle()
        self.assertTrue(source_handle)
        self.assertTrue(self.has(Source, source_handle))


class EventReferencesTest(CheckTestCase):
    """check_events repairs references to missing or mistyped events."""

    def _add_person_with_event(self, role, event_handle):
        """Add a person whose birth, death or other event has the handle."""
        event_ref = EventRef()
        event_ref.set_reference_handle(event_handle)
        person = Person()
        person.add_event_ref(event_ref)
        if role == "birth":
            person.set_birth_ref(event_ref)
        elif role == "death":
            person.set_death_ref(event_ref)
        return self.add(person)

    def test_missing_birth_and_death_get_placeholders(self):
        """A missing birth or death event gets a placeholder of that type."""
        for role, event_type in (
            ("birth", EventType.BIRTH),
            ("death", EventType.DEATH),
        ):
            with self.subTest(role):
                handle = "missing-%s" % role
                person_handle = self._add_person_with_event(role, handle)

                checker = self.run_checks("check_events")

                self.assertIn(person_handle, checker.invalid_events)
                self.assertEqual(int(self.get(Event, handle).get_type()), event_type)

    def test_mistyped_birth_and_death_are_corrected(self):
        """A birth or death event of another type is given the right type."""
        cases = (
            ("birth", EventType.BIRTH, "invalid_birth_events"),
            ("death", EventType.DEATH, "invalid_death_events"),
        )
        for role, event_type, counter in cases:
            with self.subTest(role):
                event = Event()
                event.set_type(EventType.MARRIAGE)
                event_handle = self.add(event)
                person_handle = self._add_person_with_event(role, event_handle)

                checker = self.run_checks("check_events")

                self.assertEqual(getattr(checker, counter), {person_handle})
                self.assertEqual(
                    int(self.get(Event, event_handle).get_type()), event_type
                )

    def test_missing_events_get_placeholders(self):
        """A missing event of a person or family gets a placeholder."""
        person_handle = self._add_person_with_event("other", "missing-person-event")
        event_ref = EventRef()
        event_ref.set_reference_handle("missing-family-event")
        family = Family()
        family.add_event_ref(event_ref)
        family_handle = self.add(family)

        checker = self.run_checks("check_events")

        self.assertEqual(checker.invalid_events, {person_handle, family_handle})
        self.assertTrue(self.has(Event, "missing-person-event"))
        self.assertTrue(self.has(Event, "missing-family-event"))

    def test_empty_event_references_get_placeholders(self):
        """An event reference without a handle gets a placeholder event."""
        person = Person()
        person.add_event_ref(EventRef())
        person_handle = self.add(person)
        family = Family()
        family.add_event_ref(EventRef())
        family_handle = self.add(family)

        self.run_checks("check_events")

        for cls, handle in ((Person, person_handle), (Family, family_handle)):
            with self.subTest(cls.__name__):
                ref = self.get(cls, handle).get_event_ref_list()[0].ref
                self.assertTrue(ref)
                self.assertTrue(self.has(Event, ref))


class DNATestReferencesTest(CheckTestCase):
    """check_dnatest_references repairs DNA tests naming missing people."""

    def test_missing_person_is_cleared(self):
        """A DNA test whose person is missing becomes unidentified."""
        test = DNATest()
        test.set_person_handle("missing-person")
        test_handle = self.add(test)

        checker = self.run_checks("check_dnatest_references")

        self.assertIsNone(self.get(DNATest, test_handle).get_person_handle())
        self.assertEqual(checker.invalid_dnatest_person_references, {test_handle})
        self.assertEqual(self.db.get_number_of_people(), 0)

    def test_present_person_is_kept(self):
        """A DNA test whose person exists is unchanged."""
        person_handle = self.add(Person())
        test = DNATest()
        test.set_person_handle(person_handle)
        test_handle = self.add(test)

        checker = self.run_checks("check_dnatest_references")

        self.assertEqual(
            self.get(DNATest, test_handle).get_person_handle(), person_handle
        )
        self.assertEqual(checker.invalid_dnatest_person_references, set())

    def test_unidentified_test_is_not_reported(self):
        """A DNA test with no person is not a broken reference."""
        self.add(DNATest())

        checker = self.run_checks("check_dnatest_references")

        self.assertEqual(checker.invalid_dnatest_person_references, set())


class DNAMatchReferencesTest(CheckTestCase):
    """check_dnamatch_references repairs DNA matches naming missing objects."""

    def test_missing_tests_get_placeholders(self):
        """A missing subject or match test is replaced by a placeholder test."""
        for side in ("subject", "match"):
            with self.subTest(side):
                dnamatch = DNAMatch()
                handle = "missing-%s-test" % side
                getattr(dnamatch, "set_%s_test_handle" % side)(handle)
                self.add(dnamatch)

                checker = self.run_checks("check_dnamatch_references")

                placeholder = self.get(DNATest, handle)
                self.assertEqual(
                    placeholder.get_account_name(),
                    glocale.translation.sgettext("Unknown"),
                )
                self.assertEqual(
                    placeholder.get_note_list(), [checker.explanation.handle]
                )
                self.assertEqual(checker.invalid_dnatest_references, {handle})

    def test_each_missing_test_is_counted(self):
        """A DNA match missing both tests counts two missing tests."""
        dnamatch = DNAMatch()
        dnamatch.set_subject_test_handle("missing-subject-test")
        dnamatch.set_match_test_handle("missing-match-test")
        self.add(dnamatch)

        checker = self.run_checks("check_dnamatch_references")

        self.assertEqual(
            checker.invalid_dnatest_references,
            {"missing-subject-test", "missing-match-test"},
        )
        self.assertEqual(self.db.get_number_of_dnatests(), 2)

    def test_match_without_tests_is_not_reported(self):
        """A DNA match with no kits set is not a broken reference."""
        self.add(DNAMatch())

        checker = self.run_checks("check_dnamatch_references")

        self.assertEqual(checker.invalid_dnatest_references, set())
        self.assertEqual(self.db.get_number_of_dnatests(), 0)

    def test_shared_ancestor_missing_person_is_cleared(self):
        """A shared ancestor whose person is missing keeps only its description."""
        kept_handle = self.add(Person())
        dnamatch = DNAMatch()
        for person_handle, description in (
            (kept_handle, "kept"),
            ("missing-person", "removed"),
        ):
            ancestor = SharedAncestor()
            ancestor.set_person_handle(person_handle)
            ancestor.set_description(description)
            dnamatch.add_shared_ancestor(ancestor)
        match_handle = self.add(dnamatch)

        checker = self.run_checks("check_dnamatch_references")

        ancestors = self.get(DNAMatch, match_handle).get_shared_ancestor_list()
        self.assertEqual(
            [(sa.get_person_handle(), sa.get_description()) for sa in ancestors],
            [(kept_handle, "kept"), (None, "removed")],
        )
        self.assertEqual(checker.invalid_sharedancestor_references, {match_handle})
        self.assertEqual(self.db.get_number_of_people(), 1)


class ExplanationNoteTest(CheckTestCase):
    """Placeholder objects carry a note that check_note_references adds."""

    def test_explanation_is_added_for_placeholders(self):
        """The explanation note exists once any placeholder has been made."""
        dnamatch = DNAMatch()
        dnamatch.set_subject_test_handle("missing-test")
        self.add(dnamatch)

        checker = self.run_checks("check_dnamatch_references", "check_note_references")

        self.assertTrue(self.has(Note, checker.explanation.handle))
        self.assertEqual(checker.invalid_note_references, set())

    def test_explanation_is_not_added_without_placeholders(self):
        """The explanation note is not added when nothing was repaired."""
        self.add(Person())

        checker = self.run_checks("check_person_references", "check_note_references")

        self.assertFalse(self.has(Note, checker.explanation.handle))


# -------------------------------------------------------------------------
#
# Family structure checks
#
# -------------------------------------------------------------------------
class BrokenFamilyLinksTest(CheckTestCase):
    """check_for_broken_family_links repairs links between people and families."""

    def _add_family(self, father=None, mother=None, children=()):
        """Add a family with the given members and return its handle."""
        family = Family()
        family.set_father_handle(father)
        family.set_mother_handle(mother)
        for child in children:
            child_ref = ChildRef()
            child_ref.set_reference_handle(child)
            family.add_child_ref(child_ref)
        return self.add(family)

    def _link(self, person_handle, family_handle, as_child=False):
        """Make the person refer to the family as a parent or a child."""
        person = self.get(Person, person_handle)
        if as_child:
            person.add_parent_family_handle(family_handle)
        else:
            person.add_family_handle(family_handle)
        self.commit(person)

    def test_missing_parents_are_cleared(self):
        """A father or mother that does not exist is removed from the family."""
        family_handle = self._add_family("missing-father", "missing-mother")

        checker = self.run_checks("check_for_broken_family_links")

        family = self.get(Family, family_handle)
        self.assertIsNone(family.get_father_handle())
        self.assertIsNone(family.get_mother_handle())
        self.assertEqual(
            checker.broken_parent_links,
            [("missing-father", family_handle), ("missing-mother", family_handle)],
        )

    def test_parent_without_back_link_is_relinked(self):
        """A parent that does not list the family has the family added."""
        father = self.add(Person())
        mother = self.add(Person())
        family_handle = self._add_family(father, mother)

        checker = self.run_checks("check_for_broken_family_links")

        for parent in (father, mother):
            self.assertEqual(
                self.get(Person, parent).get_family_handle_list(), [family_handle]
            )
        self.assertEqual(
            checker.broken_parent_links,
            [(father, family_handle), (mother, family_handle)],
        )

    def test_missing_child_is_removed(self):
        """A child that does not exist is removed from the family."""
        family_handle = self._add_family(children=["missing-child"])

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(self.get(Family, family_handle).get_child_ref_list(), [])
        self.assertEqual(checker.broken_links, [("missing-child", family_handle)])

    def test_parent_listed_as_child_is_removed(self):
        """A child that is also a parent of the family is removed as a child."""
        father = self.add(Person())
        family_handle = self._add_family(father, children=[father])
        self._link(father, family_handle)

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(self.get(Family, family_handle).get_child_ref_list(), [])
        self.assertIn((father, family_handle), checker.broken_links)

    def test_child_without_back_link_is_relinked(self):
        """A child that does not list the family has the family added."""
        child = self.add(Person())
        family_handle = self._add_family(children=[child])

        self.run_checks("check_for_broken_family_links")

        self.assertEqual(
            self.get(Person, child).get_parent_family_handle_list(), [family_handle]
        )

    def test_duplicate_children_are_merged(self):
        """A child listed twice in a family is listed once."""
        child = self.add(Person())
        family_handle = self._add_family(children=[child, child])
        self._link(child, family_handle, as_child=True)

        self.run_checks("check_for_broken_family_links")

        child_refs = self.get(Family, family_handle).get_child_ref_list()
        self.assertEqual([ref.ref for ref in child_refs], [child])

    def test_duplicate_parent_families_are_merged(self):
        """A person who lists a parent family twice lists it once."""
        child = self.add(Person())
        family_handle = self._add_family(children=[child])
        person = self.get(Person, child)
        person.set_parent_family_handle_list([family_handle, family_handle])
        self.commit(person)

        self.run_checks("check_for_broken_family_links")

        self.assertEqual(
            self.get(Person, child).get_parent_family_handle_list(), [family_handle]
        )

    def test_missing_parent_family_is_removed(self):
        """A parent family that does not exist is removed from the person."""
        child = self.add(Person())
        self._link(child, "missing-family", as_child=True)

        self.run_checks("check_for_broken_family_links")

        self.assertEqual(self.get(Person, child).get_parent_family_handle_list(), [])

    def test_person_not_a_child_of_parent_family_is_unlinked(self):
        """A person who is not a child of a listed parent family is unlinked."""
        person_handle = self.add(Person())
        family_handle = self._add_family()
        self._link(person_handle, family_handle, as_child=True)

        self.run_checks("check_for_broken_family_links")

        self.assertEqual(
            self.get(Person, person_handle).get_parent_family_handle_list(), []
        )

    def test_unlinked_parent_family_is_recorded(self):
        """The unlinked parent family is recorded."""
        person_handle = self.add(Person())
        family_handle = self._add_family()
        self._add_family()
        self._link(person_handle, family_handle, as_child=True)

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(checker.broken_links, [(person_handle, family_handle)])

    def test_missing_family_is_removed_from_person(self):
        """A family that does not exist is removed from the person."""
        person_handle = self.add(Person())
        self._link(person_handle, "missing-family")

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(self.get(Person, person_handle).get_family_handle_list(), [])
        self.assertEqual(checker.broken_links, [(person_handle, "missing-family")])

    def test_person_not_a_parent_of_family_is_unlinked(self):
        """A person who is not a parent of a listed family is unlinked."""
        person_handle = self.add(Person())
        family_handle = self._add_family()
        self._link(person_handle, family_handle)

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(self.get(Person, person_handle).get_family_handle_list(), [])
        self.assertEqual(checker.broken_links, [(person_handle, family_handle)])

    def test_consistent_family_is_unchanged(self):
        """A family whose links agree in both directions is not reported."""
        father = self.add(Person())
        child = self.add(Person())
        family_handle = self._add_family(father, children=[child])
        self._link(father, family_handle)
        self._link(child, family_handle, as_child=True)

        checker = self.run_checks("check_for_broken_family_links")

        self.assertEqual(checker.family_errors(), 0)


class ParentRelationshipsTest(CheckTestCase):
    """check_parent_relationships swaps parents recorded in the wrong role."""

    def _add_family(self, father_gender, mother_gender):
        """Add a family with parents of the given genders and return its handle."""
        family = Family()
        family.set_father_handle(self.add(make_person(gender=father_gender)))
        family.set_mother_handle(self.add(make_person(gender=mother_gender)))
        return self.add(family)

    def test_swapped_parents_are_corrected(self):
        """A female father and a male mother are swapped."""
        family_handle = self._add_family(Person.FEMALE, Person.MALE)
        family = self.get(Family, family_handle)
        father, mother = family.get_father_handle(), family.get_mother_handle()

        checker = self.run_checks("check_parent_relationships")

        family = self.get(Family, family_handle)
        self.assertEqual(
            (family.get_father_handle(), family.get_mother_handle()), (mother, father)
        )
        self.assertEqual(checker.fam_rel, [family_handle])

    def test_same_sex_parents_are_unchanged(self):
        """A family with parents of the same sex is not changed."""
        for gender in (Person.MALE, Person.FEMALE):
            self._add_family(gender, gender)

        checker = self.run_checks("check_parent_relationships")

        self.assertEqual(checker.fam_rel, [])


class EmptyFamiliesTest(CheckTestCase):
    """cleanup_empty_families removes families without parents or children."""

    def test_empty_family_is_removed(self):
        """A family with no members is removed and unlinked from people."""
        family = Family()
        family.set_privacy(True)
        family_handle = self.add(family)
        person = Person()
        person.add_family_handle(family_handle)
        person_handle = self.add(person)

        with DbTxn("check", self.db) as trans:
            checker = self.checker(trans)
            checker.cleanup_empty_families(None)

        self.assertFalse(self.has(Family, family_handle))
        self.assertEqual(self.get(Person, person_handle).get_family_handle_list(), [])
        self.assertEqual(len(checker.empty_family), 1)

    def test_family_with_child_is_kept(self):
        """A family with only a child is kept."""
        child_ref = ChildRef()
        child_ref.set_reference_handle(self.add(Person()))
        family = Family()
        family.add_child_ref(child_ref)
        family_handle = self.add(family)

        with DbTxn("check", self.db) as trans:
            self.checker(trans).cleanup_empty_families(None)

        self.assertTrue(self.has(Family, family_handle))


class DuplicateSpousesTest(CheckTestCase):
    """cleanup_duplicate_spouses removes repeated families from a person."""

    def test_repeated_family_is_listed_once(self):
        """A family listed twice by a person is listed once."""
        family_handle = self.add(Family())
        person = Person()
        person.set_family_handle_list([family_handle, family_handle])
        person_handle = self.add(person)

        self.run_checks("cleanup_duplicate_spouses")

        self.assertEqual(
            self.get(Person, person_handle).get_family_handle_list(), [family_handle]
        )

    def test_only_repeated_families_are_counted(self):
        """Only the repeated family is counted."""
        first = self.add(Family())
        second = self.add(Family())
        person = Person()
        person.set_family_handle_list([first, second, second])
        person_handle = self.add(person)

        checker = self.run_checks("cleanup_duplicate_spouses")

        self.assertEqual(checker.duplicate_links, [(person_handle, second)])


# -------------------------------------------------------------------------
#
# Checks of text and type data
#
# -------------------------------------------------------------------------
class CtrlCharsInNotesTest(CheckTestCase):
    """fix_ctrlchars_in_notes replaces control characters in notes."""

    def test_control_characters_are_replaced(self):
        """Control characters become spaces and tabs and newlines are kept."""
        bold = StyledTextTag(StyledTextTagType.BOLD, None, [(0, 3)])
        note = Note()
        note.set_styledtext(StyledText("one\x01two\tthree\n\x1ffour", [bold]))
        note_handle = self.add(note)

        self.run_checks("fix_ctrlchars_in_notes")

        text = self.get(Note, note_handle).get_styledtext()
        self.assertEqual(str(text), "one two\tthree\n four")
        self.assertEqual(
            [tag.serialize() for tag in text.get_tags()], [bold.serialize()]
        )


class AltPlaceNamesTest(CheckTestCase):
    """fix_alt_place_names removes blank and repeated alternative names."""

    def test_bad_alternative_names_are_removed(self):
        """Blank names, the primary name and repeated names are removed."""
        place = Place()
        place.set_name(PlaceName(value="London"))
        for value in ("", "London", "Londres", "Londres", "Londinium"):
            place.add_alternative_name(PlaceName(value=value))
        place_handle = self.add(place)

        checker = self.run_checks("fix_alt_place_names")

        names = self.get(Place, place_handle).get_alternative_names()
        self.assertEqual([name.get_value() for name in names], ["Londres", "Londinium"])
        self.assertEqual(checker.place_errors, 1)


class DeletedNameFormatsTest(CheckTestCase):
    """cleanup_deleted_name_formats resets names that use deleted formats."""

    def test_deleted_format_is_reset(self):
        """A name using an inactive format is reset to the default format."""
        number = _nd.add_name_format("Deleted format", "%l")
        _nd.set_format_inactive(number)
        self.addCleanup(_nd.del_name_format, number)
        self.db.name_formats = _nd.get_name_format(only_custom=True, only_active=False)
        person = make_person("Ann")
        person.get_primary_name().set_display_as(number)
        alternate = Name()
        alternate.set_sort_as(number)
        person.add_alternate_name(alternate)
        person_handle = self.add(person)

        checker = self.run_checks("cleanup_deleted_name_formats")

        person = self.get(Person, person_handle)
        self.assertEqual(person.get_primary_name().get_display_as(), Name.DEF)
        self.assertEqual(person.get_alternate_names()[0].get_sort_as(), Name.DEF)
        self.assertEqual(checker.removed_name_format, [person_handle])
        self.assertNotIn(number, [fmt[0] for fmt in self.db.name_formats])


class DuplicatedEventRoleNamesTest(CheckTestCase):
    """fix_duplicated_event_role_names merges custom roles named like standard ones."""

    def test_custom_role_with_standard_name_is_merged(self):
        """A custom role with the name of a standard role becomes that role."""
        standard = EventRoleType(EventRoleType.PRIMARY)
        event_ref = EventRef()
        event_ref.set_reference_handle(self.add(Event()))
        event_ref.set_role(EventRoleType((EventRoleType.CUSTOM, str(standard))))
        person = Person()
        person.add_event_ref(event_ref)
        person_handle = self.add(person)

        checker = self.run_checks("fix_duplicated_event_role_names")

        role = self.get(Person, person_handle).get_event_ref_list()[0].get_role()
        self.assertEqual(role.value, EventRoleType.PRIMARY)
        self.assertEqual(checker.duplicated_event_role_names, 1)
        self.assertEqual(checker.duplicated_event_role_references, 1)
        self.assertNotIn(str(standard), self.db.get_event_roles())


# -------------------------------------------------------------------------
#
# Report
#
# -------------------------------------------------------------------------
class ReportTest(CheckTestCase):
    """build_report counts the repairs and describes each kind."""

    def test_no_errors(self):
        """A database without problems gives no errors."""
        checker = self.run_checks("check_person_references")

        errors, text = self.report(checker)

        self.assertEqual(errors, 0)
        self.assertEqual(text, "")

    def test_dna_repairs_are_described(self):
        """Each kind of DNA repair is counted and described."""
        test = DNATest()
        test.set_person_handle("missing-person")
        self.add(test)
        ancestor = SharedAncestor()
        ancestor.set_person_handle("missing-person")
        dnamatch = DNAMatch()
        dnamatch.set_subject_test_handle("missing-test")
        dnamatch.add_shared_ancestor(ancestor)
        self.add(dnamatch)

        checker = self.run_checks(
            "check_dnatest_references", "check_dnamatch_references"
        )
        errors, text = self.report(checker)

        self.assertEqual(errors, 3)
        self.assertIn(
            "1 DNA test referred to a missing person, the reference was removed", text
        )
        self.assertIn("1 DNA test was referenced but not found", text)
        self.assertIn("1 DNA match had a shared ancestor referring to", text)

    def test_reference_repairs_are_described(self):
        """Each kind of missing reference is counted and described."""
        person = Person()
        person.add_citation("missing-citation")
        person.add_note("missing-note")
        person_ref = PersonRef()
        person_ref.set_reference_handle("missing-person")
        person.add_person_ref(person_ref)
        self.add(person)

        checker = self.run_checks(
            "check_person_references",
            "check_citation_references",
            "check_note_references",
        )
        errors, text = self.report(checker)

        self.assertIn("1 person was referenced but not found", text)
        self.assertIn("1 citation was referenced but not found", text)
        self.assertIn("1 source was referenced but not found", text)
        self.assertIn("1 note object was referenced but not found", text)
        self.assertEqual(errors, 4)

    def test_tag_repair_is_described_once(self):
        """A missing tag is described once."""
        person = Person()
        person.add_tag("missing-tag")
        self.add(person)

        checker = self.run_checks("check_tag_references")
        _errors, text = self.report(checker)

        self.assertEqual(text.count("1 tag object was referenced but not found"), 1)

    def test_duplicate_spouse_is_named(self):
        """A person with a repeated family is named with the removed link."""
        person = make_person("Repeated")
        person_handle = self.add(person)
        family = Family()
        family.set_father_handle(person_handle)
        family_handle = self.add(family)
        person.set_family_handle_list([family_handle, family_handle])
        self.commit(person)

        checker = self.run_checks("cleanup_duplicate_spouses")
        _errors, text = self.report(checker)

        self.assertIn("1 duplicate spouse/family link was removed\n", text)
        self.assertIn(
            "\t%s listed the family of %s more than once\n"
            % (
                person.get_primary_name().get_name(),
                family_name(self.get(Family, family_handle), self.db),
            ),
            text,
        )
        self.assertNotIn("restored", text)


if __name__ == "__main__":
    unittest.main()
