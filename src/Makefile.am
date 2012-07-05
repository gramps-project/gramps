# This is the src level Makefile for Gramps
# $Id$

SUBDIRS = \
	cli \
	data \
	gen \
	gui \
	images \
	plugins

gdirdir=$(prefix)/share/gramps

gdir_PYTHON = gramps.py

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
