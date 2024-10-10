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
to here for possible "underload" from low-level implementations
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from functools import wraps

# -------------------------------------------------------------------------
#
# underloadable decorator
#
# -------------------------------------------------------------------------
def underloadable(func):
    """ Mark a method as allowing a lower-level implementation """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        method_name = func.__name__
        # Find the deepest method to underload
        # Start at lowest, work up, but not current instance:
        for cls in reversed(type(self).__mro__[1:]):
            super_method = getattr(cls, method_name, None)
            if super_method:
                # bottom level, don't call wrapper:
                if hasattr(super_method, "__wrapped__"):
                    return super_method.__wrapped__(self, *args, **kwargs)
                else:
                    return super_method(self, *args, **kwargs)
        # Nothing found in hierarchy, call this one:
        return func(self, *args, **kwargs)
    return wrapper

# -------------------------------------------------------------------------
#
# Business class
#
# -------------------------------------------------------------------------
class BusinessLogic():
    """
    Mixin for Database classes. Implements business logic in high-level
    object-based code. Each of these methods could be "underloaded"
    from a lower-level implementation for speed.
    """
    @underloadable
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
