#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Analysis and Exploration/Compare individual events"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import gtk.glade

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import GenericFilter
import ListModel
import Sort
import Utils
import BaseDoc
import ODSDoc
import const
import DateHandler
from QuestionDialog import WarningDialog
from PluginUtils import Tool, register_tool
from GrampsDisplay import help
import ManagedWindow

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TableReport:

    def __init__(self,filename,doc):
        self.filename = filename
        self.doc = doc
        
    def initialize(self,cols):

        t = BaseDoc.TableStyle()
        t.set_columns(cols)
        for index in range(0,cols):
            t.set_column_width(index,4)
        self.doc.add_table_style("mytbl",t)

        f = BaseDoc.FontStyle()
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_size(12)
        f.set_bold(1)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_background_color((0xcc,0xff,0xff))
        p.set_padding(0.1)
        self.doc.add_style("head",p)

        f = BaseDoc.FontStyle()
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_size(10)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        self.doc.add_style("data",p)

        self.doc.open(self.filename)
        self.doc.start_page("Page 1","mytbl")

    def finalize(self):
        self.doc.end_page()
        self.doc.close()
        
    def write_table_data(self,data):
        self.doc.start_row()
        for item in data:
            self.doc.start_cell("data")
            self.doc.write_text(item)
            self.doc.end_cell()
        self.doc.end_row()

    def set_row(self,val):
        self.row = val + 2
        
    def write_table_head(self,data):
        self.prev = 3

        self.doc.start_row()
        for item in data:
            self.doc.start_cell("head")
            self.doc.write_text(item)
            self.doc.end_cell()
        self.doc.end_row()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EventComparison(Tool.Tool,ManagedWindow.ManagedWindow):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.dbstate = dbstate
        self.uistate = uistate
        
        Tool.Tool.__init__(self,dbstate,options_class,name)
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self)

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "eventcmp.glade"
        self.qual = 0

        self.filterDialog = gtk.glade.XML(self.glade_file,"filters","gramps")
        self.filterDialog.signal_autoconnect({
            "on_apply_clicked"       : self.on_apply_clicked,
            "on_editor_clicked"      : self.filter_editor_clicked,
            "on_filters_delete_event": self.close,
            "on_help_clicked"        : self.on_help_clicked,
            "destroy_passed_object"  : self.close
            })
    
        window = self.filterDialog.get_widget("filters")
        self.filters = self.filterDialog.get_widget("filter_list")
        self.label = _('Event comparison filter selection')
        self.set_window(window,self.filterDialog.get_widget('title'),
                        self.label)

        self.all = GenericFilter.GenericFilter()
        self.all.set_name(_("Entire Database"))
        self.all.add_rule(GenericFilter.Everyone([]))

        self.filter_menu = GenericFilter.build_filter_menu([self.all])
        filter_num = self.options.handler.get_filter_number()
        self.filter_menu.set_active(filter_num)
        self.filter_menu.show()
        self.filters.set_menu(self.filter_menu)

        self.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        help('tools-util')

    def build_menu_names(self,obj):
        return (_("Filter selection"),_("Event Comparison tool"))

    def filter_editor_clicked(self,obj):
        import FilterEditor
        FilterEditor.FilterEditor(const.custom_filters,self.db,self.parent)

    def on_apply_clicked(self,obj):
        cfilter = self.filter_menu.get_active().get_data("filter")

        progress_bar = Utils.ProgressMeter(_('Comparing events'),'')
        progress_bar.set_pass(_('Selecting people'),1)

        plist = cfilter.apply(self.db,
                              self.db.get_person_handles(sort_handles=False))

        progress_bar.step()
        progress_bar.close()
        self.options.handler.set_filter_number(self.filters.get_history())
        # Save options
        self.options.handler.save_options()

        if len(plist) == 0:
            WarningDialog(_("No matches were found"))
        else:
            DisplayChart(self.dbstate,self.uistate,plist,self.track)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_value(first,second):
    return cmp(second[0],first[0])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fix(line):
    l = line.strip().replace('&','&amp;').replace(l,'>','&gt;')
    return l.replace(l,'<','&lt;').replace(l,'"','&quot;')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DisplayChart(ManagedWindow.ManagedWindow):
    def __init__(self,dbstate,uistate,people_list,track):
        self.dbstate = dbstate
        self.uistate = uistate

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.my_list = people_list
        self.row_data = []
        self.save_form = None
        
        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "eventcmp.glade"

        self.topDialog = gtk.glade.XML(self.glade_file,"view","gramps")
        self.topDialog.signal_autoconnect({
            "on_write_table"        : self.on_write_table,
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            })

        window = self.topDialog.get_widget("view")
        self.set_window(window, self.topDialog.get_widget('title'),
                        _('Event Comparison Results'))
                        
        self.eventlist = self.topDialog.get_widget('treeview')
        self.sort = Sort.Sort(self.db)
        self.my_list.sort(self.sort.by_last_name)

        self.event_titles = self.make_event_titles()
        self.build_row_data()
        self.draw_clist_display()
        self.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        help('gramps-manual','tools-ae')

    def build_menu_names(self,obj):
        return (_("Event Comparison Results"),None)

    def draw_clist_display(self):

        titles = []
        index = 0
        for event_name in self.event_titles:
            titles.append((event_name,index,150))
            index = index + 1
            
        self.list = ListModel.ListModel(self.eventlist,titles)

        self.progress_bar.set_pass(_('Building display'),len(self.row_data))
        for data in self.row_data:
            self.list.add(data)
            self.progress_bar.step()
        self.progress_bar.close()

    def build_row_data(self):
        self.progress_bar = Utils.ProgressMeter(_('Comparing events'),'')
        self.progress_bar.set_pass(_('Building data'),
                              self.db.get_number_of_people())
        for individual_id in self.my_list:
            individual = self.db.get_person_from_handle(individual_id)
            name = individual.get_primary_name().get_name()
            birth_ref = individual.get_birth_ref()
            bdate = ""
            bplace = ""
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                bdate = DateHandler.get_date(birth)
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    bplace = self.db.get_place_from_handle(bplace_handle).get_title()
            death_ref = individual.get_death_ref()
            ddate = ""
            dplace = ""
            if death_ref:
                death = self.db.get_event_from_handle(death_ref.ref)
                ddate = DateHandler.get_date(death)
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    dplace = self.db.get_place_from_handle(dplace_handle).get_title()
            map = {}
            for ievent_ref in individual.get_event_ref_list():
                ievent = self.db.get_event_from_handle(ievent_ref.ref)
                event_name = str(ievent.get_type())
                if map.has_key(event_name):
                    map[event_name].append(ievent_ref.ref)
                else:
                    map[event_name] = [ievent_ref.ref]

            first = 1
            done = 0
            while done == 0:
                added = 0
                if first:
                    tlist = [name,"%s\n%s" % (bdate,bplace),
                             "%s\n%s" % (ddate,dplace)]
                else:
                    tlist = ["","",""]
                for ename in self.event_titles[3:]:
                    if map.has_key(ename) and len(map[ename]) > 0:
                        event_handle = map[ename][0]
                        del map[ename][0]
                        date = ""
                        place = ""
                        if event_handle:
                            event = self.db.get_event_from_handle(event_handle)
                            date = DateHandler.get_date(event)
                            place_handle = event.get_place_handle()
                            if place_handle:
                                place = self.db.get_place_from_handle(place_handle).get_title()
                        tlist.append("%s\n%s" % (date, place))
                        added = 1
                    else:
                        tlist.append("")
                
                if first:
                    first = 0
                    self.row_data.append(tlist)
                elif added == 0:
                    done = 1
                else:
                    self.row_data.append(tlist)
            self.progress_bar.step()

    def make_event_titles(self):
        """
        Creates the list of unique event types, along with the person's
        name, birth, and death.
        This should be the column titles of the report.
        """
        map = {}
        for individual_id in self.my_list:
            individual = self.db.get_person_from_handle(individual_id)
            for event_ref in individual.get_event_ref_list():
                event = self.db.get_event_from_handle(event_ref.ref)
                name = str(event.get_type())
                if not name:
                    break
                if map.has_key(name):
                    map[name] = map[name] + 1
                else:
                    map[name] = 1

        unsort_list = [ (map[item],item) for item in map.keys() ]
        unsort_list.sort(by_value)
        sort_list = [ item[1] for item in unsort_list ]

        return [_("Person"),_("Birth"),_("Death")] + sort_list

    def on_write_table(self,obj):
        f = gtk.FileChooserDialog(_("Select filename"),
                                  action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_SAVE,
                                           gtk.RESPONSE_OK))

        f.set_current_folder(os.getcwd())
        status = f.run()
        name = unicode(f.get_filename())
        f.destroy()

        if status == gtk.RESPONSE_OK:
            pstyle = BaseDoc.PaperStyle("junk",10,10)
            doc = ODSDoc.ODSDoc(pstyle,BaseDoc.PAPER_PORTRAIT)
            doc.creator(self.db.get_researcher().get_name())
            spreadsheet = TableReport(name,doc)
            spreadsheet.initialize(len(self.event_titles))

            spreadsheet.write_table_head(self.event_titles)

            index = 0
            for top in self.row_data:
                spreadsheet.set_row(index%2)
                index = index + 1
                spreadsheet.write_table_data(top)

            spreadsheet.finalize()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EventComparisonOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'eventcmp',
    category = Tool.TOOL_ANAL,
    tool_class = EventComparison,
    options_class = EventComparisonOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Compare individual events"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Aids in the analysis of data by allowing the "
                  "development of custom filters that can be applied "
                  "to the database to find similar events")
    )
