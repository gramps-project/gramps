#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Tools/Database Processing/Fix Capitalization of Family Names"""

# -------------------------------------------------------------------------
#
# gnome/gtk
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import find_surname_name, DbTxn
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.utils import ProgressMeter
from gramps.gui.display import display_help
from gramps.gui.managedwindow import ManagedWindow

from gramps.gui.dialog import OkDialog
from gramps.gui.plug import tool
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gui.glade import Glade

# -------------------------------------------------------------------------
#
# constants
#
# -------------------------------------------------------------------------

prefix_list = [
    "de",
    "van",
    "von",
    "di",
    "le",
    "du",
    "dela",
    "della",
    "des",
    "vande",
    "ten",
    "da",
    "af",
    "den",
    "das",
    "dello",
    "del",
    "en",
    "ein",
    "el" "et",
    "les",
    "lo",
    "los",
    "un",
    "um",
    "una",
    "uno",
]

WIKI_HELP_PAGE = "%s_-_Tools" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Fix_Capitalization_of_Family_Names", "manual")


# -------------------------------------------------------------------------
#
# ChangeNames
#
# -------------------------------------------------------------------------
class ChangeNames(tool.BatchTool, ManagedWindow):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = _("Capitalization changes")
        self.cb = callback

        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(Gtk.Window(), Gtk.Label(), "")

        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if self.fail:
            return

        self.progress = ProgressMeter(
            _("Checking Family Names"), "", parent=uistate.window
        )
        self.progress.set_pass(
            _("Searching family names"), len(self.db.get_surname_list())
        )
        self.name_list = []

        for name in self.db.get_surname_list():
            name.strip()
            namesplitSP = name.split()
            lSP = len(namesplitSP)
            namesplitHY = name.split("-")
            lHY = len(namesplitHY)
            if lSP == lHY == 1:
                if name != name.capitalize():
                    # Single surname without hyphen(s)
                    self.name_list.append(name)
            # if lSP == 1 and lHY > 1:
            # print "LSP==1", name, name.capitalize()
            # if name != name.capitalize():
            # Single surname with hyphen(s)
            # self.name_list.append(name)
            if lSP > 1 and lHY == 1:
                # more than one string in surname but no hyphen
                # check if first string is in prefix_list, if so test for cap in rest
                s1 = 0
                if namesplitSP[0].lower() in prefix_list:
                    s1 = 1
                for x in range(len(namesplitSP) - s1):
                    # check if any subsurname is not cap
                    notcap = False
                    if namesplitSP[s1 + x] != namesplitSP[s1 + x].capitalize():
                        notcap = True
                        break
                if notcap:
                    # Multiple surnames possibly after prefix
                    self.name_list.append(name)
            if lHY > 1:
                # more than one string in surname but hyphen(s) exists
                # check if first string is in prefix_list, if so test for cap
                if namesplitSP[0].lower() in prefix_list:
                    namesplitHY[0] = namesplitHY[0].replace(namesplitSP[0], "").strip()
                for x in range(len(namesplitHY)):
                    # check if any subsurname is not cap
                    notcap = False
                    if namesplitHY[x] != namesplitHY[x].capitalize():
                        notcap = True
                        break
                if notcap:
                    # Multiple surnames possibly after frefix
                    self.name_list.append(name)

            if uistate:
                self.progress.step()

        if self.name_list:
            self.display()
        else:
            self.progress.close()
            self.close()
            OkDialog(
                _("No modifications made"),
                _("No capitalization changes were detected."),
                parent=uistate.window,
            )

    def name_cap(self, name):
        name.strip()
        namesplitSP = name.split()
        lSP = len(namesplitSP)
        lHY = len(name.split("-"))
        namesep = " "
        if lHY > 1:
            namesep = "-"
            namesplitSP = name.replace(namesep, " ").split()
            lSP = len(namesplitSP)
        if lSP == lHY == 1:
            # if name != name.capitalize():
            # Single surname without space(s) or hyphen(s), normal case
            return name.capitalize()
        else:
            # more than one string in surname but no hyphen
            # check if first string is in prefix_list, if so CAP the rest
            # Names like (von) Kohl(-)Brandt
            result = ""
            s1 = 0
            if namesplitSP[0].lower() in prefix_list:
                s1 = 1
                result = namesplitSP[0].lower() + " "
            for x in range(lSP - s1):
                # CAP all subsurnames
                result = result + namesplitSP[s1 + x].capitalize() + namesep
            return result[:-1]

    def display(self):
        self.top = Glade()
        window = self.top.toplevel
        self.top.connect_signals(
            {
                "destroy_passed_object": self.close,
                "on_ok_clicked": self.on_ok_clicked,
                "on_help_clicked": self.on_help_clicked,
                "on_delete_event": self.close,
            }
        )

        self.list = self.top.get_object("list")
        self.set_window(window, self.top.get_object("title"), self.label)
        self.setup_configs("interface.changenames", 500, 450)

        self.model = Gtk.ListStore(
            GObject.TYPE_BOOLEAN, GObject.TYPE_STRING, GObject.TYPE_STRING
        )

        r = Gtk.CellRendererToggle()
        r.connect("toggled", self.toggled)
        c = Gtk.TreeViewColumn(_("Select"), r, active=0)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(_("Original Name"), Gtk.CellRendererText(), text=1)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(
            _("Capitalization Change"), Gtk.CellRendererText(), text=2
        )
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.iter_list = []
        self.progress.set_pass(_("Building display"), len(self.name_list))
        for name in self.name_list:
            handle = self.model.append()
            self.model.set_value(handle, 0, True)
            self.model.set_value(handle, 1, name)
            namecap = self.name_cap(name)
            self.model.set_value(handle, 2, namecap)
            self.iter_list.append(handle)
            self.progress.step()
        self.progress.close()

        self.show()

    def toggled(self, cell, path_string):
        path = tuple(map(int, path_string.split(":")))
        row = self.model[path]
        row[0] = not row[0]

    def build_menu_names(self, obj):
        return (self.label, None)

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def on_ok_clicked(self, obj):
        with DbTxn(_("Capitalization changes"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            changelist = set(
                self.model.get_value(node, 1)
                for node in self.iter_list
                if self.model.get_value(node, 0)
            )

            # with self.db.get_person_cursor(update=True, commit=True) as cursor:
            #  for handle, data in cursor:
            for handle in self.db.get_person_handles(False):
                person = self.db.get_person_from_handle(handle)
                # person = Person(data)
                change = False
                for name in [person.get_primary_name()] + person.get_alternate_names():
                    sname = find_surname_name(handle, name.serialize())
                    if sname in changelist:
                        change = True
                        for surn in name.get_surname_list():
                            sname = self.name_cap(surn.get_surname())
                            surn.set_surname(sname)
                if change:
                    # cursor.update(handle, person.serialize())
                    self.db.commit_person(person, self.trans)

        self.db.enable_signals()
        self.db.request_rebuild()
        # FIXME: this probably needs to be removed, and bookmarks
        # should always be rebuilt on a commit_person via signals
        # self.parent.bookmarks.redraw()
        self.close()
        self.cb()


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class ChangeNamesOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
