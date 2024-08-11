#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
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


# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".textdoc")

# -------------------------------------------------------------------------
#
# URL string pattern
#
# -------------------------------------------------------------------------
URL_PATTERN = (
    r"""(((https?|mailto):)(//([^ /?#"]*))?([^ ?#"]*)(\?([^ #"]*))?(#([^ "]*))?)"""
)

# -------------------------------------------------------------------------
#
# IndexMark types
#
# -------------------------------------------------------------------------
INDEX_TYPE_ALP = 0
INDEX_TYPE_TOC = 1
LOCAL_HYPERLINK = 2
LOCAL_TARGET = 3


# ------------------------------------------------------------------------
#
# IndexMark
#
# ------------------------------------------------------------------------
class IndexMark:
    """
    Defines a mark to be associated with text for indexing.
    """

    def __init__(self, key="", itype=INDEX_TYPE_ALP, level=1):
        """
        Initialize the object with default values, unless values are specified.
        """
        self.key = key
        self.type = itype
        self.level = level


# ------------------------------------------------------------------------
#
# TextDoc
#
# ------------------------------------------------------------------------


class TextDoc(metaclass=ABCMeta):
    """
    Abstract Interface for text document generators. Output formats for
    text reports must implement this interface to be used by the report
    system.
    """

    @abstractmethod
    def page_break(self):
        """
        Forces a page break, creating a new page.
        """

    @abstractmethod
    def start_bold(self):
        """
        Start a section of bold text.
        """

    @abstractmethod
    def end_bold(self):
        """
        End a section of bold text.
        """

    @abstractmethod
    def start_superscript(self):
        """
        Start a section of superscript text.
        """

    @abstractmethod
    def end_superscript(self):
        """
        End a section of superscript text.
        """

    @abstractmethod
    def start_paragraph(self, style_name, leader=None):
        """
        Starts a new paragraph, using the specified style name.

        :param style_name: name of the :class:`.ParagraphStyle` to use for the
                           paragraph.
        :param leader: Leading text for a paragraph. Typically used
                       for numbering.
        """

    @abstractmethod
    def end_paragraph(self):
        """
        Ends the current paragraph.
        """

    @abstractmethod
    def start_table(self, name, style_name):
        """
        Starts a new table.

        :param name: Unique name of the table.
        :param style_name: :class:`.TableStyle` to use for the new table
        """

    @abstractmethod
    def end_table(self):
        """
        Ends the current table.
        """

    @abstractmethod
    def start_row(self):
        """
        Starts a new row on the current table.
        """

    @abstractmethod
    def end_row(self):
        """
        Ends the current row on the current table.
        """

    @abstractmethod
    def start_cell(self, style_name, span=1):
        """
        Starts a new table cell, using the paragraph style specified.

        :param style_name: :class:`.TableCellStyle` to use for the cell
        :param span: number of columns to span
        """

    @abstractmethod
    def end_cell(self):
        """
        Ends the current table cell.
        """

    @abstractmethod
    def write_text(self, text, mark=None, links=False):
        """
        Writes the text in the current paragraph. Should only be used after a
        start_paragraph and before an end_paragraph.

        :param text: text to write.
        :param mark:  :class:`.IndexMark` to use for indexing (if supported)
        :param links: make URLs in the text clickable (if supported)
        """

    def write_markup(self, text, s_tags, mark=None):
        """
        Writes the text in the current paragraph.  Should only be used after a
        start_paragraph and before an end_paragraph. Not all backends support
        s_tags, then the same happens as with write_text. Backends supporting
        write_markup will overwrite this method

        :param text: text to write. The text is assumed to be _not_ escaped
        :param s_tags: assumed to be list of styledtexttags to apply to the
                       text
        :param mark:  :class:`.IndexMark` to use for indexing (if supported)
        """
        self.write_text(text, mark=mark)

    def write_styled_note(
        self, styledtext, format, style_name, contains_html=False, links=False
    ):
        """
        Convenience function to write a styledtext to the cairo doc.

        :param styledtext: assumed a :class:`.StyledText` object to write
        :param format: 0 = Flowed, 1 = Preformatted
        :param style_name: name of the style to use for default presentation
        :param contains_html:
            bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable.
        :param links: bool, make URLs in the text clickable (if supported)

        overwrite this method if the backend supports styled notes
        """
        text = str(styledtext)
        self.write_note(text, format, style_name)

    def write_text_citation(self, text, mark=None, links=None):
        """
        Method to write text with Gramps <super> citation marks.
        """
        if not text:
            return
        parts = text.split("<super>")
        markset = False
        for piece in parts:
            if not piece:
                # a text '<super>text ...' splits as '', 'text..'
                continue
            piecesplit = piece.split("</super>")
            if len(piecesplit) == 2:
                self.start_superscript()
                self.write_text(piecesplit[0], links=links)
                self.end_superscript()
                if not piecesplit[1]:
                    # text ended with ' ... </super>'
                    continue
                if not markset:
                    self.write_text(piecesplit[1], mark, links=links)
                    markset = True
                else:
                    self.write_text(piecesplit[1], links=links)
            else:
                if not markset:
                    self.write_text(piece, mark, links=links)
                    markset = True
                else:
                    self.write_text(piece, links=links)

    @abstractmethod
    def add_media(self, name, align, w_cm, h_cm, alt="", style_name=None, crop=None):
        """
        Add a photo of the specified width (in centimeters).

        :param name: filename of the image to add
        :param align: alignment of the image. Valid values are 'left',
                      'right', 'center', and 'single'
        :param w_cm: width in centimeters
        :param h_cm: height in centimeters
        :param alt: an alternative text to use. Useful for eg html reports
        :param style_name: style to use for captions
        :param crop: image cropping parameters
        """

    def start_link(self, link):
        """
        Start a link section. This defaults to underlining.

        :param link: should be an item that makes sense in this
                     docgen type, if it implements linking.
        """
        self.start_underline()

    def stop_link(self):
        """
        Stop the link section. Defaults to stopping the underlining
        for docgen types that don't support links.
        """
        self.stop_underline()

    def start_underline(self):
        """
        Start a section of underlining. This passes without error
        so that docgen types are not required to have this.
        """
        pass

    def stop_underline(self):
        """
        Stops a section of underlining. This passes without error
        so that docgen ntypes are not required to have this.
        """
        pass

    def insert_toc(self):
        """
        Insert a Table of Contents at this point in the document. This passes
        without error so that docgen types are not required to have this.
        """
        pass

    def insert_index(self):
        """
        Insert an Alphabetical Index at this point in the document. This passes
        without error so that docgen types are not required to have this.
        """
        pass
