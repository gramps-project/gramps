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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import string
import os

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from TextDoc import *

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
        else:
            self.height = 0
            self.width = 0
            self.para_name = ""
            self.shadow = 0
            self.color = (255,255,255)

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

#------------------------------------------------------------------------
#
# DrawDoc
#
#------------------------------------------------------------------------
class DrawDoc:
    def __init__(self,styles,type,orientation=PAPER_PORTRAIT):
        self.orientation = orientation
        if orientation == PAPER_PORTRAIT:
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

    def draw_box(self,style,text,x,y):
	pass

    def write_at(self,style,text,x,y):
	pass

    def draw_line(self,style,x1,y1,x2,y2):
	pass

