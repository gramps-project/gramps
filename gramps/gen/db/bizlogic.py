#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Douglas S. Blank <doug.blank@gmail.com>
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
Collection of business logic functions, moved from views
to here for possible overloading by low-level implementations
"""

import jsonpath_ng


# -------------------------------------------------------------------------
#
# Business class
#
# -------------------------------------------------------------------------
class BusinessLogic:
    """
    Mixin for Database classes. Implements business logic in high-level
    object-based code.
    """

    CACHE = {}

    def get_father_mother_handles_from_primary_family_from_person(
        self, handle=None, person=None
    ):
        if person:
            handle = person.handle

        fam_handle = self.extract_data(
            "person",
            handle,
            ["$.parent_family_list[0]"],
        )

        if fam_handle:
            f_handle, m_handle = self.extract_data(
                "family",
                fam_handle,
                ["$.father_handle", "$.mother_handle"],
            )
            return (f_handle, m_handle)
        return (None, None)

    def extract_data(self, table, handle, json_path_list):
        """
        Generic function that can handle jsonpath items in a list.
        """
        raw_func = self._get_table_func(table.title(), "raw_func")
        raw_data = raw_func(handle)
        results = []
        for json_path in json_path_list:
            if json_path not in self.CACHE:
                self.CACHE[json_path] = jsonpath_ng.parse(json_path)
            jsonpath_expr = self.CACHE[json_path]
            match = jsonpath_expr.find(raw_data)
            if match:
                results.append(match[0].value)
            else:
                results.append(None)
        return results
