#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
Abstracts the i18n library, providing a non-translated fallback if
everything else fails.
"""
import sys

ver = sys.version[0:3]

try:
    if ver == "1.5":
        from intl15 import *
    elif ver == "2.0":
        from intl20 import *
    elif ver == "2.1":
        from intl21 import *
    elif ver == "2.2":
        from intl22 import *
    else:
        print 'Internationalization library could be loaded'
        
        def gettext(s):
            return s

        def textdomain(s):
            return

        def bindtextdomain(s,x):
            return
except:
    import traceback
    traceback.print_exc()
    
    def gettext(s):
        return s
    
    def textdomain(s):
        return
    
    def bindtextdomain(s,x):
        return
