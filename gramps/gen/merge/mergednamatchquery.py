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
Provide merge capabilities for DNA matches.
"""

from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# MergeDNAMatchQuery
#
# -------------------------------------------------------------------------
class MergeDNAMatchQuery:
    """
    Create database query to merge two DNA matches.
    """

    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merge two DNA matches into a single record.
        """
        old_handle = self.titanic.get_handle()
        self.phoenix.merge(self.titanic)
        with DbTxn(_("Merge DNA Matches"), self.database) as trans:
            self.database.commit_dnamatch(self.phoenix, trans)
            self.database.remove_dnamatch(old_handle, trans)
