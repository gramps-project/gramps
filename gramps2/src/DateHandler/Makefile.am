# This is the src/DateHandler level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/DateHandler

pkgdata_PYTHON = \
	_Date_de.py\
	_Date_ru.py\
	_Date_lt.py\
	_Date_fr.py\
	_Date_es.py\
	_Date_fi.py\
	_Date_sv.py\
	_Date_nl.py\
	_Date_sk.py\
	_DateDisplay.py\
	_DateParser.py\
	_DateHandler.py\
	_DateUtils.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/DateHandler
pkgpythondir = @pkgpythondir@/DateHandler

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = ".."

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
