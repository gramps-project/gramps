# This is the src/Filters/Rules/Event level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Event

pkgdata_PYTHON = \
	_MatchesFilter.py\
	_EventPrivate.py\
	_HasNoteRegexp.py\
	_RegExpIdOf.py\
	_AllEvents.py\
	_HasIdOf.py\
	_HasMarkerOf.py\
	_HasType.py\
	_HasNoteMatchingSubstringOf.py\
	_HasReferenceCountOf.py\
	_MatchesPersonFilter.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Event
pkgpythondir = @pkgpythondir@/Filters/Rules/Event

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
