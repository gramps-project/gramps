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

"Generate files/Ahnentalfel Chart"

import RelLib
import const
import os
import re
import sort
import string
import utils
import OpenOffice

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
active_person = None
db = None

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReport:

    gen = {
        1 : "First",
        2 : "Second",
        3 : "Third",
        4 : "Fourth",
        5 : "Fifth",
        6 : "Sixth",
        7 : "Seventh",
        8 : "Eighth",
        9 : "Ninth",
        10: "Tenth",
        11: "Eleventh",
        12: "Twelfth",
        13: "Thirteenth",
        14: "Fourteenth",
        15: "Fifteenth",
        16: "Sixteenth",
        17: "Seventeenth",
        18: "Eigthteenth",
        19: "Nineteenth",
        20: "Twentieth",
        21: "Twenty-first",
        22: "Twenty-second",
        23: "Twenty-third",
        24: "Twenty-fourth",
        25: "Twenty-fifth",
        26: "Twenty-sixth",
        27: "Twenty-seventh",
        28: "Twenty-eighth",
        29: "Twenty-ninth"
        }

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,max,pgbrk):
        self.map = {}
        self.database = database
        self.start = person
        self.output = output
        self.max_generations = max
        self.pgbrk = pgbrk
        self.file = None
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.file.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def filter(self,person,index):
        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person
    
        family = person.getMainFamily()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_title(self,name):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_start(self,newpage):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_stop(self):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_begin(self):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_end(self):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_start(self,number,heading):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_stop(self):
        pass

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):

        self.filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.write_title("Ahnentalfel Chart for " + name)
    
        keys = self.map.keys()
        keys.sort()
        generation = 0
        need_header = 1

        for key in keys :
            if generation == 0 or key >= 2**generation:
                if generation == 0:
                    self.heading_start(0)
                else:
                    self.list_end()
                    self.heading_start(self.pgbrk)
                self.file.write(AncestorReport.gen[generation+1 ]+ " Generation")
                self.heading_stop()
                self.list_begin()
                generation = generation + 1

            person = self.map[key]
            name = person.getPrimaryName().getRegularName()
            self.list_para_start(str(key) + ".", name )

            # Check birth record
        
            birth = person.getBirth()
            if birth:
                date = birth.getDateObj()
                place = birth.getPlace()
                if date.getDate() != "" or place != "":
                    self.file.write(" was born")
                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            self.file.write(" on ")
                        else:
                            self.file.write(" in ")
                        self.file.write(date.getDate())
                if place != "":
                    self.file.write(" in " + place)
                if place == "" or place[-1] != '.':
                    self.file.write(".")
                self.file.write("\n")
            else:
                self.file.write(".\n")

            death = person.getDeath()
            buried = None
            for event in person.getEventList():
                if string.lower(event.getName()) == "burial":
                    buried = event
        
            if death:
                date = death.getDateObj()
                place = death.getPlace()
                if date.getDate() != "" or place != "":
                    if person.getGender() == RelLib.Person.male:
                        self.file.write("He")
                    else:
                        self.file.write("She")
                    self.file.write(" died")

                    if date.getDate() != "":
                        if date.getDay() != -1 and date.getMonth() != -1:
                            self.file.write(" on ")
                        else:
                            self.file.write(" in ")
                        self.file.write(date.getDate())
                    if place != "":
                        self.file.write(" in " + place)
                    if buried:
                        date = buried.getDateObj()
                        place = buried.getPlace()
                        if date.getDate() != "" or place != "":
                            self.file.write(", and was buried")

                            if date.getDate() != "":
                                if date.getDay() != -1 and date.getMonth() != -1:
                                    self.file.write(" on ")
                                else:
                                    self.file.write(" in ")
                                self.file.write(date.getDate())
                            if place != "":
                                self.file.write(" in " + place)
                    
                    if place == "" or place[-1] != '.':
                        self.file.write(".")
                    self.file.write("\n")
            else:
                self.file.write(".\n")

            self.list_para_stop()

        self.list_end()
        self.end()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class OpenOfficeAncestorReport(AncestorReport):

    def __init__(self,database,person,output,max,pgbrk,template):
        creator = database.getResearcher().getName()
        self.open_office = OpenOffice.OpenOfficeCore(output,template,".sxw",creator)
        AncestorReport.__init__(self,database,person,output,max,pgbrk)
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
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
    def write_title(self,name):
        self.file.write("<text:h text:style-name=\"P1\" ")
        self.file.write("text:level=\"1\">" + name + "</text:h>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_start(self,newpage):
        if newpage :
            self.file.write("<text:h text:style-name=\"P2\"")
        else:
            self.file.write("<text:h text:style-name=\"Heading 2\"")
        self.file.write(" text:level=\"2\">")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_stop(self):
        self.file.write("</text:h>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_start(self,number,heading):
        self.file.write("<text:p text:style-name=\"Hanging indent\">")
        self.file.write(number + "<text:tab-stop/>")
        self.file.write("<text:span text:style-name=\"T1\">")
        self.file.write(heading + "</text:span>")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_stop(self):
        self.file.write("</text:p>\n")


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportHtml(AncestorReport):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,max,pgbrk,template):
        self.template = template
        AncestorReport.__init__(self,database,person,output,max,pgbrk)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_title(self,name):
        self.file.write("<H1>" + name + "</H1>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_start(self,newpage):
        self.file.write("<H2>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_stop(self):
        self.file.write("</H2>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_start(self,number,heading):
        self.file.write("<LI VALUE=\"" + number + "\">")
        self.file.write("<STRONG>" + heading + "</STRONG>")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_stop(self):
        self.file.write("</LI>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        if self.template == "":
            self.first = [
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">\n',
                '<HTML>\n',
                '<HEAD>\n',
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">\n',
                '<TITLE>\n',
                '</TITLE>\n',
                '</HEAD>\n',
                '<BODY>\n',
                '<!-- START -->\n'
                ]
            self.last = [
                '<!-- STOP -->\n',
                '</BODY>\n',
                '</HTML>\n'
                ]
        else:    
            start = re.compile(r"<!-- START -->")

            templateFile = open(self.template,"r")
            lines = templateFile.readlines()
            templateFile.close()
    
            in_last = 0
            for line in lines:
                if start.search(line):
                    in_last = 1
                    self.last.append(line);
                elif in_last == 0:
                    self.first.append(line)
                else:
                    self.last.append(line);
        self.file = open(self.output,"w")
        titleRe = re.compile(r"<TITLE>")
        for line in self.first:
            if titleRe.search(line):
                name = self.start.getPrimaryName().getRegularName()
                self.file.write(line)
                self.file.write("Ahnentafel Chart for " + name)
            else:    
                self.file.write(line)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        for line in self.last:
            self.file.write(line)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_begin(self):
        self.file.write("<OL>\n");

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_end(self):
        self.file.write("</OL>\n");

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportAbiword(AncestorReport):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_title(self,name):
        self.file.write('<p style="Heading 1">' + name + '</p>\n')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_start(self,newpage):
        self.file.write('<p style="Heading 2">')
        if newpage:
            self.file.write('<pbr/>')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_stop(self):
        self.file.write("</p>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_start(self,number,heading):
        self.file.write('<p props="margin-left:0.5000in; text-indent:-0.5000in">')
        self.file.write(number + '\t')
        self.file.write('<c props="font-weight:bold">')
        self.file.write(heading)
        self.file.write('</c>')

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_stop(self):
        self.file.write("</p>\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.file = open(self.output,"w")
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

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportLatex(AncestorReport):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_start(self,newpage):
        if newpage:
            self.file.write("\\newpage\n")
        self.file.write("\\section{")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def heading_stop(self):
        self.file.write("}\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_para_start(self,number,heading):
        self.file.write("\\item{" + number + "}\n")
        self.file.write("\\textbf{" + heading + "}")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.first = [
            "\\documentclass{article}\n",
            "\\usepackage{makeidx}\n",
            "\\makeindex\n",
            "\\begin{document}\n"
            ]
        self.last = [
            "\\newpage\n",
            "\\printindex\n",
            "\\end{document}\n"
            ]
        self.file = open(self.output,"w")
        for line in self.first:
            self.file.write(line)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_title(self,name):
        self.file.write("\\title{%s}\n" % name)
        self.file.write("\\author{}\n")
        self.file.write("\\maketitle\n")

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_begin(self):
        self.file.write("\\begin{description}\n");

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def list_end(self):
        self.file.write("\\end{description}\n");
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        for line in self.last:
            self.file.write(line)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):

    global active_person
    global topDialog
    global glade_file
    global db
    
    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "ancestorreport.glade"
    topDialog = GladeXML(glade_file,"dialog1")
    topDialog.get_widget("htmltemplate").set_sensitive(0)

    name = person.getPrimaryName().getRegularName()
    
    topDialog.get_widget("labelTitle").set_text("Ahnentalfel Report for " + name)
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_save_clicked" : on_save_clicked,
        "on_html_toggled" : on_html_toggled
        })


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_html_toggled(obj):
    if obj.get_active():
        topDialog.get_widget("htmltemplate").set_sensitive(1)
    else:    
        topDialog.get_widget("htmltemplate").set_sensitive(0)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_save_clicked(obj):
    global active_person
    global db

    outputName = topDialog.get_widget("filename").get_text()
    max_gen = topDialog.get_widget("generations").get_value_as_int()
    pgbrk = topDialog.get_widget("pagebreak").get_active()

    if outputName == "":
        return


    if topDialog.get_widget("openoffice").get_active():
        template = const.dataDir + os.sep + "base.sxw"
        if outputName[-4:] != ".sxw":
            outputName = outputName + ".sxw"
        MyReport = OpenOfficeAncestorReport(db,active_person,outputName,\
                                            max_gen, pgbrk, template )
    elif topDialog.get_widget("html").get_active():
        template = topDialog.get_widget("htmlfile").get_text()
        MyReport = AncestorReportHtml(db,active_person,outputName,\
                                      max_gen, pgbrk, template)
    elif topDialog.get_widget("abiword").get_active():
        if outputName[-4:] != ".abw":
            outputName = outputName + ".abw"
        MyReport = AncestorReportAbiword(db,active_person,outputName,\
                                         max_gen, pgbrk)
    else:
        MyReport = AncestorReportLatex(db,active_person,outputName,\
                                       max_gen, pgbrk)

    MyReport.setup()
    MyReport.write_report()
        
    utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Produces a textual ancestral report"

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
        "       +................................+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]







