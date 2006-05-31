#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

#-----------------------------------------------------------------------
#
# Python modules
#
#-----------------------------------------------------------------------

from gettext import gettext as _
import os

#-----------------------------------------------------------------------
#
# XML modules
#
#-----------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-----------------------------------------------------------------------
#
# GRAMPS modules
#
#-----------------------------------------------------------------------
import const

#-----------------------------------------------------------------------
#
# Parser for templates file
#
#-----------------------------------------------------------------------
class TemplateParser(handler.ContentHandler):
    """
    Interface to the document template file
    """
    def __init__(self,data,fpath):
        """
        Creates a template parser. The parser loads map of tempate names
        to the file containing the tempate.

        data - dictionary that holds the name to path mappings
        fpath - filename of the XML file
        """
        handler.ContentHandler.__init__(self)
        self.data = data
        self.path = fpath
    
    def setDocumentLocator(self,locator):
        """Sets the XML document locator"""
        self.locator = locator

    def startElement(self,tag,attrs):
        """
        Loads the dictionary when an XML tag of 'template' is found. The format
        XML tag is <template title=\"name\" file=\"path\">
        """
        
        if tag == "template":
            self.data[attrs['title']] = attrs['file']

#-----------------------------------------------------------------------
#
# Initialization
#
#-----------------------------------------------------------------------
_default_template = _("Default Template")
_user_template = _("User Defined Template")

_template_map = {
    _user_template : ""
    }
try:
    template_path = const.template_dir
    xmlfile = os.path.join(const.template_dir,"templates.xml")

    if os.path.isfile(xmlfile):
        parser = make_parser()
        parser.setContentHandler(TemplateParser(_template_map,template_path))
        parser.parse(xmlfile)
    
    template_path = os.path.join(const.home_dir,"templates")
    xmlfile = os.path.join(template_path,"templates.xml")
    if os.path.isfile(xmlfile):
        parser = make_parser()
        parser.setContentHandler(TemplateParser(_template_map,template_path))
        parser.parse(xmlfile)
        
except (IOError,OSError,SAXParseException):
    pass
