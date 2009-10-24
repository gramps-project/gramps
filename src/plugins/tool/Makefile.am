# This is the src/plugins/tool level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/tool

pkgdata_PYTHON = \
	CalculateEstimatedDates.py \
	ChangeNames.py \
	ChangeTypes.py \
	Check.py \
	Desbrowser.py \
	Eval.py \
	EventCmp.py \
	EventNames.py \
	ExtractCity.py \
	FindDupes.py \
	Leak.py \
	MediaManager.py \
	NotRelated.py \
	OwnerEditor.py \
	PatchNames.py \
	Rebuild.py \
	RebuildRefMap.py \
	RelCalc.py \
	RemoveUnused.py \
	ReorderIds.py \
	SortEvents.py \
	SoundGen.py \
	tools.gpr.py \
	Verify.py
#	DumpGenderStats.py \
#	PHPGedViewConnector.py \
#	TestcaseGenerator.py

pkgpyexecdir = @pkgpyexecdir@/plugins/tool
pkgpythondir = @pkgpythondir@/plugins/tool

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
	verify.glade

	
dist_pkgdata_DATA = $(GLADEFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
