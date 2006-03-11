#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

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
import BaseDoc
from PluginUtils import Report, ReportOptions, ReportUtils, register_report
from SubstKeywords import SubstKeywords
pt2cm = ReportUtils.pt2cm

#------------------------------------------------------------------------
#
# FanChart
#
#------------------------------------------------------------------------
class FanChart(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates the FanChart object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        display   - 
        """
        Report.Report.__init__(self,database,person,options_class)

        self.height = 0
        self.lines = 0
        self.display = "%n"
        self.map = [None] * 32
        self.text= {}
        self.box_width = 0

    def define_graphics_styles(self):
        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style('FC-Title')
        g.set_line_width(0)
        self.doc.add_draw_style("t",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((255,212,210))
        g.set_paragraph_style('FC-Normal')
        self.doc.add_draw_style("FC-c1",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((255,212,210))
        g.set_paragraph_style('FC-Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("FC-c1n",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((251,204,158))
        g.set_paragraph_style('FC-Normal')
        self.doc.add_draw_style("FC-c2",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((251,204,158))
        g.set_paragraph_style('FC-Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("FC-c2n",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((255,255,111))
        g.set_paragraph_style('FC-Normal')
        self.doc.add_draw_style("FC-c3",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((255,255,111))
        g.set_paragraph_style('FC-Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("FC-c3n",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((158,255,158))
        g.set_paragraph_style('FC-Normal')
        self.doc.add_draw_style("FC-c4",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((158,255,158))
        g.set_paragraph_style('FC-Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("FC-c4n",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((156,205,255))
        g.set_paragraph_style('FC-Normal')
        self.doc.add_draw_style("FC-c5",g)

        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((156,205,255))
        g.set_paragraph_style('FC-Normal')
        g.set_line_width(0)
        self.doc.add_draw_style("FC-c5n",g)

    def apply_filter(self,person_handle,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""
        
        if (not person_handle) or (index >= 32):
            return
        self.map[index-1] = person_handle

        self.text[index-1] = []

        subst = SubstKeywords(self.database,person_handle)
        
        for line in self.display:
            self.text[index-1].append(subst.replace(line))

        self.font = self.doc.style_list["FC-Normal"].get_font()
        for line in self.text[index-1]:
            self.box_width = max(self.box_width,self.doc.string_width(self.font,line))

        self.lines = max(self.lines,len(self.text[index-1]))    

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2)
            self.apply_filter(family.get_mother_handle(),(index*2)+1)

    def write_report(self):

        self.apply_filter(self.start_person.get_handle(),1)

        block_size = self.doc.get_usable_width()/14.0

        size = min(self.doc.get_usable_width(),self.doc.get_usable_height()*2.0)/2.0
        y = self.doc.get_usable_height()
        max_lines = int(size/block_size)
        center = (self.doc.get_usable_width()/2.0)

        self.doc.start_page()
        
        n = self.start_person.get_primary_name().get_regular_name()
        self.doc.center_text('t', _('Five Generation Fan Chart for %s') % n, center, 0)

        self.circle_5(center,y,block_size)
        self.circle_4(center,y,block_size)
        self.circle_3(center,y,block_size)
        self.circle_2(center,y,block_size)
        self.circle_1(center,y,block_size)

        self.doc.end_page()

    def get_info(self,person_handle):
        person = self.database.get_person_from_handle(person_handle)
        pn = person.get_primary_name()

        birth_handle = person.get_birth_handle()
        if birth_handle:
            b = self.database.get_event_from_handle(birth_handle).get_date_object().get_year()
            if b == 0:
                b = ""
        else:
            b = ""

        death_handle = person.get_death_handle()
        if death_handle:
            d = self.database.get_event_from_handle(death_handle).get_date_object().get_year()
            if d == 0:
                d = ""
        else:
            d = ""

        if b or d:
            val = "%s - %s" % (str(b),str(d))
        else:
            val = ""
            
        return [ pn.get_first_name(), pn.get_surname(), val ]

    def circle_1(self,center,y,size):
        (xc,yc) = self.doc.draw_wedge("FC-c1", center, y, size, 180, 360)
        self.doc.rotate_text("FC-c1n", self.get_info(self.map[0]), xc, yc ,0)

    def circle_2(self,center,y,size):
        (xc,yc) = self.doc.draw_wedge("FC-c2", center, y, size*2, 180, 270, size)
        if self.map[1]:
            self.doc.rotate_text("FC-c2n", self.get_info(self.map[1]), xc, yc, -45)
            
        (xc,yc) = self.doc.draw_wedge("FC-c2", center, y, size*2, 270, 360, size)
        if self.map[2]:
            self.doc.rotate_text("FC-c2n", self.get_info(self.map[2]), xc,yc ,45)

    def circle_3(self,center,y,size):
        delta = 45
        sangle = -67.5
        for index in range(3,7):
            start = 180+(index-3)*45
            stop = start+45
            (xc,yc) = self.doc.draw_wedge("FC-c3", center, y, size*3, start, stop, size*2)
            if self.map[index]:
                self.doc.rotate_text("FC-c3n", self.get_info(self.map[index]),
                                     xc,yc ,sangle)
            sangle += 45

    def circle_4(self,center,y,size):
        delta = 22.5
        sangle = -78.75 + 90
        for i in range(0,8):
            start_angle = 180 + (i * delta)
            end_angle = 180 + ((i+1) * delta)
            (xc,yc) = self.doc.draw_wedge("FC-c4", center, y, size*5, start_angle,
                                          end_angle, size*3)
            if i == 4:
                sangle += 180
            if self.map[i+7]:
                self.doc.rotate_text("FC-c4n", self.get_info(self.map[i+7]),
                                     xc,yc ,sangle)
            sangle += 22.5

    def circle_5(self,center,y,size):
        delta = 11.25
        sangle = -84.625 + 90
        for i in range(0,16):
            start_angle = 180 + (i * delta)
            end_angle = 180 + ((i+1) * delta)
            (xc,yc) = self.doc.draw_wedge("FC-c5", center, y, size*7, start_angle,
                                          end_angle, size*5)
            if i == 8:
                sangle += 180
            if self.map[i+15]:
                self.doc.rotate_text("FC-c5n", self.get_info(self.map[i+15]),
                                     xc,yc ,sangle)
            sangle += 11.25

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FanChartOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)


    def make_default_style(self,default_style):
        """Make the default output style for the Fan Chart report."""
        f = BaseDoc.FontStyle()
        f.set_size(8)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("FC-Normal",p)

        f = BaseDoc.FontStyle()
        f.set_size(20)
        f.set_bold(1)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The style used for the title.'))
        default_style.add_style("FC-Title",p)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
register_report(
    name = 'fan_chart',
    category = Report.CATEGORY_DRAW,
    report_class = FanChart,
    options_class = FanChartOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Fan Chart"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces a five generation fan chart")
    )
