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

"""
GRAMPS registration file
"""

#------------------------------------------------------------------------
#
# Check Localized Date Displayer and Parser
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'test_for_date_parser_and_displayer',
name  = "Check Localized Date Displayer and Parser",
description =  ("This test tool will create many people showing all"
                        " different date variants as birth. The death date is"
                        " created by parsing the result of the date displayer for"
                        " the birth date. This way you can ensure that dates"
                        " printed can be parsed back in correctly."),
version = '1.0',
gramps_target_version = '3.5',
status = UNSTABLE,
fname = 'dateparserdisplaytest.py',
authors = ["Martin Hawlisch"],
authors_email = ["martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'DateParserDisplayTest',
optionclass = 'DateParserDisplayTestOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Dump Gender Statistics
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'dgenstats',
name  = "Dump Gender Statistics",
description =  ("Will dump the statistics for the gender guessing "
                        "from the first name."),
version = '1.0',
gramps_target_version = '3.5',
status = STABLE,
fname = 'dumpgenderstats.py',
authors = ["Donald N. Allingham", "Martin Hawlisch"],
authors_email = ["don@gramps-project.org", "martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'DumpGenderStats',
optionclass = 'DumpGenderStatsOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Generate Testcases for Persons and Families
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'testcasegenerator',
name  = "Generate Testcases for Persons and Families",
description =  ("The testcase generator will generate some persons "
                        "and families that have broken links in the database "
                        "or data that is in conflict to a relation."),
version = '1.0',
gramps_target_version = '3.5',
status = UNSTABLE,
fname = 'testcasegenerator.py',
authors = ["Martin Hawlisch"],
authors_email = ["martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'TestcaseGenerator',
optionclass = 'TestcaseGeneratorOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Generate Testcases for Sources and citations
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'populatesources',
name  = "Populate Sources and Citations",
description =  ("This tool generates sources and citations ofr each source in "
                "order to populate the database for testing with significant "
                "numbers of sources and citations"),
version = '1.0',
gramps_target_version = '3.5',
status = UNSTABLE,
fname = 'populatesources.py',
authors = ["Tim Lyons"],
authors_email = [""],
category = TOOL_DEBUG,
toolclass = 'PopulateSources',
optionclass = 'PopulateSourcesOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )
