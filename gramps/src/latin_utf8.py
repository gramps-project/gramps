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

import sys

if sys.version[0] != '1':
    def utf8_to_latin(s):
        return s.encode('iso-8859-1','replace')

    def latin_to_utf8(s):
        return s

else:
    try:
        import cStringIO
    
        from xml.unicode.utf8_iso import code_to_utf8
        from xml.unicode.iso8859 import UTF8String

        def utf8_to_latin(s):
            y = UTF8String(s)
            try:
                return y.encode("iso-8859-1")
            except:
                return s

        def latin_to_utf8(s):
            buff = cStringIO.StringIO()
            for c in s:
                try:
                    cv = code_to_utf8(1,c)
                except Exception:
                    cv = '?'
                buff.write(cv)
            ans = buff.getvalue()
            buff.close()
            return ans

    except:
        def utf8_to_latin(s):
            return s

        def latin_to_utf8(s):
            return s
    
