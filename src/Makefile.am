# This is the src level Makefile for Gramps
SUBDIRS = docgen filters plugins data po

# For intl. support, how do we compile?
GVFSINC = @GPREF@
CFLAGS = -fPIC -shared -O @GNOMEINC@ @CFLAGS@ @CPPFLAGS@ -I@includedir@
LDFLAGS = @GNOMELIB@ @LDFLAGS@ -L@libdir@ @LIBS@
CLEANFILES = ${INTLLIBS}
MOSTLYCLEANFILES = 

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead
pkgpython_PYTHON = ${wildcard *.py}

# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all files individually
GLADEFILES := ${wildcard *.glade}
GRAPHICS := ${wildcard *.xpm} ${wildcard *.png} ${wildcard *.jpg}

# Other stuff that we need to install
pkgdata_DATA = ${INTLLIBS} ${GLADEFILES} ${GRAPHICS} gramps.desktop

#EXTRA_DIST =@DISTLANGS@


all: ${INTLLIBS} grampslib.so

DIST_SOURCES = intl.c
dist_pkgdata_DATA = ${pkgdata_DATA} 

# These can prbably be done in a better or more elegant/generic way 
# eventually (libtool?), but this works.
intl22.so: intl.c
	$(CC) $(CFLAGS) $(LDFLAGS) @P22_INCLUDES@ -DVER22 -o $@ intl.c

grampslib.so: grampslib.i
	swig -python grampslib.i 
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
