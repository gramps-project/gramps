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

import GraphLayout

from FontScale import string_width
from DrawDoc import *
from Report import *
from TextDoc import *

import Config

import libglade
import gtk
import string

import intl
_ = intl.gettext

_sep = 0.5

#------------------------------------------------------------------------
#
# pt2cm - convert points to centimeters
#
#------------------------------------------------------------------------
def pt2cm(pt):
    return (float(pt)/72.0)*2.54

class DescendantReport:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,display,person,output,doc):
        self.doc = doc
        self.doc.creator(database.getResearcher().getName())
        self.map = {}
        self.text = {}
        self.start = person
        self.output = output
	self.box_width = 0
	self.height = 0
        self.lines = 0
        self.display = display

        plist = database.getPersonMap().values()
        self.layout = GraphLayout.DescendLine(plist,person)
        (self.v,self.e) = self.layout.layout()
        
        self.text = {}
        for (p,x,y) in self.v:

            self.text[p] = []

            n = p.getPrimaryName().getRegularName()
            N = p.getPrimaryName().getName()
            b = p.getBirth().getDate()
            d = p.getDeath().getDate()
            B = p.getBirth().getPlaceName()
            D = p.getDeath().getPlaceName()
            i = "%s" % p.getId()

            for line in self.display:
                line = string.replace(line,"$n",n)
                line = string.replace(line,"$N",N)
                line = string.replace(line,"$b",b)
                line = string.replace(line,"$B",B)
                line = string.replace(line,"$d",d)
                line = string.replace(line,"$D",D)
                line = string.replace(line,"$i",i)
                line = string.replace(line,"$$",'$')
                self.text[p].append(line)

            self.font = self.doc.style_list["Normal"].get_font()
            for line in self.text[p]:
                new_width = string_width(self.font,line)
                self.box_width = max(self.box_width,new_width)

            self.lines = max(self.lines,len(self.text[p]))    


    def write_report(self):

        self.calc()
        maxx,maxy = self.layout.max_size()

        maxx = int(maxx)
        maxy = int(maxy)

        cols = ((maxx-1)/self.maxx)
        rows = ((maxy-1)/self.maxy)

        self.pg = []
        self.ln = []

        for i in range(rows+1):
            self.pg.append([None]*(cols+1))
            self.ln.append([None]*(cols+1))

        for (p,x,y) in self.v:
            r = int((y-1)/self.maxy)
            c = int((x-1)/self.maxx)

            nx = x - (self.maxx)*c
            ny = y - (self.maxy)*r
            l = self.pg[r]
            if l[c] == None:
                l[c] = [(p,nx,ny)]
            else:
                l[c].append((p,nx,ny))

        for (x1,y1,x2,y2) in self.e:
            r1 = int((y1-1)/self.maxy)
            c1 = int((x1-1)/self.maxx)
            r2 = int((y2-1)/self.maxy)
            c2 = int((x2-1)/self.maxx)

            nx1 = x1 - (self.maxx)*c1
            nx2 = x2 - (self.maxx)*c2
            ny1 = y1 - (self.maxy)*r1
            ny2 = y2 - (self.maxy)*r2
            if r1 == r2:
                if c1 == c2:
                    l = self.ln[r1][c1]
                    if l == None:
                        self.ln[r1][c1] = [(nx1,ny1,nx2,ny2)]
                    else:
                        l.append((nx1,ny1,nx2,ny2))
                else:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,-nx2,ny2)]
                    else:
                        l1.append((nx1,ny1,-nx2,ny2))
                    if l2 == None:
                        self.ln[r2][c2] = [(-nx2,ny2,nx2,ny2)]
                    else:
                        l2.append((-nx2,ny2,nx2,ny2))
                        
                    for c in range(c1+1,c2):
                        if self.ln[r1][c]:
                            self.ln[r1][c].append((nx1,-ny1,nx2,-ny2))
                        else:
                            self.ln[r1][c] = [(nx1,-ny1,nx2,-ny2)]
            else:
                if c1 == c2:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,nx2,-ny2)]
                    else:
                        l1.append((nx1,ny1,nx2,-ny2))
                    if l2 == None:
                        self.ln[r2][c2] = [(nx1,-ny2,nx2,ny2)]
                    else:
                        l2.append((nx1,-ny2,nx2,ny2))
                    for r in range(r1+1,r2):
                        if self.ln[r][c1]:
                            self.ln[r][c1].append((nx1,-ny1,nx2,-ny2))
                        else:
                            self.ln[r][c1] = [(nx1,-ny1,nx2,-ny2)]
                else:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    l3 = self.ln[r2][c1]

                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,-nx2,-ny2)]
                    else:
                        l1.append((nx1,ny1,-nx2,-ny2))

                    if l2 == None:
                        self.ln[r2][c2] = [(-nx1,ny2,nx2,ny2)]
                    else:
                        l2.append((-nx1,ny2,nx2,ny2))

                    if l3 == None:
                        self.ln[r2][c1] = [(nx1,-ny2,-nx2,ny2)]
                    else:
                        l3.append((nx1,-ny2,-nx2,ny2))
            
	try:
            self.doc.open(self.output)
        except:
            print "Document open failure"

        for r in range(len(self.pg)):
            for c in range(len(self.pg[r])):
                self.print_page(self.pg[r][c],self.ln[r][c],r,c)
        
	try:
	    self.doc.close()
        except:
            print "Document close failure"

    #--------------------------------------------------------------------
    #
    # calc - calculate the maximum width that a box needs to be. From
    # that and the page dimensions, calculate the proper place to put
    # the elements on a page.
    #
    #--------------------------------------------------------------------
    def calc(self):
	width = 0

	self.height = self.lines*pt2cm(1.25*self.font.get_size())
	self.box_width = pt2cm(self.box_width+20)

        start = self.doc.get_right_margin()

	self.maxx = int(self.doc.get_usable_width()/(self.box_width+_sep))
        self.maxy = int(self.doc.get_usable_height()/(self.height+_sep))

        g = GraphicsStyle()
        g.set_height(self.height)
        g.set_width(self.box_width)
        g.set_paragraph_style("Normal")
        g.set_shadow(1)
        self.doc.add_draw_style("box",g)

        g = GraphicsStyle()
        self.doc.add_draw_style("line",g)

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def print_page(self, plist,elist,r,c):
        self.doc.start_page()

        delta = self.doc.get_usable_width()/(self.maxx)
        top = self.doc.get_top_margin()
        bottom = self.doc.get_top_margin() + self.doc.get_usable_height()
        left = self.doc.get_left_margin()
        right = self.doc.get_right_margin() + self.doc.get_usable_width() - (2*_sep)

        if plist:
            for (p,x,y) in plist:
                name = string.join(self.text[p],"\n")
                x = (x-1)*delta + left + _sep
                y = (y-1)*(self.height+_sep)+top
                self.doc.draw_box("box",name,x,y)
        if elist:
            for (x1,y1,x2,y2) in elist:
                if x1 < 0:
                    nx1 = left
                else:
                    nx1 = (x1-1) * delta + left + self.box_width + _sep
                if x2 < 0:
                    nx2 = right + _sep
                else:
                    nx2 = (x2-1) * delta + left + _sep
                if y1 < 0:
                    ny1 = top
                else:
                    ny1 = (y1-1)*(self.height+_sep)+ top + self.height/2.0
                if y2 < 0:
                    ny2 = bottom
                else:
                    ny2 = (y2-1)*(self.height+_sep) + top + self.height/2.0
                if y1 < 0 and y2 < 0:
                    half = (nx1+nx2)/2.0
                    print x1,x2,y1,y2,nx1,nx2,half
                    self.doc.draw_line("line",half,ny1,half,ny2)
                elif ny1 != ny2:
                    if x1 == -x2:
                        self.doc.draw_line("line",nx1,ny1,nx2,ny2)
                    else:
                        half = (nx1+nx2)/2.0
                        if y1 > 0:
                            self.doc.draw_line("line",nx1,ny1,half,ny1)
                        self.doc.draw_line("line",half,ny1,half,ny2)
                        if y2 > 0:
                            self.doc.draw_line("line",half,ny2,nx2,ny2)
                else:
                    self.doc.draw_line("line",nx1,ny1,nx2,ny2)

        y = bottom + (self.doc.get_bottom_margin()/2.0)
        if r or c:
            self.doc.write_at("Normal","(%d,%d)" % (r,c), right, y)
        self.doc.end_page()


