#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
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

class ReportError(Exception):
    
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return self.value

class GedcomError(Exception):
    
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return self.value

class PluginError(Exception):
    
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return self.value
