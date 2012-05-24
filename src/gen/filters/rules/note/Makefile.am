# This is the src/Filters/Rules/Note level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/note

pkgpython_PYTHON = \
	_allnotes.py\
	_changedsince.py\
	_hasidof.py\
	_matchessubstringof.py\
	_matchesregexpof.py\
	_hasnote.py\
	_hasreferencecountof.py\
	_hastag.py\
	_matchesfilter.py\
	_regexpidof.py\
	_noteprivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/note

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
