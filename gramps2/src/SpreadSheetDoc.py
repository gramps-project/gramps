#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

import BaseDoc

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SpreadSheetDoc:
    def __init__(self,type,orientation=BaseDoc.PAPER_PORTRAIT):
        self.orientation = orientation
        if orientation == BaseDoc.PAPER_PORTRAIT:
            self.width = type.get_width()
            self.height = type.get_height()
        else:
            self.width = type.get_height()
            self.height = type.get_width()
        self.tmargin = 2.54
        self.bmargin = 2.54
        self.lmargin = 2.54
        self.rmargin = 2.54
                
        self.font = BaseDoc.FontStyle()
        self.actfont = self.font
        self.style_list = {}
	self.table_styles = {}
        self.cell_styles = {}
        self.name = ""

    def get_usable_width(self):
        return self.width - (self.rmargin + self.lmargin)

    def get_usable_height(self):
        return self.height - (self.tmargin + self.bmargin)

    def creator(self,name):
        self.name = name

    def add_style(self,name,style):
        self.style_list[name] = BaseDoc.ParagraphStyle(style)

    def add_table_style(self,name,style):
        self.table_styles[name] = BaseDoc.TableStyle(style)

    def add_cell_style(self,name,style):
        self.cell_styles[name] = BaseDoc.TableCellStyle(style)

    def change_font(self,font):
        self.actfont = BaseDoc.FontStyle(font)

    def restore_font(self):
        self.actfont = self.font

    def get_default_font(self):
        return self.font

    def get_active_font(self):
        return self.actfont

    def open(self,filename):
        pass

    def close(self):
        pass

    def start_page(self,name,style_name):
        pass

    def end_page(self):
        pass

    def start_paragraph(self,style_name):
        pass

    def end_paragraph(self):
        pass

    def start_table(self,name,style_name):
        pass

    def end_table(self):
        pass

    def start_row(self):
        pass

    def end_row(self):
        pass

    def start_cell(self,style_name,span=1):
        pass

    def end_cell(self):
        pass

    def write_text(self,text):
        pass
