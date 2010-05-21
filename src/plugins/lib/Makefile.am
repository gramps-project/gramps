# This is the src/plugins/lib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

xmldir = $(datadir)/xml

xml_in_files = holidays.xml.in
xml_DATA = $(xml_in_files:.xml.in=.xml)

@INTLTOOL_XML_RULE@

EXTRA_DIST=$(xml_in_files) $(xml_DATA)

pkgdatadir = $(datadir)/@PACKAGE@/plugins/lib

pkgdata_PYTHON = \
	libcairodoc.py\
	libformatting.py\
	libgedcom.py\
	libgrampsxml.py\
	libgrdb.py\
	libhtml.py\
	libhtmlbackend.py\
	libhtmlconst.py\
	libholiday.py\
	libmapservice.py\
	libmixin.py\
    libnarrate.py\
	libodfbackend.py\
	libpersonview.py\
	libplaceview.py\
	libplugins.gpr.py\
	libtranslate.py

pkgpyexecdir = @pkgpyexecdir@/plugins/lib
pkgpythondir = @pkgpythondir@/plugins/lib

GLADEFILES = 

GRAPHICS = 

DATAFILES = \
	holidays.xml

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
