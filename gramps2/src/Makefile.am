# This is the src level Makefile for Gramps
# $Id$

SUBDIRS = \
	Config \
	DataViews \
	Editors \
	GrampsDb \
	GrampsLogger \
	Mime \
	Models \
	ObjectSelector \
	RelLib \
	TreeViews \
	data \
	DateHandler \
	PluginUtils \
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
	DdTargets.py\
	DisplayModels.py\
	DisplayState.py\
	DisplayTabs.py\
	Errors.py\
	Exporter.py\
	FontScale.py\
	GenericFilter.py\
	GrampsCfg.py\
	GrampsDisplay.py\
	GrampsLocale.py\
	gramps_main.py\
	gramps.py\
	GrampsWidgets.py\
	ImgManip.py\
	lds.py \
	ListModel.py\
	ManagedWindow.py\
	MergeData.py\
	MergePeople.py\
	NameDisplay.py\
	Navigation.py\
	PageView.py\
	PeopleModel.py\
	QuestionDialog.py\
	RecentFiles.py\
	Relationship.py\
	ScratchPad.py\
	SelectEvent.py\
	SelectObject.py\
	SelectPerson.py\
	Sort.py\
	soundex.py\
	Spell.py\
	StartupDialog.py\
	SubstKeywords.py\
	TipOfDay.py\
	ToolTips.py\
	TransUtils.py\
	TreeTips.py\
	Utils.py\
	ViewManager.py\
	SelectFamily.py\
	SelectSource.py

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

# Which modules to document
docmodules = RelLib DateHandler GrampsDb

pycheck: 
	for d in $(SUBDIRS) ; do \
          (cd $$d; make pycheck); \
	done;
	pychecker $(gdir_PYTHON)

docs:
	epydoc -o doc --url http://gramps.sourceforge.net --name GRAMPS --html $(docmodules)
	epydoc --pdf $(docmodules)

cmdplug:
	./build_cmdplug
