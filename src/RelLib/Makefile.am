# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/RelLib

pkgdata_PYTHON = \
	_AddressBase.py\
	_Address.py\
	_AttributeBase.py\
	_Attribute.py\
	_BaseObject.py\
	_CalSdn.py \
	_Date.py \
	_DateBase.py\
	_Event.py\
	_EventType.py\
	_EventRef.py\
	_Family.py\
	_GenderStats.py\
	_GrampsType.py\
	__init__.py\
	_LdsOrdBase.py\
	_LdsOrd.py\
	_LocationBase.py\
	_Location.py\
	_MediaBase.py\
	_MediaObject.py\
	_MediaRef.py\
	_Name.py\
	_NameType.py\
	_NoteBase.py\
	_Note.py\
	_Person.py\
	_PersonRef.py\
	_PlaceBase.py\
	_Place.py\
	_PrimaryObject.py\
	_PrivacyBase.py\
	_PrivateSourceNote.py\
	_RepoRef.py\
	_Repository.py\
	_RepositoryType.py\
	_Researcher.py\
	_SourceNote.py\
	_Source.py\
	_SourceRef.py\
	_UrlBase.py\
	_UrlType.py\
	_Url.py\
	_Witness.py\
	_SourceBase.py\
	_RefBase.py\
	_ChildRef.py\
	_AttributeType.py\
	_ChildRefType.py\
	_FamilyRelType.py\
	_SourceMediaType.py\
	_MarkerType.py\
	_EventRoleType.py

pkgpyexecdir = @pkgpyexecdir@/RelLib
pkgpythondir = @pkgpythondir@/RelLib

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
