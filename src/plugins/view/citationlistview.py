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
from gui.views.treemodels.citationlistmodel import CitationListModel
from gen.plug import CATEGORY_QR_SOURCE

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
    # The data items here have to correspond, in order, to the items in
    # src/giu.views/treemodels/citationlistmodel.py
    COL_TITLE_PAGE     =  0
    COL_ID             =  1
    COL_DATE           =  2
    COL_CONFIDENCE     =  3
    COL_CHAN           =  4    
    COL_SRC_TITLE      =  5
    COL_SRC_ID         =  6
    COL_SRC_AUTH       =  7
    COL_SRC_ABBR       =  8
    COL_SRC_PINFO      =  9
    COL_SRC_CHAN       = 10
    # name of the columns
    COLUMN_NAMES = [
        _('Title/Page'),
        _('ID'),
        _('Date'),
        _('Confidence'),
        _('Last Changed'),
        _('Source: Title'),
        _('Source: ID'),
        _('Source: Author'),
        _('Source: Abbreviation'),
        _('Source: Publication Information'),
        _('Source: Last Changed'),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TITLE_PAGE, COL_ID, COL_DATE,
                             COL_CONFIDENCE]),
        ('columns.rank', [COL_TITLE_PAGE, COL_ID, COL_DATE, COL_CONFIDENCE,
                          COL_CHAN, COL_SRC_TITLE, COL_SRC_ID, COL_SRC_AUTH,
                          COL_SRC_ABBR, COL_SRC_PINFO, COL_SRC_CHAN]),
        ('columns.size', [200, 75, 100, 100, 100, 200, 75, 75, 100, 150, 100])
        )    
    ADD_MSG = _("Add a new citation and a new source")
    ADD_SOURCE_MSG = _("Add a new source")
    ADD_CITATION_MSG = _("Add a new citation to an existing source")
    # Edit delete and merge messages are overridden for the tree view as 
    # they can apply to sources or citations
    EDIT_MSG = _("Edit the selected citation")
    DEL_MSG = _("Delete the selected citation")
    MERGE_MSG = _("Merge the selected citations")
    FILTER_TYPE = "Citation"
    QR_CATEGORY = CATEGORY_QR_SOURCE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        BaseCitationView.__init__(self, pdata, dbstate, uistate,
                               _('Citation View'), CitationListModel,
                               nav_group=nav_group)

