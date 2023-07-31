#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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

"""
A utility to make a best guess if a person is alive.  This is used to provide
privacy in reports and exports.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..display.name import displayer as name_displayer
from ..errors import DatabaseError
from ..lib.date import Date, Today
from ..proxy.proxybase import ProxyDbBase

_ = glocale.translation.sgettext

LOG = logging.getLogger(".gen.utils.alive")

# -------------------------------------------------------------------------
#
# Constants from config .ini keys
#
# -------------------------------------------------------------------------
# cache values; use refresh_constants() if they change
try:
    from ..config import config

    _MAX_AGE_PROB_ALIVE = config.get("behavior.max-age-prob-alive")
    _MAX_SIB_AGE_DIFF = config.get("behavior.max-sib-age-diff")
    _AVG_GENERATION_GAP = config.get("behavior.avg-generation-gap")
except ImportError:
    # Utils used as module not part of GRAMPS
    _MAX_AGE_PROB_ALIVE = 110
    _MAX_SIB_AGE_DIFF = 20
    _AVG_GENERATION_GAP = 20


# -------------------------------------------------------------------------
#
# ProbablyAlive class
#
# -------------------------------------------------------------------------
class ProbablyAlive:
    """
    An object to hold the parameters for considering someone alive.
    """

    def __init__(
        self,
        db,
        max_sib_age_diff=None,
        max_age_prob_alive=None,
        avg_generation_gap=None,
    ):
        self.db = db
        self.max_sib_age_diff = max_sib_age_diff or _MAX_SIB_AGE_DIFF
        self.max_age_prob_alive = max_age_prob_alive or _MAX_AGE_PROB_ALIVE
        self.avg_generation_gap = avg_generation_gap or _AVG_GENERATION_GAP
        self.persons_checked = set()

    def probably_alive_range(self, person, is_spouse=False):
        """
        Evaluate and return likely date range a person was alive.
        """
        # FIXME: some of these computed dates need to be a span. For
        #        example, if a person could be born +/- 20 yrs around
        #        a date then it should be a span, and yr_offset should
        #        deal with it as well ("between 1920 and 1930" + 10 =
        #        "between 1930 and 1940")
        if person is None:
            return (None, None, "", None)
        self.persons_checked = set()

        result = self.__check_person(person)
        if result:
            return result

        result = self.__check_siblings(person)
        if result:
            return result

        if not is_spouse:  # if you are not in recursion, let's recurse:
            result = self.__check_spouse(person)
            if result:
                return result

        result = self.__check_other_family(person)

        result = result or (None, None, "", None)
        return result

    def __check_person(self, person):
        """
        Check status of the person.
        """
        birth_date = self.__get_person_birth(person)
        death_date = self.__get_person_death(person)
        explain = ""

        if not birth_date and death_date:
            # person died more than MAX after current year
            if death_date.is_valid():
                birth_date = death_date.copy_offset_ymd(
                    year=-self.max_age_prob_alive
                )
            else:
                birth_date = death_date
            explain = _("death date")

        if not death_date and birth_date:
            # person died more than MAX after current year
            death_date = birth_date.copy_offset_ymd(
                year=self.max_age_prob_alive
            )
            explain = _("birth date")

        if death_date and birth_date:
            return (
                birth_date,
                death_date,
                explain,
                person,
            )  # direct self evidence
        return None

    def __get_person_birth(self, person):
        """
        Return birth date for a person.
        """
        birth_date = None
        birth_ref = person.get_birth_ref()

        # If they were born within X years before current year then
        # assume they are alive (we already know they are not dead).
        if birth_ref and birth_ref.get_role().is_primary():
            birth = self.db.get_event_from_handle(birth_ref.ref)
            birth_date = birth.get_date_object()
            if birth_date.get_start_date() == Date.EMPTY:
                birth_date = None

        # Look for Baptism, etc events.
        # These are fairly good indications that someone's birth.
        if not birth_date:
            for event_ref in person.get_primary_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if event.type.is_birth_fallback():
                    birth_date = event.get_date_object()
        return birth_date

    def __get_person_death(self, person):
        """
        Return death date for a person.
        """
        death_date = None
        death_ref = person.get_death_ref()

        # If the recorded death year is before current year then
        # things are simple.
        if death_ref and death_ref.get_role().is_primary():
            death = self.db.get_event_from_handle(death_ref.ref)
            death_date = death.get_date_object()

        # Look for Cause Of Death, Burial or Cremation events.
        # These are fairly good indications that someone's not alive.
        if not death_date:
            for event_ref in person.get_primary_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                if event.type.is_death_fallback():
                    death_date = event.get_date_object()
                    if not death_date.is_valid():
                        death_date = Today()  # before today
                        death_date.set_modifier(Date.MOD_BEFORE)
        return death_date

    def __check_siblings(self, person):
        """
        Check siblings.
        """
        # Neither birth nor death events are available. Try looking
        # at siblings. If a sibling was born more than X years past,
        # or more than Z future, then probably this person is
        # not alive. If the sibling died more than X years
        # past, or more than X years future, then probably not alive.

        family_list = person.get_parent_family_handle_list()
        for family_handle in family_list:
            family = self.db.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.db.get_person_from_handle(child_handle)

                # Go through once looking for direct evidence:
                birth_ref = child.get_birth_ref()
                if birth_ref:
                    birth = self.db.get_event_from_handle(birth_ref.ref)
                    result = self.__check_sibling_birth(
                        child, birth, _("sibling birth date")
                    )
                    if result is not None:
                        return result

                death_ref = child.get_death_ref()
                if death_ref:
                    death = self.db.get_event_from_handle(death_ref.ref)
                    result = self.__check_sibling_death(
                        child, death, _("sibling death date")
                    )
                    if result is not None:
                        return result

                # Go through again looking for fallback:
                for event_ref in child.get_primary_event_ref_list():
                    event = self.db.get_event_from_handle(event_ref.ref)
                    if event.type.is_birth_fallback():
                        result = self.__check_sibling_birth(
                            child,
                            event,
                            _("sibling birth-related date"),
                        )
                        if result is not None:
                            return result
                    elif event.type.is_death_fallback():
                        result = self.__check_sibling_death(
                            child, event, _("sibling death-related date")
                        )
                        if result is not None:
                            return result
        return None

    def __check_sibling_birth(self, sibling, birth, reason):
        """
        Check the siblings birth date.
        """
        date = birth.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            # if sibling birth date too far away, then not alive:
            year = date.get_year()
            if year != 0:
                # sibling birth date
                return (
                    Date().copy_ymd(year - self.max_sib_age_diff),
                    Date().copy_ymd(
                        year - self.max_sib_age_diff + self.max_age_prob_alive
                    ),
                    reason,
                    sibling,
                )
        return None

    def __check_sibling_death(self, sibling, death, reason):
        """
        Check the siblings death date.
        """
        date = death.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            # if sibling death date too far away, then not alive:
            year = date.get_year()
            if year != 0:
                # sibling death date
                return (
                    Date().copy_ymd(
                        year - self.max_sib_age_diff - self.max_age_prob_alive
                    ),
                    Date().copy_ymd(
                        year
                        - self.max_sib_age_diff
                        - self.max_age_prob_alive
                        + self.max_age_prob_alive
                    ),
                    reason,
                    sibling,
                )
        return None

    def __check_spouse(self, person):
        """
        Check spouse of the person.
        """
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            father_handle = family.get_father_handle()
            if mother_handle == person.handle and father_handle:
                spouse = self.db.get_person_from_handle(father_handle)
            elif father_handle == person.handle and mother_handle:
                spouse = self.db.get_person_from_handle(mother_handle)
            else:
                spouse = None

            if spouse:
                (
                    date1,
                    date2,
                    explain,
                    other,
                ) = self.probably_alive_range(spouse, is_spouse=True)
                result = self.__check_spouse_birth(
                    other,
                    date1,
                    explain,
                    _("a spouse's birth-related date, "),
                )
                if result:
                    return result

                result = self.__check_spouse_death(
                    other,
                    date2,
                    explain,
                    _("a spouse's death-related date, "),
                )
                if result:
                    return result

            result = self.__check_spouse_events(family, spouse)
            if result:
                return result
        return None

    def __check_spouse_birth(self, spouse, birth_date, explain, reason):
        """
        Check a spouse birth date.
        """
        if birth_date and birth_date.get_year() != 0:
            return (
                Date().copy_ymd(
                    birth_date.get_year() - self.avg_generation_gap
                ),
                Date().copy_ymd(
                    birth_date.get_year()
                    - self.avg_generation_gap
                    + self.max_age_prob_alive
                ),
                reason + explain,
                spouse,
            )
        return None

    def __check_spouse_death(self, spouse, death_date, explain, reason):
        """
        Check a spouse death date.
        """
        if death_date and death_date.get_year() != 0:
            return (
                Date().copy_ymd(
                    death_date.get_year()
                    + self.avg_generation_gap
                    - self.max_age_prob_alive
                ),
                Date().copy_ymd(
                    death_date.get_year() + self.avg_generation_gap
                ),
                reason + explain,
                spouse,
            )
        return None

    def __check_spouse_events(self, family, spouse):
        """
        Check the family events and see if we find something.
        """
        for event_ref in family.get_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            date = event.get_date_object()
            year = date.get_year()
            if year != 0:
                return (
                    Date().copy_ymd(year - self.avg_generation_gap),
                    Date().copy_ymd(
                        year - self.avg_generation_gap + self.max_age_prob_alive
                    ),
                    _("event with spouse"),
                    spouse,
                )
        return None

    def __check_other_family(self, person):
        """
        Check the descendants and ancestors of the person.
        """
        # If there are descendants that are too old for the person to have
        # been alive in the current year then they must be dead.

        date1, date2, explain, other = None, None, "", None
        try:
            date1, date2, explain, other = self.__descendants_too_old(
                person, self.avg_generation_gap
            )
        except RuntimeError as exception:
            raise DatabaseError(
                _("Database error: loop in %s's descendants")
                % name_displayer.display(person)
            ) from exception

        if date1 and date2:
            return (date1, date2, explain, other)

        # If there are ancestors that would be too old in the current year
        # then assume our person must be dead too.

        try:
            date1, date2, explain, other = self.__ancestors_too_old(
                person, -self.avg_generation_gap
            )
        except RuntimeError as exception:
            raise DatabaseError(
                _("Database error: loop in %s's ancestors")
                % name_displayer.display(person)
            ) from exception

        if date1 and date2:
            return (date1, date2, explain, other)

        # If we can't find any reason to believe that they are dead we
        # must assume they are alive.

        return (None, None, "", None)

    def __descendants_too_old(self, person, years):
        """
        Check for descendants that were born more than a lifespan ago.
        """
        if person.handle in self.persons_checked:
            return (None, None, "", None)
        self.persons_checked.add(person.handle)

        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if not family:
                # can happen with LivingProxyDb(PrivateProxyDb(db))
                continue
            for child_ref in family.get_child_ref_list():
                child = self.db.get_person_from_handle(child_ref.ref)
                event_ref = child.get_birth_ref()
                if event_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
                    result = self.__check_descendant_birth(
                        child, event, years, _("descendant birth date")
                    )
                    if result:
                        return result

                event_ref = child.get_death_ref()
                if event_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
                    result = self.__check_descendant_death(
                        child, event, _("descendant death date")
                    )
                    if result:
                        return result

                date1, date2, explain, other = self.__descendants_too_old(
                    child, years + self.avg_generation_gap
                )
                if date1 and date2:
                    return date1, date2, explain, other

                result = self.__check_descendant_fallbacks(child, years)
                if result:
                    return result

        return (None, None, "", None)

    def __check_descendant_fallbacks(self, descendant, years):
        """
        Check the descendant fallback data for birth and death equivalents
        """
        for event_ref in descendant.get_primary_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            if event.type.is_birth_fallback():
                result = self.__check_descendant_birth(
                    descendant,
                    event,
                    years,
                    _("descendant birth-related date"),
                )
                if result:
                    return result
            elif event.type.is_death_fallback():
                result = self.__check_descendant_death(
                    descendant, event, _("descendant death-related date")
                )
                if result:
                    return result
        return None

    def __check_descendant_birth(self, descendant, birth, years, reason):
        """
        Check the descendant birth date.
        """
        date = birth.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            estimated_date = Date(date)
            estimated_year = estimated_date.get_start_date()
            estimated_year = estimated_date.get_year() - years
            estimated_date.set_year(estimated_year)
            return (
                estimated_date,
                estimated_date.copy_offset_ymd(self.max_age_prob_alive),
                reason,
                descendant,
            )
        return None

    def __check_descendant_death(self, descendant, death, reason):
        """
        Check the descendant death date.
        """
        date = death.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            return (
                date.copy_offset_ymd(-self.avg_generation_gap),
                date.copy_offset_ymd(
                    -self.avg_generation_gap + self.max_age_prob_alive
                ),
                reason,
                descendant,
            )
        return None

    def __ancestors_too_old(self, person, year):
        """
        Check if any ancestors are old enough to indicate person deceased.
        """
        if person.handle in self.persons_checked:
            return (None, None, "", None)
        self.persons_checked.add(person.handle)

        LOG.debug(
            "ancestors_too_old('%s', %s)", name_displayer.display(person), year
        )
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            if not family:
                # can happen with LivingProxyDb(PrivateProxyDb(db))
                return (None, None, "", None)

            result = self.__check_ancestor_handle(
                family.get_father_handle(), year
            )
            if result:
                return result

            result = self.__check_ancestor_handle(
                family.get_mother_handle(), year
            )
            if result:
                return result

        return (None, None, "", None)

    def __check_ancestor_handle(self, ancestor_handle, year):
        """
        Check an ancestor.
        """
        if ancestor_handle:
            ancestor = self.db.get_person_from_handle(ancestor_handle)
            (date1, date2, explain, other) = self.__check_ancestor_events(
                ancestor, year
            )
            if date1 and date2:
                return (date1, date2, explain, other)

            date1, date2, explain, other = self.__ancestors_too_old(
                ancestor, year - self.avg_generation_gap
            )
            if date1 and date2:
                return (date1, date2, explain, other)
        return None

    def __check_ancestor_events(self, ancestor, year):
        """
        Check the ancestor birth and death dates.
        """
        event_ref = ancestor.get_birth_ref()
        if event_ref and event_ref.get_role().is_primary():
            event = self.db.get_event_from_handle(event_ref.ref)
            result = self.__check_ancestor_birth(
                ancestor, event, year, _("ancestor birth date")
            )
            if result:
                return result

        event_ref = ancestor.get_death_ref()
        if event_ref and event_ref.get_role().is_primary():
            event = self.db.get_event_from_handle(event_ref.ref)
            result = self.__check_ancestor_death(
                ancestor, event, year, _("ancestor death date")
            )
            if result:
                return result

        # Check fallback data:
        for event_ref in ancestor.get_primary_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            if event.type.is_birth_fallback():
                result = self.__check_ancestor_birth(
                    ancestor, event, year, _("ancestor birth-related date")
                )
                if result:
                    return result
            elif event.type.is_death_fallback():
                result = self.__check_ancestor_death(
                    ancestor, event, year, _("ancestor death-related date")
                )
                if result:
                    return result

            date1, date2, explain, other = self.__ancestors_too_old(
                ancestor, year - self.avg_generation_gap
            )
            if date1 and date2:
                return (date1, date2, explain, other)

        return (None, None, "", None)

    def __check_ancestor_birth(self, ancestor, birth, year, reason):
        """
        Check the ancestor birth date.
        """
        date = birth.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            return (
                date.copy_offset_ymd(-year),
                date.copy_offset_ymd(-year + self.max_age_prob_alive),
                reason,
                ancestor,
            )
        return None

    def __check_ancestor_death(self, ancestor, death, year, reason):
        """
        Check the ancestor death date.
        """
        date = death.get_date_object()
        if date.get_start_date() != Date.EMPTY:
            return (
                date.copy_offset_ymd(-year - self.max_age_prob_alive),
                date.copy_offset_ymd(
                    -year - self.max_age_prob_alive + self.max_age_prob_alive
                ),
                reason,
                ancestor,
            )
        return None


# -------------------------------------------------------------------------
#
# probably_alive
#
# -------------------------------------------------------------------------
def probably_alive(
    person,
    db,
    current_date=None,
    limit=0,
    max_sib_age_diff=None,
    max_age_prob_alive=None,
    avg_generation_gap=None,
    return_range=False,
):
    """
    Return true if the person may be alive on current_date.

    This works by a process of elimination. If we can't find a good
    reason to believe that someone is dead then we assume they must
    be alive.

    :param current_date: a date object that is not estimated or modified
                         (defaults to today)
    :param limit: number of years to check beyond death_date
    :param max_sib_age_diff: maximum sibling age difference, in years
    :param max_age_prob_alive: maximum age of a person, in years
    :param avg_generation_gap: average generation gap, in years
    """
    # First, get the real database to use all people
    # for determining alive status:
    birth, death, explain, relative = probably_alive_range(
        person, db, max_sib_age_diff, max_age_prob_alive, avg_generation_gap
    )
    if current_date is None:
        current_date = Today()
    LOG.debug(
        "%s: b.%s, d.%s - %s",
        " ".join(person.get_primary_name().get_text_data_list()),
        birth,
        death,
        explain,
    )
    if not birth or not death:
        # no evidence, must consider alive
        return (
            (True, None, None, _("no evidence"), None) if return_range else True
        )
    # must have dates from here:
    if limit:
        death += limit  # add these years to death
    # Finally, check to see if current_date is between dates
    result = current_date.match(birth, ">=") and current_date.match(death, "<=")
    if return_range:
        return (result, birth, death, explain, relative)
    return result


def probably_alive_range(
    person,
    db,
    max_sib_age_diff=None,
    max_age_prob_alive=None,
    avg_generation_gap=None,
):
    """
    Computes estimated birth and death dates.
    Returns: (birth_date, death_date, explain_text, related_person)
    """

    # First, find the real database to use all people
    # for determining alive status:
    basedb = db
    while isinstance(basedb, ProxyDbBase):
        basedb = basedb.db

    # Now, we create a wrapper for doing work:
    living_calculator = ProbablyAlive(
        basedb, max_sib_age_diff, max_age_prob_alive, avg_generation_gap
    )
    return living_calculator.probably_alive_range(person)


def update_constants():
    """
    Used to update the constants that are cached in this module.
    """
    from ..config import config

    global _MAX_AGE_PROB_ALIVE, _MAX_SIB_AGE_DIFF, _AVG_GENERATION_GAP
    _MAX_AGE_PROB_ALIVE = config.get("behavior.max-age-prob-alive")
    _MAX_SIB_AGE_DIFF = config.get("behavior.max-sib-age-diff")
    _AVG_GENERATION_GAP = config.get("behavior.avg-generation-gap")
