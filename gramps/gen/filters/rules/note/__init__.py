#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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

from ._allnotes import AllNotes
from ._hasidof import HasIdOf
from ._regexpidof import RegExpIdOf
from ._matchesregexpof import MatchesRegexpOf
from ._matchessubstringof import MatchesSubstringOf
from ._hasreferencecountof import HasReferenceCountOf
from ._noteprivate import NotePrivate
from ._matchesfilter import MatchesFilter
from ._hasnote import HasNote
from ._changedsince import ChangedSince
from ._hastag import HasTag
from ._hastype import HasType

editor_rule_list = [
    AllNotes,
    HasIdOf,
    RegExpIdOf,
    HasNote,
    MatchesRegexpOf,
    HasReferenceCountOf,
    NotePrivate,
    MatchesFilter,
    ChangedSince,
    HasTag,
    HasType,
]
