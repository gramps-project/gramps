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

"""interface for opening a find person dialog for gramps
"""

__author__ = 'Don Allingham'

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import string

#-------------------------------------------------------------------------
#
# Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# FindBase
#
#-------------------------------------------------------------------------
class FindBase:
    """Opens find person dialog for gramps"""
    
    def __init__(self,task,name,db,valid_map=None):
        """Opens a dialog box instance that allows users to
        search for a person.
        task - function to call to change the active person"""

        self.t = type(u' ')
        self.db = db
        self.task = task
        self.glade = gtk.glade.XML(const.gladeFile,"find","gramps")
        self.glade.signal_autoconnect({
            'on_next_clicked' : self.on_next_clicked,
            'on_back_clicked' : self.on_prev_clicked,
            'on_close_clicked' : self.on_close_clicked,
            })
        self.top = self.glade.get_widget('find')
        self.top.connect('delete_event',self.on_destroy)

        self.entry = self.glade.get_widget('entry')
        self.forward_button = self.glade.get_widget('forward')
        self.back_button = self.glade.get_widget('back')
        Utils.set_titles(self.top, self.glade.get_widget('title'), name)
        self.list = None
        self.index = 0
        self.visible = 1
        self.valid = valid_map

    def get_value(self,id):
        return id
        
    def advance(self,func):
        text = unicode(self.entry.get_text().upper())
        orow = self.index
        func()
        while self.index != orow:
            vals = self.list[self.index]
            id = vals[1]
            name = vals[0]
            if id == None:
                func()
                continue
            if self.valid and not self.valid.has_key(id):
                func()
                continue
            if string.find(name.upper(),text) >= 0:
                self.back_button.set_sensitive(0)
                self.forward_button.set_sensitive(0)
                self.task(self.get_value(id))
                self.back_button.set_sensitive(1)
                self.forward_button.set_sensitive(1)
                return
            func()

    def forward(self):
        self.index = self.index + 1
        if self.index == len(self.list):
            self.index = 0

    def backward(self):
        self.index = self.index - 1
        if self.index < 0:
            self.index = len(self.list)-1

    def on_close_clicked(self,obj):
        """Destroys the window in response to a close window button press"""
        self.visible = 0
        self.top.hide()

    def on_destroy(self,obj,event):
        self.on_close_clicked(obj)
        return 1

    def show(self):
        self.top.window.raise_()
        self.top.show()
        self.entry.grab_focus ()
        
    def on_next_clicked(self,obj):
        """Advances to the next person that matches the dialog text"""
        self.advance(self.forward)

    def on_prev_clicked(self,obj):
        """Advances to the previous person that matches the dialog text"""
        self.advance(self.backward)

#-------------------------------------------------------------------------
#
# FindPerson
#
#-------------------------------------------------------------------------
class FindPerson(FindBase):
    """Opens a Find Person dialog for GRAMPS"""
    
    def __init__(self,task,db,valid_map):
        """Opens a dialog box instance that allows users to
        search for a person.

        task - function to call to change the active person"""
        
        FindBase.__init__(self,task,_("Find Person"),db,valid_map)
        self.list = []
        for val in db.sort_person_keys():
            self.list.append(db.get_person_display(val))

    def get_value(self,id):
        return self.db.get_person(id)
    
#-------------------------------------------------------------------------
#
# FindPlace
#
#-------------------------------------------------------------------------
class FindPlace(FindBase):
    """Opens a Find Place dialog for GRAMPS"""
    
    def __init__(self,task,db):
        """Opens a dialog box instance that allows users to
        search for a place.

        task - function to call to change the active person"""
        
        FindBase.__init__(self,task,_("Find Place"),db)
        self.list = db.placeTable.values()
        self.list.sort()

#-------------------------------------------------------------------------
#
# FindSource
#
#-------------------------------------------------------------------------
class FindSource(FindBase):
    """Opens a Find Place dialog for GRAMPS"""
    
    def __init__(self,task,db):
        """Opens a dialog box instance that allows users to
        search for a place.

        task - function to call to change the active person"""
        
        FindBase.__init__(self,task,_("Find Source"),db)
        self.list = db.sourceTable.values()
        self.list.sort()

#-------------------------------------------------------------------------
#
# FindMedia
#
#-------------------------------------------------------------------------
class FindMedia(FindBase):
    """Opens a Find Media Object dialog for GRAMPS"""
    
    def __init__(self,task,db):
        """Opens a dialog box instance that allows users to
        search for a place.

        task - function to call to change the active person"""
        
        FindBase.__init__(self,task,_("Find Media Object"),db)
        self.list = []
        for n in self.db.get_object_map().values():
            self.list.append((n.get_description(),n.get_handle()))
        self.list.sort()
        
