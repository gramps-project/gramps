# This is the src/gen/lib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/lib

pkgdata_PYTHON = \
	addressbase.py \
	address.py \
	attributeBase.py \
	attribute.py \
	attrtype.py \
	baseobj.py \
	calendar.py \
	childref.py \
	childreftype.py \
	datebase.py \
	date.py \
	event.py \
	eventref.py \
	eventroletype.py \
	eventtype.py \
	family.py \
	familyreltype.py \
	genderstats.py \
	grampstype.py \
	__init__.py \
	ldsordbase.py \
	ldsord.py \
	locationbase.py \
	location.py \
	markertype.py \
	mediabase.py \
	mediaobj.py \
	mediaref.py \
	name.py \
	nametype.py \
	notebase.py \
	note.py \
	notetype.py \
	person.py \
	personref.py \
	placebase.py \
	place.py \
	primaryobj.py \
	privacybase.py \
	privsrcnote.py \
	refbase.py \
	repo.py \
	reporef.py \
	repotype.py \
	researcher.py \
	secondaryobj.py \
	srcbase.py \
	srcmediatype.py \
	srcnote.py \
	src.py \
	srcref.py \
	urlbase.py \
	url.py \
	urltype.py \
	witness.py 

pkgpyexecdir = @pkgpyexecdir@/lib
pkgpythondir = @pkgpythondir@/lib

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));

pylint:
	pylint --disable-msg=W0403,C0103 $(pkgdata_PYTHON)
