#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
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
Package providing filter rules for Gramps.
"""

from ._searchfathername import SearchFatherName
from ._searchmothername import SearchMotherName
from ._searchchildname import SearchChildName
from ._regexpfathername import RegExpFatherName
from ._regexpmothername import RegExpMotherName
from ._regexpchildname import RegExpChildName

from ._hasreltype import HasRelType
from ._allfamilies import AllFamilies
from ._hasgallery import HasGallery
from ._hasidof import HasIdOf
from ._haslds import HasLDS
from ._regexpidof import RegExpIdOf
from ._hasnote import HasNote
from ._hasnoteregexp import HasNoteRegexp
from ._hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from ._hassourcecount import HasSourceCount
from ._hassourceof import HasSourceOf
from ._hasreferencecountof import HasReferenceCountOf
from ._hascitation import HasCitation
from ._familyprivate import FamilyPrivate
from ._hasattribute import HasAttribute
from ._hasevent import HasEvent
from ._isbookmarked import IsBookmarked
from ._matchesfilter import MatchesFilter
from ._matchessourceconfidence import MatchesSourceConfidence
from ._fatherhasnameof import FatherHasNameOf
from ._fatherhasidof import FatherHasIdOf
from ._motherhasnameof import MotherHasNameOf
from ._motherhasidof import MotherHasIdOf
from ._childhasnameof import ChildHasNameOf
from ._childhasidof import ChildHasIdOf
from ._changedsince import ChangedSince
from ._hastag import HasTag
from ._hastwins import HasTwins
from ._isancestorof import IsAncestorOf
from ._isdescendantof import IsDescendantOf

editor_rule_list = [
    AllFamilies,
    HasRelType,
    HasGallery,
    HasIdOf,
    HasLDS,
    HasNote,
    RegExpIdOf,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSourceCount,
    HasSourceOf,
    HasCitation,
    FamilyPrivate,
    HasEvent,
    HasAttribute,
    IsBookmarked,
    MatchesFilter,
    MatchesSourceConfidence,
    FatherHasNameOf,
    FatherHasIdOf,
    MotherHasNameOf,
    MotherHasIdOf,
    ChildHasNameOf,
    ChildHasIdOf,
    ChangedSince,
    HasTag,
    HasTwins,
    IsAncestorOf,
    IsDescendantOf,
]
