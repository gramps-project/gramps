#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
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

import logging
from urllib.parse import unquote
from typing import Any, Iterable, List, Optional, Tuple

from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs import tree as fs_tree_mod
from gramps.gen.fs.constants import GEDCOMX_TO_GRAMPS_FACTS

from gramps.gen.lib import EventRoleType, EventType, Person
from gramps.gen.display.place import displayer as _pd
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.const import GRAMPS_LOCALE as glocale

from .formatters import person_dates_str, fs_person_dates_str

logger = logging.getLogger(__name__)

_ = glocale.translation.gettext


def _ensure_fs_people(person_ids: set[str]) -> None:
    wanted = {pid for pid in (person_ids or set()) if pid}
    if not wanted:
        return

    missing = {pid for pid in wanted if pid not in deserialize.Person.index}
    if not missing:
        return

    if getattr(fs_tree_mod, "_fs_session", None) is None:
        return

    try:
        helper_tree = fs_tree_mod.Tree()
        helper_tree._getsources = False
        helper_tree.add_persons(missing)
    except Exception:
        logger.debug(
            "Failed to load related FS people: %s",
            sorted(missing),
            exc_info=True,
        )


def _fs_person_opt(fsid: str):
    if not fsid:
        return None
    _ensure_fs_people({fsid})
    return deserialize.Person.index.get(fsid)


def _fs_person_or_blank(fsid: str):
    return _fs_person_opt(fsid) or deserialize.Person()


def _parent_ids_from_fs_person(fs_person) -> set[str]:
    """
    Collect parent ids from both relationship payload styles.
    """
    parent_ids: set[str] = set()

    for couple in getattr(fs_person, "_parents", []) or []:
        if getattr(couple, "person1", None):
            parent_ids.add(couple.person1.resourceId)
        if getattr(couple, "person2", None):
            parent_ids.add(couple.person2.resourceId)

    for rel in getattr(fs_person, "_parentsCP", []) or []:
        if getattr(rel, "parent1", None):
            parent_ids.add(rel.parent1.resourceId)
        if getattr(rel, "parent2", None):
            parent_ids.add(rel.parent2.resourceId)

    parent_ids.discard(getattr(fs_person, "id", ""))
    return {pid for pid in parent_ids if pid}


def _spouse_ids_from_children(fs_person) -> set[str]:
    """
    Infer spouse ids from child-and-parents relationships.
    """
    fsid = getattr(fs_person, "id", "")
    spouse_ids: set[str] = set()

    for rel in getattr(fs_person, "_childrenCP", []) or []:
        other_parent_id = _other_parent_id_for_child_rel(fsid, rel)
        if other_parent_id:
            spouse_ids.add(other_parent_id)

    spouse_ids.discard(fsid)
    return spouse_ids


def _other_parent_id_for_child_rel(fsid: str, rel) -> str | None:
    """
    Return the other parent id for a child relationship involving fsid.
    """
    parent1 = getattr(getattr(rel, "parent1", None), "resourceId", "")
    parent2 = getattr(getattr(rel, "parent2", None), "resourceId", "")
    if parent1 == fsid:
        return parent2 or ""
    if parent2 == fsid:
        return parent1 or ""
    return None


def _child_other_parent_ids_for_family(db, family, fs_person) -> set[str]:
    """
    Return FamilySearch other-parent groups represented by local children.
    """
    fsid = getattr(fs_person, "id", "")
    other_parent_ids: set[str] = set()
    child_groups: dict[str, set[str]] = {}

    for rel in getattr(fs_person, "_childrenCP", []) or []:
        child_id = getattr(getattr(rel, "child", None), "resourceId", "")
        other_parent_id = _other_parent_id_for_child_rel(fsid, rel)
        if child_id and other_parent_id is not None:
            child_groups.setdefault(child_id, set()).add(other_parent_id)

    for child_ref in family.get_child_ref_list():
        child = db.get_person_from_handle(child_ref.ref)
        child_fsid = fs_utilities.get_fsftid(child)
        other_parent_ids.update(child_groups.get(child_fsid, set()))

    return other_parent_ids


def _pop_fs_couple_for_spouse(fs_spouses, fsid: str, spouse_fsid: str):
    """
    Remove and return the FamilySearch couple relationship for a spouse id.
    """
    for couple in list(fs_spouses):
        person1 = getattr(getattr(couple, "person1", None), "resourceId", "")
        person2 = getattr(getattr(couple, "person2", None), "resourceId", "")
        if (
            (person1 == fsid and person2 == spouse_fsid)
            or (person2 == fsid and person1 == spouse_fsid)
            or (spouse_fsid == "" and (person1 == "" or person2 == ""))
        ):
            fs_spouses.remove(couple)
            return couple
    return None


