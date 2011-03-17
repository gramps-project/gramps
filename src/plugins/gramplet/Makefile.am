# This is the src/plugins/drawreport level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/gramplet

pkgdata_PYTHON = \
	AgeOnDateGramplet.py \
	AgeStats.py \
	Attributes.py \
	AttributesGramplet.py \
	bottombar.gpr.py \
	CalendarGramplet.py \
	Children.py \
	DescendGramplet.py \
	FanChartGramplet.py \
	FaqGramplet.py \
    Filter.py \
	Gallery.py \
	GivenNameGramplet.py \
	gramplet.gpr.py \
	MediaPreview.py \
	Notes.py \
	PedigreeGramplet.py \
	PersonDetails.py \
	MetadataViewer.py \
	PersonResidence.py \
	PlaceDetails.py \
	PluginManagerGramplet.py\
	QuickViewGramplet.py \
	RelativeGramplet.py \
	RepositoryDetails.py \
	SessionLogGramplet.py \
	Sources.py \
	StatsGramplet.py \
	SurnameCloudGramplet.py \
	ToDoGramplet.py \
	TopSurnamesGramplet.py \
	WelcomeGramplet.py \
	WhatsNext.py

pkgpyexecdir = @pkgpyexecdir@/plugins/gramplet
pkgpythondir = @pkgpythondir@/plugins/gramplet

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
