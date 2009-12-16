# This is the src/gui/editors level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	displaytabs

pkgdatadir = $(datadir)/@PACKAGE@/gui/editors

pkgdata_PYTHON = \
	addmedia.py\
	__init__.py\
	editaddress.py \
	editattribute.py \
	editchildref.py \
	editevent.py \
	editeventref.py \
	editfamily.py \
	editldsord.py \
	editlocation.py \
	editmedia.py \
	editmediaref.py \
	editname.py \
	editnote.py \
	editperson.py \
	editpersonref.py \
	editplace.py \
	editprimary.py \
	editreference.py \
	editrepository.py \
	editreporef.py \
	editsecondary.py \
	editsource.py \
	editsourceref.py \
	editurl.py \
	objectentries.py

pkgpyexecdir = @pkgpyexecdir@/src/editors
pkgpythondir = @pkgpythondir@/src/editors

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
