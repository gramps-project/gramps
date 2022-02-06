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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Package providing filter rules for Gramps.
"""

from ._allmedia import AllMedia
from ._hasidof import HasIdOf
from ._regexpidof import RegExpIdOf
from ._hascitation import HasCitation
from ._hasnoteregexp import HasNoteRegexp
from ._hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from ._hasreferencecountof import HasReferenceCountOf
from ._hassourcecount import HasSourceCount
from ._hassourceof import HasSourceOf
from ._mediaprivate import MediaPrivate
from ._matchesfilter import MatchesFilter
from ._matchessourceconfidence import MatchesSourceConfidence
from ._hasmedia import HasMedia
from ._hasattribute import HasAttribute
from ._changedsince import ChangedSince
from ._hastag import HasTag

editor_rule_list = [
    AllMedia,
    HasCitation,
    HasIdOf,
    RegExpIdOf,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSourceCount,
    HasSourceOf,
    MediaPrivate,
    MatchesFilter,
    MatchesSourceConfidence,
    HasMedia,
    HasAttribute,
    ChangedSince,
    HasTag,
]