class DescendantReportDialog(DrawReportDialog):
    def __init__(self,database,person):
        DrawReportDialog.__init__(self,database,person)

    def get_title(self):
        return "%s - %s - GRAMPS" % (_("Descendant Graph"),_("Graphical Reports"))

    def get_header(self,name):
        return _("Descendant Graph for %s") % name

    def get_target_browser_title(self):
        return _("Save Descendant Graph")

    def get_stylesheet_savefile(self):
        return "descendant_graph.xml"

    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (0, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\nb. $b\nd. $d",
                _("Allows you to customize the data in the boxes in the report"))
    
    def make_default_style(self):
        """Make the default output style for the Ancestor Chart report."""
        f = FontStyle()
        f.set_size(9)
        f.set_type_face(FONT_SANS_SERIF)
        p = ParagraphStyle()
        p.set_font(f)
        self.default_style.add_style("Normal",p)

    def make_report(self):
        """Create the object that will produce the Descendant Graph.
        All user dialog has already been handled and the output file
        opened."""
        MyReport = DescendantReport(self.db,self.report_text,
                                    self.person, self.target_path, self.doc)
        MyReport.write_report()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    DescendantReportDialog(database,person)

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
        "       +++++++++++++++++++++++++++++++++++++    ",
        "       +...................................+    ",
        "       +..@@@@@@.......@@@@@@......@@@@@@..+    ",
        "       +..@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..+    ",
        "       +..@@@@@@...@...@@@@@@...@..@@@@@@..+    ",
        "       +...........@............@..........+    ",
        "       +...........@............@..........+    ",
        "       +...........@............@..@@@@@@..+    ",
        "       +...........@............@@@@@@@@@..+    ",
        "       +...........@...............@@@@@@..+    ",
        "       +...........@.......................+    ",
        "       +...........@.......................+    ",
        "       +...........@...@@@@@@......@@@@@@..+    ",
        "       +...........@@@@@@@@@@@@@@@@@@@@@@..+    ",
        "       +...........@...@@@@@@...@..@@@@@@..+    ",
        "       +...........@............@..........+    ",
        "       +...........@............@..........+    ",
        "       +...........@............@..@@@@@@..+    ",
        "       +...........@............@@@@@@@@@..+    ",
        "       +...........@...............@@@@@@..+    ",
        "       +...........@.......................+    ",
        "       +...........@.......................+    ",
        "       +...........@...@@@@@@..............+    ",
        "       +...........@@@@@@@@@@..............+    ",
        "       +...........@...@@@@@@..............+    ",
        "       +...........@.......... ............+    ",
        "       +...........@.......................+    ",
        "       +...........@...@@@@@@..............+    ",
        "       +...........@@@@@@@@@@..............+    ",
        "       +...........@...@@@@@@..............+    ",
        "       +...........@.......................+    ",
        "       +...........@.......................+    ",
        "       +...........@...@@@@@@.....@@@@@@...+    ",
        "       +...........@@@@@@@@@@@@@@@@@@@@@...+    ",
        "       +...............@@@@@@..@..@@@@@@...+    ",
        "       +.......................@...........+    ",
        "       +.......................@...........+    ",
        "       +.......................@..@@@@@@...+    ",
        "       +.......................@@@@@@@@@...+    ",
        "       +..........................@@@@@@...+    ",
        "       +...................................+    ",
        "       +++++++++++++++++++++++++++++++++++++    ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Descendant Graph"),
    category=_("Graphical Reports"),
    description=_("Generates a list of descendants of the active person"),
    status=(_("Alpha")),
    xpm=get_xpm_image()
    )

