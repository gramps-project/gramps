# This is the src level Makefile for Gramps
SUBDIRS = docgen plugins data po calendars

# For intl. support, how do we compile?
MOSTLYCLEANFILES = 

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead

gdirdir=$(DESTDIR)$(prefix)/share/gramps

gdir_PYTHON = \
	AddMedia.py\
	AddrEdit.py\
	AddSpouse.py\
	ansel_utf8.py\
	AttrEdit.py\
	AutoComp.py\
	BaseDoc.py\
	Bookmarks.py\
	Calendar.py\
	ColumnOrder.py\
	ChooseParents.py\
	const.py\
	DateEdit.py\
	Date.py\
	DbPrompter.py\
	DisplayModels.py\
	DisplayTrace.py\
	EditPerson.py\
	EditPlace.py\
	EditSource.py\
	Errors.py\
	EventEdit.py\
	FamilyView.py\
	FontScale.py\
	FrenchRepublic.py\
	GedcomInfo.py\
	GenericFilter.py\
	GrampsCfg.py\
	GrampsBSDDB.py\
	GrampsDbBase.py\
	GrampsXMLDB.py\
	GrampsGEDDB.py\
	GrampsMime.py\
	gramps_main.py\
	gramps.py\
	GraphLayout.py\
	Gregorian.py\
	Hebrew.py\
	ImageSelect.py\
	ImgManip.py\
	Julian.py\
	latin_ansel.py\
	latin_utf8.py\
	ListModel.py\
	LocEdit.py\
	Marriage.py\
	MediaView.py\
	MergeData.py\
	NameEdit.py\
	NoteEdit.py\
	PaperMenu.py\
	PedView.py\
	PeopleView.py\
	PeopleModel.py\
	PlaceView.py\
	Plugins.py\
	QuestionDialog.py\
	ReadGedcom.py \
	ReadXML.py\
	Relationship.py\
	RelImage.py\
	RelLib.py\
	Report.py\
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
	UrlEdit.py\
	Utils.py\
	Witness.py\
	WriteGedcom.py \
	WriteXML.py\
	SelectPerson.py\
	ArgHandler.py\
	Exporter.py

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

