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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Place View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.views.placebaseview import PlaceBaseView
from gui.views.treemodels import PlaceModel

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceView
#
#-------------------------------------------------------------------------
class PlaceView(PlaceBaseView):
    """
    Flat place view.  (Original code in PlaceBaseView).
    """
    def __init__(self, dbstate, uistate):
        PlaceBaseView.__init__(self, dbstate, uistate, _('Places'), PlaceModel)
