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
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gc
from cgi import escape

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
import NameDisplay
import Date
import DateEdit
import DateHandler
import Spell
import GrampsDisplay
import DisplayState

from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# NameEditor class
#
#-------------------------------------------------------------------------
class NameEditor(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,name,track):

        self.db = dbstate.db
        self.uistate = uistate
        self.state = dbstate
        
        DisplayState.ManagedWindow.__init__(self, uistate, track, name)
        if self.already_exist:
            return

        self.name = name
        self.top = gtk.glade.XML(const.dialogFile, "name_edit","gramps")
        self.gladeif = GladeIf(self.top)
        self.window = self.top.get_widget("name_edit")
        self.given_field  = self.top.get_widget("alt_given")
        self.given_field.set_editable(not self.db.readonly)
        self.sort_as  = self.top.get_widget("sort_as")
        self.sort_as.set_sensitive(not self.db.readonly)
        self.display_as  = self.top.get_widget("display_as")
        self.display_as.set_sensitive(not self.db.readonly)
        self.group_as  = self.top.get_widget("group_as")
        self.title_field  = self.top.get_widget("alt_title")
        self.title_field.set_editable(not self.db.readonly)
        self.suffix_field = self.top.get_widget("alt_suffix")
        self.suffix_field.set_editable(not self.db.readonly)
        self.patronymic_field = self.top.get_widget("patronymic")
        self.patronymic_field.set_editable(not self.db.readonly)
        self.combo = self.top.get_widget("alt_surname_list")
        self.combo.set_sensitive(not self.db.readonly)
        self.date = self.top.get_widget('date')
        self.date.set_editable(not self.db.readonly)

        if self.name:
            self.srcreflist = self.name.get_source_references()
            self.date_obj = self.name.get_date_object()
        else:
            self.srcreflist = []
            self.date_obj = Date.Date()

        self.date.set_text(DateHandler.displayer.display(self.date_obj))

        date_stat = self.top.get_widget("date_stat")
        date_stat.set_sensitive(not self.db.readonly)
        self.date_check = DateEdit.DateEdit(
            self.date_obj, self.date,
            date_stat, self.window)

        AutoComp.fill_combo(self.combo,self.db.get_surname_list())
        self.surname_field = self.combo.get_child()
        self.prefix_field = self.top.get_widget("alt_prefix")
        self.prefix_field.set_editable(not self.db.readonly)

        self.type_combo = self.top.get_widget("name_type")
        self.type_combo.set_sensitive(not self.db.readonly)
        self.note_field = self.top.get_widget("alt_note")
        self.note_field.set_editable(not self.db.readonly)
        self.spell = Spell.Spell(self.note_field)
        
        self.slist = self.top.get_widget('slist')
        self.priv = self.top.get_widget("priv")
        self.general_label = self.top.get_widget("general_tab")
        self.sources_label = self.top.get_widget("sources_tab")
        self.notes_label = self.top.get_widget("note_tab")
        self.priv.set_sensitive(not self.db.readonly)
        self.flowed = self.top.get_widget("alt_flowed")
        self.flowed.set_sensitive(not self.db.readonly)
        self.preform = self.top.get_widget("alt_preform")
        self.preform.set_sensitive(not self.db.readonly)
        self.group_over = self.top.get_widget('group_over')
        self.group_over.set_sensitive(not self.db.readonly)

        self.type_selector = AutoComp.StandardCustomSelector(
            Utils.name_types, self.type_combo, RelLib.Name.CUSTOM,
            RelLib.Name.BIRTH)

        full_name = NameDisplay.displayer.display_name(name)

        alt_title = self.top.get_widget("title")

        if full_name == "":
            tmsg = _("Name Editor")
        else:
            tmsg = _("Name Editor for %s") % escape(full_name)

        Utils.set_titles(self.window, alt_title, tmsg, _('Name Editor'))

        self.sourcetab = Sources.SourceTab(
            self.state, self.uistate, self.track,
            self.srcreflist, self, self.top, self.window, self.slist,
            self.top.get_widget('add_src'), self.top.get_widget('edit_src'),
            self.top.get_widget('del_src'), self.db.readonly)
        
        self.note_buffer = self.note_field.get_buffer()
        
        self.gladeif.connect('name_edit','delete_event',self.on_delete_event)
        self.gladeif.connect('button119','clicked',self.close)
        self.gladeif.connect('button118','clicked',self.on_name_edit_ok_clicked)
        okbtn = self.top.get_widget('button118')
        okbtn.set_sensitive(not self.db.readonly)
        self.gladeif.connect('button131','clicked',self.on_help_clicked)
        self.gladeif.connect('notebook3','switch_page',self.on_switch_page)
        self.gladeif.connect('group_over','toggled',self.on_group_over_toggled)

        if name != None:
            self.given_field.set_text(name.get_first_name())
            self.surname_field.set_text(name.get_surname())
            self.title_field.set_text(name.get_title())
            self.suffix_field.set_text(name.get_suffix())
            self.prefix_field.set_text(name.get_surname_prefix())
            self.type_selector.set_values(name.get_type())
            self.patronymic_field.set_text(name.get_patronymic())
            self.priv.set_active(name.get_privacy())
            Utils.bold_label(self.general_label)
            if name.get_note():
                self.note_buffer.set_text(name.get_note())
                Utils.bold_label(self.notes_label)
                if name.get_note_format() == 1:
                    self.preform.set_active(1)
                else:
                    self.flowed.set_active(1)
            else:
                Utils.unbold_label(self.notes_label)
            self.display_as.set_active(name.get_display_as())
            self.sort_as.set_active(name.get_display_as())
            grp_as = name.get_group_as()
            if grp_as:
                self.group_as.set_text(name.get_group_as())
            else:
                self.group_as.set_text(name.get_surname())
        else:
            self.display_as.set_active(0)
            self.sort_as.set_active(0)
            Utils.unbold_label(self.notes_label)
            Utils.unbold_label(self.sources_label)
            Utils.unbold_label(self.general_label)

        self.surname_field.connect('changed',self.update_group_as)

        self.window.set_transient_for(self.parent_window)
        self.window.show()

    def build_menu_names(self,name):
        if name:
            submenu_label = _('%s: %s') % (_('Name',NameDisplay.displayer.display(name)))
        else:
            submenu_label = _('New Name')
        menu_label = _('Name Editor')
        return (menu_label,submenu_label)

    def update_group_as(self,obj):
        if not self.group_over.get_active():
            if self.name and self.name.get_group_as() != self.name.get_surname():
                val = self.name.get_group_as()
            else:
                name = unicode(self.surname_field.get_text())
                val = self.db.get_name_group_mapping(name)
            self.group_as.set_text(val)
        
    def on_group_over_toggled(self,obj):
        if obj.get_active():
            self.group_as.set_sensitive(True)
            self.group_as.set_editable(True)
        else:
            field_value = unicode(self.surname_field.get_text())
            mapping = self.db.get_name_group_mapping(field_value)
            self.group_as.set_text(mapping)
            self.group_as.set_sensitive(False)
            self.group_as.set_editable(False)

    def on_delete_event(self,*obj):
        self.gladeif.close()
        gc.collect()

    def close(self,*obj):
        self.gladeif.close()
        self.window.destroy()
        gc.collect()

    def on_help_clicked(self,*obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-an')

    def on_name_edit_ok_clicked(self,obj):
        first = unicode(self.given_field.get_text())
        last = unicode(self.surname_field.get_text())
        title = unicode(self.title_field.get_text())
        prefix = unicode(self.prefix_field.get_text())
        suffix = unicode(self.suffix_field.get_text())
        patronymic = unicode(self.patronymic_field.get_text())
        note = unicode(self.note_buffer.get_text(self.note_buffer.get_start_iter(),
                                 self.note_buffer.get_end_iter(),False))
        format = self.preform.get_active()
        priv = self.priv.get_active()

        the_type = self.type_selector.get_values()

        # FIXME: this remained from gramps20 -- check
        # if const.NameTypesMap.has_value(mtype):
        #     mtype = const.NameTypesMap.find_key(mtype)
        # if not mtype:
        #     mtype = "Also Known As"
        
        if self.name == None:
            self.name = RelLib.Name()
            self.parent.nlist.append(self.name)

        self.name.set_date_object(self.date_obj)
        
        self.name.set_source_reference_list(self.srcreflist)

        grp_as = unicode(self.group_as.get_text())
        srn = unicode(self.surname_field.get_text())

        if self.name.get_display_as() != self.display_as.get_active():
            self.name.set_display_as(self.display_as.get_active())
            self.parent.lists_changed = 1

        prefix = unicode(self.prefix_field.get_text())
        if self.name.get_surname_prefix() != prefix:
            self.name.set_surname_prefix(prefix)
            self.parent.lists_changed = 1
 
        if self.name.get_sort_as() != self.sort_as.get_active():
            self.name.set_sort_as(self.sort_as.get_active())
            self.parent.lists_changed = 1

        if not self.group_over.get_active():
            self.name.set_group_as("")
            self.parent.lists_changed = 1
        elif self.name.get_group_as() != grp_as:
            if grp_as not in self.db.get_name_group_keys():
                from QuestionDialog import QuestionDialog2
                q = QuestionDialog2(
                    _("Group all people with the same name?"),
                    _("You have the choice of grouping all people with the "
                      "name of %(surname)s with the name of %(group_name)s, or "
                      "just mapping this particular name.") % { 'surname' : srn,
                                                                'group_name':grp_as},
                    _("Group all"),
                    _("Group this name only"))
                val = q.run()
                if val:
                    self.name.set_group_as("")
                    self.db.set_name_group_mapping(srn,grp_as)
                else:
                    self.name.set_group_as(grp_as)
            self.parent.lists_changed = 1

        self.update_name(first,last,suffix,patronymic,title,the_type,note,format,priv)
        self.parent.lists_changed = 1

        self.close(obj)

    def update_name(self,first,last,suffix,patronymic,title,the_type,note,format,priv):
        
        if self.name.get_first_name() != first:
            self.name.set_first_name(first)
            self.parent.lists_changed = 1
        
        if self.name.get_surname() != last:
            self.name.set_surname(last)
            self.parent.lists_changed = 1

        if self.name.get_suffix() != suffix:
            self.name.set_suffix(suffix)
            self.parent.lists_changed = 1

        if self.name.get_patronymic() != patronymic:
            self.name.set_patronymic(patronymic)
            self.parent.lists_changed = 1

        if self.name.get_title() != title:
            self.name.set_title(title)
            self.parent.lists_changed = 1

        if self.name.get_type() != the_type:
            self.name.set_type(the_type)
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
        start = self.note_buffer.get_start_iter()
        stop = self.note_buffer.get_end_iter()
        text = unicode(self.note_buffer.get_text(start, stop, False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
