#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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
# gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     MenuOptions, NumberOption, EnumeratedListOption, \
     CATEGORY_DRAW, MODE_GUI, MODE_BKI, MODE_CLI
from SubstKeywords import SubstKeywords

#------------------------------------------------------------------------
#
# private constants
#
#------------------------------------------------------------------------
FULL_CIRCLE = 0
HALF_CIRCLE = 1
QUAR_CIRCLE = 2

BACKGROUND_WHITE = 0
BACKGROUND_GEN   = 1

RADIAL_UPRIGHT    = 0
RADIAL_ROUNDABOUT = 1

pt2cm = ReportUtils.pt2cm

#------------------------------------------------------------------------
#
# FanChart
#
#------------------------------------------------------------------------
class FanChart(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the FanChart object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        maxgen          - Maximum number of generations to include.
        circle          - Draw a full circle, half circle, or quarter circle.
        background      - Background color is generation dependent or white.
        radial          - Print radial texts roundabout or as upright as possible.
        """

        self.max_generations = options_class.handler.options_dict['maxgen']
        self.circle = options_class.handler.options_dict['circle']
        self.background = options_class.handler.options_dict['background']
        self.radial = options_class.handler.options_dict['radial']

        self.background_style = []
        self.text_style = []
        for i in range (0, self.max_generations):
            if self.background == BACKGROUND_WHITE:
                background_style_name = 'background_style_white'
            else:
                background_style_name = 'background_style' + '%d' % i
            self.background_style.append(background_style_name)
            text_style_name = 'text_style' + '%d' % i
            self.text_style.append(text_style_name)

        Report.__init__(self,database,person,options_class)

        self.height = 0
        self.lines = 0
        self.display = "%n"
        self.map = [None] * 2**self.max_generations
        self.text= {}
        self.box_width = 0

    def apply_filter(self,person_handle,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""
        
        if (not person_handle) or (index >= 2**self.max_generations):
            return
        self.map[index-1] = person_handle

        self.text[index-1] = []

        subst = SubstKeywords(self.database,person_handle)
        
        for line in self.display:
            self.text[index-1].append(subst.replace(line))

        style_sheet = self.doc.get_style_sheet()
        self.font = style_sheet.get_paragraph_style('text_style').get_font()
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

        self.doc.start_page()
        
        self.apply_filter(self.start_person.get_handle(),1)
        n = self.start_person.get_primary_name().get_regular_name()

        if self.circle == FULL_CIRCLE:
            max_angle = 360.0
            start_angle = 90
            max_circular = 5
            x = self.doc.get_usable_width() / 2.0
            y = self.doc.get_usable_height() / 2.0
            min_xy = min (x, y)

        elif self.circle == HALF_CIRCLE:
            max_angle = 180.0
            start_angle = 180
            max_circular = 3
            x = (self.doc.get_usable_width()/2.0)
            y = self.doc.get_usable_height()
            min_xy = min (x, y)

        else:  # quarter circle
            max_angle = 90.0
            start_angle = 270
            max_circular = 2
            x = 0
            y = self.doc.get_usable_height()
            min_xy = min (self.doc.get_usable_width(), y)

        if self.max_generations > max_circular:
            block_size = min_xy / (self.max_generations * 2 - max_circular)
        else:
            block_size = min_xy / self.max_generations
        self.doc.center_text ('t', _('%d Generation Fan Chart for %s') % (self.max_generations, n),
                             self.doc.get_usable_width() / 2, 0)

        for generation in range (0, min (max_circular, self.max_generations)):
            self.draw_circular (x, y, start_angle, max_angle, block_size, generation)
        for generation in range (max_circular, self.max_generations):
            self.draw_radial (x, y, start_angle, max_angle, block_size, generation)

        self.doc.end_page()


    def get_info(self,person_handle,generation):
        person = self.database.get_person_from_handle(person_handle)
        pn = person.get_primary_name()

        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.database.get_event_from_handle(birth_ref.ref)
            b = birth.get_date_object().get_year()
            if b == 0:
                b = ""
        else:
            b = ""

        death_ref = person.get_death_ref()
        if death_ref:
            death = self.database.get_event_from_handle(death_ref.ref)
            d = death.get_date_object().get_year()
            if d == 0:
                d = ""
        else:
            d = ""

        if b and d:
            val = "%s - %s" % (str(b),str(d))
        elif b:
            val = "* %s" % (str(b))
        elif d:
            val = "+ %s" % (str(d))
        else:
            val = ""

        if generation == 7:
            if (pn.get_first_name() != "") and (pn.get_surname() != ""):
                name = pn.get_first_name() + " " + pn.get_surname()
            else:
                name = pn.get_first_name() + pn.get_surname()

            if self.circle == FULL_CIRCLE:
                return [ name, val ]
            elif self.circle == HALF_CIRCLE:
                return [ name, val ]
            else:
                if (name != "") and (val != ""):
                    string = name + ", " + val
                else:
                    string = name + val
                return [string]
        elif generation == 6:
            if self.circle == FULL_CIRCLE:
                return [ pn.get_first_name(), pn.get_surname(), val ]
            elif self.circle == HALF_CIRCLE:
                return [ pn.get_first_name(), pn.get_surname(), val ]
            else:
                if (pn.get_first_name() != "") and (pn.get_surname() != ""):
                    name = pn.get_first_name() + " " + pn.get_surname()
                else:
                    name = pn.get_first_name() + pn.get_surname()
                return [ name, val ]
        else:
            return [ pn.get_first_name(), pn.get_surname(), val ]


    def draw_circular(self, x, y, start_angle, max_angle, size, generation):
        segments = 2**generation
        delta = max_angle / segments
        end_angle = start_angle
        text_angle = start_angle - 270 + (delta / 2.0)
        rad1 = size * generation
        rad2 = size * (generation + 1)
        background_style = self.background_style[generation]
        text_style = self.text_style[generation]

        for index in range(segments - 1, 2*segments - 1):
            start_angle = end_angle
            end_angle = start_angle + delta
            (xc,yc) = ReportUtils.draw_wedge(self.doc,background_style, x, y, rad2,
                                          start_angle, end_angle, rad1)
            if self.map[index]:
                if (generation == 0) and self.circle == FULL_CIRCLE:
                    yc = y
                self.doc.rotate_text(text_style,
                                     self.get_info(self.map[index],
                                                   generation),
                                     xc, yc, text_angle)
            text_angle += delta


    def draw_radial(self, x, y, start_angle, max_angle, size, generation):
        segments = 2**generation
        delta = max_angle / segments
        end_angle = start_angle
        text_angle = start_angle - delta / 2.0
        background_style = self.background_style[generation]
        text_style = self.text_style[generation]
        if self.circle == FULL_CIRCLE:
            rad1 = size * ((generation * 2) - 5)
            rad2 = size * ((generation * 2) - 3)
        elif self.circle == HALF_CIRCLE:
            rad1 = size * ((generation * 2) - 3)
            rad2 = size * ((generation * 2) - 1)
        else:  # quarter circle
            rad1 = size * ((generation * 2) - 2)
            rad2 = size * (generation * 2)
            
        for index in range(segments - 1, 2*segments - 1):
            start_angle = end_angle
            end_angle = start_angle + delta
            (xc,yc) = ReportUtils.draw_wedge(self.doc,background_style, x, y, rad2,
                                          start_angle, end_angle, rad1)
            text_angle += delta
            if self.map[index]:
                if self.radial == RADIAL_UPRIGHT and (start_angle >= 90) and (start_angle < 270):
                    self.doc.rotate_text(text_style,
                                         self.get_info(self.map[index],
                                                       generation),
                                         xc, yc, text_angle + 180)
                else:
                    self.doc.rotate_text(text_style,
                                         self.get_info(self.map[index],
                                                       generation),
                                         xc, yc, text_angle)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FanChartOptions(MenuOptions):

    def __init__(self,name,person_id=None):
        self.MAX_GENERATIONS = 8
        
        MenuOptions.__init__(self,name,person_id)
        
    def add_menu_options(self,menu):
        category_name = _("Report Options")
        
        max_gen = NumberOption(_("Generations"),5,1,self.MAX_GENERATIONS)
        max_gen.set_help(_("The number of generations to include in the report"))
        menu.add_option(category_name,"maxgen",max_gen)
        
        circle = EnumeratedListOption(_('Type of graph'),HALF_CIRCLE)
        circle.add_item(FULL_CIRCLE,_('full circle'))
        circle.add_item(HALF_CIRCLE,_('half circle'))
        circle.add_item(QUAR_CIRCLE,_('quarter circle'))
        circle.set_help( _("The form of the graph: full circle, half circle,"
                           " or quarter circle."))
        menu.add_option(category_name,"circle",circle)
        
        background = EnumeratedListOption(_('Background color'),BACKGROUND_GEN)
        background.add_item(BACKGROUND_WHITE,_('white'))
        background.add_item(BACKGROUND_GEN,_('generation dependent'))
        background.set_help(_("Background color is either white or generation"
                              " dependent"))
        menu.add_option(category_name,"background",background)
        
        radial = EnumeratedListOption( _('Orientation of radial texts'),
                                       RADIAL_UPRIGHT )
        radial.add_item(RADIAL_UPRIGHT,_('upright'))
        radial.add_item(RADIAL_ROUNDABOUT,_('roundabout'))
        radial.set_help(_("Print raidal texts upright or roundabout"))
        menu.add_option(category_name,"radial",radial)

    def make_default_style(self,default_style):
        """Make the default output style for the Fan Chart report."""
        BACKGROUND_COLORS = [
                             (255, 63,  0), 
                             (255,175, 15), 
                             (255,223, 87), 
                             (255,255,111),
                             (159,255,159), 
                             (111,215,255), 
                             ( 79,151,255), 
                             (231, 23,255)   
                            ]

        #Paragraph Styles
        f = BaseDoc.FontStyle()
        f.set_size(20)
        f.set_bold(1)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The style used for the title.'))
        default_style.add_paragraph_style("FC-Title",p)

        f = BaseDoc.FontStyle()
        f.set_size(9)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("text_style", p)
            
        # GraphicsStyles
        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style('FC-Title')
        g.set_line_width(0)
        default_style.add_draw_style("t",g)

        for i in range (0, self.MAX_GENERATIONS):
            g = BaseDoc.GraphicsStyle()
            g.set_fill_color(BACKGROUND_COLORS[i])
            g.set_paragraph_style('FC-Normal')
            background_style_name = 'background_style' + '%d' % i
            default_style.add_draw_style(background_style_name,g)

            g = BaseDoc.GraphicsStyle()
            g.set_fill_color(BACKGROUND_COLORS[i])
            g.set_paragraph_style('text_style')
            g.set_line_width(0)
            text_style_name = 'text_style' + '%d' % i
            default_style.add_draw_style(text_style_name,g)
            
        g = BaseDoc.GraphicsStyle()
        g.set_fill_color((255,255,255))
        g.set_paragraph_style('FC-Normal')
        default_style.add_draw_style('background_style_white',g)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
register_report(
    name = 'fan_chart',
    category = CATEGORY_DRAW,
    report_class = FanChart,
    options_class = FanChartOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Fan Chart"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces fan charts")
    )
