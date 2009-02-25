# This is the src/plugins/export level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/export

pkgdata_PYTHON = \
	ExportCd.py \
	ExportCsv.py \
	ExportFtree.py \
	ExportGedcom.py \
	ExportGeneWeb.py \
	ExportPkg.py \
	ExportVCalendar.py \
	ExportVCard.py \
	ExportXml.py

pkgpyexecdir = @pkgpyexecdir@/plugins/export
pkgpythondir = @pkgpythondir@/plugins/export

GLADEFILES = \
	ExportCsv.glade \
	ExportFtree.glade \
	ExportGeneWeb.glade \
	ExportVCalendar.glade \
	ExportVCard.glade

GRAPHICS = 

DATAFILES = 

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
