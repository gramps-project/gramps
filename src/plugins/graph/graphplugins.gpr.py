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
# Family Lines Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'familylines_graph'
plg.name  = _("Family Lines Graph")
plg.description =  _("Produces family line graphs using GraphViz.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVFamilyLines.py'
plg.ptype = REPORT
plg.authors = ["Stephane Charette"]
plg.authors_email = ["stephanecharette@gmail.com"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'FamilyLinesReport'
plg.optionclass = 'FamilyLinesOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Hourglass Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'hourglass_graph'
plg.name  = _("Hourglass Graph")
plg.description =  _("Produces an hourglass graph using Graphviz.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVHourGlass.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'HourGlassReport'
plg.optionclass = 'HourGlassOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Relationship Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'rel_graph'
plg.name  = _("Relationship Graph")
plg.description =  _("Produces relationship graphs using Graphviz.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVRelGraph.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'RelGraphReport'
plg.optionclass = 'RelGraphOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
