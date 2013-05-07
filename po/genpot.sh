#!/bin/sh
# $Id$

# Make translation files

# additional keywords must always be kept in sync with those in update_po.py
XGETTEXT_ARGS='--keyword=_T_ --keyword=trans_text' \
  intltool-update -g gramps -o gramps.pot -p
