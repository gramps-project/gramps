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
import Utils
import AutoComp
import Sources
from RelLib import *

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# NameEditor class
#
#-------------------------------------------------------------------------
class NameEditor:

    def __init__(self,parent,name):
        self.parent = parent
        self.name = name
        self.top = libglade.GladeXML(const.dialogFile, "name_edit")
        self.window = self.top.get_widget("name_edit")
        self.given_field  = self.top.get_widget("alt_given")
        self.title_field  = self.top.get_widget("alt_title")
        self.surname_field = self.top.get_widget("alt_last")
        self.suffix_field = self.top.get_widget("alt_suffix")
        self.type_field = self.top.get_widget("name_type")
        self.note_field = self.top.get_widget("alt_note")
        self.slist = self.top.get_widget('slist')
        slist = self.top.get_widget("alt_surname_list")
        self.combo = AutoComp.AutoCombo(slist,self.parent.db.getSurnames())
        self.priv = self.top.get_widget("priv")

        types = const.NameTypesMap.keys()
        types.sort()
        self.type_field.set_popdown_strings(types)
        self.typecomp = AutoComp.AutoEntry(self.type_field.entry,types)

        if self.name:
            self.srcreflist = self.name.getSourceRefList()
        else:
            self.srcreflist = []

        full_name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("altTitle").set_text(
            _("Alternate Name Editor for %s") % full_name)

        # Typing CR selects OK button
        self.window.editable_enters(self.given_field)
        self.window.editable_enters(self.surname_field)
        self.window.editable_enters(self.suffix_field)
        self.window.editable_enters(self.title_field)
        self.window.editable_enters(self.type_field.entry)

        self.sourcetab = Sources.SourceTab(self.srcreflist,self.parent,self.top,self.slist)
        
        if name != None:
            self.given_field.set_text(name.getFirstName())
            self.surname_field.set_text(name.getSurname())
            self.title_field.set_text(name.getTitle())
            self.suffix_field.set_text(name.getSuffix())
            self.type_field.entry.set_text(_(name.getType()))
            self.priv.set_active(name.getPrivacy())
            self.note_field.set_point(0)
            self.note_field.insert_defaults(name.getNote())
            self.note_field.set_word_wrap(1)

        self.top.signal_autoconnect({
            "destroy_passed_object"   : Utils.destroy_passed_object,
            "on_combo_insert_text"    : Utils.combo_insert_text,
            "on_name_edit_ok_clicked" : self.on_name_edit_ok_clicked,
            })

    def on_name_edit_ok_clicked(self,obj):
        first = self.given_field.get_text()
        last = self.surname_field.get_text()
        title = self.title_field.get_text()
        suffix = self.suffix_field.get_text()
        note = self.note_field.get_chars(0,-1)
        priv = self.priv.get_active()

        type = self.type_field.entry.get_text()

        if const.NameTypesMap.has_key(type):
            type = const.NameTypesMap[type]
        else:
            type = "Also Known As"
        
        if self.name == None:
            self.name = Name()
            self.parent.nlist.append(self.name)
        
        self.name.setSourceRefList(self.srcreflist)
        
        self.update_name(first,last,suffix,title,type,note,priv)
        self.parent.lists_changed = 1

        self.parent.redraw_name_list()
        Utils.destroy_passed_object(obj)

    def update_name(self,first,last,suffix,title,type,note,priv):
        
        if self.name.getFirstName() != first:
            self.name.setFirstName(first)
            self.parent.lists_changed = 1
        
        if self.name.getSurname() != last:
            self.name.setSurname(last)
            self.parent.db.addSurname(last)
            self.parent.lists_changed = 1

        if self.name.getSuffix() != suffix:
            self.name.setSuffix(suffix)
            self.parent.lists_changed = 1

        if self.name.getTitle() != title:
            self.name.setTitle(title)
            self.parent.lists_changed = 1

        if self.name.getType() != type:
            self.name.setType(type)
            self.parent.lists_changed = 1

        if self.name.getNote() != note:
            self.name.setNote(note)
            self.parent.lists_changed = 1

        if self.name.getPrivacy() != priv:
            self.name.setPrivacy(priv)
            self.parent.lists_changed = 1
        
    
