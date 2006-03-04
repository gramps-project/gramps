# $Id: Makefile.am 6057 2006-03-03 12:49:39Z loshawlos $

# This is the src level Makefile for Gramps
SUBDIRS = 

# For intl. support, how do we compile?
MOSTLYCLEANFILES = 
CLEANFILES = 

# What are the PYTHON scripts for this package that need to be handled?
#
# We only want optimized byte-compiled (.pyo) versions, no .pyc
# In principle, this is handled by PYCFILES and PYOFILES, but
# they don't seem to work so we edited the py-compile script instead

# Could use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all files individually
# The latter is more portable and POSIX-friendly :)
IMAGEFILES = \
	bad.png\
	caution.png\
	edit.png\
	edit_sm.png\
	events24.png\
	events.png\
	flist.svg\
	good.png\
	gramps.png\
	land_shallow_topo_2048.jpg\
	land_shallow_topo_350.jpg\
	locked.png\
	logo.png\
	media.png\
	media.svg\
	ped24.png\
	person.svg\
	place24.png\
	place.png\
	relation.svg\
	repos24.png\
	repos.png\
	sources24.png\
	sources.png\
	splash.jpg\
	stock_link.png\
	tools.png

# Other stuff that we need to install
dist_pkgdata_DATA = $(IMAGEFILES)

