# This is the src/Filters/Rules/Event level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/event

pkgpython_PYTHON = \
	_ChangedSince.py\
	_MatchesFilter.py\
	_EventPrivate.py\
	_HasNoteRegexp.py\
	_RegExpIdOf.py\
	_AllEvents.py\
	_HasCitation.py \
	_HasData.py\
	_HasGallery.py \
	_HasIdOf.py\
	_HasNote.py \
    _HasSourceCount.py \
	_HasType.py\
	_HasNoteMatchingSubstringOf.py\
	_HasReferenceCountOf.py\
	_MatchesPersonFilter.py\
        _MatchesSourceConfidence.py\
	_MatchesSourceFilter.py\
	_HasAttribute.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/event


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
