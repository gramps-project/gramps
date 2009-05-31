# This is the src/gen/plug/menu level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/plug/docgen

pkgdata_PYTHON = \
	__init__.py \
	basedoc.py  \
	drawdoc.py \
	fontscale.py \
	fontstyle.py \
	graphdoc.py \
	graphicstyle.py \
	paperstyle.py \
	paragraphstyle.py \
	stylesheet.py \
	tablestyle.py \
	textdoc.py 

pkgpyexecdir = @pkgpyexecdir@/gen/plug/docgen
pkgpythondir = @pkgpythondir@/gen/plug/docgen


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
