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
# Module imports
#
#------------------------------------------------------------------------
import os
import sort
import Utils
import string
import ListColors
import Filter
import const
from TextDoc import *
from OpenSpreadSheet import *
import intl

import gtk
import gnome.ui
import libglade

import xml.parsers.expat

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Unicode to latin conversion
#
#-------------------------------------------------------------------------
from latin_utf8 import utf8_to_latin
u2l = utf8_to_latin

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

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
class EventComparison:

    def __init__(self,database):
        self.db = database

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "eventcmp.glade"
        self.qual = 0

        xml = os.path.expanduser("~/.gramps/eventcmp.xml")
        self.interface = ComplexFilterFile(xml)

        self.filterDialog = libglade.GladeXML(self.glade_file,"filters")
        self.filterDialog.signal_autoconnect({
            "on_add_clicked"         : self.on_add_clicked,
            "on_delete_clicked"      : self.on_delete_clicked,
            "on_filter_save_clicked" : self.on_filter_save_clicked,
            "on_filter_load_clicked" : self.on_filter_load_clicked,
            "on_apply_clicked"       : self.on_apply_clicked,
            "destroy_passed_object"  : Utils.destroy_passed_object
            })
    
        top =self.filterDialog.get_widget("filters")
        self.filter_menu = self.filterDialog.get_widget("filter_list")
        self.filter_list_obj = self.filterDialog.get_widget("active_filters")
        qualifier = self.filterDialog.get_widget("qualifier")

        self.filter_list = []

        myMenu  = Filter.build_filter_menu(self.on_filter_name_changed,qualifier)
        self.filter_menu.set_menu(myMenu)

        top.show()

    def on_apply_clicked(self,obj):
        my_list = []

        for person in self.db.getPersonMap().values():
            for filter in self.filter_list:
                if not filter.compare(person):
                    break
            else:
                my_list.append(person)

        if len(my_list) == 0:
            gnome.ui.GnomeWarningDialog(_("No matches were found"))
        else:
            DisplayChart(my_list)

    def on_delete_clicked(self,obj):
        if len(self.filter_list_obj.selection) != 1:
            return
        
        row = self.filter_list_obj.selection[0]
        self.filter_list_obj.remove(row)
        self.filter_list_obj.unselect_all()
        del self.filter_list[row]

    def on_add_clicked(self,obj):

        invert = self.filterDialog.get_widget("invert").get_active()
        qwidget = self.filterDialog.get_widget("qualifier")

        if self.qual:
            qualifier = qwidget.get_text()
        else:
            qualifier = ""
            
        menu = self.filter_menu.get_menu()

        function = menu.get_active().get_data(FUNCTION)
        name = menu.get_active().get_data(NAME)

        myfilter = function(qualifier)
        myfilter.set_invert(invert)
    
        self.filter_list.append(myfilter)
        if invert:
            invert_text = "yes"
        else:
            invert_text = "no"

        self.filter_list_obj.append([name,qualifier,invert_text])

    def on_filter_save_clicked(self,obj):
        self.load_dialog = libglade.GladeXML(self.glade_file,"filter_file")
        self.filter_combo = self.load_dialog.get_widget("filter_combo")
        self.load_dialog.get_widget("title").set_text("Save complex filter")
        names = self.interface.get_filter_names()
        if len(names) > 0:
            self.filter_combo.set_popdown_strings(names)
        self.load_dialog.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "combo_insert_text"     : Utils.combo_insert_text,
            "on_load_filter"        : self.on_save_filter,
            })

    def on_filter_load_clicked(self,obj):
        self.load_dialog = libglade.GladeXML(self.glade_file,"filter_file")
        self.filter_combo = self.load_dialog.get_widget("filter_combo")
        self.load_dialog.get_widget("title").set_text("Load complex filter")
        names = self.interface.get_filter_names()
        if len(names) > 0:
            self.filter_combo.set_popdown_strings(names)
        self.load_dialog.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "combo_insert_text"     : Utils.combo_insert_text,
            "on_load_filter"        : self.on_load_filter,
            })

    def on_load_filter(self,obj):
        name = self.load_dialog.get_widget("name").get_text()
        self.filter_list = self.interface.get_filter(name)
        self.filter_list_obj.freeze()
        self.filter_list_obj.clear()
        for f in self.filter_list:
            if f.get_invert():
                invert = "yes"
            else:
                invert = "no"
            name = str(f.__class__)
            name = Filter.get_filter_description(name)
            self.filter_list_obj.append([name,f.get_text(),invert])
        self.filter_list_obj.thaw()
        Utils.destroy_passed_object(obj)

    def on_save_filter(self,obj):
        name = self.load_dialog.get_widget("name").get_text()
        self.interface.save_filter(name,self.filter_list)
        Utils.destroy_passed_object(obj)
        
    def on_filter_name_changed(self,obj):
        self.qual = obj.get_data(QUALIFIER)
        obj.get_data(FILTER).set_sensitive(self.qual)


