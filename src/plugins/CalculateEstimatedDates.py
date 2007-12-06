#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: $

"Calculate Estimated Dates"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import time

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import Tool, register_tool, PluginWindows, \
    MenuToolOptions, BooleanOption, FilterListOption, StringOption, \
    NumberOption
import gen.lib
import Config

class CalcEstDateOptions(MenuToolOptions):
    """ Calculate Estimated Date options  """
    
    def add_menu_options(self, menu):
        """ Adds the options """
        category_name = _("Options")

        filter = FilterListOption(_("Filter"))
        filter.add_item("person")
        filter.set_help(_("Select filter to restrict people"))
        menu.add_option(category_name,"filter", filter)

        source_text = StringOption(_("Source text"), 
                                   _("Calculated Date Estimates"))
        source_text.set_help(_("Source to remove and/or add"))
        menu.add_option(category_name, "source_text", source_text)

        remove = BooleanOption(_("Remove previously added dates"), True)
        remove.set_help(_("Remove"))
        menu.add_option(category_name, "remove", remove)

        birth = BooleanOption(_("Add estimated birth dates"), True)
        birth.set_help(_("Add"))
        menu.add_option(category_name, "add_birth", birth)

        death = BooleanOption(_("Add estimated death dates"), True)
        death.set_help(_("Add estimated death dates"))
        menu.add_option(category_name, "add_death", death)

        # -----------------------------------------------------
        category_name = _("Config")
        num = NumberOption(_("Maximum age"), 
                           Config.get(Config.MAX_AGE_PROB_ALIVE),
                           0, 200)
        num.set_help(_("Maximum age that one can live to"))
        menu.add_option(category_name, "MAX_AGE_PROB_ALIVE", num)

        num = NumberOption(_("Maximum sibling age difference"), 
                           Config.get(Config.MAX_SIB_AGE_DIFF),
                           0, 200)
        num.set_help(_("Maximum age difference between siblings"))
        menu.add_option(category_name, "MAX_SIB_AGE_DIFF", num)

        num = NumberOption(_("Minimum years between generations"), 
                           Config.get(Config.MIN_GENERATION_YEARS),
                           0, 200)
        num.set_help(_("Minimum years between two generations"))
        menu.add_option(category_name, "MIN_GENERATION_YEARS", num)

        num = NumberOption(_("Average years between generations"), 
                           Config.get(Config.AVG_GENERATION_GAP),
                           0, 200)
        num.set_help(_("Average years between two generations"))
        menu.add_option(category_name, "AVG_GENERATION_GAP", num)


