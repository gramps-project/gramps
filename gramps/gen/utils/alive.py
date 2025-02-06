#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2024       Cameron Davidson
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
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..display.name import displayer as name_displayer
from ..lib.date import Date, Today
from ..lib.person import Person
from ..lib.json_utils import DataDict
from ..errors import DatabaseError
from ..const import GRAMPS_LOCALE as glocale
from ..proxy.proxybase import ProxyDbBase

LOG = logging.getLogger(".gen.utils.alive")

_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext

# DEBUGLEVEL should be 1 for production, as higher levels are rather cryptic unless
# viewed in the context of the source code.
DEBUGLEVEL = 1  # 4 = everything; 3 much detail; 2= minor detail; 1 = summary
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
    _MIN_GENERATION_YEARS = config.get("behavior.min-generation-years")
except ImportError:
    # Utils used as module not part of GRAMPS
    _MAX_AGE_PROB_ALIVE = 110
    _MAX_SIB_AGE_DIFF = 20
    _AVG_GENERATION_GAP = 20
    _MIN_GENERATION_YEARS = 13


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
        min_generation_years=None,
    ):
        self.db = db
        if max_sib_age_diff is None:
            max_sib_age_diff = _MAX_SIB_AGE_DIFF
        if max_age_prob_alive is None:
            max_age_prob_alive = _MAX_AGE_PROB_ALIVE
        if avg_generation_gap is None:
            avg_generation_gap = _AVG_GENERATION_GAP
        if min_generation_years is None:
            min_generation_years = _MIN_GENERATION_YEARS
        self.MAX_SIB_AGE_DIFF = max_sib_age_diff
        self.MAX_AGE_PROB_ALIVE = max_age_prob_alive
        self.AVG_GENERATION_GAP = avg_generation_gap
        self.MIN_GENERATION_YEARS = min_generation_years
        self.pset = set()

    def probably_alive_range(self, person, is_spouse=False, immediate_fam_only=False):
        """
        Find likely birth and death date ranges, either from dates of actual
        events recorded in the db or else estimating range limits from
        other events in their lives or those of close family.
        If is_spouse is True then we are calling this recursively for the
        spouse of the original "person". That will be done in two passes:
        if immediate_fam_only is True then only immediate family of spouse
        is checked, otherwise a full check is done.

        Returns: (birth_date, death_date, explain_text, related_person)
        """
        # where appropriate, some derived dates are expressed as a range.
        if person is None:
            return (None, None, "", None)
        self.pset = set()
        birth_date = None
        death_date = None
        known_to_be_dead = False
        # whether the birth evidence (date or fallback) is known for this person
        birth_evidence_direct = False
        min_birth_year = None
        max_birth_year = None
        min_birth_year_from_death = None  # values derived from 110 year extrapolations
        max_birth_year_from_death = None
        # these min/max parameters are simply years
        sib_birth_min, sib_birth_max = (None, None)
        explain_birth_min = ""
        explain_birth_max = ""
        explain_death = ""

        def get_person_bd(class_or_handle):
            """
                Looks up birth and death events for referenced person,
                using fallback dates if necessary.
                The dates will always be either None or valid values, avoiding EMPTYs.
                Only actual recorded dates are returned - there are no inferred
                limit values supplied for missing dates.

            returns  (birth_date, death_date, death_found, explain_birth, explain_death)
                                 for the referenced person
            """
            birth_date = None
            death_date = None
            death_found = False
            explain_birth = ""
            explain_death = ""

            if not class_or_handle:
                return (
                    birth_date,
                    death_date,
                    death_found,
                    explain_birth,
                    explain_death,
                )

            if isinstance(class_or_handle, (Person, DataDict)):
                thisperson = class_or_handle
            elif isinstance(class_or_handle, str):
                thisperson = self.db.get_person_from_handle(class_or_handle)
            else:
                thisperson = None

            if not thisperson:
                LOG.debug("    get_person_bd(): null person called")
                return (
                    birth_date,
                    death_date,
                    death_found,
                    explain_birth,
                    explain_death,
                )
            # is there an actual death record?  Even if yes, there may be no date,
            # in which case the EMPTY date is reported for the event.
            death_ref = thisperson.get_death_ref()
            if death_ref and death_ref.get_role().is_primary():
                evnt = self.db.get_event_from_handle(death_ref.ref)
                if evnt:
                    death_found = True
                    dateobj = evnt.get_date_object()
                    if dateobj and dateobj.is_valid():
                        death_date = dateobj
                        explain_death = _("date")

            # at this stage death_date is None or a valid date.
            # death_found is true if thisperson is known to be dead,
            #        whether or not a date was found.
            # If we have no death_date then look for fallback event such as Burial.
            # These fallbacks are fairly good indications that someone's not alive.
            # If the fallback death event does not have a valid date then it means
            # we know they are dead but not when they died.
            # So keep checking in case we get a date.
            if not death_date:
                for ev_ref in thisperson.get_primary_event_ref_list():
                    if ev_ref:
                        evnt = self.db.get_event_from_handle(ev_ref.ref)
                        if evnt and evnt.type.is_death_fallback():
                            death_date_fb = evnt.get_date_object()
                            death_found = True
                            if death_date_fb.is_valid():
                                death_date = death_date_fb
                                explain_death = _("date fallback")
                                if death_date.get_modifier() == Date.MOD_NONE:
                                    death_date.set_modifier(Date.MOD_BEFORE)
                                break  # we found a valid date, stop looking.
            # At this point:
            # * death_found is False: (no death indication found); or
            # * death_found is True. (death confirmed somehow);  In which case:
            #       * (death_date is valid) some form of death date found; or
            #       * (death_date is None and no date was recorded)
            # now repeat, looking for birth date
            birth_ref = thisperson.get_birth_ref()
            if birth_ref and birth_ref.get_role().is_primary():
                evnt = self.db.get_event_from_handle(birth_ref.ref)
                if evnt:
                    dateobj = evnt.get_date_object()
                    if dateobj and dateobj.is_valid():
                        birth_date = dateobj
                        explain_birth = _("date")

            # to here:
            #   birth_date is None: either no birth record or else no date reported; or
            #   birth_date is a valid date
            # Look for Baptism, etc events.
            # These are fairly good indications of someone's birth date.
            if not birth_date:
                for ev_ref in thisperson.get_primary_event_ref_list():
                    evnt = self.db.get_event_from_handle(ev_ref.ref)
                    if evnt and evnt.type.is_birth_fallback():
                        birth_date_fb = evnt.get_date_object()
                        if birth_date_fb and birth_date_fb.is_valid():
                            birth_date = birth_date_fb
                            explain_birth = _("date fallback")
                            break
            if DEBUGLEVEL > 3:
                LOG.debug(
                    "           << get_person_bd for [%s], birth %s, death %s",
                    thisperson.get_gramps_id(),
                    birth_date,
                    death_date,
                )
            return (birth_date, death_date, death_found, explain_birth, explain_death)

        birth_date, death_date, known_to_be_dead, explain_birth_min, explain_death = (
            get_person_bd(person)
        )

        if birth_date is not None:
            birth_evidence_direct = True
            if death_date is not None:
                explanation = _(
                    "Direct evidence for this person - birth: {birth_min_src}, death: {death_src}"
                ).format(
                    birth_min_src=explain_birth_min,
                    death_src=explain_death,
                )
                return (
                    birth_date,
                    death_date,
                    explanation,
                    person,
                )  # direct self evidence

        # birth and/or death dates are not known, so let's see what we can estimate.
        # First: minimum is X years before death;
        # Second: get the parent's birth/death dates if available, so we can constrain
        # to sensible values - mother's age and parent's death.
        # Finally: get birth dates for any full siblings to further constrain.
        # Currently only look at full siblings, ranges would get wider for half sibs.

        if birth_date is None:
            # only need to estimate birth_date if we have no more direct evidence.
            if death_date is not None:
                # person died so guess initial limits to birth date
                if death_date.get_year_valid():
                    max_birth_year_from_death = death_date.get_year()
                    min_birth_year_from_death = (
                        max_birth_year_from_death - self.MAX_AGE_PROB_ALIVE
                    )

            m_birth = m_death = None  # mother's birth and death dates
            f_birth = f_death = None  # father's
            parents = None  # Family with parents
            parenth_p1 = person.get_main_parents_family_handle()
            if parenth_p1:
                parents = self.db.get_family_from_handle(parenth_p1)
                mother_handle_p1 = parents.get_mother_handle()
                m_birth, m_death = get_person_bd(mother_handle_p1)[0:2]
                father_handle_p1 = parents.get_father_handle()
                f_birth, f_death = get_person_bd(father_handle_p1)[0:2]
            # now scan siblings
            family_list = person.get_parent_family_handle_list()
            for family_handle in family_list:
                family = self.db.get_family_from_handle(family_handle)
                if family is None:
                    continue
                if parents is not None and family_handle != parenth_p1:
                    LOG.debug(
                        "      skipping family %s but parents is %s.",
                        family.get_gramps_id(),
                        parents.get_gramps_id(),
                    )
                    continue
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    child = self.db.get_person_from_handle(child_handle)
                    if child is None or child == person:
                        continue
                    need_birth_fallback = True
                    # Go through once looking for direct evidence:
                    # extract the range of birth dates, either direct or fallback
                    for ev_ref in child.get_primary_event_ref_list():
                        evnt = self.db.get_event_from_handle(ev_ref.ref)
                        if evnt and evnt.type.is_birth():
                            dobj = evnt.get_date_object()
                            if dobj and dobj.get_year_valid():
                                year = dobj.get_year()
                                need_birth_fallback = False
                                if sib_birth_min is None or year < sib_birth_min:
                                    sib_birth_min = year
                                if sib_birth_max is None or year > sib_birth_max:
                                    sib_birth_max = year
                    # scan event list again looking for fallback:
                    if need_birth_fallback:
                        for ev_ref in child.get_primary_event_ref_list():
                            evnt = self.db.get_event_from_handle(ev_ref.ref)
                            if evnt and evnt.type.is_birth_fallback():
                                dobj = evnt.get_date_object()
                                if dobj and dobj.get_year_valid():
                                    # if sibling birth date too far away, then
                                    # cannot be alive:
                                    year = dobj.get_year()
                                    if sib_birth_min is None or year < sib_birth_min:
                                        sib_birth_min = year
                                    if sib_birth_max is None or year > sib_birth_max:
                                        sib_birth_max = year
            # Now combine estimates based on parents and siblings:
            # Make sure child is born after both parents are old enough
            if m_birth:
                min_birth_year = m_birth.get_year() + self.MIN_GENERATION_YEARS
                explain_birth_min = _("mother's age")
            if f_birth:
                min_from_f = f_birth.get_year() + self.MIN_GENERATION_YEARS
                if min_birth_year is None or min_from_f > min_birth_year:
                    min_birth_year = min_from_f
                    explain_birth_min = _("father's age")
            if min_birth_year_from_death:
                if min_birth_year is None or min_birth_year_from_death > min_birth_year:
                    min_birth_year = min_birth_year_from_death
                    explain_birth_min = _("from death date")
            # Calculate the latest year that the child could have been born
            if m_death:
                max_birth_year = m_death.get_year()
                explain_birth_max = _("mother's death")
            if f_death:
                max_from_f = f_death.get_year() + 1
                if max_birth_year is None or max_from_f < max_birth_year:
                    max_birth_year = max_from_f
                    explain_birth_max = _("father's death")
            if max_birth_year_from_death:
                if max_birth_year is None or max_birth_year_from_death < max_birth_year:
                    max_birth_year = max_birth_year_from_death
                    explain_birth_max = _("person's death")

            # sib_xx_min/max are either both None or both have a value (maybe the same)
            if sib_birth_max:
                min_from_sib = sib_birth_max - self.MAX_SIB_AGE_DIFF
                if min_birth_year is None or min_from_sib > min_birth_year:
                    min_birth_year = min_from_sib
                    explain_birth_min = _("oldest sibling's age")

                max_from_sib = sib_birth_min + self.MAX_SIB_AGE_DIFF
                if max_birth_year is None or max_from_sib < max_birth_year:
                    max_birth_year = max_from_sib
                    explain_birth_max = _("youngest sibling's age")

        if birth_date is None or not birth_date.is_valid():
            birth_date = Date()  # make sure we have an empty date
            #  use proxy estimate
            if min_birth_year and max_birth_year:
                # create a range set
                birth_range = list(Date.EMPTY + Date.EMPTY)
                birth_range[Date._POS_YR] = min_birth_year
                birth_range[Date._POS_RYR] = max_birth_year
                birth_date.set(modifier=Date.MOD_RANGE, value=tuple(birth_range))
            else:
                if min_birth_year:
                    birth_date.set_yr_mon_day(min_birth_year, 1, 1)
                    birth_date.set_modifier(Date.MOD_AFTER)
                elif max_birth_year:
                    birth_date.set_yr_mon_day(max_birth_year, 12, 31)
                    birth_date.set_modifier(Date.MOD_BEFORE)
            birth_date.recalc_sort_value()

        # If we have no death date but we know death has happened then
        # we set death range somewhere between birth and yesterday.
        # otherwise we assume MAX years after birth
        if death_date is None:
            if birth_date and birth_date.is_valid():
                death_date = Date(birth_date)
                max_death_date = birth_date.copy_offset_ymd(
                    year=self.MAX_AGE_PROB_ALIVE
                )
                if known_to_be_dead:
                    if max_death_date.match(Today(), ">="):
                        max_death_date = Today()
                        max_death_date.set_yr_mon_day_offset(
                            day=-1
                        )  # make it yesterday
                    # range start value stays at birth date
                    death_date.set_modifier(Date.MOD_RANGE)
                    death_date.set_text_value("")
                    death_date.set2_yr_mon_day(
                        max_death_date.get_year(),
                        max_death_date.get_month(),
                        max_death_date.get_day(),
                    )
                    explain_death = _("birth date and known to be dead")
                else:
                    death_date.set_yr_mon_day_offset(year=self.MAX_AGE_PROB_ALIVE)
                    explain_death = _("offset from birth date")
                death_date.recalc_sort_value()
            else:
                death_date = Date()

        # at this stage we should have valid dates for both birth and death,
        #  or else both are zero (if None then it's a bug).
        if birth_evidence_direct:
            explanation = _(
                "Direct evidence for this person - birth: {birth_min_src}, death: {death_src}"
            ).format(
                birth_min_src=explain_birth_min,
                death_src=explain_death,
            )
        elif explain_birth_max == "":
            explanation = _(
                "inferred from parents and siblings - birth: {birth_min_src}, death: {death_src}"
            ).format(
                birth_min_src=explain_birth_min,
                death_src=explain_death,
            )
        else:
            explanation = _(
                "inferred from parents and siblings - birth: {birth_min_src} (earliest) to {birth_max_src} (latest), death: {death_src}"
            ).format(
                birth_min_src=explain_birth_min,
                birth_max_src=explain_birth_max,
                death_src=explain_death,
            )

        if birth_date.is_valid() and death_date.is_valid():
            return (birth_date, death_date, explanation, person)

        # have finished immediate family, so try spouse, as the
        # remaining person (probably) of this generation ..

        def spouse_test(only_immediate_family):
            # test against spouse details - this is done in two passes, at different
            # stages of generating dates for the reference person.:
            # 1. test spouse details only - this should be a reasonable proxy for
            # reference person, after immediate family.
            # 2. run full test recursing into probably_alive_range
            # Only run this pass at the end - tests have higher uncertainty than the
            # same test on the reference person.
            # We allow for an age difference +/- AVG_GENERATION_GAP
            # which, assuming defaults, results in 150 year "probably alive" range.
            # In reality, if we have reached this far then any value is unreliable.

            LOG.debug(
                "    ----- trying spouse check: %s",
                "immediate family only" if only_immediate_family else "full tree",
            )
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
                    mother_handle = family.get_mother_handle()
                    father_handle = family.get_father_handle()
                    if mother_handle is None or father_handle is None:
                        if DEBUGLEVEL > 1:
                            LOG.debug(
                                "         single parent family: [%s]",
                                family.get_gramps_id(),
                            )
                        # no recorded spouse
                        continue
                    spouse = None
                    if mother_handle == person.handle:
                        spouse = self.db.get_person_from_handle(father_handle)
                    elif father_handle == person.handle:
                        spouse = self.db.get_person_from_handle(mother_handle)
                    if spouse is not None:
                        date1, date2, explain, other = self.probably_alive_range(
                            spouse,
                            is_spouse=True,
                            immediate_fam_only=only_immediate_family,
                        )
                        if DEBUGLEVEL > 2:
                            LOG.debug(
                                "            found spouse [%s], returned b:%s, d:%s, because:%s",
                                spouse.get_gramps_id(),
                                date1,
                                date2,
                                explain,
                            )
                        if date1 and date1.get_year() != 0:
                            birth_date = date1.copy_offset_ymd(-self.AVG_GENERATION_GAP)
                            if birth_date.is_compound():
                                # it will have already offset both values, so correct that
                                # and then offset to be 1 GEN GAP higher.
                                birth_date.set2_yr_mon_day_offset(
                                    2 * self.AVG_GENERATION_GAP
                                )
                            else:
                                birth_date.set_modifier(Date.MOD_RANGE)
                                birth_date.set_text_value("")
                                # duplicate lower birth limit
                                birth_date.set2_yr_mon_day(
                                    date1.get_year(),
                                    date1.get_month(),
                                    date1.get_day(),
                                )
                                # then extend upper limit the other direction
                                birth_date.set2_yr_mon_day_offset(
                                    self.AVG_GENERATION_GAP
                                )
                            death_date = birth_date.copy_offset_ymd(
                                self.MAX_AGE_PROB_ALIVE
                            )

                            return (
                                birth_date,
                                death_date,
                                _("a spouse's birth-related date, ") + explain,
                                other,
                            )
                        if date2 and date2.get_year() != 0:
                            return (
                                Date().copy_ymd(
                                    date2.get_year()
                                    + self.AVG_GENERATION_GAP
                                    - self.MAX_AGE_PROB_ALIVE
                                ),
                                Date().copy_ymd(
                                    date2.get_year() + self.AVG_GENERATION_GAP
                                ),
                                _("a spouse's death-related date, ") + explain,
                                other,
                            )

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
                                        other = self.db.get_person_from_handle(
                                            father_handle
                                        )
                                    elif (
                                        person.handle == father_handle and mother_handle
                                    ):
                                        other = self.db.get_person_from_handle(
                                            mother_handle
                                        )
                                    return (
                                        Date().copy_ymd(year - self.AVG_GENERATION_GAP),
                                        Date().copy_ymd(
                                            year
                                            - self.AVG_GENERATION_GAP
                                            + self.MAX_AGE_PROB_ALIVE
                                        ),
                                        _("event with spouse"),
                                        other,
                                    )
            return (None, None, "", None)

        if not is_spouse:
            birth_date, death_date, explain, who = spouse_test(True)
            if birth_date is not None and death_date is not None:
                return (birth_date, death_date, explain, who)
        elif immediate_fam_only:
            return (None, None, "", None)

        # Try to estimate probable lifespan by scanning descendants

        def recurse_descendants(person, generation):
            """
            Recursively scan descendants' tree to determine likely birth/death
            dates for the person specified.
            Returns the range of birth and/or deaths years for the closest generation
            in which any are available.
            generation: gets incremented as we descend the tree.
            Returns: birth_year_min, birth_year_max,
                death_year_min, death_year_max,
                n_generations,
                child
            min and max years will be either both None or both valid values
            If all years are None then n_generations will be None
            """

            no_valid_descendant = (None, None, None, None, None, None)
            if person.handle in self.pset:
                LOG.debug(
                    "....... person %s skipped - already seen in descendants test",
                    person.get_gramps_id(),
                )
                return no_valid_descendant
            if DEBUGLEVEL > 2:
                LOG.debug(
                    "     %s recursing into person [%s] %s, gen %s",
                    "..." * generation,
                    person.get_gramps_id(),
                    person.get_primary_name().get_gedcom_name(),
                    generation,
                )
            self.pset.add(person.handle)
            child_result = list()
            birth_min = birth_max = None
            death_min = death_max = None
            for family_handle in person.get_family_handle_list():
                # only families in which person is a parent or spouse of parent
                family = self.db.get_family_from_handle(family_handle)
                if not family:
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    continue
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    bdate, ddate, dfound, expb, expd = get_person_bd(child_handle)
                    cd = dict(
                        handle=child_handle,
                        birthdate=bdate,
                        deathdate=ddate,
                        deathfound=dfound,
                        birth_expl=expb,
                        death_expl=expd,
                    )
                    child_result.append(cd)
                    if bdate is not None or ddate is not None:
                        if bdate is not None:
                            byear = bdate.get_year()
                            if birth_min is None or byear < birth_min:
                                birth_min = byear
                            if birth_max is None or byear > birth_max:
                                birth_max = byear
                        if ddate is not None:
                            dyear = ddate.get_year()
                            if death_min is None or dyear < death_min:
                                death_min = dyear
                            if death_max is None or dyear > death_max:
                                death_max = dyear

            # if we have something at this stage then just report it and descend no further
            if birth_min is not None or death_min is not None:
                return (birth_min, birth_max, death_min, death_max, generation, person)
            # otherwise recursively scan childrens' descendants, accumulating the results
            nextgen = list()
            mingen = None
            for childdict in child_result:
                child_handle = childdict["handle"]
                child = self.db.get_person_from_handle(child_handle)

                bmin, bmax, dmin, dmax, ngens, who = recurse_descendants(
                    child, 1 + generation
                )
                if ngens is not None:
                    if mingen is None or ngens < mingen:
                        mingen = ngens
                    ngd = dict(
                        bmin=bmin,
                        bmax=bmax,
                        dmin=dmin,
                        dmax=dmax,
                        ngens=ngens,
                        who=who,
                    )
                    nextgen.append(ngd)
            # having accumulated all results from this generation's descendants,
            # identify the values from the closest generation
            if mingen is None:
                return no_valid_descendant
            gen_bmin = gen_bmax = None  # generational min/max birth years
            gen_dmin = gen_dmax = None  # generational min/max death years
            retb_who = retd_who = None
            for ngd in nextgen:
                if ngd["ngens"] > mingen:
                    continue
                bmin = ngd["bmin"]
                dmin = ngd["dmin"]
                if bmin is not None:
                    if gen_bmin is None or bmin < gen_bmin:
                        gen_bmin = bmin
                        retb_who = ngd["who"]
                    bmax = ngd["bmax"]
                    if gen_bmax is None or bmax > gen_bmax:
                        gen_bmax = bmax
                if dmin is not None:
                    if gen_dmin is None or dmin < gen_dmin:
                        gen_dmin = dmin
                    dmax = ngd["dmax"]
                    if gen_dmax is None or dmax > gen_dmax:
                        gen_dmax = dmax
                        retd_who = ngd["who"]

            # at this stage we have summary of closest result from all descendants of person
            if gen_bmin is not None or gen_dmin is not None:
                return (
                    gen_bmin,
                    gen_bmax,
                    gen_dmin,
                    gen_dmax,
                    mingen,
                    retd_who if retb_who is None else retb_who,
                )

            return no_valid_descendant

        def estimate_bd_range_from_descendants(person):
            """
            wrapper function to initiate descendant recursion and process final results.
            """
            bmin, bmax, dmin, dmax, ngens, other = recurse_descendants(person, 1)

            date1, date2, explain = None, None, ""
            if bmin is not None:
                # This could be extended to create more realistic ranges, but, let's face it,
                # if these dates are important then the users should be making realistic estimates
                # themselves.  We'll just use averages...
                meanbirth = (bmin + bmax) / 2
                if DEBUGLEVEL > 2:
                    LOG.debug(
                        "     == desc for %s returned bmin:%s, bmax:%s, ngens:%s, dmin:%s, dmax:%s, who:%s",
                        person.get_gramps_id(),
                        bmin,
                        bmax,
                        ngens,
                        dmin,
                        dmax,
                        (
                            "None"
                            if other is None
                            else other.get_primary_name().get_gedcom_name()
                        ),
                    )
                birth_year = int(meanbirth - (ngens * self.AVG_GENERATION_GAP))
                date1 = Date()
                date1.set_yr_mon_day(birth_year, 1, 1)
                date1.set_modifier(Date.MOD_ABOUT)
                date2 = date1.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE)
                explain = ngettext(
                    "descendant birth: {number_of} generation ",
                    "descendant birth: {number_of} generations ",
                    ngens,
                ).format(number_of=ngens)
            elif dmin is not None:
                # no births, just death dates ... unreliable estimates only
                # An upper limit would be based on min_generation_gap below the first death.
                # A lower limit could be based on no child exceeding 110 year
                upper_birth_year = dmin - (ngens * self.MIN_GENERATION_YEARS)
                lower_birth_year = dmax - (
                    ngens * self.AVG_GENERATION_GAP + self.MAX_AGE_PROB_ALIVE
                )
                if lower_birth_year > upper_birth_year:
                    upper_birth_year, lower_birth_year = (
                        lower_birth_year,
                        upper_birth_year,
                    )
                date1 = Date()
                date1.set_yr_mon_day(lower_birth_year, 1, 1)
                date1.set_modifier(Date.MOD_RANGE)
                date1.set2_yr_mon_day(upper_birth_year, 1, 1)
                date2 = date1.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE)
                explain = ngettext(
                    "descendant death: {number_of} generation ",
                    "descendant death: {number_of} generations ",
                    ngens,
                ).format(number_of=ngens)
            if date1 and date2:
                return (date1, date2, explain, other)
            return (None, None, "", None)

        LOG.debug("    ------- checking descendants of [%s]", person.get_gramps_id())
        date1, date2, explain, other = None, None, "", None
        try:
            date1, date2, explain, other = estimate_bd_range_from_descendants(person)

        except RuntimeError:
            raise DatabaseError(
                _("Database error: loop in descendants of %s.")
                % name_displayer.display(person)
            )

        if date1 and date2:
            return (date1, date2, explain, other)

        self.pset = set()  # clear the list from descendant check

        # Try to estimate probable lifespan by scanning ancestors. We have already
        # checked person's parents, so we should scan each of their ancestors

        def estimate_bd_range_from_ancestors(person, year, generation):
            """
            Estimate birth and death year ranges based on a person's ancestors.
            The year value is the average number of years between generations.
            generation parameter is current depth of recursion.
            """
            range_not_found = (None, None, "", None, None)
            if person.handle in self.pset:
                LOG.debug(
                    "....... person %s skipped - already seen in ancestor test",
                    person.get_gramps_id(),
                )
                return range_not_found
            self.pset.add(person.handle)

            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = self.db.get_family_from_handle(family_handle)
                if not family:
                    # can happen with LivingProxyDb(PrivateProxyDb(db))
                    return range_not_found
                mother_handle = family.get_mother_handle()
                (
                    mother_birth,
                    mother_death,
                    mother_death_found,
                    mother_expl_b,
                    mother_expl_d,
                ) = get_person_bd(mother_handle)

                father_handle = family.get_father_handle()
                (
                    father_birth,
                    father_death,
                    father_death_found,
                    father_expl_b,
                    father_expl_d,
                ) = get_person_bd(father_handle)

                parent_birth = mother_birth
                explan = _("mother birth ") + mother_expl_b
                parenth = mother_handle
                if parent_birth is None:
                    parent_birth = father_birth
                    explan = _("father birth ") + father_expl_b
                    parenth = father_handle
                elif father_birth is not None:
                    # have both births, try for youngest
                    if father_birth.match(mother_birth, ">"):
                        parent_birth = father_birth
                        explan = _("father birth ") + father_expl_b
                        parenth = father_handle
                if parent_birth is not None:
                    person_birth = parent_birth.copy_offset_ymd(year)
                    person_death = person_birth.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE)
                    return (
                        person_birth,
                        person_death,
                        _("ancestor ") + explan,
                        self.db.get_person_from_handle(parenth),
                        generation,
                    )
                # no useful birth, try death...
                first_parent_death = parent_death = mother_death
                explan = _("mother death ") + mother_expl_d
                parenth = mother_handle
                if parent_death is None:
                    first_parent_death = parent_death = father_death
                    explan = _("father death ") + father_expl_d
                    parenth = father_handle
                elif father_death is not None:
                    # have both deaths, try for last to die
                    if father_death.match(mother_death, ">"):
                        parent_death = father_death
                        explan = _("father death ") + father_expl_b
                        parenth = father_handle
                        first_parent_death = mother_death
                if parent_death is not None:
                    person_birth = parent_death.copy_offset_ymd(
                        year - self.MAX_AGE_PROB_ALIVE
                    )
                    person_birth.set_modifier(Date.MOD_RANGE)
                    person_birth.set2_yr_mon_day(
                        year + first_parent_death.get_year(), 1, 1
                    )
                    person_death = person_birth.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE)
                    return (
                        person_birth,
                        person_death,
                        _("ancestor ") + explan,
                        self.db.get_person_from_handle(parenth),
                        generation,
                    )

                # nothing found yet, so recurse up the mother's line first
                # This becomes a depth-first search, which is undesirable,
                # but we choose the shortest number of generations from the responses
                # not very efficient, but...
                gen_m = gen_f = None
                if mother_handle is not None:
                    date1_m, date2_m, explan_m, other_m, gen_m = (
                        estimate_bd_range_from_ancestors(
                            self.db.get_person_from_handle(mother_handle),
                            year + self.AVG_GENERATION_GAP,
                            generation + 1,
                        )
                    )
                # now try the father's line
                if father_handle is not None:
                    date1_f, date2_f, explan_f, other_f, gen_f = (
                        estimate_bd_range_from_ancestors(
                            self.db.get_person_from_handle(father_handle),
                            year + self.AVG_GENERATION_GAP,
                            generation + 1,
                        )
                    )
                # now decide which of maternal/paternal lines is better choice.
                use_side = "none"
                if gen_m is not None and gen_f is not None:
                    # if both maternal and paternal ancestral lines returned values,
                    # then take shortest depth.
                    if gen_f < gen_m:
                        use_side = "father"
                    else:
                        use_side = "mother"
                elif gen_m is not None:
                    use_side = "mother"
                elif gen_f is not None:
                    use_side = "father"

                if use_side == "mother":
                    if date1_m and date2_m:
                        return (date1_m, date2_m, explan_m, other_m, gen_m)
                elif use_side == "father":
                    if date1_f and date2_f:
                        return (date1_f, date2_f, explan_f, other_f, gen_f)

            return range_not_found

        if parenth_p1:
            LOG.debug("    ------ checking ancestors %s", person.get_gramps_id())
            try:
                date1, date2, explain, other, gen = estimate_bd_range_from_ancestors(
                    person, int(self.AVG_GENERATION_GAP), 1
                )
            except RuntimeError:
                raise DatabaseError(
                    _("Database error: loop in ancestors of %s.")
                    % name_displayer.display(person)
                )

            if date1 is not None and date2 is not None:
                return (date1, date2, explain, other)

        if not is_spouse:  # if you are not in recursion, let's recurse again:
            birth_date, death_date, explain, who = spouse_test(False)
            if birth_date is not None and death_date is not None:
                return (birth_date, death_date, explain, who)

        # If we can't find any reason to believe that they are dead we
        # must assume they are alive.

        return (None, None, "", None)


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
                         (defaults to today if None or a blank string)
    :param limit: number of years to check beyond death_date
    :param max_sib_age_diff: maximum sibling age difference, in years
            if None then default to the setting in user config
    :param max_age_prob_alive: maximum age of a person, in years
            if None then default to the setting in user config
    :param avg_generation_gap: average generation gap, in years
    """
    LOG.debug(
        " *** probably_alive() called for [%s] %s: ",
        person.get_gramps_id(),
        person.get_primary_name().get_gedcom_name(),
    )
    # First, get the probable birth and death ranges for
    # this person from the real database:
    birth, death, explain, relative = probably_alive_range(
        person, db, max_sib_age_diff, max_age_prob_alive, avg_generation_gap
    )
    if current_date is None or not current_date.is_valid():
        current_date = Today()

    if DEBUGLEVEL > 0:
        if relative is None:
            rel_id = "nobody"
        else:
            rel_id = relative.get_gramps_id()
        LOG.debug(
            "      range: b.%s, d.%s vs %s reason: %s to [%s]",
            birth,
            death,
            current_date,
            explain,
            rel_id,
        )
    if not birth and not death:
        # no evidence, must consider alive
        LOG.debug(
            "      [%s] %s: decided alive - no evidence",
            person.get_gramps_id(),
            person.get_primary_name().get_gedcom_name(),
        )
        return (True, None, None, _("no evidence"), None) if return_range else True
    if not birth or not death:
        # insufficient evidence, must consider alive
        LOG.debug(
            "   LOGIC ERROR -  [%s] %s: only %s found; decided alive",
            person.get_gramps_id(),
            person.get_primary_name().get_gedcom_name(),
            "birth" if birth else "death",
        )
        return (True, None, None, _("no evidence"), None) if return_range else True
    # must have dates from here:
    if limit:
        death += limit  # add these years to death
    # Finally, check to see if current_date is between dates
    # ---true if  current_date >= birth(min)   and  true if current_date < death
    # these include true if current_date is within the estimated range
    result = current_date.match(birth, ">=") and current_date.match(death, "<")
    if DEBUGLEVEL > 3:
        (bthmin, bthmax) = birth.get_start_stop_range()
        (dthmin, dthmax) = death.get_start_stop_range()
        (dmin, dmax) = current_date.get_start_stop_range()
        LOG.debug(
            "        alive=%s, btest: %s, dtest: %s (born %s-%s, dd %s-%s) vs (%s-%s)",
            result,
            current_date.match(birth, ">="),
            current_date.match(death, "<"),
            bthmin,
            bthmax,
            dthmin,
            dthmax,
            dmin,
            dmax,
        )
    if return_range:
        return (result, birth, death, explain, relative)

    return result


def probably_alive_range(
    person, db, max_sib_age_diff=None, max_age_prob_alive=None, avg_generation_gap=None
):
    """
    Computes estimated birth and death date ranges.
    Returns: (birth_date, death_date, explain_text, related_person)
    """
    # First, find the real database to use all people
    # for determining alive status:
    basedb = db
    while isinstance(basedb, ProxyDbBase):
        basedb = basedb.db
    # Now, we create a wrapper for doing work:
    pbac = ProbablyAlive(
        basedb, max_sib_age_diff, max_age_prob_alive, avg_generation_gap
    )
    return pbac.probably_alive_range(person)


def update_constants():
    """
    Used to update the constants that are cached in this module.
    """

    global _MAX_AGE_PROB_ALIVE, _MAX_SIB_AGE_DIFF
    global _AVG_GENERATION_GAP, _MIN_GENERATION_YEARS
    _MAX_AGE_PROB_ALIVE = config.get("behavior.max-age-prob-alive")
    _MAX_SIB_AGE_DIFF = config.get("behavior.max-sib-age-diff")
    _AVG_GENERATION_GAP = config.get("behavior.avg-generation-gap")
    _MIN_GENERATION_YEARS = config.get("behavior.min-generation-years")
