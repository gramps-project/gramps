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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
from RelLib import *
import Sources

_ = intl.gettext

#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor:

    def __init__(self,parent,attrib,title,list):
        self.parent = parent
        self.attrib = attrib
        self.top = libglade.GladeXML(const.dialogFile, "attr_edit")
        self.window = self.top.get_widget("attr_edit")
        self.type_field  = self.top.get_widget("attr_type")
        self.value_field = self.top.get_widget("attr_value")
        self.note_field = self.top.get_widget("attr_note")
        self.attrib_menu = self.top.get_widget("attr_menu")
        self.source_field = self.top.get_widget("attr_source")
        self.priv = self.top.get_widget("priv")
        
        if attrib:
            self.srcreflist = self.attrib.getSourceRefList()
        else:
            self.srcreflist = []

        # Typing CR selects OK button
        self.window.editable_enters(self.type_field);
        self.window.editable_enters(self.value_field);

        title = _("Attribute Editor for %s") % title
        self.top.get_widget("attrTitle").set_text(title)
        if len(list) > 0:
            self.attrib_menu.set_popdown_strings(list)
            self.type_field.select_region(0, -1)

        if attrib != None:
            self.type_field.set_text(attrib.getType())
            self.value_field.set_text(attrib.getValue())
            self.priv.set_active(attrib.getPrivacy())

            self.note_field.set_point(0)
            self.note_field.insert_defaults(attrib.getNote())
            self.note_field.set_word_wrap(1)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_attr_edit_ok_clicked" : self.on_attrib_edit_ok_clicked,
            "on_combo_insert_text"    : utils.combo_insert_text,
            "on_source_clicked" : self.on_attrib_source_clicked
            })

    def on_attrib_source_clicked(self,obj):
        Sources.SourceSelector(self.srcreflist,self.parent,src_changed)
            
    def on_attrib_edit_ok_clicked(self,obj):

        type = self.type_field.get_text()
        value = self.value_field.get_text()
        note = self.note_field.get_chars(0,-1)
        priv = self.priv.get_active()

        if self.attrib == None:
            self.attrib = Attribute()
            self.attrib.setSourceRefList(self.srcreflist)
            self.parent.alist.append(self.attrib)
        
        self.update_attrib(type,value,note,priv)
        
        self.parent.redraw_attr_list()
        utils.destroy_passed_object(obj)

    def update_attrib(self,type,value,note,priv):
        
        if self.attrib.getType() != const.save_pattr(type):
            self.attrib.setType(const.save_pattr(type))
            self.parent.lists_changed = 1
        
        if self.attrib.getValue() != value:
            self.attrib.setValue(value)
            self.parent.lists_changed = 1

        if self.attrib.getNote() != note:
            self.attrib.setNote(note)
            self.parent.lists_changed = 1

        if self.attrib.getPrivacy() != priv:
            self.attrib.setPrivacy(priv)
            self.parent.lists_changed = 1

def src_changed(parent):
    parent.lists_changed = 1
