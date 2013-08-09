#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2011       Doug Blank <doug.blank@gmail.com>
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

The following filters are provided in Filters/Rules.

Match given values:
_HasCitationBase             Citation with a particular value (HasCitation)
                             also used for Person, Family and Event having a 
                             particular Citation
_HasEventBase                Event with a particular value (HasEvent)
                             also used for Family and Person having a particular
                             Event
_HasSourceBase               Source with a particular value (HasSource)
                             also used for Citation having a particular Source

Match on sub-objects
_ChangedSinceBase            Object changed since date
_HasAttributeBase            Object has particular attribute value
_HasGrampsId                 Object has a specific Gramps Id
_HasNoteRegexBase            Object has notes matching regular expression
_HasNoteSubstrBase           Object has note containing substring
_HasTagBase                  Object has a particular tag
_HasTextMatchingRegexpOf     Object has text matching regular expression
_HasTextMatchingSubstringOf  Object has text containing substring
_IsPrivate                   Object is marked as private
_IsPublic                    Object is not marked as private
_MatchesFilterBase           Object matches another filter
_RegExpldBase                Object has Gramps Id matching regular expression

Match on related objects
_MatchesFilterEventBase      Object has an event that matches another filter
_MatchesSourceConfidenceBase Object with specific confidence on direct sources
_MatchesSourceFilterBase     Object matches another filter on direct sources

Count based
_HasGalleryBase              Object has </>/= number of media objects
_HasLDSBase                  Object has </>/= number of LDS  sub-objects
_HasNoteBase                 Object has </>/= number of notes
_HasReferenceCountBase       Object has </>/= number of references
_HasSourceCountBase          Object has </>/= number of sources

_Rule                        Base rule class
_Everything                  Match every object in the database
"""

# Need to expose this to be available for filter plugins:
# the plugins should say: from Filters.Rules import Rule
from Filters.Rules._Rule import Rule

from Filters.Rules._Everything import Everything
from Filters.Rules._HasGrampsId import HasGrampsId
from Filters.Rules._RegExpIdBase import RegExpIdBase
from Filters.Rules._IsPrivate import IsPrivate
from Filters.Rules._IsPublic import IsPublic
from Filters.Rules._HasTextMatchingSubstringOf import HasTextMatchingSubstringOf
from Filters.Rules._HasTextMatchingRegexpOf import HasTextMatchingRegexpOf
from Filters.Rules._MatchesFilterBase import MatchesFilterBase
from Filters.Rules._MatchesEventFilterBase import MatchesEventFilterBase
from Filters.Rules._MatchesSourceConfidenceBase import MatchesSourceConfidenceBase
from Filters.Rules._MatchesSourceFilterBase import MatchesSourceFilterBase
from Filters.Rules._ChangedSinceBase import ChangedSinceBase

from Filters.Rules import (Person, Family, Event, Source, Citation, Place, 
                           MediaObject, Repository, Note)
