#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------
from xml.parsers.expat import ParserCreate
from random import Random
from gettext import gettext as _
import os

#-------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Config
import Utils

#-------------------------------------------------------------------------
#
# Tip Display class
#
#-------------------------------------------------------------------------
class TipOfDay:
    def __init__(self,uistate):
        xml = gtk.glade.XML(const.gladeFile, "tod", "gramps")
        top = xml.get_widget("tod")
        tip = xml.get_widget("tip")
        use = xml.get_widget('usetips')
        image = xml.get_widget('image')
        image.set_from_file(os.path.join(const.image_dir,'splash.jpg'))

        alt_title = xml.get_widget("title")
        tmsg = _("GRAMPS' Tip of the Day")
        Utils.set_titles(top, alt_title, tmsg, _("Tip of the Day"))
        
        tp = TipParser()
        tip_list = tp.get()
        use.set_active(Config.get_usetips())

        new_index = range(len(tip_list))
        Random().shuffle(new_index)

        top.set_transient_for(uistate.window)

        index = 0
        rval = 0
        while rval == 0:
            tip.set_text(_(tip_list[new_index[index]]))
            tip.set_use_markup(1)
            rval = top.run()
            if index >= len(tip_list)-1:
                index = 0
            else:
                index += 1
        
        Config.save_usetips(use.get_active())
        top.destroy()

#-------------------------------------------------------------------------
#
# Tip parser class
#
#-------------------------------------------------------------------------
class TipParser:
    """
    Interface to the document template file
    """
    def __init__(self):
        """
        Creates a template parser. The parser loads map of tempate names
        to the file containing the tempate.

        data - dictionary that holds the name to path mappings
        fpath - filename of the XML file
        """

        self.mylist = []
        xml_file = open(const.tipdata)
        self.tlist = []
        p = ParserCreate()
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.ParseFile(xml_file)
        xml_file.close()

    def get(self):
        return self.mylist
    
    def setDocumentLocator(self,locator):
        """Sets the XML document locator"""
        self.locator = locator

    def startElement(self,tag,attrs):
        """
        Loads the dictionary when an XML tag of 'template' is found. The format
        XML tag is <template title=\"name\" file=\"path\">
        """
        if tag == "tip":
            self.tlist = []
            # Skip all tips with xml:lang attribute, as they are
            # already in the translation catalog
            self.skip = attrs.has_key('xml:lang')
        elif tag != "tips":
            # let all the other tags through, except for the "tips" tag
            self.tlist.append("<%s>" % tag)

    def endElement(self,tag):
        if tag == "tip" and not self.skip:
            text = self.escape(''.join(self.tlist))
            self.mylist.append(' '.join(text.split()))
        elif tag != "tips":
            # let all the other tags through, except for the "tips" tag
            self.tlist.append("</%s>" % tag)

    def characters(self, data):
        self.tlist.append(data)

    def escape(self,text):
        """
        The tip's text will be interpreted as a markup, so we need to escape
        some special chars.
        """
        text = text.replace('&','&amp;');       # Must be first
        return text
