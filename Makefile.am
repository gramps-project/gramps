# copyright (C) 2000 Sun Microsystems, Inc.

SUBDIRS = src doc example

EXTRA_DIST = autogen.sh gramps.spec.in COPYING-DOCS

bin_SCRIPTS = gramps

gramps: gramps.sh
	cp gramps.sh gramps

dist-hook: gramps.spec
	cp gramps.spec $(distdir)
