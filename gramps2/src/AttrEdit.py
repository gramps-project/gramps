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
import Sources
import AutoComp
import RelLib
import Spell
import GrampsDisplay
import DisplayState

from QuestionDialog import WarningDialog
from WindowUtils import GladeIf
from DisplayTabs import *

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

        self.top = gtk.glade.XML(const.gladeFile, "attr_edit","gramps")
        self.value_field = self.top.get_widget("attr_value")
        self.attrib_menu = self.top.get_widget("attr_menu")
        self.source_field = self.top.get_widget("attr_source")
        self.priv = self.top.get_widget("priv")
        self.notebook = self.top.get_widget("notebook")

        self.window = self.top.get_widget("attr_edit")
        self.type_selector = AutoComp.StandardCustomSelector(
            Utils.personal_attributes,self.attrib_menu,
            RelLib.Attribute.CUSTOM,RelLib.Attribute.DESCRIPTION)
        
        if title == ", ":
            title = _("Attribute Editor")
        else:
            title = _("Attribute Editor for %s") % escape(title)
        l = self.top.get_widget("title")
        Utils.set_titles(self.window,l,title,_('Attribute Editor'))

        if attrib:
            self.type_selector.set_values(attrib.get_type())
            self.value_field.set_text(attrib.get_value())
            self.priv.set_active(attrib.get_privacy())
        else:
            self.attrib = RelLib.Attribute()
            
        self.gladeif = GladeIf(self.top)
        self.gladeif.connect('attr_edit','delete_event', self.on_delete_event)
        self.gladeif.connect('button116', 'clicked', self.close_window)
        self.gladeif.connect('button115', 'clicked', self.on_ok_clicked)
        self.gladeif.connect('button127', 'clicked', self.on_help_clicked)

        if self.db.readonly:
            w = self.top.get_widget("button115")
            w.set_sensitive(False)
            self.value_field.set_editable(False)
            self.attrib_menu.set_sensitive(False)

        self._create_tabbed_pages()
        self.show()

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
        self.gladeif.close()
        self.close()

    def close_window(self,obj):
        self.gladeif.close()
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
        attr_data = self.type_selector.get_values()
        value = unicode(self.value_field.get_text())

        priv = self.priv.get_active()

        if (attr_data[0] == RelLib.Attribute.CUSTOM and
            not attr_data[1] in self.alist):
            WarningDialog(
                _('New attribute type created'),
                _('The "%s" attribute type has been added to this database.\n'
                  'It will now appear in the attribute menus for this database') % attr_data[1])
            self.alist.append(attr_data[1])
            self.alist.sort()

        self.update(attr_data,value,note,format,priv)
        self.callback(self.attrib)
        self.close_window(obj)

    def check(self,get,set,data):
        """Compares a data item, updates if necessary, and sets the
        parents lists_changed flag"""
        if get() != data:
            set(data)
            
    def update(self,attr_data,value,note,format,priv):
        """Compares the data items, and updates if necessary"""
        self.check(self.attrib.get_type,self.attrib.set_type,attr_data)
        self.check(self.attrib.get_value,self.attrib.set_value,value)
        self.check(self.attrib.get_privacy,self.attrib.set_privacy,priv)
