#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

"""Reports/Graphical Reports/Descendant Tree..."""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from BasicUtils import name_displayer
from PluginUtils import register_report, NumberOption, BooleanOption, \
    TextOption, PersonOption
from ReportBase import Report, MenuReportOptions, \
    ReportUtils, CATEGORY_DRAW, MODE_GUI, MODE_BKI, MODE_CLI
from SubstKeywords import SubstKeywords
from gettext import gettext as _
import BaseDoc

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
pt2cm = ReportUtils.pt2cm
cm2pt = ReportUtils.cm2pt

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('b.')
_DIED = _('d.')

_LINE_HORIZONTAL = 1
_LINE_VERTICAL   = 2
_LINE_ANGLE      = 3

#------------------------------------------------------------------------
#
# Layout class
#
#------------------------------------------------------------------------
class GenChart:

    def __init__(self,generations):
        self.generations = generations
        self.map = {}
        
        self.array = {}
        self.max_x = 0
        self.max_y = 0
        
    def get_xy(self,x,y):
        if not self.array.has_key(y):
            return 0
        return self.array[y].get(x,0)

    def set_xy(self,x,y,value):
        self.max_x = max(self.max_x,x)
        self.max_y = max(self.max_y,y)

        if not self.array.has_key(y):
            self.array[y] = {}
        self.array[y][x] = value

    def dimensions(self):
        return (self.max_y+1,self.max_x+1)

    def not_blank(self,line):
        for i in line:
            if i and type(i) == tuple:
                return 1
        return 0

