# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009    Nick Hall
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
Place List View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.plugins.lib.libplaceview import PlaceBaseView
from gramps.gui.views.treemodels.placemodel import PlaceListModel

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PlaceListView
#
#-------------------------------------------------------------------------
class PlaceListView(PlaceBaseView):
    """
    Flat place view.  (Original code in PlaceBaseView).
    """
    def __init__(self, pdata, dbstate, uistate):
        PlaceBaseView.__init__(self, pdata, dbstate, uistate,
                               _('Place View'), PlaceListModel,
                               nav_group=0)
