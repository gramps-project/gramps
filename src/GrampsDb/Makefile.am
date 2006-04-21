# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/GrampsDb

pkgdata_PYTHON = \
	_DbUtils.py \
	_GedcomInfo.py\
	_GedTokens.py\
	_GrampsBSDDB.py\
	_GrampsDbBase.py\
	_GrampsDBCallback.py\
	_GrampsDbExceptions.py\
	_GrampsDbFactories.py\
	_GrampsGEDDB.py\
	_GrampsInMemDB.py\
	_GrampsXMLDB.py\
	__init__.py\
	_ReadGedcom.py\
	_ReadGrdb.py\
	_ReadXML.py\
	_WriteGedcom.py\
	_WriteGrdb.py\
	_WriteXML.py

pkgpyexecdir = @pkgpyexecdir@/GrampsDb
pkgpythondir = @pkgpythondir@/GrampsDb

GLADEFILES = \
	gedcomimport.glade\
	gedcomexport.glade

dist_pkgdata_DATA = $(GLADEFILES) 

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
