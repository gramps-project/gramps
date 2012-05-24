# This is the src/Filters/Rules/Person level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/person

pkgpython_PYTHON = \
	_ChangedSince.py\
	_Disconnected.py \
	_DeepRelationshipPathBetween.py \
	_Everyone.py \
	_FamilyWithIncompleteEvent.py \
	_HasAttribute.py \
	_HasAddress.py \
	_HasAlternateName.py \
	_HasAssociation.py \
	_HasBirth.py \
	_HasCitation.py \
	_HasCommonAncestorWith.py \
	_HasCommonAncestorWithFilterMatch.py \
	_HasDeath.py \
	_HasEvent.py \
	_HasFamilyAttribute.py \
	_HasFamilyEvent.py \
	_HasGallery.py \
	_HasIdOf.py \
	_HasLDS.py \
	_HasNameOf.py \
	_HasNameOriginType.py \
	_HasNameType.py \
	_HasNickname.py \
	_HasNote.py \
	_HasNoteMatchingSubstringOf.py \
	_HasRelationship.py \
	_HasSourceCount.py \
	_HasSourceOf.py \
	_HasTag.py \
	_HasTextMatchingRegexpOf.py \
	_HasTextMatchingSubstringOf.py \
	_HasUnknownGender.py \
	_HaveAltFamilies.py \
	_HaveChildren.py \
	_IncompleteNames.py \
	_IsAncestorOf.py \
	_IsAncestorOfFilterMatch.py \
	_IsBookmarked.py \
	_IsChildOfFilterMatch.py \
	_IsDefaultPerson.py \
	_IsDescendantFamilyOf.py \
        _IsDescendantFamilyOfFilterMatch.py \
	_IsDescendantOf.py \
	_IsDescendantOfFilterMatch.py \
	_IsDuplicatedAncestorOf.py \
	_IsFemale.py \
	_IsLessThanNthGenerationAncestorOf.py \
	_IsLessThanNthGenerationAncestorOfBookmarked.py \
	_IsLessThanNthGenerationAncestorOfDefaultPerson.py \
	_IsLessThanNthGenerationDescendantOf.py \
	_IsMale.py \
	_IsMoreThanNthGenerationAncestorOf.py \
	_IsMoreThanNthGenerationDescendantOf.py \
	_IsParentOfFilterMatch.py \
        _IsRelatedWith.py \
	_IsSiblingOfFilterMatch.py \
	_IsSpouseOfFilterMatch.py \
	_IsWitness.py \
	_MatchesFilter.py \
	_MatchesEventFilter.py \
        _MatchesSourceConfidence.py \
	_MissingParent.py \
	_MultipleMarriages.py \
	_NeverMarried.py \
	_NoBirthdate.py \
        _NoDeathdate.py \
	_PeoplePrivate.py \
        _PeoplePublic.py \
	_PersonWithIncompleteEvent.py \
	_ProbablyAlive.py \
	_RelationshipPathBetween.py \
	_RelationshipPathBetweenBookmarks.py \
	_SearchName.py \
	_RegExpIdOf.py \
	_MatchIdOf.py \
	_HasNoteRegexp.py \
	_RegExpName.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/person

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
