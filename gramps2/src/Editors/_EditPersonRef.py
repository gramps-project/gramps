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

# $Id: _EditPersonRef.py 6282 2006-04-06 22:02:46Z rshura $

"""
The EditPersonRef module provides the EditPersonRef class. This provides a
mechanism for the user to edit address information.
"""

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
import NameDisplay
from _EditSecondary import EditSecondary

from DisplayTabs import SourceEmbedList, NoteTab
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditPersonRef class
#
#-------------------------------------------------------------------------
class EditPersonRef(EditSecondary):
    """
    Displays a dialog that allows the user to edit an address.
    """

    WIDTH_KEY = Config.PERSON_REF_WIDTH
    HEIGHT_KEY = Config.PERSON_REF_HEIGHT

    def __init__(self, dbstate, uistate, track, addr, callback):
        """
        Displays the dialog box.

        parent - The class that called the PersonRef editor.
        addr - The address that is to be edited
        """
        EditSecondary.__init__(self, dbstate, uistate, track, addr, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "pref_edit","gramps")
        self.set_window(self.top.get_widget("pref_edit"),
                        self.top.get_widget("title"),
                        _('Person Reference Editor'))
        self.person_label = self.top.get_widget('person')

    def _setup_fields(self):

        if self.obj.ref:
            p = self.dbstate.db.get_person_from_handle(self.obj.ref)
            self.person_label.set_text(NameDisplay.displayer.display(p))
        
        self.street = MonitoredEntry(
            self.top.get_widget("relationship"),
            self.obj.set_relation,
            self.obj.get_relation,
            self.db.readonly)

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj,
            self.db.readonly)

    def _connect_signals(self):
        #self.define_help_button(self.top.get_widget('help'),'adv-ad')
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_ok_button(self.top.get_widget('ok'),self.save)
        self.top.get_widget('select').connect('clicked',self._select_person)

    def _select_person(self, obj):
        from Selectors import selector_factory
        SelectPerson = selector_factory('Person')

        sel = SelectPerson(self.dbstate, self.uistate, self.track)
        person = sel.run()

        if person:
            self.obj.ref = person.get_handle()
            self.person_label.set_text(NameDisplay.displayer.display(person))

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        
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

    def build_menu_names(self,obj):
        return (_('Person Reference'),_('Person Reference Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """

        if self.obj.ref:
            if self.callback:
                self.callback(self.obj)
            self.close()
        else:
            from QuestionDialog import ErrorDialog

            ErrorDialog(
                _('No person selected'),
                _('You must either select a person or Cancel '
                  'the edit'))

