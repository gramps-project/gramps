#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your ) any later version.
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
# gen/plug/menu/__init__.py
"""
The menu package for allowing plugins to specify options in a generic way.
"""

from ._menu import Menu
from ._option import Option
from ._string import StringOption
from ._color import ColorOption
from ._number import NumberOption
from ._text import TextOption
from ._boolean import BooleanOption
from ._enumeratedlist import EnumeratedListOption
from ._filter import FilterOption
from ._person import PersonOption
from ._family import FamilyOption
from ._note import NoteOption
from ._media import MediaOption
from ._personlist import PersonListOption
from ._placelist import PlaceListOption
from ._surnamecolor import SurnameColorOption
from ._destination import DestinationOption
from ._style import StyleOption
from ._booleanlist import BooleanListOption
