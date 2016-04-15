#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009   Stephane Charette
# Copyright (C) 2016-       Serge Noiraud
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

"Find possible loop in a people descendance"

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.plug import tool
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gui.editors import EditPerson, EditFamily
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.utils import ProgressMeter
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gen.lib import Tag
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as _nd

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Find_database_loop')

#------------------------------------------------------------------------
#
# FindLoop class
#
#------------------------------------------------------------------------
class FindLoop(ManagedWindow) :

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        self.title = _('Find database loop')
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.dbstate = dbstate
        self.uistate = uistate
        self.db = dbstate.db

        topDialog = Glade()

        topDialog.connect_signals({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_event"       : self.close,
        })

        window = topDialog.toplevel
        title = topDialog.get_object("title")
        self.set_window(window, title, self.title)

        # start the progress indicator
        self.progress = ProgressMeter(self.title,_('Starting'),
                                      parent=self.window)
        self.progress.set_pass(_('Looking for possible loop for each person'),
                               self.db.get_number_of_people())

        self.model = Gtk.ListStore(
            GObject.TYPE_STRING,    # 0==father id
            GObject.TYPE_STRING,    # 1==father
            GObject.TYPE_STRING,    # 2==son id
            GObject.TYPE_STRING,    # 3==son
            GObject.TYPE_STRING)    # 4==family gid

        self.treeView = topDialog.get_object("treeview")
        self.treeView.set_model(self.model)
        col1 = Gtk.TreeViewColumn(_('Gramps ID'),     Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_('Ancestor'),   Gtk.CellRendererText(), text=1)
        col3 = Gtk.TreeViewColumn(_('Gramps ID'),     Gtk.CellRendererText(), text=2)
        col4 = Gtk.TreeViewColumn(_('Descendant'),     Gtk.CellRendererText(), text=3)
        col5 = Gtk.TreeViewColumn(_('Family ID'), Gtk.CellRendererText(), text=4)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col3.set_resizable(True)
        col4.set_resizable(True)
        col5.set_resizable(True)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col4.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col5.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        col3.set_sort_column_id(2)
        col4.set_sort_column_id(3)
        col5.set_sort_column_id(4)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.treeView.append_column(col3)
        self.treeView.append_column(col4)
        self.treeView.append_column(col5)
        self.treeSelection = self.treeView.get_selection()
        self.treeView.connect('row-activated', self.rowactivated)

        people = self.db.get_person_handles()
        count = 0
        for person_handle in people:
            person = self.db.get_person_from_handle(person_handle)
            count += 1
            self.current = person
            self.parent = None
            self.descendants(person_handle, set())
            self.progress.set_header("%d/%d" % (count, len(people)))
            self.progress.step()

        # close the progress bar
        self.progress.close()

        self.show()

    def descendants(self, person_handle, new_list):
        person = self.db.get_person_from_handle(person_handle)
        pset = set()
        for item in new_list:
            pset.add(item)
        if person.handle in pset:
            # We found one loop
            father_id = self.current.get_gramps_id()
            father = _nd.display(self.current)
            son_id = self.parent.get_gramps_id()
            son = _nd.display(self.parent)
            value = (father_id, father, son_id, son, self.curr_fam)
            found = False
            for pth in range(len(self.model)):
                path = Gtk.TreePath(pth)
                treeiter = self.model.get_iter(path)
                find = (self.model.get_value(treeiter, 0),
                        self.model.get_value(treeiter, 1),
                        self.model.get_value(treeiter, 2),
                        self.model.get_value(treeiter, 3),
                        self.model.get_value(treeiter, 4))
                if find == value:
                    found = True
            if not found:
                self.model.append(value)
            return
        pset.add(person.handle)
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            self.curr_fam = family.get_gramps_id()
            if not family:
                # can happen with LivingProxyDb(PrivateProxyDb(db))
                continue
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                self.parent = person
                self.descendants(child_handle, pset)

    def rowactivated(self, treeView, path, column) :
        # first we need to check that the row corresponds to a person
        iter = self.model.get_iter(path)
        From_id = self.model.get_value(iter, 0)
        To_id = self.model.get_value(iter, 2)
        Fam_id = self.model.get_value(iter, 4)
        fam = self.dbstate.db.get_family_from_gramps_id(Fam_id)
        if fam:
            try:
                EditFamily(self.dbstate, self.uistate, [], fam)
            except WindowActiveError:
                pass
            return True
        return False

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def close(self, *obj):
        ManagedWindow.close(self,*obj)

#------------------------------------------------------------------------
#
# FindLoopOptions
#
#------------------------------------------------------------------------
class FindLoopOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        """ Initialize the options class """
        tool.ToolOptions.__init__(self, name, person_id)
