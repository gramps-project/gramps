# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2008-2011 Reinhard Müller
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2013-2016 Paul Franklin
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

# ------------------------------------------------------------------------
#
# Standard Python modules
#
# ------------------------------------------------------------------------
import datetime

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.lib import (
    ChildRefType,
    Date,
    Span,
    Name,
    StyledText,
    StyledTextTag,
    StyledTextTagType,
)
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.alive import probably_alive
from gramps.gen.proxy import LivingProxyDb

# ------------------------------------------------------------------------
#
# List of records
#
# ------------------------------------------------------------------------


def _T_(value, context=""):  # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh

RECORDS = [
    (_T_("Youngest living person"), "person_youngestliving", True),
    (_T_("Oldest living person"), "person_oldestliving", True),
    (_T_("Person died at youngest age"), "person_youngestdied", False),
    (_T_("Person died at oldest age"), "person_oldestdied", True),
    (_T_("Person married at youngest age"), "person_youngestmarried", True),
    (_T_("Person married at oldest age"), "person_oldestmarried", True),
    (_T_("Person divorced at youngest age"), "person_youngestdivorced", False),
    (_T_("Person divorced at oldest age"), "person_oldestdivorced", False),
    (_T_("Youngest father"), "person_youngestfather", True),
    (_T_("Youngest mother"), "person_youngestmother", True),
    (_T_("Oldest father"), "person_oldestfather", True),
    (_T_("Oldest mother"), "person_oldestmother", True),
    (_T_("Father with most children"), "person_mostkidsfather", False),
    (_T_("Mother with most children"), "person_mostkidsmother", False),
    (_T_("Father with most grandchildren"), "person_mostgrandkidsfather", False),
    (_T_("Mother with most grandchildren"), "person_mostgrandkidsmother", False),
    (_T_("Couple with most children"), "family_mostchildren", True),
    (_T_("Living couple married most recently"), "family_youngestmarried", True),
    (_T_("Living couple married most long ago"), "family_oldestmarried", True),
    (_T_("Shortest past marriage"), "family_shortest", False),
    (_T_("Longest past marriage"), "family_longest", True),
    (_T_("Couple with smallest age difference"), "family_smallestagediff", True),
    (_T_("Couple with biggest age difference"), "family_biggestagediff", True),
]


# ------------------------------------------------------------------------
#
# Global functions
#
# ------------------------------------------------------------------------
def _good_date(date):
    return date is not None and date.is_valid()


def _find_death_date(db, person):
    death_ref = person.get_death_ref()
    if death_ref:
        death = db.get_event_from_handle(death_ref.ref)
        return death.get_date_object()
    else:
        event_list = person.get_primary_event_ref_list()
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type().is_death_fallback():
                return event.get_date_object()
    return None


