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
# Load the base TextDoc class
#
#------------------------------------------------------------------------
from TextDoc import *

#------------------------------------------------------------------------
#
# Attempt to load the Python Imaging Library for the handling of photos.
#
#------------------------------------------------------------------------
try:
    import PIL.Image
    no_pil = 0
except:
    no_pil = 1

#------------------------------------------------------------------------
#
# RTF uses a unit called "twips" for its measurements. According to the 
# RTF specification, 1 point is 20 twips. This routines converts 
# centimeters to twips
#
# 2.54 cm/inch 72pts/inch, 20twips/pt
#
#------------------------------------------------------------------------
def twips(cm):
    return int(((cm/2.54)*72)+0.5)*20

#------------------------------------------------------------------------
#
# Rich Text Format Document interface. The current inteface does not
# use style sheets. Instead it writes raw formatting.
#
#------------------------------------------------------------------------
class RTFDoc(TextDoc):

    #--------------------------------------------------------------------
    #
    # Opens the file, and writes the header. Builds the color and font
    # tables.  Fonts are chosen using the MS TrueType fonts, since it
    # is assumed that if you are generating RTF, you are probably 
    # targeting Word.  This generator assumes a Western Europe character
    # set.
    #
    #--------------------------------------------------------------------
    def open(self,filename):
        if filename[-4:] != ".rtf":
            self.filename = filename + ".rtf"
        else:
            self.filename = filename

        self.f = open(self.filename,"w")
        self.f.write('{\\rtf1\\ansi\\ansicpg1252\\deff0\n')
        self.f.write('{\\fonttbl\n')
        self.f.write('{\\f0\\froman\\fcharset0\\fprq0 Times New Roman;}\n')
        self.f.write('{\\f1\\fswiss\\fcharset0\\fprq0 Arial;}}\n')
        self.f.write('{\colortbl\n')
        self.color_map = {}
        index = 1
        self.color_map[(0,0,0)] = 0
        self.f.write('\\red0\\green0\\blue0;')
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            fgcolor = style.get_font().get_color()
            bgcolor = style.get_background_color()
            if not self.color_map.has_key(fgcolor):
                self.color_map[fgcolor] = index
                self.f.write('\\red%d\\green%d\\blue%d;' % fgcolor)
                index = index + 1
            if not self.color_map.has_key(bgcolor):
                self.f.write('\\red%d\\green%d\\blue%d;' % bgcolor)
                self.color_map[bgcolor] = index
                index = index + 1
        self.f.write('}\n')
        self.f.write('\\kerning0\\cf0\\viewkind1')
        self.f.write('\\paperw%d' % twips(self.width))
        self.f.write('\\paperh%d' % twips(self.height))
        self.f.write('\\margl%d' % twips(self.lmargin))
        self.f.write('\\margr%d' % twips(self.rmargin))
        self.f.write('\\margt%d' % twips(self.tmargin))
        self.f.write('\\margb%d' % twips(self.bmargin))
        self.f.write('\\widowctl\n')
	self.in_table = 0
	self.text = ""

    #--------------------------------------------------------------------
    #
    # Write the closing brace, and close the file.
    #
    #--------------------------------------------------------------------
    def close(self):
        self.f.write('}\n')
        self.f.close()

    #--------------------------------------------------------------------
    #
    # Force a section page break
    #
    #--------------------------------------------------------------------
    def end_page(self):
        self.f.write('\\sbkpage\n')

    #--------------------------------------------------------------------
    #
    # Starts a paragraph. Instead of using a style sheet, generate the
    # the style for each paragraph on the fly. Not the ideal, but it 
    # does work.
    #
    #--------------------------------------------------------------------
    def start_paragraph(self,style_name,leader=None):
        self.opened = 0
        p = self.style_list[style_name]

	# build font information

        f = p.get_font()
        size = f.get_size()*2
        bgindex = self.color_map[p.get_background_color()]
        fgindex = self.color_map[f.get_color()]
        if f.get_type_face() == FONT_SERIF:
            self.font_type = '\\f0\\fs%d\\cf%d\\cb%d' % (size,fgindex,bgindex)
        else:
            self.font_type = '\\f1\\fs%d\\cf%d\\cb%d' % (size,fgindex,bgindex)
        if f.get_bold():
            self.font_type = self.font_type + "\\b"
        if f.get_underline():
            self.font_type = self.font_type + "\\ul"
        if f.get_italic():
            self.font_type = self.font_type + "\\i"

	# build paragraph information

	if not self.in_table:
            self.f.write('\\pard')
        if p.get_alignment() == PARA_ALIGN_RIGHT:
            self.f.write('\\qr')
        elif p.get_alignment() == PARA_ALIGN_CENTER:
            self.f.write('\\qc')
        self.f.write('\\ri%d' % twips(p.get_right_margin()))
        self.f.write('\\li%d' % twips(p.get_left_margin()))
        self.f.write('\\fi%d' % twips(p.get_first_indent()))
        if p.get_alignment() == PARA_ALIGN_JUSTIFY:
            self.f.write('\\qj')
        if p.get_padding():
            self.f.write('\\sa%d' % twips(p.get_padding()/2.0))
        if p.get_top_border():
            self.f.write('\\brdrt\\brdrs')
        if p.get_bottom_border():
            self.f.write('\\brdrb\\brdrs')
        if p.get_left_border():
            self.f.write('\\brdrl\\brdrs')
        if p.get_right_border():
            self.f.write('\\brdrr\\brdrs')
        if p.get_first_indent():
            self.f.write('\\fi%d' % twips(p.get_first_indent()))
        if p.get_left_margin():
            self.f.write('\\li%d' % twips(p.get_left_margin()))
        if p.get_right_margin():
            self.f.write('\\ri%d' % twips(p.get_right_margin()))

        if leader:
            self.opened = 1
            self.f.write('\\tx%d' % twips(p.get_left_margin()))
            self.f.write('{%s ' % self.font_type)
            self.write_text(leader)
            self.f.write('\\tab}')
            self.opened = 0
    
    #--------------------------------------------------------------------
    #
    # Ends a paragraph. Care has to be taken to make sure that the 
    # braces are closed properly. The self.opened flag is used to indicate
    # if braces are currently open. If the last write was the end of 
    # a bold-faced phrase, braces may already be closed.
    #
    #--------------------------------------------------------------------
    def end_paragraph(self):
	if not self.in_table:
            self.f.write(self.text)
            if self.opened:
                self.f.write('}')
                self.text = ""
                self.opened = 0
            self.f.write('\n\\par')
        else:
            if self.text == "":
                self.write_text(" ")
            self.text = self.text + '}'

    #--------------------------------------------------------------------
    #
    # Starts boldfaced text, enclosed the braces
    #
    #--------------------------------------------------------------------
    def start_bold(self):
        if self.opened:
            self.f.write('}')
        self.f.write('{%s\\b ' % self.font_type)
        self.opened = 1

    #--------------------------------------------------------------------
    #
    # Ends boldfaced text, closing the braces
    #
    #--------------------------------------------------------------------
    def end_bold(self):
        self.opened = 0
        self.f.write('}')

    #--------------------------------------------------------------------
    #
    # Start a table. Grab the table style, and store it. Keep a flag to
    # indicate that we are in a table. This helps us deal with paragraphs
    # internal to a table. RTF does not require anything to start a 
    # table, since a table is treated as a bunch of rows.
    #
    #--------------------------------------------------------------------
    def start_table(self,name,style_name):
	self.in_table = 1
	self.tbl_style = self.table_styles[style_name]

    #--------------------------------------------------------------------
    #
    # End a table. Turn off the table flag
    #
    #--------------------------------------------------------------------
    def end_table(self):
	self.in_table = 0

    #--------------------------------------------------------------------
    #
    # Start a row. RTF uses the \trowd to start a row. RTF also specifies
    # all the cell data after it has specified the cell definitions for
    # the row. Therefore it is necessary to keep a list of cell contents
    # that is to be written after all the cells are defined.
    #
    #--------------------------------------------------------------------
    def start_row(self):
        self.contents = []
	self.cell = 0
	self.prev = 0
	self.cell_percent = 0.0
	self.f.write('\\trowd\n')

    #--------------------------------------------------------------------
    #
    # End a row. Write the cell contents, separated by the \cell marker,
    # then terminate the row
    #
    #--------------------------------------------------------------------
    def end_row(self):
	self.f.write('{')
	for line in self.contents:
	    self.f.write(line)
            self.f.write('\\cell ')
	self.f.write('}\\pard\\intbl\\row\n')

    #--------------------------------------------------------------------
    #
    # Start a cell. Dump out the cell specifics, such as borders. Cell
    # widths are kind of interesting. RTF doesn't specify how wide a cell
    # is, but rather where it's right edge is in relationship to the 
    # left margin. This means that each cell is the cumlative of the 
    # previous cells plus its own width.
    #
    #--------------------------------------------------------------------
    def start_cell(self,style_name,span=1):
	s = self.cell_styles[style_name]
	self.remain = span -1
	if s.get_top_border():
	    self.f.write('\\clbrdrt\\brdrs\\brdrw10\n')
	if s.get_bottom_border():
	    self.f.write('\\clbrdrb\\brdrs\\brdrw10\n')
	if s.get_left_border():
	    self.f.write('\\clbrdrl\\brdrs\\brdrw10\n')
	if s.get_right_border():
	    self.f.write('\\clbrdrr\\brdrs\\brdrw10\n')
	table_width = float(self.get_usable_width())
	for cell in range(self.cell,self.cell+span):
	    self.cell_percent = self.cell_percent + float(self.tbl_style.get_column_width(cell))
	cell_width = twips((table_width * self.cell_percent)/100.0)
	self.f.write('\\cellx%d\\pard\intbl\n' % cell_width)
	self.cell = self.cell+1

    #--------------------------------------------------------------------
    #
    # End a cell. Save the current text in the content lists, since data
    # must be saved until all cells are defined.
    #
    #--------------------------------------------------------------------
    def end_cell(self):
        self.contents.append(self.text)
        self.text = ""

    #--------------------------------------------------------------------
    #
    # Add a photo. Embed the photo in the document. Use the Python 
    # imaging library to load and scale the photo. The image is converted
    # to JPEG, since it is smaller, and supported by RTF. The data is
    # dumped as a string of HEX numbers.
    #
    # If the PIL library is not loaded, ignore the request to load the 
    # photo.
    #
    #--------------------------------------------------------------------
    def add_photo(self,name,x,y):
	if no_pil:
	    return

	im = PIL.Image.open(name)
        nx,ny = im.size
        buf = im.tostring("jpeg","RGB")

        scale = float(ny)/float(nx)
        if scale > 1:
            scale = 1.0/scale
        act_width = twips(x * scale)
        act_height = twips(y * scale)
        im.thumbnail((int(act_width*40),int(act_height*40)))

	self.f.write('{\*\shppict{\\pict\\jpegblip\\picwgoal%d\\pichgoal%d\n' % (x,y))
	index = 1
	for i in buf:
	    self.f.write('%02x' % ord(i))
	    if index%32==0:
	        self.f.write('\n')
	    index = index+1
	self.f.write('}}\\par\n')
    
    #--------------------------------------------------------------------
    #
    # Writes text. If braces are not currently open, open them. Loop 
    # character by character (terribly inefficient, but it works). If a
    # character is 8 bit (>127), convert it to a hex representation in 
    # the form of \`XX. Make sure to escape braces.
    #
    #--------------------------------------------------------------------
    def write_text(self,text):
        if self.opened == 0:
            self.opened = 1
            self.text = self.text + '{%s ' % self.font_type
        for i in text:
            if ord(i) > 127:
                self.text = self.text + '\\\'%2x' % ord(i)
            elif i == '{' or i == '}' :
                self.text = self.text + '\\%s' % i
            else:
                self.text = self.text + i


