#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

# $Id: __init__.py 5872 2006-02-03 15:49:59Z hippy $

"""
This package implements access to GRAMPS configuration.
It provides the choice between different storage backends.
"""

from _GrampsConfigKeys import *
from _GrampsIniKeys import *

import os

def __upgrade_gconf():
   import _GrampsGconfKeys as GconfKeys
   print "Upgrading INI file"
   for key in default_value.keys():
      data = GconfKeys.get(key)
      set(key, data)

if not os.path.exists(INIFILE):
   try:
      __upgrade_gconf()
   except ImportError:
      print "Cannot upgrade GCONF settings"



   
