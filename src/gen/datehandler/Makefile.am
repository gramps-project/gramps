# This is the src/DateHandler level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	_date_bg.py\
	_date_ca.py\
	_date_cs.py\
	_date_da.py\
	_date_de.py\
	_date_es.py\
	_date_fi.py\
	_date_fr.py\
	_date_hr.py\
	_date_it.py\
	_date_lt.py\
	_date_nb.py\
	_date_nl.py\
	_date_pl.py\
	_date_pt.py\
	_date_ru.py\
	_date_sk.py\
	_date_sl.py\
	_date_sr.py\
	_date_sv.py\
	_datedisplay.py\
	_dateparser.py\
	_datehandler.py\
	_dateutils.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/datehandler
pkgpythondir = $(datadir)/@PACKAGE@/gen/datehandler

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../.."

docfiles=\
	_datedisplay.py\
	_dateparser.py\
	_datehandler.py\
	_dateutils.py

docs:
	export PYTHONPATH='../..'; epydoc --graph=umlclasstree -o ../html --url http://gramps-project.org --name GRAMPS --html $(docfiles)

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
