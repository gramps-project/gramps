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
Provide merge capabilities for DNA tests.
"""

from ..lib import DNAMatch
from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..errors import MergeError


# -------------------------------------------------------------------------
#
# MergeDNATestQuery
#
# -------------------------------------------------------------------------
class MergeDNATestQuery:
    """
    Create database query to merge two DNA tests.
    """

    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merge two DNA tests into a single record.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()
        self.phoenix.merge(self.titanic)
        with DbTxn(_("Merge DNA Tests"), self.database) as trans:
            self.database.commit_dnatest(self.phoenix, trans)
            for class_name, handle in self.database.find_backlink_handles(old_handle):
                if class_name == DNAMatch.__name__:
                    match = self.database.get_dnamatch_from_handle(handle)
                    assert match.has_handle_reference("DNATest", old_handle)
                    match.replace_handle_reference("DNATest", old_handle, new_handle)
                    self.database.commit_dnamatch(match, trans)
                else:
                    raise MergeError(
                        "Encountered object of type %s that has a DNATest reference."
                        % class_name
                    )
            self.database.remove_dnatest(old_handle, trans)
