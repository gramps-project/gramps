# This is the src/plugins level Makefile for Gramps
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually
pkgpython_PYTHON = AncestorChart.py \
		 AncestorReport.py \
		 Capitalize.py \
		 ChangeTypes.py \
		 Check.py \
		 count_anc.py \
		 Desbrowser.py \
		 DescendReport.py \
		 DesGraph.py \
		 DetAncestralReport.py \
		 DetDescendantReport.py \
		 EventCmp.py \
		 FamilyGroup.py \
		 FilterEditor.py \
		 Graph.py \
		 GraphViz.py \
		 IndivComplete.py \
		 IndivSummary.py \
		 Merge.py \
		 PatchNames.py \
		 ReadGedcom.py \
		 ReadNative.py \
		 RelCalc.py \
		 ReorderIds.py \
		 soundgen.py \
		 Summary.py \
		 Verify.py \
		 WebPage.py \
		 WriteGedcom.py \
		 WritePafPalm.py \
		 WritePkg.py 

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = desbrowse.glade \
	   eventcmp.glade \
	   gedcomexport.glade \
	   gedcomimport.glade \
	   merge.glade \
	   pafexport.glade \
	   patchnames.glade \
	   pkgexport.glade \
	   readgedcom.glade \
	   relcalc.glade \
	   soundex.glade \
	   summary.glade \
	   verify.glade


pkgdatadir = ${datadir}/@PACKAGE@/plugins

pkgdata_DATA = ${GLADEFILES}
dist_pkgdata_DATA = ${pkgdata_DATA} 

