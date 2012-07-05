# This is the src/plugins/docgen level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/docgen

pkgpython_PYTHON = \
	asciidoc.py \
	docgen.gpr.py\
	gtkprint.py \
	htmldoc.py \
	latexdoc.py \
	odfdoc.py \
	pdfdoc.py \
	psdrawdoc.py \
	rtfdoc.py \
	svgdrawdoc.py

pkgpyexecdir = @pkgpyexecdir@/plugins/docgen
pkgpythondir = $(datadir)/@PACKAGE@/plugins/docgen

GLADEFILES = \
	gtkprint.glade 

GRAPHICS = 

DATAFILES = 

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
