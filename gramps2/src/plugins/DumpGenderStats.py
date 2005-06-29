#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Martin Hawlisch, Donald N. Allingham
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

"Dump gender stats"

import gtk
import ListModel
_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def DumpGenderStatsPlugin(database,active_person,callback,parent=None):
    stats_list = []
    for name in database.genderStats.stats.keys():
        stats_list.append((name,)+database.genderStats.stats[name]+(_GENDER[database.genderStats.guess_gender(name)],))

    titles = [(_('Name'),1,100), (_('Male'),2,70),
              (_('Female'),3,70), ('Unknown',4,70), (_('Guess'),5,70) ]
    treeview = gtk.TreeView()
    model = ListModel.ListModel(treeview,titles)
    for entry in stats_list:
        model.add(entry,entry[0])
    w = gtk.Window()
    w.set_position(gtk.WIN_POS_MOUSE)
    w.set_default_size(400,300)
    s=gtk.ScrolledWindow()
    s.add(treeview)
    w.add(s)
    w.show_all()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    DumpGenderStatsPlugin,
    _("Dumps gender statistics"),
    category=_("Debug"),
    description=_("Will dump the statistics for the gender guessing from the first name.")
    )
