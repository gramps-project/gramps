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

"""LaTeX document generator"""

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
from TextDoc import *
import Plugins
import intl
_ = intl.gettext

#------------------------------------------------------------------------
#
# LaTeXDoc
#
#------------------------------------------------------------------------
class LaTeXDoc(TextDoc):
    """LaTeX document interface class. Derived from TextDoc"""
    
    def open(self,filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        
        if filename[-4:] != ".tex":
            self.filename = filename + ".tex"
        else:
            self.filename = filename
        self.f = open(self.filename,"w")

        # Font size control seems to be limited. For now, ignore
        # any style constraints, and use 12pt has the default
        
        options = "12pt"

        if self.orientation == PAPER_LANDSCAPE:
            options = options + ",landscape"

        # Paper selections seem to be limited as well. Not sure
        # what to do if the user picks something else. I believe
        # this defaults to 'letter'
        if self.paper.name == "A4":
            options = options + ",a4paper"
        elif self.paper.name == "A5":
            options = options + ",a5paper"
        elif self.paper.name == "B5":
            options = options + ",b4paper"

        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 character encodings.
        
        self.f.write('\\documentclass[%s]{article}\n' % options)
        self.f.write('\\usepackage[T1]{fontenc}\n')
        self.f.write('\\usepackage[latin1]{inputenc}\n')
        self.f.write('\\begin{document}\n')
        self.f.write("\\title{}\n")
        self.f.write("\\author{}\n")
        self.in_list = 0

    def close(self):
        """Clean up and close the document"""
        
        if self.in_list:
            self.f.write('\\end{description}\n')
        self.f.write('\\end{document}\n')
        self.f.close()

    def start_page(self,orientation=None):
        """Nothing needs to be done to start a page"""
        pass

    def end_page(self):
        """Issue a new page command"""
        self.f.write('\\newpage')

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - paragraphs seem to be limited in
        what we can do. The only thing I can see to do is to use
        the levels to provide the headers."""
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
        """End the current paragraph"""
        if self.level > 0:
            self.f.write('}\n')
        elif not self.in_list:
            self.f.write('\n\\par\\noindent\n')
        else:
            self.f.write('\n')

    def start_bold(self):
        """Bold face"""
        self.f.write('\\bfseries ')

    def end_bold(self):
        """End bold face"""
        self.f.write('\\mdseries ')

    def start_table(self,name,style_name):
        """Currently no table support"""
        pass

    def end_table(self):
        """Currently no table support"""
        pass

    def start_row(self):
        """Currently no table support"""
        pass

    def end_row(self):
        """Currently no table support"""
        pass

    def start_cell(self,style_name,span=1):
        """Currently no table support"""
        pass

    def end_cell(self):
        """Currently no table support"""
        pass

    def add_photo(self,name,pos,x,y):
        """Currently no table support"""
        pass
    
    def write_text(self,text):
        """Write the text to the file"""
        self.f.write(text)


#------------------------------------------------------------------------
#
# Register the document generator with the system
#
#------------------------------------------------------------------------
Plugins.register_text_doc(
    name=_("LaTeX"),
    classref=LaTeXDoc,
    table=0,
    paper=1,
    style=0
    )
