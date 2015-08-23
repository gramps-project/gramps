#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
# Copyright (C) 2009 Serge Noiraud
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

"""File and File format management for the openoffice reports
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from xml.sax.saxutils import escape
import os.path

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug.docbackend import DocBackend

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".odfbackend.py")

#------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
#------------------------------------------------------------------------

def _escape(string):
    """ a write to the file
    """"""
    change text in text that latex shows correctly
    special characters: & < and >
    """
    string = string.replace('&', '&amp;') # must be the first
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    return string

class OdfBackend(DocBackend):
    """
    Implementation for open document format docs
    """

    STYLETAG_TO_PROPERTY = {
    }

    # overwrite base class attributes, they become static var of CairoDoc
    SUPPORTED_MARKUP = [
            DocBackend.BOLD,
            DocBackend.ITALIC,
            DocBackend.UNDERLINE,
            DocBackend.FONTFACE,
            DocBackend.FONTSIZE,
            DocBackend.FONTCOLOR,
            DocBackend.HIGHLIGHT,
            DocBackend.SUPERSCRIPT,
            DocBackend.LINK,
            ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        :
            ("<text:span text:style-name=\"Tbold\">",
             "</text:span>"),
        DocBackend.ITALIC      :
            ("<text:span text:style-name=\"Titalic\">",
             "</text:span>"),
        DocBackend.UNDERLINE   :
            ("<text:span text:style-name=\"Tunderline\">",
             "</text:span>"),
        DocBackend.SUPERSCRIPT :
            ("<text:span text:style-name=\"GSuper\">",
             "</text:span>"),
    }

    ESCAPE_FUNC = lambda x: _escape

    def __init__(self, filename=None):
        """
        @param filename: path name of the file the backend works on
        """
        DocBackend.__init__(self, filename)

    def _create_xmltag(self, tagtype, value):
        """
        overwrites the method in DocBackend
        creates the pango xml tags needed for non bool style types
        """
        if tagtype not in self.SUPPORTED_MARKUP:
            return None
        # The ODF validator does not like spaces or hash in style-names. the
        # font name needs to have the spaces restored, we just hope that the
        # name did not have a hyphen in it originally. The colour is represented
        # without the leading hash, this can be replaced when used in the text-
        # property font colour
        if ( tagtype == DocBackend.FONTCOLOR ):
            return ('<text:span text:style-name=\"FontColor__%s__\">' %
                                value.replace("#", ""),
                    '</text:span>')
        elif ( tagtype == DocBackend.FONTFACE ):
            return ('<text:span text:style-name=\"FontFace__%s__\">' %
                                self.ESCAPE_FUNC()(value).replace(" ", "-"),
                    '</text:span>')
        elif ( tagtype == DocBackend.FONTSIZE ):
            return ('<text:span text:style-name=\"FontSize__%d__\">' % value,
                    '</text:span>')
        else: #elif ( tagtype == DocBackend.HIGHLIGHT ):
            return ('<text:span text:style-name=\"FontHighlight__%s__\">' %
                                value.replace("#", ""),
                    '</text:span>')

    def format_link(self, value):
        """
        Override of base method.
        """
        if value.startswith("gramps://"):
            return self.STYLETAG_MARKUP[DocBackend.UNDERLINE]
        else:
            return ('<text:a xlink:href="%s">' % self.ESCAPE_FUNC()(value),
                    '</text:a>')