def _fs_fact_gramps_tag(fs_fact: Any) -> Any:
    """
    Return the Gramps event tag represented by a FamilySearch fact.
    """
    fs_type = str(getattr(fs_fact, "type", "") or "")
    ged_tag = GEDCOMX_TO_GRAMPS_FACTS.get(unquote(fs_type))
    if not ged_tag:
        if fs_type[:6] == "data:,":
            ged_tag = unquote(fs_type[6:])
        else:
            ged_tag = fs_type

    if (
        (ged_tag in (EventType.MARR_ALT, EventType.MARRIAGE))
        and getattr(fs_fact, "attribution", None)
        and getattr(fs_fact.attribution, "changeMessage", None)
    ):
        line = fs_fact.attribution.changeMessage.partition("\n")[0]
        if line[:5] == "http:":
            tag = GEDCOMX_TO_GRAMPS_FACTS.get(line)
        elif line[:5] == "data:":
            tag = unquote(line[6:])
        else:
            tag = None
        if tag:
            ged_tag = GEDCOMX_TO_GRAMPS_FACTS.get(line) or tag

    return ged_tag


def _event_type_value(event_type: Any) -> Any:
    """
    Return the comparable primitive value for a Gramps event type.
    """
    try:
        return int(event_type) or event_type
    except Exception:
        return event_type


def _fs_fact_date(fs_fact: Any) -> str:
    """
    Return the display date for a FamilySearch fact.
    """
    return str(getattr(fs_fact, "date", None) or "")


def _fs_fact_place(fs_fact: Any) -> str:
    """
    Return the display place for a FamilySearch fact.
    """
    place = getattr(fs_fact, "place", None)
    if not place:
        return ""
    return getattr(place, "original", "") or ""


def _fs_fact_value(fs_fact: Any) -> str:
    """
    Return the display value for a FamilySearch fact.
    """
    return getattr(fs_fact, "value", "") or ""


def _fs_fact_signature(fs_fact: Any) -> tuple[Any, str, str, str]:
    """
    Return the value signature used to collapse duplicate FS facts.
    """
    return (
        _fs_fact_gramps_tag(fs_fact),
        _fs_fact_date(fs_fact),
        _fs_fact_place(fs_fact),
        _fs_fact_value(fs_fact),
    )


def _unique_fs_facts(fs_facts: Iterable[Any]) -> list[Any]:
    """
    Return FS facts with duplicate-equivalent rows collapsed.
    """
    facts: list[Any] = []
    seen: set[tuple[Any, str, str, str]] = set()
    for fs_fact in fs_facts or []:
        signature = _fs_fact_signature(fs_fact)
        if signature in seen:
            continue
        seen.add(signature)
        facts.append(fs_fact)
    return facts


def _find_best_fs_fact_match(
    fs_facts: list[Any], gr_tag: Any, gr_date: str, gr_id: str
) -> Any | None:
    """
    Return the best FamilySearch fact for a Gramps family event.
    """
    if gr_id:
        for fs_fact in fs_facts:
            if getattr(fs_fact, "id", None) == gr_id:
                return fs_fact

    fallback = None
    for fs_fact in fs_facts:
        if _fs_fact_gramps_tag(fs_fact) != gr_tag:
            continue
        if fallback is None:
            fallback = fs_fact
        if _fs_fact_date(fs_fact) == gr_date:
            return fs_fact
    return fallback


def compare_gender(gr_person: Person, fs_person) -> Tuple:
    # Compare GRAMPS gender vs FS gender, returns a color-coded tuple
    if gr_person.get_gender() == Person.MALE:
        gr_gender = _("male")
    elif gr_person.get_gender() == Person.FEMALE:
        gr_gender = _("female")
    else:
        gr_gender = _("unknown")

    if fs_person.gender and fs_person.gender.type == "http://gedcomx.org/Male":
        fs_gender = _("male")
    elif fs_person.gender and fs_person.gender.type == "http://gedcomx.org/Female":
        fs_gender = _("female")
    else:
        fs_gender = _("unknown")

    color = "green" if gr_gender == fs_gender else "red"
    return (
        color,
        _("Gender:"),
        "",
        gr_gender,
        "",
        fs_gender,
        "",
        False,
        "gender",
        None,
        None,
    )


