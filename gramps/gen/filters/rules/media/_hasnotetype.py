#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025      Steve Youngs
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
# Standard Python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .._hasnotetypebase import HasNoteTypeBase


# -------------------------------------------------------------------------
# "Media having notes"
# -------------------------------------------------------------------------
class HasNoteType(HasNoteTypeBase):
    """Media with a note of the specified type"""

    name = _("Media with a note of type <type>")
    description = _("Matches media with a note of a specified type")
    category = _("Note filters")
