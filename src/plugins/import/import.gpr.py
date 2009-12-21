#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#------------------------------------------------------------------------
#
# Comma _Separated Values Spreadsheet (CSV)
#
#------------------------------------------------------------------------

_mime_type = "text/x-comma-separated-values" # CSV Document
_mime_type_rfc_4180 = "text/csv" # CSV Document   See rfc4180 for mime type
plg = newplugin()
plg.id    = 'im_csv'
plg.name  = _("Comma _Separated Values Spreadsheet (CSV)")
plg.description =  _("Import data from CSV files")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportCsv.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "csv"

#------------------------------------------------------------------------
#
# GEDCOM
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_ged'
plg.name  = _('GEDCOM')
plg.description =  _('GEDCOM is used to transfer data between genealogy programs. '
                'Most genealogy software will accept a GEDCOM file as input.')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportGedcom.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "ged"

#------------------------------------------------------------------------
#
# Geneweb
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_geneweb'
plg.name  = _('GeneWeb')
plg.description =  _('Import data from GeneWeb files')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportGeneWeb.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "gw"

#------------------------------------------------------------------------
#
# GRAMPS package (portable XML)
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_gpkg'
plg.name  = _('Gramps package (portable XML)')
plg.description =  _('Import data from a Gramps package (an archived XML '
                     'family tree together with the media object files.')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportGpkg.py'
plg.ptype = IMPORT
plg.import_function = 'impData'
plg.extension = "gpkg"

#------------------------------------------------------------------------
#
# GRAMPS XML database
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_gramps'
plg.name  = _('Gramps XML Family Tree')
plg.description =  _('The Gramps XML format is a text '
                     'version of a family tree. It is '
                     'read-write compatible with the '
                     'present Gramps database format.')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportXml.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "gramps"

#------------------------------------------------------------------------
#
# GRDB database
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_grdb'
plg.name  = _('Gramps 2.x database')
plg.description =  _('Import data from Gramps 2.x database files')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportGrdb.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "grdb"

#------------------------------------------------------------------------
#
# Pro-Gen Files
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_progen'
plg.name  = _('Pro-Gen')
plg.description =  _('Import data from Pro-Gen files')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportProGen.py'
plg.ptype = IMPORT
plg.import_function = '_importData'
plg.extension = "def"

#------------------------------------------------------------------------
#
# vCard
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_vcard'
plg.name  = _('vCard')
plg.description =  _('Import data from vCard files')
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ImportVCard.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "vcf"