def compare_fact(
    db, person: Person, fs_person, gr_event, fs_fact_tag
) -> Optional[Tuple]:
    # Compare a single core fact (Birth, Death, etc.) between GRAMPS and FS
    gr_fact = fs_utilities.get_gramps_event(db, person, EventType(gr_event))
    gr_handle = None
    title = str(EventType(gr_event))

    if gr_fact is not None:
        gr_handle = gr_fact.handle
        gr_date = fs_utilities.gramps_date_to_formal(gr_fact.date)
        if gr_fact.place:
            place = db.get_place_from_handle(gr_fact.place)
            gr_place = _pd.display(db, place)
        else:
            gr_place = ""
    else:
        gr_date = ""
        gr_place = ""

    fs_fact = fs_utilities.get_fs_fact(fs_person, fs_fact_tag)
    fs_id = fs_fact.id if fs_fact else None
    fs_date = ""
    fs_place = ""
    if fs_fact and getattr(fs_fact, "date", None):
        fs_date = str(fs_fact.date)
    if fs_fact and getattr(fs_fact, "place", None):
        fs_place = fs_fact.place.original or ""

    color = (
        "red"
        if (gr_event == EventType.BIRTH or gr_event == EventType.DEATH)
        else "orange"
    )
    if gr_date == fs_date:
        color = "green"

    if gr_date == "" and gr_place == "" and fs_date == "" and fs_place == "":
        return None
    if fs_date == "" and gr_date != "":
        color = "yellow"
    if gr_date == "" and fs_date != "":
        color = "yellow3"

    return (
        color,
        title,
        gr_date,
        gr_place,
        fs_date,
        fs_place,
        "",
        False,
        "fact",
        gr_handle,
        fs_id,
    )


def compare_names(gr_person: Person, fs_person) -> List[Tuple]:
    res: List[Tuple] = []
    gr_primary = gr_person.primary_name
    fs_name = fs_person.preferred_name()

    color = "red"
    if (gr_primary.get_surname() == fs_name.akSurname()) and (
        gr_primary.first_name == fs_name.akGiven()
    ):
        color = "green"

    res.append(
        (
            color,
            _("Name"),
            "",
            gr_primary.get_surname() + ", " + gr_primary.first_name,
            "",
            fs_name.akSurname() + ", " + fs_name.akGiven(),
            "",
            False,
            "primary_name",
            str(gr_primary),
            fs_name.id,
            gr_primary.get_surname(),
            gr_primary.first_name,
        )
    )

    fs_names = fs_person.names.copy()
    if fs_name and fs_name in fs_names:
        fs_names.remove(fs_name)

    for gr_alt in gr_person.alternate_names:
        candidate = deserialize.Name()
        color = "yellow"
        for x in fs_names:
            if (gr_alt.get_surname() == x.akSurname()) and (
                gr_alt.first_name == x.akGiven()
            ):
                candidate = x
                color = "green"
                fs_names.remove(x)
                break
        res.append(
            (
                color,
                "  " + _("Name"),
                "",
                gr_alt.get_surname() + ", " + gr_alt.first_name,
                "",
                candidate.akSurname() + ", " + candidate.akGiven(),
                "",
                False,
                "name",
                str(gr_alt),
                candidate.id,
                gr_alt.get_surname(),
                gr_alt.first_name,
            )
        )

    color = "yellow3"
    for fs_n in fs_names:
        res.append(
            (
                color,
                "  " + _("Name"),
                "",
                "",
                "",
                fs_n.akSurname() + ", " + fs_n.akGiven(),
                "",
                False,
                "name",
                None,
                fs_n.id,
            )
        )

    return res


