# This is the src/plugins level Makefile for Gramps
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually
pkgpython_PYTHON := ${wildcard *.py}
pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES := ${wildcard *.glade}

pkgdatadir = ${datadir}/@PACKAGE@/plugins

pkgdata_DATA = ${GLADEFILES}
dist_pkgdata_DATA = ${pkgdata_DATA} 

