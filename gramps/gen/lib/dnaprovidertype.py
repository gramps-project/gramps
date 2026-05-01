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
DNA testing provider types.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .grampstype import GrampsType

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DNAProviderType
#
# -------------------------------------------------------------------------
class DNAProviderType(GrampsType):
    """
    Class encapsulating the DNA testing provider.
    """

    UNKNOWN = -1
    CUSTOM = 0
    ANCESTRY = 1
    TWENTY_THREE_AND_ME = 2
    MYHERITAGE = 3
    FTDNA = 4
    GEDMATCH = 5
    LIVINGDNA = 6

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (ANCESTRY, _("AncestryDNA"), "AncestryDNA"),
        (TWENTY_THREE_AND_ME, _("23andMe"), "23andMe"),
        (MYHERITAGE, _("MyHeritage"), "MyHeritage"),
        (FTDNA, _("FTDNA"), "FTDNA"),
        (GEDMATCH, _("GEDmatch"), "GEDmatch"),
        (LIVINGDNA, _("LivingDNA"), "LivingDNA"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
