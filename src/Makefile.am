# This is the src level Makefile for Gramps
SUBDIRS = docgen filters plugins data po

# For intl. support, how do we compile?
CFLAGS = -fPIC -shared -O @CFLAGS@ @CPPFLAGS@ -I@includedir@
LDFLAGS = @LDFLAGS@ -L@libdir@ @LIBS@
CLEANFILES = ${INTLLIBS}
MOSTLYCLEANFILES = 

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead
pkgpython_PYTHON = AddMedia.py \
		 AddrEdit.py \
		 AddSpouse.py \
		 AttrEdit.py \
		 AutoComp.py \
		 Bookmarks.py \
		 Calendar.py \
		 ChooseParents.py \
		 const.py \
		 DateEdit.py \
		 Date.py \
		 DbPrompter.py \
		 DisplayTrace.py \
		 DrawDoc.py \
		 EditPerson.py \
		 EditPlace.py \
		 EditSource.py \
		 EventEdit.py \
		 Filter.py \
		 Find.py \
		 FontScale.py \
		 GedcomInfo.py \
		 GenericFilter.py \
		 GrampsCfg.py \
		 gramps_main.py \
		 GrampsParser.py \
		 gramps.py \
		 GrampsXML.py \
		 GrampsZODB.py \
		 GraphLayout.py \
		 ImageSelect.py \
		 ImgManip.py \
		 intl.py \
		 latin_ansel.py \
		 latin_utf8.py \
		 LocEdit.py \
		 Marriage.py \
		 MediaView.py \
		 MergeData.py \
		 NameEdit.py \
		 NoteEdit.py \
		 PaperMenu.py \
		 PedView.py \
		 PlaceView.py \
		 Plugins.py \
		 QuestionDialog.py \
		 QuickAdd.py \
		 ReadXML.py \
		 RelImage.py \
		 RelLib.py \
		 Report.py \
		 SelectChild.py \
		 Sorter.py \
		 sort.py \
		 soundex.py \
		 Sources.py \
		 SourceView.py \
		 SpreadSheetDoc.py \
		 StartupDialog.py \
		 StyleEditor.py \
		 SubstKeywords.py \
		 TarFile.py \
		 TextDoc.py \
		 UrlEdit.py \
		 Utils.py \
		 VersionControl.py \
		 WriteXML.py 


# Could use GNU make's ':=' syntax for nice wildcard use but since
# GNU make is not POSIX-compliant, we list all files individually
GLADEFILES = config.glade \
	   dialog.glade \
	   EditPerson.glade \
	   gramps.glade \
	   imagesel.glade \
	   marriage.glade \
	   mergedata.glade \
	   places.glade \
	   plugins.glade \
	   preferences.glade \
	   revision.glade \
	   rule.glade \
	   srcsel.glade \
	   styles.glade 
XPMFILES = earth.xpm \
	 fam.xpm \
	 gramps.xpm \
	 pedegree.xpm \
	 people.xpm 


PNGFILES = gramps.png \
	 logo.png

JPGFILES = splash.jpg

GRAPHICS = ${XPMFILES} ${PNGFILES} ${JPGFILES}

# Other stuff that we need to install
pkgdata_DATA = ${INTLLIBS} ${GLADEFILES} ${GRAPHICS} gramps.desktop

#EXTRA_DIST =@DISTLANGS@


all: ${INTLLIBS}

DIST_SOURCES = intl.c
dist_pkgdata_DATA = ${GLADEFILES} ${GRAPHICS} gramps.desktop

# These can prbably be done in a better or more elegant/generic way 
# eventually (libtool?), but this works.
intl15.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P15_INCLUDES@ -DVER15 -o $@ intl.c
intl20.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P20_INCLUDES@ -DVER20 -o $@ intl.c
intl21.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P21_INCLUDES@ -DVER21 -o $@ intl.c
intl22.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P22_INCLUDES@ -DVER22 -o $@ intl.c

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
