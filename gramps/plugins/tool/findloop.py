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
from collections import OrderedDict

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
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.plug import tool
from gramps.gui.editors import EditFamily
from gramps.gen.errors import WindowActiveError
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.utils import ProgressMeter
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gen.display.name import displayer as _nd
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Find_database_loop', 'manual')


#------------------------------------------------------------------------
#
# FindLoop class
#
#------------------------------------------------------------------------
class FindLoop(ManagedWindow):
    """
    Find loops in the family tree.
    """
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        self.title = _('Find database loop')
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.dbstate = dbstate
        self.uistate = uistate
        #self.db = CacheProxyDb(dbstate.db)
        self.db = dbstate.db

        top_dialog = Glade()

        top_dialog.connect_signals({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_event"       : self.close,
        })

        window = top_dialog.toplevel
        title = top_dialog.get_object("title")
        self.set_window(window, title, self.title)

        # start the progress indicator
        self.progress = ProgressMeter(self.title, _('Starting'),
                                      parent=uistate.window)
        self.progress.set_pass(_('Looking for possible loop for each person'),
                               self.db.get_number_of_people())

        self.model = Gtk.ListStore(
            GObject.TYPE_STRING,    # 0==father id
            GObject.TYPE_STRING,    # 1==father
            GObject.TYPE_STRING,    # 2==son id
            GObject.TYPE_STRING,    # 3==son
            GObject.TYPE_STRING,    # 4==family gid
            GObject.TYPE_STRING)    # 5==loop number
        self.model.set_sort_column_id(
            Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, 0)

        self.treeview = top_dialog.get_object("treeview")
        self.treeview.set_model(self.model)
        col0 = Gtk.TreeViewColumn('',
                                  Gtk.CellRendererText(), text=5)
        col1 = Gtk.TreeViewColumn(_('Gramps ID'),
                                  Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_('Parent'),
                                  Gtk.CellRendererText(), text=1)
        col3 = Gtk.TreeViewColumn(_('Gramps ID'),
                                  Gtk.CellRendererText(), text=2)
        col4 = Gtk.TreeViewColumn(_('Child'),
                                  Gtk.CellRendererText(), text=3)
        col5 = Gtk.TreeViewColumn(_('Family ID'),
                                  Gtk.CellRendererText(), text=4)
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
        self.treeview.append_column(col0)
        self.treeview.append_column(col1)
        self.treeview.append_column(col2)
        self.treeview.append_column(col3)
        self.treeview.append_column(col4)
        self.treeview.append_column(col5)
        self.treeselection = self.treeview.get_selection()
        self.treeview.connect('row-activated', self.rowactivated_cb)

        self.curr_fam = None
        people = self.db.get_person_handles()
        self.total = len(people)  # total number of people to process.
        self.count = 0  # current number of people completely processed
        self.loop = 0  # Number of loops found for GUI

        pset = OrderedDict()
        # pset is the handle list of persons from the current start of
        # exploration path to the current limit.  The use of OrderedDict
        # allows us to use it as a LIFO during recursion, as well as makes for
        # quick lookup.  If we find a loop, pset provides a nice way to get
        # the loop path.
        self.done = set()
        # self.done is the handle set of people that have been fully explored
        # and do NOT have loops in the decendent tree.  We use this to avoid
        # repeating work when we encounter one of these during the search.
        for person_handle in people:
            person = self.db.get_person_from_handle(person_handle)
            self.current = person
            self.parent = None
            self.descendants(person_handle, pset)

        # close the progress bar
        self.progress.close()

        self.show()

    def descendants(self, person_handle, pset):
        """
        Find the descendants of a given person.
        Returns False if a loop for the person is NOT found, True if loop found
        We use the return value to ensure a person is not put on done list if
        part of a loop
        """
        if person_handle in self.done:
            return False  # We have already verified no loops for this one
        if person_handle in pset:
            # We found one loop.
            # person_handle is child, self.parent, self.curr_fam valid
            # see if it has already been put into display
            person = self.db.get_person_from_handle(person_handle)
            pers_id = person.get_gramps_id()
            pers_name = _nd.display(person)
            parent_id = self.parent.get_gramps_id()
            parent_name = _nd.display(self.parent)
            value = (parent_id, parent_name, pers_id, pers_name, self.curr_fam)
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
                    found = True  # This loop is in display model
                    break
            if not found:
                # Need to put loop in display model.
                self.loop += 1
                # place first node
                self.model.append(value + (str(self.loop),))
                state = 0
                # Now search for loop beginning.
                for hndl in pset.keys():
                    if hndl != person_handle and state == 0:
                        continue  # beginning not found
                    if state == 0:
                        state = 1  # found beginning, get first item to display
                        continue
                    # we have a good handle, now put item on display list
                    self.parent = person
                    person = self.db.get_person_from_handle(hndl)
                    # Get the family that is both parent/person
                    for fam_h in person.get_parent_family_handle_list():
                        if fam_h in self.parent.get_family_handle_list():
                            break
                    family = self.db.get_family_from_handle(fam_h)
                    fam_id = family.get_gramps_id()
                    pers_id = person.get_gramps_id()
                    pers_name = _nd.display(person)
                    parent_id = self.parent.get_gramps_id()
                    parent_name = _nd.display(self.parent)
                    value = (parent_id, parent_name, pers_id, pers_name,
                             fam_id, str(self.loop))
                    self.model.append(value)
            return True
        # We are not part of loop (yet) so search descendents
        person = self.db.get_person_from_handle(person_handle)
        # put in the pset path list for recursive calls to find
        pset[person_handle] = None
        loop = False
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if not family:
                # can happen with LivingProxyDb(PrivateProxyDb(db))
                continue
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                self.curr_fam = family.get_gramps_id()
                self.parent = person
                # if any descendants are part of loop, so is search person
                loop |= self.descendants(child_handle, pset)
        # we have completed search, we can pop the person off pset list
        person_handle, dummy = pset.popitem(last=True)

        if not loop:
            # person was not in loop, so add to done list and update progress
            self.done.add(person_handle)
            self.count += 1
            self.progress.set_header("%d/%d" % (self.count, self.total))
            self.progress.step()
            return False
        # person was in loop...
        return True

    def rowactivated_cb(self, treeview, path, column):
        """
        Called when a row is activated.
        """
        # first we need to check that the row corresponds to a person
        iter_ = self.model.get_iter(path)
        fam_id = self.model.get_value(iter_, 4)
        fam = self.dbstate.db.get_family_from_gramps_id(fam_id)
        if fam:
            try:
                EditFamily(self.dbstate, self.uistate, [], fam)
            except WindowActiveError:
                pass
            return True
        return False

    def on_help_clicked(self, obj):
        """
        Display the relevant portion of Gramps manual.
        """
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def close(self, *obj):
        ManagedWindow.close(self, *obj)

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
