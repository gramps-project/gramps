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
Genome build / reference assembly types.
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
# DNAGenomeBuildType
#
# -------------------------------------------------------------------------
class DNAGenomeBuildType(GrampsType):
    """
    Class encapsulating the genome reference assembly used by a DNA kit.

    Left at UNKNOWN for Y-DNA and mtDNA tests where coordinate space does
    not apply.
    """

    UNKNOWN = -1
    CUSTOM = 0
    GRCH37 = 1
    GRCH38 = 2

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (GRCH37, _("GRCh37"), "GRCh37"),
        (GRCH38, _("GRCh38"), "GRCh38"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
