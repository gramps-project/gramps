#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
#
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

def pt2cm(pt):
    """
    Converts points to centimeters. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param pt: points
    @type pt: float or int
    @returns: equivalent units in centimeters
    @rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Converts centimeters to points. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param cm: centimeters
    @type cm: float or int
    @returns: equivalent units in points
    @rtype: float
    """
    return cm*182.88

def draw_pie_chart(doc, center_x, center_y, radius, data, start=0):
    """
    Draws a pie chart in the specified document. The data passed is plotted as
    a pie chart. The data should consist of the actual data. Percentages of
    each slice are determined by the routine.

    @param doc: Document to which the pie chart should be added
    @type doc: BaseDoc derived class
    @param center_x: x coordinate in centimeters where the center of the pie
       chart should be. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the center of the pie
       chart should be. 0 is the top edge of the document
    @param center_y: float
    @type radius: radius of the pie chart. The pie charts width and height will
       be twice this value.
    @type radius: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    @param start: starting point in degrees, where the default of 0 indicates
       a start point extending from the center to right in a horizontal line.
    @type start: float
    """

    total = 0.0
    for item in data:
        total += item[1]

    for item in data:
        incr = 360.0*(item[1]/total)
        doc.draw_wedge(item[0], center_x, center_y, radius, start, start + incr)
        start += incr

def draw_legend(doc, start_x, start_y, data):
    """
    Draws a legend for a graph in the specified document. The data passed is
    used to define the legend.

    @param doc: Document to which the legend chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand corner
        of the legend is placed. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the top of the legend
        should be. 0 is the top edge of the document
    @param center_y: float
    @param data: List of tuples containing the data to be used to create the
       legend. In order to be compatible with the graph plots, the first and
       third values of the tuple used. The format is (graphics_format, value,
       legend_description).
    @type data: list
    """
    for (format, size, legend) in data:
        gstyle = doc.get_draw_style(format)
        pstyle = gstyle.get_paragraph_style()
        size = pt2cm(doc.get_style(pstyle).get_font().get_size())
        
        doc.draw_bar(format, start_x, start_y, start_x + (2*size), start_y + size)
        doc.write_at(format, legend, start_x + (3*size), start_y - (size*0.25))
        start_y += size * 1.3
        
def draw_vertical_bar_graph(doc, format, start_x, start_y, height, width, data):
    doc.draw_line(format,start_x,start_y,start_x,start_y+height)
    doc.draw_line(format,start_x,start_y+height,start_x+width,start_y+height)

    largest = 0.0
    for item in data:
        largest = max(item[1],largest)

    scale = float(height)/float(largest)
    units = len(data)
    box_width = (float(width) / (units*3.0+1.0))*2

    bottom = float(start_y)+float(height)

    start = 0.5*box_width + start_x
    for index in range(units):
        print height, float(data[index][1]) * scale
        size = float(data[index][1]) * scale
        doc.draw_bar(data[index][0],start,bottom-size,start+box_width,bottom)
        start += box_width * 1.5

def age_of(person):
    pass

if __name__ == "__main__":
    import BaseDoc
    import OpenOfficeDoc

    sheet = BaseDoc.StyleSheet()
    paper = BaseDoc.PaperStyle("Letter",27.94,21.59)
    doc = OpenOfficeDoc.OpenOfficeDoc(sheet,paper,None)

    font = BaseDoc.FontStyle()
    font.set_size(10)

    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    sheet.add_style('Normal', para)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,255,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("green",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((255,0,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("red",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,0,255))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("blue",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,255,255))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("yellow",g)

    g = BaseDoc.GraphicsStyle()
    g.set_fill_color((0,0,0))
    g.set_paragraph_style('Normal')
    g.set_line_width(1)
    doc.add_draw_style("black",g)


    doc.open("foo.sxw")
    doc.init()
    chart_data = [
        ('red',250,'red label'),
        ('green',35,'green label'),
        ('blue', 158, 'blue label'),
        ('yellow', 100, 'yellow label'),
        ]
    
    draw_pie_chart(doc, 4, 4, 3, chart_data)
    draw_legend(doc, 7.5, 2, chart_data)

    draw_vertical_bar_graph(doc, "black", 2, 10, 8, 12, chart_data)
    
    doc.close()
