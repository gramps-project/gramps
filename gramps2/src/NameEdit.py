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

# $Id$

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

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
        self.db = self.parent.db
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
        self.sources_label = self.top.get_widget("sourcesName")
        self.notes_label = self.top.get_widget("noteName")
        self.flowed = self.top.get_widget("alt_flowed")
        self.preform = self.top.get_widget("alt_preform")

        types = const.NameTypesMap.get_values()
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

        self.sourcetab = Sources.SourceTab(self.srcreflist, self,
                                           self.top, self.window, self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))
        
        self.note_buffer = self.note_field.get_buffer()
        
        self.top.signal_autoconnect({
            "on_help_name_clicked" : self.on_help_clicked,
            "on_switch_page" : self.on_switch_page
            })

        if name != None:
            self.given_field.set_text(name.getFirstName())
            self.surname_field.set_text(name.getSurname())
            self.title_field.set_text(name.getTitle())
            self.suffix_field.set_text(name.getSuffix())
            self.type_field.entry.set_text(_(name.getType()))
            self.priv.set_active(name.getPrivacy())
            if name.getNote():
            	self.note_buffer.set_text(name.getNote())
                Utils.bold_label(self.notes_label)
            	if name.getNoteFormat() == 1:
                    self.preform.set_active(1)
            	else:
                    self.flowed.set_active(1)

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_name_edit_ok_clicked()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        self.val = self.window.run()

    def on_name_edit_ok_clicked(self):
        first = unicode(self.given_field.get_text())
        last = unicode(self.surname_field.get_text())
        title = unicode(self.title_field.get_text())
        suffix = unicode(self.suffix_field.get_text())
        note = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                 self.note_buffer.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()
        priv = self.priv.get_active()

        type = unicode(self.type_field.entry.get_text())

        if const.NameTypesMap.has_value(type):
            type = const.NameTypesMap.find_key(type)
        else:
            type = "Also Known As"
        
        if self.name == None:
            self.name = RelLib.Name()
            self.parent.nlist.append(self.name)
        
        self.name.setSourceRefList(self.srcreflist)
        
        self.update_name(first,last,suffix,title,type,note,format,priv)
        self.parent.lists_changed = 1

        self.callback(self.name)

    def update_name(self,first,last,suffix,title,type,note,format,priv):
        
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

        if self.name.getNoteFormat() != format:
            self.name.setNoteFormat(format)
            self.parent.lists_changed = 1

        if self.name.getPrivacy() != priv:
            self.name.setPrivacy(priv)
            self.parent.lists_changed = 1
        
    def on_switch_page(self,obj,a,page):
        text = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                self.note_buffer.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
