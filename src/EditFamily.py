#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
import gc
from gettext import gettext as _
import sys

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ImageSelect
import NameDisplay
import DisplayState
import Spell
import GrampsDisplay
import RelLib
import ListModel
import ReportUtils

from DdTargets import DdTargets
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditFamily(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,family):
        self.dbstate = dbstate
        self.uistate = uistate
        self.family  = family

        DisplayState.ManagedWindow.__init__(self, uistate, track, family)
        if self.already_exist:
            return
        
        self.build_interface()
        if self.family:
            self.load_data()

        self.show()

    def build_menu_names(self,obj):
        return ('Edit Family','Undefined Submenu')

    def build_window_key(self,obj):
        return id(self.family.handle)

    def build_interface(self):
        self.top = gtk.glade.XML(const.placesFile,"marriageEditor","gramps")
        self.gladeif = GladeIf(self.top)
        self.window = self.top.get_widget("marriageEditor")

        self.fname  = self.top.get_widget('fname')
        self.fbirth = self.top.get_widget('fbirth')
        self.fdeath = self.top.get_widget('fdeath')
        
        self.mname  = self.top.get_widget('mname')
        self.mbirth = self.top.get_widget('mbirth')
        self.mdeath = self.top.get_widget('mdeath')

        self.gid    = self.top.get_widget('gid')
        self.reltype= self.top.get_widget('relationship_type')

        self.ok     = self.top.get_widget('ok')
        self.cancel = self.top.get_widget('cancel')

        self.cancel.connect('clicked', self.close_window)
        
    def load_data(self):
        self.load_parent(self.family.get_father_handle(),self.fname,
                         self.fbirth, self.fdeath)
        self.load_parent(self.family.get_mother_handle(),self.mname,
                         self.mbirth, self.mdeath)

    def load_parent(self,handle,name_obj,birth_obj,death_obj):
        if handle:
            db = self.dbstate.db
            person = db.get_person_from_handle(handle)
            name = "%s [%s]" % (NameDisplay.displayer.display(person),
                                person.gramps_id)
            data = ReportUtils.get_birth_death_strings(db,person)
            birth = data[0]
            death = data[4]
        else:
            name = ""
            birth = ""
            death = ""

        name_obj.set_text(name)
        birth_obj.set_text(birth)
        death_obj.set_text(death)

    def close_window(self,obj):
        self.close()
