SUBDIRS = src doc example

EXTRA_DIST = autogen.sh gramps.spec.in gramps.spec gramps-mdk.spec gramps-mdk.spec.in COPYING-DOCS FAQ

bin_SCRIPTS = gramps

gramps: gramps.sh
	cp gramps.sh gramps

.PHONY: pycheck trans

pycheck:
	(cd src; make pycheck) 
trans:
	(cd src; make trans) 

CLEANFILES = gramps
