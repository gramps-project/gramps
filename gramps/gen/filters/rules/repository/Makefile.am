# This is the src/Filters/Rules/Media level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/repository

pkgpython_PYTHON = \
	_allrepos.py\
	_changedsince.py\
	_hasidof.py\
	_hasnotematchingsubstringof.py\
	_hasnoteregexp.py\
	_hasreferencecountof.py\
	_hasrepo.py\
	_matchesfilter.py\
        _matchesnamesubstringof.py\
	_regexpidof.py\
	_repoprivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/repository

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
