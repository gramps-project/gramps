# This is the src/plugins/tool level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/tool

pkgpython_PYTHON = \
	changenames.py \
	changetypes.py \
	check.py \
	desbrowser.py \
	eval.py \
	eventcmp.py \
	eventnames.py \
	extractcity.py \
	finddupes.py \
	leak.py \
	mediamanager.py \
	notrelated.py \
	ownereditor.py \
	patchnames.py \
	rebuild.py \
	rebuildgenderstat.py \
	rebuildrefmap.py \
	relcalc.py \
	removeunused.py \
	reorderids.py \
	sortevents.py \
	soundgen.py \
	tools.gpr.py \
	verify.py \
	mergecitations.py
#	dumpgenderstats.py \
#	phpgedviewconnector.py \
#	testcasegenerator.py

pkgpyexecdir = @pkgpyexecdir@/plugins/tool
pkgpythondir = $(datadir)/@PACKAGE@/plugins/tool

GLADEFILES = \
	changenames.glade \
	changetypes.glade \
	check.glade \
	desbrowser.glade \
	eval.glade \
	eventcmp.glade \
	finddupes.glade \
	leak.glade \
	notrelated.glade \
	ownereditor.glade \
	patchnames.glade \
	phpgedview.glade \
	relcalc.glade \
	removeunused.glade \
	soundgen.glade \
	verify.glade \
	mergecitations.glade

dist_pkgdata_DATA = $(GLADEFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
