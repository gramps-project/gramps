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
import gzip
import cStringIO
import string

_BLKSIZE=512
nul = '\0'

#------------------------------------------------------------------------
#
# TarFile
#
#------------------------------------------------------------------------
class TarFile:
    def __init__(self,name):
        self.name = name
        self.f = gzip.open(name,"wb")
        self.pos = 0
        
    def add_file(self,filename,mtime,iobuf):
        iobuf.seek(0,2)
        length = iobuf.tell()
        iobuf.seek(0)

        buf = filename
        buf = buf + '\0'*(100-len(filename))
        buf = buf + "0100664" + nul
        buf = buf + "0000764" + nul
        buf = buf + "0000764" + nul
        buf = buf + "%011o" % length + nul
        buf = buf + "%011o" % mtime + nul
        buf = buf + "%s"
        buf = buf + "0" + '\0'*100 + 'ustar  \0'
        buf = buf + '\0'*32
        buf = buf + '\0'*32
        buf = buf + '\0'*183

        chksum = 0
        blank = "        "
        temp = buf % (blank)
        for c in temp:
            chksum = chksum + ord(c)
        vsum = "%06o " % chksum
        vsum = vsum + nul
        buf = buf % vsum

        self.pos = self.pos + len(buf)
        self.f.write(buf)

        buf = iobuf.read(length)
        self.f.write(buf)
        self.pos = self.pos + length
        rem = _BLKSIZE - (self.pos % _BLKSIZE)
        if rem != 0:
            self.f.write('\0' * rem)
        self.pos = self.pos + rem

    def close(self):
        rem = (_BLKSIZE*20) - (self.pos % (_BLKSIZE*20))
        if rem != 0:
            self.f.write('\0' * rem)
        self.f.close()

#------------------------------------------------------------------------
#
# ReadTarFile
#
#------------------------------------------------------------------------
class ReadTarFile:
    def __init__(self,name,wd="/tmp"):
        self.name = name
	self.wd = wd
        self.f = gzip.open(name,"rb")
        self.pos = 0

    def extract_files(self):
        map = {}
	while 1:
	    buf = self.f.read(100)
            if buf == '':
	        return
            index = 0
	    for b in buf:
	        if b != nul:
		    index = index + 1
	        else:
		    if index == 0:
                        return map
		    continue
	    filename = buf[0:index]
            if filename == None:
                return map
	    self.f.read(24) # modes
            l = string.replace(self.f.read(12),chr(0),' ')
            length = int(l,8) 
	    self.f.read(12)
	    self.f.read(6)
	    self.f.read(111)

	    self.f.read(64)
	    self.f.read(183)
            foo = cStringIO.StringIO()
            map[filename] = foo
	    foo.write(self.f.read(length))
	    foo.reset()
	    self.f.read(_BLKSIZE-(length%_BLKSIZE))
    
    def extract(self):
	while 1:
	    buf = self.f.read(100)
            if buf == '':
	        return
            index = 0
	    for b in buf:
	        if b != nul:
		    index = index + 1
	        else:
		    if index == 0:
                        return
		    continue
	    filename = buf[0:index]
	    self.f.read(24) # modes
            l = self.f.read(12)
            length_string = "";
            for char in l:
                if ord(char) != 0:
                    length_string = length_string + char
            length = int(length_string,8) 
	    self.f.read(12)
	    self.f.read(6)
	    self.f.read(111)

	    self.f.read(64)
	    self.f.read(183)
            foo = open("%s/%s" % (self.wd,filename),"wb")
	    foo.write(self.f.read(length))
	    foo.close()
	    self.f.read(_BLKSIZE-(length%_BLKSIZE))

    def close(self):
        self.f.close()

