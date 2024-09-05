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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Handles the Tip of the Day dialog
"""

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
from xml.parsers.expat import ParserCreate, ExpatError
from random import Random
import os

# -------------------------------------------------------------------------
#
# GTK/GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import IMAGE_DIR, TIP_DATA
from gramps.gen.config import config
from .managedwindow import ManagedWindow
from .dialog import ErrorDialog


# -------------------------------------------------------------------------
#
# Tip Display class
#
# -------------------------------------------------------------------------
@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "glade/tipofday.glade"))
class TipOfDay(ManagedWindow, Gtk.Window):
    __gtype_name__ = "TipOfDay"

    title = Gtk.Template.Child()
    tip = Gtk.Template.Child()
    usetips = Gtk.Template.Child()
    image = Gtk.Template.Child()

    def __init__(self, uistate):
        ManagedWindow.__init__(self, uistate, [], self)
        Gtk.Window.__init__(self)

        self.set_window(self, self.title, _("Tip of the Day"), _("Tip of the Day"))
        self.setup_configs("interface.tipofday", 550, 350)

        self.usetips.set_active(config.get("behavior.use-tips"))
        self.image.set_from_file(os.path.join(IMAGE_DIR, "splash.jpg"))

        try:
            tparser = TipParser()
        except (IOError, ExpatError) as e:
            self.close()
            ErrorDialog(
                _("Failed to display tip of the day"),
                _("Unable to read the tips from external file.\n\n%s") % e,
                parent=uistate.window,
            )
            return
        self.tip_list = tparser.get()

        self.new_index = list(range(len(self.tip_list)))
        Random().shuffle(self.new_index)

        self.index = 0
        self.next_tip_cb()

        self.show()

    def escape(self, text):
        text = text.replace("&", "&amp;")
        # Must be first
        text = text.replace(" > ", " &gt; ")
        # Replace standalone > char
        return text

    @Gtk.Template.Callback()
    def next_tip_cb(self, dummy=None):
        tip_text = _(self.escape(self.tip_list[self.new_index[self.index]]))
        newtext = "\n\n".join(tip_text.split("<br/>"))
        self.tip.set_text(newtext)
        self.tip.set_use_markup(True)
        self.index = (self.index + 1) % len(self.tip_list)

    @Gtk.Template.Callback()
    def close_cb(self, dummy=None):
        config.set("behavior.use-tips", self.usetips.get_active())
        self.close()

    def build_menu_names(self, obj):
        return (_("Tip of the Day"), None)


# -------------------------------------------------------------------------
#
# Tip parser class
#
# -------------------------------------------------------------------------
class TipParser:
    """
    Interface to the document template file
    """

    def __init__(self):
        """
        Create a template parser. The parser loads map of tempate names
        to the file containing the tempate.

        data - dictionary that holds the name to path mappings
        fpath - filename of the XML file
        """

        self.mylist = []
        self.skip = False
        self.tlist = []
        parser = ParserCreate()
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characters
        with open(TIP_DATA, "rb") as xml_file:
            parser.ParseFile(xml_file)

    def get(self):
        """
        Return the list of tips
        """
        return self.mylist

    def setDocumentLocator(self, locator):
        """Set the XML document locator"""
        self.locator = locator

    def startElement(self, tag, attrs):
        """
        Loads the dictionary when an XML tag of 'template' is found. The format
        XML tag is <template title=\"name\" file=\"path\">
        """
        if tag == "tip":
            self.tlist = []
            # Skip all tips with xml:lang attribute, as they are
            # already in the translation catalog
            self.skip = "xml:lang" in attrs
        elif tag == "br":
            pass
        elif tag != "tips":
            # let all the other tags through, except for the "tips" tag
            # eg <b> my text</b>
            self.tlist.append("<%s>" % tag)

    def endElement(self, tag):
        if tag == "tip" and not self.skip:
            text = "".join(self.tlist)
            self.mylist.append(" ".join(text.split()))
        elif tag == "br":
            self.tlist.append("<br/>")
        elif tag != "tips":
            # let all the other tags through, except for the "tips" tag
            # eg <b> my text</b>
            self.tlist.append("</%s>" % tag)

    def characters(self, data):
        self.tlist.append(data)
