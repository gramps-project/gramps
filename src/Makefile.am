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

# For intl. support, how do we compile?
MOSTLYCLEANFILES = 
CLEANFILES = const.pyc const.pyo

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead

gdirdir=$(prefix)/share/gramps

docfiles = \
	RelLib.py \
	Date.py \
	DateParser.py \
	DateDisplay.py \
	GrampsDbBase.py 

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
	ListModel.py\
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
	ViewManager.py

pycheck: 
	for d in $(SUBDIRS) ; do \
          (cd $$d; make pycheck); \
	done;
	pychecker $(gdir_PYTHON)

docs:
	epydoc -o doc --url http://gramps.sourceforge.net --name GRAMPS --html $(docfiles)
	epydoc --pdf $(docfiles)

cmdplug:
	./build_cmdplug
