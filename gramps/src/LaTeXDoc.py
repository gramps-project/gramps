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

from TextDoc import *
from latin_utf8 import latin_to_utf8

try:
    import PIL.Image
    no_pil = 0
except:
    no_pil = 1

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class LaTeXDoc(TextDoc):

    def open(self,filename):
        if filename[-4:] != ".tex":
            self.filename = filename + ".tex"
        else:
            self.filename = filename

        self.f = open(self.filename,"w")
        options = "12pt"

        if self.orientation == PAPER_LANDSCAPE:
            options = options + ",landscape"

        if self.paper.name == "A4":
            options = options + ",a4paper"
        elif self.paper.name == "A5":
            options = options + ",a5paper"
        elif self.paper.name == "B5":
            options = options + ",b4paper"
            
        self.f.write('\\documentclass[%s]{article}\n' % options)
        self.f.write('\\usepackage[T1]{fontenc}\n')
        self.f.write('\\usepackage[latin1]{inputenc}\n')
        self.f.write('\\begin{document}\n')
        self.f.write("\\title{}\n")
        self.f.write("\\author{}\n")
        self.in_list = 0
	self.in_table = 0
	self.cell_number = 1
	self.columns = 0

    def close(self):
        if self.in_list:
            self.f.write('\\end{description}\n')
        self.f.write('\\end{document}\n')
        self.f.close()

    def start_page(self,orientation=None):
        pass

    def end_page(self):
        self.f.write('\\newpage')

    def start_paragraph(self,style_name,leader=None):
        style = self.style_list[style_name]
        self.level = style.get_header_level()

        if leader == None and self.in_list:
            self.f.write('\\end{description}\n')
            self.in_list = 0

        if self.level == 1 :
            self.f.write('\\section*{')
        elif self.level == 2:
            self.f.write('\\subsection*{')
        elif self.level == 3:
            self.f.write('\\subsubsection*{')
        if leader != None and not self.in_list:
            self.f.write('\\begin{description}\n')
            self.in_list = 1
        if leader != None:
            self.f.write('\\item{%s} ' % leader)
    
    def end_paragraph(self):
        if self.level > 0:
            self.f.write('}\n')
        elif not self.in_list and not self.in_table:
            self.f.write('\n\\par\\noindent\n')
	elif self.in_table:
	    pass
        else:
            self.f.write('\n')

    def start_bold(self):
        self.f.write('\\bfseries ')
        pass

    def end_bold(self):
        self.f.write('\\mdseries ')
        pass

    def start_table(self,name,style_name):
        self.f.write('\n\\par\\noindent\n')
	self.f.write("\\medskip\n");
        self.f.write("\\begin{tabular}{");
	tbl = self.table_styles[style_name]
	self.columns = tbl.get_columns()
	for i in range(0, self.columns ):
	    self.f.write("l");
	self.f.write("}\n");
	self.in_table = 1
	self.cell_number = 0
        pass

    def end_table(self):
        # self.f.write("\\hline\n");
        self.f.write("\\end{tabular}\n");
        pass

    def start_row(self):
        # self.f.write("\\hline\n");
        self.cell_number = 0
        pass

    def end_row(self):
        for i in range( self.cell_number, self.columns ):
	   self.f.write(" & ");
        self.f.write("\\\\\n")
        pass

    def start_cell(self,style_name,span=1):
        if self.cell_number > 0:
	    self.f.write(" & ");
	self.cell_number = self.cell_number +1
        pass

    def end_cell(self):
        pass

    def add_photo(self,name,x,y):
        pass
    
    def horizontal_line(self):
        pass

    def write_text(self,text):
        self.f.write(text)

