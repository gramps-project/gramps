pkgdatadir = $(datadir)/@PACKAGE@/plugins/lib/maps
# $Id$

pkgpython_PYTHON = \
	constants.py\
	datelayer.py\
	dummylayer.py\
	dummynogps.py\
	geography.py\
	__init__.py\
	lifewaylayer.py\
	osmGps.py\
	placeselection.py\
	selectionlayer.py


pkgpyexecdir = @pkgpyexecdir@/plugins/lib/maps
pkgpythondir = $(datadir)/@PACKAGE@/plugins/lib/maps

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../:../view"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
