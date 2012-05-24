# This is the src/gen/filters/rules level Makefile for Gramps
# $Id$

SUBDIRS = person family event place source media repository note citation

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules

pkgpython_PYTHON = \
	_changedsincebase.py\
	_everything.py\
	_haseventbase.py\
	_hasattributebase.py\
	_hasgallerybase.py \
	_hasgrampsid.py\
	_hasldsbase.py \
	_hasnotebase.py \
	_hasnoteregexbase.py\
	_hasnotesubstrbase.py\
	_hasreferencecountbase.py \
	_hassourcecountbase.py \
	_hassourcebase.py \
	_hastagbase.py \
	_hastextmatchingregexpof.py\
	_hastextmatchingsubstringof.py\
	__init__.py\
	_isprivate.py\
        _ispublic.py\
	_regexpidbase.py\
	_rule.py\
	_matchesfilterbase.py\
    _matcheseventfilterbase.py \
    _matchessourceconfidencebase.py \
    _matchessourcefilterbase.py \
    _hascitationbase.py


pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
