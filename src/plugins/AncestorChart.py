#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Graphical Reports/Ancestor Chart"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string

#------------------------------------------------------------------------
#
# gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import BaseDoc
import Report
import Errors
import FontScale
from QuestionDialog import ErrorDialog
from SubstKeywords import SubstKeywords
from gettext import gettext as _

_BORN = _('b.')
_DIED = _('d.')

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

    def __init__(self,database,person,max,display,doc,output,newpage=0):
        self.database = database
        self.doc = doc
        self.doc.creator(database.get_researcher().get_name())
        self.map = {}
        self.text = {}
        self.start = person
        self.max_generations = max
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
        self.calc()
        
    def filter(self,person_handle,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""
        
        if (not person_handle) or (index >= 2**self.max_generations):
            return
        self.map[index] = person_handle

        self.text[index] = []

        subst = SubstKeywords(self.database,person_handle)
        
        for line in self.display:
            self.text[index].append(subst.replace(line))

        self.font = self.doc.style_list["AC-Normal"].get_font()
        for line in self.text[index]:
            self.box_width = max(self.box_width,FontScale.string_width(self.font,line))

        self.lines = max(self.lines,len(self.text[index]))    

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.find_family_from_handle(family_handle)
            self.filter(family.get_father_handle(),index*2)
            self.filter(family.get_mother_handle(),(index*2)+1)

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

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
        if self.standalone:
            self.doc.close()

    def calc(self):
        """
        calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page.
        """
        self.filter(self.start.get_handle(),1)

        self.height = self.lines*pt2cm((125.0*self.font.get_size())/100.0)
        self.box_width = pt2cm(self.box_width+20)

        start = 0
        delta = (self.doc.get_usable_width() - (self.box_width + (5.0/10.0)))/3.0
        uh = self.doc.get_usable_height()

        ystart = -self.height/2.0
        self.x = [start, start + delta, start + (2*delta), start + (3*delta)]
        self.y = [ ystart + (uh/2.0),   ystart + (uh/4.0),
                   ystart + 3*(uh/4.0), ystart + (uh/8.0),
                   ystart + 3*(uh/8.0), ystart + 5*(uh/8.0),
                   ystart + 7*(uh/8.0), 
                   ystart + (uh/16.0),   ystart + 3*(uh/16.0),
                   ystart + 5*(uh/16.0), ystart + 7*(uh/16.0),
                   ystart + 9*(uh/16.0), ystart + 11*(uh/16.0),
                   ystart + 13*(uh/16.0), ystart + 15*(uh/16.0)]

        g = BaseDoc.GraphicsStyle()
        g.set_height(self.height)
        g.set_width(self.box_width)
        g.set_paragraph_style("AC-Normal")
        g.set_shadow(1)
        g.set_fill_color((255,255,255))
        self.doc.add_draw_style("AC-box",g)

        g = BaseDoc.GraphicsStyle()
        self.doc.add_draw_style("AC-line",g)
        if self.standalone:
            self.doc.init()

    def get_numbers(self,start,index,vals):
        if index > 4:
            return
        if self.map.has_key(start):
            vals.append(start)
        self.get_numbers(start*2,index+1,vals)
        self.get_numbers((start*2)+1,index+1,vals)

    def print_page(self,start,generation, page):
        self.doc.start_page()
        self.draw_graph(1,start,0)
        self.doc.end_page()

    def draw_graph(self,index,start,level):
        if self.map.has_key(start) and index <= 15:
            text = self.text[start]

            name = string.join(text,"\n")
            self.doc.draw_box("AC-box",name,self.x[level],self.y[index-1])

            if index > 1:
                old_index = int(index/2)-1
                x2 = self.x[level]
                x1 = self.x[level-1]+(self.x[level]-self.x[level-1])/2.0
                if index % 2 == 1:
                    y1 = self.y[old_index]+self.height
                else:
                    y1 = self.y[old_index]
                    
                y2 = self.y[index-1]+(self.height/2.0)
                self.doc.draw_line("AC-line",x1,y1,x1,y2)
                self.doc.draw_line("AC-line",x1,y2,x2,y2)
            self.draw_graph(index*2,start*2,level+1)
            self.draw_graph((index*2)+1,(start*2)+1,level+1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
    """Make the default output style for the Ancestor Chart report."""
    f = BaseDoc.FontStyle()
    f.set_size(9)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_description(_('The basic style used for the text display.'))
    default_style.add_style("AC-Normal",p)

#------------------------------------------------------------------------
#
# AncestorChartDialog
#
#------------------------------------------------------------------------
class AncestorChartDialog(Report.DrawReportDialog):

    report_options = {}
    
    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person,self.report_options)

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
        return _style_file
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\n%s $b\n%s $d" % (_BORN,_DIED),
                _("Allows you to customize the data in the boxes in the report"))

    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""

        try:
            MyReport = AncestorChart(self.db, self.person, 
                self.max_gen, self.report_text, self.doc,self.target_path)
            MyReport.write_report()
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
# entry point
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorChartDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ancestor_chart.xml"
_style_name = "default" 

_person_handle = ""
_max_gen = 10
_disp_format = [ "$n", "%s $b" % _BORN, "%s $d" % _DIED ]
_options = ( _person_handle, _max_gen, _disp_format )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class AncestorChartBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person_from_handle(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.max_gen = int(self.options[1])
        self.disp_format = string.join(self.options[2],'\n')
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.extra_textbox.get_buffer().set_text(
            self.disp_format,len(self.disp_format))
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Ancestor Chart"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ancestor Chart for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\n%s $b\n%s $d" % (_BORN,_DIED),
                _("Allows you to customize the data in the boxes in the report"))

    def make_default_style(self):
        _make_default_style(self.default_style)

    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.get_handle(), self.max_gen, self.report_text )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Ancestor Chart using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person_from_handle(options[0])
        max_gen = int(options[1])
        disp_format = options[2]
        return AncestorChart(database, person, max_gen,
                                   disp_format, doc, None, newpage )
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
# 
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Ancestor Chart"),
    category=_("Graphical Reports"),
    status=(_("Beta")),
    description=_("Produces a graphical ancestral tree graph"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Ancestor Chart"), 
    _("Graphics"),
    AncestorChartBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )

