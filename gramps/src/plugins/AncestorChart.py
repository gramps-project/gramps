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

"Graphical Reports/Ancestor Chart"

import GrampsCfg
import os
import string

from FontScale import string_width
from DrawDoc import *
from Report import *
from SubstKeywords import SubstKeywords

import libglade
import gtk

import intl
_ = intl.gettext

#------------------------------------------------------------------------
#
# pt2cm - convert points to centimeters
#
#------------------------------------------------------------------------
def pt2cm(pt):
    return (float(pt)/72.0)*(254.0/100.0)

#------------------------------------------------------------------------
#
# AncestorChart
#
#------------------------------------------------------------------------
class AncestorChart:

    def __init__(self,database,person,output,max,doc,display):
        self.doc = doc
        self.doc.creator(database.getResearcher().getName())
        self.map = {}
        self.text = {}
        self.start = person
        self.max_generations = max
        self.output = output
	self.box_width = 0
	self.height = 0
        self.lines = 0
        self.display = display
        
    def filter(self,person,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""
        
        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person

	self.text[index] = []

        subst = SubstKeywords(person)
        
        for line in self.display:
            self.text[index].append(subst.replace(line))

        self.font = self.doc.style_list["Normal"].get_font()
	for line in self.text[index]:
	    self.box_width = max(self.box_width,string_width(self.font,line))

	self.lines = max(self.lines,len(self.text[index]))    

        family = person.getMainParents()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    #--------------------------------------------------------------------
    #
    # filter - Generate the actual report
    #
    #--------------------------------------------------------------------
    def write_report(self):
	self.calc()
	try:
            self.doc.open(self.output)
        except:
            print _("Document write failure")

        generation = 1
        done = 0
        page = 1
        while done == 0:
            done = 1
            start = 2**(generation-1)
            for index in range(start, (start*2)):
                values = []
                self.get_numbers(index,1,values)
                if len(values) > 1 or generation == 1:
                    done = 0
                    self.print_page(index, generation, page)
                    page = page + 1
            generation = generation + 3
	try:
            self.doc.close()
        except:
            print _("Document write failure")

    #--------------------------------------------------------------------
    #
    # calc - calculate the maximum width that a box needs to be. From
    # that and the page dimensions, calculate the proper place to put
    # the elements on a page.
    #
    #--------------------------------------------------------------------
    def calc(self):
        self.filter(self.start,1)

	self.height = self.lines*pt2cm((125.0*self.font.get_size())/100.0)
	self.box_width = pt2cm(self.box_width+20)

        start = self.doc.get_right_margin()
	delta = (self.doc.get_usable_width() - (self.box_width + (5.0/10.0)))/3.0
        uh = self.doc.get_usable_height()

        ystart = self.doc.get_top_margin() - ((self.height+(3.0/10.0))/2.0)
        self.x = [start, start + delta, start + (2*delta), start + (3*delta)]
        self.y = [ ystart + (uh/2.0),   ystart + (uh/4.0),
                   ystart + 3*(uh/4.0), ystart + (uh/8.0),
                   ystart + 3*(uh/8.0), ystart + 5*(uh/8.0),
                   ystart + 7*(uh/8.0), 
                   ystart + (uh/16.0),   ystart + 3*(uh/16.0),
                   ystart + 5*(uh/16.0), ystart + 7*(uh/16.0),
                   ystart + 9*(uh/16.0), ystart + 11*(uh/16.0),
                   ystart + 13*(uh/16.0), ystart + 15*(uh/16.0)]

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
    def get_numbers(self,start,index,vals):
        if index > 4:
            return
        if self.map.has_key(start):
            vals.append(start)
        self.get_numbers(start*2,index+1,vals)
        self.get_numbers((start*2)+1,index+1,vals)

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def print_page(self,start,generation, page):
        self.doc.start_page()
        self.draw_graph(1,start,0)
        self.doc.end_page()

    #--------------------------------------------------------------------
    #
    #
    #
    #--------------------------------------------------------------------
    def draw_graph(self,index,start,level):
        if self.map.has_key(start) and index <= 15:
	    text = self.text[start]

	    name = string.join(text,"\n")
            self.doc.draw_box("box",name,self.x[level],self.y[index-1])

            if index > 1:
                old_index = int(index/2)-1
                x2 = self.x[level]
                x1 = self.x[level-1]+(self.x[level]-self.x[level-1])/2.0
                if index % 2 == 1:
                    y1 = self.y[old_index]+self.height
                else:
                    y1 = self.y[old_index]
                    
                y2 = self.y[index-1]+(self.height/2.0)
                self.doc.draw_line("line",x1,y1,x1,y2)
                self.doc.draw_line("line",x1,y2,x2,y2)
            self.draw_graph(index*2,start*2,level+1)
            self.draw_graph((index*2)+1,(start*2)+1,level+1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorChartDialog(DrawReportDialog):
    def __init__(self,database,person):
        DrawReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Ancestor Chart"),_("Graphical Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents."""
        return _("Ancestor Chart for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ancestor Chart")

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return "ancestor_chart.xml"
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\nb. $b\nd. $d",
                _("Allows you to customize the data in the boxes in the report"))

    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make the default output style for the Ancestor Chart report."""
        f = FontStyle()
        f.set_size(9)
        f.set_type_face(FONT_SANS_SERIF)
        p = ParagraphStyle()
        p.set_font(f)
        self.default_style.add_style("Normal",p)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""

        try:
            MyReport = AncestorChart(self.db, self.person, self.target_path,
                                     self.max_gen, self.doc, self.report_text)
            MyReport.write_report()
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorChartDialog(database,person)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 85 1",
        " 	c None",
        ".	c #887D6C",
        "+	c #8C8A87",
        "@	c #787775",
        "#	c #766D5F",
        "$	c #67655F",
        "%	c #5E5A54",
        "&	c #55524C",
        "*	c #BBBAB8",
        "=	c #B7AFA2",
        "-	c #A9A5A0",
        ";	c #99948A",
        ">	c #FAFAFA",
        ",	c #F8F6F2",
        "'	c #F6F2EC",
        ")	c #E6E5E5",
        "!	c #D2CCBF",
        "~	c #C7C6C3",
        "{	c #413F3F",
        "]	c #DCD9D4",
        "^	c #322E2B",
        "/	c #4F4E4C",
        "(	c #908F8D",
        "_	c #989897",
        ":	c #8A8986",
        "<	c #898885",
        "[	c #F5EEE5",
        "}	c #F5F5F5",
        "|	c #979695",
        "1	c #888784",
        "2	c #8B8A87",
        "3	c #1A1A1A",
        "4	c #858582",
        "5	c #949390",
        "6	c #858480",
        "7	c #92918E",
        "8	c #8F8E8B",
        "9	c #8E8D8A",
        "0	c #797773",
        "a	c #7B7975",
        "b	c #81807C",
        "c	c #817F7C",
        "d	c #989796",
        "e	c #807E7B",
        "f	c #8C8B88",
        "g	c #E3CAA5",
        "h	c #F2EADF",
        "i	c #DDCDB4",
        "j	c #8E8E8B",
        "k	c #888785",
        "l	c #EFE4D2",
        "m	c #969694",
        "n	c #9F9F9D",
        "o	c #E6D4B7",
        "p	c #A5967E",
        "q	c #8A8987",
        "r	c #EBDCC4",
        "s	c #878683",
        "t	c #9B9995",
        "u	c #9A9892",
        "v	c #807F7B",
        "w	c #7E7C79",
        "x	c #8E8C88",
        "y	c #8F8E8C",
        "z	c #8D8B88",
        "A	c #B59871",
        "B	c #878581",
        "C	c #8E8B87",
        "D	c #848480",
        "E	c #898785",
        "F	c #8A8886",
        "G	c #7D7B77",
        "H	c #8D8C89",
        "I	c #8B8A86",
        "J	c #918F8B",
        "K	c #989795",
        "L	c #BBA382",
        "M	c #8D8B86",
        "N	c #868480",
        "O	c #8E8C87",
        "P	c #8E8B86",
        "Q	c #8A8985",
        "R	c #807F7A",
        "S	c #8D8A84",
        "T	c #898884",
        "                                                ",
        "                                                ",
        "             .+....@@#####$$$%$%&$@             ",
        "             .**************=*-;+%%@            ",
        "             .*>>,>>>>>>,>>>>')!*..;&           ",
        "             .*>>>>>>>>>>>>>>>,)!=@~;{          ",
        "             .*,>>>>>>>>>>>>>>>,]]%)~+^         ",
        "             .*>>>>>>>>>>>>>>>>>))/>)~+^        ",
        "             .*>>>>>>>>>>>>>>>>>(_/>>)~+^       ",
        "             .*>>>>>>>>>>>>>>>>>:>/)>>)~+{      ",
        "             @*>>>>>>>>>>>>>>>>><>/]'>>)~;&     ",
        "             @*>>>>>>>>>>>>>>>>>:>/~][>>)~;$    ",
        "             #*>>>>>>>>>}}|1<<2>:>/33^{{%$@$@   ",
        "             .*>>>>>>>>>4:<<<<<56>)~*-;+@$%{$   ",
        "             #*>>>>>>>>><>|<1<7>8>>)!~=-;+@&{   ",
        "             #*>>>>>>>>><>>>>>>>9>>,]!~*-;+${   ",
        "             #*>>>>>>>>><>>>>>>>8>>,))~~*-;@^   ",
        "             #*>>>>>>>>><>>>>>>>:>(000a!~*-@^   ",
        "             #*>>>>>>>>>1>>>>>>>b2<<<1c]~~*.^   ",
        "             #*>>>>>>>>><>>>>>>>,>de<<f]g~*+^   ",
        "             #*>>>>>>>>><>>>>>>,,,''[h]]ii~+^   ",
        "             $*>>jkkkkj><>>>>>,>'''[[hl]]ig;^   ",
        "             $*>>mkkkkjn<>>>>>,,'''h[hl]o!!p^   ",
        "             $*>>jkkkkq><>>>>,'''[)[hhll]i!p^   ",
        "             $*>>>>>>>>><>>>,,'),[hh)llrro!p^   ",
        "             $*>>>>>>>>><>>,,'''h[hhhllrriip^   ",
        "             $*>>>>>>>>><>,'''h[hhlllllrroip^   ",
        "             %*>>>>>>>>><,''''[[hh|<s<2rroip^   ",
        "             %*>>>>>>>>><'''hhh)tu<<v0wrroip^   ",
        "             $*>>>>>>>>,<''['[[hxly<<<zroooA^   ",
        "             %*>>>>>>>,,<'hh)hhlxllrrrrrroiA^   ",
        "             %*>>>>>>,''1[[[[hllxlrlrroooooA^   ",
        "             %*>>>>>,,''<hqk<<BlClrrrrrooooA^   ",
        "             %*>>>>,'''hDEF<<<GHIrrrroooogiA^   ",
        "             %*>>>,,'''h)hJ<1<KrCrrorooooggL^   ",
        "             &*>>,''[[h[[hllllrlCroroooggogA^   ",
        "             &*>,,''[h[hlhllrlrrCroooooggggA^   ",
        "             &=,''[[[[hlhllllrrrMoqkk1NogggL^   ",
        "             &*''''h)hhlllrrrrrrOPQ<ksRggggA^   ",
        "             /=''h[[[h)llrllrrrooo2STE6ggggA^   ",
        "             &=''h)hlhlllrrrrorooooggggggggA^   ",
        "             /=[[[[hhllrrlrroroooogggggg*ggA^   ",
        "             /=hhhllllllrrrroooogogggggggggA^   ",
        "             /=*=======LLLLLLLLLLLLAAAAAAAAA^   ",
        "             ^^^^^^^^^^^^^^^^^^^^^^^^^^3^^3^^   ",
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
    _("Ancestor Chart"),
    category=_("Graphical Reports"),
    status=(_("Beta")),
    description=_("Produces a graphical ancestral tree graph"),
    xpm=get_xpm_image()
    )

