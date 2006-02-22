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
import DateEdit
import DateHandler
import Spell
import GrampsDisplay
import DisplayState
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# NameEditor class
#
#-------------------------------------------------------------------------
class NameEditor(DisplayState.ManagedWindow):

    def __init__(self, dbstate, uistate, track, name, callback):

        self.db = dbstate.db
        self.dbstate = dbstate
        self.uistate = uistate
        self.state = dbstate
        self.callback = callback
        
        DisplayState.ManagedWindow.__init__(self, uistate, track, name)
        if self.already_exist:
            return

        self.name = name
        self.original_group_as = self.name.get_group_as()

        self.top = gtk.glade.XML(const.gladeFile, "name_edit","gramps")
        self.window = self.top.get_widget("name_edit")

        self.notebook = self.top.get_widget("notebook")
        self.general_label = self.top.get_widget("general_tab")

        self.group_over = self.top.get_widget('group_over')
        self.group_over.connect('toggled',self.on_group_over_toggled)
        self.group_over.set_sensitive(not self.db.readonly)

        full_name = NameDisplay.displayer.display_name(name)

        alt_title = self.top.get_widget("title")

        if full_name == "":
            tmsg = _("Name Editor")
        else:
            tmsg = _("Name Editor for %s") % escape(full_name)

        Utils.set_titles(self.window, alt_title, tmsg, _('Name Editor'))

        Utils.bold_label(self.general_label)

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        
        if self.original_group_as and self.original_group_as != self.name.get_surname():
            self.group_over.set_active(True)

        self.show()

    def _connect_signals(self):
        self.window.connect('delete_event',self.on_delete_event)
        self.top.get_widget('button119').connect('clicked',self.close_window)
        self.top.get_widget('button131').connect('clicked',self.on_help_clicked)
        okbtn = self.top.get_widget('button118')
        okbtn.set_sensitive(not self.db.readonly)
        okbtn.connect('clicked',self.on_name_edit_ok_clicked)

    def _setup_fields(self):
        self.group_as = MonitoredEntry(
            self.top.get_widget("group_as"), self.name.set_group_as,
            self.name.get_group_as, self.db.readonly)

        if not self.original_group_as:
            self.group_as.force_value(self.name.get_surname())
            
        self.sort_as = MonitoredMenu(
            self.top.get_widget('sort_as'),self.name.set_sort_as,
            self.name.get_sort_as,
            [(_('Default (based on locale'),RelLib.Name.DEF),
             (_('Given name Family name'), RelLib.Name.FNLN),
             (_('Family name Given Name'), RelLib.Name.LNFN)],
            self.db.readonly)

        self.display_as = MonitoredMenu(
            self.top.get_widget('display_as'),
            self.name.set_display_as, self.name.get_display_as,
            [(_('Default (based on locale'),RelLib.Name.DEF),
             (_('Given name Family name'), RelLib.Name.FNLN),
             (_('Family name Given Name'), RelLib.Name.LNFN)],
            self.db.readonly)

        self.given_field = MonitoredEntry(
            self.top.get_widget("alt_given"), self.name.set_first_name,
            self.name.get_first_name, self.db.readonly)

        self.title_field = MonitoredEntry(
            self.top.get_widget("alt_title"), self.name.set_title,
            self.name.get_title, self.db.readonly)

        self.suffix_field = MonitoredEntry(
            self.top.get_widget("alt_suffix"), self.name.set_suffix,
            self.name.get_suffix, self.db.readonly)

        self.patronymic_field = MonitoredEntry(
            self.top.get_widget("patronymic"), self.name.set_patronymic,
            self.name.get_patronymic, self.db.readonly)

        self.surname_field = MonitoredEntry(
            self.top.get_widget("alt_surname"), self.name.set_surname,
            self.name.get_surname, self.db.readonly,
            self.update_group_as)

        self.prefix_field = MonitoredEntry(
            self.top.get_widget("alt_prefix"), self.name.set_surname_prefix,
            self.name.get_surname_prefix, self.db.readonly)
            
        self.date = MonitoredDate(self.top.get_widget("date"),
                                  self.top.get_widget("date_stat"), 
                                  self.name.get_date_object(),self.window)

        self.name_combo = MonitoredType(
            self.top.get_widget("name_type"), self.name.set_type,
            self.name.get_type, dict(Utils.name_types), RelLib.Name.CUSTOM)
        
        self.privacy = PrivacyButton(
            self.top.get_widget("priv"), self.name)
        
    def _create_tabbed_pages(self):
        self.srcref_list = self._add_page(SourceEmbedList(
            self.dbstate,self.uistate, self.track,
            self.name.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            self.name.get_note_object()))

    def build_menu_names(self,name):
        if name:
            ntext = NameDisplay.displayer.display_name(name)
            submenu_label = _('%s: %s') % (_('Name'),ntext)
        else:
            submenu_label = _('New Name')
        menu_label = _('Name Editor')
        return (menu_label,submenu_label)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def update_group_as(self,obj):
        if not self.group_over.get_active():
            if self.name.get_group_as() != self.name.get_surname():
                val = self.name.get_group_as()
            else:
                name = self.name.get_surname()
                val = self.db.get_name_group_mapping(name)
            self.group_as.force_value(val)
        
    def on_group_over_toggled(self,obj):
        self.group_as.enable(obj.get_active())
        
        if not obj.get_active():
            field_value = self.name.get_surname()
            mapping = self.db.get_name_group_mapping(field_value)
            self.group_as.set_text(mapping)

    def on_delete_event(self,*obj):
        self.close()

    def close_window(self,*obj):
        self.close()
        self.window.destroy()
        gc.collect()

    def on_help_clicked(self,*obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-an')

    def on_name_edit_ok_clicked(self,obj):

        if not self.group_over.get_active():
            self.name.set_group_as("")
        elif self.name.get_group_as() == self.name.get_surname():
            self.name.set_group_as("")
        elif self.name.get_group_as() != self.original_group_as:
            grp_as = self.name.get_group_as()
            srn = self.name.get_surname()
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

        self.callback(self.name)
        self.close_window(obj)

        