class CalcToolManagedWindow(PluginWindows.ToolManagedWindowBatch):

    def initial_frame(self):
        return _("Options")

    def run(self):
        self.add_results_frame()
        self.results_write("Processing...\n")
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        self.filter = self.options.handler.options_dict['filter']
        people = self.filter.apply(self.db,
                                   self.db.get_person_handles(sort_handles=False))
        source_text = self.options.handler.options_dict['source_text']
        add_birth = self.options.handler.options_dict['add_birth']
        add_death = self.options.handler.options_dict['add_death']
        remove_old = self.options.handler.options_dict['remove']

        self.MIN_GENERATION_YEARS = self.options.handler.options_dict['MIN_GENERATION_YEARS']
        self.MAX_SIB_AGE_DIFF = self.options.handler.options_dict['MAX_SIB_AGE_DIFF']
        self.MAX_AGE_PROB_ALIVE = self.options.handler.options_dict['MAX_AGE_PROB_ALIVE']
        self.AVG_GENERATION_GAP = self.options.handler.options_dict['AVG_GENERATION_GAP']
        if remove_old:
            self.results_write("Replacing...\n")
            self.progress.set_pass(_("Removing '%s'..." % source_text), 
                                   len(people))
            for person_handle in people:
                self.progress.step()
                pupdate = 0
                person = self.db.get_person_from_handle(person_handle)
                birth_ref = person.get_birth_ref()
                if birth_ref:
                    birth = self.db.get_event_from_handle(birth_ref.ref)
                    source_list = birth.get_source_references()
                    for source_ref in source_list:
                        #print "birth handle:", source_ref
                        source = self.db.get_source_from_handle(source_ref.ref)
                        if source:
                            #print "birth source:", source, source.get_title()
                            if source.get_title() == source_text:
                                person.set_birth_ref(None)
                                person.remove_handle_references('Event',[birth_ref.ref])
                                self.db.remove_event(birth_ref.ref, self.trans)
                                self.db.commit_source(source, self.trans)
                                pupdate = 1
                                break
                death_ref = person.get_death_ref()
                if death_ref:
                    death = self.db.get_event_from_handle(death_ref.ref)
                    source_list = death.get_source_references()
                    for source_ref in source_list:
                        #print "death handle:", source_ref
                        source = self.db.get_source_from_handle(source_ref.ref)
                        if source:
                            #print "death source:", source, source.get_title()
                            if source.get_title() == source_text:
                                person.set_death_ref(None)
                                person.remove_handle_references('Event',[death_ref.ref])
                                self.db.remove_event(death_ref.ref, self.trans)
                                self.db.commit_source(source, self.trans)
                                pupdate = 1
                                break
                if pupdate == 1:
                    self.db.commit_person(person, self.trans)
        if add_birth or add_death:
            self.results_write("Calculating...\n")
            self.progress.set_pass(_('Calculating estimated dates...'), 
                                   len(people))
            source = self.get_or_create_source(source_text)
            for person_handle in people:
                self.progress.step()
                person = self.db.get_person_from_handle(person_handle)
                birth_ref = person.get_birth_ref()
                death_ref = person.get_death_ref()
                #print birth_ref, death_ref
                date1, date2 = self.calc_estimates(person, birth_ref, death_ref)
                #print date1, date2
                if not birth_ref and add_birth and date1:
                    #print "added birth"
                    birth = self.create_event("Estimated birth date", 
                                              gen.lib.EventType.BIRTH, 
                                              date1, source)
                    event_ref = gen.lib.EventRef()
                    event_ref.set_reference_handle(birth.get_handle())
                    person.set_birth_ref(event_ref)
                    self.db.commit_person(person, self.trans)
                if not death_ref and add_death and date2:
                    current_date = gen.lib.Date()
                    current_date.set_yr_mon_day(*time.localtime(time.time())[0:3])
                    if current_date.match( date2, "<<"):
                        # don't add events in the future!
                        pass
                    else:
                        #print "added death"
                        death = self.create_event("Estimated death date", 
                                                  gen.lib.EventType.DEATH, 
                                                  date2, source)
                        event_ref = gen.lib.EventRef()
                        event_ref.set_reference_handle(death.get_handle())
                        person.set_death_ref(event_ref)
                        self.db.commit_person(person, self.trans)
        self.db.transaction_commit(self.trans, _("Calculate date estimates"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.results_write("Done!\n")

    def get_or_create_source(self, source_text):
        source_list = self.db.get_source_handles()
        for source_handle in source_list:
            source = self.db.get_source_from_handle(source_handle)
            if source.get_title() == source_text:
                return source
        source = gen.lib.Source()
        source.set_title(source_text)
        self.db.add_source(source, self.trans)
        return source

    def create_event(self, description="Estimated date", 
                     type=None, date=None, source=None):
        event = gen.lib.Event()
        event.set_description(description)
        if type:
            event.set_type(gen.lib.EventType(type))
        if date:
            date.set_modifier(gen.lib.Date.MOD_ABOUT)
            date.set_quality(gen.lib.Date.QUAL_ESTIMATED)
            date.set_yr_mon_day(date.get_year(), 0, 0)
            event.set_date_object(date)
        if source:
            sref = gen.lib.SourceRef()
            sref.set_reference_handle(source.get_handle())
            event.add_source_reference(sref)
            self.db.commit_source(source, self.trans)
        self.db.add_event(event, self.trans)
        return event

    def calc_estimates(self, person, birth_ref, death_ref):
        death_date = None
        birth_date = None
        # If the recorded death year is before current year then
        # things are simple.
        if death_ref and death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
            death = self.db.get_event_from_handle(death_ref.ref)
            if death.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
                death_date = death.get_date_object()

        # Look for Cause Of Death, Burial or Cremation events.
        # These are fairly good indications that someone's not alive.
        for ev_ref in person.get_primary_event_ref_list():
            ev = self.db.get_event_from_handle(ev_ref.ref)
            if ev and int(ev.get_type()) in [gen.lib.EventType.CAUSE_DEATH, 
                                             gen.lib.EventType.BURIAL, 
                                             gen.lib.EventType.CREMATION]:
                if not death_date:
                    death_date = ev.get_date_object()

        # If they were born within 100 years before current year then
        # assume they are alive (we already know they are not dead).
        if birth_ref and birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
            birth = self.db.get_event_from_handle(birth_ref.ref)
            if birth.get_date_object().get_start_date() != gen.lib.Date.EMPTY:
                if not birth_date:
                    birth_date = birth.get_date_object()

        #print "   calculating...", birth_date, death_date

        if not birth_date and death_date:
            # person died more than MAX after current year
            birth_date = death_date.copy_offset_ymd(year=-self.MAX_AGE_PROB_ALIVE)

        if not death_date and birth_date:
            # person died more than MAX after current year
            death_date = birth_date.copy_offset_ymd(year=self.MAX_AGE_PROB_ALIVE)

        if death_date and birth_date:
            return (birth_date, death_date)
        
        # Neither birth nor death events are available. Try looking
        # at siblings. If a sibling was born more than 120 years past, 
        # or more than 20 future, then probably this person is
        # not alive. If the sibling died more than 120 years
        # past, or more than 120 years future, then probably not alive.

        #print "    searching family..."

        family_list = person.get_parent_family_handle_list()
        for family_handle in family_list:
            family = self.db.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                child = self.db.get_person_from_handle(child_handle)
                child_birth_ref = child.get_birth_ref()
                if child_birth_ref:
                    child_birth = self.db.get_event_from_handle(child_birth_ref.ref)
                    dobj = child_birth.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        # if sibling birth date too far away, then not alive:
                        year = dobj.get_year()
                        if year != 0:
                            # sibling birth date
                            return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF),
                                    gen.lib.Date().copy_ymd(year + self.MAX_SIB_AGE_DIFF + self.MAX_AGE_PROB_ALIVE))
                child_death_ref = child.get_death_ref()
                if child_death_ref:
                    child_death = self.db.get_event_from_handle(child_death_ref.ref)
                    dobj = child_death.get_date_object()
                    if dobj.get_start_date() != gen.lib.Date.EMPTY:
                        # if sibling death date too far away, then not alive:
                        year = dobj.get_year()
                        if year != 0:
                            # sibling death date
                            return (gen.lib.Date().copy_ymd(year - self.MAX_SIB_AGE_DIFF - self.MAX_AGE_PROB_ALIVE),
                                    gen.lib.Date().copy_ymd(year + self.MAX_SIB_AGE_DIFF))

        # Try looking for descendants that were born more than a lifespan
        # ago.

        def descendants_too_old (person, years):
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    child = self.db.get_person_from_handle(child_handle)
                    child_birth_ref = child.get_birth_ref()
                    if child_birth_ref:
                        child_birth = self.db.get_event_from_handle(child_birth_ref.ref)
                        dobj = child_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            d = gen.lib.Date(dobj)
                            val = d.get_start_date()
                            val = d.get_year() - years
                            d.set_year(val)
                            return (d, d.copy_offset_ymd(self.MAX_AGE_PROB_ALIVE))
                    child_death_ref = child.get_death_ref()
                    if child_death_ref:
                        child_death = self.db.get_event_from_handle(child_death_ref.ref)
                        dobj = child_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- self.MIN_GENERATION_YEARS), 
                                    dobj.copy_offset_ymd(- self.MIN_GENERATION_YEARS + self.MAX_AGE_PROB_ALIVE))
                    date1, date2 = descendants_too_old (child, years + self.MIN_GENERATION_YEARS)
                    if date1 and date2:
                        return date1, date2
            return (None, None)

        # If there are descendants that are too old for the person to have
        # been alive in the current year then they must be dead.

        date1, date2 = None, None
        try:
            date1, date2 = descendants_too_old(person, self.MIN_GENERATION_YEARS)
        except RuntimeError:
            raise Errors.DatabaseError(
                _("Database error: %s is defined as his or her own ancestor") %
                name_displayer.display(person))

        if date1 and date2:
            return (date1, date2)

        def ancestors_too_old(person, year):
            family_handle = person.get_main_parents_family_handle()
            if family_handle:                
                family = self.db.get_family_from_handle(family_handle)
                father_handle = family.get_father_handle()
                if father_handle:
                    father = self.db.get_person_from_handle(father_handle)
                    father_birth_ref = father.get_birth_ref()
                    if father_birth_ref and father_birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                        father_birth = self.db.get_event_from_handle(
                            father_birth_ref.ref)
                        dobj = father_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year), 
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE))
                    father_death_ref = father.get_death_ref()
                    if father_death_ref and father_death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                        father_death = self.db.get_event_from_handle(
                            father_death_ref.ref)
                        dobj = father_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE))
                    date1, date2 = ancestors_too_old (father, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return date1, date2
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                    mother_birth_ref = mother.get_birth_ref()
                    if mother_birth_ref and mother_birth_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                        mother_birth = self.db.get_event_from_handle(mother_birth_ref.ref)
                        dobj = mother_birth.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year), 
                                    dobj.copy_offset_ymd(- year + self.MAX_AGE_PROB_ALIVE))
                    mother_death_ref = mother.get_death_ref()
                    if mother_death_ref and mother_death_ref.get_role() == gen.lib.EventRoleType.PRIMARY:
                        mother_death = self.db.get_event_from_handle(
                            mother_death_ref.ref)
                        dobj = mother_death.get_date_object()
                        if dobj.get_start_date() != gen.lib.Date.EMPTY:
                            return (dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE), 
                                    dobj.copy_offset_ymd(- year - self.MAX_AGE_PROB_ALIVE + self.MAX_AGE_PROB_ALIVE))
                    date1, date2 = ancestors_too_old (mother, year - self.AVG_GENERATION_GAP)
                    if date1 and date2:
                        return (date1, date2)
            return (None, None)

        # If there are ancestors that would be too old in the current year
        # then assume our person must be dead too.
        date1, date2 = ancestors_too_old (person, - self.MIN_GENERATION_YEARS)
        if date1 and date2:
            return (date1, date2)
        #print "   FAIL"
        # If we can't find any reason to believe that they are dead we
        # must assume they are alive.
        return (None, None)

#-------------------------------------------------------------------------
#
# Register the tool
#
#-------------------------------------------------------------------------
register_tool(
    name = 'calculateestimateddates',
    category = Tool.TOOL_DBPROC,
    tool_class = CalcToolManagedWindow,
    options_class = CalcEstDateOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Calculate Estimated Dates"),
    status = _("Beta"),
    author_name = "Douglas S. Blank",
    author_email = "dblank@cs.brynmawr.edu",
    description=_("Calculates estimated dates for birth and death.")
    )
