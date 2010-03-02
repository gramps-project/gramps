# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
# Copyright (C) 2008  Brian Matherly
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

# $Id$

"Calculate Estimated Dates"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _
import time

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import Tool, PluginWindows, MenuToolOptions
from gen.plug.menu import BooleanOption, NumberOption, StringOption, \
                         FilterOption, PersonOption, EnumeratedListOption
import gen.lib
import config
from gen.display.name import displayer as name_displayer
import Errors
from ReportBase import ReportUtils
from docgen import TextBufDoc
from Simple import make_basic_stylesheet, SimpleAccess, SimpleDoc, SimpleTable
from QuestionDialog import QuestionDialog
from Utils import create_id, probably_alive_range
import DateHandler

#------------------------------------------------------------------------
#
# Tool Classes
#
#------------------------------------------------------------------------
class CalcEstDateOptions(MenuToolOptions):
    """ Calculate Estimated Date options  """
    def __init__(self, name, person_id=None, dbstate=None):
        self.__db = dbstate.get_database()
        self.__dbstate = dbstate
        MenuToolOptions.__init__(self, name, person_id, dbstate)

    def get_dbstate(self):
        return self.__dbstate
    
    def add_menu_options(self, menu):
        
        """ Add the options """
        category_name = _("Options")
        
        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(_("Select filter to restrict people"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)
        
        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()

        source_text = StringOption(_("Source text"), 
                                   _("Calculated Date Estimates"))
        source_text.set_help(_("Source to remove and/or add"))
        menu.add_option(category_name, "source_text", source_text)

        remove = BooleanOption(_("Remove previously added events, notes, and source"), True)
        remove.set_help(_("Remove calculated events, notes, and source; occurs immediately on Execute"))
        menu.add_option(category_name, "remove", remove)

        birth = EnumeratedListOption(_("Birth"), 0)
        birth.add_item(0, _("Do not add birth events"))
        birth.add_item(1, _("Add birth events without dates"))
        birth.add_item(2, _("Add birth events with dates"))
        birth.set_help( _("Add a birth events with or without estimated dates"))
        menu.add_option(category_name, "add_birth", birth)

        death = EnumeratedListOption(_("Death"), 0)
        death.add_item(0, _("Do not add death events"))
        death.add_item(1, _("Add death events without dates"))
        death.add_item(2, _("Add death events with dates"))
        death.set_help( _("Add death events with or without estimated dates"))
        menu.add_option(category_name, "add_death", death)

        # -----------------------------------------------------
        num = NumberOption(_("Maximum age"), 
                           config.get('behavior.max-age-prob-alive'),
                           0, 200)
        num.set_help(_("Maximum age that one can live to"))
        menu.add_option(category_name, "MAX_AGE_PROB_ALIVE", num)

        num = NumberOption(_("Maximum sibling age difference"), 
                           config.get('behavior.max-sib-age-diff'),
                           0, 200)
        num.set_help(_("Maximum age difference between siblings"))
        menu.add_option(category_name, "MAX_SIB_AGE_DIFF", num)

        num = NumberOption(_("Average years between generations"), 
                           config.get('behavior.avg-generation-gap'),
                           0, 200)
        num.set_help(_("Average years between two generations"))
        menu.add_option(category_name, "AVG_GENERATION_GAP", num)

        dates = EnumeratedListOption(_("Estimated Dates"), 0)
        dates.add_item(0, _("Approximate (about)"))
        dates.add_item(1, _("Extremes (after and before)"))
        dates.set_help( _("Dates on events are either about or after/before"))
        menu.add_option(category_name, "dates", dates)
        
    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)
        
    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 0, 2, 3, 4 and 5 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)


