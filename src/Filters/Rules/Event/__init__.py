#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Package providing filter rules for GRAMPS.
"""

from Filters.Rules._HasEventBase import HasEventBase as HasEvent

from _HasType import HasType
from _AllEvents import AllEvents
from _HasGallery import HasGallery
from _HasIdOf import HasIdOf
from _RegExpIdOf import RegExpIdOf
from _HasCitation import HasCitation
from _HasNote import HasNote
from _HasNoteRegexp import HasNoteRegexp
from _HasNoteMatchingSubstringOf import HasNoteMatchingSubstringOf
from _HasReferenceCountOf import HasReferenceCountOf
from _HasSourceCount import HasSourceCount
from _EventPrivate import EventPrivate
from _MatchesFilter import MatchesFilter
from _MatchesPersonFilter import MatchesPersonFilter
from _MatchesSourceConfidence import MatchesSourceConfidence
from _MatchesSourceFilter import MatchesSourceFilter
from _HasAttribute import HasAttribute
from _HasData import HasData
from _ChangedSince import ChangedSince
from _MatchesPlaceFilter import MatchesPlaceFilter

editor_rule_list = [
    AllEvents,
    HasType,
    HasIdOf,
    HasGallery,
    RegExpIdOf,
    HasCitation, 
    HasNote,
    HasNoteRegexp,
    HasNoteMatchingSubstringOf,
    HasReferenceCountOf,
    HasSourceCount,
    EventPrivate,
    MatchesFilter,
    MatchesPersonFilter,
    MatchesSourceConfidence,
    MatchesSourceFilter,
    HasAttribute,
    HasData,
    ChangedSince,
    MatchesPlaceFilter
]
