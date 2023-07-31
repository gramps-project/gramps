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

MODULE_VERSION = "5.2"

# ------------------------------------------------------------------------
#
# Narrated Web Site
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "navwebpage"
plg.name = _("Narrated Web Site")
plg.description = _(
    "Produces web (HTML) pages for individuals, or a set of " "individuals"
)
plg.version = "2.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "narrativeweb.py"
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham", "Rob G. Healey", "Serge Noiraud"]
plg.authors_email = ["don@gramps-project.org", "serge.noiraud@free.fr"]
plg.category = CATEGORY_WEB
plg.reportclass = "NavWebReport"
plg.optionclass = "NavWebOptions"
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]


# ------------------------------------------------------------------------
#
# Web Calendar
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "WebCal"
plg.name = _("Web Calendar")
plg.description = _("Produces web (HTML) calendars.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "webcal.py"
plg.ptype = REPORT
plg.authors = ["Thom Sturgill", "Rob G. Healey"]
plg.authors_email = ["thsturgill@yahoo.com", "robhealey1@gmail.com"]
plg.category = CATEGORY_WEB
plg.reportclass = "WebCalReport"
plg.optionclass = "WebCalOptions"
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
