# This is the src/plugins/import level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/import

pkgpython_PYTHON = \
	import.gpr.py \
	ImportCsv.py \
	ImportGedcom.py \
	ImportGeneWeb.py \
	ImportGpkg.py \
	ImportGrdb.py \
	ImportProGen.py \
	ImportVCard.py \
	ImportXml.py

pkgpyexecdir = @pkgpyexecdir@/plugins/import
pkgpythondir = $(datadir)/@PACKAGE@/plugins/import

dist_pkgdata_DATA = importgedcom.glade

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
