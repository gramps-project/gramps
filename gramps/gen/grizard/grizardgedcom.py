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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
GEDCOM implementation of the Grizard import framework.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import copy
import logging
import os
from typing import Any

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db.base import DbWriteBase
from gramps.gen.db.txn import DbTxn
from gramps.gen.db.utils import import_as_dict, make_database
from gramps.gen.config import config
from gramps.gen.plug import BasePluginManager
from gramps.gen.types import PersonHandle
from gramps.gen.user import User
from gramps.gen.lib import (
    Person,
    Event,
    EventRef,
    Place,
    Name,
    Family,
    ChildRef,
    Attribute,
    EventRoleType,
    EventType,
)
from gramps.gen.soundex import soundex
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Local imports
#
# -------------------------------------------------------------------------
from .grizard import (
    GrizardBase,
    GrizardCompareRow,
    CandidateMatcher,
    surname_prefix_text,
    surname_text,
    safe_get_event,
    safe_get_family,
    safe_get_person,
    safe_get_place,
    safe_get_source,
)

# -------------------------------------------------------------------------
#
# Log
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(__name__)

_ = glocale.translation.gettext


# ------------------------------------------------------------
#
# GedGrizard
#
# ------------------------------------------------------------
class GedGrizard(GrizardBase):
    """
    Concrete Grizard implementation for importing data from GEDCOM (.ged)
    and Gramps XML (.gramps, .xml) files.
    """

    # File extensions (without dot) treated as Gramps XML even though no
    # ``xml`` importer is registered. ``import_as_dict`` dispatches purely
    # on extension, so a bare ``.xml`` holding Gramps XML would otherwise
    # fail to load.
    GRAMPS_XML_EXTENSIONS = frozenset({"gramps", "xml"})

    def __init__(self, db: DbWriteBase) -> None:
        """
        Initialize the GedGrizard.

        :param db: The target database to merge data into.
        """
        super().__init__(db)

    def _is_gramps_xml_file(self, path: str) -> bool:
        """
        Return True if the file looks like Gramps XML.

        Files with a ``.gramps`` extension are trusted by extension (the
        registered ``gramps`` importer only reads Gramps XML). Anything
        else is sniffed: the first bytes must contain a ``<database``
        element in the Gramps XML namespace.
        """
        extension = os.path.splitext(os.path.basename(path))[1][1:].lower()
        if extension == "gramps":
            return True
        try:
            with open(path, "rb") as handle:
                head = handle.read(4096)
        except OSError:
            return False
        if b"<database" not in head:
            return False
        return b"gramps-project.org/xml" in head

    def _load_gramps_xml(self, path: str, user: User) -> DbWriteBase | None:
        """
        Load Gramps XML from any extension into an in-memory database.

        Routes the registered ``gramps`` importer plugin at the file in
        place (no temp copy); only falls back to ``import_as_dict`` when
        the plugin manager has no importers registered (e.g. bare
        ``gen``-level unit contexts).
        """
        db = make_database("sqlite")
        db.load(":memory:")
        db.set_feature("skip-import-additions", True)
        db.set_prefixes(
            config.get("preferences.iprefix"),
            config.get("preferences.oprefix"),
            config.get("preferences.fprefix"),
            config.get("preferences.sprefix"),
            config.get("preferences.cprefix"),
            config.get("preferences.pprefix"),
            config.get("preferences.eprefix"),
            config.get("preferences.rprefix"),
            config.get("preferences.nprefix"),
        )
        pmgr = BasePluginManager.get_instance()
        for pdata in pmgr.get_reg_importers():
            if pdata.extension == "gramps":
                mod = pmgr.load_plugin(pdata)
                if not mod:
                    break
                import_function = getattr(mod, pdata.import_function)
                try:
                    results = import_function(db, path, user)
                except Exception:
                    LOG.exception("Failed to import Gramps XML file: %s", path)
                    db.close()
                    return None
                if results is None:
                    db.close()
                    return None
                return db
        # No importers registered: fall back to the standard dispatcher,
        # which returns None for unknown extensions.
        db.close()
        return import_as_dict(path, user)

    def _connect(self, **kwargs: Any) -> bool:
        """
        Configure connection details by supplying a path to a GEDCOM file.

        :param gedcom_path: Path to the GEDCOM file.
        :type gedcom_path: str
        :returns: True if path is valid and file exists.
        :rtype: bool
        """
        gedcom_path = kwargs.get("gedcom_path", "")
        if not gedcom_path or not os.path.isfile(gedcom_path):
            LOG.error("Invalid GEDCOM path: %s", gedcom_path)
            return False

        self.context["gedcom_path"] = gedcom_path
        return True

    def _load(self, **kwargs: Any) -> list[Person]:
        """
        Load source data into an in-memory dictionary database for analysis.

        Supports GEDCOM (``.ged``) and Gramps XML (``.gramps``, plus a
        bare ``.xml`` holding Gramps XML, routed to the ``gramps``
        importer without any temp copy).

        :returns: A list of Person objects loaded from the file.
        :rtype: list[Person]
        """
        gedcom_path = self.context.get("gedcom_path")
        if not gedcom_path:
            raise ValueError("No GEDCOM path configured. Call connect step first.")

        user = User()
        source_db: DbWriteBase | None = None
        extension = os.path.splitext(os.path.basename(gedcom_path))[1][1:].lower()
        if extension in self.GRAMPS_XML_EXTENSIONS or self._is_gramps_xml_file(
            gedcom_path
        ):
            source_db = self._load_gramps_xml(gedcom_path, user)
        else:
            source_db = import_as_dict(gedcom_path, user)
        if not source_db:
            raise RuntimeError("Failed to import GEDCOM file.")

        self.context["source_db"] = source_db

        people: list[Person] = []
        for handle in source_db.iter_person_handles():
            person = safe_get_person(source_db, handle)
            if person:
                people.append(person)

        return people

    def _match(self, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Find potential matching persons in the target database.

        :param source_person_handle: Handle of the person in the source database.
        :type source_person_handle: str
        :param threshold: Minimum matching score required to include a candidate.
        :type threshold: float
        :returns: List of target candidates with details.
        :rtype: list[dict[str, Any]]
        """
        source_person_handle = kwargs.get("source_person_handle")
        if not source_person_handle:
            raise ValueError("source_person_handle parameter is required.")
        try:
            threshold = float(kwargs.get("threshold", 0.5))
        except (TypeError, ValueError):
            threshold = 0.5

        source_db = self.context.get("source_db")
        if not source_db:
            raise ValueError("Source database is not loaded.")

        source_person = safe_get_person(source_db, source_person_handle)
        if not source_person:
            raise ValueError(
                f"Source person not found for handle: {source_person_handle}"
            )

        matcher = CandidateMatcher(self.db)
        matches = matcher.find_matches(
            source_person, threshold=threshold, source_db=source_db
        )

        candidates: list[dict[str, Any]] = []
        for target_handle, score in matches:
            try:
                target_person = safe_get_person(self.db, target_handle)
                if target_person:
                    name_str = glocale.translation.gettext(
                        target_person.get_primary_name().get_name()
                    )
                    # Use formatted birth year if available
                    birth_ref = target_person.get_birth_ref()
                    birth_yr = ""
                    if birth_ref:
                        birth_evt = safe_get_event(self.db, birth_ref.ref)
                        if birth_evt:
                            birth_yr = str(birth_evt.get_date_object().get_year() or "")

                    candidates.append(
                        {
                            "handle": target_handle,
                            "score": score,
                            "name": name_str,
                            "birth_year": birth_yr,
                        }
                    )
            except Exception:
                continue

        return candidates

    def _compare(self, **kwargs: Any) -> list[GrizardCompareRow]:
        """
        Generate comparative side-by-side rows between a source person and target person.

        :param source_person_handle: Handle of the person in the source database.
        :type source_person_handle: str
        :param target_person_handle: Handle of the person in the target database.
        :type target_person_handle: PersonHandle
        :returns: List of comparison rows.
        :rtype: list[GrizardCompareRow]
        """
        source_person_handle = kwargs.get("source_person_handle")
        target_person_handle = kwargs.get("target_person_handle")

        if not source_person_handle or not target_person_handle:
            raise ValueError(
                "Both source_person_handle and target_person_handle are required."
            )

        source_db = self.context.get("source_db")
        if not source_db:
            raise ValueError("Source database is not loaded.")

        s_person = safe_get_person(source_db, source_person_handle)
        t_person = safe_get_person(self.db, target_person_handle)

        if not s_person or not t_person:
            raise ValueError("Source or target person record not found.")

        rows: list[GrizardCompareRow] = []

        # Helper for statuses
        def get_status(s_val: str, t_val: str) -> str:
            if not s_val and not t_val:
                return "match"
            if s_val and not t_val:
                return "source_only"
            if t_val and not s_val:
                return "target_only"
            if s_val.strip().lower() == t_val.strip().lower():
                return "match"
            return "differ"

        # 1. Compare Given Name
        s_given = s_person.get_primary_name().first_name
        t_given = t_person.get_primary_name().first_name
        rows.append(
            GrizardCompareRow(
                status=get_status(s_given, t_given),
                field=_("Given Name"),
                source_val=s_given,
                target_val=t_given,
                field_type="given_name",
            )
        )

        # 2. Compare Surnames
        s_surname = surname_text(s_person.get_primary_name())
        t_surname = surname_text(t_person.get_primary_name())
        rows.append(
            GrizardCompareRow(
                status=get_status(s_surname, t_surname),
                field=_("Surname"),
                source_val=s_surname,
                target_val=t_surname,
                field_type="surname",
            )
        )

        # 2b. Compare Surname Prefixes (GEDCOM SPFX, e.g. "Vrow")
        s_prefix = surname_prefix_text(s_person.get_primary_name())
        t_prefix = surname_prefix_text(t_person.get_primary_name())
        rows.append(
            GrizardCompareRow(
                status=get_status(s_prefix, t_prefix),
                field=_("Surname Prefix"),
                source_val=s_prefix,
                target_val=t_prefix,
                field_type="surname_prefix",
            )
        )

        # 3. Compare Gender
        def format_gender(gender_val: int) -> str:
            genders = {
                Person.MALE: _("Male"),
                Person.FEMALE: _("Female"),
                Person.OTHER: _("Other"),
                Person.UNKNOWN: _("Unknown"),
            }
            return genders.get(gender_val, _("Unknown"))

        s_gender_str = format_gender(s_person.get_gender())
        t_gender_str = format_gender(t_person.get_gender())
        rows.append(
            GrizardCompareRow(
                status=get_status(s_gender_str, t_gender_str),
                field=_("Gender"),
                source_val=s_gender_str,
                target_val=t_gender_str,
                field_type="gender",
            )
        )

        # Helper to extract event details
        def get_event_details(
            db: DbWriteBase, person: Person, event_type_val: int
        ) -> tuple[str, str, str]:
            for ref in person.get_event_ref_list():
                try:
                    event = safe_get_event(db, ref.ref)
                    if event and event.get_type() == event_type_val:
                        dt_str = glocale.date_displayer.display(event.get_date_object())
                        pl_handle = event.get_place_handle()
                        pl_title = ""
                        if pl_handle:
                            place = safe_get_place(db, pl_handle)
                            if place:
                                pl_title = place.get_title()
                        return dt_str, pl_title, event.handle
                except Exception:
                    continue
            return "", "", ""

        # 4. Compare Birth Event
        s_birth_dt, s_birth_pl, s_birth_h = get_event_details(
            source_db, s_person, EventType.BIRTH
        )
        t_birth_dt, t_birth_pl, t_birth_h = get_event_details(
            self.db, t_person, EventType.BIRTH
        )

        s_birth_val = f"{s_birth_dt} ({s_birth_pl})" if s_birth_pl else s_birth_dt
        t_birth_val = f"{t_birth_dt} ({t_birth_pl})" if t_birth_pl else t_birth_dt

        rows.append(
            GrizardCompareRow(
                status=get_status(s_birth_val, t_birth_val),
                field=_("Birth"),
                source_val=s_birth_val,
                target_val=t_birth_val,
                source_date=s_birth_dt,
                target_date=t_birth_dt,
                field_type="birth_event",
                extra_data={"source_handle": s_birth_h, "target_handle": t_birth_h},
            )
        )

        # 5. Compare Death Event
        s_death_dt, s_death_pl, s_death_h = get_event_details(
            source_db, s_person, EventType.DEATH
        )
        t_death_dt, t_death_pl, t_death_h = get_event_details(
            self.db, t_person, EventType.DEATH
        )

        s_death_val = f"{s_death_dt} ({s_death_pl})" if s_death_pl else s_death_dt
        t_death_val = f"{t_death_dt} ({t_death_pl})" if t_death_pl else t_death_dt

        rows.append(
            GrizardCompareRow(
                status=get_status(s_death_val, t_death_val),
                field=_("Death"),
                source_val=s_death_val,
                target_val=t_death_val,
                source_date=s_death_dt,
                target_date=t_death_dt,
                field_type="death_event",
                extra_data={"source_handle": s_death_h, "target_handle": t_death_h},
            )
        )

        return rows

    def _apply(self, **kwargs: Any) -> bool:
        """
        Apply resolutions by updating an existing person or adding as a new person in target db.

        :param source_person_handle: Handle of the person in the source database.
        :type source_person_handle: str
        :param target_person_handle: Handle of the person in target db, or None to add new.
        :type target_person_handle: PersonHandle | None
        :param resolutions: Dictionary of field resolutions (e.g. {'birth_event': 'source'}).
        :type resolutions: dict[str, str]
        :returns: True if successfully applied and committed.
        :rtype: bool
        """
        source_person_handle = kwargs.get("source_person_handle")
        target_person_handle = kwargs.get("target_person_handle")
        resolutions = kwargs.get("resolutions", {})

        if not source_person_handle:
            raise ValueError("source_person_handle is required.")

        source_db = self.context.get("source_db")
        if not source_db:
            raise ValueError("Source database is not loaded.")

        s_person = safe_get_person(source_db, source_person_handle)
        if not s_person:
            raise ValueError("Source person not found.")

        # Helper to get/create place
        def get_or_create_place(s_pl_handle: str | None, trans: Any) -> str | None:
            if not s_pl_handle:
                return None
            try:
                s_place = safe_get_place(source_db, s_pl_handle)
                if not s_place:
                    return None

                # Check if place with same title already exists in target
                title = s_place.get_title()
                for h in self.db.iter_place_handles():
                    t_pl = safe_get_place(self.db, h)
                    if t_pl and t_pl.get_title() == title:
                        return h

                new_place = copy.deepcopy(s_place)
                self.db.add_place(new_place, trans)
                return new_place.handle
            except Exception:
                pass
            return None

        # Helper to copy note
        def copy_note(s_note_handle: str | None, trans: Any) -> str | None:
            if not s_note_handle:
                return None
            try:
                if self.db.get_note_from_handle(s_note_handle):
                    return s_note_handle
            except Exception:
                pass
            try:
                s_note = source_db.get_note_from_handle(s_note_handle)
                if not s_note:
                    return None
                new_note = copy.deepcopy(s_note)
                self.db.add_note(new_note, trans)
                return new_note.handle
            except Exception:
                pass
            return None

        # Helper to copy media
        def copy_media(s_media_handle: str | None, trans: Any) -> str | None:
            if not s_media_handle:
                return None
            try:
                if self.db.get_media_from_handle(s_media_handle):
                    return s_media_handle
            except Exception:
                pass
            try:
                s_media = source_db.get_media_from_handle(s_media_handle)
                if not s_media:
                    return None
                new_media = copy.deepcopy(s_media)
                new_notes = []
                for nh in new_media.get_note_list():
                    new_nh = copy_note(nh, trans)
                    if new_nh:
                        new_notes.append(new_nh)
                new_media.set_note_list(new_notes)

                self.db.add_media(new_media, trans)
                return new_media.handle
            except Exception:
                pass
            return None

        # Helper to copy repository
        def copy_repository(s_repo_handle: str | None, trans: Any) -> str | None:
            if not s_repo_handle:
                return None
            try:
                if self.db.get_repository_from_handle(s_repo_handle):
                    return s_repo_handle
            except Exception:
                pass
            try:
                s_repo = source_db.get_repository_from_handle(s_repo_handle)
                if not s_repo:
                    return None
                new_repo = copy.deepcopy(s_repo)
                new_notes = []
                for nh in new_repo.get_note_list():
                    new_nh = copy_note(nh, trans)
                    if new_nh:
                        new_notes.append(new_nh)
                new_repo.set_note_list(new_notes)

                self.db.add_repository(new_repo, trans)
                return new_repo.handle
            except Exception:
                pass
            return None

        # Helper to copy source
        def copy_source(s_source_handle: str | None, trans: Any) -> str | None:
            if not s_source_handle:
                return None
            try:
                if safe_get_source(self.db, s_source_handle):
                    return s_source_handle
            except Exception:
                pass
            try:
                s_source = safe_get_source(source_db, s_source_handle)
                if not s_source:
                    return None
                new_source = copy.deepcopy(s_source)
                new_notes = []
                for nh in new_source.get_note_list():
                    new_nh = copy_note(nh, trans)
                    if new_nh:
                        new_notes.append(new_nh)
                new_source.set_note_list(new_notes)

                for mref in new_source.media_list:
                    new_mh = copy_media(mref.get_reference_handle(), trans)
                    if new_mh:
                        mref.set_reference_handle(new_mh)

                for rref in new_source.reporef_list:
                    new_rh = copy_repository(rref.get_reference_handle(), trans)
                    if new_rh:
                        rref.set_reference_handle(new_rh)

                self.db.add_source(new_source, trans)
                return new_source.handle
            except Exception:
                pass
            return None

        # Helper to copy citation
        def copy_citation(s_citation_handle: str | None, trans: Any) -> str | None:
            if not s_citation_handle:
                return None
            try:
                if self.db.get_citation_from_handle(s_citation_handle):
                    return s_citation_handle
            except Exception:
                pass
            try:
                s_citation = source_db.get_citation_from_handle(s_citation_handle)
                if not s_citation:
                    return None
                new_citation = copy.deepcopy(s_citation)
                new_notes = []
                for nh in new_citation.get_note_list():
                    new_nh = copy_note(nh, trans)
                    if new_nh:
                        new_notes.append(new_nh)
                new_citation.set_note_list(new_notes)

                for mref in new_citation.media_list:
                    new_mh = copy_media(mref.get_reference_handle(), trans)
                    if new_mh:
                        mref.set_reference_handle(new_mh)

                new_sh = copy_source(new_citation.get_reference_handle(), trans)
                if new_sh:
                    new_citation.set_reference_handle(new_sh)

                self.db.add_citation(new_citation, trans)
                return new_citation.handle
            except Exception:
                pass
            return None

        # Helper to resolve references on an Event
        def resolve_references_for_event(new_event: Any, trans: Any) -> None:
            new_notes = []
            for nh in new_event.get_note_list():
                new_nh = copy_note(nh, trans)
                if new_nh:
                    new_notes.append(new_nh)
            new_event.set_note_list(new_notes)

            for mref in new_event.media_list:
                new_mh = copy_media(mref.get_reference_handle(), trans)
                if new_mh:
                    mref.set_reference_handle(new_mh)

            new_citations = []
            for ch in new_event.get_citation_list():
                new_ch = copy_citation(ch, trans)
                if new_ch:
                    new_citations.append(new_ch)
            new_event.set_citation_list(new_citations)

        # Helper to resolve references on a Person
        def resolve_references_for_person(new_person: Any, trans: Any) -> None:
            new_notes = []
            for nh in new_person.get_note_list():
                new_nh = copy_note(nh, trans)
                if new_nh:
                    new_notes.append(new_nh)
            new_person.set_note_list(new_notes)

            for mref in new_person.media_list:
                new_mh = copy_media(mref.get_reference_handle(), trans)
                if new_mh:
                    mref.set_reference_handle(new_mh)

            new_citations = []
            for ch in new_person.get_citation_list():
                new_ch = copy_citation(ch, trans)
                if new_ch:
                    new_citations.append(new_ch)
            new_person.set_citation_list(new_citations)

        # Helper to copy event
        def copy_event(s_evt_handle: str | None, trans: Any) -> str | None:
            if not s_evt_handle:
                return None
            try:
                s_event = safe_get_event(source_db, s_evt_handle)
                if not s_event:
                    return None

                new_event = copy.deepcopy(s_event)
                new_place = get_or_create_place(s_event.get_place_handle(), trans)
                new_event.set_place_handle(new_place)
                resolve_references_for_event(new_event, trans)
                self.db.add_event(new_event, trans)
                return new_event.handle
            except Exception:
                pass
            return None

        with DbTxn(_("Grizard Data Merge"), self.db) as trans:
            if target_person_handle is None:
                # Add as entirely new person
                new_person = copy.deepcopy(s_person)
                resolve_references_for_person(new_person, trans)
                # Copy birth event if exists
                s_birth_ref = s_person.get_birth_ref()
                if s_birth_ref:
                    t_birth_h = copy_event(s_birth_ref.ref, trans)
                    if t_birth_h:
                        new_birth_ref = EventRef()
                        new_birth_ref.ref = t_birth_h
                        new_birth_ref.set_role(EventRoleType.PRIMARY)
                        # We must clear the existing event ref list and set the correct birth ref
                        # In Gramps, birth/death references reside in event_ref_list.
                        # set_birth_ref internally manages the ref.
                        new_person.set_birth_ref(new_birth_ref)

                s_death_ref = s_person.get_death_ref()
                if s_death_ref:
                    t_death_h = copy_event(s_death_ref.ref, trans)
                    if t_death_h:
                        new_death_ref = EventRef()
                        new_death_ref.ref = t_death_h
                        new_death_ref.set_role(EventRoleType.PRIMARY)
                        new_person.set_death_ref(new_death_ref)

                self.db.add_person(new_person, trans)
                LOG.info("Added new person: %s", new_person.handle)
            else:
                # Merge into existing target person
                t_person = safe_get_person(self.db, target_person_handle)
                if not t_person:
                    return False

                # Apply choices
                # 1. Given Name
                if resolutions.get("given_name") == "source":
                    t_person.get_primary_name().first_name = (
                        s_person.get_primary_name().first_name
                    )

                # 2. Surname
                if resolutions.get("surname") == "source":
                    # Clear target surname list and copy source list
                    t_person.get_primary_name().surname_list = copy.deepcopy(
                        s_person.get_primary_name().surname_list
                    )

                # 2b. Surname Prefix (a GEDCOM SPFX value lives on the
                # Surname itself, so only the prefixes of the surnames
                # present on both sides are copied; the whole list is
                # already copied when the surname row was chosen)
                if (
                    resolutions.get("surname_prefix") == "source"
                    and resolutions.get("surname") != "source"
                ):
                    s_list = s_person.get_primary_name().surname_list
                    t_list = t_person.get_primary_name().surname_list
                    for idx, t_surn in enumerate(t_list):
                        if idx < len(s_list):
                            t_surn.set_prefix(s_list[idx].get_prefix())

                # 3. Gender
                if resolutions.get("gender") == "source":
                    t_person.set_gender(s_person.get_gender())

                # Helper to extract event details to match comparison
                def get_source_event_handle(
                    person: Person, event_type_val: int
                ) -> str | None:
                    for ref in person.get_event_ref_list():
                        try:
                            event = safe_get_event(source_db, ref.ref)
                            if event and event.get_type() == event_type_val:
                                return event.handle
                        except Exception:
                            continue
                    return None

                # 4. Birth Event
                if resolutions.get("birth_event") == "source":
                    s_birth_h = get_source_event_handle(s_person, EventType.BIRTH)
                    t_birth_h = copy_event(s_birth_h, trans)
                    if t_birth_h:
                        new_birth_ref = EventRef()
                        new_birth_ref.ref = t_birth_h
                        new_birth_ref.set_role(EventRoleType.PRIMARY)
                        t_person.set_birth_ref(new_birth_ref)

                # 5. Death Event
                if resolutions.get("death_event") == "source":
                    s_death_h = get_source_event_handle(s_person, EventType.DEATH)
                    t_death_h = copy_event(s_death_h, trans)
                    if t_death_h:
                        new_death_ref = EventRef()
                        new_death_ref.ref = t_death_h
                        new_death_ref.set_role(EventRoleType.PRIMARY)
                        t_person.set_death_ref(new_death_ref)

                # Helpers for field-level items beyond the standard rows
                def best_target_person(s_handle: str) -> str | None:
                    """
                    Find the target person that best matches the source
                    person with the given handle.
                    """
                    rel = safe_get_person(source_db, s_handle)
                    if not rel:
                        return None
                    matches = CandidateMatcher(self.db).find_matches(
                        rel, threshold=0.5, source_db=source_db
                    )
                    if not matches:
                        return None
                    matches.sort(key=lambda m: m[1], reverse=True)
                    return matches[0][0]

                def ensure_parent_family(trans: Any) -> Family:
                    """
                    Return the target person's first parent family,
                    creating it (with the target person as child) if
                    needed.
                    """
                    for fh in t_person.get_parent_family_handle_list():
                        fam = safe_get_family(self.db, fh)
                        if fam:
                            return fam
                    fam = Family()
                    child_ref = ChildRef()
                    child_ref.ref = t_person.handle
                    fam.add_child_ref(child_ref)
                    self.db.add_family(fam, trans)
                    t_person.add_parent_family_handle(fam.handle)
                    return fam

                def source_fs_id() -> str:
                    """
                    Return the FamilySearch ID of the source person from
                    the _FSFTID attribute, falling back to the _FSLINK
                    event URL tail.
                    """
                    for attr in s_person.get_attribute_list():
                        try:
                            if str(attr.get_type()) == "_FSFTID":
                                return attr.get_value() or ""
                        except Exception:
                            continue
                    for ref in s_person.get_event_ref_list():
                        try:
                            event = safe_get_event(source_db, ref.ref)
                            if event and str(event.get_type()) == "_FSLINK":
                                desc = event.get_description() or ""
                                tail = desc.rstrip("/").split("/")[-1]
                                if tail and tail != "details":
                                    return tail
                        except Exception:
                            continue
                    return ""

                s_birth_h = get_source_event_handle(s_person, EventType.BIRTH)
                s_death_h = get_source_event_handle(s_person, EventType.DEATH)

                for key, res in resolutions.items():
                    if res != "source" or target_person_handle is None:
                        continue

                    # 6. Other events: key is "event:<source event handle>"
                    if key.startswith("event:"):
                        s_evt_h = key.split(":", 1)[1]
                        if s_evt_h in (s_birth_h, s_death_h):
                            continue
                        t_evt_h = copy_event(s_evt_h, trans)
                        if t_evt_h:
                            event_ref = EventRef()
                            event_ref.ref = t_evt_h
                            event_ref.set_role(EventRoleType.CUSTOM)
                            t_person.add_event_ref(event_ref)
                        continue

                    # 7. FamilySearch ID
                    if key == "fsid":
                        fs_id = source_fs_id()
                        if fs_id:
                            attr = Attribute()
                            attr.set_type("_FSFTID")
                            attr.set_value(fs_id)
                            t_person.add_attribute(attr)
                        continue

                    # 8. Family relations: father/mother, keys are
                    # "<role>:<source person handle>"; relatives are
                    # linked through their best-matching target person.
                    if key.startswith(("father:", "mother:")):
                        role, s_handle = key.split(":", 1)
                        t_rel_h = best_target_person(s_handle)
                        if not t_rel_h:
                            LOG.warning("No target match for %s; skipped", key)
                            continue
                        fam = ensure_parent_family(trans)
                        if role == "father" and not fam.get_father_handle():
                            fam.set_father_handle(t_rel_h)
                        elif role == "mother" and not fam.get_mother_handle():
                            fam.set_mother_handle(t_rel_h)
                        else:
                            LOG.warning("%s slot occupied; skipped", key)
                            continue
                        self.db.commit_family(fam, trans)
                        continue

                    # 9. Spouse, key is "spouse:<source person handle>".
                    if key.startswith("spouse:"):
                        s_handle = key.split(":", 1)[1]
                        t_rel_h = best_target_person(s_handle)
                        t_rel = safe_get_person(self.db, t_rel_h) if t_rel_h else None
                        if not t_rel:
                            LOG.warning("No target match for spouse; skipped")
                            continue
                        spouse_fam: Family | None = None
                        occupied = False
                        for fh in t_person.get_family_handle_list():
                            candidate = safe_get_family(self.db, fh)
                            if not candidate:
                                continue
                            father_h = candidate.get_father_handle()
                            mother_h = candidate.get_mother_handle()
                            if t_rel_h in (father_h, mother_h):
                                occupied = True
                                break
                            if t_person.handle in (father_h, mother_h) and (
                                father_h is None or mother_h is None
                            ):
                                spouse_fam = candidate
                                break
                        if occupied:
                            continue
                        if spouse_fam is None:
                            if t_person.get_gender() == Person.FEMALE:
                                spouse_fam = Family()
                                spouse_fam.set_mother_handle(t_person.handle)
                                spouse_fam.set_father_handle(t_rel_h)
                            else:
                                spouse_fam = Family()
                                spouse_fam.set_father_handle(t_person.handle)
                                spouse_fam.set_mother_handle(t_rel_h)
                            self.db.add_family(spouse_fam, trans)
                            t_person.add_family_handle(spouse_fam.handle)
                        elif spouse_fam.get_father_handle() is None:
                            spouse_fam.set_father_handle(t_rel_h)
                        else:
                            spouse_fam.set_mother_handle(t_rel_h)
                        self.db.commit_family(spouse_fam, trans)
                        t_rel.add_family_handle(spouse_fam.handle)
                        self.db.commit_person(t_rel, trans)
                        continue

                    # 10. Child, key is "child:<source person handle>".
                    if key.startswith("child:"):
                        s_handle = key.split(":", 1)[1]
                        t_rel_h = best_target_person(s_handle)
                        if not t_rel_h:
                            LOG.warning("No target match for child; skipped")
                            continue
                        child_fam: Family | None = None
                        for fh in t_person.get_family_handle_list():
                            candidate = safe_get_family(self.db, fh)
                            if candidate and t_person.handle in (
                                candidate.get_father_handle(),
                                candidate.get_mother_handle(),
                            ):
                                child_fam = candidate
                                break
                        if child_fam is None:
                            child_fam = Family()
                            if t_person.get_gender() == Person.FEMALE:
                                child_fam.set_mother_handle(t_person.handle)
                            else:
                                child_fam.set_father_handle(t_person.handle)
                            self.db.add_family(child_fam, trans)
                            t_person.add_family_handle(child_fam.handle)
                        child_ref = ChildRef()
                        child_ref.ref = t_rel_h
                        child_fam.add_child_ref(child_ref)
                        self.db.commit_family(child_fam, trans)
                        t_rel = safe_get_person(self.db, t_rel_h)
                        if t_rel:
                            t_rel.add_parent_family_handle(child_fam.handle)
                            self.db.commit_person(t_rel, trans)
                        continue

                self.db.commit_person(t_person, trans)
                LOG.info("Merged changes into person: %s", t_person.handle)

        return True
