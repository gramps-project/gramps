# $Id$
# This is the src level Makefile for Gramps
SUBDIRS = docgen plugins dates data po 

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
	accent.py \
	AddMedia.py\
	AddrEdit.py\
	AddSpouse.py\
	ansel_utf8.py\
	AttrEdit.py\
	AutoComp.py\
	BaseDoc.py\
	Bookmarks.py\
	CalSdn.py\
	ColumnOrder.py\
	ChooseParents.py\
	const.py\
	DateEdit.py\
	Date.py\
	DateParser.py\
	DateHandler.py\
	DateDisplay.py\
	DbPrompter.py\
	DdTargets.py\
	DisplayModels.py\
	DisplayTrace.py\
	EditPerson.py\
	EditPlace.py\
	EditSource.py\
	Errors.py\
	EventEdit.py\
	FamilyView.py\
	FontScale.py\
	GedcomInfo.py\
	GenericFilter.py\
	GrampsCfg.py\
	GrampsBSDDB.py\
	GrampsDbBase.py\
	GrampsDBCallback.py\
	GrampsInMemDB.py\
	GrampsXMLDB.py\
	GrampsGEDDB.py\
	GrampsMime.py\
	gramps_main.py\
	gramps.py\
	GraphLayout.py\
	ImageSelect.py\
	ImgManip.py\
	latin_ansel.py\
	latin_utf8.py\
	ListModel.py\
	LocEdit.py\
	Marriage.py\
	MediaView.py\
	MergeData.py\
	MergePeople.py\
	NameDisplay.py\
	NameEdit.py\
	NoteEdit.py\
	PaperMenu.py\
	PedView.py\
	PeopleView.py\
	PeopleModel.py\
	PlaceView.py\
	Plugins.py\
	PluginMgr.py\
	QuestionDialog.py\
	ReadGedcom.py \
	ReadXML.py\
	Relationship.py\
	RelImage.py\
	RelLib.py\
	Report.py\
	ReportUtils.py\
	SelectChild.py\
	SelectObject.py\
	Sort.py\
	soundex.py\
	Sources.py\
	SourceView.py\
	SpreadSheetDoc.py\
	StartupDialog.py\
	StyleEditor.py\
	SubstKeywords.py\
	TarFile.py\
	TipOfDay.py\
	TransTable.py\
	TreeTips.py\
	UrlEdit.py\
	Utils.py\
	Witness.py\
	WriteGedcom.py \
	WriteXML.py\
	SelectPerson.py\
	ArgHandler.py\
	Exporter.py\
	GrampsKeys.py\
	GrampsIniKeys.py\
	GrampsGconfKeys.py\
	RecentFiles.py\
	ReportOptions.py\
	ReadGrdb.py\
	WriteGrdb.py

# Could use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all files individually
# The latter is more portable and POSIX-friendly :)
GLADEFILES = \
	gramps.glade\
	mergedata.glade\
	gedcomexport.glade\
	gedcomimport.glade\
	plugins.glade\
	rule.glade

GRAPHICS = \
	bad.png\
	caution.png\
	edit.png\
	edit_sm.png \
	family48.png\
	good.png\
	home.png\
	logo.png\
	gramps.png \
	media.png\
	people48.png\
	place.png\
	sources.png\
	splash.jpg\
	tools.png

# Other stuff that we need to install
dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) 

# In principle the following rule slightly  violates the automake/autoconf 
# spirit of keeping each subdirectory as a separate entity unto itself. 
# But, since the template depends on everything from here, we allow this
# one exception.
# Build po/template.po.
.PHONY: trans
trans:
	./build_po

pycheck: 
	for d in $(SUBDIRS) ; do \
          (cd $$d; make pycheck); \
	done;
	pychecker $(gdir_PYTHON)

docs:
	epydoc -o doc --url http://gramps.sourceforge.net --name GRAMPS --html $(docfiles)
	epydoc --pdf $(docfiles)
