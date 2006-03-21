# This is the data level Makefile for gramps
# $Id$

SUBDIRS = man

# Rules for files with translatable strings
# These are taken care of by the intltool
desktopdir = $(datadir)/applications
desktop_in_files = gramps.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

keys_in_files = gramps.keys.in
keys_files = $(keys_in_files:.keys.in=.keys)
@INTLTOOL_KEYS_RULE@

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = gramps.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

schemasdir = $(GCONF_SCHEMA_FILE_DIR)
schemas_in_files = gramps.schemas.in
schemas_DATA = $(schemas_in_files:.schemas.in=.schemas)
@INTLTOOL_SCHEMAS_RULE@

applicationsdir = $(datadir)/application-registry
applications_DATA = gramps.applications

mimedir = $(datadir)/mime-info
mime_DATA = $(keys_files) gramps.mime

xmldir = $(SHARED_MIME_DIR)/packages
xml_DATA = $(xml_files)

pngdir = $(datadir)/icons/gnome/48x48/mimetypes
png_DATA = \
	gnome-mime-application-x-gramps.png \
	gnome-mime-application-x-gedcom.png \
	gnome-mime-application-x-gramps-package.png \
	gnome-mime-application-x-gramps-xml.png \
	gnome-mime-application-x-geneweb.png

EXTRA_DIST = \
	$(png_DATA) \
	$(applications_DATA) \
	$(keys_in_files) \
	$(desktop_in_files) \
	$(schemas_in_files) \
	$(mime_DATA) \
	$(xml_DATA) \
	$(desktop_DATA) \
	$(schemas_DATA) \
	$(xml_in_files)

CLEANFILES = \
	$(desktop_DATA) \
	$(keys_files) \
	$(xml_files) \
	$(schemas_DATA)

# Conditionally enable/disable gconf schemas or mime types,
# or disable both in a packager mode
GCONF_SCHEMAS_INSTALLATION =
GCONF_SCHEMAS_UNINSTALLATION = 
SHARED_MIME_INSTALLATION =
SHARED_MIME_UNINSTALLATION =

if !PACKAGER_MODE
if GCONF_SCHEMAS_INSTALL
GCONF_SCHEMAS_INSTALLATION += \
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas ;\
	pkill gconfd ; echo Restarting gconfd

GCONF_SCHEMAS_UNINSTALLATION += \
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-uninstall-rule $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas
endif
if SHARED_MIME_INSTALL
SHARED_MIME_INSTALLATION += \
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
SHARED_MIME_UNINSTALLATION += \
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
endif
endif


install-data-hook:
	$(SHARED_MIME_INSTALLATION)
	$(GCONF_SCHEMAS_INSTALLATION)

uninstall-local:
	$(GCONF_SCHEMAS_UNINSTALLATION)

uninstall-hook:
	$(SHARED_MIME_UNINSTALLATION)
