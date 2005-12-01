# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/dates

pkgdata_PYTHON = \
	Date_de.py\
	Date_ru.py\
	Date_fr.py\
	Date_es.py\
	Date_fi.py\
	Date_sv.py\
	Date_nl.py

pkgpyexecdir = @pkgpyexecdir@/dates
pkgpythondir = @pkgpythondir@/dates

GRAMPS_PY_MODPATH = ".."

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
