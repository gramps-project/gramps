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
import ListModel

#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectPerson:

    def __init__(self,db,title,flabel="",filter=None,parent_window=None):

        self.db = db
        self.filter = filter
        gladefile = "%s/choose.glade" % const.rootDir
        self.glade = gtk.glade.XML(gladefile,"select","gramps")
        self.top = self.glade.get_widget('select')
        title_label = self.glade.get_widget('title')
        self.filter_select = self.glade.get_widget('filter')
        self.female = self.glade.get_widget('female')
        self.male =  self.glade.get_widget('male')
        self.unknown =  self.glade.get_widget('unknown')
        self.notebook =  self.glade.get_widget('notebook')
        if filter:
            self.use_filter = 1
        else:
            self.use_filter = 0

        Utils.set_titles(self.top,title_label,title)

        titles = [(_('Name'),3,150),(_('ID'),1,50), (_('Birth date'),4,100),
                  ('',0,0),('',0,0)]

        self.fmodel = ListModel.ListModel(self.female,titles)
        self.mmodel = ListModel.ListModel(self.male,titles)
        self.umodel = ListModel.ListModel(self.unknown,titles)

        if filter:
            self.filter_select.set_label(flabel)
            self.filter_select.connect('toggled',self.redraw_cb)
            self.filter_select.show()
            self.filter_select.set_active(1)
        else:
            self.filter_select.hide()

        self.redraw()
        self.top.show()

        if parent_window:
            self.top.set_transient_for(parent_window)

    def redraw_cb(self,obj):
        self.use_filter = self.filter_select.get_active()
        self.redraw()
        
    def redraw(self):
        
        self.fmodel.clear()
        self.fmodel.new_model()

        self.mmodel.clear()
        self.mmodel.new_model()

        self.umodel.clear()
        self.umodel.new_model()

        for key in self.db.sortPersonKeys():
            person = self.db.getPerson(key)
            if self.use_filter and not self.filter(person):
                continue
                
            data = self.db.getPersonDisplay(key)
            gender = person.getGender()
            if gender == RelLib.Person.male:
                self.mmodel.add([data[0],data[1],data[3],data[5],data[6]],key)
            elif gender == RelLib.Person.female:
                self.fmodel.add([data[0],data[1],data[3],data[5],data[6]],key)
            else:
                self.umodel.add([data[0],data[1],data[3],data[5],data[6]],key)

        self.fmodel.connect_model()
        self.mmodel.connect_model()
        self.umodel.connect_model()
        
    def run(self):
        val = self.top.run()
        page = self.notebook.get_current_page()

        if val == gtk.RESPONSE_OK:
	    if page == 0:
                lmodel = self.fmodel
            elif page == 1:
                lmodel = self.mmodel
            else:
                lmodel = self.umodel

            model,iter = lmodel.get_selected()
            if iter:
                id = lmodel.get_object(iter)
                return_value = self.db.getPerson(id)
            else:
                return_value = None
            self.top.destroy()
	    return return_value
        else:
            self.top.destroy()
            return None