#------------------------------------------------------------------------
#
# DescendChart
#
#------------------------------------------------------------------------
class DescendChart(Report):

    def __init__(self,database,person,options_class):
        """
        Creates DescendChart object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        dispf     - Display format for the output box.
        singlep   - Whether to scale to fit on a single page.
        maxgen    - Maximum number of generations to include.
        """
        Report.__init__(self, database, person, options_class)
        
        menu = options_class.menu
        self.display = menu.get_option_by_name('dispf').get_value()
        self.max_generations = menu.get_option_by_name('maxgen').get_value()
        self.force_fit = menu.get_option_by_name('singlep').get_value()
        self.incblank = menu.get_option_by_name('incblank').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        center_person = database.get_person_from_gramps_id(pid)
        
        name = name_displayer.display_formal(center_person)
        self.title = _("Descendant Chart for %s") % name

        self.map = {}
        self.text = {}

        self.box_width = 0
        self.box_height = 0
        self.lines = 0
        self.scale = 1
        self.box_gap = 0.2
        
        self.genchart = GenChart(32)
        
        self.apply_filter(center_person.get_handle(),0,0)

        self.calc()
        
        if self.force_fit:
            self.scale_styles()

    def apply_filter(self,person_handle,x,y):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""

        if x/2 >= self.max_generations:
            return 0

        self.genchart.set_xy(x,y,person_handle)
        
        person = self.database.get_person_from_handle(person_handle)

        index = 0
        
        style_sheet = self.doc.get_style_sheet()
        pstyle = style_sheet.get_paragraph_style("DC2-Normal")
        font = pstyle.get_font()

        em = self.doc.string_width(font,"m")

        subst = SubstKeywords(self.database,person_handle)
        self.text[(x,y)] = subst.replace_and_clean(self.display)
        for line in self.text[(x,y)]:
            this_box_width = self.doc.string_width(font,line) + 2*em
            self.box_width = max(self.box_width,this_box_width)

        self.lines = max(self.lines,len(self.text[(x,y)]))    

        new_y = y
        for family_handle in person.get_family_handle_list():
            
            family = self.database.get_family_from_handle(family_handle)

            for child_ref in family.get_child_ref_list():
                sub = self.apply_filter(child_ref.ref, x+2, new_y)
                index += sub
                new_y += sub

        return max(1,index)

    def add_lines(self):

        (maxy,maxx) = self.genchart.dimensions()

        for y in range(0,maxy+1):
            for x in range(0,maxx+1):
                # skip columns reserved for rows - no data here
                if x%2:
                    continue

                # if we have a person directly next to a person, that
                # person must be a child of the first person
                
                if self.genchart.get_xy(x,y) and self.genchart.get_xy(x+2,y):
                    self.genchart.set_xy(x+1,y,_LINE_HORIZONTAL)
                else:
                    continue

                # look through the entries below this one. All people in the
                # next column are descendants until we hit a person in our own
                # column.

                last = y
                for newy in range(y+1,maxy+1):
                    if self.genchart.get_xy(x,newy):
                        break

                    # if the next position is occupied, we need an
                    # angle, otherwise, we may need a vertical line.
                    if self.genchart.get_xy(x+2,newy):
                        self.genchart.set_xy(x+1,newy,_LINE_ANGLE)
                        for tempy in range(last+1,newy):
                            self.genchart.set_xy(x+1,tempy,_LINE_VERTICAL)
                        last = newy

    def write_report(self):

        (maxy,maxx) = self.genchart.dimensions()
        maxx = (maxx-1)*2
        maxh = int((self.uh-0.75)/(self.box_height*1.25))

        if self.force_fit:
            self.print_page(0,maxx,0,maxy,0,0)
        else:
            starty = 0
            coly = 0
            while starty < maxy:
                startx = 0
                colx = 0
                while startx < maxx:
                    stopx = min(maxx,startx+self.generations_per_page*2)
                    stopy = min(maxy,starty+maxh)
                    self.print_page(startx,stopx,starty,stopy,colx,coly)
                    colx += 1
                    startx += self.generations_per_page*2
                coly += 1
                starty += maxh
            
    def calc(self):
        """
        calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page.
        """
        style_sheet = self.doc.get_style_sheet()

        self.add_lines()

        self.box_pad_pts = 10
        if self.title and self.force_fit:
            pstyle = style_sheet.get_paragraph_style("DC2-Title")
            tfont = pstyle.get_font()
            self.offset = pt2cm(1.25 * tfont.get_size())
            
            gstyle = style_sheet.get_draw_style("DC2-box")
            shadow_height = gstyle.get_shadow_space()
        else:
            # Make space for the page number labels at the bottom.
            p = style_sheet.get_paragraph_style("DC2-Normal")
            font = p.get_font()
            lheight = pt2cm(1.2*font.get_size())
            lwidth = pt2cm(1.1*self.doc.string_width(font,"(00,00)"))
            self.page_label_x_offset = self.doc.get_usable_width()  - lwidth
            self.page_label_y_offset = self.doc.get_usable_height() - lheight

            self.offset = pt2cm(1.25 * font.get_size())
            shadow_height = 0
        self.uh = self.doc.get_usable_height() - self.offset - shadow_height
        uw = self.doc.get_usable_width() - pt2cm(self.box_pad_pts)

        calc_width = pt2cm(self.box_width + self.box_pad_pts) + self.box_gap
        self.box_width = pt2cm(self.box_width)
        pstyle = style_sheet.get_paragraph_style("DC2-Normal")
        font = pstyle.get_font()
        self.box_height = self.lines*pt2cm(1.25*font.get_size())

        self.scale = 1
        
        if self.force_fit:
            (maxy,maxx) = self.genchart.dimensions()

            bw = (calc_width/(uw/(maxx+1)))
            bh = (self.box_height*(1.25)+self.box_gap)/(self.uh/maxy)
            
            self.scale = max(bw/2,bh)
            self.box_width = self.box_width/self.scale
            self.box_height = self.box_height/self.scale
            self.box_pad_pts = self.box_pad_pts/self.scale
            self.box_gap = self.box_gap/self.scale

