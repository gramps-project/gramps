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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from gramps.gen.plug._pluginreg import newplugin, STABLE, EXPORT
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.2"

# ------------------------------------------------------------------------
#
# Comma _Separated Values Spreadsheet (CSV)
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_csv"
plg.name = _("Comma Separated Values Spreadsheet (CSV)")
plg.name_accell = _("Comma _Separated Values Spreadsheet (CSV)")
plg.description = _(
    "CSV is a common spreadsheet format."
    "\nYou can change this behavior in the 'Configure active"
    " view' of any list-based view"
)
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportcsv.py"
plg.ptype = EXPORT
plg.export_function = "exportData"
plg.export_options = "CSVWriterOptionBox"
plg.export_options_title = _("CSV spreadsheet options")
plg.extension = "csv"

# ------------------------------------------------------------------------
#
# Web Family Tree export
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_webfamtree"
plg.name = _("Web Family Tree")
plg.name_accell = _("_Web Family Tree")
plg.description = _("Web Family Tree format")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportftree.py"
plg.ptype = EXPORT
plg.export_function = "writeData"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("Web Family Tree export options")
plg.extension = "wft"

# ------------------------------------------------------------------------
#
# GEDCOM
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_ged"
plg.name = _("GEDCOM")
plg.name_accell = _("GE_DCOM")
plg.description = _(
    "GEDCOM is used to transfer data between genealogy programs. "
    "Most genealogy software will accept a GEDCOM file as input."
)
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportgedcom.py"
plg.ptype = EXPORT
plg.export_function = "export_data"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("GEDCOM export options")
plg.extension = "ged"

# ------------------------------------------------------------------------
#
# Geneweb
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_geneweb"
plg.name = _("GeneWeb")
plg.name_accell = _("_GeneWeb")
plg.description = _("GeneWeb is a web based genealogy program.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportgeneweb.py"
plg.ptype = EXPORT
plg.export_function = "exportData"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("GeneWeb export options")
plg.extension = "gw"

# ------------------------------------------------------------------------
#
# Gramps package (portable XML)
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_gpkg"
plg.name = _("Gramps XML Package (family tree and media)")
plg.name_accell = _("Gra_mps XML Package (family tree and media)")
plg.description = _(
    "Gramps package is an archived XML family tree together "
    "with the media object files."
)
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportpkg.py"
plg.ptype = EXPORT
plg.export_function = "writeData"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("Gramps package export options")
plg.extension = "gpkg"

# ------------------------------------------------------------------------
#
# Gramps XML database
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_gramps"
plg.name = _("Gramps XML (family tree)")
plg.name_accell = _("Gramps _XML (family tree)")
plg.description = _(
    "Gramps XML export is a complete archived XML backup of a"
    " Gramps family tree without the media object files."
    " Suitable for backup purposes."
)
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportxml.py"
plg.ptype = EXPORT
plg.export_function = "export_data"
plg.export_options = "WriterOptionBoxWithCompression"
plg.export_options_title = _("Gramps XML export options")
plg.extension = "gramps"

# ------------------------------------------------------------------------
#
# vCalendar
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_vcal"
plg.name = _("vCalendar")
plg.name_accell = _("vC_alendar")
plg.description = _("vCalendar is used in many calendaring and PIM applications.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportvcalendar.py"
plg.ptype = EXPORT
plg.export_function = "exportData"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("vCalendar export options")
plg.extension = "vcs"

# ------------------------------------------------------------------------
#
# vCard
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "ex_vcard"
plg.name = _("vCard")
plg.name_accell = _("_vCard")
plg.description = _("vCard is used in many addressbook and pim applications.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "exportvcard.py"
plg.ptype = EXPORT
plg.export_function = "exportData"
plg.export_options = "WriterOptionBox"
plg.export_options_title = _("vCard export options")
plg.extension = "vcf"
