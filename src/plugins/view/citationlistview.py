# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton 
# Copyright (C) 2011       Tim G L Lyons
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
Citation List View
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from libcitationview import BaseCitationView
from gui.views.treemodels.citationmodel import CitationListModel

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _


#-------------------------------------------------------------------------
#
# CitationView
#
#-------------------------------------------------------------------------
class CitationListView(BaseCitationView):
    """
    A list view of citations.
    """
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        BaseCitationView.__init__(self, pdata, dbstate, uistate,
                               _('Citation View'), CitationListModel,
                               nav_group=nav_group)

