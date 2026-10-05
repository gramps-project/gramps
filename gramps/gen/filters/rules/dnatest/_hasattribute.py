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
from ....lib.dnaattrtype import DNAAttributeType
from .._hasattributebase import HasAttributeBase

_ = glocale.translation.gettext


class HasAttribute(HasAttributeBase):
    """Rule that checks for a DNA test with a particular attribute"""

    attribute_class = DNAAttributeType
    labels = [_("DNA test attribute:"), _("Value:")]
    name = _("DNA tests with the attribute <attribute>")
    description = _("Matches DNA tests with the attribute of a particular value")
