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

"""Html and Html format management for the different reports
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
from gramps.plugins.lib.libhtml import Html, xml_lang
from gramps.gen.errors import ReportError

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------

def process_spaces(intext, format):
    """
    Function to process spaces in text lines for pre-formatted notes.
    line : text to process
    format : = 0 : Flowed, = 1 : Preformatted

    If the text is pre-formatted (format==1), then leading spaces  (after ignoring XML)
    are replaced by alternating non-breaking spaces and ordinary spaces.
    After the first non-space character, single spaces are left
    but multiple spaces are replaced by alternating NBSP and space
    If the text is flowed, the text is unchanged.

    Returns the processed text, and the number of significant
    (i.e. non-xml non-white-space) chars.
    """
    NORMAL=1
    SPACE=2
    NBSP=3
    XML=4
    SPACEHOLD=5

    sigcount = 0
    state = NORMAL
    outtext = ""
    if format == 1:
    # Pre-formatted
        for char in intext:
            if state == NORMAL:
                if char == " ":
                    if sigcount == 0:
                        state = NBSP
                        outtext += "&nbsp;"
                    else:
                        state = SPACEHOLD
                elif char == "<":
                    state = XML
                    outtext += char
                else:
                    sigcount += 1
                    outtext += char
            elif state == SPACE:
                if char == " ":
                    state = NBSP
                    outtext += "&nbsp;"
                elif char == "<":
                    state = XML
                    outtext += char
                else:
                    sigcount += 1
                    state = NORMAL
                    outtext += char
            elif state == NBSP:
                if char == " ":
                    state = SPACE
                elif char == "<":
                    state = XML
                else:
                    sigcount += 1
                    state = NORMAL
                outtext += char
            elif state == XML:
                if char == ">":
                    state = NORMAL
                outtext += char
            elif state == SPACEHOLD:
                if char == " ":
                    outtext += " &nbsp;"
                    state = NORMAL
                elif char == "<":
                    outtext += " "+char
                    state = XML
                else:
                    outtext += " "+char
                    sigcount += 1
                    state = NORMAL

    else:
    # format == 0 flowed
        for char in intext:
            if char == '<' and state == NORMAL:
                state = XML
                outtext += char
            elif char == '>' and state == XML:
                state = NORMAL
                outtext += char
            elif state == XML:
                outtext += char
            else:
                sigcount += 1
                outtext += char

    return [outtext, sigcount]

#------------------------------------------------------------------------
#
# Document Backend class for html pages
#
#------------------------------------------------------------------------

class HtmlBackend(DocBackend):
    """
    Implementation for html pages
    Contrary to other backends, we do not write to file but to a Html object
    instead, writing out the file on close.
    """

    STYLETAG_TO_PROPERTY = {
        DocBackend.FONTCOLOR : 'color:%s;',
        DocBackend.HIGHLIGHT : 'background-color:%s;',
        DocBackend.FONTFACE  : "font-family:'%s';",
        DocBackend.FONTSIZE  : 'font-size:%spx;',
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
        DocBackend.BOLD        : ("<strong>", "</strong>"),
        DocBackend.ITALIC      : ("<em>", "</em>"),
        DocBackend.UNDERLINE   : ('<span style="text-decoration:underline;">',
                                    "</span>"),
        DocBackend.SUPERSCRIPT : ("<sup>", "</sup>"),
    }

    ESCAPE_FUNC = lambda self: escape

    def __init__(self, filename=None):
        """
        @param filename: path name of the file the backend works on
        """
        DocBackend.__init__(self, filename)
        self.html_page = None
        self.html_header = None
        self.html_body = None
        self._subdir = None
        self.title = None
        self.build_link = None

    def _create_xmltag(self, tagtype, value):
        """
        overwrites the method in DocBackend
        creates the pango xml tags needed for non bool style types
        """
        if tagtype not in self.SUPPORTED_MARKUP:
            return None
        elif tagtype == DocBackend.LINK:
            return self.format_link(value)
        elif tagtype == DocBackend.FONTSIZE:
            #size is in points
            value = str(value)
        elif tagtype == DocBackend.FONTFACE:
            #fonts can have strange symbols in them, ' needs to be escaped
            value = value.replace("'", "\\'") if value else ""
        return ('<span style="%s">' % (self.STYLETAG_TO_PROPERTY[tagtype] %
                                       (value)),
                '</span>')

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for this filetype
        """
        fparts = os.path.basename(self._filename).split('.')
        if not len(fparts) >= 2 and not (fparts[-1] == 'html' or
                fparts[-1] == 'htm' or fparts[-1] == 'php'):
            self._filename = self._filename + ".htm"
        fparts = os.path.basename(self._filename).split('.')
        self._subdir = '.'.join(fparts[:-1])

    def set_title(self, title):
        """
        Set the title to use for the html page
        """
        self.title = title

    def open(self):
        """
        overwrite method, htmlbackend creates a html object that is written on
        close
        """
        try:
            DocBackend.open(self)
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") %
                                 self._filename, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") %
                                     self._filename)
        if not os.path.isdir(self.datadirfull()):
            try:
                os.mkdir(self.datadirfull())
            except IOError as msg:
                errmsg = "%s\n%s" % (_("Could not create %s") %
                                     self.datadirfull(), msg)
                raise ReportError(errmsg)
            except:
                raise ReportError(_("Could not create %s") %
                                         self.datadirfull())
        self.html_page, self.html_header, self.html_body = Html.page(
                        lang=xml_lang(), title=self.title)

    def __write(self, string):
        """ a write to the file
        """
        DocBackend.write(self, string + '\n')

    def write(self, obj):
        """ write to the html page. One can pass a html object, or a string
        """
        self.html_body += obj

    def close(self):
        """
        write out the html to the page
        """
        self.html_page.write(self.__write, indent='  ')
        DocBackend.close(self)

    def datadir(self):
        """
        the directory where to save extra files
        """
        return self._subdir

    def datadirfull(self):
        """
        full path of the datadir directory
        """
        return os.path.join(os.path.dirname(self.getf()), self.datadir())

    def format_link(self, value):
        """
        Override of base method.
        """
        if value.startswith("gramps://"):
            if self.build_link:
                obj_class, prop, handle = value[9:].split("/", 3)
                if prop in ["handle", "gramps_id"]:
                    value = self.build_link(prop, handle, obj_class)
                    if not value:
                        return self.STYLETAG_MARKUP[DocBackend.UNDERLINE]
                else:
                    return self.STYLETAG_MARKUP[DocBackend.UNDERLINE]
            else:
                return self.STYLETAG_MARKUP[DocBackend.UNDERLINE]
        return ('<a href="%s">' % self.ESCAPE_FUNC()(value),
                '</a>')

