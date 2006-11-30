#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: __init__.py 6521 2006-05-03 01:02:54Z rshura $

"""
Package providing filter rules for GRAMPS.
"""

__author__ = "Don Allingham"

from _SearchFatherName import SearchFatherName
from _SearchMotherName import SearchMotherName
from _SearchChildName import SearchChildName

from _HasRelType import HasRelType
from _AllFamilies import AllFamilies
from _HasIdOf import HasIdOf
from _RegExpIdOf import RegExpIdOf
from _HasNoteRegexp import HasNoteRegexp
from _HasNoteMatchingSubstringOf import HasNoteMatchingSubstringOf
from _FamilyPrivate import FamilyPrivate
from _HasAttribute import HasAttribute
from _HasEvent import HasEvent
from _HasMarkerOf import HasMarkerOf
from _MatchesFilter import MatchesFilter
from _FatherHasNameOf import FatherHasNameOf
from _FatherHasIdOf import FatherHasIdOf
from _MotherHasNameOf import MotherHasNameOf
from _MotherHasIdOf import MotherHasIdOf
from _ChildHasNameOf import ChildHasNameOf
from _ChildHasIdOf import ChildHasIdOf

editor_rule_list = [
    AllFamilies,
    HasRelType,
    HasIdOf,
    RegExpIdOf,
    HasNoteRegexp,
    HasNoteMatchingSubstringOf,
    FamilyPrivate,
    HasEvent,
    HasAttribute,
    HasMarkerOf,
    MatchesFilter,
    FatherHasNameOf,
    FatherHasIdOf,
    MotherHasNameOf,
    MotherHasIdOf,
    ChildHasNameOf,
    ChildHasIdOf,
]
