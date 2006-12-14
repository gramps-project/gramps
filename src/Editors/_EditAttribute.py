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

"""
The EditAttribute module provides the AttributeEditor class. This provides a
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
import Config
from _EditSecondary import EditSecondary

from DisplayTabs import SourceEmbedList, NoteTab
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditAttribute class
#
#-------------------------------------------------------------------------
class EditAttribute(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    WIDTH_KEY = Config.ATTR_WIDTH
    HEIGHT_KEY = Config.ATTR_HEIGHT

    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        self.alist = data_list
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "attr_edit","gramps")
        self.set_window(self.top.get_widget("attr_edit"),
                        self.top.get_widget('title'),
                        _('Attribute Editor'))

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'),'adv-at')
        self.define_ok_button(self.top.get_widget('ok'),self.save)

    def _setup_fields(self):
        self.value_field = MonitoredEntry(
            self.top.get_widget("attr_value"),
            self.obj.set_value, self.obj.get_value,
            self.db.readonly)
        
        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj, self.db.readonly)

        self.type_selector = MonitoredDataType(
            self.top.get_widget("attr_menu"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            custom_values=self.alist
            )

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,self.track,self.obj))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)
        
    def build_menu_names(self, attrib):
        if not attrib:
            label = _("New Attribute")
        else:
            label = str(attrib.get_type())
        if not label.strip():
            label = _("New Attribute")
        label = "%s: %s" % (_('Attribute'),label)
        return (label, _('Attribute Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """
        t = self.obj.get_type()
        
        if t.is_custom() and str(t) == '':
            from QuestionDialog import ErrorDialog
            ErrorDialog(
                _("Cannot save attribute"),
                _("The attribute type cannot be empty"))
            return
        if self.callback:
            self.callback(self.obj)
        self.close()

#-------------------------------------------------------------------------
#
# EditAttribute class
#
#-------------------------------------------------------------------------
class EditFamilyAttribute(EditAttribute):
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
        EditAttribute.__init__(self, state, uistate, track, attrib, title,
                               data_list, callback)
