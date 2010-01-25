# This is the src/gui/editors/displaytabs level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/gui/editors/displaytabs

pkgdata_PYTHON = \
	addrembedlist.py \
	addressmodel.py \
	attrembedlist.py \
	attrmodel.py \
	backreflist.py \
	backrefmodel.py \
	buttontab.py \
	childmodel.py \
	dataembedlist.py \
	datamodel.py \
	embeddedlist.py \
	eventbackreflist.py \
	eventembedlist.py \
	eventrefmodel.py \
	familyattrembedlist.py \
	familyldsembedlist.py \
	gallerytab.py \
	grampstab.py \
	groupembeddedlist.py \
	ldsembedlist.py \
	ldsmodel.py \
	locationembedlist.py \
	locationmodel.py \
	mediabackreflist.py \
	nameembedlist.py \
	namemodel.py \
	notebackreflist.py \
	notetab.py \
	notemodel.py \
	personbackreflist.py \
	personeventembedlist.py \
	personrefembedlist.py \
	personrefmodel.py \
	placebackreflist.py \
	repoembedlist.py \
	reporefmodel.py \
	sourcebackreflist.py \
	sourceembedlist.py \
	sourcerefmodel.py \
	webembedlist.py \
	webmodel.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gui/editors/displaytabs
pkgpythondir = @pkgpythondir@/gui/editors/displaytabs

# clean up all the byte-compiled files
MOSTLYcLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
