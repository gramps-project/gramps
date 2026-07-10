#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Selector dialog for DNAMatch objects.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.const import URL_MANUAL_PAGE
from ..views.treemodels import DNAMatchModel
from .baseselector import BaseSelector


# -------------------------------------------------------------------------
#
# SelectDNAMatch
#
# -------------------------------------------------------------------------
class SelectDNAMatch(BaseSelector):
    """Dialog for selecting an existing DNAMatch record."""

    def _local_init(self):
        self.setup_configs("interface.dnamatch-sel", 600, 450)

    def get_window_title(self):
        return _("Select DNA Match")

    def get_model_class(self):
        return DNAMatchModel

    def get_column_titles(self):
        return [
            (_("Subject test"), 200, BaseSelector.TEXT, 1),
            (_("Match test"), 200, BaseSelector.TEXT, 2),
            (_("Shared cM"), 100, BaseSelector.TEXT, 3),
            (_("Segment count"), 100, BaseSelector.TEXT, 5),
            (_("ID"), 75, BaseSelector.TEXT, 0),
            (_("Tags"), 100, BaseSelector.TEXT, 10),
            (_("Last Changed"), 150, BaseSelector.TEXT, 11),
        ]

    def get_from_handle_func(self):
        return self.db.get_dnamatch_from_handle

    def get_config_name(self):
        return __name__

    WIKI_HELP_PAGE = URL_MANUAL_PAGE
    WIKI_HELP_SEC = _("Select_DNA_Match_selector", "manual")
