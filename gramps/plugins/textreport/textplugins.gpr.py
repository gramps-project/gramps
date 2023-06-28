# encoding:utf-8
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
from gramps.gen.plug._pluginreg import *
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

MODULE_VERSION="5.2"

# this is the default in gen/plug/_pluginreg.py: plg.require_active = True

#------------------------------------------------------------------------
#
# Ancestor Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'ancestor_report'
plg.name = _("Ahnentafel Report")
plg.description = _("Produces a textual ancestral report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'ancestorreport.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'AncestorReport'
plg.optionclass = 'AncestorOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Birthday Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'birthday_report'
plg.name = _("Birthday and Anniversary Report")
plg.description = _("Produces a report of birthdays and anniversaries")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'birthdayreport.py'
plg.ptype = REPORT
plg.authors = ["Douglas S. Blank"]
plg.authors_email = ["dblank@cs.brynmawr.edu"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'BirthdayReport'
plg.optionclass = 'BirthdayOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Custom text BookItem
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'custom_text'
plg.name = _("Custom Text")
plg.description = _("Add custom text to the book report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'custombooktext.py'
plg.ptype = REPORT
plg.authors = ["The Gramps Project"]
plg.authors_email = [""]
plg.category = CATEGORY_TEXT
plg.reportclass = 'CustomText'
plg.optionclass = 'CustomTextOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Descendant Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'descend_report'
plg.name = _("Descendant Report")
plg.description = _("Produces a list of descendants of the active person")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'descendreport.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DescendantReport'
plg.optionclass = 'DescendantOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Detailed Ancestral Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'det_ancestor_report'
plg.name = _("Detailed Ancestral Report")
plg.description = _("Produces a detailed ancestral report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'detancestralreport.py'
plg.ptype = REPORT
plg.authors = ["Bruce DeGrasse"]
plg.authors_email = ["bdegrasse1@attbi.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DetAncestorReport'
plg.optionclass = 'DetAncestorOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Detailed Descendant Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'det_descendant_report'
plg.name = _("Detailed Descendant Report")
plg.description = _("Produces a detailed descendant report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'detdescendantreport.py'
plg.ptype = REPORT
plg.authors = ["Bruce DeGrasse"]
plg.authors_email = ["bdegrasse1@attbi.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DetDescendantReport'
plg.optionclass = 'DetDescendantOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# End of Line Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'endofline_report'
plg.name = _("End of Line Report")
plg.description = _("Produces a textual end of line report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'endoflinereport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'EndOfLineReport'
plg.optionclass = 'EndOfLineOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Family Group Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'family_group'
plg.name = _("Family Group Report")
plg.description = _("Produces a family group report showing information "
                    "on a set of parents and their children.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'familygroup.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'FamilyGroup'
plg.optionclass = 'FamilyGroupOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Complete Individual Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'indiv_complete'
plg.name = _("Complete Individual Report")
plg.description = _("Produces a complete report on the selected people")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'indivcomplete.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'IndivCompleteReport'
plg.optionclass = 'IndivCompleteOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Kinship Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'kinship_report'
plg.name = _("Kinship Report")
plg.description = _("Produces a textual report of kinship for a given person")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'kinshipreport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'KinshipReport'
plg.optionclass = 'KinshipOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Tag Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'tag_report'
plg.name = _("Tag Report")
plg.description = _("Produces a list of people with a specified tag")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'tagreport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'TagReport'
plg.optionclass = 'TagOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Number of Ancestors Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'number_of_ancestors'
plg.name = _("Number of Ancestors Report")
plg.description = _("Counts number of ancestors of selected person")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'numberofancestorsreport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'NumberOfAncestorsReport'
plg.optionclass = 'NumberOfAncestorsOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Place Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'place_report'
plg.name = _("Place Report")
plg.description = _("Produces a textual place report")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'placereport.py'
plg.ptype = REPORT
plg.authors = ["Gary Burton"]
plg.authors_email = ["gary.burton@zen.co.uk"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'PlaceReport'
plg.optionclass = 'PlaceOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Book Title Page
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'simple_book_title'
plg.name = _("Title Page")
plg.description = _("Produces a title page for book reports.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'simplebooktitle.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'SimpleBookTitle'
plg.optionclass = 'SimpleBookTitleOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Database Summary Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'summary'
plg.name = _("Database Summary Report")
plg.description = _("Provides a summary of the current database")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'summary.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'SummaryReport'
plg.optionclass = 'SummaryOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Table Of Contents
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'table_of_contents'
plg.name = _("Table Of Contents")
plg.description = _("Produces a table of contents for book reports.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'tableofcontents.py'
plg.ptype = REPORT
plg.authors = ["Nick Hall"]
plg.authors_email = ["nick__hall@hotmail.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'TableOfContents'
plg.optionclass = 'TableOfContentsOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Alphabetical Index
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'alphabetical_index'
plg.name = _("Alphabetical Index")
plg.description = _("Produces an alphabetical index for book reports.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'alphabeticalindex.py'
plg.ptype = REPORT
plg.authors = ["Nick Hall"]
plg.authors_email = ["nick__hall@hotmail.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'AlphabeticalIndex'
plg.optionclass = 'AlphabeticalIndexOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Records Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'records'
plg.name = _("Records Report")
plg.description = _("Shows some interesting records about people and families")
plg.version = '1.1'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'recordsreport.py'
plg.ptype = REPORT
plg.authors = ["Reinhard Müller"]
plg.authors_email = ["reinhard.mueller@bytewise.at"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'RecordsReport'
plg.optionclass = 'RecordsReportOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI, REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Note Link Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'notelinkreport'
plg.name = _("Note Link Report")
plg.description = _("Shows status of links in notes")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'notelinkreport.py'
plg.ptype = REPORT
plg.authors = ["Doug Blank"]
plg.authors_email = ["doug.blank@gmail.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'NoteLinkReport'
plg.optionclass = 'NoteLinkOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI, REPORT_MODE_BKI]
