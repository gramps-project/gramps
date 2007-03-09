#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

from ansel_utf8 import ansel_to_utf8
import codecs

class BaseReader:
    def __init__(self, ifile, encoding):
        self.ifile = ifile
        self.enc = encoding

    def reset(self):
        self.ifile.seek(0)

    def readline(self):
        return unicode(self.ifile.readline(), 
                       encoding=self.enc,
                       errors='replace')

class UTF8Reader(BaseReader):

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, 'utf8')
        self.reset()

    def reset(self):
        self.ifile.seek(0)
        data = self.ifile.read(3)
        if data != "\xef\xbb\xbf":
            self.ifile.seek(0)

    def readline(self):
        return unicode(self.ifile.readline(),
                       encoding=self.enc,
                       errors='replace')

class UTF16Reader(BaseReader):

    def __init__(self, ifile):
        new_file = codecs.EncodedFile(ifile, 'utf8', 'utf16')
        BaseReader.__init__(self, new_file, 'utf16')
        self.reset()

    def readline(self):
        l = self.ifile.readline()
        if l.strip():
            return l
        else:
            return self.ifile.readline()

class AnsiReader(BaseReader):

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, 'latin1')
    
class AnselReader(BaseReader):

    def __init__(self, ifile):
        BaseReader.__init__(self, ifile, "")

    def readline(self):
        return ansel_to_utf8(self.ifile.readline())
