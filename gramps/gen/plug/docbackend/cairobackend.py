#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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

"""File and File format management for the different reports
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from xml.sax.saxutils import escape

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
from .docbackend import DocBackend

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".cairobackend.py")

#------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
#------------------------------------------------------------------------

class CairoBackend(DocBackend):
    """
    Implementation for cairo docs
    """

    STYLETAG_TO_PROPERTY = {
        DocBackend.FONTCOLOR : 'foreground',
        DocBackend.HIGHLIGHT : 'background',
        DocBackend.FONTFACE  : 'face',
        DocBackend.FONTSIZE  : 'size',
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
            DocBackend.SUPERSCRIPT ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("<b>", "</b>"),
        DocBackend.ITALIC      : ("<i>", "</i>"),
        DocBackend.UNDERLINE   : ("<u>", "</u>"),
        DocBackend.SUPERSCRIPT : ("<sup>", "</sup>"),
    }

    ESCAPE_FUNC = lambda x: escape

    def _create_xmltag(self, tagtype, value):
        """
        overwrites the method in DocBackend
        creates the pango xml tags needed for non bool style types
        """
        if tagtype not in self.SUPPORTED_MARKUP:
            return None
        if tagtype == DocBackend.FONTSIZE:
            #size is in thousandths of a point in pango
            value = str(1000 * value)

        return ('<span %s="%s">' % (self.STYLETAG_TO_PROPERTY[tagtype],
                                    self.ESCAPE_FUNC()(value)),
                '</span>')
