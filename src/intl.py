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
import gtk

ver = sys.version[0:3]
_trans = None

try:
    if ver == "2.2":
        from intl22 import *
        status = None
    else:
        import gettext as foo
        
        status = 'Internationalization library could not be loaded'
        print status
        
        def gettext(s):
            return foo.gettext(s)

        def textdomain(s):
            return foo.textdomain(s)

        def bindtextdomain(s,x):
            return foo.bindtextdomain(s,x)

        def bind_textdomain_codeset(s,x):
            return
except:
    import gettext as foo

    status = 'Internationalization library could not be loaded'
    
    def textdomain(s):
        return foo.textdomain(s)
    
    def bindtextdomain(s,x):
        gtk.glade.bindtextdomain(s,x)
        return foo.bindtextdomain(s,x)

    def null(s):
        return s
    
    def bind_textdomain_codeset(s,x):
        global gettext
        try:
            gettext = foo.translation(s).ugettext
        except:
            gettext = null
