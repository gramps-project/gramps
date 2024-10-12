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

# -------------------------------------------------------------------------
#
# Business class
#
# -------------------------------------------------------------------------
class BusinessLogic():
    """
    Mixin for Database classes. Implements business logic in high-level
    object-based code. 
    """
    def get_father_mother_handles_from_primary_family_from_person(
            self,
            handle=None,
            person=None
    ):
        """ High-level implementation """
        if handle:
            person = self.get_person_from_handle(handle)

        fam_id = person.get_main_parents_family_handle()
        if fam_id:
            fam = self.get_family_from_handle(fam_id)
            if fam:
                f_id = fam.get_father_handle()
                m_id = fam.get_mother_handle()
                return (f_id, m_id)

        return (None, None)
