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

from math import cos,sin,pi

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import TextDoc

SOLID = 0
DASHED = 1

#------------------------------------------------------------------------
#
# GraphicsStyle
#
#------------------------------------------------------------------------
class GraphicsStyle:
    def __init__(self,obj=None):
        if obj:
            self.height = obj.height
            self.width = obj.width
            self.para_name = obj.para_name
            self.shadow = obj.shadow
	    self.color = obj.color
            self.fill_color = obj.fill_color
            self.lwidth = obj.lwidth
            self.lstyle = obj.lstyle
        else:
            self.height = 0
            self.width = 0
            self.para_name = ""
            self.shadow = 0
            self.lwidth = 0.5
            self.color = (0,0,0)
            self.fill_color = (255,255,255)
            self.lstyle = SOLID

    def set_line_width(self,val):
        self.lwidth = val

    def get_line_width(self):
        return self.lwidth

    def get_line_style(self):
        return self.lstyle

    def set_line_style(self,val):
        self.lstyle = val

    def set_height(self,val):
        self.height = val

    def set_width(self,val):
        self.width = val

    def set_paragraph_style(self,val):
        self.para_name = val

    def set_shadow(self,val):
        self.shadow = val

    def set_color(self,val):
        self.color = val

    def set_fill_color(self,val):
        self.fill_color = val

    def get_height(self):
        return self.height

    def get_width(self):
	return self.width

    def get_paragraph_style(self):
        return self.para_name

    def get_shadow(self):
        return self.shadow

    def get_color(self):
        return self.color

    def get_fill_color(self):
        return self.fill_color

#------------------------------------------------------------------------
#
# DrawDoc
#
#------------------------------------------------------------------------
class DrawDoc:
    def __init__(self,styles,type,orientation=TextDoc.PAPER_PORTRAIT):
        self.orientation = orientation
        if orientation == TextDoc.PAPER_PORTRAIT:
            self.width = type.get_width()
            self.height = type.get_height()
        else:
            self.width = type.get_height()
            self.height = type.get_width()
        self.tmargin = 2.54
        self.bmargin = 2.54
        self.lmargin = 2.54
        self.rmargin = 2.54
                
        self.style_list = styles.get_styles()
	self.draw_styles = {}
        self.name = ""

    def get_usable_width(self):
        return self.width - (self.rmargin + self.lmargin)

    def get_usable_height(self):
        return self.height - (self.tmargin + self.bmargin)

    def get_right_margin(self):
        return self.rmargin

    def get_left_margin(self):
        return self.lmargin

    def get_top_margin(self):
        return self.tmargin

    def get_bottom_margin(self):
        return self.bmargin

    def creator(self,name):
        self.name = name

    def add_draw_style(self,name,style):
        self.draw_styles[name] = GraphicsStyle(style)

    def open(self,filename):
        pass

    def close(self):
        pass

    def start_page(self,orientation=None):
        pass

    def end_page(self):
        pass

    def draw_arc(self,style,x1,y1,x2,y2,angle,extent):
        pass

    def draw_path(self,style,path):
        pass
    
    def draw_box(self,style,text,x,y):
	pass

    def write_at(self,style,text,x,y):
	pass

    def draw_bar(self,style,x1,y1,x2,y2):
        pass

    def draw_text(self,style,text,x1,y1):
        pass

    def center_text(self,style,text,x1,y1):
        pass

    def rotate_text(self,style,text,x,y,angle):
        pass
    
    def draw_line(self,style,x1,y1,x2,y2):
	pass

    def draw_wedge(self, style, centerx, centery, radius, start_angle,
                   end_angle, short_radius=0):

        while end_angle < start_angle:
            end_angle += 360

        p = []
        
        degreestoradians = pi/180.0
        radiansdelta = degreestoradians/2
        sangle = start_angle*degreestoradians
        eangle = end_angle*degreestoradians
        while eangle<sangle:
            eangle = eangle+2*pi
        angle = sangle

        if short_radius == 0:
            p.append((centerx,centery))
        else:
            origx = (centerx + cos(angle)*short_radius)
            origy = (centery + sin(angle)*short_radius)
            p.append((origx, origy))
            
        while angle<eangle:
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*radius
            p.append((x,y))
            angle = angle+radiansdelta
        x = centerx + cos(eangle)*radius
        y = centery + sin(eangle)*radius
        p.append((x,y))

        if short_radius:
            x = centerx + cos(eangle)*short_radius
            y = centery + sin(eangle)*short_radius
            p.append((x,y))

            angle = eangle
            while angle>=sangle:
                x = centerx + cos(angle)*short_radius
                y = centery + sin(angle)*short_radius
                p.append((x,y))
                angle = angle-radiansdelta
        self.draw_path(style,p)

        delta = (eangle - sangle)/2.0
        rad = short_radius + (radius-short_radius)/2.0

        return ( (centerx + cos(sangle+delta) * rad),
                 (centery + sin(sangle+delta) * rad))
    
    def start_path(self,style,x,y):
        pass

    def line_to(self,x,y):
        pass

    def arc_to(self,x,y,angle,extent):
        pass

    def end_path(self):
        pass
    
