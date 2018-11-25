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
SelectCitation class for Gramps.
"""

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..views.treemodels import CitationTreeModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

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
        self.setup_configs('interface.source-sel', 600, 450)

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
        return self.get_source_or_citation

    def get_source_or_citation(self, handle):
        if self.db.has_source_handle(handle):
            return self.db.get_source_from_handle(handle)
        else:
            return self.db.get_citation_from_handle(handle)

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _('manual|Select_Source_or_Citation_selector')
