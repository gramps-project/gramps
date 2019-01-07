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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".gen.utils.alive")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..display.name import displayer as name_displayer
from ..lib.date import Date, Today
from ..errors import DatabaseError
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Constants from config .ini keys
#
#-------------------------------------------------------------------------
# cache values; use refresh_constants() if they change
try:
    from ..config import config
    _MAX_AGE_PROB_ALIVE = config.get('behavior.max-age-prob-alive')
    _MAX_SIB_AGE_DIFF = config.get('behavior.max-sib-age-diff')
    _AVG_GENERATION_GAP = config.get('behavior.avg-generation-gap')
except ImportError:
    # Utils used as module not part of GRAMPS
    _MAX_AGE_PROB_ALIVE = 110
    _MAX_SIB_AGE_DIFF = 20
    _AVG_GENERATION_GAP = 20

#-------------------------------------------------------------------------
#
# ProbablyAlive class
#
#-------------------------------------------------------------------------
class ProbablyAlive:
    """
    An object to hold the parameters for considering someone alive.
    """

    def __init__(self,
                 db,
                 max_sib_age_diff=None,
                 max_age_prob_alive=None,
                 avg_generation_gap=None):
        self.db = db
        if max_sib_age_diff is None:
            max_sib_age_diff = _MAX_SIB_AGE_DIFF
        if max_age_prob_alive is None:
            max_age_prob_alive = _MAX_AGE_PROB_ALIVE
        if avg_generation_gap is None:
            avg_generation_gap = _AVG_GENERATION_GAP
        self.MAX_SIB_AGE_DIFF = max_sib_age_diff
        self.MAX_AGE_PROB_ALIVE = max_age_prob_alive
        self.AVG_GENERATION_GAP = avg_generation_gap
        self.pset = set()

    def probably_alive_range(self, person, is_spouse=False):
        # FIXME: some of these computed dates need to be a span. For
        #        example, if a person could be born +/- 20 yrs around
        #        a date then it should be a span, and yr_offset should
        #        deal with it as well ("between 1920 and 1930" + 10 =
        #        "between 1930 and 1940")
        if person is None:
            return (None, None, "", None)
        self.pset = set()
        birth_ref = person.get_birth_ref()
        death_ref = person.get_death_ref()
        death_date = None
        birth_date = None
        explain = ""
        # If the recorded death year is before current year then
        # things are simple.
        if death_ref and death_ref.get_role().is_primary():
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                if death:
                    death_date = death.get_date_object()

        # Look for Cause Of Death, Burial or Cremation events.
        # These are fairly good indications that someone's not alive.
        if not death_date:
            for ev_ref in person.get_primary_event_ref_list():
                if ev_ref:
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_death_fallback():
                        death_date = ev.get_date_object()
                        if not death_date.is_valid():
                            death_date = Today() # before today
                            death_date.set_modifier(Date.MOD_BEFORE)

        # If they were born within X years before current year then
        # assume they are alive (we already know they are not dead).
        if not birth_date:
            if birth_ref and birth_ref.get_role().is_primary():
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth and birth.get_date_object().get_start_date() != Date.EMPTY:
                    birth_date = birth.get_date_object()

        # Look for Baptism, etc events.
        # These are fairly good indications that someone's birth.
        if not birth_date:
            for ev_ref in person.get_primary_event_ref_list():
                ev = self.db.get_event_from_handle(ev_ref.ref)
                if ev and ev.type.is_birth_fallback():
                    birth_date = ev.get_date_object()

        if not birth_date and death_date:
            # person died more than MAX after current year
            if death_date.is_valid():
                birth_date = death_date.copy_offset_ymd(year=-self.MAX_AGE_PROB_ALIVE)
            explain = _("death date")

        if not death_date and birth_date:
            # person died more than MAX after current year
            death_date = birth_date.copy_offset_ymd(year=self.MAX_AGE_PROB_ALIVE)
            explain = _("birth date")

        if death_date and birth_date:
            return (birth_date, death_date, explain, person) # direct self evidence

        # Neither birth nor death events are available. Try looking
        # at siblings. If a sibling was born more than X years past,
        # or more than Z future, then probably this person is
        # not alive. If the sibling died more than X years
        # past, or more than X years future, then probably not alive.

        family_list = person.get_parent_family_handle_list()
        for family_handle in family_list:
            family = self.db.get_family_from_handle(family_handle)
            if family is None:
                continue
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.db.get_person_from_handle(child_handle)
                if child is None:
                    continue
                # Go through once looking for direct evidence:
                for ev_ref in child.get_primary_event_ref_list():
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_birth():
                        dobj = ev.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            # if sibling birth date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling birth date
                                return (Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF),
                                        Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling birth date"),
                                        child)
                    elif ev and ev.type.is_death():
                        dobj = ev.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            # if sibling death date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling death date
                                return (Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE),
                                        Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE
                                                                + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling death date"),
                                        child)
                # Go through again looking for fallback:
                for ev_ref in child.get_primary_event_ref_list():
                    ev = self.db.get_event_from_handle(ev_ref.ref)
                    if ev and ev.type.is_birth_fallback():
                        dobj = ev.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            # if sibling birth date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling birth date
                                return (Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF),
                                        Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling birth-related date"),
                                        child)
                    elif ev and ev.type.is_death_fallback():
                        dobj = ev.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            # if sibling death date too far away, then not alive:
                            year = dobj.get_year()
                            if year != 0:
                                # sibling death date
                                return (Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE),
                                        Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("sibling death-related date"),
                                        child)

        if not is_spouse: # if you are not in recursion, let's recurse:
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
                    mother_handle = family.get_mother_handle()
                    father_handle = family.get_father_handle()
                    if mother_handle == person.handle and father_handle:
                        father = self.db.get_person_from_handle(father_handle)
                        date1, date2, explain, other = self.probably_alive_range(father, is_spouse=True)
                        if date1 and date1.get_year() != 0:
                            return (Date().copy_ymd(date1.get_year() - self.AVG_GENERATION_GAP),
                                    Date().copy_ymd(date1.get_year() - self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                    _("a spouse's birth-related date, ") + explain, other)
                        elif date2 and date2.get_year() != 0:
                            return (Date().copy_ymd(date2.get_year() + self.AVG_GENERATION_GAP - self.MAX_AGE_PROB_ALIVE),
                                    Date().copy_ymd(date2.get_year() + self.AVG_GENERATION_GAP),
                                    _("a spouse's death-related date, ") + explain, other)
                    elif father_handle == person.handle and mother_handle:
                        mother = self.db.get_person_from_handle(mother_handle)
                        date1, date2, explain, other = self.probably_alive_range(mother, is_spouse=True)
                        if date1 and date1.get_year() != 0:
                            return (Date().copy_ymd(date1.get_year() - self.AVG_GENERATION_GAP),
                                    Date().copy_ymd(date1.get_year() - self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                    _("a spouse's birth-related date, ") + explain, other)
                        elif date2 and date2.get_year() != 0:
                            return (Date().copy_ymd(date2.get_year() + self.AVG_GENERATION_GAP - self.MAX_AGE_PROB_ALIVE),
                                    Date().copy_ymd(date2.get_year() + self.AVG_GENERATION_GAP),
                                    _("a spouse's death-related date, ") + explain, other)
                    # Let's check the family events and see if we find something
                    for ref in family.get_event_ref_list():
                        if ref:
                            event = self.db.get_event_from_handle(ref.ref)
                            if event:
                                date = event.get_date_object()
                                year = date.get_year()
                                if year != 0:
                                    other = None
                                    if person.handle == mother_handle and father_handle:
                                        other = self.db.get_person_from_handle(father_handle)
                                    elif person.handle == father_handle and mother_handle:
                                        other = self.db.get_person_from_handle(mother_handle)
                                    return (Date().copy_ymd(year - self.AVG_GENERATION_GAP),
                                            Date().copy_ymd(year - self.AVG_GENERATION_GAP +
                                                                    self.MAX_AGE_PROB_ALIVE),

                                            _("event with spouse"), other)

        # Try looking for descendants that were born more than a lifespan
        # ago.

        def descendants_too_old (person, years):
            if person.handle in self.pset:
                return (None, None, "", None)
            self.pset.add(person.handle)
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if not family:
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    continue
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    child = self.db.get_person_from_handle(child_handle)
                    child_birth_ref = child.get_birth_ref()
                    if child_birth_ref:
                        child_birth = self.db.get_event_from_handle(child_birth_ref.ref)
                        dobj = child_birth.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            d = Date(dobj)
                            val = d.get_start_date()
                            val = d.get_year() - years
                            d.set_year(val)
                            return (d, d.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE),
                                    _("descendant birth date"),
                                    child)
                    child_death_ref = child.get_death_ref()
                    if child_death_ref:
                        child_death = self.db.get_event_from_handle(child_death_ref.ref)
                        dobj = child_death.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            return (dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP),
                                    dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                    _("descendant death date"),
                                    child)
                    date1, date2, explain, other = descendants_too_old (child, years + self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return date1, date2, explain, other
                    # Check fallback data:
                    for ev_ref in child.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                d = Date(dobj)
                                val = d.get_start_date()
                                val = d.get_year() - years
                                d.set_year(val)
                                return (d, d.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE),
                                        _("descendant birth-related date"),
                                        child)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                return (dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP),
                                        dobj.copy_offset_ymd(- self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE),
                                        _("descendant death-related date"),
                                        child)

            return (None, None, "", None)

        # If there are descendants that are too old for the person to have
        # been alive in the current year then they must be dead.

        date1, date2, explain, other = None, None, "", None
        try:
            date1, date2, explain, other = descendants_too_old(person, self.AVG_GENERATION_GAP)
        except RuntimeError:
            raise DatabaseError(
                _("Database error: loop in %s's descendants") %
                name_displayer.display(person))

        if date1 and date2:
            return (date1, date2, explain, other)

        def ancestors_too_old(person, year):
            if person.handle in self.pset:
                return (None, None, "", None)
            self.pset.add(person.handle)
            LOG.debug("ancestors_too_old('%s', %s)".format(
                name_displayer.display(person), year) )
            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = self.db.get_family_from_handle(family_handle)
                if not family:
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    return (None, None, "", None)
                father_handle = family.get_father_handle()
                if father_handle:
                    father = self.db.get_person_from_handle(father_handle)
                    father_birth_ref = father.get_birth_ref()
                    if father_birth_ref and father_birth_ref.get_role().is_primary():
                        father_birth = self.db.get_event_from_handle(
                            father_birth_ref.ref)
                        dobj = father_birth.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year),
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor birth date"),
                                    father)
                    father_death_ref = father.get_death_ref()
                    if father_death_ref and father_death_ref.get_role().is_primary():
                        father_death = self.db.get_event_from_handle(
                            father_death_ref.ref)
                        dobj = father_death.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE),
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor death date"),
                                    father)

                    # Check fallback data:
                    for ev_ref in father.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year),
                                        dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor birth-related date"),
                                        father)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE),
                                        dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor death-related date"),
                                        father)

                    date1, date2, explain, other = ancestors_too_old (father, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return date1, date2, explain, other

                mother_handle = family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                    mother_birth_ref = mother.get_birth_ref()
                    if mother_birth_ref and mother_birth_ref.get_role().is_primary():
                        mother_birth = self.db.get_event_from_handle(mother_birth_ref.ref)
                        dobj = mother_birth.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year),
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor birth date"),
                                    mother)
                    mother_death_ref = mother.get_death_ref()
                    if mother_death_ref and mother_death_ref.get_role().is_primary():
                        mother_death = self.db.get_event_from_handle(
                            mother_death_ref.ref)
                        dobj = mother_death.get_date_object()
                        if dobj.get_start_date() != Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE),
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                    _("ancestor death date"),
                                    mother)

                    # Check fallback data:
                    for ev_ref in mother.get_primary_event_ref_list():
                        ev = self.db.get_event_from_handle(ev_ref.ref)
                        if ev and ev.type.is_birth_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year),
                                        dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor birth-related date"),
                                        mother)

                        elif ev and ev.type.is_death_fallback():
                            dobj = ev.get_date_object()
                            if dobj.get_start_date() != Date.EMPTY:
                                return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE),
                                        dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE),
                                        _("ancestor death-related date"),
                                        mother)

                    date1, date2, explain, other = ancestors_too_old (mother, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return (date1, date2, explain, other)

            return (None, None, "", None)

        try:
            # If there are ancestors that would be too old in the current year
            # then assume our person must be dead too.
            date1, date2, explain, other = ancestors_too_old (person, - self.AVG_GENERATION_GAP)
        except RuntimeError:
            raise DatabaseError(
                _("Database error: loop in %s's ancestors") %
                name_displayer.display(person))
        if date1 and date2:
            return (date1, date2, explain, other)

        # If we can't find any reason to believe that they are dead we
        # must assume they are alive.

        return (None, None, "", None)

#-------------------------------------------------------------------------
#
# probably_alive
#
#-------------------------------------------------------------------------
def probably_alive(person, db,
                   current_date=None,
                   limit=0,
                   max_sib_age_diff=None,
                   max_age_prob_alive=None,
                   avg_generation_gap=None,
                   return_range=False):
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
    birth, death, explain, relative = probably_alive_range(person, db,
            max_sib_age_diff, max_age_prob_alive, avg_generation_gap)
    if current_date is None:
        current_date = Today()
    LOG.debug("%s: b.%s, d.%s - %s".format(
        " ".join(person.get_primary_name().get_text_data_list()),
        birth, death, explain))
    if not birth or not death:
        # no evidence, must consider alive
        return ((True, None, None, _("no evidence"), None) if return_range
                else True)
    # must have dates from here:
    if limit:
        death += limit # add these years to death
    # Finally, check to see if current_date is between dates
    result = (current_date.match(birth, ">=") and
              current_date.match(death, "<="))
    if return_range:
        return (result, birth, death, explain, relative)
    else:
        return result

def probably_alive_range(person, db,
                         max_sib_age_diff=None,
                         max_age_prob_alive=None,
                         avg_generation_gap=None):
    """
    Computes estimated birth and death dates.
    Returns: (birth_date, death_date, explain_text, related_person)
    """
    # First, find the real database to use all people
    # for determining alive status:
    from ..proxy.proxybase import ProxyDbBase
    basedb = db
    while isinstance(basedb, ProxyDbBase):
        basedb = basedb.db
    # Now, we create a wrapper for doing work:
    pb = ProbablyAlive(basedb, max_sib_age_diff,
                       max_age_prob_alive, avg_generation_gap)
    return pb.probably_alive_range(person)

def update_constants():
    """
    Used to update the constants that are cached in this module.
    """
    from ..config import config
    global _MAX_AGE_PROB_ALIVE, _MAX_SIB_AGE_DIFF, _AVG_GENERATION_GAP
    _MAX_AGE_PROB_ALIVE = config.get('behavior.max-age-prob-alive')
    _MAX_SIB_AGE_DIFF = config.get('behavior.max-sib-age-diff')
    _AVG_GENERATION_GAP = config.get('behavior.avg-generation-gap')
