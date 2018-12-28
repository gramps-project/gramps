# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("gui.widgets.reorderfam")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.db import DbTxn
from gramps.gen.const import URL_MANUAL_PAGE
from ..listmodel import ListModel
from ..display import display_help
from ..managedwindow import ManagedWindow
from ..glade import Glade
from gramps.gen.display.name import displayer as name_displayer

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Categories"
WIKI_HELP_SEC = _('manual|Reorder_Relationships_dialog')


#-------------------------------------------------------------------------
#
# Reorder class
#
#-------------------------------------------------------------------------

class Reorder(ManagedWindow):
    """
    Interface to reorder the families a person is parent in
    """

    def __init__(self, state, uistate, track, handle):
        xml = Glade('reorder.glade')
        top = xml.toplevel

        self.dbstate = state
        ManagedWindow.__init__(self, uistate, track, self)

        self.person = self.dbstate.db.get_person_from_handle(handle)
        self.parent_list = self.person.get_parent_family_handle_list()
        self.family_list = self.person.get_family_handle_list()

        penable = len(self.parent_list) > 1
        fenable = len(self.family_list) > 1

        self.set_window(top, None, _("Reorder Relationships"))
        self.setup_configs('interface.reorder', 500, 400)

        self.ptree = xml.get_object('ptree')
        self.pmodel = ListModel(self.ptree,
                               [(_('Father'), -1, 200),
                                (_('Mother'), -1, 200),
                                ('', -1, 0)])

        self.ftree = xml.get_object('ftree')
        self.fmodel = ListModel(self.ftree,
                               [(_('Spouse'), -1, 200),
                                (_('Relationship'), -1, 200),
                                ('', -1, 0)])

        xml.get_object('ok').connect('clicked', self.ok_clicked)
        xml.get_object('cancel').connect('clicked', self.cancel_clicked)
        xml.get_object('help').connect(
            'clicked', lambda x: display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC))
        fup = xml.get_object('fup')
        fup.connect('clicked', self.fup_clicked)
        fup.set_sensitive(fenable)

        fdown = xml.get_object('fdown')
        fdown.connect('clicked', self.fdown_clicked)
        fdown.set_sensitive(fenable)

        pup = xml.get_object('pup')
        pup.connect('clicked', self.pup_clicked)
        pup.set_sensitive(penable)

        pdown = xml.get_object('pdown')
        pdown.connect('clicked', self.pdown_clicked)
        pdown.set_sensitive(penable)

        self.fill_data()

        self.show()

    def fill_data(self):
        self.fill_parents()
        self.fill_family()

    def fill_parents(self):
        for handle in self.parent_list:
            family = self.dbstate.db.get_family_from_handle(handle)
            fhandle = family.get_father_handle()
            mhandle = family.get_mother_handle()

            fname = ""
            if fhandle:
                father = self.dbstate.db.get_person_from_handle(fhandle)
                if father:
                    fname = name_displayer.display(father)

            mname = ""
            if mhandle:
                mother = self.dbstate.db.get_person_from_handle(mhandle)
                if mother:
                    mname = name_displayer.display(mother)

            self.pmodel.add([fname, mname, handle])

    def fill_family(self):
        for handle in self.family_list:

            family = self.dbstate.db.get_family_from_handle(handle)
            fhandle = family.get_father_handle()
            mhandle = family.get_mother_handle()

            name = ""

            if fhandle and fhandle != self.person.handle:
                spouse = self.dbstate.db.get_person_from_handle(fhandle)
                if spouse:
                    name = name_displayer.display(spouse)
            elif mhandle:
                spouse = self.dbstate.db.get_person_from_handle(mhandle)
                if spouse:
                    name = name_displayer.display(spouse)

            reltype = str(family.get_relationship())

            self.fmodel.add([name, reltype, handle])

    def cancel_clicked(self, obj):
        self.close()

    def ok_clicked(self, obj):
        name = name_displayer.display(self.person)
        msg = _("Reorder Relationships: %s") % name
        with DbTxn(msg, self.dbstate.db) as trans:
            self.dbstate.db.commit_person(self.person, trans)

        self.close()

    def pup_clicked(self, obj):
        """Moves the current selection up one row"""
        row = self.pmodel.get_selected_row()
        if not row or row == -1:
            return
        store, the_iter = self.pmodel.get_selected()
        data = self.pmodel.get_data(the_iter, range(3))
        self.pmodel.remove(the_iter)
        self.pmodel.insert(row-1, data, None, 1)
        handle = self.parent_list.pop(row)
        self.parent_list.insert(row-1, handle)

    def pdown_clicked(self, obj):
        row = self.pmodel.get_selected_row()
        if row + 1 >= self.pmodel.count or row == -1:
            return
        store, the_iter = self.pmodel.get_selected()
        data = self.pmodel.get_data(the_iter, range(3))
        self.pmodel.remove(the_iter)
        self.pmodel.insert(row+1, data, None, 1)
        handle = self.parent_list.pop(row)
        self.parent_list.insert(row+1, handle)

    def fup_clicked(self, obj):
        row = self.fmodel.get_selected_row()
        if not row or row == -1:
            return
        store, the_iter = self.fmodel.get_selected()
        data = self.fmodel.get_data(the_iter, range(3))
        self.fmodel.remove(the_iter)
        self.fmodel.insert(row-1, data, None, 1)
        handle = self.family_list.pop(row)
        self.family_list.insert(row-1, handle)


    def fdown_clicked(self, obj):
        row = self.fmodel.get_selected_row()
        if row + 1 >= self.fmodel.count or row == -1:
            return
        store, the_iter = self.fmodel.get_selected()
        data = self.fmodel.get_data(the_iter, range(3))
        self.fmodel.remove(the_iter)
        self.fmodel.insert(row+1, data, None, 1)
        handle = self.family_list.pop(row)
        self.family_list.insert(row+1, handle)
