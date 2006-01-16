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
import sys
from gettext import gettext as _

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
import NameDisplay
import DisplayState
import Spell
import GrampsDisplay
import RelLib
import ReportUtils
import AutoComp
import GrampsWidgets

from DdTargets import DdTargets
from WindowUtils import GladeIf
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class AttrEmbedList(EmbeddedList):

    _HANDLE_COL = -1

    column_names = [
        (_('Type'),0),
        (_('Value'),1),
        ]
    
    def __init__(self,dbstate,uistate,track,data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Attributes'), FamilyAttrModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

class ChildEmbedList(EmbeddedList):

    _HANDLE_COL = 8

    column_names = [
        (_('#'),0) ,
        (_('ID'),1) ,
        (_('Name'),9),
        (_('Gender'),3),
        (_('Birth Date'),10),
        (_('Death Date'),11),
        (_('Birth Place'),6),
        (_('Death Place'),7),
        ]
    
    def __init__(self,dbstate,uistate,track,family):
        self.family = family
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Children'), ChildModel)

    def get_icon_name(self):
        return 'gramps-person'

    def get_data(self):
        return self.family.get_child_handle_list()

    def column_order(self):
        return self.dbstate.db.get_child_column_order()

    def add_button_clicked(self,obj):
        print "Add Button Clicked"

    def del_button_clicked(self,obj):
        handle = self.get_selected()
        if handle:
            self.family.remove_child_handle(handle)
            self.rebuild()

    def edit_button_clicked(self,obj):
        handle = self.get_selected()
        if handle:
            import EditPerson
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.dbstate,self.uistate,self.track,person)

#-------------------------------------------------------------------------
#
# EditFamily
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

        self.mname  = None
        self.fname  = None
        
        self.show()

    def build_menu_names(self,obj):
        return ('Edit Family','Undefined Submenu')

    def build_window_key(self,obj):
        return id(self.family.handle)

    def build_interface(self):

        self.top = gtk.glade.XML(const.placesFile,"marriageEditor","gramps")
        self.gladeif = GladeIf(self.top)
        self.window = self.top.get_widget("marriageEditor")

        self.fbirth = self.top.get_widget('fbirth')
        self.fdeath = self.top.get_widget('fdeath')
        
        self.mbirth = self.top.get_widget('mbirth')
        self.mdeath = self.top.get_widget('mdeath')

        self.gid    = self.top.get_widget('gid')
        self.reltype= self.top.get_widget('marriage_type')

        self.mbutton= self.top.get_widget('mbutton')
        self.fbutton= self.top.get_widget('fbutton')

        self.mbox   = self.top.get_widget('mbox')
        self.fbox   = self.top.get_widget('fbox')

        self.ok     = self.top.get_widget('ok')
        self.cancel = self.top.get_widget('cancel')

        self.vbox   = self.top.get_widget('vbox')
        self.child_list = self.top.get_widget('child_list')

        rel_types = dict(Utils.family_relations)

        mtype = self.family.get_relationship()
        if mtype:
            defval = mtype[0]
        else:
            defval = None

        self.type_sel = AutoComp.StandardCustomSelector(
            rel_types, self.reltype, RelLib.Family.CUSTOM, defval)

        self.notebook = gtk.Notebook()
        self.notebook.show()
        
        self.vbox.pack_start(self.notebook,True)
        self.cancel.connect('clicked', self.close_window)
        
    def load_data(self):
        self.update_father(self.family.get_father_handle())
        self.update_mother(self.family.get_mother_handle())

        self.mbutton.connect('clicked',self.mother_clicked)
        self.fbutton.connect('clicked',self.father_clicked)

        self.child_list = ChildEmbedList(self.dbstate,self.uistate,
                                         self.track, self.family)
        self.event_list = EventEmbedList(self.dbstate,self.uistate,
                                         self.track,self.family)
        self.attr_list = AttrEmbedList(self.dbstate, self.uistate, self.track,
                                       self.family.get_attribute_list())
        self.note_tab = NoteTab(self.dbstate, self.uistate, self.track,
                                self.family.get_note_object())
        self.gallery_tab = GalleryTab(self.dbstate, self.uistate, self.track,
                                      self.family.get_media_list())

        self.notebook.insert_page(self.child_list)
        self.notebook.set_tab_label(self.child_list,self.child_list.get_tab_widget())

        self.notebook.insert_page(self.event_list)
        self.notebook.set_tab_label(self.event_list,self.event_list.get_tab_widget())

        self.notebook.insert_page(self.attr_list)
        self.notebook.set_tab_label(self.attr_list,self.attr_list.get_tab_widget())

        self.notebook.insert_page(self.note_tab)
        self.notebook.set_tab_label(self.note_tab,self.note_tab.get_tab_widget())

        self.notebook.insert_page(self.gallery_tab)
        self.notebook.set_tab_label(self.gallery_tab,self.gallery_tab.get_tab_widget())

        self.gid.set_text(self.family.get_gramps_id())

    def update_father(self,handle):
        self.load_parent(handle, self.fbox, self.fbirth, self.fdeath, self.fbutton)

    def update_mother(self,handle):
        self.load_parent(handle, self.mbox, self.mbirth, self.mdeath, self.mbutton)

    def mother_clicked(self,obj):
        handle = self.family.get_mother_handle()
        if handle:
            self.family.set_mother_handle(None)
            self.update_mother(None)
        else:
            print "Call person selector"

    def father_clicked(self,obj):
        handle = self.family.get_father_handle()
        if handle:
            self.family.set_father_handle(None)
            self.update_father(None)
        else:
            print "Call person selector"

    def edit_person(self,obj,event,handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            import EditPerson
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.dbstate, self.uistate, self.track, person)

    def load_parent(self,handle,box,birth_obj,death_obj,btn_obj):

        is_used = handle != None

        for i in box.get_children():
            box.remove(i)
        
        btn_obj.remove(btn_obj.get_children()[0])
        
        if is_used:
            db = self.dbstate.db
            person = db.get_person_from_handle(handle)
            name = "%s [%s]" % (NameDisplay.displayer.display(person),
                                person.gramps_id)
            data = ReportUtils.get_birth_death_strings(db,person)
            birth = data[0]
            death = data[4]

            del_image = gtk.Image()
            del_image.show()
            del_image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_BUTTON)
            btn_obj.add(del_image)

            box.pack_start(GrampsWidgets.LinkBox(
                GrampsWidgets.BasicLabel(name),
                GrampsWidgets.IconButton(self.edit_person,person.handle)
                ))
        else:
            name = ""
            birth = ""
            death = ""

            add_image = gtk.Image()
            add_image.show()
            add_image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_BUTTON)
            btn_obj.add(add_image)

        birth_obj.set_text(birth)
        death_obj.set_text(death)

    def close_window(self,obj):
        self.close()
