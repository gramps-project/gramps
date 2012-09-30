# This is the src/Filters/Rules/Source level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/source

pkgpython_PYTHON = \
	_changedsince.py\
	_matchesfilter.py\
	_sourceprivate.py\
	_regexpidof.py\
	_hasgallery.py \
	_hasnotematchingsubstringof.py\
	_hasreferencecountof.py\
	_allsources.py\
	_hasidof.py\
	_hasnote.py \
	_hasnoteregexp.py\
	_hasrepository.py\
	__init__.py\
        _matchestitlesubstringof.py\
        _hasrepositorycallnumberref.py\
        _matchesrepositoryfilter.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/source

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
