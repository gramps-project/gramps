# This is the src/DisplayTabs level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/DisplayTabs

pkgdata_PYTHON = \
	_AddrEmbedList.py \
	_AddressModel.py \
	_AttrEmbedList.py \
	_AttrModel.py \
	_BackRefList.py \
	_BackRefModel.py \
	_ButtonTab.py \
	_ChildModel.py \
	_DataEmbedList.py \
	_DataModel.py \
	_EmbeddedList.py \
	_EventBackRefList.py \
	_EventEmbedList.py \
	_EventRefModel.py \
	_FamilyAttrEmbedList.py \
	_FamilyLdsEmbedList.py \
	_GalleryTab.py \
	_GrampsTab.py \
	_LdsEmbedList.py \
	_LdsModel.py \
	_LocationEmbedList.py \
	_LocationModel.py \
	_MediaBackRefList.py \
	_NameEmbedList.py \
	_NameModel.py \
	_NoteTab.py \
	_PersonEventEmbedList.py \
	_PersonRefEmbedList.py \
	_PersonRefModel.py \
	_PlaceBackRefList.py \
	_RepoEmbedList.py \
	_RepoRefModel.py \
	_SourceBackRefList.py \
	_SourceEmbedList.py \
	_SourceRefModel.py \
	_WebEmbedList.py \
	_WebModel.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/DisplayTabs
pkgpythondir = @pkgpythondir@/DisplayTabs

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
