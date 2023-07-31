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

# this is the default in gen/plug/_pluginreg.py: plg.require_active = True

# ------------------------------------------------------------------------
#
# Family Lines Graph
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "familylines_graph"
plg.name = _("Family Lines Graph")
plg.description = _("Produces family line graphs using Graphviz.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "gvfamilylines.py"
plg.ptype = REPORT
plg.authors = ["Stephane Charette"]
plg.authors_email = ["stephanecharette@gmail.com"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = "FamilyLinesReport"
plg.optionclass = "FamilyLinesOptions"
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
plg.require_active = False

# ------------------------------------------------------------------------
#
# Hourglass Graph
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "hourglass_graph"
plg.name = _("Hourglass Graph")
plg.description = _("Produces an hourglass graph using Graphviz.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "gvhourglass.py"
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = "HourGlassReport"
plg.optionclass = "HourGlassOptions"
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

# ------------------------------------------------------------------------
#
# Relationship Graph
#
# ------------------------------------------------------------------------

plg = newplugin()
plg.id = "rel_graph"
plg.name = _("Relationship Graph")
plg.description = _("Produces relationship graphs using Graphviz.")
plg.version = "1.0"
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = "gvrelgraph.py"
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = "RelGraphReport"
plg.optionclass = "RelGraphOptions"
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
