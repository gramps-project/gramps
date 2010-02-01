# This is the src level Makefile for Gramps
# $Id$

SUBDIRS = \
	cli \
	data \
	DateHandler \
	docgen \
	Filters \
	gen \
	glade \
	GrampsLocale \
	GrampsLogger \
	gui \
	images \
	Merge \
	mapstraction \
	PluginUtils \
	plugins \
	ReportBase \
	Simple

gdirdir=$(prefix)/share/gramps

gdir_PYTHON = \
	Assistant.py\
	AutoComp.py\
	Bookmarks.py\
	config.py\
	const.py\
	DateEdit.py\
	Date.py\
	DbState.py\
	DdTargets.py\
	DisplayState.py\
	Errors.py\
	ExportAssistant.py\
	ExportOptions.py\
	glade.py\
	GrampsAboutDialog.py\
	GrampsDisplay.py\
	gramps.py\
	ImgManip.py\
	LdsUtils.py \
	ListModel.py\
	Lru.py\
	ManagedWindow.py\
	QuestionDialog.py\
	QuickReports.py\
	RecentFiles.py\
	Relationship.py\
	Reorder.py\
	ScratchPad.py\
	Sort.py\
	soundex.py\
	Spell.py\
	SubstKeywords.py\
	TipOfDay.py\
	ThumbNails.py\
	ToolTips.py\
	TransUtils.py\
	TreeTips.py\
	Utils.py\
	UndoHistory.py\
	PlaceUtils.py

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

# Which modules to document
docmodules = RelLib DateHandler GrampsDb Simple BaseDoc #Filters ReportBase GrampsDbUtils 

pycheck: 
	for d in $(SUBDIRS) ; do \
          (cd $$d; make pycheck); \
	done;
	pychecker $(gdir_PYTHON)

docs:
	epydoc -v -o html --html --exclude gtk --no-private --show-imports --url=http://gramps-project.org  --graph=umlclasstree $(docmodules)
	epydoc -v -o pdf --pdf --exclude gtk --no-private --show-imports --url=http://gramps-project.org  --graph=umlclasstree $(docmodules)

cmdplug:
	./build_cmdplug
