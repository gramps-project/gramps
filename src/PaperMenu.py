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
import TextDoc
import GrampsCfg
import const
import Utils
from intl import gettext as _

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
def make_paper_menu(main_menu):

    index = 0
    myMenu = gtk.Menu()
    for paper in paper_sizes:
        name = paper.get_name()
        menuitem = gtk.MenuItem(name)
        menuitem.set_data("i",paper)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.paper_preference:
            myMenu.set_active(index)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# make_orientation_menu
#
#-------------------------------------------------------------------------
def make_orientation_menu(main_menu):

    myMenu = gtk.Menu()
    menuitem = gtk.MenuItem(_("Portrait"))
    menuitem.set_data("i",TextDoc.PAPER_PORTRAIT)
    menuitem.show()
    myMenu.append(menuitem)

    menuitem = gtk.MenuItem(_("Landscape"))
    menuitem.set_data("i",TextDoc.PAPER_LANDSCAPE)
    menuitem.show()
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
            self.paper_list.append(TextDoc.PaperStyle(name,height,width))

#-------------------------------------------------------------------------
#
# Parse XML file. If failed, used default
#
#-------------------------------------------------------------------------
try:
    parser = make_parser()
    parser.setContentHandler(PageSizeParser(paper_sizes))
    parser.parse(const.papersize)
    paper_sizes.append(TextDoc.PaperStyle(_("Custom Size"),-1,-1))
except (IOError,OSError,SAXParseException):
    paper_sizes = [
        TextDoc.PaperStyle("Letter",27.94,21.59),
        TextDoc.PaperStyle("Legal",35.56,21.59),
        TextDoc.PaperStyle("A4",29.7,21.0),
        TextDoc.PaperStyle("A5",21.0,14.8),
        TextDoc.PaperStyle("B4",35.3,25.0),
        TextDoc.PaperStyle("B6",17.6,12.5),
        TextDoc.PaperStyle("C4",32.4,22.9),
        TextDoc.PaperStyle("C5",22.9,16.2),
        TextDoc.PaperStyle("C6",16.2,11.4),
        TextDoc.PaperStyle(_("Custom Size"),-1,-1)
        ]