def compare_parents(db, gr_person: Person, fs_person) -> List[Tuple]:
    # add parent comparisons to result list
    family_handle = gr_person.get_main_parents_family_handle()
    father = None
    father_handle = None
    father_name = ""
    mother = None
    mother_handle = None
    mother_name = ""
    res: List[Tuple] = []

    if family_handle:
        family = db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        if father_handle:
            father = db.get_person_from_handle(father_handle)
            father_name = name_displayer.display(father)
        mother_handle = family.get_mother_handle()
        if mother_handle:
            mother = db.get_person_from_handle(mother_handle)
            mother_name = name_displayer.display(mother)

    parent_ids = _parent_ids_from_fs_person(fs_person)
    if parent_ids:
        _ensure_fs_people(parent_ids)

        fs_father_id = ""
        fs_father = None
        fs_mother_id = ""
        fs_mother = None
        for fsid in parent_ids:
            fs2 = deserialize.Person.index.get(fsid) or deserialize.Person()
            if fs2.gender and fs2.gender.type == "http://gedcomx.org/Male":
                fs_father_id = fsid
                fs_father = fs2
            elif fs2.gender and fs2.gender.type == "http://gedcomx.org/Female":
                fs_mother_id = fsid
                fs_mother = fs2

        if fs_father:
            name = fs_father.preferred_name()
            fs_father_name = name.akSurname() + ", " + name.akGiven()
        else:
            fs_father_name = ""
        if fs_mother:
            name = fs_mother.preferred_name()
            fs_mother_name = name.akSurname() + ", " + name.akGiven()
        else:
            fs_mother_name = ""
    else:
        fs_father_id = ""
        fs_mother_id = ""
        fs_father = None
        fs_mother = None
        fs_father_name = ""
        fs_mother_name = ""

    father_fsid = fs_utilities.get_fsftid(father)
    mother_fsid = fs_utilities.get_fsftid(mother)

    color = "orange"
    if father_fsid == fs_father_id:
        color = "green"
    elif father and fs_father_id == "":
        color = "yellow"
    elif father is None and fs_father_id != "":
        color = "yellow3"
    if father or fs_father:
        res.append(
            (
                color,
                _("Father"),
                person_dates_str(db, father),
                " " + father_name + " [" + father_fsid + "]",
                fs_person_dates_str(db, fs_father),
                fs_father_name + " [" + fs_father_id + "]",
                "",
                False,
                "father",
                father_handle,
                father_fsid,
            )
        )

    color = "orange"
    if mother_fsid == fs_mother_id:
        color = "green"
    elif mother and fs_mother_id == "":
        color = "yellow"
    elif mother is None and fs_mother_id != "":
        color = "yellow3"
    if mother or fs_mother:
        res.append(
            (
                color,
                _("Mother"),
                person_dates_str(db, mother),
                " " + mother_name + " [" + mother_fsid + "]",
                fs_person_dates_str(db, fs_mother),
                fs_mother_name + " [" + fs_mother_id + "]",
                "",
                False,
                "mother",
                mother_handle,
                mother_fsid,
            )
        )

    return res


def compare_spouse_notes(db, gr_person: Person, fs_person) -> List[Tuple]:
    # add spouse comparison lines without family events (used in notes pane)
    res: List[Tuple] = []
    fs_spouses = fs_person._spouses.copy()
    fsid = fs_person.id

    for family_handle in gr_person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        if family:
            spouse_handle = family.mother_handle
            if spouse_handle == gr_person.handle:
                spouse_handle = family.father_handle
            if spouse_handle:
                spouse = db.get_person_from_handle(spouse_handle)
            else:
                spouse = Person()

            spouse_name = spouse.primary_name
            spouse_fsid = fs_utilities.get_fsftid(spouse)
            fs_spouse_id = ""
            fs_pair = None
            fs_pair_id = None

            for couple in fs_spouses:
                if (couple.person1 and couple.person1.resourceId == spouse_fsid) or (
                    (couple.person1 is None or couple.person1.resourceId == "")
                    and spouse_fsid == ""
                ):
                    fs_spouse_id = spouse_fsid
                    fs_pair = couple
                    fs_pair_id = couple.id
                    fs_spouses.remove(couple)
                    break
                elif (couple.person2 and couple.person2.resourceId == spouse_fsid) or (
                    (couple.person2 is None or couple.person2.resourceId == "")
                    and spouse_fsid == ""
                ):
                    fs_spouse_id = spouse_fsid
                    fs_pair = couple
                    fs_pair_id = couple.id
                    fs_spouses.remove(couple)
                    break

            color = "yellow"
            if spouse_fsid and spouse_fsid == fs_spouse_id:
                color = "green"
            if spouse_handle is None and fs_spouse_id == "":
                color = "green"

            fs_spouse = _fs_person_or_blank(fs_spouse_id)

            fs_name = fs_spouse.preferred_name()
            res.append(
                (
                    color,
                    _("Spouse"),
                    person_dates_str(db, spouse),
                    spouse_name.get_surname()
                    + ", "
                    + spouse_name.first_name
                    + " ["
                    + spouse_fsid
                    + "]",
                    fs_person_dates_str(db, fs_spouse),
                    fs_name.akSurname()
                    + ", "
                    + fs_name.akGiven()
                    + " ["
                    + fs_spouse_id
                    + "]",
                    "",
                    False,
                    "spouse",
                    spouse_handle,
                    fs_spouse_id,
                    family.handle,
                    fs_pair_id,
                )
            )

    color = "yellow3"
    for couple in fs_spouses:
        # keep this ALWAYS str (never None) so mypy is happy
        if couple.person1 and couple.person1.resourceId == fsid:
            fs_spouse_id = couple.person2.resourceId
        elif couple.person1:
            fs_spouse_id = couple.person1.resourceId
        else:
            fs_spouse_id = ""

        fs_spouse_opt = _fs_person_opt(fs_spouse_id)

        # mypy-proof: never call preferred_name() on an Optional
        fs_spouse_for_name = (
            fs_spouse_opt if fs_spouse_opt is not None else deserialize.Person()
        )
        fs_name = fs_spouse_for_name.preferred_name()

        res.append(
            (
                color,
                _("Spouse"),
                "",
                "",
                fs_person_dates_str(db, fs_spouse_opt),
                fs_name.akSurname()
                + ", "
                + fs_name.akGiven()
                + " ["
                + fs_spouse_id
                + "]",
                "",
                False,
                "spouse",
                None,
                fs_spouse_id,
                None,
                couple.id,
            )
        )

    return res


