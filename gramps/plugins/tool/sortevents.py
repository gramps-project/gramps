#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Jakim Friant
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

"""Tools/Database Processing/Sort Events"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.sort import Sort
from gramps.gen.db import DbTxn
from gramps.gui.plug import MenuToolOptions, PluginWindows
from gramps.gen.plug.report import utils
from gramps.gen.plug.menu import FilterOption, PersonOption, \
                          EnumeratedListOption, BooleanOption

#------------------------------------------------------------------------
#
# Private Functions
#
#------------------------------------------------------------------------
def _get_sort_functions(sort):
    """
    Define the types of sorting that is available
    """
    return [
        (_("Date"), sort.by_date_key),
        (_("Type"), sort.by_event_type_key),
        (_("ID"), sort.by_event_id_key),
        (_("Description"), sort.by_event_description_key),
        (_("Place"), sort.by_event_place_key),]

#-------------------------------------------------------------------------
#
# SortEvents
#
#-------------------------------------------------------------------------
class SortEvents(PluginWindows.ToolManagedWindowBatch):
    """
    This tool can be used to sort personal and family events by a variety
    of event attributes. It is primarily intended for re-organising data
    imported from an external source where the events are randomly ordered.
    """

    def get_title(self):
        """
        Return the window title.
        """
        return _("Sort Events")

    def initial_frame(self):
        """
        The name of the initial menu tab.
        """
        self.setup_configs('interface.sortevents', 500, 350)
        return _("Options")

    def run(self):
        """
        Perform the actual extraction of information.
        """
        menu = self.options.menu
        self.filter = menu.get_option_by_name('filter').get_filter()
        sort_func_num = menu.get_option_by_name('sort_by').get_value()
        self.sort_desc = menu.get_option_by_name('sort_desc').get_value()
        self.fam_events = menu.get_option_by_name('family_events').get_value()
        sort_functions = _get_sort_functions(Sort(self.db))
        self.sort_name = sort_functions[sort_func_num][0]
        self.sort_func = sort_functions[sort_func_num][1]
        self.sort = Sort(self.db)
        with DbTxn(_("Sort event changes"), self.db, batch=True) as trans:
            self.db.disable_signals()
            family_handles = self.sort_person_events(trans)
            if len(family_handles) > 0:
                self.sort_family_events(family_handles, trans)
        self.db.enable_signals()
        self.db.request_rebuild()

    def sort_person_events(self, trans):
        """
        Sort the personal events associated with the selected people.
        """
        people_handles = self.filter.apply(self.db,
                                 self.db.iter_person_handles(),
                                 user=self._user)
        self.progress.set_pass(_("Sorting personal events..."),
                                    self.db.get_number_of_people())
        family_handles = []
        for handle in people_handles:
            person = self.db.get_person_from_handle(handle)
            self.progress.step()
            event_ref_list = person.get_event_ref_list()
            event_ref_list.sort(key=lambda x: self.sort_func(x.ref))
            if self.sort_desc:
                event_ref_list.reverse()
            if self.fam_events:
                family_handles.extend(person.get_family_handle_list())
            person.set_event_ref_list(event_ref_list)
            self.db.set_birth_death_index(person)
            self.db.commit_person(person, trans)
            self.change = True
        return family_handles

    def sort_family_events(self, family_handles, trans):
        """
        Sort the family events associated with the selected people.
        """
        self.progress.set_pass(_("Sorting family events..."),
                                 len(family_handles))
        for handle in family_handles:
            family = self.db.get_family_from_handle(handle)
            self.progress.step()
            event_ref_list = family.get_event_ref_list()
            event_ref_list.sort(key=lambda x: self.sort_func(x.ref))
            if self.sort_desc:
                event_ref_list.reverse()
            family.set_event_ref_list(event_ref_list)
            self.db.commit_family(family, trans)
            self.change = True

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class SortEventOptions(MenuToolOptions):
    """
    Define options and provides handling interface.
    """

    def __init__(self, name, person_id=None, dbstate=None):
        self.__db = dbstate.get_database()
        MenuToolOptions.__init__(self, name, person_id, dbstate)

    def add_menu_options(self, menu):
        """
        Define the options for the menu.
        """
        category_name = _("Tool Options")

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(_("Select the people to sort"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self.__update_filters()

        sort_by = EnumeratedListOption(_('Sort by'), 0 )
        idx = 0
        for item in _get_sort_functions(Sort(self.__db)):
            sort_by.add_item(idx, item[0])
            idx += 1
        sort_by.set_help( _("Sorting method to use"))
        menu.add_option(category_name, "sort_by", sort_by)

        sort_desc = BooleanOption(_("Sort descending"), False)
        sort_desc.set_help(_("Set the sort order"))
        menu.add_option(category_name, "sort_desc", sort_desc)

        family_events = BooleanOption(_("Include family events"), True)
        family_events.set_help(_("Sort family events of the person"))
        menu.add_option(category_name, "family_events", family_events)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 0: # "Entire Database" (as "include_single=False")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = utils.get_person_filters(person, include_single=False)
        self.__filter.set_filters(filter_list)