class CalcToolManagedWindow(PluginWindows.ToolManagedWindowBatch):

    def __init__(self, *args, **kwargs):
        PluginWindows.ToolManagedWindowBatch.__init__(self, *args, **kwargs)
        if self.fail: return
        self.help_page = self.add_page(_("Help"))
        self.write_to_page(self.help_page, 
                           _("The Calculate Estimated Dates Tool is used to add and remove "
                           "birth and death events for people that are missing these "
                           "events.\n\n"
                           "To use:\n"
                           "1. Go to the Options tab\n"
                           "2. Check the [ ] Remove option to remove previous estimates\n"
                           "3. Select the Add date options to date events with or without dates\n"
                           "4. Click on Execute\n"
                           "5. Select the people with which to add events\n"
                           "6. Click on 'Add Selected Events' button to create\n\n"
                           "NOTES: if you decide to make an event permanent, remove it from "
                           "the Source. Otherwise, it will get removed the next time you "
                           "automatically remove these events.\n\n"
                           "You may have to run the tool repeatedly (without removing previous "
                           "events) to add all of the events possible."))
        self.set_current_frame(_("Help"))

    def get_title(self):
        return _("Calculate Estimated Dates")

    def initial_frame(self):
        return _("Options")

    def set_reselect(self):
        self.reselect = True

    def run(self):
        BUTTONS = ((_("Select All"), self.select_all),
                   (_("Select None"), self.select_none),
                   (_("Toggle Selection"), self.toggle_select),
                   (_("Add Selected Events"), self.apply_selection),
                   )

        if hasattr(self, "table") and self.table:
            self.reselect = False
            if self.options.handler.options_dict['remove']:
                QuestionDialog(_("Remove Events, Notes, and Source and Reselect Data"),
                               _("Are you sure you want to remove previous events, notes, and source and reselect data?"),
                               _("Remove and Run Select Again"),
                               self.set_reselect,
                               self.window)
            else:
                QuestionDialog(_("Reselect Data"),
                               _("Are you sure you want to reselect data?"),
                               _("Run Select Again"),
                               self.set_reselect,
                               self.window)
            if not self.reselect:
                return

        current_date = gen.lib.Date()
        current_date.set_yr_mon_day(*time.localtime(time.time())[0:3])
        self.action = {}
        widget = self.add_results_frame(_("Select"))
        document = TextBufDoc(make_basic_stylesheet(), None)
        document.dbstate = self.dbstate
        document.uistate = self.uistate
        document.open("", container=widget)
        self.sdb = SimpleAccess(self.db)
        sdoc = SimpleDoc(document)
        stab = SimpleTable(self.sdb)
        self.table = stab
        stab.columns(_("Select"), _("Person"), _("Action"), 
                     _("Birth Date"), _("Death Date"), 
                     _("Evidence"), _("Relative"))
        self.results_write(_("Processing...\n"))
        self.filter_option =  self.options.menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter() # the actual filter
        people = self.filter.apply(self.db,
                                   self.db.iter_person_handles())
        num_people = self.db.get_number_of_people()
        source_text = self.options.handler.options_dict['source_text']
        source = None
        add_birth = self.options.handler.options_dict['add_birth']
        add_death = self.options.handler.options_dict['add_death']
        remove_old = self.options.handler.options_dict['remove']

        self.MAX_SIB_AGE_DIFF = self.options.handler.options_dict['MAX_SIB_AGE_DIFF']
        self.MAX_AGE_PROB_ALIVE = self.options.handler.options_dict['MAX_AGE_PROB_ALIVE']
        self.AVG_GENERATION_GAP = self.options.handler.options_dict['AVG_GENERATION_GAP']
        if remove_old:
            self.trans = self.db.transaction_begin("",batch=True)
            self.db.disable_signals()
            self.results_write(_("Removing old estimations... "))
            self.progress.set_pass((_("Removing '%s'...") % source_text), 
                                   num_people)
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
                                # remove note
                                note_list = birth.get_referenced_note_handles()
                                birth.remove_handle_references('Note', 
                                  [note_handle for (obj_type, note_handle) in note_list])
                                for (obj_type, note_handle) in note_list:
                                    self.db.remove_note(note_handle, self.trans)
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
                                # remove note
                                note_list = death.get_referenced_note_handles()
                                birth.remove_handle_references('Note', 
                                  [note_handle for (obj_type, note_handle) in note_list])
                                for (obj_type, note_handle) in note_list:
                                    self.db.remove_note(note_handle, self.trans)
                                self.db.remove_event(death_ref.ref, self.trans)
                                self.db.commit_source(source, self.trans)
                                pupdate = 1
                                break
                if pupdate == 1:
                    self.db.commit_person(person, self.trans)
            if source:
                self.db.remove_source(source.handle, self.trans)
            self.results_write(_("done!\n"))
            self.db.transaction_commit(self.trans, _("Removed date estimates"))
            self.db.enable_signals()
            self.db.request_rebuild()
        if add_birth or add_death:
            self.results_write(_("Selecting... \n\n"))
            self.progress.set_pass(_('Selecting...'), 
                                   num_people)
            row = 0
            for person_handle in people:
                self.progress.step()
                person = self.db.get_person_from_handle(person_handle)
                birth_ref = person.get_birth_ref()
                death_ref = person.get_death_ref()
                add_birth_event, add_death_event = False, False
                if not birth_ref or not death_ref:
                    date1, date2, explain, other = self.calc_estimates(person)
                    if birth_ref:
                        ev = self.db.get_event_from_handle(birth_ref.ref)
                        date1 = ev.get_date_object()
                    elif not birth_ref and add_birth and date1:
                        if date1.match( current_date, "<"):
                            add_birth_event = True
                            date1.make_vague()
                        else:
                            date1 = gen.lib.Date()
                    else:
                        date1 = gen.lib.Date()
                    if death_ref:
                        ev = self.db.get_event_from_handle(death_ref.ref)
                        date2 = ev.get_date_object()
                    elif not death_ref and add_death and date2:
                        if date2.match( current_date, "<"):
                            add_death_event = True
                            date2.make_vague()
                        else:
                            date2 = gen.lib.Date()
                    else:
                        date2 = gen.lib.Date()
                    # Describe
                    if add_birth_event and add_death_event: 
                        action = _("Add birth and death events")
                    elif add_birth_event:
                        action = _("Add birth event")
                    elif add_death_event: 
                        action = _("Add death event")
                    else:
                        continue
                    #stab.columns(_("Select"), _("Person"), _("Action"), 
                    # _("Birth Date"), _("Death Date"), _("Evidence"), _("Relative"))
                    if add_birth == 1 and not birth_ref: # no date
                        date1 = gen.lib.Date()
                    if add_death == 1 and not death_ref: # no date
                        date2 = gen.lib.Date()
                    if person == other:
                        other = None
                    stab.row("checkbox", 
                             person, 
                             action, 
                             date1,
                             date2,
                             explain or "", 
                             other or "")
                    if add_birth_event:
                        stab.set_cell_markup(3, row, "<b>%s</b>" % DateHandler.displayer.display(date1))
                    if add_death_event:
                        stab.set_cell_markup(4, row, "<b>%s</b>" % DateHandler.displayer.display(date2))
                    self.action[person.handle] = (add_birth_event, add_death_event)
                    row += 1
            if row > 0:
                self.results_write("  ")
                for text, function in BUTTONS:
                    self.make_button(text, function, widget)
                self.results_write("\n")
                stab.write(sdoc)
                self.results_write("  ")
                for text, function in BUTTONS:
                    self.make_button(text, function, widget)
                self.results_write("\n")
            else:
                self.results_write(_("No events to be added."))
                self.results_write("\n")
        self.results_write("\n")
        self.progress.close()
        self.set_current_frame(_("Select"))

    def make_button(self, text, function, widget):
        import gtk
        button = gtk.Button(text)
        buffer = widget.get_buffer()
        iter = buffer.get_end_iter()
        anchor = buffer.create_child_anchor(iter)
        widget.add_child_at_anchor(button, anchor)
        button.connect("clicked", function)
        button.show()
        self.results_write("  ")

    def select_all(self, obj):
        select_col = self.table.model_index_of_column[_("Select")]
        for row in self.table.treeview.get_model():
            row[select_col] = True 

    def select_none(self, obj):
        select_col = self.table.model_index_of_column[_("Select")]
        for row in self.table.treeview.get_model():
            row[select_col] = False

    def toggle_select(self, obj):
        select_col = self.table.model_index_of_column[_("Select")]
        for row in self.table.treeview.get_model():
            row[select_col] = not row[select_col]

    def apply_selection(self, *args, **kwargs):
        # Do not add birth or death event if one exists, no matter what
        if self.table.treeview.get_model() is None:
            return
        self.trans = self.db.transaction_begin("",batch=True)
        self.pre_run()
        source_text = self.options.handler.options_dict['source_text']
        select_col = self.table.model_index_of_column[_("Select")]
        source = self.get_or_create_source(source_text)
        self.db.disable_signals()
        self.results_write(_("Selecting... "))
        self.progress.set_pass((_("Adding events '%s'...") % source_text), 
                               len(self.table.treeview.get_model()))
        count = 0
        for row in self.table.treeview.get_model():
            self.progress.step()
            select = row[select_col] # live select value
            if not select:
                continue
            pupdate = False
            index = row[0] # order put in
            row_data = self.table.get_raw_data(index)
            person = row_data[1] # check, person, action, date1, date2
            date1 = row_data[3] # date
            date2 = row_data[4] # date
            evidence = row_data[5] # evidence
            other = row_data[6] # other person
            add_birth_event, add_death_event = self.action[person.handle]
            birth_ref = person.get_birth_ref()
            death_ref = person.get_death_ref()
            if not birth_ref and add_birth_event:
                other_name = self.sdb.name(other)
                if other_name:
                    explanation = _("Added birth event based on %(evidence)s, from %(name)s") % {
                        'evidence' : evidence, 'name' : other_name }
                else:
                    explanation = _("Added birth event based on %s") % evidence
                modifier = self.get_modifier("birth")
                birth = self.create_event(_("Estimated birth date"), 
                                          gen.lib.EventType.BIRTH, 
                                          date1, source, explanation, modifier)
                event_ref = gen.lib.EventRef()
                event_ref.set_reference_handle(birth.get_handle())
                person.set_birth_ref(event_ref)
                pupdate = True
                count += 1
            if not death_ref and add_death_event:
                other_name = self.sdb.name(other)
                if other_name:
                    explanation = _("Added death event based on %(evidence)s, from %(person)s") % {
                    'evidence' : evidence, 'person' : other_name }
                else:
                    explanation = _("Added death event based on %s") % evidence
                modifier = self.get_modifier("death")
                death = self.create_event(_("Estimated death date"), 
                                          gen.lib.EventType.DEATH, 
                                          date2, source, explanation, modifier)
                event_ref = gen.lib.EventRef()
                event_ref.set_reference_handle(death.get_handle())
                person.set_death_ref(event_ref)
                pupdate = True
                count += 1
            if pupdate:
                self.db.commit_person(person, self.trans)
        self.results_write(_(" Done! Committing..."))
        self.results_write("\n")
        self.db.transaction_commit(self.trans, _("Add date estimates"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.results_write(_("Added %d events.") % count)
        self.results_write("\n\n")
        self.progress.close()

    def get_modifier(self, event_type):
        setting = self.options.handler.options_dict['dates']
        if event_type == "birth":
            if setting == 0:
                return gen.lib.Date.MOD_ABOUT
            else:
                return gen.lib.Date.MOD_AFTER
        else:
            if setting == 0:
                return gen.lib.Date.MOD_ABOUT
            else:
                return gen.lib.Date.MOD_BEFORE

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

    def create_event(self, description=_("Estimated date"), 
                     type=None, date=None, source=None, 
                     note_text="", modifier=None):
        event = gen.lib.Event()
        event.set_description(description)
        note = gen.lib.Note()
        note.handle = create_id()
        note.type.set(gen.lib.NoteType.EVENT)
        note.set(note_text)
        self.db.add_note(note, self.trans)
        event.add_note(note.handle)
        if type:
            event.set_type(gen.lib.EventType(type))
        if date:
            if modifier:
                date.set_modifier(modifier)
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

    def calc_estimates(self, person):
        return probably_alive_range(person, self.db,
                         self.MAX_SIB_AGE_DIFF, 
                         self.MAX_AGE_PROB_ALIVE, 
                         self.AVG_GENERATION_GAP)

