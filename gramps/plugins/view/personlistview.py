# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2010       Benny Malengier
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
Person list View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.plugins.lib.libpersonview import BasePersonView
from gramps.gui.views.treemodels.peoplemodel import PersonListModel

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PersonListView(BasePersonView):
    """
    A hierarchical view of the top three levels of places.
    """
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        BasePersonView.__init__(self, pdata, dbstate, uistate,
                               _('Person View'), PersonListModel,
                               nav_group=nav_group)
