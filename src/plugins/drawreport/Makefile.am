# This is the src/plugins/drawreport level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/drawreport

pkgpython_PYTHON = \
	ancestortree.py \
	calendar.py\
	descendtree.py \
	drawplugins.gpr.py\
	fanchart.py \
	statisticschart.py \
	timeline.py

pkgpyexecdir = @pkgpyexecdir@/plugins/drawreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