def find_records(
    db,
    filter,
    top_size,
    callname,
    trans_text=glocale.translation.sgettext,
    name_format=None,
    living_mode=LivingProxyDb.MODE_INCLUDE_ALL,
    user=None,
):
    """
    @param trans_text: allow deferred translation of strings
    @type trans_text: a GrampsLocale sgettext instance
    trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
    :param name_format: optional format to control display of person's name
    :type name_format: None or int
    :param living_mode: enable optional control of living people's records
    :type living_mode: int
    """

    def get_unfiltered_person_from_handle(person_handle):
        if living_mode == LivingProxyDb.MODE_INCLUDE_ALL:
            return db.get_person_from_handle(person_handle)
        else:  # we are in the proxy so get the person before proxy changes
            return db.get_unfiltered_person(person_handle)

    today = datetime.date.today()
    today_date = Date(today.year, today.month, today.day)

    # Person records
    person_youngestliving = []
    person_oldestliving = []
    person_youngestdied = []
    person_oldestdied = []
    person_youngestmarried = []
    person_oldestmarried = []
    person_youngestdivorced = []
    person_oldestdivorced = []
    person_youngestfather = []
    person_youngestmother = []
    person_oldestfather = []
    person_oldestmother = []
    person_mostkidsfather = []
    person_mostkidsmother = []
    person_mostgrandkidsfather = []
    person_mostgrandkidsmother = []

    person_handle_list = db.iter_person_handles()

    # the next "if" will turn person_handle_list from a generator into a
    # list, but only when this code is called from a report (which has a
    # filter) and not when called from a gramplet (which has no filter);
    # so the next line drains the generator and turns it into a list
    # always, so the gramplet can use it later, in the second loop
    person_handle_list = list(person_handle_list)

    if filter:
        person_handle_list = filter.apply(db, person_handle_list, user=user)

    for person_handle in person_handle_list:
        person = db.get_person_from_handle(person_handle)
        unfil_person = get_unfiltered_person_from_handle(person_handle)
        if person is None:
            continue

        # FIXME this should check for a "fallback" birth also/instead
        birth_ref = person.get_birth_ref()

        if not birth_ref:
            # No birth event, so we can't calculate any age.
            continue

        birth = db.get_event_from_handle(birth_ref.ref)
        birth_date = birth.get_date_object()

        death_date = _find_death_date(db, person)

        if not _good_date(birth_date):
            # Birth date unknown or incomplete, so we can't calculate any age.
            continue

        name = _get_styled_primary_name(
            person, callname, trans_text=trans_text, name_format=name_format
        )

        if death_date is None:
            if probably_alive(unfil_person, db):
                # Still living, look for age records
                _record(
                    person_youngestliving,
                    person_oldestliving,
                    today_date - birth_date,
                    name,
                    "Person",
                    person_handle,
                    top_size,
                )
        elif _good_date(death_date):
            # Already died, look for age records
            _record(
                person_youngestdied,
                person_oldestdied,
                death_date - birth_date,
                name,
                "Person",
                person_handle,
                top_size,
            )

        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)

            marriage_date = None
            divorce_date = None
            for event_ref in family.get_event_ref_list():
                event = db.get_event_from_handle(event_ref.ref)
                if event.get_type().is_marriage() and (
                    event_ref.get_role().is_family()
                    or event_ref.get_role().is_primary()
                ):
                    marriage_date = event.get_date_object()
                elif event.get_type().is_divorce() and (
                    event_ref.get_role().is_family()
                    or event_ref.get_role().is_primary()
                ):
                    divorce_date = event.get_date_object()

            if _good_date(marriage_date):
                _record(
                    person_youngestmarried,
                    person_oldestmarried,
                    marriage_date - birth_date,
                    name,
                    "Person",
                    person_handle,
                    top_size,
                )

            if _good_date(divorce_date):
                _record(
                    person_youngestdivorced,
                    person_oldestdivorced,
                    divorce_date - birth_date,
                    name,
                    "Person",
                    person_handle,
                    top_size,
                )

            for child_ref in family.get_child_ref_list():
                if person.get_gender() == person.MALE:
                    relation = child_ref.get_father_relation()
                elif person.get_gender() == person.FEMALE:
                    relation = child_ref.get_mother_relation()
                else:
                    continue
                if relation != ChildRefType.BIRTH:
                    continue

                child = db.get_person_from_handle(child_ref.ref)

                # FIXME this should check for a "fallback" birth also/instead
                child_birth_ref = child.get_birth_ref()
                if not child_birth_ref:
                    continue

                child_birth = db.get_event_from_handle(child_birth_ref.ref)
                child_birth_date = child_birth.get_date_object()

                if not _good_date(child_birth_date):
                    continue

                if person.get_gender() == person.MALE:
                    _record(
                        person_youngestfather,
                        person_oldestfather,
                        child_birth_date - birth_date,
                        name,
                        "Person",
                        person_handle,
                        top_size,
                    )
                elif person.get_gender() == person.FEMALE:
                    _record(
                        person_youngestmother,
                        person_oldestmother,
                        child_birth_date - birth_date,
                        name,
                        "Person",
                        person_handle,
                        top_size,
                    )

    for person_handle in person_handle_list:
        # this "person loop" doesn't care about a person's birth or death
        person = db.get_person_from_handle(person_handle)
        if person is None:
            continue

        name = _get_styled_primary_name(
            person, callname, trans_text=trans_text, name_format=name_format
        )

        person_child_list = get_birth_children(db, person)
        if person.get_gender() == person.MALE:
            _record(
                None,
                person_mostkidsfather,
                len(person_child_list),
                name,
                "Person",
                person_handle,
                top_size,
            )
        elif person.get_gender() == person.FEMALE:
            _record(
                None,
                person_mostkidsmother,
                len(person_child_list),
                name,
                "Person",
                person_handle,
                top_size,
            )

        person_grandchild_list = []
        for child in person_child_list:
            person_grandchild_list += get_birth_children(db, child)
        if person.get_gender() == person.MALE:
            _record(
                None,
                person_mostgrandkidsfather,
                len(person_grandchild_list),
                name,
                "Person",
                person_handle,
                top_size,
            )
        elif person.get_gender() == person.FEMALE:
            _record(
                None,
                person_mostgrandkidsmother,
                len(person_grandchild_list),
                name,
                "Person",
                person_handle,
                top_size,
            )

    # Family records
    family_mostchildren = []
    family_youngestmarried = []
    family_oldestmarried = []
    family_shortest = []
    family_longest = []
    family_smallestagediff = []
    family_biggestagediff = []

    for family in db.iter_families():
        # family = db.get_family_from_handle(family_handle)
        if living_mode != LivingProxyDb.MODE_INCLUDE_ALL:
            # FIXME no iter_families method in LivingProxyDb so do it this way
            family = db.get_family_from_handle(family.get_handle())

        father_handle = family.get_father_handle()
        if not father_handle:
            continue
        mother_handle = family.get_mother_handle()
        if not mother_handle:
            continue

        # Test if either father or mother are in filter
        if filter:
            # we don't want many progress reports popping up, so no user=user
            if not filter.apply(db, [father_handle, mother_handle]):
                continue

        father = db.get_person_from_handle(father_handle)
        unfil_father = get_unfiltered_person_from_handle(father_handle)
        if father is None:
            continue
        mother = db.get_person_from_handle(mother_handle)
        unfil_mother = get_unfiltered_person_from_handle(mother_handle)
        if mother is None:
            continue

        father_name = _get_styled_primary_name(
            father, callname, trans_text=trans_text, name_format=name_format
        )
        mother_name = _get_styled_primary_name(
            mother, callname, trans_text=trans_text, name_format=name_format
        )

        name = StyledText(trans_text("%(father)s and %(mother)s"))
        name = name.replace("%(father)s", father_name)
        name = name.replace("%(mother)s", mother_name)

        if living_mode == LivingProxyDb.MODE_INCLUDE_ALL or (
            not probably_alive(unfil_father, db)
            and not probably_alive(unfil_mother, db)
        ):
            _record(
                None,
                family_mostchildren,
                len(family.get_child_ref_list()),
                name,
                "Family",
                family.handle,
                top_size,
            )

        father_birth_ref = father.get_birth_ref()
        if father_birth_ref:
            father_birth_date = db.get_event_from_handle(
                father_birth_ref.ref
            ).get_date_object()
        else:
            father_birth_date = None

        mother_birth_ref = mother.get_birth_ref()
        if mother_birth_ref:
            mother_birth_date = db.get_event_from_handle(
                mother_birth_ref.ref
            ).get_date_object()
        else:
            mother_birth_date = None

        if _good_date(father_birth_date) and _good_date(mother_birth_date):
            if father_birth_date >> mother_birth_date:
                _record(
                    family_smallestagediff,
                    family_biggestagediff,
                    father_birth_date - mother_birth_date,
                    name,
                    "Family",
                    family.handle,
                    top_size,
                )
            elif mother_birth_date >> father_birth_date:
                _record(
                    family_smallestagediff,
                    family_biggestagediff,
                    mother_birth_date - father_birth_date,
                    name,
                    "Family",
                    family.handle,
                    top_size,
                )

        marriage_date = None
        divorce = None
        divorce_date = None
        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type().is_marriage() and (
                event_ref.get_role().is_family() or event_ref.get_role().is_primary()
            ):
                marriage_date = event.get_date_object()
            if (
                event
                and event.get_type().is_divorce()
                and (
                    event_ref.get_role().is_family()
                    or event_ref.get_role().is_primary()
                )
            ):
                divorce = event
                divorce_date = event.get_date_object()

        father_death_date = _find_death_date(db, father)
        mother_death_date = _find_death_date(db, mother)

        if not _good_date(marriage_date):
            # Not married or marriage date unknown
            continue

        if divorce is not None and not _good_date(divorce_date):
            # Divorced but date unknown or inexact
            continue

        if not probably_alive(unfil_father, db) and not _good_date(father_death_date):
            # Father died but death date unknown or inexact
            continue

        if not probably_alive(unfil_mother, db) and not _good_date(mother_death_date):
            # Mother died but death date unknown or inexact
            continue

        if (
            divorce_date is None
            and father_death_date is None
            and mother_death_date is None
        ):
            # Still married and alive
            if probably_alive(unfil_father, db) and probably_alive(unfil_mother, db):
                _record(
                    family_youngestmarried,
                    family_oldestmarried,
                    today_date - marriage_date,
                    name,
                    "Family",
                    family.handle,
                    top_size,
                )
        elif (
            _good_date(divorce_date)
            or _good_date(father_death_date)
            or _good_date(mother_death_date)
        ):
            end = None
            if _good_date(father_death_date) and _good_date(mother_death_date):
                end = min(father_death_date, mother_death_date)
            elif _good_date(father_death_date):
                end = father_death_date
            elif _good_date(mother_death_date):
                end = mother_death_date
            if _good_date(divorce_date):
                if end:
                    end = min(end, divorce_date)
                else:
                    end = divorce_date
            duration = end - marriage_date

            _record(
                family_shortest,
                family_longest,
                duration,
                name,
                "Family",
                family.handle,
                top_size,
            )
    # python 3 workaround: assign locals to tmp so we work with runtime version
    tmp = locals()
    return [
        (trans_text(text), varname, tmp[varname])
        for (text, varname, default) in RECORDS
    ]


