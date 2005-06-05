# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	AncestorChart.py\
	AncestorChart2.py\
	AncestorReport.py\
	Ancestors.py\
	BookReport.py\
	ChangeTypes.py\
	ChangeNames.py\
	Check.py\
	CountAncestors.py\
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
	ReadPkg.py\
	RelCalc.py\
	ReorderIds.py\
	ScratchPad.py\
	SoundGen.py\
	StatisticsChart.py\
	Summary.py\
	TimeLine.py\
	Verify.py\
	WebPage.py\
	WriteFtree.py\
	WritePkg.py\
	WriteCD.py\
	rel_ru.py\
	Eval.py\
	Leak.py\
	SimpleBookTitle.py\
	CustomBookText.py\
	rel_it.py\
	rel_hu.py\
	rel_da.py\
	rel_de.py\
	rel_fi.py\
	rel_fr.py\
	rel_no.py\
	rel_sv.py\
	ImportGeneWeb.py\
	WriteGeneWeb.py\
	rel_es.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	changetype.glade\
	desbrowse.glade\
	eventcmp.glade\
	merge.glade\
	patchnames.glade\
	changenames.glade\
	relcalc.glade\
	soundex.glade\
	summary.glade\
	verify.glade\
	cdexport.glade\
	eval.glade\
	leak.glade\
	book.glade\
	writeftree.glade\
	genewebexport.glade\
	scratchpad.glade

GRAPHICS = \
	stock_link.png

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS)

GRAMPS_PY_MODPATH = "../:../docgen"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
