#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Thierry Vignaud
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
from .._hasnotattributebase import HasNotAttributeBase


# -------------------------------------------------------------------------
#
# HasNotAttribute
#
# -------------------------------------------------------------------------
class HasNotAttribute(HasNotAttributeBase):
    """Rule that checks for an event with a particular event attribute"""

    labels = [_("Event attribute:")]
    name = _("Events without the attribute <attribute>")
    description = _("Matches events without the event attribute")
