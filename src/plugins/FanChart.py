#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#------------------------------------------------------------------------
#
# gnome/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import GrampsCfg
import DrawDoc
import Report
import Errors
import TextDoc
import Calendar

from QuestionDialog import ErrorDialog
from FontScale import string_width
from SubstKeywords import SubstKeywords
from gettext import gettext as _

#------------------------------------------------------------------------
#
# pt2cm - convert points to centimeters
#
#------------------------------------------------------------------------
def pt2cm(pt):
    return (float(pt)/72.0)*(254.0/100.0)

#------------------------------------------------------------------------
#
# FanChart
#
#------------------------------------------------------------------------
class FanChart:

    def __init__(self,database,person,output,doc,display):
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

        g = DrawDoc.GraphicsStyle()
        g.set_paragraph_style('Title')
        self.doc.add_draw_style("t",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((255,212,210))
        g.set_paragraph_style('Normal')
        self.doc.add_draw_style("c1",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((255,212,210))
        g.set_paragraph_style('Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("c1n",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((251,204,158))
        g.set_paragraph_style('Normal')
        self.doc.add_draw_style("c2",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((251,204,158))
        g.set_paragraph_style('Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("c2n",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((255,255,111))
        g.set_paragraph_style('Normal')
        self.doc.add_draw_style("c3",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((255,255,111))
        g.set_paragraph_style('Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("c3n",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((158,255,158))
        g.set_paragraph_style('Normal')
        self.doc.add_draw_style("c4",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((158,255,158))
        g.set_paragraph_style('Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("c4n",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((156,205,255))
        g.set_paragraph_style('Normal')
        self.doc.add_draw_style("c5",g)

        g = DrawDoc.GraphicsStyle()
        g.set_fill_color((156,205,255))
        g.set_paragraph_style('Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("c5n",g)

        self.map = [None] * 32
	self.text= {}
        self.box_width = 0

    def filter(self,person,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""
        
        if person == None or index >= 32:
            return
        self.map[index-1] = person

	self.text[index-1] = []

        subst = SubstKeywords(person)
        
        for line in self.display:
            self.text[index-1].append(subst.replace(line))

        self.font = self.doc.style_list["Normal"].get_font()
	for line in self.text[index-1]:
	    self.box_width = max(self.box_width,string_width(self.font,line))

	self.lines = max(self.lines,len(self.text[index-1]))    

        family = person.getMainParents()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    def write_report(self):

        self.filter(self.start,1)

        block_size = self.doc.get_usable_width()/14.0
	try:
            self.doc.open(self.output)
        except Errors.ReportError, val:
            (m1,m2) = val.messages()
            ErrorDialog(m1,m2)

        size = min(self.doc.get_usable_width(),self.doc.get_usable_height()*2.0)/2.0
        y = self.doc.get_usable_height()
        max_lines = int(size/block_size)
        center = (self.doc.get_usable_width()/2.0)

        self.doc.start_page()
        
        n = self.start.getPrimaryName().getRegularName()
        self.doc.center_text('t', _('Five Generation Fan Chart for %s') % n, center, 0)

        self.circle_5(center,y,block_size)
        self.circle_4(center,y,block_size)
        self.circle_3(center,y,block_size)
        self.circle_2(center,y,block_size)
        self.circle_1(center,y,block_size)

        self.doc.end_page()
	try:
            self.doc.close()
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

    def get_info(self,person):
        pn = person.getPrimaryName()
        b = person.getBirth().getDateObj().getYear()
        d = person.getDeath().getDateObj().getYear()
        if b == Calendar.UNDEF:
            b = ""
        if d == Calendar.UNDEF:
            d = ""

        if b or d:
            val = "%s - %s" % (str(b),str(d))
        else:
            val = ""
            
        return [ pn.getFirstName(), pn.getSurname(), val ]

    def circle_1(self,center,y,size):
        (xc,yc) = self.doc.draw_wedge("c1", center, y, size, 180, 360)
        print center, y, xc, yc
        self.doc.rotate_text("c1n", self.get_info(self.map[0]), xc, yc ,0)

    def circle_2(self,center,y,size):
        (xc,yc) = self.doc.draw_wedge("c2", center, y, size*2, 180, 270, size)
        if self.map[1]:
            self.doc.rotate_text("c2n", self.get_info(self.map[1]), xc, yc, -45)
            
        (xc,yc) = self.doc.draw_wedge("c2", center, y, size*2, 270, 360, size)
        if self.map[2]:
            self.doc.rotate_text("c2n", self.get_info(self.map[2]), xc,yc ,45)

    def circle_3(self,center,y,size):
        delta = 45
        sangle = -67.5
        for index in range(3,7):
            start = 180+(index-3)*45
            stop = start+45
            (xc,yc) = self.doc.draw_wedge("c3", center, y, size*3, start, stop, size*2)
            if self.map[index]:
                self.doc.rotate_text("c3n", self.get_info(self.map[index]),
                                     xc,yc ,sangle)
            sangle += 45

    def circle_4(self,center,y,size):
        delta = 22.5
        sangle = -78.75 + 90
        for i in range(0,8):
            start_angle = 180 + (i * delta)
            end_angle = 180 + ((i+1) * delta)
            (xc,yc) = self.doc.draw_wedge("c4", center, y, size*5, start_angle,
                                          end_angle, size*3)
            if i == 4:
                sangle += 180
            if self.map[i+7]:
                self.doc.rotate_text("c4n", self.get_info(self.map[i+7]),
                                     xc,yc ,sangle)
            sangle += 22.5

    def circle_5(self,center,y,size):
        delta = 11.25
        sangle = -84.625 + 90
        for i in range(0,16):
            start_angle = 180 + (i * delta)
            end_angle = 180 + ((i+1) * delta)
            (xc,yc) = self.doc.draw_wedge("c5", center, y, size*7, start_angle,
                                          end_angle, size*5)
            if i == 8:
                sangle += 180
            if self.map[i+15]:
                self.doc.rotate_text("c5n", self.get_info(self.map[i+15]),
                                     xc,yc ,sangle)
            sangle += 11.25

#------------------------------------------------------------------------
#
# FanChartDialog 
#
#------------------------------------------------------------------------
class FanChartDialog(Report.DrawReportDialog):
    
    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Fan Chart"),_("Graphical Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents."""
        return _("Fan Chart for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Fan Chart")

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return "fan_chart.xml"
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (0, 0)

    def make_default_style(self):
        """Make the default output style for the Ancestor Chart report."""
        f = TextDoc.FontStyle()
        f.set_size(8)
        f.set_type_face(TextDoc.FONT_SANS_SERIF)
        p = TextDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(TextDoc.PARA_ALIGN_CENTER)
        self.default_style.add_style("Normal",p)

        f = TextDoc.FontStyle()
        f.set_size(20)
        f.set_bold(1)
        f.set_type_face(TextDoc.FONT_SANS_SERIF)
        p = TextDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(TextDoc.PARA_ALIGN_CENTER)
        self.default_style.add_style("Title",p)

    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""

        try:
            MyReport = FanChart(self.db, self.person, self.target_path,self.doc,"%n")
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Entry point of the report. Takes the database and the active person
# as its arguments.
#
#------------------------------------------------------------------------
def report(database,person):
    FanChartDialog(database,person)

#------------------------------------------------------------------------
#
# Register the report with the plugin system. If this is not done, then
# GRAMPS will not know that the report exists.
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Fan Chart"),
    category=_("Graphical Reports"),
    status=(_("Alpha")),
    description=_("Produces a five generation fan chart")
    )

