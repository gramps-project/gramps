# This is the src/calendars level Makefile for Gramps
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually

calendardir = $(datadir)/@PACKAGE@/calendars

calendar_PYTHON = \
	Islamic.py \
	Persian.py


GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
