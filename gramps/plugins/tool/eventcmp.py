#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""Tools/Analysis and Exploration/Compare Individual Events"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from collections import defaultdict

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.filters import GenericFilter, rules
from gramps.gui.filters import build_filter_model
from gramps.gen.sort import Sort
from gramps.gui.utils import ProgressMeter
from gramps.gen.utils.docgen import ODSTab
from gramps.gen.const import CUSTOM_FILTERS, URL_MANUAL_PAGE
from gramps.gen.errors import WindowActiveError
from gramps.gen.datehandler import get_date
from gramps.gui.dialog import WarningDialog
from gramps.gui.plug import tool
from gramps.gen.plug.report import utils
from gramps.gui.display import display_help
from gramps.gui.managedwindow import ManagedWindow
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gui.glade import Glade
from gramps.gui.editors import FilterEditor
from gramps.gen.constfunc import get_curr_dir

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Compare_Individual_Events', 'manual')

#------------------------------------------------------------------------
#
# EventCmp
#
#------------------------------------------------------------------------
class TableReport:
    """
    This class provides an interface for the spreadsheet table
    used to save the data into the file.
    """

    def __init__(self,filename,doc):
        self.filename = filename
        self.doc = doc

    def initialize(self,cols):
        self.doc.open(self.filename)
        self.doc.start_page()

    def finalize(self):
        self.doc.end_page()
        self.doc.close()

    def write_table_data(self,data,skip_columns=[]):
        self.doc.start_row()
        index = -1
        for item in data:
            index += 1
            if index not in skip_columns:
                self.doc.write_cell(item)
        self.doc.end_row()

    def set_row(self,val):
        self.row = val + 2

    def write_table_head(self, data):
        self.doc.start_row()
        list(map(self.doc.write_cell, data))
        self.doc.end_row()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class EventComparison(tool.Tool,ManagedWindow):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.dbstate = dbstate
        self.uistate = uistate

        tool.Tool.__init__(self,dbstate, options_class, name)
        ManagedWindow.__init__(self, uistate, [], self)
        self.qual = 0

        self.filterDialog = Glade(toplevel="filters", also_load=["liststore1"])
        self.filterDialog.connect_signals({
            "on_apply_clicked"       : self.on_apply_clicked,
            "on_editor_clicked"      : self.filter_editor_clicked,
            "on_help_clicked"        : self.on_help_clicked,
            "destroy_passed_object"  : self.close,
            "on_write_table"         : self.__dummy,
            })

        window = self.filterDialog.toplevel
        self.filters = self.filterDialog.get_object("filter_list")
        self.label = _('Event comparison filter selection')
        self.set_window(window,self.filterDialog.get_object('title'),
                        self.label)
        self.setup_configs('interface.eventcomparison', 640, 220)

        self.on_filters_changed('Person')
        uistate.connect('filters-changed', self.on_filters_changed)

        self.show()

    def __dummy(self, obj):
        """dummy callback, needed because widget is in same glade file
        as another widget, so callbacks must be defined to avoid warnings.
        """
        pass

    def on_filters_changed(self, name_space):
        if name_space == 'Person':
            all_filter = GenericFilter()
            all_filter.set_name(_("Entire Database"))
            all_filter.add_rule(rules.person.Everyone([]))
            self.filter_model = build_filter_model('Person', [all_filter])
            self.filters.set_model(self.filter_model)
            self.filters.set_active(0)

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_menu_names(self, obj):
        return (_("Filter selection"),_("Event Comparison tool"))

    def filter_editor_clicked(self, obj):
        try:
            FilterEditor('Person',CUSTOM_FILTERS,
                                      self.dbstate,self.uistate)
        except WindowActiveError:
            pass

    def on_apply_clicked(self, obj):
        cfilter = self.filter_model[self.filters.get_active()][1]

        progress_bar = ProgressMeter(_('Comparing events'), '',
                                     parent=self.window)
        progress_bar.set_pass(_('Selecting people'),1)

        plist = cfilter.apply(self.db,
                              self.db.iter_person_handles())

        progress_bar.step()
        progress_bar.close()
        self.options.handler.options_dict['filter'] = self.filters.get_active()
        # Save options
        self.options.handler.save_options()

        if len(plist) == 0:
            WarningDialog(_("No matches were found"),
                          parent=self.window)
        else:
            EventComparisonResults(self.dbstate, self.uistate, plist, self.track)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
##def by_value(first,second):
##    return cmp(second[0],first[0])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fix(line):
    l = line.strip().replace('&','&amp;').replace('>','&gt;')
    return l.replace(l,'<','&lt;').replace(l,'"','&quot;')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class EventComparisonResults(ManagedWindow):
    def __init__(self,dbstate,uistate,people_list,track):
        self.dbstate = dbstate
        self.uistate = uistate

        ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.my_list = people_list
        self.row_data = []
        self.save_form = None

        self.topDialog = Glade(toplevel="eventcmp")
        self.topDialog.connect_signals({
            "on_write_table"        : self.on_write_table,
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_apply_clicked"      : self.__dummy,
            "on_editor_clicked"     : self.__dummy,
            })

        window = self.topDialog.toplevel
        self.set_window(window, self.topDialog.get_object('title'),
                        _('Event Comparison Results'))
        self.setup_configs('interface.eventcomparisonresults', 750, 400)

        self.eventlist = self.topDialog.get_object('treeview')
        self.sort = Sort(self.db)
        self.my_list.sort(key=self.sort.by_last_name_key)

        self.event_titles = self.make_event_titles()

        self.table_titles = [_("Person"),_("ID")]
        for event_name in self.event_titles:
            self.table_titles.append(_("%(event_name)s Date") %
                {'event_name' :event_name}
                )
            self.table_titles.append('sort') # This won't be shown in a tree
            self.table_titles.append(_("%(event_name)s Place") %
                {'event_name' :event_name}
                )

        self.build_row_data()
        self.draw_display()
        self.show()

    def __dummy(self, obj):
        """dummy callback, needed because widget is in same glade file
        as another widget, so callbacks must be defined to avoid warnings.
        """
        pass

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_menu_names(self, obj):
        return (_("Event Comparison Results"),None)

    def draw_display(self):

        model_index = 0
        tree_index = 0
        mylist = []
        renderer = Gtk.CellRendererText()
        for title in self.table_titles:
            mylist.append(str)
            if title == 'sort':
                # This will override the previously defined column
                self.eventlist.get_column(
                    tree_index-1).set_sort_column_id(model_index)
            else:
                column = Gtk.TreeViewColumn(title,renderer,text=model_index)
                column.set_sort_column_id(model_index)
                self.eventlist.append_column(column)
                # This one numbers the tree columns: increment on new column
                tree_index += 1
            # This one numbers the model columns: always increment
            model_index += 1

        model = Gtk.ListStore(*mylist)
        self.eventlist.set_model(model)

        self.progress_bar.set_pass(_('Building display'),len(self.row_data))
        for data in self.row_data:
            model.append(row=list(data))
            self.progress_bar.step()
        self.progress_bar.close()

    def build_row_data(self):
        self.progress_bar = ProgressMeter(
            _('Comparing Events'), '', parent=self.uistate.window)
        self.progress_bar.set_pass(_('Building data'),len(self.my_list))
        for individual_id in self.my_list:
            individual = self.db.get_person_from_handle(individual_id)
            name = individual.get_primary_name().get_name()
            gid = individual.get_gramps_id()

            the_map = defaultdict(list)
            for ievent_ref in individual.get_event_ref_list():
                ievent = self.db.get_event_from_handle(ievent_ref.ref)
                event_name = str(ievent.get_type())
                the_map[event_name].append(ievent_ref.ref)

            first = True
            done = False
            while not done:
                added = False
                tlist = [name, gid] if first else ["", ""]

                for ename in self.event_titles:
                    if ename in the_map and len(the_map[ename]) > 0:
                        event_handle = the_map[ename][0]
                        del the_map[ename][0]
                        date = place = ""

                        if event_handle:
                            event = self.db.get_event_from_handle(event_handle)
                            date = get_date(event)
                            sortdate = "%09d" % (
                                       event.get_date_object().get_sort_value()
                                       )
                            place_handle = event.get_place_handle()
                            if place_handle:
                                place = self.db.get_place_from_handle(
                                            place_handle).get_title()
                        tlist += [date, sortdate, place]
                        added = True
                    else:
                        tlist += [""]*3

                if first:
                    first = False
                    self.row_data.append(tlist)
                elif not added:
                    done = True
                else:
                    self.row_data.append(tlist)
            self.progress_bar.step()

    def make_event_titles(self):
        """
        Create the list of unique event types, along with the person's
        name, birth, and death.
        This should be the column titles of the report.
        """
        the_map = defaultdict(int)
        for individual_id in self.my_list:
            individual = self.db.get_person_from_handle(individual_id)
            for event_ref in individual.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                name = str(event.get_type())
                if not name:
                    break
                the_map[name] += 1

        unsort_list = sorted([(d, k) for k,d in the_map.items()],
                             key=lambda x: x[0], reverse=True)

        sort_list = [ item[1] for item in unsort_list ]
## Presently there's no Birth and Death. Instead there's Birth Date and
## Birth Place, as well as Death Date and Death Place.
##         # Move birth and death to the begining of the list
##         if _("Death") in the_map:
##             sort_list.remove(_("Death"))
##             sort_list = [_("Death")] + sort_list

##         if _("Birth") in the_map:
##             sort_list.remove(_("Birth"))
##             sort_list = [_("Birth")] + sort_list

        return sort_list

    def on_write_table(self, obj):
        f = Gtk.FileChooserDialog(_("Select filename"),
                                  transient_for=self.window,
                                  action=Gtk.FileChooserAction.SAVE)
        f.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                      _('_Save'), Gtk.ResponseType.OK)

        f.set_current_folder(get_curr_dir())
        status = f.run()
        f.hide()

        if status == Gtk.ResponseType.OK:
            name = f.get_filename()
            doc = ODSTab(len(self.row_data))
            doc.creator(self.db.get_researcher().get_name())

            spreadsheet = TableReport(name, doc)

            new_titles = []
            skip_columns = []
            index = 0
            for title in self.table_titles:
                if title == 'sort':
                    skip_columns.append(index)
                else:
                    new_titles.append(title)
                index += 1
            spreadsheet.initialize(len(new_titles))

            spreadsheet.write_table_head(new_titles)

            index = 0
            for top in self.row_data:
                spreadsheet.set_row(index%2)
                index += 1
                spreadsheet.write_table_data(top,skip_columns)

            spreadsheet.finalize()
        f.destroy()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class EventComparisonOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'filter'   : 0,
        }
        filters = utils.get_person_filters(None)
        self.options_help = {
            'filter'   : ("=num","Filter number.",
                          [ filt.get_name() for filt in filters ],
                          True ),
        }
