# This is the src/plugins/rel level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/rel

pkgdata_PYTHON = \
	relplugins.gpr.py\
	rel_cs.py\
	rel_da.py\
	rel_de.py\
	rel_es.py\
	rel_fi.py\
	rel_fr.py\
	rel_hu.py\
	rel_it.py\
	rel_nl.py\
	rel_no.py\
	rel_pl.py\
	rel_pt.py\
	rel_ru.py\
	rel_sk.py\
	rel_sv.py

pkgpyexecdir = @pkgpyexecdir@/plugins/rel
pkgpythondir = @pkgpythondir@/plugins/rel

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
