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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import Gtk
from gramps.gui.listmodel import ListModel, INTEGER
from gramps.gui.managedwindow import ManagedWindow

from gramps.gui.plug import tool

_GENDER = [ _('female'), _('male'), _('unknown') ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DumpGenderStats(tool.Tool, ManagedWindow):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = _("Gender Statistics tool")
        tool.Tool.__init__(self, dbstate, options_class, name)
        if uistate:
            ManagedWindow.__init__(self,uistate,[],
                                                 self.__class__)

        stats_list = []
        for name, value in dbstate.db.genderStats.stats.items():
            stats_list.append(
                (name,)
                + value
                + (_GENDER[dbstate.db.genderStats.guess_gender(name)],)
                )

        if uistate:
            titles = [
                (_('Name'),0,100),
                (_('Male'),1,70,INTEGER),
                (_('Female'),2,70,INTEGER),
                (_('Unknown'),3,70,INTEGER),
                (_('Guess'),4,70)
                ]

            treeview = Gtk.TreeView()
            model = ListModel(treeview, titles)
            for entry in stats_list:
                model.add(entry, entry[0])

            window = Gtk.Window()
            window.set_default_size(400, 300)
            s = Gtk.ScrolledWindow()
            s.add(treeview)
            window.add(s)
            window.show_all()
            self.set_window(window, None, self.label)
            self.show()

        else:
            print('\t%s'*5 % ('Name','Male','Female','Unknown','Guess'))
            print()
            for entry in stats_list:
                print('\t%s'*5 % entry)

    def build_menu_names(self, obj):
        return (self.label,None)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class DumpGenderStatsOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
