# This is the src/Filters/Rules/Person level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/person

pkgpython_PYTHON = \
	_changedsince.py\
	_disconnected.py \
	_deeprelationshippathbetween.py \
	_everyone.py \
	_familywithincompleteevent.py \
	_hasattribute.py \
	_hasaddress.py \
	_hasalternatename.py \
	_hasassociation.py \
	_hasbirth.py \
	_hascitation.py \
	_hascommonancestorwith.py \
	_hascommonancestorwithfiltermatch.py \
	_hasdeath.py \
	_hasevent.py \
	_hasfamilyattribute.py \
	_hasfamilyevent.py \
	_hasgallery.py \
	_hasidof.py \
	_haslds.py \
	_hasnameof.py \
	_hasnameorigintype.py \
	_hasnametype.py \
	_hasnickname.py \
	_hasnote.py \
	_hasnotematchingsubstringof.py \
	_hasrelationship.py \
	_hassourcecount.py \
	_hassourceof.py \
	_hastag.py \
	_hastextmatchingregexpof.py \
	_hastextmatchingsubstringof.py \
	_hasunknowngender.py \
	_havealtfamilies.py \
	_havechildren.py \
	_incompletenames.py \
	_isancestorof.py \
	_isancestoroffiltermatch.py \
	_isbookmarked.py \
	_ischildoffiltermatch.py \
	_isdefaultperson.py \
	_isdescendantfamilyof.py \
        _isdescendantfamilyoffiltermatch.py \
	_isdescendantof.py \
	_isdescendantoffiltermatch.py \
	_isduplicatedancestorof.py \
	_isfemale.py \
	_islessthannthgenerationancestorof.py \
	_islessthannthgenerationancestorofbookmarked.py \
	_islessthannthgenerationancestorofdefaultperson.py \
	_islessthannthgenerationdescendantof.py \
	_ismale.py \
	_ismorethannthgenerationancestorof.py \
	_ismorethannthgenerationdescendantof.py \
	_isparentoffiltermatch.py \
        _isrelatedwith.py \
	_issiblingoffiltermatch.py \
	_isspouseoffiltermatch.py \
	_iswitness.py \
	_matchesfilter.py \
	_matcheseventfilter.py \
        _matchessourceconfidence.py \
	_missingparent.py \
	_multiplemarriages.py \
	_nevermarried.py \
	_nobirthdate.py \
        _nodeathdate.py \
	_peopleprivate.py \
        _peoplepublic.py \
	_personwithincompleteevent.py \
	_probablyalive.py \
	_relationshippathbetween.py \
	_relationshippathbetweenbookmarks.py \
	_searchname.py \
	_regexpidof.py \
	_matchidof.py \
	_hasnoteregexp.py \
	_regexpname.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/person

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
