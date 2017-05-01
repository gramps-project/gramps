#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2017-      Serge Noiraud
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

from ._allplaces import AllPlaces
from ._hascitation import HasCitation
from ._hasgallery import HasGallery
from ._hasidof import HasIdOf
from ._regexpidof import RegExpIdOf
from ._hasnote import HasNote
from ._hasnoteregexp import HasNoteRegexp
from ._hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from ._hasreferencecountof import HasReferenceCountOf
from ._hassourcecount import HasSourceCount
from ._hassourceof import HasSourceOf
from ._placeprivate import PlacePrivate
from ._matchesfilter import MatchesFilter
from ._hasplace import HasPlace
from ._hasdata import HasData
from ._hasnolatorlon import HasNoLatOrLon
from ._inlatlonneighborhood import InLatLonNeighborhood
from ._isenclosedby import IsEnclosedBy
from ._matcheseventfilter import MatchesEventFilter
from ._matchessourceconfidence import MatchesSourceConfidence
from ._changedsince import ChangedSince
from ._hastag import HasTag
from ._hastitle import HasTitle
from ._withinarea import WithinArea

editor_rule_list = [
    AllPlaces,
    HasCitation,
    HasGallery,
    HasIdOf,
    RegExpIdOf,
    HasNote,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSourceCount,
    HasSourceOf,
    PlacePrivate,
    MatchesFilter,
    MatchesSourceConfidence,
    HasData,
    HasNoLatOrLon,
    InLatLonNeighborhood,
    MatchesEventFilter,
    ChangedSince,
    HasTag,
    HasTitle,
    WithinArea,
    IsEnclosedBy
]
