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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: docbackend.py 12437 2009-04-13 02:11:49Z pez4brian $

"""File and File format management for latex docs
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------

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
from docbackend import DocBackend

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".latexbackend.py")

#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------
def latexescape(text):
    """
    change text in text that latex shows correctly
    special characters: \&     \$     \%     \#     \_    \{     \}
    """
    text = text.replace('&','\\&')
    text = text.replace('$','\\$')
    text = text.replace('%','\\%')
    text = text.replace('#','\\#')
    text = text.replace('_','\\_')
    text = text.replace('{','\\{')
    text = text.replace('}','\\}')
    return text

def latexescapeverbatim(text):
    """
    change text in text that latex shows correctly respecting whitespace
    special characters: \&     \$     \%     \#     \_    \{     \}
    Now also make sure space and newline is respected
    """
    text = text.replace('&', '\\&')
    text = text.replace('$', '\\$')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace(' ', '\\ ')
    text = text.replace('\n', '\\newline\n')
    #spaces at begin are normally ignored, make sure they are not.
    #due to above a space at begin is now \newline\n\ 
    text = text.replace('\\newline\n\\ ', '\\newline\n\\hspace*{0.1cm}\\ ')
    return text

#------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
#------------------------------------------------------------------------

class LateXBackend(DocBackend):
    """
    Implementation of docbackend for latex docs.
    """
    # overwrite base class attributes, they become static var of LaTeXDoc
    SUPPORTED_MARKUP = [
            DocBackend.BOLD,
            DocBackend.ITALIC,
            DocBackend.UNDERLINE,
            DocBackend.FONTSIZE,
            DocBackend.FONTFACE,
            DocBackend.SUPERSCRIPT ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("\\textbf{", "}"),
        DocBackend.ITALIC      : ("\\textit{", "}"),
        DocBackend.UNDERLINE   : ("\\underline{", "}"),
        DocBackend.SUPERSCRIPT : ("\\textsuperscript{", "}"),
    }
    
    ESCAPE_FUNC = lambda x: latexescape
    
    def setescape(self, preformatted=False):
        """
        Latex needs two different escape functions depending on the type. 
        This function allows to switch the escape function
        """
        if not preformatted:
            LateXBackend.ESCAPE_FUNC = lambda x: latexescape
        else:
            LateXBackend.ESCAPE_FUNC = lambda x: latexescapeverbatim

    def _create_xmltag(self, type, value):
        """
        overwrites the method in DocBackend.
        creates the latex tags needed for non bool style types we support:
            FONTSIZE : use different \large denomination based
                                        on size
                                     : very basic, in mono in the font face 
                                        then we use {\ttfamily }
        """
        if type not in self.SUPPORTED_MARKUP:
            return None
        elif type == DocBackend.FONTSIZE:
            #translate size in point to something LaTeX can work with
            if value >= 22:
                return ("{\\Huge ", "}")
            elif value >= 20:
                return ("{\\huge ", "}")
            elif value >= 18:
                return ("{\\LARGE ", "}")
            elif value >= 16:
                return ("{\\Large ", "}")
            elif value >= 14:
                return ("{\\large ", "}")
            elif value < 8:
                return ("{\\scriptsize ", "}")
            elif value < 10:
                return ("{\\footnotesize ", "}")
            elif value < 12:
                return ("{\\small ", "}")
            else:
                return ("", "")
        elif type == DocBackend.FONTFACE:
            if 'MONO' in value.upper():
                return ("{\\ttfamily ", "}")
            elif 'ROMAN' in value.upper():
                return ("{\\rmfamily ", "}")
        return None

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for this filetype
        """
        if self._filename[-4:] != ".tex":
            self._filename = self._filename + ".tex"
