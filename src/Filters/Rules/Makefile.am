# This is the src/Filters/Rules level Makefile for Gramps
# $Id$

SUBDIRS = Person Family Event Place Source MediaObject Repository Note Citation

pkgpythondir = $(datadir)/@PACKAGE@/Filters/Rules

pkgpython_PYTHON = \
	_ChangedSinceBase.py\
	_Everything.py\
	_HasEventBase.py\
	_HasAttributeBase.py\
	_HasGalleryBase.py \
	_HasGrampsId.py\
	_HasLDSBase.py \
	_HasNoteBase.py \
	_HasNoteRegexBase.py\
	_HasNoteSubstrBase.py\
	_HasReferenceCountBase.py \
	_HasSourceCountBase.py \
	_HasSourceBase.py \
	_HasTagBase.py \
	_HasTextMatchingRegexpOf.py\
	_HasTextMatchingSubstringOf.py\
	__init__.py\
	_IsPrivate.py\
        _IsPublic.py\
	_RegExpIdBase.py\
	_Rule.py\
	_MatchesFilterBase.py\
    _MatchesEventFilterBase.py \
    _MatchesSourceConfidenceBase.py \
    _MatchesSourceFilterBase.py \
    _HasCitationBase.py


pkgpyexecdir = @pkgpyexecdir@/Filters/Rules

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
