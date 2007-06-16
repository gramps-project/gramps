# This is the src/GrampsDbUtils level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/GrampsDbUtils

pkgdata_PYTHON = \
	_Backup.py\
	_GedcomChar.py\
	_GedcomInfo.py\
	_GedcomLex.py\
	_GedcomParse.py\
	_GedcomTokens.py\
	_GedcomUtils.py\
	_GrampsDbWRFactories.py\
	__init__.py\
	_ReadGedcom.py\
	_ReadXML.py\
	_WriteGedcom.py\
	_WriteGrdb.py\
	_WriteXML.py

pkgpyexecdir = @pkgpyexecdir@/GrampsDbUtils
pkgpythondir = @pkgpythondir@/GrampsDbUtils

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

pylint: 
	(export PYTHONPATH=..:.; pylint --rcfile=pylintrc _GedcomParse.py)
