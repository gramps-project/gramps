# This is the src/Filters/Rules/Citation level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/citation

pkgpython_PYTHON = \
	__init__.py \
	_allcitations.py \
	_changedsince.py \
	_citationprivate.py \
	_hascitation.py \
	_hasgallery.py \
	_hasidof.py \
	_hasnote.py \
	_hasnotematchingsubstringof.py \
	_hasnoteregexp.py \
	_hasreferencecountof.py \
	_hassource.py \
	_matchesfilter.py \
	_matchespagesubstringof.py \
	_matchesrepositoryfilter.py \
	_matchessourcefilter.py \
	_regexpidof.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/citation

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
