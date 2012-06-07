# This is the src level Makefile for Gramps
# $Id$

SUBDIRS = \
	cli \
	data \
	docgen \
	gen \
	gui \
	images \
	plugins

gdirdir=$(prefix)/share/gramps

gdir_PYTHON = \
	AutoComp.py\
	config.py\
	const.py\
        constfunc.py\
	DateEdit.py\
	ExportAssistant.py\
	ExportOptions.py\
	gramps.py\
	ImgManip.py\
	LdsUtils.py \
	Lru.py\
	MacTransUtils.py\
	Relationship.py\
	Reorder.py\
	Sort.py\
	soundex.py\
	Spell.py\
	ToolTips.py\
	TransUtils.py\
	TreeTips.py\
	Utils.py\
	PlaceUtils.py

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
