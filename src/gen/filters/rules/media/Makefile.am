# This is the src/Filters/Rules/MediaObject level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/media

pkgpython_PYTHON = \
	_allmedia.py\
	_changedsince.py\
	_hascitation.py \
	_hasidof.py\
	_hasmedia.py\
	_hasnotematchingsubstringof.py\
	_hasnoteregexp.py\
	_hasreferencecountof.py\
	_hastag.py\
	_hassourcecount.py \
	_hassourceof \
	_matchesfilter.py\
        _matchessourceconfidence.py\
	_mediaprivate.py\
	_hasattribute.py\
	_regexpidof.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/media


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
