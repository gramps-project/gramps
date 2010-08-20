# This is the src/plugins/webstuff level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

DATAFILES = \
        css/ancestortree.css \
	css/behaviour.css          \
        css/Mapstraction.css \
	css/Web_Basic-Spruce.css \
	css/Web_Mainz.css \
	css/Web_Basic-Ash.css      \
	css/Web_Navigation-Horizontal.css \
	css/Web_Basic-Blue.css     \
	css/Web_Navigation-Vertical.css \
	css/Web_Basic-Cypress.css  \
	css/Web_Nebraska.css \
	css/Web_Basic-Lilac.css    \
	css/Web_Print-Default.css \
	css/Web_Basic-Peach.css    \
	css/Web_Visually.css \
	images/blank.gif \
	images/document.png \
	images/favicon2.ico \
	images/favicon.ico \
	images/Web_Gender_Female.png \
	images/Web_Gender_Male.png \
	images/Web_Mainz_Bkgd.png \
	images/Web_Mainz_Header.png \
	images/Web_Mainz_MidLight.png \
	images/Web_Mainz_Mid.png

pkgdatadir = $(datadir)/@PACKAGE@/plugins/webstuff

pkgdata_PYTHON = \
	webstuff.py \
	webstuff.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/webstuff
pkgpythondir = @pkgpythondir@/plugins/webstuff

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
