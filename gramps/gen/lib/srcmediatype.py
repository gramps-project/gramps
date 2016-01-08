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
SourceMedia types.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class SourceMediaType(GrampsType):

    UNKNOWN = -1
    CUSTOM = 0
    AUDIO = 1
    BOOK = 2
    CARD = 3
    ELECTRONIC = 4
    FICHE = 5
    FILM = 6
    MAGAZINE = 7
    MANUSCRIPT = 8
    MAP = 9
    NEWSPAPER = 10
    PHOTO = 11
    TOMBSTONE = 12
    VIDEO = 13

    _CUSTOM = CUSTOM
    _DEFAULT = BOOK

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (AUDIO, _("Audio"), "Audio"),
        (BOOK, _("Book"), "Book"),
        (CARD, _("Card"), "Card"),
        (ELECTRONIC, _("Electronic"), "Electronic"),
        (FICHE, _("Fiche"), "Fiche"),
        (FILM, _("Film"), "Film"),
        (MAGAZINE, _("Magazine"), "Magazine"),
        (MANUSCRIPT, _("Manuscript"), "Manuscript"),
        (MAP, _("Map"), "Map"),
        (NEWSPAPER, _("Newspaper"), "Newspaper"),
        (PHOTO, _("Photo"), "Photo"),
        (TOMBSTONE, _("Tombstone"), "Tombstone"),
        (VIDEO, _("Video"), "Video"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
