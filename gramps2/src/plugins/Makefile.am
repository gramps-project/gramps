# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually
pkgpython_PYTHON = \
	AncestorChart.py\
	AncestorReport.py\
	Ancestors.py\
	BookReport.py\
	ChangeTypes.py\
	Check.py\
	count_anc.py\
	Desbrowser.py\
	DescendReport.py\
	DesGraph.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EventCmp.py\
	FamilyGroup.py\
	FanChart.py\
	FtmStyleAncestors.py\
	FtmStyleDescendants.py\
	FilterEditor.py\
	GraphViz.py\
	IndivComplete.py\
	IndivSummary.py\
	Merge.py\
	PatchNames.py\
	ReadGedcom.py\
	ReadPkg.py\
	ReadNative.py\
	RelCalc.py\
	ReorderIds.py\
	soundgen.py\
	Summary.py\
	TimeLine.py\
	Verify.py\
	WebPage.py\
	WriteFtree.py\
	WriteGedcom.py\
	WritePkg.py\
	WriteCD.py\
	rel_ru.py\
	eval.py\
	leak.py\
	SimpleBookTitle.py\
	CustomBookText.py\
	RelGraph.py\
	rel_it.py\
	rel_hu.py\
	rel_de.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	changetype.glade\
	desbrowse.glade\
	eventcmp.glade\
	gedcomexport.glade\
	gedcomimport.glade\
	merge.glade\
	pafexport.glade\
	patchnames.glade\
	pkgexport.glade\
	relcalc.glade\
	soundex.glade\
	summary.glade\
	verify.glade\
	cdexport.glade\
	eval.glade\
	leak.glade\
	book.glade\
	writeftree.glade

pkgdatadir = $(datadir)/@PACKAGE@/plugins

dist_pkgdata_DATA = $(GLADEFILES)

GRAMPS_PY_MODPATH = "../:../docgen"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
