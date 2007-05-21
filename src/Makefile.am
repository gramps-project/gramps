# This is the src level Makefile for Gramps
# $Id$

SUBDIRS = \
	BasicUtils \
	Config \
	DateHandler \
	DataViews \
	Editors \
	Filters \
	FilterEditor \
	GrampsDb \
	GrampsDbUtils \
	GrampsLocale \
	Merge \
	DisplayTabs \
	DisplayModels \
	GrampsLogger \
	Mime \
	Selectors \
	Simple \
	RelLib \
	data \
	PluginUtils \
	ReportBase \
	glade \
	docgen \
	images \
	plugins

gdirdir=$(prefix)/share/gramps

gdir_PYTHON = \
	AddMedia.py\
	ansel_utf8.py\
	ArgHandler.py\
	Assistant.py\
	AutoComp.py\
	BaseDoc.py\
	Bookmarks.py\
	ColumnOrder.py\
	const.py\
	DateEdit.py\
	Date.py\
	DbLoader.py\
	DbState.py\
	DdTargets.py\
	DisplayState.py\
	Errors.py\
	Exporter.py\
	FontScale.py\
	GrampsCfg.py\
	GrampsDisplay.py\
	gramps_main.py\
	gramps.py\
	GrampsWidgets.py\
	ImgManip.py\
	LdsUtils.py \
	ListModel.py\
	Lru.py\
	ManagedWindow.py\
	MarkupText.py\
	Navigation.py\
	PageView.py\
	QuestionDialog.py\
	RecentFiles.py\
	Relationship.py\
	Reorder.py\
	ScratchPad.py\
	Sort.py\
	soundex.py\
	Spell.py\
	SubstKeywords.py\
	TipOfDay.py\
	ToolTips.py\
	TransUtils.py\
	TreeTips.py\
	Utils.py\
	ViewManager.py\
	UndoHistory.py\
	PlaceUtils.py

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

# Which modules to document
docmodules = RelLib DateHandler GrampsDb Filters ReportBase GrampsDbUtils 

pycheck: 
	for d in $(SUBDIRS) ; do \
          (cd $$d; make pycheck); \
	done;
	pychecker $(gdir_PYTHON)

docs:
	epydoc -o doc --url http://gramps-project.org --name GRAMPS --html $(docmodules)
	epydoc --pdf $(docmodules)

cmdplug:
	./build_cmdplug
