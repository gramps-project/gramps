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

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import BaseDoc
import const
import Utils
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
paper_sizes = []

#-------------------------------------------------------------------------
#
# make_paper_menu
#
#-------------------------------------------------------------------------
def make_paper_menu(main_menu,default=""):

    index = 0
    myMenu = gtk.Menu()
    for paper in paper_sizes:
        name = paper.get_name()
        menuitem = gtk.MenuItem(name)
        menuitem.set_data("i",paper)
        menuitem.show()
        myMenu.append(menuitem)
        if default == name:
            myMenu.set_active(index)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# make_orientation_menu
#
#-------------------------------------------------------------------------
def make_orientation_menu(main_menu,value=0):

    myMenu = gtk.Menu()
    menuitem = gtk.MenuItem(_("Portrait"))
    menuitem.set_data("i",BaseDoc.PAPER_PORTRAIT)
    menuitem.show()
    if value == BaseDoc.PAPER_PORTRAIT:
        menuitem.select()
    myMenu.append(menuitem)

    menuitem = gtk.MenuItem(_("Landscape"))
    menuitem.set_data("i",BaseDoc.PAPER_LANDSCAPE)
    menuitem.show()
    if value == BaseDoc.PAPER_LANDSCAPE:
        menuitem.select()
    myMenu.append(menuitem)

    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# FilterParser
#
#-------------------------------------------------------------------------
class PageSizeParser(handler.ContentHandler):
    """Parses the XML file and builds the list of page sizes"""
    
    def __init__(self,paper_list):
        handler.ContentHandler.__init__(self)
        self.paper_list = paper_list
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "page":
            name = attrs['name']
            height = Utils.gfloat(attrs['height'])
            width = Utils.gfloat(attrs['width'])
            self.paper_list.append(BaseDoc.PaperStyle(name,height,width))

#-------------------------------------------------------------------------
#
# Parse XML file. If failed, used default
#
#-------------------------------------------------------------------------
try:
    parser = make_parser()
    parser.setContentHandler(PageSizeParser(paper_sizes))
    parser.parse(const.papersize)
    paper_sizes.append(BaseDoc.PaperStyle(_("Custom Size"),-1,-1))
except (IOError,OSError,SAXParseException):
    paper_sizes = [
        BaseDoc.PaperStyle("Letter",27.94,21.59),
        BaseDoc.PaperStyle("Legal",35.56,21.59),
        BaseDoc.PaperStyle("A0",118.9,84.1),
        BaseDoc.PaperStyle("A1",84.1,59.4),
        BaseDoc.PaperStyle("A2",59.4,42.0),
        BaseDoc.PaperStyle("A3",42.0,29.7),
        BaseDoc.PaperStyle("A4",29.7,21.0),
        BaseDoc.PaperStyle("A5",21.0,14.8),
        BaseDoc.PaperStyle("B0",141.4,100.0),
        BaseDoc.PaperStyle("B1",100.0,70.7),
        BaseDoc.PaperStyle("B2",70.7,50.0),
        BaseDoc.PaperStyle("B3",50.0,35.3),
        BaseDoc.PaperStyle("B4",35.3,25.0),
        BaseDoc.PaperStyle("B5",25.0,17.6),
        BaseDoc.PaperStyle("B6",17.6,12.5),
        BaseDoc.PaperStyle("B",43.18,27.94),
        BaseDoc.PaperStyle("C",56.1,43.18),
        BaseDoc.PaperStyle("D",86.36, 56.1),
        BaseDoc.PaperStyle("E",111.76,86.36),
        BaseDoc.PaperStyle(_("Custom Size"),-1,-1)
        ]
