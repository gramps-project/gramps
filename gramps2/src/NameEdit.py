#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import AutoComp
import Sources
import RelLib

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# NameEditor class
#
#-------------------------------------------------------------------------
class NameEditor:

    def __init__(self,parent,name,callback,parent_window=None):
        self.parent = parent
        self.name = name
        self.callback = callback
        self.top = gtk.glade.XML(const.dialogFile, "name_edit","gramps")
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

        alt_title = self.top.get_widget("title")

        if full_name == ", ":
            tmsg = _("Alternate Name Editor")
        else:
            tmsg = _("Alternate Name Editor for %s") % full_name

        Utils.set_titles(self.window, alt_title, tmsg, _('Alternate Name Editor'))

        self.sourcetab = Sources.SourceTab(self.srcreflist, self.parent,
                                           self.top, self.window, self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))
        
        self.note_buffer = self.note_field.get_buffer()
        
        if name != None:
            self.given_field.set_text(name.getFirstName())
            self.surname_field.set_text(name.getSurname())
            self.title_field.set_text(name.getTitle())
            self.suffix_field.set_text(name.getSuffix())
            self.type_field.entry.set_text(_(name.getType()))
            self.priv.set_active(name.getPrivacy())
            self.note_buffer.set_text(name.getNote())

        if parent_window:
            self.window.set_transient_for(parent_window)
        val = self.window.run()
        if val == gtk.RESPONSE_OK:
            self.on_name_edit_ok_clicked()
        self.window.destroy()

    def on_name_edit_ok_clicked(self):
        first = self.given_field.get_text()
        last = self.surname_field.get_text()
        title = self.title_field.get_text()
        suffix = self.suffix_field.get_text()
        note = self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                         self.note_buffer.get_end_iter(),gtk.FALSE)
        priv = self.priv.get_active()

        type = self.type_field.entry.get_text()

        if const.NameTypesMap.has_key(type):
            type = const.NameTypesMap[type]
        else:
            type = "Also Known As"
        
        if self.name == None:
            self.name = RelLib.Name()
            self.parent.nlist.append(self.name)
        
        self.name.setSourceRefList(self.srcreflist)
        
        self.update_name(first,last,suffix,title,type,note,priv)
        self.parent.lists_changed = 1

        self.callback(self.name)

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
        
    
