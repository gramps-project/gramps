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
	quickview \
	rel \
	textreport \
	tool \
	webreport

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	BookReport.py\
	Calendar.py \
	ExportXml.py\
	ImportGpkg.py\
	ImportXml.py\
	Records.py\
	WebCal.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	book.glade

GRAPHICS = 

DATAFILES = \
	holidays.xml

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../:../docgen"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
