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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: placetreeview.py 14176 2010-02-01 07:01:45Z bmcage $

"""
Person list View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.views.listview import LISTTREE
from libpersonview import BasePersonView
from gui.views.treemodels.peoplemodel import PersonListModel
import gen.lib
import Errors
from gui.editors import EditPerson

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PersonListView(BasePersonView):
    """
    A hierarchical view of the top three levels of places.
    """
    def __init__(self, dbstate, uistate, nav_group=0):
        BasePersonView.__init__(self, dbstate, uistate,
                               _('People List'), PersonListModel,
                               nav_group=nav_group)
