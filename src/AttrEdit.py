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
"""
The AttrEdit module provides the AddressEditor class. This provides a
mechanism for the user to edit address information.
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import utils
from RelLib import *
import Sources

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor:
    """
    Displays a dialog that allows the user to edit an attribute.
    """
    def __init__(self,parent,attrib,title,list):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
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
            "on_attr_edit_ok_clicked" : self.on_ok_clicked,
            "on_combo_insert_text"    : utils.combo_insert_text,
            "on_source_clicked" : self.on_source_clicked
            })

    def on_source_clicked(self,obj):
        """Displays the SourceSelector, allowing sources to be edited"""
        Sources.SourceSelector(self.srcreflist,self.parent,src_changed)
            
    def on_ok_clicked(self,obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """
        type = self.type_field.get_text()
        value = self.value_field.get_text()
        note = self.note_field.get_chars(0,-1)
        priv = self.priv.get_active()

        if self.attrib == None:
            self.attrib = Attribute()
            self.attrib.setSourceRefList(self.srcreflist)
            self.parent.alist.append(self.attrib)
        
        self.update(type,value,note,priv)
        
        self.parent.redraw_attr_list()
        utils.destroy_passed_object(obj)

    def check(self,get,set,data):
        """Compares a data item, updates if necessary, and sets the
        parents lists_changed flag"""
        if get() != data:
            set(data)
            self.parent.lists_changed = 1
            
    def update(self,type,value,note,priv):
        """Compares the data items, and updates if necessary"""
        ntype = const.save_pattr(type)
        self.check(self.attrib.getType,self.attrib.setType,ntype)
        self.check(self.attrib.getValue,self.attrib.setValue,value)
        self.check(self.attrib.getNote,self.attrib.setNote,note)
        self.check(self.attrib.getPrivacy,self.attrib.setPrivacy,priv)

def src_changed(parent):
    """Sets the lists_changed flag of the parent object. Used as a callback
    to the source editor, so the source editor can indicate a change."""
    parent.lists_changed = 1
