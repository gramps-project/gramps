#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
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

""" Dump Gender Statistics.

    Tools/Debug/Dump Gender Statistics
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gui.listmodel import ListModel, INTEGER
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.plug import tool

_GENDER = [_("female"), _("male"), _("unknown")]


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class DumpGenderStats(tool.Tool, ManagedWindow):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = _("Gender Statistics tool")
        tool.Tool.__init__(self, dbstate, options_class, name)

        stats_list = []
        for name, value in dbstate.db.genderStats.stats.items():
            stats_list.append(
                (name,) + value + (_GENDER[dbstate.db.genderStats.guess_gender(name)],)
            )

        if uistate:
            ManagedWindow.__init__(self, uistate, [], self.__class__)

            titles = [
                (_("Name"), 0, 100),
                (_("Male"), 1, 70, INTEGER),
                (_("Female"), 2, 70, INTEGER),
                (_("Unknown"), 3, 90, INTEGER),
                (_("Guess"), 4, 70),
            ]

            treeview = Gtk.TreeView()
            model = ListModel(treeview, titles)
            for entry in sorted(stats_list):
                model.add(entry, entry[0])

            s = Gtk.ScrolledWindow()
            s.add(treeview)
            dialog = Gtk.Dialog()
            dialog.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
            dialog.connect("response", self._response)
            dialog.vbox.pack_start(s, expand=True, fill=True, padding=0)
            self.set_window(dialog, None, self.label)
            self.setup_configs("interface.dumpgenderstats", 420, 300)
            self.show()

        else:
            if len(_("Name")) < 16:
                print(
                    "%s%s%s" % (_("Name"), " " * (16 - len(_("Name"))), _("Male")),
                    "\t%s" * 3 % (_("Female"), _("Unknown"), _("Guess")),
                )
            else:
                print(
                    _("Name"),
                    "\t%s" * 4 % (_("Male"), _("Female"), _("Unknown"), _("Guess")),
                )
            print()
            for entry in sorted(stats_list):
                if len(entry[0]) < 16:
                    print(
                        "%s%s%s" % (entry[0], " " * (16 - len(entry[0])), entry[1]),
                        "\t%s" * 3 % (entry[2:]),
                    )
                else:
                    print(entry[0], "\t%s" * 4 % (entry[1:]))

    def _response(self, obj, response_id):
        if response_id == Gtk.ResponseType.CLOSE:
            self.close()

    def build_menu_names(self, obj):
        return (self.label, None)


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class DumpGenderStatsOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
