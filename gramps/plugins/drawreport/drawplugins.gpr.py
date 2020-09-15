#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
#
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
# Ancestor Tree
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'ancestor_chart,BKI'
plg.name = _("Ancestor Chart")
plg.description = _("Produces a graphical ancestral chart")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'ancestortree.py'
plg.ptype = REPORT
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'AncestorTree'
plg.optionclass = 'AncestorTreeOptions'
plg.report_modes = [REPORT_MODE_BKI]

plg = newplugin()
plg.id = 'ancestor_chart'
plg.name = _("Ancestor Tree")
plg.description = _("Produces a graphical ancestral tree")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'ancestortree.py'
plg.ptype = REPORT
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'AncestorTree'
plg.optionclass = 'AncestorTreeOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Calendar
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'calendar'
plg.name = _("Calendar")
plg.description = _("Produces a graphical calendar")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'calendarreport.py'
plg.ptype = REPORT
plg.authors = ["Douglas S. Blank"]
plg.authors_email = ["dblank@cs.brynmawr.edu"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'Calendar'
plg.optionclass = 'CalendarOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Descendant Tree
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'descend_chart,BKI'
plg.name = _("Descendant Chart")
plg.description = _("Produces a graphical descendant chart")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'descendtree.py'
plg.ptype = REPORT
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'DescendTree'
plg.optionclass = 'DescendTreeOptions'
plg.report_modes = [REPORT_MODE_BKI]

plg = newplugin()
plg.id = 'descend_chart'
plg.name = _("Descendant Tree")
plg.description = _("Produces a graphical descendant tree")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'descendtree.py'
plg.ptype = REPORT
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'DescendTree'
plg.optionclass = 'DescendTreeOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Family Descendant Tree
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'family_descend_chart,BKI'
plg.name = _("Family Descendant Chart")
plg.description = _("Produces a graphical descendant chart around a family")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'descendtree.py'
plg.ptype = REPORT
plg.category = CATEGORY_DRAW
plg.gramps_target_version = MODULE_VERSION
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.require_active = True
plg.reportclass = 'DescendTree'
plg.optionclass = 'DescendTreeOptions'
plg.report_modes = [REPORT_MODE_BKI]

plg = newplugin()
plg.id = 'family_descend_chart'
plg.name = _("Family Descendant Tree")
plg.description = _("Produces a graphical descendant tree around a family")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'descendtree.py'
plg.ptype = REPORT
plg.category = CATEGORY_DRAW
plg.gramps_target_version = MODULE_VERSION
plg.authors = ["Craig J. Anderson"]
plg.authors_email = ["ander882@hotmail.com"]
plg.require_active = True
plg.reportclass = 'DescendTree'
plg.optionclass = 'DescendTreeOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Fan Chart
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'fan_chart'
plg.name = _("Fan Chart")
plg.description = _("Produces fan charts")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'fanchart.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'FanChart'
plg.optionclass = 'FanChartOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Statistics Charts
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'statistics_chart'
plg.name = _("Statistics Charts")
plg.description = _("Produces statistical bar and pie charts of the people "
                    "in the database")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'statisticschart.py'
plg.ptype = REPORT
plg.authors = ["Eero Tamminen"]
plg.authors_email = [""]
plg.category = CATEGORY_DRAW
plg.reportclass = 'StatisticsChart'
plg.optionclass = 'StatisticsChartOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Timeline Chart
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'timeline'
plg.name = _("Timeline Chart")
plg.description = _("Produces a timeline chart.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'timeline.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_DRAW
plg.reportclass = 'TimeLine'
plg.optionclass = 'TimeLineOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
