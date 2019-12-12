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

from ._hascitation import HasCitation
from ._allcitations import AllCitations
from ._changedsince import ChangedSince
from ._citationprivate import CitationPrivate
from ._hasattribute import HasAttribute
from ._hasgallery import HasGallery
from ._hasidof import HasIdOf
from ._hasnote import HasNote
from ._hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from ._hasnoteregexp import HasNoteRegexp
from ._hasreferencecountof import HasReferenceCountOf
from ._hassource import HasSource
from ._hassourceidof import HasSourceIdOf
from ._hassourcenoteregexp import HasSourceNoteRegexp
from ._matchesfilter import MatchesFilter
from ._matchespagesubstringof import MatchesPageSubstringOf
from ._matchesrepositoryfilter import MatchesRepositoryFilter
from ._matchessourcefilter import MatchesSourceFilter
from ._regexpidof import RegExpIdOf
from ._regexpsourceidof import RegExpSourceIdOf
from ._hastag import HasTag

editor_rule_list = [
    HasCitation,
    AllCitations,
    ChangedSince,
    CitationPrivate,
    HasAttribute,
    HasGallery,
    HasIdOf,
    HasNote,
    HasNoteRegexp,
    HasReferenceCountOf,
    HasSource,
    HasSourceIdOf,
    HasSourceNoteRegexp,
    MatchesFilter,
    MatchesPageSubstringOf,
    MatchesRepositoryFilter,
    MatchesSourceFilter,
    RegExpIdOf,
    RegExpSourceIdOf,
    HasTag
]
