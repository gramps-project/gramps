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
DNA test types.
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
# DNATestType
#
# -------------------------------------------------------------------------
class DNATestType(GrampsType):
    """
    Class encapsulating the type of DNA test.
    """

    UNKNOWN = -1
    CUSTOM = 0
    AUTOSOMAL = 1
    YDNA_12 = 2
    YDNA_37 = 3
    YDNA_67 = 4
    YDNA_111 = 5
    BIGY = 6
    MTDNA_HVR1 = 7
    MTDNA_FULL = 8

    _CUSTOM = CUSTOM
    _DEFAULT = AUTOSOMAL

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (AUTOSOMAL, _("Autosomal"), "Autosomal"),
        (YDNA_12, _("Y-DNA 12"), "Y-DNA 12"),
        (YDNA_37, _("Y-DNA 37"), "Y-DNA 37"),
        (YDNA_67, _("Y-DNA 67"), "Y-DNA 67"),
        (YDNA_111, _("Y-DNA 111"), "Y-DNA 111"),
        (BIGY, _("Big Y"), "Big Y"),
        (MTDNA_HVR1, _("mtDNA HVR1"), "mtDNA HVR1"),
        (MTDNA_FULL, _("mtDNA Full"), "mtDNA Full"),
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
