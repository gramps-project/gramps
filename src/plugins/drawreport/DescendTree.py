#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009  Craig J. Anderson
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

"""Reports/Graphical Reports/Descendant Tree"""

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from BasicUtils import name_displayer
from Errors import ReportError
from gen.plug.docgen import (GraphicsStyle, FontStyle, ParagraphStyle,
                            FONT_SANS_SERIF, PARA_ALIGN_CENTER)
from gen.plug.menu import TextOption, NumberOption, BooleanOption, PersonOption
from ReportBase import Report, MenuReportOptions, ReportUtils
from SubstKeywords import SubstKeywords
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('short for born|b.')
_MARR = _('short for married|m.')
_DIED = _('short for died|d.')

_LINE_HORIZONTAL = 1
_LINE_VERTICAL   = 2
_LINE_ANGLE      = 3

_PERSON_DIRECT = 1
_PERSON_SPOUSE = 2

#------------------------------------------------------------------------
#
# Layout class
#
#------------------------------------------------------------------------
class GenChart(object):

    def __init__(self, generations):
        self.generations = generations
        self.map = {}
        
        self.array = {}
        self.sparray = {}
        self.max_x = 0
        self.max_y = 0
        
    def get_xy(self, x, y):
        if y not in self.array:
            return 0
        return self.array[y].get(x, 0)

    def set_xy(self, x, y, value):
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

        if y not in self.array:
            self.array[y] = {}
        self.array[y][x] = value

    def get_sp(self, col_x, row_y):
        """gets whether person at x,y
        is a direct descendent or a spouse"""
        if (col_x, row_y) not in self.sparray:
            return None
        return self.sparray[col_x, row_y]

    def set_sp(self, col_x, row_y, value):
        """sets whether person at x,y
        is a direct descendent or a spouse"""
        self.sparray[col_x, row_y] = value

    def dimensions(self):
        """
        Returns the dimensions of the chart.
        """
        return (self.max_y+1, self.max_x+1)

