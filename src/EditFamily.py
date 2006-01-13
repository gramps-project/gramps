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
import ImageSelect
import NameDisplay
import DisplayState
import Spell
import GrampsDisplay
import RelLib
import ListModel
import ReportUtils
import DisplayTabs

from DdTargets import DdTargets
from WindowUtils import GladeIf

class EventEmbedList(DisplayTabs.EmbeddedList):

    column_names = [
        (_('Description'),0),
        (_('ID'),1),
        (_('Type'),2),
        (_('Date'),3),
        (_('Place'),4),
        (_('Cause'),5),
        ]
    
    def __init__(self,db,family):
        self.family = family
        self.hbox = gtk.HBox()
        self.label = gtk.Label(_('Events'))
        self.hbox.show_all()
        
        DisplayTabs.EmbeddedList.__init__(self, db, DisplayTabs.EventRefModel)

    def get_data(self):
        return self.family.get_event_ref_list()

    def column_order(self):
        return ((1,0),(1,1),(1,2),(1,3),(1,4),(1,5))

    def set_label(self):
        if len(self.get_data()):
            self.label.set_text("<b>%s</b>" % _('Events'))
            self.label.set_use_markup(True)
        else:
            self.label.set_text(_('Events'))
        
    def get_tab_widget(self):
        return self.label

class AttrEmbedList(DisplayTabs.EmbeddedList):

    column_names = [
        (_('Type'),0),
        (_('Value'),1),
        ]
    
    def __init__(self,db,data):
        self.data = data
        self.hbox = gtk.HBox()
        self.label = gtk.Label(_('Attributes'))
        self.hbox.show_all()
        
        DisplayTabs.EmbeddedList.__init__(self, db, DisplayTabs.FamilyAttrModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,0),(1,1))

    def set_label(self):
        if len(self.get_data()):
            self.label.set_text("<b>%s</b>" % _('Attributes'))
            self.label.set_use_markup(True)
        else:
            self.label.set_text(_('Attributes'))
        
    def get_tab_widget(self):
        return self.label

class ChildEmbedList(DisplayTabs.EmbeddedList):

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
    
    def __init__(self,db,family):
        self.family = family
        self.hbox = gtk.HBox()
        self.label = gtk.Label(_('Children'))
        self.add_btn = gtk.Button()
        self.add_btn.add(gtk.image_new_from_stock(gtk.STOCK_ADD,
                                                  gtk.ICON_SIZE_BUTTON))
        self.edit_btn = gtk.Button()
        self.edit_btn.add(gtk.image_new_from_stock(gtk.STOCK_EDIT,
                                                   gtk.ICON_SIZE_BUTTON))
        self.del_btn = gtk.Button()
        self.del_btn.add(gtk.image_new_from_stock(gtk.STOCK_REMOVE,
                                                  gtk.ICON_SIZE_BUTTON))
        self.hbox.show_all()

        DisplayTabs.EmbeddedList.__init__(self, db, DisplayTabs.ChildModel)

        self.set_spacing(6)
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.add_btn,False)
        vbox.pack_start(self.edit_btn,False)
        vbox.pack_start(self.del_btn,False)
        vbox.show_all()
        self.pack_start(vbox,False)
    
    def get_data(self):
        return self.family.get_child_handle_list()

    def column_order(self):
        return self.db.get_child_column_order()

    def set_label(self):
        if len(self.get_data()):
            self.label.set_text("<b>%s</b>" % _('Children'))
            self.label.set_use_markup(True)
        else:
            self.label.set_text(_('Children'))
        
    def get_tab_widget(self):
        return self.label

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

        self.mbutton= self.top.get_widget('mbutton')
        self.fbutton= self.top.get_widget('fbutton')

        self.ok     = self.top.get_widget('ok')
        self.cancel = self.top.get_widget('cancel')

        self.vbox   = self.top.get_widget('vbox')
        
        self.notebook = gtk.Notebook()
        self.notebook.show()
        
        self.vbox.pack_start(self.notebook,True)

        self.child_list = self.top.get_widget('child_list')
        self.cancel.connect('clicked', self.close_window)
        
    def load_data(self):
        self.load_parent(self.family.get_father_handle(),self.fname,
                         self.fbirth, self.fdeath, self.fbutton)
        self.load_parent(self.family.get_mother_handle(),self.mname,
                         self.mbirth, self.mdeath, self.mbutton)

        self.child_list = ChildEmbedList(self.dbstate.db, self.family)
        self.event_list = EventEmbedList(self.dbstate.db, self.family)
        self.attr_list = AttrEmbedList(self.dbstate.db, self.family.get_attribute_list())
        self.note_tab = DisplayTabs.NoteTab(self.family.get_note_object())
        self.gallery_tab = DisplayTabs.GalleryTab(self.dbstate.db,self.family.get_media_list())

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


    def load_parent(self,handle,name_obj,birth_obj,death_obj,btn_obj):

        is_used = handle != None
        
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
        else:
            name = ""
            birth = ""
            death = ""

            add_image = gtk.Image()
            add_image.show()
            add_image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_BUTTON)
            btn_obj.add(add_image)

        name_obj.set_text(name)
        birth_obj.set_text(birth)
        death_obj.set_text(death)

    def close_window(self,obj):
        self.close()
