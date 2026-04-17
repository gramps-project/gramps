#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026  Gabriel Rios
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

from __future__ import annotations

from gramps.gen.lib import (
    Person,
    Family,
    ChildRef,
    EventRef,
    EventRoleType,
    EventType,
    Attribute,
)
from gramps.gen.errors import HandleError

from . import _
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.utils import get_fsftid
from gramps.gen.fs.fs_import.names import add_names
from gramps.gen.fs.fs_import.events import add_event
from gramps.gen.fs.fs_import.notes import add_note
from gramps.gen.fs.fs_import.sources import add_source


class FSToGrampsImporter:
    """
    Core FamilySearch -> Gramps importer logic.

    GUI/session/progress orchestration lives in gramps.gui.fs.fs_import.importer.
    """

    fs_TreeImp = None
    active_handle = None

    def __init__(self):
        self.noreimport = False
        self.asc = 1
        self.desc = 1
        self.include_spouses = False  # never auto-import spouses
        self.include_notes = False
        self.include_sources = False
        self.verbosity = 0
        self.added_person = False
        self.refresh_signals = True
        self.txn = None
        self.dbstate = None
        self.FS_ID = None
        # used by actions.py flows to avoid double-linking
        self.import_cpr = True

    # ---- helpers ----------------------------------------------------------

    def _find_couple_family(self, father_h, mother_h):
        # return an existing Family with exactly these parents if any
        if father_h:
            father = self.dbstate.db.get_person_from_handle(father_h)
            for family_handle in list(father.get_family_handle_list() or []):
                if not family_handle:
                    continue
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if (
                    family
                    and family.get_mother_handle() == mother_h
                    and family.get_father_handle() == father_h
                ):
                    return family

        if mother_h:
            mother = self.dbstate.db.get_person_from_handle(mother_h)
            for family_handle in list(mother.get_family_handle_list() or []):
                if not family_handle:
                    continue
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if (
                    family
                    and family.get_father_handle() == father_h
                    and family.get_mother_handle() == mother_h
                ):
                    return family

        return None

    def _strip_unknowns(self, data):
        key = "PersonInfo:visibleToAllWhenUsingFamilySearchApps"
        if isinstance(data, dict):
            data.pop(key, None)
            for value in list(data.values()):
                self._strip_unknowns(value)
        elif isinstance(data, list):
            for value in list(data):
                self._strip_unknowns(value)

    def _ensure_root_parent_link(self, root_fsid: str):
        # if only one parent is imported, ensure the selected/root child is linked
        # by generating/reusing a one-parent Family
        if not root_fsid:
            return

        child_h = fs_utilities.FS_INDEX_PEOPLE.get(root_fsid)
        if not child_h:
            return

        child = self.dbstate.db.get_person_from_handle(child_h)

        # If already linked to some parent family nothing to do.
        if child.get_parent_family_handle_list():
            return

        father_h = None
        mother_h = None

        for cpr in list(
            getattr(self.fs_TreeImp, "childAndParentsRelationships", []) or []
        ):
            if cpr.child and cpr.child.resourceId == root_fsid:
                father_h = (
                    fs_utilities.FS_INDEX_PEOPLE.get(cpr.parent1.resourceId)
                    if cpr.parent1
                    else None
                )
                mother_h = (
                    fs_utilities.FS_INDEX_PEOPLE.get(cpr.parent2.resourceId)
                    if cpr.parent2
                    else None
                )
                break

        if not father_h and not mother_h:
            return

        family = self._find_couple_family(father_h, mother_h)
        if not family:
            family = Family()
            family.set_father_handle(father_h)
            family.set_mother_handle(mother_h)
            self.dbstate.db.add_family(family, self.txn)
            self.dbstate.db.commit_family(family, self.txn)

            if father_h:
                father = self.dbstate.db.get_person_from_handle(father_h)
                father.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(father, self.txn)

            if mother_h:
                mother = self.dbstate.db.get_person_from_handle(mother_h)
                mother.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(mother, self.txn)

        if not any(
            child_ref.get_reference_handle() == child_h
            for child_ref in list(family.get_child_ref_list() or [])
        ):
            child_ref = ChildRef()
            child_ref.set_reference_handle(child_h)
            family.add_child_ref(child_ref)
            self.dbstate.db.commit_family(family, self.txn)
            child.add_parent_family_handle(family.get_handle())
            self.dbstate.db.commit_person(child, self.txn)

    # ---- core import steps ------------------------------------------------

    def add_person(self, db, txn, fs_person):
        fsid = fs_person.id

        gr_person = None
        gr_handle = fs_utilities.FS_INDEX_PEOPLE.get(fsid)

        if gr_handle:
            try:
                gr_person = db.get_person_from_handle(gr_handle)
            except HandleError:
                fs_utilities.FS_INDEX_PEOPLE.pop(fsid, None)
                gr_handle = None

        # If the mapping was stale but the person may still exist, try to find by FSID
        if gr_person is None:
            try:
                for handle in db.get_person_handles():
                    person = db.get_person_from_handle(handle)
                    if get_fsftid(person) == fsid:
                        gr_person = person
                        fs_utilities.FS_INDEX_PEOPLE[fsid] = person.handle
                        gr_handle = person.handle
                        break
            except Exception:
                pass

        # create if still not found
        if gr_person is None:
            gr_person = Person()
            add_names(db, txn, fs_person, gr_person)

            if not fs_person.gender:
                gr_person.set_gender(Person.UNKNOWN)
            elif fs_person.gender.type == "http://gedcomx.org/Male":
                gr_person.set_gender(Person.MALE)
            elif fs_person.gender.type == "http://gedcomx.org/Female":
                gr_person.set_gender(Person.FEMALE)
            else:
                gr_person.set_gender(Person.UNKNOWN)

            db.add_person(gr_person, txn)
            self.added_person = True
            fs_utilities.link_gramps_fs_id(db, gr_person, fsid)
            fs_utilities.FS_INDEX_PEOPLE[fsid] = gr_person.handle
        elif self.noreimport:
            return

        for fs_fact in list(getattr(fs_person, "facts", []) or []):
            event = add_event(db, txn, fs_fact, gr_person)

            link_ref = None
            for event_ref in list(gr_person.get_event_ref_list() or []):
                if event_ref.ref == event.handle:
                    link_ref = event_ref
                    break

            if link_ref is None:
                link_ref = EventRef()
                link_ref.set_role(EventRoleType.PRIMARY)
                link_ref.set_reference_handle(event.get_handle())
                db.commit_event(event, txn)
                gr_person.add_event_ref(link_ref)

            event_type = (
                int(event.type) if hasattr(event.type, "__int__") else event.type
            )
            if event_type == EventType.BIRTH:
                gr_person.set_birth_ref(link_ref)
            elif event_type == EventType.DEATH:
                gr_person.set_death_ref(link_ref)

            db.commit_person(gr_person, txn)

        for fs_note in list(getattr(fs_person, "notes", []) or []):
            note = add_note(db, txn, fs_note, gr_person.note_list)
            gr_person.add_note(note.handle)

        for fs_src in list(getattr(fs_person, "sources", []) or []):
            add_source(
                db, txn, fs_src.descriptionId, gr_person, gr_person.citation_list
            )

        db.commit_person(gr_person, txn)

    def add_child(self, fs_cpr):
        if fs_cpr.parent1:
            father_h = fs_utilities.FS_INDEX_PEOPLE.get(fs_cpr.parent1.resourceId)
        else:
            father_h = None

        if fs_cpr.parent2:
            mother_h = fs_utilities.FS_INDEX_PEOPLE.get(fs_cpr.parent2.resourceId)
        else:
            mother_h = None

        child_h = (
            fs_utilities.FS_INDEX_PEOPLE.get(fs_cpr.child.resourceId)
            if fs_cpr.child
            else None
        )

        if child_h and (child_h == father_h or child_h == mother_h):
            print(_("Skipping invalid relationship: child equals a parent"))
            return

        if not (father_h or mother_h):
            print(
                _("Possibly parentless family - Need at least one known parent locally")
            )
            return

        family = self._find_couple_family(father_h, mother_h)
        if not family:
            family = Family()
            family.set_father_handle(father_h)
            family.set_mother_handle(mother_h)
            self.dbstate.db.add_family(family, self.txn)
            self.dbstate.db.commit_family(family, self.txn)

            if father_h:
                father = self.dbstate.db.get_person_from_handle(father_h)
                father.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(father, self.txn)

            if mother_h:
                mother = self.dbstate.db.get_person_from_handle(mother_h)
                mother.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(mother, self.txn)

        if not child_h:
            return

        if not any(
            child_ref.get_reference_handle() == child_h
            for child_ref in list(family.get_child_ref_list() or [])
        ):
            child_ref = ChildRef()
            child_ref.set_reference_handle(child_h)
            family.add_child_ref(child_ref)
            self.dbstate.db.commit_family(family, self.txn)

            child = self.dbstate.db.get_person_from_handle(child_h)
            child.add_parent_family_handle(family.get_handle())
            self.dbstate.db.commit_person(child, self.txn)

    def add_family(self, fs_fam):
        family = None
        father_h = fs_utilities.FS_INDEX_PEOPLE.get(fs_fam.person1.resourceId)
        mother_h = fs_utilities.FS_INDEX_PEOPLE.get(fs_fam.person2.resourceId)

        father = self.dbstate.db.get_person_from_handle(father_h) if father_h else None
        mother = self.dbstate.db.get_person_from_handle(mother_h) if mother_h else None

        if father_h and mother_h and father_h == mother_h:
            print(_("Skipping invalid couple: same person as both parents"))
            return

        if father_h or mother_h:
            family = self._find_couple_family(father_h, mother_h)

        if not family:
            if father:
                for family_handle in list(father.get_family_handle_list() or []):
                    if not family_handle:
                        continue
                    existing_family = self.dbstate.db.get_family_from_handle(
                        family_handle
                    )
                    if not existing_family:
                        continue
                    if existing_family.get_mother_handle() == mother_h:
                        family = existing_family
                        break
                    family_fsid = get_fsftid(existing_family)
                    if family_fsid == fs_fam.id:
                        family = existing_family
                        break

            if not family and mother:
                for family_handle in list(mother.get_family_handle_list() or []):
                    if not family_handle:
                        continue
                    existing_family = self.dbstate.db.get_family_from_handle(
                        family_handle
                    )
                    if not existing_family:
                        continue
                    if existing_family.get_father_handle() == father_h:
                        family = existing_family
                        break
                    family_fsid = get_fsftid(existing_family)
                    if family_fsid == fs_fam.id:
                        family = existing_family
                        break

        if not father_h and not mother_h:
            print(_("Possible parentless family?"))
            return

        if family and not family.get_father_handle() and father_h:
            family.set_father_handle(father_h)
            if father:
                father.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(father, self.txn)

        if family and not family.get_mother_handle() and mother_h:
            family.set_mother_handle(mother_h)
            if mother:
                mother.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(mother, self.txn)

        if not family:
            family = Family()
            family.set_father_handle(father_h)
            family.set_mother_handle(mother_h)

            attr = Attribute()
            attr.set_type("_FSFTID")
            attr.set_value(fs_fam.id)
            family.add_attribute(attr)

            self.dbstate.db.add_family(family, self.txn)
            self.dbstate.db.commit_family(family, self.txn)

            if father:
                father.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(father, self.txn)

            if mother:
                mother.add_family_handle(family.get_handle())
                self.dbstate.db.commit_person(mother, self.txn)

        for fs_fact in list(getattr(fs_fam, "facts", []) or []):
            event = add_event(self.dbstate.db, self.txn, fs_fact, family)
            if not any(
                event_ref.ref == event.handle
                for event_ref in list(family.get_event_ref_list() or [])
            ):
                event_ref = EventRef()
                event_ref.set_role(EventRoleType.FAMILY)
                event_ref.set_reference_handle(event.get_handle())
                self.dbstate.db.commit_event(event, self.txn)
                family.add_event_ref(event_ref)

        self.dbstate.db.commit_family(family, self.txn)

        for fs_note in list(getattr(fs_fam, "notes", []) or []):
            note = add_note(self.dbstate.db, self.txn, fs_note, family.note_list)
            family.add_note(note.handle)

        for fs_src in list(getattr(fs_fam, "sources", []) or []):
            add_source(
                self.dbstate.db,
                self.txn,
                fs_src.descriptionId,
                family,
                family.citation_list,
            )

        self.dbstate.db.commit_family(family, self.txn)
