#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import PeopleModel

#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectPerson:

    def __init__(self,db,title,flabel="",filter=None,parent_window=None):

        self.renderer = gtk.CellRendererText()
        self.db = db
        self.filter = filter
        gladefile = "%s/choose.glade" % const.rootDir
        self.glade = gtk.glade.XML(gladefile,"select","gramps")
        self.top = self.glade.get_widget('select')
        title_label = self.glade.get_widget('title')
        self.filter_select = self.glade.get_widget('filter')
        self.plist =  self.glade.get_widget('plist')
        self.notebook =  self.glade.get_widget('notebook')
        if filter:
            self.use_filter = 1
        else:
            self.use_filter = 0

        Utils.set_titles(self.top,title_label,title)

        self.model = PeopleModel.PeopleModel(self.db)

        if filter:
            self.filter_select.set_label(flabel)
            self.filter_select.connect('toggled',self.redraw_cb)
            self.filter_select.show()
            self.filter_select.set_active(1)
        else:
            self.filter_select.hide()

        self.add_columns(self.plist)
        self.redraw()
        self.plist.set_model(self.model)
        self.top.show()

        if parent_window:
            self.top.set_transient_for(parent_window)

    def redraw_cb(self,obj):
        self.use_filter = self.filter_select.get_active()
        self.redraw()

    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        column.set_sort_column_id(0)
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        column.set_sort_column_id(1)
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        #column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        tree.append_column(column)
        
    def redraw(self):

        return
    
        for key in self.db.sort_person_keys():
            person = self.db.get_person(key)
            if self.use_filter and not self.filter(person):
                continue
                
            data = self.db.get_person_display(key)
            gender = person.get_gender()
            if gender == RelLib.Person.plist:
                self.mmodel.add([data[0],data[1],data[3],data[5],data[6]],key)
            elif gender == RelLib.Person.feplist:
                self.fmodel.add([data[0],data[1],data[3],data[5],data[6]],key)
            else:
                self.umodel.add([data[0],data[1],data[3],data[5],data[6]],key)

    def select_function(self,store,path,iter,id_list):
        id_list.append(self.model.get_value(iter,1))

    def get_selected_ids(self):
        mlist = []
        self.plist.get_selection().selected_foreach(self.select_function,mlist)
        return mlist

    def run(self):
        val = self.top.run()
        if val == gtk.RESPONSE_OK:

            idlist = self.get_selected_ids()
            if idlist and idlist[0]:
                return_value = self.db.get_person(idlist[0])
            else:
                return_value = None
            self.top.destroy()
	    return return_value
        else:
            self.top.destroy()
            return None
