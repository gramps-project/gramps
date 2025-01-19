#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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

# -------------------------------------------------------------------------
#
# internationalization
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..views.treemodels import FamilyModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_PAGE

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# SelectFamily
#
# -------------------------------------------------------------------------
class SelectFamily(BaseSelector):
    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs("interface.family-sel", 600, 450)

    def get_window_title(self):
        return _("Select Family")

    def get_model_class(self):
        return FamilyModel

    def get_column_titles(self):
        return [
            (_("ID"), 75, BaseSelector.TEXT, 0),
            (_("Father"), 200, BaseSelector.TEXT, 1),
            (_("Mother"), 200, BaseSelector.TEXT, 2),
            (_("Last Change"), 150, BaseSelector.TEXT, 7),
        ]

    def get_from_gramps_id_func(self):
        return self.db.get_family_from_gramps_id

    def get_from_handle_func(self):
        return self.db.get_family_from_handle

    def get_config_name(self):
        return __name__

    WIKI_HELP_PAGE = "%s_-_Categories" % URL_MANUAL_PAGE
    WIKI_HELP_SEC = _("Select_Family_selector", "manual")
