# This is the src/Filters/Rules/Person level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Person

pkgdata_PYTHON = \
	_Disconnected.py \
	_Everyone.py \
	_FamilyWithIncompleteEvent.py \
	_HasAttribute.py \
	_HasBirth.py \
	_HasCommonAncestorWith.py \
	_HasCommonAncestorWithFilterMatch.py \
	_HasCompleteRecord.py \
	_HasDeath.py \
	_HasEvent.py \
	_HasFamilyAttribute.py \
	_HasFamilyEvent.py \
	_HasIdOf.py \
	_HasNameOf.py \
	_HasNote.py \
	_HasNoteMatchingSubstringOf.py \
	_HasRelationship.py \
	_HasSourceOf.py \
	_HasTextMatchingRegexpOf.py \
	_HasTextMatchingSubstringOf.py \
	_HasUnknownGender.py \
	_HaveAltFamilies.py \
	_HaveChildren.py \
	_HavePhotos.py \
	_IncompleteNames.py \
	_IsAncestorOf.py \
	_IsAncestorOfFilterMatch.py \
	_IsBookmarked.py \
	_IsChildOfFilterMatch.py \
	_IsDefaultPerson.py \
	_IsDescendantFamilyOf.py \
	_IsDescendantOf.py \
	_IsDescendantOfFilterMatch.py \
	_IsFemale.py \
	_IsLessThanNthGenerationAncestorOf.py \
	_IsLessThanNthGenerationAncestorOfBookmarked.py \
	_IsLessThanNthGenerationAncestorOfDefaultPerson.py \
	_IsLessThanNthGenerationDescendantOf.py \
	_IsMale.py \
	_IsMoreThanNthGenerationAncestorOf.py \
	_IsMoreThanNthGenerationDescendantOf.py \
	_IsParentOfFilterMatch.py \
	_IsSiblingOfFilterMatch.py \
	_IsSpouseOfFilterMatch.py \
	_IsWitness.py \
	_MatchesFilter.py \
	_MissingParent.py \
	_MultipleMarriages.py \
	_NeverMarried.py \
	_NoBirthdate.py \
	_PeoplePrivate.py \
	_PersonWithIncompleteEvent.py \
	_ProbablyAlive.py \
	_RelationshipPathBetween.py \
	_RelationshipPathBetweenBookmarks.py \
	_SearchName.py \
	_RegExpIdOf.py \
	_MatchIdOf.py \
	_HasNoteRegexp.py \
	_RegExpName.py \
	_HasMarkerOf.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Person
pkgpythondir = @pkgpythondir@/Filters/Rules/Person

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
