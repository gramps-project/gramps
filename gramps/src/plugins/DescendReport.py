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

"Generate files/Descendant Report"

import RelLib
import const
import os
import re
import sort
import string
import OpenOffice
import utils

import const

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantReport:
    def __init__(self,name,person):
        self.name = name
        self.person = person

    def setup(self):
        pass

    def report(self):
        pass

    def end(self):
        pass
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class OpenOfficeDesReport(DescendantReport):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,name,person,db):
        self.creator = db.getResearcher().getName()
        DescendantReport.__init__(self,name,person)
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self,template):
        self.open_office = OpenOffice.OpenOfficeCore(self.name,template,\
                                                     ".sxw",self.creator)
        self.file = self.open_office.setup()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.open_office.end()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def report(self):
        self.file.write('<text:p text:style-name="Title">')
        self.file.write('Descendants of ')
        self.file.write(self.person.getPrimaryName().getRegularName())
        self.file.write('</text:p>\n')
        self.dump(1,self.person)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump(self,level,person):
        self.file.write('<text:p text:style-name="P' + str(level) + '">')
        self.file.write(str(level) + '. ')
        self.file.write(person.getPrimaryName().getRegularName())

        birth = person.getBirth().getDateObj().getYear()
        death = person.getDeath().getDateObj().getYear()
        if birth != -1 or death != -1:
            self.file.write(' (')
            if birth != -1:
                self.file.write('b. ' + str(birth))
            if death != -1:
                if birth != -1:
                    self.file.write(', ')
                self.file.write('d. ' + str(death))
            self.file.write(')')
        self.file.write('</text:p>\n')

        for family in person.getFamilyList():
            for child in family.getChildList():
                self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AbiwordDesReport(DescendantReport):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self,template):
        if self.name[-4:] != ".abw":
            self.name = self.name + ".abw"
        self.file = open(self.name,"w")
        self.file.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        self.file.write('<abiword version="0.7.12">\n')
        self.file.write('<section>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):

        self.file.write('</section>\n')
        self.file.write('</abiword>\n')
        self.file.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def report(self):
        self.file.write('<p style="Heading 1">')
        self.file.write('Descendants of ')
        self.file.write(self.person.getPrimaryName().getRegularName())
        self.file.write('</p>\n')
        self.dump(1,self.person)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump(self,level,person):
        self.file.write('<p style="Normal"')
        if level > 1:
            self.file.write(' props="margin-left:')
            val = float(level-1) / 2.0
            self.file.write("%6.3fin\"" % (val))
        self.file.write('>')
        self.file.write(str(level) + '. ')
        self.file.write(person.getPrimaryName().getRegularName())

        birth = person.getBirth().getDateObj().getYear()
        death = person.getDeath().getDateObj().getYear()
        if birth != -1 or death != -1:
            self.file.write(' (')
            if birth != -1:
                self.file.write('b. ' + str(birth))
            if death != -1:
                if birth != -1:
                    self.file.write(', ')
                self.file.write('d. ' + str(death))
            self.file.write(')')
        self.file.write('</p>\n')

        for family in person.getFamilyList():
            for child in family.getChildList():
                self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DesReportWindow:
    def __init__(self,person,db):
        self.person = person

        glade_file = os.path.dirname(__file__) + os.sep + "desreport.glade"
        self.top = GladeXML(glade_file,"dialog1")
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_html_toggled": on_html_toggled,
            "on_save_clicked": on_save_clicked
            })
        mytop = self.top.get_widget("dialog1")
        mytop.set_data("o",self)
        mytop.set_data("d",db)
        mytop.show()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    report = DesReportWindow(person,database)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_clicked(obj):
    myobj = obj.get_data("o")
    db = obj.get_data("d")

    file = myobj.top.get_widget("filename").get_text()
    if file == "":
        return

    if myobj.top.get_widget("openoffice").get_active():
        report = OpenOfficeDesReport(file,myobj.person,db)
    elif myobj.top.get_widget("abiword").get_active():
        report = AbiwordDesReport(file,myobj.person)
    else:
        return

    report.setup(const.dataDir + os.sep + "deslist.sxw")
    report.report()
    report.end()

    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_html_toggled(obj):
    myobj = obj.get_data(OBJECT)
    if myobj.form.get_widget("html").get_active():
        myobj.form.get_widget("htmltemplate").set_sensitive(1)
    else:
        myobj.form.get_widget("htmltemplate").set_sensitive(0)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Generates a list of descendants of the active person"
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 4 1",
        " 	c None",
        ".	c #FFFFFF",
        "+	c #C0C0C0",
        "@	c #000000",
        "                                                ",
        "                                                ",
        "                                                ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@..................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +............@@@@@@@@@@@.........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]
