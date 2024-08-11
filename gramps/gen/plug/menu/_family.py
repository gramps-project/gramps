#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008       Gary Burton
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
Option class representing a family.
"""

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from . import StringOption


# -------------------------------------------------------------------------
#
# FamilyOption class
#
# -------------------------------------------------------------------------
class FamilyOption(StringOption):
    """
    This class describes an option that allows a family from the
    database to be selected.
    """

    def __init__(self, label):
        """
        :param label: A friendly label to be applied to this option.
            Example: "Center Family"
        :type label: string
        :param value: A Gramps ID of a family for this option.
            Example: "f11"
        :type value: string
        :return: nothing
        """
        StringOption.__init__(self, label, "")