if __name__ == "__main__":

    paper = PaperStyle("Letter",27.94,21.59)

    styles = StyleSheet()
    foo = FontStyle()
    foo.set_type_face(FONT_SANS_SERIF)
    foo.set_color((255,0,0))
    foo.set_size(24)
    foo.set_underline(1)
    foo.set_bold(1)
    foo.set_italic(1)

    para = ParagraphStyle()
    para.set_alignment(PARA_ALIGN_RIGHT)
    para.set_font(foo)
    styles.add_style("Title",para)

    foo = FontStyle()
    foo.set_type_face(FONT_SERIF)
    foo.set_size(12)

    para = ParagraphStyle()
    para.set_font(foo)
    styles.add_style("Normal",para)

    foo = FontStyle()
    foo.set_type_face(FONT_SERIF)
    foo.set_size(12)

    para = ParagraphStyle()
    para.set_font(foo)
    para.set_top_border(1)
    para.set_left_border(1)
    para.set_right_border(1)
    para.set_bottom_border(1)
    styles.add_style("Box",para)

    doc = RTFDoc(styles,paper,PAPER_PORTRAIT)

    cell = TableCellStyle()
    cell.set_padding(0.2)
    cell.set_top_border(1)
    cell.set_bottom_border(1)
    cell.set_right_border(1)
    cell.set_left_border(1)
    doc.add_cell_style('ParentHead',cell)

    cell = TableCellStyle()
    cell.set_padding(0.1)
    cell.set_bottom_border(1)
    cell.set_left_border(1)
    doc.add_cell_style('TextContents',cell)

    cell = TableCellStyle()
    cell.set_padding(0.1)
    cell.set_bottom_border(0)
    cell.set_left_border(1)
    cell.set_padding(0.1)
    doc.add_cell_style('TextChild1',cell)

    cell = TableCellStyle()
    cell.set_padding(0.1)
    cell.set_bottom_border(1)
    cell.set_left_border(1)
    cell.set_padding(0.1)
    doc.add_cell_style('TextChild2',cell)

    cell = TableCellStyle()
    cell.set_padding(0.1)
    cell.set_bottom_border(1)
    cell.set_right_border(1)
    cell.set_left_border(1)
    doc.add_cell_style('TextContentsEnd',cell)

    cell = TableCellStyle()
    cell.set_padding(0.2)
    cell.set_bottom_border(1)
    cell.set_right_border(1)
    cell.set_left_border(1)
    doc.add_cell_style('ChildName',cell)

    table = TableStyle()
    table.set_width(100)
    table.set_columns(3)
    table.set_column_width(0,20)
    table.set_column_width(1,40)
    table.set_column_width(2,40)
    doc.add_table_style('ParentTable',table)

    table = TableStyle()
    table.set_width(100)
    table.set_columns(4)
    table.set_column_width(0,5)
    table.set_column_width(1,15)
    table.set_column_width(2,40)
    table.set_column_width(3,40)
    doc.add_table_style('ChildTable',table)

    doc.open("test")

    doc.start_paragraph("Title")
    doc.write_text("My Title")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.write_text("Hello there. This is fun")
    doc.end_paragraph()

    doc.start_paragraph("Box")
    doc.write_text("This is my box")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.add_photo("foo.png",200,200)
    doc.end_paragraph()

    doc.start_table(id,'ParentTable')
    doc.start_row()
    doc.start_cell('ParentHead',3)
    doc.start_paragraph('Normal')
    doc.write_text('Banana : Smith ')
    doc.end_paragraph()
    doc.end_cell()
    doc.end_row()

    doc.start_row()
    doc.start_cell("TextContents")
    doc.start_paragraph('Normal')
    doc.write_text("some event")
    doc.end_paragraph()
    doc.end_cell()
    doc.start_cell("TextContents")
    doc.start_paragraph('Normal')
    doc.write_text("someday")
    doc.end_paragraph()
    doc.end_cell()
    doc.start_cell("TextContentsEnd")
    doc.start_paragraph('Normal')
    doc.write_text("somewhere")
    doc.end_paragraph()
    doc.end_cell()
    doc.end_row()

    doc.end_table()

    doc.close()
