#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
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
import Report
import Errors
import Calendar

from QuestionDialog import ErrorDialog
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

    def __init__(self,database,person,display,doc,output,newpage=0):
        self.database = database
        self.doc = doc
        self.doc.creator(database.get_researcher().get_name())
        self.map = {}
        self.text = {}
        self.start = person
        self.output = output
        self.box_width = 0
        self.height = 0
        self.lines = 0
        self.display = display
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
        else:
            self.standalone = 0

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

        self.map = [None] * 32
        self.text= {}
        self.box_width = 0
        if self.standalone:
            self.doc.init()

    def filter(self,person_handle,index):
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
            self.filter(family.get_father_handle(),index*2)
            self.filter(family.get_mother_handle(),(index*2)+1)

    def write_report(self):

        self.filter(self.start.get_handle(),1)

        block_size = self.doc.get_usable_width()/14.0

        if self.newpage:
            self.doc.page_break()

        size = min(self.doc.get_usable_width(),self.doc.get_usable_height()*2.0)/2.0
        y = self.doc.get_usable_height()
        max_lines = int(size/block_size)
        center = (self.doc.get_usable_width()/2.0)

        self.doc.start_page()
        
        n = self.start.get_primary_name().get_regular_name()
        self.doc.center_text('t', _('Five Generation Fan Chart for %s') % n, center, 0)

        self.circle_5(center,y,block_size)
        self.circle_4(center,y,block_size)
        self.circle_3(center,y,block_size)
        self.circle_2(center,y,block_size)
        self.circle_1(center,y,block_size)

        self.doc.end_page()
        if self.standalone:
            self.doc.close()

    def get_info(self,person_handle):
        person = self.database.get_person_from_handle(person_handle)
        pn = person.get_primary_name()

        birth_handle = person.get_birth_handle()
        if birth_handle:
            b = self.database.find_event_from_handle(birth_handle).get_date_object().get_year()
            if b == Calendar.UNDEF:
                b = ""
        else:
            b = ""

        death_handle = person.get_death_handle()
        if death_handle:
            d = self.database.find_event_from_handle(death_handle).get_date_object().get_year()
            if d == Calendar.UNDEF:
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
def _make_default_style(default_style):
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
# FanChartDialog 
#
#------------------------------------------------------------------------
class FanChartDialog(Report.DrawReportDialog):

    report_options = {}
    
    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person,self.report_options)

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
        return _style_file
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (0, 0)

    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Fan Chart.
        All user dialog has already been handled and the output file
        opened."""

        try:
            MyReport = FanChart(self.db, self.person,
                        "%n", self.doc, self.target_path)
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
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "fan_chart.xml"
_style_name = "default" 

_person_handle = ""
_options = ( _person_handle, )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class FanChartBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person_from_handle(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)
        self.new_person = None
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Fan Chart"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Fan Chart for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """No generations, no page breaks."""
        return (0, 0)
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.get_handle(), )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Fan Chart using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person_from_handle(options[0])
        return FanChart(database, person, 
                                   "%n", doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Register the report with the plugin system. If this is not done, then
# GRAMPS will not know that the report exists.
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Fan Chart"),
    category=_("Graphical Reports"),
    status=(_("Alpha")),
    description=_("Produces a five generation fan chart")
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Fan Chart"), 
    _("Graphics"),
    FanChartBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
