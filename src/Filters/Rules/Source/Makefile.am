# This is the src/Filters/Rules/Source level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Source

pkgdata_PYTHON = \
	_MatchesFilter.py\
	_SourcePrivate.py\
	_RegExpIdOf.py\
	_HasNoteMatchingSubstringOf.py\
	_AllSources.py\
	_HasIdOf.py\
	_HasSource.py\
	_HasNoteRegexp.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Source
pkgpythondir = @pkgpythondir@/Filters/Rules/Source

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
