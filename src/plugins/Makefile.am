# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	docgen \
	drawreport \
	export \
	gramplet \
	graph \
	import \
	lib \
	mapservices \
	quickview \
	rel \
	textreport \
	tool \
	view \
	webreport

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	BookReport.py\
	records.gpr.py\
	Records.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	bookreport.glade

GRAPHICS = 

DATAFILES = 

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../:../docgen"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
