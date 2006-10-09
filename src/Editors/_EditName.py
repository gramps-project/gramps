#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import NameDisplay
from _EditSecondary import EditSecondary

from DisplayTabs import SourceEmbedList,NoteTab
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditName class
#
#-------------------------------------------------------------------------
class EditName(EditSecondary):

    def __init__(self, dbstate, uistate, track, name, callback):

        EditSecondary.__init__(self, dbstate, uistate,
                               track, name, callback)

    def _local_init(self):
        
        self.top = gtk.glade.XML(const.gladeFile, "name_edit","gramps")
        self.set_window(self.top.get_widget("name_edit"),
                        self.top.get_widget("title"),
                        _("Name Editor"))

        self.original_group_as = self.obj.get_group_as()
        self.general_label = self.top.get_widget("general_tab")

        self.group_over = self.top.get_widget('group_over')
        self.group_over.connect('toggled',self.on_group_over_toggled)
        self.group_over.set_sensitive(not self.db.readonly)

        Utils.bold_label(self.general_label)

    def _post_init(self):
        if self.original_group_as and \
               (self.original_group_as != self.obj.get_surname()):
            self.group_over.set_active(True)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('button119'))
        self.define_help_button(self.top.get_widget('button131'),'adv-an')
        self.define_ok_button(self.top.get_widget('button118'),self.save)

    def _setup_fields(self):
        self.group_as = MonitoredEntry(
            self.top.get_widget("group_as"),
            self.obj.set_group_as,
            self.obj.get_group_as,
            self.db.readonly)

        if not self.original_group_as:
            self.group_as.force_value(self.obj.get_surname())
            
        format_list = [(name,number) for (number,name,fmt_str,act)
                       in NameDisplay.displayer.get_name_format(also_default=True)]
            
        self.sort_as = MonitoredMenu(
            self.top.get_widget('sort_as'),
            self.obj.set_sort_as,
            self.obj.get_sort_as,
            format_list,
            self.db.readonly)

        self.display_as = MonitoredMenu(
            self.top.get_widget('display_as'),
            self.obj.set_display_as,
            self.obj.get_display_as,
            format_list,
            self.db.readonly)

        self.given_field = MonitoredEntry(
            self.top.get_widget("alt_given"),
            self.obj.set_first_name,
            self.obj.get_first_name,
            self.db.readonly)

        self.call_field = MonitoredEntry(
            self.top.get_widget("call"),
            self.obj.set_call_name,
            self.obj.get_call_name,
            self.db.readonly)

        self.title_field = MonitoredEntry(
            self.top.get_widget("alt_title"),
            self.obj.set_title,
            self.obj.get_title,
            self.db.readonly)

        self.suffix_field = MonitoredEntry(
            self.top.get_widget("alt_suffix"),
            self.obj.set_suffix,
            self.obj.get_suffix,
            self.db.readonly)

        self.patronymic_field = MonitoredEntry(
            self.top.get_widget("patronymic"),
            self.obj.set_patronymic,
            self.obj.get_patronymic,
            self.db.readonly)

        self.surname_field = MonitoredEntry(
            self.top.get_widget("alt_surname"),
            self.obj.set_surname,
            self.obj.get_surname,
            self.db.readonly,
            changed=self.update_group_as)

        self.prefix_field = MonitoredEntry(
            self.top.get_widget("alt_prefix"),
            self.obj.set_surname_prefix,
            self.obj.get_surname_prefix,
            self.db.readonly)
            
        self.date = MonitoredDate(
            self.top.get_widget("date"),
            self.top.get_widget("date_stat"), 
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

        self.obj_combo = MonitoredDataType(
            self.top.get_widget("name_type"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            self.db.get_name_types(),
            )
        
        self.privacy = PrivacyButton(
            self.top.get_widget("priv"), self.obj)
        
    def _create_tabbed_pages(self):

        notebook = self.top.get_widget("notebook")

        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,self.track,self.obj))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))

    def build_menu_names(self,name):
        if name:
            ntext = NameDisplay.displayer.display_name(name)
            submenu_label = _('%s: %s') % (_('Name'),ntext)
        else:
            submenu_label = _('New Name')
        menu_label = _('Name Editor')
        return (menu_label,submenu_label)

    def update_group_as(self,obj):
        if not self.group_over.get_active():
            if self.obj.get_group_as() != self.obj.get_surname():
                val = self.obj.get_group_as()
            else:
                name = self.obj.get_surname()
                val = self.db.get_name_group_mapping(name)
            self.group_as.force_value(val)
        
    def on_group_over_toggled(self,obj):
        self.group_as.enable(obj.get_active())
        
        if not obj.get_active():
            field_value = self.obj.get_surname()
            mapping = self.db.get_name_group_mapping(field_value)
            self.group_as.set_text(mapping)

    def save(self,*obj):

        if not self.group_over.get_active():
            self.obj.set_group_as("")
        elif self.obj.get_group_as() == self.obj.get_surname():
            self.obj.set_group_as("")
        elif self.obj.get_group_as() != self.original_group_as:
            grp_as = self.obj.get_group_as()
            srn = self.obj.get_surname()
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
                    self.obj.set_group_as("")
                    self.db.set_name_group_mapping(srn,grp_as)
                else:
                    self.obj.set_group_as(grp_as)

        if self.callback:
            self.callback(self.obj)
        self.close()

        
