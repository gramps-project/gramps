#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gettext import gettext as _

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
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_DRAW, MODE_GUI, MODE_BKI, MODE_CLI

from SubstKeywords import SubstKeywords
pt2cm = ReportUtils.pt2cm

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('b.')
_DIED = _('d.')

#------------------------------------------------------------------------
#
# AncestorChart
#
#------------------------------------------------------------------------
class AncestorChart(Report):

    def __init__(self,database,person,options_class):
        """
        Creates AncestorChart object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.
        dispf     - Display format for the output box.
        """
        Report.__init__(self,database,person,options_class)

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()
        self.display = options_class.handler.options_dict['dispf']

        self.map = {}
        self.text = {}

        self.box_width = 0
        self.height = 0
        self.lines = 0
        self.calc()
        
    def apply_filter(self,person_handle,index):
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
            this_box_width = self.doc.string_width(self.font,line)
            self.box_width = max(self.box_width,this_box_width)

        self.lines = max(self.lines,len(self.text[index]))    

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2)
            self.apply_filter(family.get_mother_handle(),(index*2)+1)

    def write_report(self):

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

    def calc(self):
        """
        calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page.
        """
        self.apply_filter(self.start_person.get_handle(),1)

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

            name = "\n".join(text)
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
class AncestorChartOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
            'dispf'     : [ "$n", "%s $b" % _BORN, "%s $d" % _DIED ],
        }

    def make_default_style(self,default_style):
        """Make the default output style for the Ancestor Chart report."""
        f = BaseDoc.FontStyle()
        f.set_size(9)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("AC-Normal",p)

    def get_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), self.options_dict['dispf'],
                _("Allows you to customize the data in the boxes in the report"))

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        dialog.get_report_extra_textbox_info = self.get_textbox_info

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'ancestor_chart',
    category = CATEGORY_DRAW,
    report_class = AncestorChart,
    options_class = AncestorChartOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Ancestor Chart"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces a graphical ancestral tree graph"),
    unsupported = True,
    )