def _record(lowest, highest, value, text, handle_type, handle, top_size):
    if value < 0:  # ignore erroneous data
        return  # (since the data-verification tool already finds it)

    if isinstance(value, Span):
        low_value = value.minmax[0]
        high_value = value.minmax[1]
    else:
        low_value = value
        high_value = value

    if lowest is not None:
        lowest.append((high_value, value, text, handle_type, handle))
        lowest.sort(key=lambda a: a[0])  # FIXME: Ist das lambda notwendig?
        for i in range(top_size, len(lowest)):
            if lowest[i - 1][0] < lowest[i][0]:
                del lowest[i:]
                break

    if highest is not None:
        highest.append((low_value, value, text, handle_type, handle))
        highest.sort(reverse=True)
        for i in range(top_size, len(highest)):
            if highest[i - 1][0] > highest[i][0]:
                del highest[i:]
                break


def get_birth_children(db, person):
    """return all the birth children of a person, in a list"""
    person_child_list = []
    for family_handle in person.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        for child_ref in family.get_child_ref_list():
            if person.get_gender() == person.MALE:
                relation = child_ref.get_father_relation()
            elif person.get_gender() == person.FEMALE:
                relation = child_ref.get_mother_relation()
            else:
                continue  # no records are kept for unknown-sex parents
            if relation != ChildRefType.BIRTH:
                continue  # only count birth children
            child = db.get_person_from_handle(child_ref.ref)
            if child not in person_child_list:
                person_child_list += [child]
    return person_child_list


# ------------------------------------------------------------------------
#
# Reusable functions (could be methods of gen.lib.*)
#
# ------------------------------------------------------------------------

CALLNAME_DONTUSE = 0
CALLNAME_REPLACE = 1
CALLNAME_UNDERLINE_ADD = 2


def _get_styled(
    name,
    callname,
    placeholder=False,
    trans_text=glocale.translation.sgettext,
    name_format=None,
):
    """
    Return a StyledText object with the name formatted according to the
    parameters:

    @param callname: whether the callname should be used instead of the first
        name (CALLNAME_REPLACE), underlined within the first name
        (CALLNAME_UNDERLINE_ADD) or not used at all (CALLNAME_DONTUSE).
    @param placeholder: whether a series of underscores should be inserted as a
        placeholder if first name or surname are missing.
    @param trans_text: allow deferred translation of strings
    @type trans_text: a GrampsLocale sgettext instance
    trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
    :param name_format: optional format to control display of person's name
    :type name_format: None or int
    """

    # Make a copy of the name object so we don't mess around with the real
    # data.
    n = Name(source=name)

    # Insert placeholders.
    if placeholder:
        if not n.first_name:
            n.first_name = "____________"
        if not n.surname:
            n.surname = "____________"

    if n.call:
        if callname == CALLNAME_REPLACE:
            # Replace first name with call name.
            n.first_name = n.call
        elif callname == CALLNAME_UNDERLINE_ADD:
            if n.call not in n.first_name:
                # Add call name to first name.
                # Translators: used in French+Russian, ignore otherwise
                n.first_name = trans_text('"%(callname)s" (%(firstname)s)') % {
                    "callname": n.call,
                    "firstname": n.first_name,
                }

    real_format = name_displayer.get_default_format()
    if name_format is not None:
        name_displayer.set_default_format(name_format)
    text = name_displayer.display_name(n)
    name_displayer.set_default_format(real_format)
    tags = []

    if n.call:
        if callname == CALLNAME_UNDERLINE_ADD:
            # "name" in next line is on purpose: only underline the call name
            # if it was a part of the *original* first name
            if n.call in name.first_name:
                # Underline call name
                callpos = text.find(n.call)
                tags = [
                    StyledTextTag(
                        StyledTextTagType.UNDERLINE,
                        True,
                        [(callpos, callpos + len(n.call))],
                    )
                ]

    return StyledText(text, tags)


def _get_styled_primary_name(
    person,
    callname,
    placeholder=False,
    trans_text=glocale.translation.sgettext,
    name_format=None,
):
    """
    Return a StyledText object with the person's name formatted according to
    the parameters:

    @param callname: whether the callname should be used instead of the first
        name (CALLNAME_REPLACE), underlined within the first name
        (CALLNAME_UNDERLINE_ADD) or not used at all (CALLNAME_DONTUSE).
    @param placeholder: whether a series of underscores should be inserted as a
        placeholder if first name or surname are missing.
    @param trans_text: allow deferred translation of strings
    @type trans_text: a GrampsLocale sgettext instance
    trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
    :param name_format: optional format to control display of person's name
    :type name_format: None or int
    """

    return _get_styled(
        person.get_primary_name(),
        callname,
        trans_text=trans_text,
        placeholder=placeholder,
        name_format=name_format,
    )
