#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
        if name:
            if self.parent.child_windows.has_key(name):
                self.parent.child_windows[name].present(None)
                return
            else:
                self.win_key = name
        else:
            self.win_key = self
        self.name = name
        self.callback = callback
        self.child_windows = {}
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
        self.combo = AutoComp.AutoCombo(slist,self.parent.db.get_surnames())
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
            self.srcreflist = self.name.get_source_references()
        else:
            self.srcreflist = []

        full_name = parent.person.get_primary_name().get_name()

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
            "on_name_edit_ok_clicked" : self.on_name_edit_ok_clicked,
            "on_name_edit_cancel_clicked" : self.close, 
            "on_name_edit_delete_event" : self.on_delete_event,
            "on_switch_page" : self.on_switch_page
            })

        if name != None:
            self.given_field.set_text(name.get_first_name())
            self.surname_field.set_text(name.get_surname())
            self.title_field.set_text(name.get_title())
            self.suffix_field.set_text(name.get_suffix())
            self.type_field.entry.set_text(_(name.get_type()))
            self.priv.set_active(name.get_privacy())
            if name.get_note():
                self.note_buffer.set_text(name.get_note())
                Utils.bold_label(self.notes_label)
                if name.get_note_format() == 1:
                    self.preform.set_active(1)
                else:
                    self.flowed.set_active(1)

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if not self.name:
            label = _("New Name")
        else:
            label = self.name.get_name()
        if not label.strip():
            label = _("New Name")
        label = "%s: %s" % (_('Alternate Name'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Name Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def on_name_edit_ok_clicked(self,obj):
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
        
        self.name.set_source_reference_list(self.srcreflist)
        
        self.update_name(first,last,suffix,title,type,note,format,priv)
        self.parent.lists_changed = 1

        self.callback(self.name)
        self.close(obj)

    def update_name(self,first,last,suffix,title,type,note,format,priv):
        
        if self.name.get_first_name() != first:
            self.name.set_first_name(first)
            self.parent.lists_changed = 1
        
        if self.name.get_surname() != last:
            self.name.set_surname(last)
            self.parent.db.add_surname(last)
            self.parent.lists_changed = 1

        if self.name.get_suffix() != suffix:
            self.name.set_suffix(suffix)
            self.parent.lists_changed = 1

        if self.name.get_title() != title:
            self.name.set_title(title)
            self.parent.lists_changed = 1

        if self.name.get_type() != type:
            self.name.set_type(type)
            self.parent.lists_changed = 1

        if self.name.get_note() != note:
            self.name.set_note(note)
            self.parent.lists_changed = 1

        if self.name.get_note_format() != format:
            self.name.set_note_format(format)
            self.parent.lists_changed = 1

        if self.name.get_privacy() != priv:
            self.name.set_privacy(priv)
            self.parent.lists_changed = 1
        
    def on_switch_page(self,obj,a,page):
        text = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                self.note_buffer.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
