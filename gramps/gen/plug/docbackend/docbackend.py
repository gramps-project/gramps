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
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".docbackend.py")

#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------

def noescape(text):
    """
    Function that does not escape the text passed. Default for backends
    """
    return text

#-------------------------------------------------------------------------
#
# DocBackend exception
#
#-------------------------------------------------------------------------
class DocBackendError(Exception):
    """Error used to report docbackend errors."""
    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value

#------------------------------------------------------------------------
#
# Document Backend class
#
#------------------------------------------------------------------------

class DocBackend:
    """
    Base class for text document backends.
    The DocBackend manages a file to which it writes. It further knowns
    enough of the file format to be able to translate between the BaseDoc API
    and the file format.
    Specifically for text reports a translation of styled notes to the file
    format usage is done.
    """
    BOLD = 0
    ITALIC = 1
    UNDERLINE = 2
    FONTFACE = 3
    FONTSIZE = 4
    FONTCOLOR = 5
    HIGHLIGHT = 6
    SUPERSCRIPT = 7
    LINK = 8

    SUPPORTED_MARKUP = []

    ESCAPE_FUNC = lambda: noescape
    #Map between styletypes and internally used values. This map is needed
    # to make TextDoc officially independant of gen.lib.styledtexttag
    STYLETYPE_MAP = {
        }
    CLASSMAP = None

    #STYLETAGTABLE to store markup for write_markup associated with style tags
    STYLETAG_MARKUP = {
        BOLD        : ("", ""),
        ITALIC      : ("", ""),
        UNDERLINE   : ("", ""),
        SUPERSCRIPT : ("", ""),
        LINK        : ("", ""),
        }

    def __init__(self, filename=None):
        """
        :param filename: path name of the file the backend works on
        """
        self.__file = None
        self._filename = filename

    def getf(self):
        """
        Obtain the filename on which backend writes
        """
        return self._filename

    def setf(self, value):
        """
        Set the filename on which the backend writes, changing the value
        passed on initialization.
        Can only be done if the previous filename is not open.
        """
        if self.__file is not None:
            raise ValueError(_('Close file first'))
        self._filename = value

    filename = property(getf, setf, None, "The filename the backend works on")

    def open(self):
        """
        Opens the document.
        """
        if self.filename is None:
            raise DocBackendError(_('No filename given'))
        if self.__file is not None :
            raise DocBackendError(_('File %s already open, close it first.')
                                            % self.filename)
        self._checkfilename()
        try:
            self.__file = open(self.filename, "w", encoding="utf-8")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise DocBackendError(errmsg)
        except:
            raise DocBackendError(_("Could not create %s") % self.filename)

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for this filetype
        """
        pass

    def close(self):
        """
        Closes the file that is written on.
        """
        if self.__file is None:
            raise IOError('No file open')
        self.__file.close()
        self.__file = None

    def write(self, string):
        """
        Write a string to the file. There is no return value.
        Due to buffering, the string may not actually show up until the
        :meth:`close` method is called.
        """
        self.__file.write(string)

    def writelines(self, sequence):
        """
        Write a sequence of strings to the file. The sequence can be any
        iterable object producing strings, typically a list of strings.
        """
        self.__file.writelines(sequence)

    def escape(self, preformatted=False):
        """
        The escape func on text for this file format.

        :param preformatted: some formats can have different escape function
                             for normal text and preformatted text
        :type preformatted: bool
        """
        return self.ESCAPE_FUNC()


    def find_tag_by_stag(self, s_tag):
        """
        :param s_tag: object: assumed styledtexttag
        :param s_tagvalue: None/int/str: value associated with the tag

        A styled tag is type with a value. Every styled tag must be converted
        to the tags used in the corresponding markup for the backend,
        eg <b>text</b> for bold in html. These markups are stored in
        STYLETAG_MARKUP. They are tuples for begin and end tag. If a markup is
        not present yet, it is created, using the :meth:`_create_xmltag` method
        you can overwrite.
        """
        tagtype = s_tag.name

        if not self.STYLETYPE_MAP or \
        self.CLASSMAP != tagtype.__class__.__name__ :
            self.CLASSMAP = tagtype.__class__.__name__
            self.STYLETYPE_MAP[tagtype.BOLD]        = self.BOLD
            self.STYLETYPE_MAP[tagtype.ITALIC]      = self.ITALIC
            self.STYLETYPE_MAP[tagtype.UNDERLINE]   = self.UNDERLINE
            self.STYLETYPE_MAP[tagtype.FONTFACE]    = self.FONTFACE
            self.STYLETYPE_MAP[tagtype.FONTSIZE]    = self.FONTSIZE
            self.STYLETYPE_MAP[tagtype.FONTCOLOR]   = self.FONTCOLOR
            self.STYLETYPE_MAP[tagtype.HIGHLIGHT]   = self.HIGHLIGHT
            self.STYLETYPE_MAP[tagtype.SUPERSCRIPT] = self.SUPERSCRIPT
            self.STYLETYPE_MAP[tagtype.LINK]        = self.LINK

        if s_tag.name == tagtype.LINK:
            return self.format_link(s_tag.value)
        typeval = int(s_tag.name)
        s_tagvalue = s_tag.value
        tag_name = None
        if tagtype.STYLE_TYPE[typeval] == bool:
            return self.STYLETAG_MARKUP[self.STYLETYPE_MAP[typeval]]
        elif tagtype.STYLE_TYPE[typeval] == str:
            tag_name = "%d %s" % (typeval, s_tagvalue)
        elif tagtype.STYLE_TYPE[typeval] == int:
            tag_name = "%d %d" % (typeval, int(s_tagvalue))
        if not tag_name:
            return None

        tags = self.STYLETAG_MARKUP.get(tag_name)
        if tags is not None:
            return tags
        #no tag known yet, create the markup, add to lookup, and return
        tags = self._create_xmltag(self.STYLETYPE_MAP[typeval], s_tagvalue)
        self.STYLETAG_MARKUP[tag_name] = tags
        return tags

    def _create_xmltag(self, tagtype, value):
        """
        Create the xmltags for the backend.
        Overwrite this method to create functionality with a backend
        """
        if tagtype not in self.SUPPORTED_MARKUP:
            return None
        return ('', '')

    def add_markup_from_styled(self, text, s_tags, split='', escape=True):
        """
        Input is plain text, output is text with markup added according to the
        s_tags which are assumed to be styledtexttags.
        When split is given the text will be split over the value given, and
        tags applied in such a way that it the text can be safely splitted in
        pieces along split.

        :param text: str, a piece of text
        :param s_tags: styledtexttags that must be applied to the text
        :param split: str, optional. A string along which the output can
                      be safely split without breaking the styling.

        As adding markup means original text must be escaped, ESCAPE_FUNC is
        used. This can be used to convert the text of a styledtext to the format
        needed for a document backend.  Do not call this method in a report,
        use the :meth:`write_markup` method.

        .. note:: the algorithm is complex as it assumes mixing of tags is not
                  allowed: eg <b>text<i> here</b> not</i> is assumed invalid
                  as markup. If the s_tags require such a setup, what is
                  returned is <b>text</b><i><b> here</b> not</i>
                  overwrite this method if this complexity is not needed.
        """
        if not escape:
            escape_func = self.ESCAPE_FUNC
            self.ESCAPE_FUNC = lambda: (lambda text: text)
        #unicode text must be sliced correctly
        text = str(text)
        FIRST = 0
        LAST = 1
        tagspos = {}
        for s_tag in s_tags:
            tag = self.find_tag_by_stag(s_tag)
            if tag is not None:
                for (start, end) in s_tag.ranges:
                    if start in tagspos:
                        tagspos[start] += [(tag, FIRST)]
                    else:
                        tagspos[start] = [(tag, FIRST)]
                    if end in tagspos:
                        tagspos[end] = [(tag, LAST)] + tagspos[end]
                    else:
                        tagspos[end] = [(tag, LAST)]
        start = 0
        end = len(text)
        keylist = list(tagspos.keys())
        keylist.sort()
        keylist = [x for x in keylist if x <= len(text)]
        opentags = []
        otext = ""  #the output, text with markup
        lensplit = len(split)
        for pos in keylist:
            #write text up to tag
            if pos > start:
                if split:
                    #make sure text can split
                    splitpos = text[start:pos].find(split)
                    while splitpos != -1:
                        otext += self.ESCAPE_FUNC()(text[start:start+splitpos])
                        #close open tags
                        for opentag in reversed(opentags):
                            otext += opentag[1]
                        #add split text
                        otext += self.ESCAPE_FUNC()(split)
                        #open the tags again
                        for opentag in opentags:
                            otext += opentag[0]
                        #obtain new values
                        start = start + splitpos + lensplit
                        splitpos = text[start:pos].find(split)

                otext += self.ESCAPE_FUNC()(text[start:pos])
            #write out tags
            for tag in tagspos[pos]:
                #close open tags starting from last open
                for opentag in reversed(opentags):
                    otext += opentag[1]
                #if start, add to opentag in beginning as first to open
                if tag[1] == FIRST:
                    opentags = [tag[0]] + opentags
                else:
                    #end tag, is closed already, remove from opentag
                    opentags = [x for x in opentags if not x == tag[0] ]
                #now all tags are closed, open the ones that should open
                for opentag in opentags:
                    otext += opentag[0]
            start = pos
        #add remainder of text, no markup present there if all is correct
        if opentags:
            # a problem, we don't have a closing tag left but there are open
            # tags. Just keep them up to end of text
            pos = len(text)
            print('WARNING: DocBackend : More style tags in text than length '\
                    'of text allows.\n', opentags)
            if pos > start:
                if split:
                    #make sure text can split
                    splitpos = text[start:pos].find(split)
                    while splitpos != -1:
                        otext += self.ESCAPE_FUNC()(text[start:start+splitpos])
                        #close open tags
                        for opentag in reversed(opentags):
                            otext += opentag[1]
                        #add split text
                        otext += self.ESCAPE_FUNC()(split)
                        #open the tags again
                        for opentag in opentags:
                            otext += opentag[0]
                        #obtain new values
                        start = start + splitpos + lensplit
                        splitpos = text[start:pos].find(split)

                otext += self.ESCAPE_FUNC()(text[start:pos])
            for opentag in reversed(opentags):
                otext += opentag[1]
        else:
            otext += self.ESCAPE_FUNC()(text[start:end])
        if not escape:
            self.ESCAPE_FUNC = escape_func
        return otext

    def format_link(self, value):
        """
        Default format for links. Override for better support.

        value is: "TYPE DATA" where TYPE is 'url' or 'ref'.

        """
        return self.STYLETAG_MARKUP[DocBackend.UNDERLINE]

