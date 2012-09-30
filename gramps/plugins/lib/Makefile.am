# This is the src/plugins/lib level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

xml_in_files = holidays.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)

@INTLTOOL_XML_NOMERGE_RULE@

EXTRA_DIST=$(xml_in_files) $(xml_files)

pkgdatadir = $(datadir)/@PACKAGE@/plugins/lib

SUBDIRS = maps

pkgpython_PYTHON = \
	libcairodoc.py\
	libgedcom.py\
	libgrampsxml.py\
	libgrdb.py\
	libhtml.py\
	libhtmlbackend.py\
	libhtmlconst.py\
	libholiday.py\
	libmapservice.py\
	libmetadata.py\
	libmixin.py\
	libnarrate.py\
	libodfbackend.py\
	libpersonview.py\
	libplaceview.py\
	libplugins.gpr.py\
	libsubstkeyword.py\
	libtranslate.py\
	libtreebase.py

pkgpyexecdir = @pkgpyexecdir@/plugins/lib
pkgpythondir = $(datadir)/@PACKAGE@/plugins/lib

GLADEFILES = 

GRAPHICS = 

DATAFILES = \
	holidays.xml

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

CLEANFILES = \
    $(xml_files)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
