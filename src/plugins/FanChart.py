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
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_DRAW, MODE_GUI, MODE_BKI, MODE_CLI
from SubstKeywords import SubstKeywords
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
        full_circle     - != 0: draw a full circle; half_circle and quar_circle should be 0.
        half_circle     - != 0: draw a half circle; full_circle and quar_circle should be 0.
        quar_circle     - != 0: draw a quarter circle; full_circle and half_circle should be 0.
        backgr_white    - 0: Background color is generation dependent; 1: Background color is white.
        radial_upright  - 0: Print radial texts roundabout; 1: Print radial texts as upright as possible.
        """

        self.max_generations = options_class.handler.options_dict['maxgen']
        self.full_circle = options_class.handler.options_dict['full_circle']
        self.half_circle = options_class.handler.options_dict['half_circle']
        self.quar_circle = options_class.handler.options_dict['quar_circle']
        self.backgr_white = options_class.handler.options_dict['backgr_white']
        self.radial_upright = options_class.handler.options_dict['radial_upright']

        self.background_style = []
        self.text_style = []
        for i in range (0, self.max_generations):
            if self.backgr_white:
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

        if self.full_circle:
            max_angle = 360.0
            start_angle = 90
            max_circular = 5
            x = self.doc.get_usable_width() / 2.0
            y = self.doc.get_usable_height() / 2.0
            min_xy = min (x, y)

        elif self.half_circle:
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

            if self.full_circle:
                return [ name, val ]
            elif self.half_circle:
                return [ name, val ]
            else:
                if (name != "") and (val != ""):
                    string = name + ", " + val
                else:
                    string = name + val
                return [string]
        elif generation == 6:
            if self.full_circle:
                return [ pn.get_first_name(), pn.get_surname(), val ]
            elif self.half_circle:
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
                if (generation == 0) and self.full_circle:
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
        if self.full_circle:
            rad1 = size * ((generation * 2) - 5)
            rad2 = size * ((generation * 2) - 3)
        elif self.half_circle:
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
                if self.radial_upright and (start_angle >= 90) and (start_angle < 270):
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
class FanChartOptions(ReportOptions):

    """
    Defines options and provides handling interface for Fan Chart.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)
        
        self.MAX_GENERATIONS = 8

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'maxgen'    : 5,
            'full_circle' : 0,
            'half_circle' : 1,
            'quar_circle' : 0,
            'backgr_white' : 0,
            'backgr_generation' : 1,
            'radial_upright' : 1,
            'radial_roundabout' : 0,
        }
        self.options_help = {
            'maxgen'    : ("=num","Number of generations to print.",
                            [],
                            True),
            'full_circle': ("=0/1","The form of the diagram shall be a full circle.",
                            ["half or quarter circle","full circle"],
                            True),
            'half_circle': ("=0/1","The form of the diagram shall be a half circle.",
                            ["full or quarter circle","half circle"],
                            True),
            'quar_circle': ("=0/1","The form of the diagram shall be a quarter circle.",
                            ["full or half circle","quarter circle"],
                            True),
            'backgr_white': ("=0/1","Background color is white.",
                             ["generation dependent","white"],
                             True),
            'backgr_generation': ("=0/1","Background color is generation dependent.",
                                  ["white","generation dependent"],
                                  True),
            'radial_upright': ("=0/1","Print radial texts as upright as possible.",
                                ["roundabout","upright"],
                                True),
            'radial_roundabout': ("=0/1","Print radial texts roundabout.",
                                  ["upright","roundabout"],
                                  True),
        }

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the number of generations to print, ....
        """
        self.max_gen = gtk.SpinButton(gtk.Adjustment(5,2,self.MAX_GENERATIONS,1))
        self.max_gen.set_value(self.options_dict['maxgen'])
        self.max_gen.set_wrap(True)
        dialog.add_option(_('Generations'),self.max_gen)
        self.type_box = gtk.combo_box_new_text ()
        self.type_box.append_text (_('full circle'))
        self.type_box.append_text (_('half circle'))
        self.type_box.append_text (_('quarter circle'))
        self.type_box.set_active(self.options_dict['half_circle'] + 2 * self.options_dict['quar_circle'])
        dialog.add_option(_('Type of graph'),self.type_box)
        self.backgr_box = gtk.combo_box_new_text ()
        self.backgr_box.append_text (_('white'))
        self.backgr_box.append_text (_('generation dependent'))
        self.backgr_box.set_active(self.options_dict['backgr_generation'])
        dialog.add_option(_('Background color'),self.backgr_box)
        self.radial_box = gtk.combo_box_new_text ()
        self.radial_box.append_text (_('upright'))
        self.radial_box.append_text (_('roundabout'))
        self.radial_box.set_active(self.options_dict['radial_roundabout'])
        dialog.add_option(_('Orientation of radial texts'),self.radial_box)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['maxgen'] = int(self.max_gen.get_value_as_int())
        self.options_dict['full_circle'] = int(self.type_box.get_active() == 0)
        self.options_dict['half_circle'] = int(self.type_box.get_active() == 1)
        self.options_dict['quar_circle'] = int(self.type_box.get_active() == 2)
        self.options_dict['backgr_white'] = int(self.backgr_box.get_active() == 0)
        self.options_dict['backgr_generation'] = int(self.backgr_box.get_active() == 1)
        self.options_dict['radial_upright'] = int(self.radial_box.get_active() == 0)
        self.options_dict['radial_roundabout'] = int(self.radial_box.get_active() == 1)


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
