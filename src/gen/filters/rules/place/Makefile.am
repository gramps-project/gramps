# This is the src/Filters/Rules/Place level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/place

pkgpython_PYTHON = \
	_allplaces.py\
	_changedsince.py\
	_hasidof.py\
	_hasnolatorlon.py\
	_inlatlonneighborhood.py\
	_hasgallery.py \
	_hasnotematchingsubstringof.py\
	_hasnoteregexp.py\
	_hasplace.py\
	_hasnote.py \
	_hasreferencecountof.py\
	_matchesfilter.py\
	_matcheseventfilter.py\
	_placeprivate.py\
	_regexpidof.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/place

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