def compare_spouses(db, gr_person: Person, fs_person) -> List[Tuple]:
    # add spouse &family event comparisons to result list
    res: List[Tuple] = []
    fs_spouses = fs_person._spouses.copy()
    fs_children = fs_person._childrenCP.copy()
    fs_spouse_ids = _spouse_ids_from_children(fs_person)
    fsid = fs_person.id

    for family_handle in gr_person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        if family:
            spouse_handle = family.mother_handle
            if spouse_handle == gr_person.handle:
                spouse_handle = family.father_handle
            if spouse_handle:
                spouse = db.get_person_from_handle(spouse_handle)
            else:
                spouse = Person()

            spouse_name = spouse.primary_name
            spouse_fsid = fs_utilities.get_fsftid(spouse)
            fs_spouse_id = ""
            fs_pair = None
            fs_pair_id = None
            child_other_parent_ids = _child_other_parent_ids_for_family(
                db,
                family,
                fs_person,
            )

            for couple in fs_spouses:
                if (couple.person1 and couple.person1.resourceId == spouse_fsid) or (
                    (couple.person1 is None or couple.person1.resourceId == "")
                    and spouse_fsid == ""
                ):
                    fs_spouse_id = spouse_fsid
                    fs_pair = couple
                    fs_pair_id = couple.id
                    fs_spouses.remove(couple)
                    break
                elif (couple.person2 and couple.person2.resourceId == spouse_fsid) or (
                    (couple.person2 is None or couple.person2.resourceId == "")
                    and spouse_fsid == ""
                ):
                    fs_spouse_id = spouse_fsid
                    fs_pair = couple
                    fs_pair_id = couple.id
                    fs_spouses.remove(couple)
                    break

            if not fs_spouse_id and not spouse_fsid:
                non_blank_child_parent_ids = sorted(
                    parent_id for parent_id in child_other_parent_ids if parent_id
                )
                if len(non_blank_child_parent_ids) == 1:
                    fs_spouse_id = non_blank_child_parent_ids[0]
                    fs_pair = _pop_fs_couple_for_spouse(
                        fs_spouses,
                        fsid,
                        fs_spouse_id,
                    )
                    fs_pair_id = getattr(fs_pair, "id", None) if fs_pair else None
                    fs_spouse_ids.discard(fs_spouse_id)

            if not fs_spouse_id and spouse_fsid and spouse_fsid in fs_spouse_ids:
                fs_spouse_id = spouse_fsid
                fs_spouse_ids.remove(spouse_fsid)
            elif spouse_fsid:
                fs_spouse_ids.discard(spouse_fsid)

            color = "orange"
            if spouse_fsid and spouse_fsid == fs_spouse_id:
                color = "green"
            elif spouse_handle is None and fs_spouse_id:
                color = "yellow3"
            elif spouse_handle is None and fs_spouse_id == "":
                color = "green"
                if any(parent_id for parent_id in child_other_parent_ids):
                    color = "orange"
            elif spouse_fsid and not fs_spouse_id:
                color = "yellow"

            fs_spouse = _fs_person_or_blank(fs_spouse_id)

            fs_name = fs_spouse.preferred_name()
            res.append(
                (
                    color,
                    _("Spouse"),
                    person_dates_str(db, spouse),
                    spouse_name.get_surname()
                    + ", "
                    + spouse_name.first_name
                    + " ["
                    + spouse_fsid
                    + "]",
                    fs_person_dates_str(db, fs_spouse),
                    fs_name.akSurname()
                    + ", "
                    + fs_name.akGiven()
                    + " ["
                    + fs_spouse_id
                    + "]",
                    "",
                    False,
                    "spouse",
                    spouse_handle,
                    fs_spouse_id,
                    family.handle,
                    fs_pair_id,
                )
            )

            # family-level events like marriage
            if fs_pair:
                fs_facts = list(getattr(fs_pair, "facts", []) or [])
                fs_pair_id_local = fs_pair.id
            else:
                fs_facts = []
                fs_pair_id_local = None

            for eventref in family.get_event_ref_list():
                event = db.get_event_from_handle(eventref.ref)
                title = str(EventType(event.type))
                gr_desc = event.description or ""
                gr_date = fs_utilities.gramps_date_to_formal(event.date)
                if event.place:
                    place = db.get_place_from_handle(event.place)
                    gr_place = _pd.display(db, place)
                else:
                    gr_place = ""
                gr_value = (
                    gr_desc
                    if gr_place == ""
                    else (
                        gr_desc + " from deserialize.xml import parse_xml " + gr_place
                    )
                )

                color = "yellow"
                fs_date = ""
                fs_place = ""
                fs_desc = ""
                fs_id = None
                gr_id = fs_utilities.get_fsftid(event)
                gr_tag = _event_type_value(event.type)

                fs_fact = _find_best_fs_fact_match(fs_facts, gr_tag, gr_date, gr_id)
                if fs_fact:
                    fs_date = _fs_fact_date(fs_fact)
                    if fs_date == gr_date:
                        color = "green"
                    fs_place = _fs_fact_place(fs_fact)
                    fs_desc = _fs_fact_value(fs_fact)
                    fs_id = getattr(fs_fact, "id", None)
                    if color == "green":
                        matched_signature = _fs_fact_signature(fs_fact)
                        fs_facts = [
                            fact
                            for fact in fs_facts
                            if _fs_fact_signature(fact) != matched_signature
                        ]
                    else:
                        fs_facts.remove(fs_fact)
                    if color == "green" and not gr_id and fs_id:
                        logger.debug("Linking GR family event to FS fact id=%s", fs_id)
                        fs_utilities.link_gramps_fs_id(db, event, fs_id)

                fs_value = (
                    fs_desc
                    if fs_place == ""
                    else (
                        fs_desc + " from deserialize.xml import parse_xml " + fs_place
                    )
                )

                res.append(
                    (
                        color,
                        " " + title,
                        gr_date,
                        gr_value,
                        fs_date,
                        fs_value,
                        "",
                        False,
                        "spouse_fact",
                        eventref.ref,
                        fs_id,
                        family.handle,
                        fs_pair_id_local,
                    )
                )

            # FS facts not in GRAMPS
            color = "yellow3"
            for fs_fact in _unique_fs_facts(fs_facts):
                evt_type = _fs_fact_gramps_tag(fs_fact)
                if evt_type:
                    try:
                        title = str(EventType(evt_type))
                    except Exception:
                        title = str(evt_type)
                else:
                    title = str(getattr(fs_fact, "type", "") or "")
                fs_date = _fs_fact_date(fs_fact)
                fs_place = _fs_fact_place(fs_fact)
                fs_desc = _fs_fact_value(fs_fact)
                fs_value = (
                    fs_desc
                    if fs_place == ""
                    else (
                        fs_desc + " from deserialize.xml import parse_xml " + fs_place
                    )
                )

                res.append(
                    (
                        color,
                        " " + title,
                        "",
                        "",
                        fs_date,
                        fs_value,
                        "",
                        False,
                        "spouse_fact",
                        None,
                        fs_fact.id,
                        family.handle,
                        fs_pair.id if fs_pair else None,
                    )
                )

            # children under this family
            for child_ref in family.get_child_ref_list():
                child = db.get_person_from_handle(child_ref.ref)
                child_name = child.primary_name
                child_fsid = fs_utilities.get_fsftid(child)
                fs_child_id = ""
                fs_child_other_parent_id = None
                for triple in list(fs_children):
                    other_parent_id = _other_parent_id_for_child_rel(fsid, triple)
                    if (
                        other_parent_id is not None
                        and triple.child.resourceId == child_fsid
                    ):
                        fs_child_id = child_fsid
                        fs_child_other_parent_id = other_parent_id
                        fs_children.remove(triple)
                        break

                color = "yellow"
                if fs_child_id != "" and fs_child_id == child_fsid:
                    color = "green"
                    if fs_child_other_parent_id != fs_spouse_id:
                        color = "orange"

                fs_child = _fs_person_or_blank(fs_child_id)

                fs_name = fs_child.preferred_name()
                res.append(
                    (
                        color,
                        "    " + _("Child"),
                        person_dates_str(db, child),
                        child_name.get_surname()
                        + ", "
                        + child_name.first_name
                        + " ["
                        + child_fsid
                        + "]",
                        fs_person_dates_str(db, fs_child),
                        fs_name.akSurname()
                        + ", "
                        + fs_name.akGiven()
                        + " ["
                        + fs_child_id
                        + "]",
                        "",
                        False,
                        "child",
                        child_ref.ref,
                        fs_child_id,
                        family.handle,
                        fs_pair_id,
                    )
                )

            to_remove = set()
            for triple in fs_children:
                if _other_parent_id_for_child_rel(fsid, triple) == fs_spouse_id:
                    fs_child_id = triple.child.resourceId
                    color = "yellow3"

                    fs_child_opt = _fs_person_opt(fs_child_id)

                    # mypy-proof
                    fs_child_for_name = (
                        fs_child_opt
                        if fs_child_opt is not None
                        else deserialize.Person()
                    )
                    fs_name = fs_child_for_name.preferred_name()

                    res.append(
                        (
                            color,
                            "    " + _("Child"),
                            "",
                            "",
                            fs_person_dates_str(db, fs_child_opt),
                            fs_name.akSurname()
                            + ", "
                            + fs_name.akGiven()
                            + " ["
                            + fs_child_id
                            + "]",
                            "",
                            False,
                            "child",
                            None,
                            fs_child_id,
                            family.handle,
                            fs_pair_id,
                        )
                    )
                    to_remove.add(triple)

            for triple in to_remove:
                fs_children.remove(triple)

    color = "yellow3"
    for couple in fs_spouses:
        # keep ALWAYS str
        if couple.person1 and couple.person1.resourceId == fsid:
            fs_spouse_id = couple.person2.resourceId
        elif couple.person1:
            fs_spouse_id = couple.person1.resourceId
        else:
            fs_spouse_id = ""
        fs_spouse_ids.discard(fs_spouse_id)

        fs_spouse_opt = _fs_person_opt(fs_spouse_id)

        # mypy-proof
        fs_spouse_for_name = (
            fs_spouse_opt if fs_spouse_opt is not None else deserialize.Person()
        )
        fs_name = fs_spouse_for_name.preferred_name()

        res.append(
            (
                color,
                _("Spouse"),
                "",
                "",
                fs_person_dates_str(db, fs_spouse_opt),
                fs_name.akSurname()
                + ", "
                + fs_name.akGiven()
                + " ["
                + fs_spouse_id
                + "]",
                "",
                False,
                "spouse",
                None,
                fs_spouse_id,
                None,
                couple.id,
            )
        )

        to_remove = set()
        for triple in fs_children:
            if _other_parent_id_for_child_rel(fsid, triple) == fs_spouse_id:
                fs_child_id = triple.child.resourceId

                fs_child_opt = _fs_person_opt(fs_child_id)

                # mypy-proof
                fs_child_for_name = (
                    fs_child_opt if fs_child_opt is not None else deserialize.Person()
                )
                fs_name = fs_child_for_name.preferred_name()

                res.append(
                    (
                        color,
                        "    " + _("Child"),
                        "",
                        "",
                        fs_person_dates_str(db, fs_child_opt),
                        fs_name.akSurname()
                        + ", "
                        + fs_name.akGiven()
                        + " ["
                        + fs_child_id
                        + "]",
                        "",
                        False,
                        "child",
                        None,
                        fs_child_id,
                        None,
                        couple.id,
                    )
                )
                to_remove.add(triple)
        for triple in to_remove:
            fs_children.remove(triple)

    color = "yellow3"
    for fs_spouse_id in sorted(fs_spouse_ids):
        fs_spouse_opt = _fs_person_opt(fs_spouse_id)
        fs_spouse_for_name = (
            fs_spouse_opt if fs_spouse_opt is not None else deserialize.Person()
        )
        fs_name = fs_spouse_for_name.preferred_name()

        res.append(
            (
                color,
                _("Spouse"),
                "",
                "",
                fs_person_dates_str(db, fs_spouse_opt),
                fs_name.akSurname()
                + ", "
                + fs_name.akGiven()
                + " ["
                + fs_spouse_id
                + "]",
                "",
                False,
                "spouse",
                None,
                fs_spouse_id,
                None,
                None,
            )
        )

        to_remove = set()
        for triple in fs_children:
            if _other_parent_id_for_child_rel(fsid, triple) == fs_spouse_id:
                fs_child_id = triple.child.resourceId
                fs_child_opt = _fs_person_opt(fs_child_id)
                fs_child_for_name = (
                    fs_child_opt if fs_child_opt is not None else deserialize.Person()
                )
                fs_name = fs_child_for_name.preferred_name()

                res.append(
                    (
                        color,
                        "    " + _("Child"),
                        "",
                        "",
                        fs_person_dates_str(db, fs_child_opt),
                        fs_name.akSurname()
                        + ", "
                        + fs_name.akGiven()
                        + " ["
                        + fs_child_id
                        + "]",
                        "",
                        False,
                        "child",
                        None,
                        fs_child_id,
                        None,
                        None,
                    )
                )
                to_remove.add(triple)
        for triple in to_remove:
            fs_children.remove(triple)

    for triple in fs_children:
        fs_child_id = triple.child.resourceId

        fs_child_opt = _fs_person_opt(fs_child_id)

        # mypy-proof
        fs_child_for_name = (
            fs_child_opt if fs_child_opt is not None else deserialize.Person()
        )
        fs_name = fs_child_for_name.preferred_name()

        res.append(
            (
                color,
                _("Child"),
                "",
                "",
                fs_person_dates_str(db, fs_child_opt),
                fs_name.akSurname()
                + ", "
                + fs_name.akGiven()
                + " ["
                + fs_child_id
                + "]",
                "",
                False,
                "child",
                None,
                fs_child_id,
                None,
                None,
            )
        )

    return res


