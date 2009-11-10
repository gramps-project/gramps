# This is the src/plugins/quickview level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/view

pkgdata_PYTHON = \
	eventview.py \
	familyview.py \
	geoview.py \
	geoview.gpr.py \
	grampletview.py \
	htmlrenderer.py \
	mediaview.py \
	noteview.py \
	pedigreeview.py \
	personview.py \
	placeview.py \
	relview.py \
	repoview.py \
	sourceview.py \
	view.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/view
pkgpythondir = @pkgpythondir@/plugins/view

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
