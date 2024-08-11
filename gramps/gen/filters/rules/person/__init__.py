#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
# Copyright (C) 2007-2008   Brian G. Matherly
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Package providing filter rules for Gramps.
"""

from ._disconnected import Disconnected
from ._everyone import Everyone
from ._familywithincompleteevent import FamilyWithIncompleteEvent
from ._hasaddress import HasAddress
from ._hasaddresstext import HasAddressText
from ._hasalternatename import HasAlternateName
from ._hasassociation import HasAssociation
from ._hasattribute import HasAttribute
from ._hasbirth import HasBirth
from ._hascitation import HasCitation
from ._hascommonancestorwith import HasCommonAncestorWith
from ._hascommonancestorwithfiltermatch import HasCommonAncestorWithFilterMatch
from ._hasdeath import HasDeath
from ._hasevent import HasEvent
from ._hasfamilyattribute import HasFamilyAttribute
from ._hasfamilyevent import HasFamilyEvent
from ._hasgallery import HavePhotos
from ._hasidof import HasIdOf
from ._haslds import HasLDS
from ._hasnameof import HasNameOf
from ._hasnameorigintype import HasNameOriginType
from ._hasnametype import HasNameType
from ._hasnickname import HasNickname
from ._hasnote import HasNote
from ._hasnotematchingsubstringof import HasNoteMatchingSubstringOf
from ._hasnoteregexp import HasNoteRegexp
from ._hasothergender import HasOtherGender
from ._hasrelationship import HasRelationship
from ._hassourcecount import HasSourceCount
from ._hassourceof import HasSourceOf
from ._hastag import HasTag
from ._hastextmatchingregexpof import HasTextMatchingRegexpOf
from ._hastextmatchingsubstringof import HasTextMatchingSubstringOf
from ._hasunknowngender import HasUnknownGender
from ._havealtfamilies import HaveAltFamilies
from ._havechildren import HaveChildren
from ._incompletenames import IncompleteNames
from ._isancestorof import IsAncestorOf
from ._isancestoroffiltermatch import IsAncestorOfFilterMatch
from ._isbookmarked import IsBookmarked
from ._ischildoffiltermatch import IsChildOfFilterMatch
from ._isdefaultperson import IsDefaultPerson
from ._isdescendantfamilyof import IsDescendantFamilyOf
from ._isdescendantfamilyoffiltermatch import IsDescendantFamilyOfFilterMatch
from ._isdescendantof import IsDescendantOf
from ._isdescendantoffiltermatch import IsDescendantOfFilterMatch
from ._isduplicatedancestorof import IsDuplicatedAncestorOf
from ._isfemale import IsFemale
from ._islessthannthgenerationancestorof import IsLessThanNthGenerationAncestorOf
from ._islessthannthgenerationancestorofbookmarked import (
    IsLessThanNthGenerationAncestorOfBookmarked,
)
from ._islessthannthgenerationancestorofdefaultperson import (
    IsLessThanNthGenerationAncestorOfDefaultPerson,
)
from ._islessthannthgenerationdescendantof import IsLessThanNthGenerationDescendantOf
from ._ismale import IsMale
from ._ismorethannthgenerationancestorof import IsMoreThanNthGenerationAncestorOf
from ._ismorethannthgenerationdescendantof import IsMoreThanNthGenerationDescendantOf
from ._isparentoffiltermatch import IsParentOfFilterMatch
from ._issiblingoffiltermatch import IsSiblingOfFilterMatch
from ._isspouseoffiltermatch import IsSpouseOfFilterMatch
from ._iswitness import IsWitness
from ._matchesfilter import MatchesFilter
from ._matcheseventfilter import MatchesEventFilter
from ._matchessourceconfidence import MatchesSourceConfidence
from ._missingparent import MissingParent
from ._multiplemarriages import MultipleMarriages
from ._nevermarried import NeverMarried
from ._nobirthdate import NoBirthdate
from ._nodeathdate import NoDeathdate
from ._peopleprivate import PeoplePrivate
from ._peoplepublic import PeoplePublic
from ._personwithincompleteevent import PersonWithIncompleteEvent
from ._probablyalive import ProbablyAlive
from ._relationshippathbetween import RelationshipPathBetween
from ._deeprelationshippathbetween import DeepRelationshipPathBetween
from ._relationshippathbetweenbookmarks import RelationshipPathBetweenBookmarks
from ._searchname import SearchName
from ._regexpname import RegExpName
from ._matchidof import MatchIdOf
from ._regexpidof import RegExpIdOf
from ._changedsince import ChangedSince
from ._isrelatedwith import IsRelatedWith
from ._hassoundexname import HasSoundexName

# -------------------------------------------------------------------------
#
# This is used by Custom Filter Editor tool
#
# -------------------------------------------------------------------------
editor_rule_list = [
    Everyone,
    IsFemale,
    IsMale,
    HasOtherGender,
    HasUnknownGender,
    IsDefaultPerson,
    IsBookmarked,
    HasAlternateName,
    HasAddress,
    HasAddressText,
    HasAssociation,
    HasIdOf,
    HasLDS,
    HasNameOf,
    HasNameOriginType,
    HasNameType,
    HasNickname,
    HasRelationship,
    HasDeath,
    HasBirth,
    HasCitation,
    HasEvent,
    HasFamilyEvent,
    HasAttribute,
    HasFamilyAttribute,
    HasTag,
    HasSourceCount,
    HasSourceOf,
    HaveAltFamilies,
    HavePhotos,
    HaveChildren,
    IncompleteNames,
    NeverMarried,
    MultipleMarriages,
    NoBirthdate,
    NoDeathdate,
    PersonWithIncompleteEvent,
    FamilyWithIncompleteEvent,
    ProbablyAlive,
    PeoplePrivate,
    PeoplePublic,
    IsWitness,
    IsDescendantOf,
    IsDescendantFamilyOf,
    IsDescendantFamilyOfFilterMatch,
    IsLessThanNthGenerationAncestorOfDefaultPerson,
    IsDescendantOfFilterMatch,
    IsDuplicatedAncestorOf,
    IsLessThanNthGenerationDescendantOf,
    IsMoreThanNthGenerationDescendantOf,
    IsAncestorOf,
    IsAncestorOfFilterMatch,
    IsLessThanNthGenerationAncestorOf,
    IsLessThanNthGenerationAncestorOfBookmarked,
    IsMoreThanNthGenerationAncestorOf,
    HasCommonAncestorWith,
    HasCommonAncestorWithFilterMatch,
    MatchesFilter,
    MatchesEventFilter,
    MatchesSourceConfidence,
    MissingParent,
    IsChildOfFilterMatch,
    IsParentOfFilterMatch,
    IsSpouseOfFilterMatch,
    IsSiblingOfFilterMatch,
    RelationshipPathBetween,
    DeepRelationshipPathBetween,
    RelationshipPathBetweenBookmarks,
    HasTextMatchingSubstringOf,
    HasNote,
    HasNoteRegexp,
    RegExpIdOf,
    RegExpName,
    Disconnected,
    ChangedSince,
    IsRelatedWith,
    HasSoundexName,
]
