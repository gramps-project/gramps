# This is the src level Makefile for Gramps
SUBDIRS = docgen filters plugins data po calendars

# For intl. support, how do we compile?
CFLAGS = -fPIC -shared -O @GNOMEINC@ @CFLAGS@ @CPPFLAGS@ -I@includedir@
LDFLAGS = @GNOMELIB@ @LDFLAGS@ -L@libdir@ @LIBS@
CLEANFILES = grampslib.so
MOSTLYCLEANFILES = 

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
	BaseDoc.py\
	Bookmarks.py\
	Calendar.py\
	ChooseParents.py\
	const.py\
	DateEdit.py\
	Date.py\
	DbPrompter.py\
	DisplayTrace.py\
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
	PeopleStore.py\
	PlaceView.py\
	Plugins.py\
	QuestionDialog.py\
	ReadXML.py\
	Relationship.py\
	RelImage.py\
	RelLib.py\
	Report.py\
	SelectChild.py\
	SelectObject.py\
	sort.py\
	soundex.py\
	Sources.py\
	SourceView.py\
	SpreadSheetDoc.py\
	StartupDialog.py\
	StyleEditor.py\
	SubstKeywords.py\
	TarFile.py\
	UrlEdit.py\
	Utils.py\
	VersionControl.py\
	Witness.py\
	WriteXML.py\
	SelectPerson.py\
	ArgHandler.py

# Could use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all files individually
# The latter is more portable and POSIX-friendly :)
GLADEFILES = \
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
	styles.glade\
        choose.glade

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
	splash.jpg\
	tools.png

# Other stuff that we need to install
dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) gramps.desktop papersize.xml

EXTRA_DIST = grampslib.i grampslib_wrap.c

all-local: grampslib.so

# These can probably be done in a better or more elegant/generic way 
# eventually (libtool?), but this works.

grampslib.so: $(srcdir)/grampslib_wrap.c
	$(CC) $(CFLAGS) $(PYTHON_CPPFLAGS) -o $@ $(srcdir)/grampslib_wrap.c $(LDFLAGS) 

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
	pychecker $(pkgpython_PYTHON)

install-data-local:
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL_DATA) $(srcdir)/gramps.png $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL_DATA) $(srcdir)/gramps.desktop $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL) -d $(DESTDIR)$(pkglibdir)
	$(INSTALL_DATA) grampslib.so $(DESTDIR)$(pkglibdir)

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/pixmaps/gramps.png
	-rm $(DESTDIR)$(prefix)/share/gnome/apps/Applications/gramps.desktop
	-rm $(DESTDIR)$(pkglibdir)/grampslib.so
