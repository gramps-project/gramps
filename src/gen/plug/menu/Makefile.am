# This is the src/gen/plug/menu level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/plug/menu

pkgdata_PYTHON = \
	__init__.py \
	_boolean.py \
	_color.py \
	_destination.py \
	_enumeratedlist.py \
	_family.py \
	_filter.py \
	_media.py \
	_menu.py \
	_note.py \
	_number.py \
	_option.py \
	_person.py \
	_personlist.py \
	_placelist.py \
	_string.py \
	_style.py \
	_surnamecolor.py \
	_text.py \
	_translation.py

pkgpyexecdir = @pkgpyexecdir@/gen/plug/menu
pkgpythondir = @pkgpythondir@/gen/plug/menu


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
