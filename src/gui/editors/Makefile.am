# This is the src/Editors level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gui/editors

pkgdata_PYTHON = \
	addmedia.py\
	__init__.py\
	editaddress.py \
	editattribute.py \
	editchildRef.py \
	editevent.py \
	editeventRef.py \
	editfamily.py \
	editldsOrd.py \
	editlocation.py \
	editmedia.py \
	editmediaRef.py \
	editname.py \
	editnote.py \
	editperson.py \
	editpersonRef.py \
	editplace.py \
	editprimary.py \
	editreference.py \
	editrepository.py \
	editrepoRef.py \
	editsecondary.py \
	editsource.py \
	editsourceRef.py \
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