#------------------------------------------------------------------------
#
# DescendTree
#
#------------------------------------------------------------------------
class DescendTree(Report):
    """
    Report class that generates a descendant tree.
    """

    def __init__(self, database, options_class):
        """
        Create DescendTree object that produces the report.
        
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
        Report.__init__(self, database, options_class)
        
        menu = options_class.menu
        self.display = menu.get_option_by_name('dispf').get_value()
        self.max_generations = menu.get_option_by_name('maxgen').get_value()
        self.force_fit = menu.get_option_by_name('singlep').get_value()
        self.incblank = menu.get_option_by_name('incblank').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        center_person = database.get_person_from_gramps_id(pid)
        if (center_person == None) :
            raise ReportError(_("Person %s is not in the Database") % pid )
        
        self.showspouse = menu.get_option_by_name('shows').get_value()
        
        name = name_displayer.display_formal(center_person)
        self.title = _("Descendant Chart for %s") % name

        self.map = {}
        self.text = {}

        self.box_width = 0
        self.box_height = 0
        self.lines = 0
        self.scale = 1
        self.box_gap = 0.2
        self.box_pad_pts = 0
        self.offset = 0
        self.page_label_x_offset = 0
        self.page_label_y_offset = 0
        self.usable_height = 0
        self.usable_width = 0
        self.generations_per_page = 0
        self.delta = 0
        
        self.genchart = GenChart(32)
        
        self.apply_filter(center_person.get_handle(), 0, 0)

        self.calc()
        
        if self.force_fit:
            self.scale_styles()

    def add_person(self, person_handle, col_x, row_y, spouse_level):
        """Add a new person into the x,y position
        also sets wether the person is:
        - a direct descendent or a spouse
        - the max length of the text/box, and number of lines"""
        self.genchart.set_sp(col_x, row_y, spouse_level)
        if person_handle is not None:
            self.genchart.set_xy(col_x, row_y, person_handle)
        else:
            #make sure that a box prints
            self.genchart.set_xy(col_x, row_y, ".")
            #make a blank box.
            self.text[(col_x, row_y)] = [""]
            return
        
        style_sheet = self.doc.get_style_sheet()
        pstyle = style_sheet.get_paragraph_style("DC2-Normal")
        font = pstyle.get_font()

        em = self.doc.string_width(font, "m")

        subst = SubstKeywords(self.database, person_handle)
        self.text[(col_x, row_y)] = subst.replace_and_clean(self.display)
        for line in self.text[(col_x, row_y)]:
            this_box_width = self.doc.string_width(font, line) + (2 * em)
            self.box_width = max(self.box_width, this_box_width)

        self.lines = max(self.lines, len(self.text[(col_x, row_y)]))    

    def apply_filter(self, person_handle, col_x, row_y):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""

        if (col_x / 2) >= self.max_generations:
            return 0

        person = self.database.get_person_from_handle(person_handle)
        self.add_person(person_handle, col_x, row_y, _PERSON_DIRECT)

        working_col = 1
        next_col = 0
        for family_handle in person.get_family_handle_list():
            
            family = self.database.get_family_from_handle(family_handle)

            if self.showspouse:
                spouse_handle = ReportUtils.find_spouse(person, family)
                self.add_person(spouse_handle, col_x, row_y + working_col,
                                _PERSON_SPOUSE)
                working_col += 1

            for child_ref in family.get_child_ref_list():
                next_col += self.apply_filter(child_ref.ref, col_x + 2, 
                                              row_y + next_col)

            working_col = next_col = max(working_col, next_col)

        return working_col


    def add_lines(self):
        """
        Add the lines that connect the boxes in the chart.
        """
        (maxy, maxx) = self.genchart.dimensions()

        for y in range(0, maxy + 1):
            for x in range(0, maxx + 1):
                # skip columns reserved for rows - no data here
                if x % 2:
                    continue

                # if we have a direct child to the right of a person
                # check to see if the child is a descendant of the person
                if self.genchart.get_sp(x + 2, y) == _PERSON_DIRECT:
                    if self.genchart.get_sp(x, y) == _PERSON_DIRECT:
                        self.genchart.set_xy(x + 1, y , _LINE_HORIZONTAL)
                        continue
                    elif self.genchart.get_sp(x, y) == _PERSON_SPOUSE and \
                    self.genchart.get_sp(x, y - 1) != _PERSON_DIRECT:
                        self.genchart.set_xy(x + 1, y , _LINE_HORIZONTAL)
                        continue
                else:
                    continue

                self.genchart.set_xy(x + 1, y, _LINE_ANGLE)

                # look through the entries ABOVE this one. All direct people
                # in the next column are descendants until we hit the first
                #  direct person (marked with _LINE_HORIZONTAL)
                last = y - 1
                while last > 0:
                    if self.genchart.get_xy(x + 1, last) == 0:
                        self.genchart.set_xy(x + 1, last, _LINE_VERTICAL)
                    else:
                        break
                    last -= 1


    def write_report(self):
        """
        Write the report to the document.
        """
        (maxy, maxx) = self.genchart.dimensions()
        if maxx != 1:
            maxx = (maxx - 1) * 2
        else:
            #no descendants
            maxx = 1
        maxh = int((self.usable_height - 0.75) / (self.box_height * 1.25))

        if self.force_fit:
            self.print_page(0, maxx, 0, maxy, 0, 0)
        else:
            starty = 0
            coly = 0
            while starty < maxy:
                startx = 0
                colx = 0
                while startx < maxx:
                    stopx = min(maxx, startx + (self.generations_per_page * 2))
                    stopy = min(maxy, starty + maxh)
                    self.print_page(startx, stopx, starty, stopy, colx, coly)
                    colx += 1
                    startx += self.generations_per_page * 2
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
            self.offset = ReportUtils.pt2cm(1.25 * tfont.get_size())
            
            gstyle = style_sheet.get_draw_style("DC2-box")
            shadow_height = gstyle.get_shadow_space()
        else:
            # Make space for the page number labels at the bottom.
            p = style_sheet.get_paragraph_style("DC2-Normal")
            font = p.get_font()
            lheight = ReportUtils.pt2cm(1.2 * font.get_size())
            lwidth = ReportUtils.pt2cm(1.1 * 
                                       self.doc.string_width(font, "(00,00)"))
            self.page_label_x_offset = self.doc.get_usable_width() - lwidth
            self.page_label_y_offset = self.doc.get_usable_height() - lheight

            self.offset = ReportUtils.pt2cm(1.25 * font.get_size())
            shadow_height = 0
        self.usable_height = self.doc.get_usable_height() \
                             - self.offset                \
                             - shadow_height
        self.usable_width = self.doc.get_usable_width() \
                            - ReportUtils.pt2cm(self.box_pad_pts)

        calc_width = ReportUtils.pt2cm(self.box_width + self.box_pad_pts) \
                     + self.box_gap
        self.box_width = ReportUtils.pt2cm(self.box_width)
        pstyle = style_sheet.get_paragraph_style("DC2-Normal")
        font = pstyle.get_font()
        self.box_height = self.lines*ReportUtils.pt2cm(1.25 * font.get_size())

        self.scale = 1
        
        if self.force_fit:
            (maxy, maxx) = self.genchart.dimensions()

            bw = (calc_width / (self.usable_width / (maxx + 1)))
            bh = ((self.box_height * 1.25) + self.box_gap) \
                 / (self.usable_height / maxy)

            self.scale = max(bw / 2, bh)
            self.box_width /= self.scale
            self.box_height /= self.scale
            self.box_pad_pts /= self.scale
            self.box_gap /= self.scale

        maxw = int(self.usable_width / calc_width) 

        self.generations_per_page = maxw
        
        self.delta = ReportUtils.pt2cm(self.box_pad_pts) \
                     + self.box_width                    \
                     + self.box_gap
        if not self.force_fit:
            calc_width = self.box_width + ReportUtils.pt2cm(self.box_pad_pts)
            remain = self.doc.get_usable_width() \
                     - (self.generations_per_page * calc_width)
            self.delta += remain / float(self.generations_per_page)

    def scale_styles(self):
        """
        Scale the styles for this report. This must be done in the constructor.
        """
        style_sheet = self.doc.get_style_sheet()

        box_style = style_sheet.get_draw_style("DC2-box")
        box_style.set_shadow(box_style.get_shadow(), 
                             box_style.get_shadow_space() / self.scale)
        box_style.set_line_width(box_style.get_line_width() / self.scale)
        style_sheet.add_draw_style("DC2-box", box_style)
        
        para_style = style_sheet.get_paragraph_style("DC2-Normal")
        font = para_style.get_font()
        font.set_size(font.get_size() / self.scale)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("DC2-Normal", para_style)
            
        self.doc.set_style_sheet(style_sheet)

    def print_page(self, startx, stopx, starty, stopy, colx, coly):
        if not self.incblank:
            blank = True
            for y in range(starty, stopy):
                for x in range(startx, stopx):
                    if self.genchart.get_xy(x, y) != 0:
                        blank = False
                        break
                if not blank: 
                    break
            if blank: 
                return

        self.doc.start_page()
        if self.title and self.force_fit:
            self.doc.center_text('DC2-title', self.title,
                                 self.doc.get_usable_width() / 2, 0)
        phys_y = 1
        bh = self.box_height * 1.25
        for y in range(starty, stopy):
            phys_x = 0
            for x in range(startx, stopx):
                value = self.genchart.get_xy(x, y)
                if isinstance(value, basestring):
                    text = '\n'.join(self.text[(x, y)])
                    xbegin = phys_x * self.delta
                    yend   = (phys_y * bh) + self.offset
                    self.doc.draw_box("DC2-box",
                                      text,
                                      xbegin,
                                      yend,
                                      self.box_width,
                                      self.box_height)
                elif value == _LINE_HORIZONTAL:
                    xbegin = phys_x * self.delta
                    ystart = ((phys_y * bh) + self.box_height / 2.0) \
                             + self.offset
                    xstart = xbegin + self.box_width
                    xstop  = (phys_x + 1) * self.delta
                    self.doc.draw_line('DC2-line', xstart, ystart, xstop, 
                                       ystart)
                elif value == _LINE_VERTICAL:
                    ystart = ((phys_y - 1) * bh)       \
                             + (self.box_height / 2.0) \
                             + self.offset
                    ystop  = (phys_y * bh)             \
                             + (self.box_height / 2.0) \
                             + self.offset
                    xlast  = (phys_x * self.delta) \
                             + self.box_width      \
                             + self.box_gap
                    self.doc.draw_line('DC2-line', xlast, ystart, xlast, ystop)
                elif value == _LINE_ANGLE:
                    ystart = ((phys_y - 1) * bh)       \
                             + (self.box_height / 2.0) \
                             + self.offset
                    ystop  = (phys_y * bh)             \
                             + (self.box_height / 2.0) \
                             + self.offset
                    xlast  = (phys_x * self.delta) \
                             + self.box_width      \
                             + self.box_gap
                    xnext  = (phys_x + 1) * self.delta
                    self.doc.draw_line('DC2-line', xlast, ystart, xlast, ystop)
                    self.doc.draw_line('DC2-line', xlast, ystop, xnext, ystop)
                
                if x % 2:
                    phys_x += 1
            phys_y += 1
                    
        if not self.force_fit:
            self.doc.draw_text('DC2-box',
                               '(%d,%d)' % (colx + 1, coly + 1),
                               self.page_label_x_offset,
                               self.page_label_y_offset)
        self.doc.end_page()
                    
#------------------------------------------------------------------------
#
# DescendTreeOptions
#
#------------------------------------------------------------------------
class DescendTreeOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the descendant report.
        """
        category_name = _("Tree Options")
        
        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the tree"))
        menu.add_option(category_name, "pid", pid)
        
        max_gen = NumberOption(_("Generations"), 10, 1, 50)
        max_gen.set_help(_("The number of generations to include in the tree"))
        menu.add_option(category_name, "maxgen", max_gen)
        
        disp = TextOption( _("Display Format"),
                           ["$n","%s $b" % _BORN,"%s $d" %_DIED] )
        disp.set_help(_("Display format for the outputbox."))
        menu.add_option(category_name, "dispf", disp)
        
        scale = BooleanOption(_('Sc_ale to fit on a single page'), True)
        scale.set_help(_("Whether to scale to fit on a single page."))
        menu.add_option(category_name, "singlep", scale)
        
        blank = BooleanOption(_('Include Blank Pages'), True)
        blank.set_help(_("Whether to include pages that are blank."))
        menu.add_option(category_name, "incblank", blank)
        
        shows = BooleanOption(_('Show Sp_ouses'), True)
        shows.set_help(_("Whether to show spouses in the tree."))
        menu.add_option(category_name, "shows", shows)

    def make_default_style(self, default_style):
        """Make the default output style for the Ancestor Tree."""
        ## Paragraph Styles:
        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        p_style = ParagraphStyle()
        p_style.set_font(font)
        p_style.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("DC2-Normal", p_style)

        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        p_style = ParagraphStyle()
        p_style.set_font(font)
        p_style.set_alignment(PARA_ALIGN_CENTER)
        p_style.set_description(_('The basic style used for the title display.'))
        default_style.add_paragraph_style("DC2-Title", p_style)
        
        ## Draw styles
        g_style = GraphicsStyle()
        g_style.set_paragraph_style("DC2-Normal")
        g_style.set_shadow(1, 0.2)
        g_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("DC2-box", g_style)

        g_style = GraphicsStyle()
        g_style.set_paragraph_style("DC2-Title")
        g_style.set_color((0, 0, 0))
        g_style.set_fill_color((255, 255, 255))
        g_style.set_line_width(0)
        default_style.add_draw_style("DC2-title", g_style)

        g_style = GraphicsStyle()
        default_style.add_draw_style("DC2-line", g_style)
