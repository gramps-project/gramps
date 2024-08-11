#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""Tools/Database Processing/Extract Information from Names"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import re

# -------------------------------------------------------------------------
#
# gnome/gtk
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.utils import ProgressMeter
from gramps.gui.plug import tool
from gramps.gui.dialog import OkDialog
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gen.lib import NameOriginType, Surname
from gramps.gen.db import DbTxn
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Tools" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Extract_Information_from_Names", "manual")

# -------------------------------------------------------------------------
#
# constants
#
# -------------------------------------------------------------------------

# List of possible surname prefixes. Notice that you must run the tool
# multiple times for prefixes such as "van der".
PREFIX_LIST = [
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
    "der",
    "ter",
    "te",
    "die",
]

CONNECTOR_LIST = [
    "e",
    "y",
]
CONNECTOR_LIST_NONSPLIT = ["de", "van"]

_title_re = re.compile(r"^ ([A-Za-z][A-Za-z]+\.) \s+ (.+) $", re.VERBOSE)
_nick_re = re.compile(r"(.+) \s* [(\"] (.+) [)\"]", re.VERBOSE)


# -------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.  Also, search for
# surname prefixes. If found, change the name entry and put the prefix in
# the name prefix field.
#
# -------------------------------------------------------------------------


class PatchNames(tool.BatchTool, ManagedWindow):
    titleid = 1
    nickid = 2
    pref1id = 3
    compid = 4

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = _("Name and title extraction tool")
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(Gtk.Window(), Gtk.Label(), "")

        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if self.fail:
            self.close()
            return

        winprefix = Gtk.Dialog(
            title=_("Default prefix and connector settings"),
            transient_for=self.uistate.window,
            modal=True,
            destroy_with_parent=True,
        )
        winprefix.add_button(_("_OK"), Gtk.ResponseType.ACCEPT)
        winprefix.vbox.set_spacing(5)
        hboxpref = Gtk.Box()
        label = Gtk.Label(label=_("Prefixes to search for:"))
        hboxpref.pack_start(label, False, False, 5)
        self.prefixbox = Gtk.Entry()
        self.prefixbox.set_text(", ".join(PREFIX_LIST))
        hboxpref.pack_start(self.prefixbox, True, True, 0)
        winprefix.vbox.pack_start(hboxpref, True, True, 0)
        hboxcon = Gtk.Box()
        label = Gtk.Label(label=_("Connectors splitting surnames:"))
        hboxcon.pack_start(label, False, False, 5)
        self.conbox = Gtk.Entry()
        self.conbox.set_text(", ".join(CONNECTOR_LIST))
        hboxcon.pack_start(self.conbox, True, True, 0)
        winprefix.vbox.pack_start(hboxcon, True, True, 0)
        hboxconns = Gtk.Box()
        label = Gtk.Label(label=_("Connectors not splitting surnames:"))
        hboxconns.pack_start(label, False, False, 5)
        self.connsbox = Gtk.Entry()
        self.connsbox.set_text(", ".join(CONNECTOR_LIST_NONSPLIT))
        hboxconns.pack_start(self.connsbox, True, True, 0)
        winprefix.vbox.pack_start(hboxconns, True, True, 0)
        winprefix.resize(700, 100)
        winprefix.show_all()

        response = winprefix.run()
        self.prefix_list = self.prefixbox.get_text().split(",")
        self.prefix_list = list(map(strip, self.prefix_list))
        self.prefixbox = None
        self.connector_list = self.conbox.get_text().split(",")
        self.connector_list = list(map(strip, self.connector_list))
        self.conbox = None
        self.connector_list_nonsplit = self.connsbox.get_text().split(",")
        self.connector_list_nonsplit = list(map(strip, self.connector_list_nonsplit))
        self.connsbox = None

        # Find a prefix in the first_name
        self._fn_prefix_re = re.compile(
            r"(\S+)\s+(%s)\s*$" % "|".join(self.prefix_list), re.IGNORECASE
        )

        # Find a prefix in the surname
        self._sn_prefix_re = re.compile(
            r"^\s*(%s)\s+(.+)" % "|".join(self.prefix_list), re.IGNORECASE
        )
        # Find a connector in the surname
        self._sn_con_re = re.compile(
            r"^\s*(.+)\s+(%s)\s+(.+)" % "|".join(self.connector_list), re.IGNORECASE
        )
        winprefix.destroy()

        self.cb = callback
        self.handle_to_action = {}

        self.progress = ProgressMeter(
            _("Extracting Information from Names"), "", parent=self.uistate.window
        )
        self.progress.set_pass(_("Analyzing names"), self.db.get_number_of_people())

        for person in self.db.iter_people():
            key = person.handle
            name = person.get_primary_name()
            first = name.get_first_name()
            sname = name.get_surname()

            old_prefix = []
            old_surn = []
            old_con = []
            old_prim = []
            old_orig = []
            for surn in name.get_surname_list():
                old_prefix.append(surn.get_prefix())
                old_surn.append(surn.get_surname())
                old_con.append(surn.get_connector())
                old_prim.append(surn.get_primary())
                old_orig.append(surn.get_origintype())

            if name.get_title():
                old_title = [name.get_title()]
            else:
                old_title = []
            new_title = []

            match = _title_re.match(first)
            while match:
                groups = match.groups()
                first = groups[1]
                new_title.append(groups[0])
                match = _title_re.match(first)
            matchnick = _nick_re.match(first)

            if new_title:
                titleval = (" ".join(old_title + new_title), first)
                if key in self.handle_to_action:
                    self.handle_to_action[key][self.titleid] = titleval
                else:
                    self.handle_to_action[key] = {self.titleid: titleval}
            elif matchnick:
                # we check for nick, which changes given name like title
                groups = matchnick.groups()
                nickval = (groups[0], groups[1])
                if key in self.handle_to_action:
                    self.handle_to_action[key][self.nickid] = nickval
                else:
                    self.handle_to_action[key] = {self.nickid: nickval}
            else:
                # Try to find the name prefix in the given name, also this
                # changes given name
                match = self._fn_prefix_re.match(first)
                if match:
                    groups = match.groups()
                    if old_prefix[0]:
                        # Put the found prefix before the old prefix
                        new_prefix = " ".join([groups[1], old_prefix[0]])
                    else:
                        new_prefix = groups[1]
                    pref1val = (groups[0], new_prefix, groups[1])
                    if key in self.handle_to_action:
                        self.handle_to_action[key][self.pref1id] = pref1val
                    else:
                        self.handle_to_action[key] = {self.pref1id: pref1val}

            # check for Gedcom import of compound surnames
            if len(old_surn) == 1 and old_con[0] == "":
                prefixes = old_prefix[0].split(",")
                surnames = old_surn[0].split(",")
                if len(prefixes) > 1 and len(prefixes) == len(surnames):
                    # assume a list of prefix and a list of surnames
                    prefixes = list(map(strip, prefixes))
                    surnames = list(map(strip, surnames))
                    primaries = [False] * len(prefixes)
                    primaries[0] = True
                    origs = []
                    for ind in range(len(prefixes)):
                        origs.append(NameOriginType())
                    origs[0] = old_orig[0]
                    compoundval = (
                        surnames,
                        prefixes,
                        [""] * len(prefixes),
                        primaries,
                        origs,
                    )
                    if key in self.handle_to_action:
                        self.handle_to_action[key][self.compid] = compoundval
                    else:
                        self.handle_to_action[key] = {self.compid: compoundval}
                    # we cannot check compound surnames, so continue the loop
                    continue

            # Next, try to split surname in compounds: prefix surname connector
            found = False
            new_prefix_list = []
            new_surname_list = []
            new_connector_list = []
            new_prim_list = []
            new_orig_list = []
            ind = 0
            cont = True
            for pref, surn, con, prim, orig in zip(
                old_prefix, old_surn, old_con, old_prim, old_orig
            ):
                surnval = surn.split()
                if surnval == []:
                    new_prefix_list.append(pref)
                    new_surname_list.append("")
                    new_connector_list.append(con)
                    new_prim_list.append(prim)
                    new_orig_list.append(orig)
                    cont = False
                    continue
                val = surnval.pop(0)
                while cont:
                    new_prefix_list.append(pref)
                    new_surname_list.append("")
                    new_connector_list.append(con)
                    new_prim_list.append(prim)
                    new_orig_list.append(orig)

                    while cont and (val.lower() in self.prefix_list):
                        found = True
                        if new_prefix_list[-1]:
                            new_prefix_list[-1] += " " + val
                        else:
                            new_prefix_list[-1] = val
                        try:
                            val = surnval.pop(0)
                        except IndexError:
                            val = ""
                            cont = False
                    # after prefix we have a surname
                    if cont:
                        new_surname_list[-1] = val
                        try:
                            val = surnval.pop(0)
                        except IndexError:
                            val = ""
                            cont = False
                    # if value after surname indicates continue, then continue
                    while cont and (val.lower() in self.connector_list_nonsplit):
                        # add this val to the current surname
                        new_surname_list[-1] += " " + val
                        try:
                            val = surnval.pop(0)
                        except IndexError:
                            val = ""
                            cont = False
                    # if previous is non-splitting connector, then add new val
                    # to current surname
                    if cont and (
                        new_surname_list[-1].split()[-1].lower()
                        in self.connector_list_nonsplit
                    ):
                        new_surname_list[-1] += " " + val
                        try:
                            val = surnval.pop(0)
                        except IndexError:
                            val = ""
                            cont = False
                    # if next is a connector, add it to the surname
                    if cont and val.lower() in self.connector_list:
                        found = True
                        if new_connector_list[-1]:
                            new_connector_list[-1] = " " + val
                        else:
                            new_connector_list[-1] = val
                        try:
                            val = surnval.pop(0)
                        except IndexError:
                            val = ""
                            cont = False
                    # initialize for a next surname in case there are still
                    # val
                    if cont:
                        found = True  # we split surname
                        pref = ""
                        con = ""
                        prim = False
                        orig = NameOriginType()
                ind += 1
            if found:
                compoundval = (
                    new_surname_list,
                    new_prefix_list,
                    new_connector_list,
                    new_prim_list,
                    new_orig_list,
                )
                if key in self.handle_to_action:
                    self.handle_to_action[key][self.compid] = compoundval
                else:
                    self.handle_to_action[key] = {self.compid: compoundval}

            self.progress.step()

        if self.handle_to_action:
            self.display()
        else:
            self.progress.close()
            self.close()
            OkDialog(
                _("No modifications made"),
                _("No titles, nicknames or prefixes were found"),
                parent=self.uistate.window,
            )

    def build_menu_names(self, obj):
        return (self.label, None)

    def toggled(self, cell, path_string):
        path = tuple(map(int, path_string.split(":")))
        row = self.model[path]
        row[0] = not row[0]
        self.model.row_changed(path, row.iter)

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
        self.setup_configs("interface.patchnames", 680, 400)

        self.model = Gtk.ListStore(
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )

        r = Gtk.CellRendererToggle()
        r.connect("toggled", self.toggled)
        c = Gtk.TreeViewColumn(_("Select"), r, active=0)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=1)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(_("Type"), Gtk.CellRendererText(), text=2)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(_("Value"), Gtk.CellRendererText(), text=3)
        self.list.append_column(c)

        c = Gtk.TreeViewColumn(_("Current Name"), Gtk.CellRendererText(), text=4)
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.nick_hash = {}
        self.title_hash = {}
        self.prefix1_hash = {}
        self.compound_hash = {}

        self.progress.set_pass(
            _("Building display"), len(list(self.handle_to_action.keys()))
        )

        for key, data in self.handle_to_action.items():
            p = self.db.get_person_from_handle(key)
            gid = p.get_gramps_id()
            if self.nickid in data:
                given, nick = data[self.nickid]
                handle = self.model.append()
                self.model.set_value(handle, 0, 1)
                self.model.set_value(handle, 1, gid)
                self.model.set_value(handle, 2, _("Nickname"))
                self.model.set_value(handle, 3, nick)
                self.model.set_value(handle, 4, p.get_primary_name().get_name())
                self.nick_hash[key] = handle

            if self.titleid in data:
                title, given = data[self.titleid]
                handle = self.model.append()
                self.model.set_value(handle, 0, 1)
                self.model.set_value(handle, 1, gid)
                self.model.set_value(handle, 2, _("Title", "Person"))
                self.model.set_value(handle, 3, title)
                self.model.set_value(handle, 4, p.get_primary_name().get_name())
                self.title_hash[key] = handle

            if self.pref1id in data:
                given, prefixtotal, new_prefix = data[self.pref1id]
                handle = self.model.append()
                self.model.set_value(handle, 0, 1)
                self.model.set_value(handle, 1, gid)
                self.model.set_value(handle, 2, _("Prefix in given name"))
                self.model.set_value(handle, 3, prefixtotal)
                self.model.set_value(handle, 4, p.get_primary_name().get_name())
                self.prefix1_hash[key] = handle

            if self.compid in data:
                surn_list, pref_list, con_list, prims, origs = data[self.compid]
                handle = self.model.append()
                self.model.set_value(handle, 0, 1)
                self.model.set_value(handle, 1, gid)
                self.model.set_value(handle, 2, _("Compound surname"))
                newval = ""
                for sur, pre, con in zip(surn_list, pref_list, con_list):
                    if newval:
                        newval += "-["
                    else:
                        newval = "["
                    newval += pre + "," + sur
                    if con:
                        newval += "," + con + "]"
                    else:
                        newval += "]"
                self.model.set_value(handle, 3, newval)
                self.model.set_value(handle, 4, p.get_primary_name().get_name())
                self.compound_hash[key] = handle

            self.progress.step()

        self.progress.close()
        self.show()

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def on_ok_clicked(self, obj):
        with DbTxn(_("Extract information from names"), self.db, batch=True) as trans:
            self.db.disable_signals()

            for key, data in self.handle_to_action.items():
                p = self.db.get_person_from_handle(key)
                if self.nickid in data:
                    modelhandle = self.nick_hash[key]
                    val = self.model.get_value(modelhandle, 0)
                    if val:
                        given, nick = data[self.nickid]
                        name = p.get_primary_name()
                        name.set_first_name(given.strip())
                        name.set_nick_name(nick.strip())

                if self.titleid in data:
                    modelhandle = self.title_hash[key]
                    val = self.model.get_value(modelhandle, 0)
                    if val:
                        title, given = data[self.titleid]
                        name = p.get_primary_name()
                        name.set_first_name(given.strip())
                        name.set_title(title.strip())

                if self.pref1id in data:
                    modelhandle = self.prefix1_hash[key]
                    val = self.model.get_value(modelhandle, 0)
                    if val:
                        given, prefixtotal, prefix = data[self.pref1id]
                        name = p.get_primary_name()
                        name.set_first_name(given.strip())
                        oldpref = name.get_surname_list()[0].get_prefix().strip()
                        if oldpref == "" or oldpref == prefix.strip():
                            name.get_surname_list()[0].set_prefix(prefix)
                        else:
                            name.get_surname_list()[0].set_prefix(
                                "%s %s" % (prefix, oldpref)
                            )

                if self.compid in data:
                    modelhandle = self.compound_hash[key]
                    val = self.model.get_value(modelhandle, 0)
                    if val:
                        surns, prefs, cons, prims, origs = data[self.compid]
                        name = p.get_primary_name()
                        new_surn_list = []
                        for surn, pref, con, prim, orig in zip(
                            surns, prefs, cons, prims, origs
                        ):
                            new_surn_list.append(Surname())
                            new_surn_list[-1].set_surname(surn.strip())
                            new_surn_list[-1].set_prefix(pref.strip())
                            new_surn_list[-1].set_connector(con.strip())
                            new_surn_list[-1].set_primary(prim)
                            new_surn_list[-1].set_origintype(orig)
                        name.set_surname_list(new_surn_list)

                self.db.commit_person(p, trans)

        self.db.enable_signals()
        self.db.request_rebuild()
        self.close()
        self.cb()


class PatchNamesOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)


def strip(arg):
    return arg.strip()
