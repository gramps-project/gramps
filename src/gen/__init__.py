#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""
The gen module provides 5 packages. 
  1. gen.lib gives access to all genealogy related objects, like family,
     person, ...
  2. gen.db provides access to the bsddb backend storing genea data
  3. gen.proxy provides access to the data via a proxy that filters out 
     specific data
  4. gen.plug defines a plugin system so plugins can be written that can 
     work on the data. This can be in CLI or GUI
  5. gen.utils provides some generic utilities
"""

__all__ = [ "db", "display", "lib", "mime", "plug", "proxy", "utils" ]
