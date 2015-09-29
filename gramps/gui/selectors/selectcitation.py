#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006 Donald N. Allingham
#               2009 Gary Burton 
# Copyright (C) 2011       Tim G L Lyons, Nick Hall
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
SelectCitation class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..views.treemodels import CitationTreeModel
from .baseselector import BaseSelector
from gramps.gui.display import display_help
from gramps.gen.const import URL_MANUAL_PAGE

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = _('%s_-_Entering_and_editing_data:_detailed_-_part_2') % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Select_Source_or_Citation_selector')

#-------------------------------------------------------------------------
#
# SelectSource
#
#-------------------------------------------------------------------------
class SelectCitation(BaseSelector):

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.width_key = 'interface.source-sel-width'
        self.height_key = 'interface.source-sel-height'

    def get_window_title(self):
        return _("Select Source or Citation")
        
    def get_model_class(self):
        return CitationTreeModel

    def get_column_titles(self):
        return [
            (_('Source: Title or Citation: Volume/Page'), 350, BaseSelector.TEXT, 0),
            (_('ID'),     75, BaseSelector.TEXT, 1),
            (_('Last Change'), 150, BaseSelector.TEXT, 6),
            ]

    def get_from_handle_func(self):
        return self.db.get_source_from_handle
        
    def get_from_handle_func2(self):
        return self.db.get_citation_from_handle
