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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Package providing filter rules for GRAMPS.
"""

from .._hassourcebase import HasSourceBase as HasSource

from _allsources import AllSources
from _hasgallery import HasGallery
from _hasidof import HasIdOf
from _regexpidof import RegExpIdOf
from _hasnote import HasNote
from _hasnoteregexp import HasNoteRegexp
from _hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from _hasreferencecountof import HasReferenceCountOf
from _sourceprivate import SourcePrivate
from _matchesfilter import MatchesFilter
from _changedsince import ChangedSince
from _hasrepository import HasRepository
from _matchestitlesubstringof import MatchesTitleSubstringOf
from _hasrepositorycallnumberref import HasRepositoryCallNumberRef
from _matchesrepositoryfilter import MatchesRepositoryFilter

editor_rule_list = [
    AllSources,
    HasGallery,
    HasIdOf,
    RegExpIdOf,
    HasNote,
    HasNoteRegexp,
    HasNoteMatchingSubstringOf,
    HasReferenceCountOf,
    SourcePrivate,
    MatchesFilter,
    ChangedSince,
    HasRepository,
    MatchesTitleSubstringOf,
    HasRepositoryCallNumberRef,
    MatchesRepositoryFilter
]
