# This is the src/calendars level Makefile for Gramps
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	Islamic.py \
	Persian.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

pkgdatadir = $(datadir)/@PACKAGE@/calendars

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