class ComplexFilterFile:
    def __init__(self,name):
        self.filters = {}
        self.fname = name
        try:
            f = open(self.fname)
            parser = ComplexFilterParser(self)
            parser.parse(f)
            f.close()
        except IOError:
            pass

    def get_filter_names(self):
        return self.filters.keys()

    def get_filter(self,name):
        if self.filters.has_key(name):
            return self.filters[name]
        else:
            return []

    def save_filter(self,name,filter_list):
        self.filters[name] = filter_list
        
        f = open(self.fname,"w")
        f.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')
        f.write('<filterlist>\n')
        for name in self.filters.keys():
            f.write('  <complex_filter name="%s">\n' % name)
            for filter in self.filters[name]:
                val = (filter.get_name(),filter.get_text(),filter.get_invert())
                f.write('    <filter name="%s" text="%s" invert="%d"/>\n' % val)
            f.write('  </complex_filter>\n')
        f.write('</filterlist>\n')
        f.close()

class ComplexFilterParser:
    def __init__(self,parent):
        self.parent = parent
        self.curfilter = []
        self.curname = ""

    def parse(self,f):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.ParseFile(f)

    def startElement(self,tag,attrs):
        tag = u2l(tag)
        if tag == "complex_filter":
            self.curname = u2l(attrs['name'])
            self.curfilter = []
        elif tag == "filter":
            name = u2l(attrs['name'])
            qual = u2l(attrs['text'])
            invert = int(attrs['invert'])
            f = Filter.make_filter_from_name(name,qual,invert)
            self.curfilter.append(f)

    def endElement(self,tag):
        if u2l(tag) == "complex_filter":
            self.parent.filters[self.curname] = self.curfilter

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
def by_value(first,second):
    return cmp(second[0],first[0])

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
class DisplayChart:
    def __init__(self,people_list):
        self.my_list = people_list
        self.row_data = []
        
        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "eventcmp.glade"

        self.topDialog = libglade.GladeXML(self.glade_file,"view")
        self.topDialog.signal_autoconnect({
            "on_write_table"        : self.on_write_table,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        self.top = self.topDialog.get_widget("view")
        self.table = self.topDialog.get_widget("addarea")
    
        self.my_list.sort(sort.by_last_name)

        self.event_titles = self.make_event_titles()
        self.build_row_data()
        self.draw_clist_display()
        self.top.show()

    def draw_clist_display(self):

        eventlist = gtk.GtkCList(len(self.event_titles),self.event_titles)
        self.table.add(eventlist)
        eventlist.show()
        color_clist = ListColors.ColorList(eventlist,2)

        for (top,bottom) in self.row_data:
            color_clist.add(top)
            color_clist.add(bottom)

        for index in range(0,len(self.event_titles)):
            width = min(150,eventlist.optimal_column_width(index))
            eventlist.set_column_width(index,width)

    def build_row_data(self):
        for individual in self.my_list:
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
                for ename in self.event_titles[3:]:
                    if map.has_key(ename) and len(map[ename]) > 0:
                        event = map[ename][0]
                        del map[ename][0]
                        tlist.append(event.getDate())
                        blist.append(event.getPlaceName())
                        added = 1
                    else:
                        tlist.append("")
                        blist.append("")
                
                if first:
                    first = 0
                    self.row_data.append((tlist,blist))
                elif added == 0:
                    done = 1
                else:
                    self.row_data.append((tlist,blist))

    def make_event_titles(self):
        """Creates the list of unique event types, along with the person's
        name, birth, and death. This should be the column titles of the report"""
        map = {}
        for individual in self.my_list:
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

        return [_("Person"),_("Birth"),_("Death")] + sort_list

    def on_write_table(self,obj):
        self.form = libglade.GladeXML(self.glade_file,"dialog1")
        self.form.signal_autoconnect({
            "on_save_clicked"       : self.on_save_clicked,
            "on_html_toggled"       : self.on_html_toggled,
            "destroy_passed_object" : Utils.destroy_passed_object
            })
        self.save_form = self.form.get_widget("dialog1")
        self.save_form.show()

    def on_html_toggled(self,obj):
        active = self.form.get_widget("html").get_active()
        self.form.get_widget("htmltemplate").set_sensitive(active)

    def on_save_clicked(self,obj):
        
        name = self.form.get_widget("filename").get_text()

        doc = OpenSpreadSheet(PaperStyle("junk",10,10),PAPER_PORTRAIT)
        spreadsheet = TableReport(name,doc)
        spreadsheet.initialize(len(self.event_titles))

        spreadsheet.write_table_head(self.event_titles)

        index = 0
        for (top,bottom) in self.row_data:
            spreadsheet.set_row(index%2)
            index = index + 1
            spreadsheet.write_table_data(top)
            spreadsheet.write_table_data(bottom)

        spreadsheet.finalize()
        Utils.destroy_passed_object(obj)

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

