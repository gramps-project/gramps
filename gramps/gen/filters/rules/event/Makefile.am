# This is the src/Filters/Rules/Event level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/event

pkgpython_PYTHON = \
	_changedsince.py\
	_matchesfilter.py\
	_eventprivate.py\
	_hasnoteregexp.py\
	_regexpidof.py\
	_allevents.py\
	_hascitation.py \
	_hasdata.py\
	_hasgallery.py \
	_hasidof.py\
	_hasnote.py \
    _hassourcecount.py \
	_hastype.py\
	_hasnotematchingsubstringof.py\
	_hasreferencecountof.py\
	_matchespersonfilter.py\
        _matchessourceconfidence.py\
	_matchessourcefilter.py\
	_hasattribute.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/event


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
