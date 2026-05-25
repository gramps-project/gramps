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
from .._hasnoteregexbase import HasNoteRegexBase

_ = glocale.translation.gettext


class HasNoteRegexp(HasNoteRegexBase):
    name = _("DNA matches having notes containing <text>")
    description = _(
        "Matches DNA matches whose notes contain text matching a regular expression"
    )
    category = _("Note filters")