def compare_other_facts(db, person: Person, fs_person) -> List[list]:
    # compare non-core facts
    gr_facts = person.event_ref_list
    fs_facts = fs_person.facts.copy()
    res: List[list] = []

    for gr_ref in gr_facts:
        if int(gr_ref.get_role()) != EventRoleType.PRIMARY:
            continue
        event = db.get_event_from_handle(gr_ref.ref)
        if event.type in (
            EventType.BIRTH,
            EventType.DEATH,
            EventType.BAPTISM,
            EventType.BURIAL,
        ):
            continue

        title = str(EventType(event.type))
        gr_desc = event.description or ""
        gr_date = fs_utilities.gramps_date_to_formal(event.date)
        gr_id = fs_utilities.get_fsftid(event)
        if event.place:
            place = db.get_place_from_handle(event.place)
            gr_place = _pd.display(db, place)
        else:
            gr_place = ""

        gr_value = (
            gr_desc
            if gr_place == ""
            else (gr_desc + " from deserialize.xml import parse_xml " + gr_place)
        )
        color = "yellow"
        fs_id = None
        fs_date = ""
        fs_place = ""
        fs_desc = ""

        for fs_fact in fs_facts:
            if fs_fact.id == gr_id:
                fs_id = fs_fact.id
                fs_facts.remove(fs_fact)
                break

        if gr_id == "" and not fs_id:
            for fs_fact in fs_facts:
                ged_tag = GEDCOMX_TO_GRAMPS_FACTS.get(unquote(fs_fact.type))
                if not ged_tag:
                    if fs_fact.type[:6] == "data:,":
                        ged_tag = unquote(fs_fact.type[6:])
                    else:
                        ged_tag = fs_fact.type
                if not ged_tag:
                    continue
                gr_tag = int(event.type) or event.type
                if ged_tag != gr_tag:
                    continue
                if getattr(fs_fact, "date", None):
                    fs_date = str(fs_fact.date)
                if fs_date != gr_date:
                    fs_date = ""
                    continue
                fs_id = fs_fact.id
                fs_facts.remove(fs_fact)
                break

        if fs_id:
            color = "green"
            if getattr(fs_fact, "date", None):
                fs_date = str(fs_fact.date)
            if getattr(fs_fact, "place", None):
                fs_place = fs_fact.place.original or ""
            fs_desc = getattr(fs_fact, "value", "") or ""
            if gr_date != fs_date:
                color = "orange"

        fs_value = (
            fs_desc
            if fs_place == ""
            else (fs_desc + " from deserialize.xml import parse_xml " + fs_place)
        )
        if color == "green" and gr_id == "" and fs_id:
            logger.debug("Linking GR event to FS fact id=%s", fs_id)
            fs_utilities.link_gramps_fs_id(db, event, fs_id)

        res.append(
            [
                color,
                title,
                gr_date,
                gr_value,
                fs_date,
                fs_value,
                "",
                False,
                "fact",
                gr_ref.ref,
                fs_id,
            ]
        )

    color = "yellow3"
    for fs_fact in fs_facts:
        if fs_fact.type in (
            "http://gedcomx.org/Birth",
            "http://gedcomx.org/Baptism",
            "http://gedcomx.org/Death",
            "http://gedcomx.org/Burial",
        ):
            continue
        ged_tag = GEDCOMX_TO_GRAMPS_FACTS.get(unquote(fs_fact.type))
        if not ged_tag:
            if fs_fact.type[:6] == "data:,":
                title = unquote(fs_fact.type[6:])
            else:
                title = fs_fact.type
        else:
            title = str(EventType(ged_tag))

        fs_date = str(fs_fact.date or "") if hasattr(fs_fact, "date") else ""
        fs_place = (
            fs_fact.place.original or "" if getattr(fs_fact, "place", None) else ""
        )
        fs_desc = fs_fact.value or ""
        fs_value = (
            fs_desc
            if fs_place == ""
            else (fs_desc + " from deserialize.xml import parse_xml " + fs_place)
        )

        res.append(
            [
                color,
                title,
                "",
                "",
                fs_date,
                fs_value,
                "",
                False,
                "fact",
                None,
                fs_fact.id,
            ]
        )

    return res
