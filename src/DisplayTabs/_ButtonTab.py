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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from GrampsWidgets import SimpleButton
from _GrampsTab import GrampsTab
import Errors

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class ButtonTab(GrampsTab):
    """
    This class derives from the base GrampsTab, yet is not a usable Tab. It
    serves as another base tab for classes which need an Add/Edit/Remove button
    combination.
    """

    _MSG = {
        'add'   : _('Add'),
        'del'   : _('Remove'),
        'edit'  : _('Edit'),
        'share' : _('Share'),
    }
    
    _ACCEL = {
        'add': 'Insert',
        'del': 'Delete',
        'edit': '<Control>E',
        'share': '<Control>S',
    }

    def __init__(self, dbstate, uistate, track, name, share_button=False):
        """
        Similar to the base class, except after Build
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        """
        GrampsTab.__init__(self,dbstate, uistate, track, name)
        self.tooltips = gtk.Tooltips()
        self.create_buttons(share_button)

    def create_buttons(self, share_button=False):
        """
        Creates a button box consisting of three buttons, one for Add,
        one for Edit, and one for Delete. This button box is then appended
        hbox (self).
        """
        self.add_btn  = SimpleButton(gtk.STOCK_ADD, self.add_button_clicked)
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)
        self.del_btn  = SimpleButton(gtk.STOCK_REMOVE, self.del_button_clicked)

        self.tooltips.set_tip(self.add_btn, self._MSG['add'])
        self.tooltips.set_tip(self.edit_btn, self._MSG['edit'])
        self.tooltips.set_tip(self.del_btn, self._MSG['del'])
        
        key, mod = gtk.accelerator_parse(self._ACCEL['add'])
        self.add_btn.add_accelerator('activate', self.accel_group, key, mod, gtk.ACCEL_VISIBLE)
        key, mod = gtk.accelerator_parse(self._ACCEL['edit'])
        self.edit_btn.add_accelerator('activate', self.accel_group, key, mod, gtk.ACCEL_VISIBLE)
        key, mod = gtk.accelerator_parse(self._ACCEL['del'])
        self.del_btn.add_accelerator('activate', self.accel_group, key, mod, gtk.ACCEL_VISIBLE)

        if share_button:
            self.share_btn = SimpleButton(gtk.STOCK_INDEX, self.share_button_clicked)
            self.tooltips.set_tip(self.share_btn, self._MSG['share'])
        else:
            self.share_btn = None

        if self.dbstate.db.readonly:
            self.add_btn.set_sensitive(False)
            self.del_btn.set_sensitive(False)
            if share_button:
                self.share_btn.set_sensitive(False)

        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.add_btn, False)
        if share_button:
            vbox.pack_start(self.share_btn, False)
        vbox.pack_start(self.edit_btn, False)
        vbox.pack_start(self.del_btn, False)
        vbox.show_all()
        self.pack_start(vbox, False)

    def double_click(self, obj, event):
        """
        Handles the double click on list. If the double click occurs,
        the Edit button handler is called
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            try:
                self.edit_button_clicked(obj)
            except Errors.WindowActiveError:
                pass

    def add_button_clicked(self, obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Add clicked"

    def share_button_clicked(self, obj):
        """
        Function called with the Add button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Share clicked"

    def del_button_clicked(self, obj):
        """
        Function called with the Delete button is clicked. This function
        should be overridden by the derived class.
        """
        print "Uncaught Delete clicked"

    def edit_button_clicked(self, obj):
        """
        Function called with the Edit button is clicked or the double
        click is caught. This function should be overridden by the derived
        class.
        """
        print "Uncaught Edit clicked"

    def _selection_changed(self, obj=None):
        """
        Attached to the selection's 'changed' signal. Checks
        to see if anything is selected. If it is, the edit and
        delete buttons are enabled, otherwise the are disabled.
        """
        # Comparing to None is important, as empty strings
        # and 0 can be returned
        if self.get_selected() != None:
            self.edit_btn.set_sensitive(True)
            if not self.dbstate.db.readonly:
                self.del_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            if not self.dbstate.db.readonly:
                self.del_btn.set_sensitive(False)
