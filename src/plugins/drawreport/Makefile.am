# This is the src/plugins/drawreport level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/drawreport

pkgdata_PYTHON = \
	AncestorTree.py \
        Calendar.py\
	DescendTree.py \
	FanChart.py \
	StatisticsChart.py \
	TimeLine.py

pkgpyexecdir = @pkgpyexecdir@/plugins/drawreport
pkgpythondir = @pkgpythondir@/plugins/drawreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
