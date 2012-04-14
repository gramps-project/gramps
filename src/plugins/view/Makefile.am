# This is the src/plugins/quickview level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/view

pkgpython_PYTHON = \
	citationlistview.py \
	citationtreeview.py \
	eventview.py \
	familyview.py \
	fanchartview.py \
	geoclose.py \
	geoevents.py \
	geoplaces.py \
	geoperson.py \
	geofamily.py \
	geography.gpr.py \
	htmlrenderer.gpr.py \
	grampletview.py \
	htmlrenderer.py \
	mediaview.py \
	noteview.py \
	pedigreeview.py \
	personlistview.py \
	persontreeview.py \
	placelistview.py \
	placetreeview.py \
	relview.py \
	repoview.py \
	sourceview.py \
	view.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/view

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
