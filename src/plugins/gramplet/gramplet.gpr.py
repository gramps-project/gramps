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
# Register Gramplet
#
#------------------------------------------------------------------------
register(GRAMPLET, 
         id="Age on Date Gramplet", 
         name=_("Age on Date Gramplet"), 
         version="2.0.0",
         status = STABLE,
         fname="AgeOnDateGramplet.py",
         #gramps="3.1.0",
         height=200,
         gramplet = 'AgeOnDateGramplet',
         gramplet_title=_("Age on Date"),
         )

register(GRAMPLET, 
         id = "Age Stats Gramplet",
         name = _("Age Stats Gramplet"),
         status = STABLE,
         fname="AgeStats.py",
         height=100,
         expand=True,
         gramplet = 'AgeStatsGramplet',
         gramplet_title=_("Age Stats"),
         detached_width = 600,
         detached_height = 450,
         )

register(GRAMPLET, 
         id="Attributes Gramplet", 
         name=_("Attributes Gramplet"), 
         status = STABLE,
         fname="AttributesGramplet.py",
         height=150,
         expand=True,
         gramplet = 'AttributesGramplet',
         gramplet_title=_("Attributes"),
         detached_width = 325,
         detached_height = 250,
         )

register(GRAMPLET, 
         id="Calendar Gramplet", 
         name=_("Calendar Gramplet"), 
         status = STABLE,
         fname="CalendarGramplet.py",
         height=200,
         gramplet = 'CalendarGramplet',
         gramplet_title=_("Calendar"),
         )

register(GRAMPLET, 
         id = "Descendant Gramplet", 
         name=_("Descendant Gramplet"), 
         status = STABLE,
         fname="DescendGramplet.py",
         height=100,
         expand=True,
         gramplet = 'DescendantGramplet',
         gramplet_title=_("Descendants"),
         detached_width = 500,
         detached_height = 500,
         )

register(GRAMPLET, 
         id= "Fan Chart Gramplet", 
         name=_("Fan Chart Gramplet"), 
         status = STABLE,
         fname="FanChartGramplet.py",
         height=430,
         expand=True,
         gramplet = 'FanChartGramplet',
         detached_height = 550,
         detached_width = 475,
         gramplet_title=_("Fan Chart"),
         )
register(GRAMPLET, 
         id="FAQ Gramplet", 
         name=_("FAQ Gramplet"), 
         status = STABLE,
         fname="FaqGramplet.py",
         height=300,
         gramplet = 'FAQGramplet',
         gramplet_title=_("FAQ"),
         #gramps="3.1.0",
         version="1.0.0",
         )

register(GRAMPLET, 
         id= "Given Name Cloud Gramplet", 
         name=_("Given Name Cloud Gramplet"), 
         status = STABLE,
         fname="GivenNameGramplet.py",
         height=300,
         expand=True,
         gramplet = 'GivenNameCloudGramplet',
         gramplet_title=_("Given Name Cloud"),
         )

register(GRAMPLET, 
         id="Pedigree Gramplet", 
         name=_("Pedigree Gramplet"), 
         status = STABLE,
         fname="PedigreeGramplet.py",
         height=300,
         gramplet = 'PedigreeGramplet',
         gramplet_title=_("Pedigree"),
         expand=True,
         detached_width = 600,
         detached_height = 400,
         )

register(GRAMPLET, 
         id="Plugin Manager Gramplet", 
         name=_("Plugin Manager Gramplet"), 
         status = STABLE,
         fname="PluginManagerGramplet.py",
         height=300,
         expand=True,
         gramplet = 'PluginManagerGramplet',
         gramplet_title=_("Plugin Manager"),
         version="1.0.0",
         #gramps="3.1.0",
         )

register(GRAMPLET, 
         id="Quick View Gramplet", 
         name=_("Quick View Gramplet"), 
         status = STABLE,
         fname="QuickViewGramplet.py",
         height=300,
         expand=True,
         gramplet = 'QuickViewGramplet',
         gramplet_title=_("Quick View"),
         detached_width = 600,
         detached_height = 400,
         )

register(GRAMPLET, 
         id="Relatives Gramplet", 
         name=_("Relatives Gramplet"), 
         status = STABLE,
         fname="RelativeGramplet.py",
         height=200,
         gramplet = 'RelativesGramplet',
         gramplet_title=_("Relatives"),
         detached_width = 250,
         detached_height = 300,
         )

register(GRAMPLET, 
         id="Session Log Gramplet", 
         name=_("Session Log Gramplet"), 
         status = STABLE,
         fname="SessionLogGramplet.py",
         height=230,
         #data=['no'],
         gramplet = 'LogGramplet',
         gramplet_title=_("Session Log"),
         )

register(GRAMPLET, 
         id="Statistics Gramplet", 
         name=_("Statistics Gramplet"), 
         status = STABLE,
         fname="StatsGramplet.py",
         height=230,
         expand=True,
         gramplet = 'StatsGramplet',
         gramplet_title=_("Statistics"),
         )

register(GRAMPLET, 
         id= "Surname Cloud Gramplet", 
         name=_("Surname Cloud Gramplet"), 
         status = STABLE,
         fname="SurnameCloudGramplet.py",
         height=300,
         expand=True,
         gramplet = 'SurnameCloudGramplet',
         gramplet_title=_("Surname Cloud"),
         )

register(GRAMPLET, 
         id="TODO Gramplet", 
         name=_("TODO Gramplet"), 
         status = STABLE,
         fname="ToDoGramplet.py",
         height=300,
         expand=True,
         gramplet = 'TODOGramplet',
         gramplet_title=_("TODO List"),
         )

register(GRAMPLET, 
         id= "Top Surnames Gramplet", 
         name=_("Top Surnames Gramplet"), 
         status = STABLE,
         fname="TopSurnamesGramplet.py",
         height=230,
         gramplet = 'TopSurnamesGramplet',
         gramplet_title=_("Top Surnames"),
         )

register(GRAMPLET, 
         id="Welcome Gramplet", 
         name=_("Welcome Gramplet"), 
         status = STABLE,
         fname="WelcomeGramplet.py",
         height=300,
         expand=True,
         gramplet = 'make_welcome_content',
         gramplet_title=_("Welcome to Gramps!"),
         )

register(GRAMPLET, 
         id = "What's Next Gramplet", 
         name =_("What's Next Gramplet"), 
         status = STABLE,
         fname="WhatsNext.py",
         height = 230,
         expand = True,
         gramplet = 'WhatNextGramplet',
         gramplet_title = _("What's Next?"))
