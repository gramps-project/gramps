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

import os
import re
import time
import tempfile
import const

meta_creator = re.compile(r"""\s*<meta:initial-creator>""")
dc_creator   = re.compile(r"""\s*<dc:creator>""")
meta_date    = re.compile(r"""\s*<meta:creation-date>""")
dc_date      = re.compile(r"""\s*<dc:date>""")

class OpenOfficeCore:

    def __init__(self,filename,template,ext,owner=""):
        self.template = template
        self.owner = owner
        if filename[-4:] != ext:
            self.filename = filename + ext
        else:
            self.filename = filename
        self.first = []
        self.last = []
        self.file = None
        self.image_list = []
        self.tempdir = ""

    def setup(self):
        templateFile = open(self.template,"r")
        lines = templateFile.readlines()
        templateFile.close()
    
        in_last = 0
        t = time.localtime(time.time())
        time_str="%04d-%02d-%02dT%02d:%02d:%02d" % \
                  (t[0],t[1],t[2],t[3],t[4],t[5])
        for line in lines:
            if line[1:15] == "</office:body>":
                in_last = 1
                self.last.append(line);
            elif in_last == 0:
                if meta_creator.match(line):
                    self.first.append("<meta:initial-creator>" + self.owner + \
                                      "</meta:initial-creator>")
                elif dc_creator.match(line):
                    self.first.append("<dc:creator>" + self.owner + \
                                      "</dc:creator>")
                elif dc_date.match(line):
                    self.first.append("<dc:date>" + time_str + \
                                      "</dc:date>")
                elif meta_date.match(line):
                    self.first.append("<meta:creation-date>" + time_str + \
                                      "</meta:creation-date>")
                else:
                    self.first.append(line)
            else:
                self.last.append(line);

        tempfile.tempdir = "/tmp"
        self.tempdir = tempfile.mktemp()
        os.mkdir(self.tempdir,0700)
        os.mkdir(self.tempdir + os.sep + "Pictures")
        os.mkdir(self.tempdir + os.sep + "META-INF")
        self.file = open(self.tempdir + os.sep + "Content.xml","w")
        for line in self.first:
            self.file.write(line)
        return self.file

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def add_image(self,name):
        self.image_list.append(name)
        return self.tempdir + os.sep + "Pictures" + os.sep + name

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        import shutil
        
        for line in self.last:
            self.file.write(line)

        self.file.close()
        tmpname = tempfile.mktemp()

        file = open(self.tempdir + os.sep + "META-INF" + os.sep + \
                    "manifest.xml","w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<manifest><file-entry media-type="" ')
        file.write('full-path="Pictures/"/>')
        for image in self.image_list:
            file.write('<file-entry media-type="" full-path="Pictures/')
            file.write(image + '"/>')
        file.write('<file-entry media-type="" full-path="Content.xml"/>')
        file.write('</manifest>\n')
        file.close()
        os.system("cd " + self.tempdir + "; " + const.zipcmd + " " \
                  + tmpname + " .")
        if os.path.isfile(self.filename):
            os.unlink(self.filename)
        shutil.copy(tmpname,self.filename)
        os.unlink(tmpname)
        os.unlink(self.tempdir + os.sep + "META-INF" + os.sep + "manifest.xml")
        os.unlink(self.tempdir + os.sep + "Content.xml")
        for image in self.image_list:
            os.unlink(self.tempdir + os.sep + "Pictures" + os.sep + image)
        os.rmdir(self.tempdir + os.sep + "Pictures")
        os.rmdir(self.tempdir + os.sep + "META-INF")
        os.rmdir(self.tempdir)
    
    
