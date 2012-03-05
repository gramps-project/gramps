# This is the src/plugins/export level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	export.gpr.py \
	ExportCsv.py \
	ExportFtree.py \
	ExportGedcom.py \
	ExportGeneWeb.py \
	ExportPkg.py \
	ExportVCalendar.py \
	ExportVCard.py \
	ExportXml.py

pkgpyexecdir = @pkgpyexecdir@/plugins/export
pkgpythondir = $(datadir)/@PACKAGE@/plugins/export


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
