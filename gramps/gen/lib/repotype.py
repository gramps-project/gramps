#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Repository types.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class RepositoryType(GrampsType):

    UNKNOWN = -1
    CUSTOM = 0
    LIBRARY = 1
    CEMETERY = 2
    CHURCH = 3
    ARCHIVE = 4
    ALBUM = 5
    WEBSITE = 6
    BOOKSTORE = 7
    COLLECTION = 8
    SAFE = 9

    _CUSTOM = CUSTOM
    _DEFAULT = LIBRARY

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (LIBRARY, _("Library"), "Library"),
        (CEMETERY, _("Cemetery"), "Cemetery"),
        (CHURCH, _("Church"), "Church"),
        (ARCHIVE, _("Archive"), "Archive"),
        (ALBUM, _("Album"), "Album"),
        (WEBSITE, _("Web site"), "Web site"),
        (BOOKSTORE, _("Bookstore"), "Bookstore"),
        (COLLECTION, _("Collection"), "Collection"),
        (SAFE, _("Safe"), "Safe"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
