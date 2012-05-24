# This is the src/Filters/Rules/Family level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/family

pkgpython_PYTHON = \
	_allfamilies.py\
	_changedsince.py\
	_familyprivate.py\
	_hasevent.py\
	_hasattribute.py\
	_hascitation.py \
	_hasgallery.py \
	_hasidof.py\
	_haslds.py \
	_hasnote.py \
	_hasnotematchingsubstringof.py\
	_hasnoteregexp.py\
	_hasreferencecountof.py\
	_hasreltype.py\
	_hassourcecount.py \
	_hastag.py \
	__init__.py\
	_isbookmarked.py\
	_regexpidof.py\
	_matchesfilter.py\
        _matchessourceconfidence.py\
	_fatherhasnameof.py\
	_fatherhasidof.py\
	_motherhasnameof.py\
	_motherhasidof.py\
	_childhasnameof.py\
	_childhasidof.py\
	_searchfathername.py\
	_searchmothername.py\
	_searchchildname.py\
	_regexpfathername.py\
	_regexpmothername.py\
	_regexpchildname.py\
	_memberbase.py


pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/family

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
