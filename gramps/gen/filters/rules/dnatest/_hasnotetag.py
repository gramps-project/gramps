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
from .._hasnotetagbase import HasNoteTagBase

_ = glocale.translation.gettext


class HasNoteTag(HasNoteTagBase):
    """Rule that checks for DNA tests with a note with a specified tag."""

    name = _("DNA tests with a note with a tag of <tag>")
    description = _("Matches DNA tests with a note bearing a specified tag")
    category = _("Note filters")
