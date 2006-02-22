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

"""
The AttrEdit module provides the AttributeEditor class. This provides a
mechanism for the user to edit attribute information.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python modules
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
import RelLib
import GrampsDisplay
import DisplayState

from QuestionDialog import WarningDialog
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor(DisplayState.ManagedWindow):
    """
    Displays a dialog that allows the user to edit an attribute.
    """
    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """

        self.db = state.db
        self.attrib = attrib
        self.callback = callback
        self.track = track
        self.uistate = uistate
        self.state = state
        self.alist = data_list

        DisplayState.ManagedWindow.__init__(self, uistate, track, attrib)
        if self.already_exist:
            return

        if not attrib:
            self.attrib = RelLib.Attribute()

        self.top = gtk.glade.XML(const.gladeFile, "attr_edit","gramps")
        self.notebook = self.top.get_widget("notebook")

        self.window = self.top.get_widget("attr_edit")
        title = _("Attribute Editor")
        l = self.top.get_widget("title")
        Utils.set_titles(self.window,l,title,_('Attribute Editor'))
            
        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.window.connect('delete_event', self.on_delete_event)
        
        self.top.get_widget('cancel').connect('clicked', self.close_window)
        self.top.get_widget('help').connect('clicked', self.on_help_clicked)

        ok = self.top.get_widget('ok')
        ok.connect('clicked', self.on_ok_clicked)
        if self.db.readonly:
            ok.set_sensitive(False)

    def _setup_fields(self):
        self.value_field = MonitoredEntry(
            self.top.get_widget("attr_value"),
            self.attrib.set_value, self.attrib.get_value,
            self.db.readonly)
        
        self.priv = PrivacyButton(self.top.get_widget("private"),self.attrib)

        self.type_selector = MonitoredType(
            self.top.get_widget("attr_menu"),
            self.attrib.set_type, self.attrib.get_type,
            dict(Utils.personal_attributes),
            RelLib.Attribute.CUSTOM)

    def _create_tabbed_pages(self):
        vbox = self.top.get_widget('vbox')
        
        self.notebook = gtk.Notebook()
        self.srcref_list = self._add_page(SourceEmbedList(
            self.state,self.uistate, self.track,
            self.attrib.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.state, self.uistate, self.track,
            self.attrib.get_note_object()))
        self.notebook.show_all()
        vbox.pack_start(self.notebook,True)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def on_delete_event(self,obj,b):
        self.close()

    def close_window(self,obj):
        self.close()

    def build_menu_names(self, attrib):
        if not attrib:
            label = _("New Attribute")
        else:
            label = attrib.get_type()[1]
        if not label.strip():
            label = _("New Attribute")
        label = "%s: %s" % (_('Attribute'),label)
        return (label, _('Attribute Editor'))

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-at')

    def on_ok_clicked(self,obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """

        attr_data = self.attrib.get_type()
        if (attr_data[0] == RelLib.Attribute.CUSTOM and
            not attr_data[1] in self.alist):
            WarningDialog(
                _('New attribute type created'),
                _('The "%s" attribute type has been added to this database.\n'
                  'It will now appear in the attribute menus for this database') % attr_data[1])
            self.alist.append(attr_data[1])
            self.alist.sort()

        self.callback(self.attrib)
        self.close_window(obj)

