# This is the src/plugins/drawreport level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/gramplet

pkgpython_PYTHON = \
	ageondategramplet.py \
	agestats.py \
	attributes.py \
	attributesgramplet.py \
	backlinks.py \
	calendargramplet.py \
	children.py \
	citations.py \
	descendgramplet.py \
        editexifmetadata.py \
	events.py \
	fanchartgramplet.py \
	faqgramplet.py \
	filter.py \
	gallery.py \
	givennamegramplet.py \
	gramplet.gpr.py \
	mediapreview.py \
	metadataviewer.py \
	notes.py \
	pedigreegramplet.py \
	persondetails.py \
	personresidence.py \
	placedetails.py \
	quickviewgramplet.py \
	relativegramplet.py \
	repositorydetails.py \
	sessionloggramplet.py \
	statsgramplet.py \
	surnamecloudgramplet.py \
	todogramplet.py \
	topsurnamesgramplet.py \
	welcomegramplet.py \
	whatsnext.py

pkgpyexecdir = @pkgpyexecdir@/plugins/gramplet

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
