# This is the src level Makefile for Gramps
SUBDIRS = docgen filters plugins data po calendars

# For intl. support, how do we compile?
GVFSINC = @GPREF@
CFLAGS = -fPIC -shared -O @GNOMEINC@ @CFLAGS@ @CPPFLAGS@ -I@includedir@
LDFLAGS = @GNOMELIB@ @LDFLAGS@ -L@libdir@ @LIBS@
CLEANFILES = ${INTLLIBS}
MOSTLYCLEANFILES = 
INTLLIBS= intl22.so

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead

pkgpython_PYTHON = \
	AddMedia.py\
	AddrEdit.py\
	AddSpouse.py\
	ansel_utf8.py\
	AttrEdit.py\
	AutoComp.py\
	Bookmarks.py\
	Calendar.py\
	ChooseParents.py\
	const.py\
	DateEdit.py\
	Date.py\
	DbPrompter.py\
	DisplayTrace.py\
	DrawDoc.py\
	EditPerson.py\
	EditPlace.py\
	EditSource.py\
	Errors.py\
	EventEdit.py\
	FamilyView.py\
	Filter.py\
	Find.py\
	FontScale.py\
	FrenchRepublic.py\
	GedcomInfo.py\
	GenericFilter.py\
	GrampsCfg.py\
	gramps_main.py\
	GrampsParser.py\
	gramps.py\
	GrampsXML.py\
	GrampsZODB.py\
	GraphLayout.py\
	Gregorian.py\
	Hebrew.py\
	ImageSelect.py\
	ImgManip.py\
	intl.py\
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
	PlaceView.py\
	Plugins.py\
	QuestionDialog.py\
	QuickAdd.py\
	ReadXML.py\
	RelImage.py\
	RelLib.py\
	Report.py\
	SelectChild.py\
	sort.py\
	soundex.py\
	Sources.py\
	SourceView.py\
	SpreadSheetDoc.py\
	StartupDialog.py\
	StyleEditor.py\
	SubstKeywords.py\
	TarFile.py\
	TextDoc.py\
	UrlEdit.py\
	Utils.py\
	VersionControl.py\
	Witness.py\
	WriteXML.py

# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all files individually
GLADEFILES = \
	config.glade\
	dialog.glade\
	edit_person.glade\
	errdialogs.glade\
	gramps.glade\
	imagesel.glade\
	marriage.glade\
	mergedata.glade\
	places.glade\
	plugins.glade\
	preferences.glade\
	revision.glade\
	rule.glade\
	srcsel.glade\
	styles.glade

GRAPHICS = \
	bad.png\
	caution.png\
	edit.png\
	family48.png\
	good.png\
	gramps.png\
	gramps.xpm\
	logo.png\
	media.png\
	pedigree.xpm\
	people48.png\
	people.xpm\
	place.png\
	sources.png\
	splash.jpg

# Other stuff that we need to install
pkgdata_DATA = ${INTLLIBS} ${GLADEFILES} ${GRAPHICS} gramps.desktop grampslib.so

EXTRA_DIST = grampslib.i

all: ${INTLLIBS} grampslib.so

DIST_SOURCES = intl.c grampslib_wrap.c
dist_pkgdata_DATA = ${pkgdata_DATA} 

# These can prbably be done in a better or more elegant/generic way 
# eventually (libtool?), but this works.
intl22.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P22_INCLUDES@ -DVER22 -o $@ intl.c

grampslib.so: grampslib_wrap.c
	$(CC) $(CFLAGS) @P22_INCLUDES@ -o $@ grampslib_wrap.c $(LDFLAGS) 

# In principle the following rule slightly  violates the automake/autoconf 
# spirit of keeping each subdirectory as a separate entity unto itself. 
# But, since the template depends on everything from here, we allow this
# one exception.
trans: po/template.po
	./build_po

install-data-local:
	${INSTALL} -d ${prefix}/share/pixmaps
	${INSTALL_DATA} gramps.png ${prefix}/share/pixmaps
	${INSTALL} -d ${prefix}/share/gnome/apps/Applications
	${INSTALL_DATA} gramps.desktop ${prefix}/share/gnome/apps/Applications

uninstall-local:
	-rm ${prefix}/share/pixmaps/gramps.png
	-rm ${prefix}/share/gnome/apps/Applications/gramps.desktop
