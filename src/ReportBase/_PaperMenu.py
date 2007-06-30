#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

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

class PaperComboBox(gtk.ComboBox):

    def __init__(self):
        gtk.ComboBox.__init__(self,model=None)

    def set(self,mapping,default):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.mapping = {}

        index = 0
        start_index = 0
        for key in mapping:
            self.mapping[key.get_name()]  = key
            self.store.append(row=[key.get_name()])
            if key.get_name() == default:
                start_index = index
            index += 1
            
        self.set_active(start_index)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        key = self.store[active][0]
        return (self.mapping[key],key)

class OrientationComboBox(gtk.ComboBox):

    def __init__(self):
        gtk.ComboBox.__init__(self,model=None)

    def set(self,default=0):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.mapping = {}

        self.store.append(row=[_('Portrait')])
        self.store.append(row=[_('Landscape')])
        if default == BaseDoc.PAPER_PORTRAIT:
            self.set_active(0)
        else:
            self.set_active(1)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        if active == 0:
            return BaseDoc.PAPER_PORTRAIT
        else:
            return BaseDoc.PAPER_LANDSCAPE

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
    myMenu.append(menuitem)

    menuitem = gtk.MenuItem(_("Landscape"))
    menuitem.set_data("i",BaseDoc.PAPER_LANDSCAPE)
    menuitem.show()
    myMenu.append(menuitem)

    if value == BaseDoc.PAPER_PORTRAIT:
        myMenu.set_active(0)
    elif value == BaseDoc.PAPER_LANDSCAPE:
        myMenu.set_active(1)

    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# PageSizeParser
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
    the_file = open(const.papersize)
    parser.parse(the_file)
    the_file.close()
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
