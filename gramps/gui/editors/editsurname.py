#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2011  Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2017       Paul Culley
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
EditSurname Dialog. Provide the interface to allow the Gramps program
to edit information about a particular Persons Surname.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from .. import widgets
from ..glade import Glade

from ..managedwindow import ManagedWindow
from ..display import display_help
from ..dbguielement import DbGUIElement
from gramps.gen.const import URL_MANUAL_SECT1

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1


class EditSurname(ManagedWindow, DbGUIElement):
    """
    The EditSurname dialog is derived from the EditSecondary class.

    It allows for the editing of the Surname object type of Person.

    """

    def __init__(self, dbstate, uistate, track, surname, callback=None):
        """
        Create an EditSurname window.

        Associate a surname with the window.

        """
        self.old_obj = surname.serialize()
        self.dbstate = dbstate
        self.uistate = uistate
        self.db = dbstate.db
        self.callback = callback
        self.sname = surname
        self.original = surname.serialize()
        ManagedWindow.__init__(self, uistate, track, surname, modal=True)
        DbGUIElement.__init__(self, self.db)
        self.top = Glade()

        self.set_window(self.top.toplevel, None, _("Surname Editor"))
        self.setup_configs('interface.surname', 375, 140)
        self._set_size()
        self._setup_fields()
        self._connect_signals()
        self.show()

    def build_window_key(self, obj):
        """ For ManagedWindow ID purposes """
        return id(obj)

    def _connect_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditSecondary).
        """
        self.top.get_object("cancel_btn").connect('clicked', self.canceledits)
        self.top.get_object("ok_btn").connect('clicked', self.save)
        self.top.get_object("help_btn").connect(
            'clicked', lambda x: display_help(WIKI_HELP_PAGE,
                                              _('manual|Editing_Surname')))

    def canceledits(self, *obj):
        """
        Undo the edits that happened on this secondary object
        """
        self.sname.unserialize(self.old_obj)
        self.close(obj)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('person-rebuild', self.canceledits)
        self._add_db_signal('person-delete', self.canceledits)

    def _setup_fields(self):
        """
        Connect the GrampsWidget objects to field in the interface.

        This allows the widgets to keep the data in the attached Person object
        up to date at all times, eliminating a lot of need in 'save' routine.

        """

        self.surname_field = widgets.MonitoredEntry(
            self.top.get_object("surname"),
            self.sname.set_surname,
            self.sname.get_surname,
            self.db.readonly,
            autolist=self.db.get_surname_list() if not self.db.readonly
            else [])

        self.prefix = widgets.MonitoredEntry(
            self.top.get_object("prefix"),
            self.sname.set_prefix,
            self.sname.get_prefix,
            self.db.readonly)

        self.connector = widgets.MonitoredEntry(
            self.top.get_object("connector"),
            self.sname.set_connector,
            self.sname.get_connector,
            self.db.readonly)

        self.ortype_field = widgets.MonitoredDataType(
            self.top.get_object("cmborigin"),
            self.sname.set_origintype,
            self.sname.get_origintype,
            self.db.readonly,
            self.db.get_origin_types())

    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Surname'), "")

    def save(self, *obj):
        """
        Save the data.
        """
        self.callback(self.sname)
        self._cleanup_callbacks()
        ManagedWindow.close(self)

    def close(self, *obj):
        """
        Here we revert to the original data and then close.
        """
        self.sname.unserialize(self.original)
        self.callback(self.sname)
        self._cleanup_callbacks()
        ManagedWindow.close(self)
