# Copyright (C) 2026 Ian Davis
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

from ....const import GRAMPS_LOCALE as glocale
from ....db import Database
from .. import HasGrampsId

_ = glocale.translation.gettext


class HasIdOf(HasGrampsId):
    """Rule that checks for a DNA test with a specific Gramps ID"""

    name = _("DNA test with <Id>")
    description = _("Matches a DNA test with a specified Gramps ID")

    def prepare(self, db: Database, user):
        data = db._get_raw_dnatest_from_id_data(self.list[0])
        if data:
            self.selected_handles = set([data.handle])
        else:
            self.selected_handles = set([])