#        maxh = int((self.uh)/(self.box_height+self.box_gap))
        maxw = int(uw/calc_width) 

        # build array of x indices

        self.generations_per_page = maxw
        
        self.delta = pt2cm(self.box_pad_pts) + self.box_width + self.box_gap
        if not self.force_fit:
            calc_width = self.box_width + pt2cm(self.box_pad_pts)
            remain = self.doc.get_usable_width() - ((self.generations_per_page)*calc_width)
            self.delta += remain/float(self.generations_per_page)

    def scale_styles(self):
        """
        Scale the styles for this report. This must be done in the constructor.
        """
        style_sheet = self.doc.get_style_sheet()

        g = style_sheet.get_draw_style("DC2-box")
        g.set_shadow(g.get_shadow(),g.get_shadow_space()/self.scale)
        g.set_line_width(g.get_line_width()/self.scale)
        style_sheet.add_draw_style("DC2-box",g)
        
        p = style_sheet.get_paragraph_style("DC2-Normal")
        font = p.get_font()
        font.set_size(font.get_size()/self.scale)
        p.set_font(font)
        style_sheet.add_paragraph_style("DC2-Normal",p)
            
        self.doc.set_style_sheet(style_sheet)

    def print_page(self,startx,stopx,starty,stopy,colx,coly):

        if not self.incblank:
            blank = True
            for y in range(starty,stopy):
                for x in range(startx,stopx):
                    if self.genchart.get_xy(x,y) != 0:
                        blank = False
                        break
                if not blank: break
            if blank: return

        self.doc.start_page()
        if self.title and self.force_fit:
            self.doc.center_text('DC2-title',self.title,self.doc.get_usable_width()/2,0)
        phys_y = 1
        bh = self.box_height * 1.25
        for y in range(starty,stopy):
            phys_x = 0
            for x in range(startx,stopx):
                value = self.genchart.get_xy(x,y)
                if type(value) == str or type(value) == unicode:
                    text = '\n'.join(self.text[(x,y)])
                    xbegin = phys_x*self.delta
                    yend   = phys_y*bh+self.offset
                    self.doc.draw_box("DC2-box",
                                      text,
                                      xbegin,
                                      yend,
                                      self.box_width,
                                      self.box_height)
                elif value == _LINE_HORIZONTAL:
                    xbegin = phys_x*self.delta
                    ystart = (phys_y*bh + self.box_height/2.0) + self.offset
                    xstart = xbegin + self.box_width
                    xstop  = (phys_x+1)*self.delta
                    self.doc.draw_line('DC2-line', xstart, ystart, xstop, ystart)
                elif value == _LINE_VERTICAL:
                    ystart = ((phys_y-1)*bh + self.box_height/2.0) + self.offset
                    ystop  = (phys_y*bh + self.box_height/2.0) + self.offset
                    xlast  = (phys_x*self.delta) + self.box_width + self.box_gap
                    self.doc.draw_line('DC2-line', xlast, ystart, xlast, ystop)
                elif value == _LINE_ANGLE:
                    ystart = ((phys_y-1)*bh + self.box_height/2.0) + self.offset
                    ystop  = (phys_y*bh + self.box_height/2.0) + self.offset
                    xlast  = (phys_x*self.delta) + self.box_width + self.box_gap
                    xnext  = (phys_x+1)*self.delta
                    self.doc.draw_line('DC2-line', xlast, ystart, xlast, ystop)
                    self.doc.draw_line('DC2-line', xlast, ystop, xnext, ystop)
                
                if x%2:
                    phys_x +=1
            phys_y += 1
                    
        if not self.force_fit:
            self.doc.draw_text('DC2-box',
                               '(%d,%d)' % (colx+1,coly+1),
                               self.page_label_x_offset,
                               self.page_label_y_offset)
        self.doc.end_page()
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendChartOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the descendant report.
        """
        category_name = _("Report Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", pid)
        
        max_gen = NumberOption(_("Generations"),10,1,50)
        max_gen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name,"maxgen",max_gen)
        
        disp = TextOption( _("Display Format"),
                           ["$n","%s $b" % _BORN,"%s $d" %_DIED] )
        disp.set_help(_("Display format for the outputbox."))
        menu.add_option(category_name,"dispf",disp)
        
        scale = BooleanOption(_('Sc_ale to fit on a single page'),True)
        scale.set_help(_("Whether to scale to fit on a single page."))
        menu.add_option(category_name,"singlep",scale)
        
        blank = BooleanOption(_('Include Blank Pages'),True)
        blank.set_help(_("Whether to include pages that are blank."))
        menu.add_option(category_name,"incblank",blank)
        
        compress = BooleanOption(_('Co_mpress chart'),True)
        compress.set_help(_("Whether to compress chart."))
        menu.add_option(category_name,"compress",compress)
        
    def make_default_style(self,default_style):
        """Make the default output style for the Ancestor Chart report."""
        ## Paragraph Styles:
        f = BaseDoc.FontStyle()
        f.set_size(9)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("DC2-Normal",p)

        f = BaseDoc.FontStyle()
        f.set_size(16)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The basic style used for the title display.'))
        default_style.add_paragraph_style("DC2-Title",p)
        
        ## Draw styles
        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("DC2-Normal")
        g.set_shadow(1,0.2)
        g.set_fill_color((255,255,255))
        default_style.add_draw_style("DC2-box",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("DC2-Title")
        g.set_color((0,0,0))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        default_style.add_draw_style("DC2-title",g)

        g = BaseDoc.GraphicsStyle()
        default_style.add_draw_style("DC2-line",g)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'descend_chart',
    category = CATEGORY_DRAW,
    report_class = DescendChart,
    options_class = DescendChartOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Descendant Tree..."),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces a graphical descendant tree chart"),
    )
