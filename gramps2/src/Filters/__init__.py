#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Package providing filtering framework for GRAMPS.
"""

__author__ = "Don Allingham"

SystemFilters = None
CustomFilters = None

from const import system_filters, custom_filters
from _FilterList import FilterList
from _GenericFilter import GenericFilter, GenericFamilyFilter
from _ParamFilter import ParamFilter

def reload_system_filters():
    global SystemFilters
    SystemFilters = FilterList(system_filters)
    SystemFilters.load()
    
def reload_custom_filters():
    global CustomFilters
    CustomFilters = FilterList(custom_filters)
    CustomFilters.load()
    
if not SystemFilters:
    reload_system_filters()

if not CustomFilters:
    reload_custom_filters()

from _FilterComboBox import FilterComboBox
from _FilterMenu import build_filter_menu, build_filter_model
from _FilterStore import FilterStore
from _SearchBar import SearchBar
from _SearchFilter import SearchFilter
from _SidebarFilter import SidebarFilter
from _PersonSidebarFilter import PersonSidebarFilter
from _FamilySidebarFilter import FamilySidebarFilter
