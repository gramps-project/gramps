#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Analysis and Exploration/Compare individual events"

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
import os
import re
import sort
import utils
import string
import intl

_ = intl.gettext

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
import ListColors
import Filter
import const
from TextDoc import *
from OpenSpreadSheet import *


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

OBJECT   = "o"
INDEX    = "i"
FILTER   = "filter"
FUNCTION = "function"
QUALIFIER= "qual"
NAME     = "name"

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TableReport:

    def __init__(self,filename,doc):
        self.filename = filename
        self.doc = doc
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def initialize(self,cols):

        t = TableStyle()
        t.set_columns(cols)
        for index in range(0,cols):
            t.set_column_width(index,4)
        self.doc.add_table_style("mytbl",t)

        f = FontStyle()
        f.set_type_face(FONT_SANS_SERIF)
        f.set_size(12)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_font(f)
        p.set_background_color((0xcc,0xff,0xff))
        p.set_padding(0.1)
        self.doc.add_style("head",p)

        f = FontStyle()
        f.set_type_face(FONT_SANS_SERIF)
        f.set_size(10)
        p = ParagraphStyle()
        p.set_font(f)
        self.doc.add_style("data",p)

        self.doc.open(self.filename)
        self.doc.start_page("Page 1","mytbl")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def finalize(self):
        self.doc.end_page()
        self.doc.close()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_table_data(self,data):
        length = len(data)

        self.doc.start_row()
        for item in data:
            self.doc.start_cell("data")
            self.doc.write_text(item)
            self.doc.end_cell()
        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def set_row(self,val):
        self.row = val + 2
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_table_head(self,data):
        length = len(data)
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
class EventComparison:

    #------------------------------------------------------------------------
    #
    # 
    #
    #------------------------------------------------------------------------
    def __init__(self,database):
        self.db = database

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "eventcmp.glade"

        self.filterDialog = GladeXML(self.glade_file,"filters")
        self.filterDialog.signal_autoconnect({
            "on_add_clicked": on_add_clicked,
            "on_delete_clicked":on_delete_clicked,
            "on_select_row" : on_select_row,
            "on_filter_save_clicked" : on_filter_save_clicked,
            "on_apply_clicked":on_apply_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })
    
        top =self.filterDialog.get_widget("filters")
        self.filter_menu = self.filterDialog.get_widget("filter_list")
        self.filter_list_obj = self.filterDialog.get_widget("active_filters")
        qualifier = self.filterDialog.get_widget("qualifier")

        self.filter_list_obj.set_data(INDEX,-1)
        self.filter_list_obj.set_data(OBJECT,self)

        self.filter_list = []

        myMenu  = Filter.build_filter_menu(on_filter_name_changed,qualifier)
        self.filter_menu.set_menu(myMenu)

        top.set_data(OBJECT,self)
        top.show()

    #------------------------------------------------------------------------
    #
    # 
    #
    #------------------------------------------------------------------------
    def display_results(self):
        my_list = []

        for person in self.db.getPersonMap().values():
            match = 1
            for filter in self.filter_list:
                if not filter.compare(person):
                    match = 0
            if match == 1:
                my_list.append(person)

        if len(my_list) == 0:
            GnomeWarningDialog("No matches were found")
            return

        self.topDialog = GladeXML(self.glade_file,"top")
        self.topDialog.signal_autoconnect({
            "on_write_table" : on_write_table,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        top = self.topDialog.get_widget("top")
        top.set_data(OBJECT,self)
        table = self.topDialog.get_widget("addarea")
    
        my_list.sort(sort.by_last_name)

        map = {}
        for individual in my_list:
            elist = individual.getEventList()
            for event in elist:
                name = event.getName()
                if not name:
                    break
                if map.has_key(name):
                    map[name] = map[name] + 1
                else:
                    map[name] = 1

        unsort_list = []
        for item in map.keys():
            unsort_list.append((map[item],item))
        unsort_list.sort(by_value)

        sort_list = []
        for item in unsort_list:
            sort_list.append(item[1])

        event_titles = ["Person","Birth","Death"] + sort_list

        eventlist = GtkCList(len(event_titles),event_titles)
        eventlist.set_data(INDEX,-1)
    
        table.add(eventlist)
        eventlist.show()
    
        color_clist = ListColors.ColorList(eventlist,2)
    
        for individual in my_list:
            name = individual.getPrimaryName().getName()
            birth = individual.getBirth()
            death = individual.getDeath()
            map = {}
            elist = individual.getEventList()[:]
            for ievent in elist:
                event_name = ievent.getName()
                if map.has_key(event_name):
                    map[event_name].append(ievent)
                else:
                    map[event_name] = [ievent]

            first = 1
            done = 0
            while done == 0:
                added = 0
                if first:
                    tlist = [name,birth.getDate(),death.getDate()]
                    blist = ["",birth.getPlaceName(),death.getPlaceName()]
                else:
                    tlist = ["","",""]
                    blist = ["","",""]
                for ename in event_titles[3:]:
                    if map.has_key(ename) and len(map[ename]) > 0:
                        mylist = map[ename]
                        event = mylist[0]
                        del mylist[0]
                        tlist.append(event.getDate())
                        blist.append(event.getPlaceName())
                        added = 1
                    else:
                        tlist.append("")
                        blist.append("")
                
                if first:
                    first = 0
                    color_clist.add(tlist)
                    color_clist.add(blist)
                elif added == 0:
                    done = 1
                else:
                    color_clist.add(tlist)
                    color_clist.add(blist)

        for index in range(0,len(event_titles)):
            eventlist.set_column_width(index,eventlist.optimal_column_width(index))
        top.show()

    #------------------------------------------------------------------------
    #
    # 
    #
    #------------------------------------------------------------------------
    def save_data(self):
        
        my_list = []
        for person in self.db.getPersonMap().values():
            match = 1
            for filter in self.filter_list:
                if not filter.compare(person):
                    match = 0
            if match == 1:
                my_list.append(person)

        my_list.sort(sort.by_last_name)

        map = {}
        for individual in my_list:
            elist = individual.getEventList()[:]
            for event in elist:
                name = event.getName()
                if not name:
                    break
                if map.has_key(name):
                    map[name] = map[name] + 1
                else:
                    map[name] = 1

        unsort_list = []
        for item in map.keys():
            unsort_list.append((map[item],item))
        unsort_list.sort(by_value)

        sort_list = []
        for item in unsort_list:
            sort_list.append(item[1])

        event_titles = ["Person","Birth","Death"] + sort_list

        name = self.form.get_widget("filename").get_text()

        doc = OpenSpreadSheet(PaperStyle("junk",10,10),PAPER_PORTRAIT)
        spreadsheet = TableReport(name,doc)
        spreadsheet.initialize(len(event_titles))


        spreadsheet.write_table_head(event_titles)
    
        index = 0
        for individual in my_list:
            spreadsheet.set_row(index%2)
            index = index + 1
            name = individual.getPrimaryName().getName()
            birth = individual.getBirth()
            death = individual.getDeath()
            map = {}
            elist = individual.getEventList()[:]
            for ievent in elist:
                event_name = ievent.getName()
                if map.has_key(event_name):
                    map[event_name].append(ievent)
                else:
                    map[event_name] = [ievent]

            first = 1
            done = 0
            while done == 0:
                added = 0
                if first:
                    tlist = [name,birth.getDate(),death.getDate()]
                    blist = ["",birth.getPlaceName(),death.getPlaceName()]
                else:
                    tlist = ["","",""]
                    blist = ["","",""]
                for ename in event_titles[3:]:
                    if map.has_key(ename) and len(map[ename]) > 0:
                        mylist = map[ename]
                        event = mylist[0]
                        del mylist[0]
                        tlist.append(event.getDate())
                        blist.append(event.getPlaceName())
                        added = 1
                    else:
                        tlist.append("")
                        blist.append("")
                
                if first:
                    first = 0
                    spreadsheet.write_table_data(tlist)
                    spreadsheet.write_table_data(blist)
                elif added == 0:
                    done = 1
                else:
                    spreadsheet.write_table_data(tlist)
                    spreadsheet.write_table_data(blist)

        spreadsheet.finalize()

    #------------------------------------------------------------------------
    #
    # 
    #
    #------------------------------------------------------------------------
    def display_save_form(self):
        self.form = GladeXML(self.glade_file,"dialog1")
        self.form.signal_autoconnect({
            "on_save_clicked": on_save_clicked,
            "on_html_toggled": on_html_toggled,
            "destroy_passed_object" : utils.destroy_passed_object
            })
        self.save_form = self.form.get_widget("dialog1")
        self.save_form.set_data(OBJECT,self)
        self.save_form.show()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def runTool(database,person,callback):
    EventComparison(database)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    myobj = obj.get_data(OBJECT)
    myobj.display_results()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_write_table(obj):
    myobj = obj.get_data(OBJECT)
    myobj.display_save_form()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_clicked(obj):
    myobj = obj.get_data(OBJECT)
    myobj.save_data()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_html_toggled(obj):
    myobj = obj.get_data(OBJECT)
    if myobj.form.get_widget("html").get_active():
        myobj.form.get_widget("htmltemplate").set_sensitive(1)
    else:
        myobj.form.get_widget("htmltemplate").set_sensitive(0)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_double_click(obj,event):
    import EditPerson

    row = obj.get_data(INDEX)
    if event.button == 1 and event.type == GDK._2BUTTON_PRESS and row != -1:
        EditPerson.EditPerson(obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_clicked(obj):
    myobj = obj.get_data(OBJECT)
    row = myobj.filter_list_obj.get_data(INDEX)

    if row == -1:
        return
    myobj.filter_list_obj.remove(row)
    myobj.filter_list_obj.set_data(INDEX,row-1)
    myobj.filter_list_obj.unselect_all()
    del myobj.filter_list[row]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_clicked(obj):

    myobj = obj.get_data(OBJECT)

    invert = myobj.filterDialog.get_widget("invert").get_active()
    qualifier = myobj.filterDialog.get_widget("qualifier").get_text()
    menu = myobj.filter_menu.get_menu()

    function = menu.get_active().get_data(FUNCTION)
    name = menu.get_active().get_data(NAME)

    myfilter = function(qualifier)
    myfilter.set_invert(invert)
    
    myobj.filter_list.append(myfilter)

    row = myobj.filter_list_obj.get_data(INDEX)

    myobj.filter_list_obj.set_data(INDEX,row+1)
    if invert:
        invert_text = "yes"
    else:
        invert_text = "no"

    myobj.filter_list_obj.append([name,qualifier,invert_text])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_filter_name_changed(obj):
    obj.get_data(FILTER).set_sensitive(obj.get_data(QUALIFIER))

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
def on_filter_save_clicked(obj):
    myobj = obj.get_data(OBJECT)

    for filter in myobj.filter_list:
        print "%s(\"%s\"),%d" % (filter,filter.text,filter.invert)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def fix(line):
    l = string.strip(line)
    l = string.replace(l,'&','&amp;')
    l = string.replace(l,'>','&gt;')
    l = string.replace(l,'<','&lt;')
    return string.replace(l,'"','&quot;')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Compare individual events"),
    category=_("Analysis and Exploration"),
    description=_("Aids in the analysis of data by allowing the development of custom filters that can be applied to the database to find similar events")
    )

