#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2017       Paul Franklin
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import logging

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug.docgen import (
    BaseDoc,
    TextDoc,
    FONT_SERIF,
    PARA_ALIGN_RIGHT,
    PARA_ALIGN_CENTER,
    PARA_ALIGN_JUSTIFY,
    URL_PATTERN,
)
from gramps.gen.utils.image import image_size, image_actual_size, resize_to_jpeg_buffer
from gramps.gen.errors import ReportError
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

LOG = logging.getLogger(".rtfdoc")

# ------------------------------------------------------------------------
#
# Set up to make links clickable
#
# ------------------------------------------------------------------------
_CLICKABLE = r"""{\\field{\\*\\fldinst HYPERLINK "\1"}{\\fldrslt \1}}"""


# ------------------------------------------------------------------------
#
# Functions
#
# ------------------------------------------------------------------------
def twips(length_cm):
    """
    RTF uses a unit called "twips" for its measurements. According to the
    RTF specification, 1 point is 20 twips. This routines converts
    centimeters to twips

    2.54 cm/inch 72pts/inch, 20twips/pt
    """
    return int(((length_cm / 2.54) * 72) + 0.5) * 20


# ------------------------------------------------------------------------
#
# Rich Text Format Document interface. The current interface does not
# use style sheets. Instead it writes raw formatting.
#
# ------------------------------------------------------------------------
class RTFDoc(BaseDoc, TextDoc):
    """
    Opens the file, and writes the header. Builds the color and font tables.
    Fonts are chosen using the MS TrueType fonts, since it is assumed that if
    you are generating RTF, you are probably targeting Word.  This generator
    assumes a Western Europe character set.
    """

    def open(self, filename):
        if filename[-4:] != ".rtf":
            self.filename = filename + ".rtf"
        else:
            self.filename = filename

        try:
            self.file = open(self.filename, "w")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.filename)

        style_sheet = self.get_style_sheet()

        self.file.write(
            "{\\rtf1\\ansi\\ansicpg1252\\deff0\n"
            "{\\fonttbl\n"
            "{\\f0\\froman\\fcharset0\\fprq0 Times New Roman;}\n"
            "{\\f1\\fswiss\\fcharset0\\fprq0 Arial;}}\n"
            "{\\colortbl\n"
        )

        self.color_map = {}
        index = 1
        self.color_map[(0, 0, 0)] = 0
        self.file.write("\\red0\\green0\\blue0;")
        for style_name in style_sheet.get_paragraph_style_names():
            style = style_sheet.get_paragraph_style(style_name)
            fgcolor = style.get_font().get_color()
            bgcolor = style.get_background_color()
            if fgcolor not in self.color_map:
                self.color_map[fgcolor] = index
                self.file.write("\\red%d\\green%d\\blue%d;" % fgcolor)
                index += 1
            if bgcolor not in self.color_map:
                self.file.write("\\red%d\\green%d\\blue%d;" % bgcolor)
                self.color_map[bgcolor] = index
                index += 1
        self.file.write("}\n")
        self.file.write(
            "\\kerning0\\cf0\\viewkind1"
            + "\\paperw%d" % twips(self.paper.get_size().get_width())
            + "\\paperh%d" % twips(self.paper.get_size().get_height())
            + "\\margl%d" % twips(self.paper.get_left_margin())
            + "\\margr%d" % twips(self.paper.get_right_margin())
            + "\\margt%d" % twips(self.paper.get_top_margin())
            + "\\margb%d" % twips(self.paper.get_bottom_margin())
            + "\\widowctl\n"
        )
        self.in_table = 0
        self.text = ""
        self.p_wide = float(self.paper.get_usable_width())

    # --------------------------------------------------------------------
    #
    # Write the closing brace, and close the file.
    #
    # --------------------------------------------------------------------
    def close(self):
        self.file.write("}\n")
        self.file.close()

    # --------------------------------------------------------------------
    #
    # Force a section page break
    #
    # --------------------------------------------------------------------
    def end_page(self):
        self.file.write("\\sbkpage\n")

    # --------------------------------------------------------------------
    #
    # Starts a paragraph. Instead of using a style sheet, generate
    # the style for each paragraph on the fly. Not the ideal, but it
    # does work.
    #
    # --------------------------------------------------------------------
    def start_paragraph(self, style_name, leader=None):
        self.opened = 0
        style_sheet = self.get_style_sheet()
        para = style_sheet.get_paragraph_style(style_name)

        # build font information

        font = para.get_font()
        size = font.get_size() * 2
        bgindex = self.color_map[para.get_background_color()]
        fgindex = self.color_map[font.get_color()]
        if font.get_type_face() == FONT_SERIF:
            self.font_type = "\\f0"
        else:
            self.font_type = "\\f1"
        self.font_type += "\\fs%d\\cf%d\\cb%d" % (size, fgindex, bgindex)

        if font.get_bold():
            self.font_type += "\\b"
        if font.get_underline():
            self.font_type += "\\ul"
        if font.get_italic():
            self.font_type += "\\i"

        # build paragraph information

        if not self.in_table:
            para_type = "\n\\pard"
        else:
            para_type = "\n\\pard\\intbl"
        if para.get_alignment() == PARA_ALIGN_RIGHT:
            para_type += "\\qr"
        elif para.get_alignment() == PARA_ALIGN_CENTER:
            para_type += "\\qc"
        para_type += (
            "\\ri%d" % twips(para.get_right_margin())
            + "\\li%d" % twips(para.get_left_margin())
            + "\\fi%d" % twips(para.get_first_indent())
        )

        if para.get_alignment() == PARA_ALIGN_JUSTIFY:
            para_type += "\\qj"
        if para.get_padding():
            para_type += "\\sa%d" % twips(para.get_padding() / 2.0)
        if para.get_top_border():
            para_type += "\\brdrt\\brdrs"
        if para.get_bottom_border():
            para_type += "\\brdrb\\brdrs"
        if para.get_left_border():
            para_type += "\\brdrl\\brdrs"
        if para.get_right_border():
            para_type += "\\brdrr\\brdrs"
        if para.get_first_indent():
            para_type += "\\fi%d" % twips(para.get_first_indent())
        if para.get_left_margin():
            para_type += "\\li%d" % twips(para.get_left_margin())
        if para.get_right_margin():
            para_type += "\\ri%d" % twips(para.get_right_margin())

        # the deferred newline while in table cell
        if self.in_table and self.need_nl:
            self.text += "\n\\line}"
            self.need_nl = False

        self.text += para_type

        if leader:
            self.opened = 1
            self.text += "\\tx%d" % twips(para.get_left_margin())
            self.text += "{%s " % self.font_type
            self.text += leader
            # self.write_text(leader)
            # self.file.write(self.text)
            # self.text = ""
            self.text += "\\tab}"
            self.opened = 0

    # --------------------------------------------------------------------
    #
    # Ends a paragraph. Care has to be taken to make sure that the
    # braces are closed properly. The self.opened flag is used to indicate
    # if braces are currently open. If the last write was the end of
    # a bold-faced phrase, braces may already be closed.
    #
    # --------------------------------------------------------------------
    def end_paragraph(self):
        # To deal with newlines in the table cell, we defer them till the
        # beginning of the next paragraph.  This is so that we don't get
        # an excessive space at the end of a table.
        if not self.in_table:
            self.file.write(self.text)
            LOG.debug(
                "end_paragraph: opened: %d write: %s",
                self.opened,
                self.text + "}" if self.opened else "" + "newline",
            )
            if self.opened:
                self.file.write("}")
                self.opened = 0
            self.file.write("\n\\par")
            self.text = ""
        else:
            if self.text == "":
                self.write_text(" ")
            self.need_nl = True

    # --------------------------------------------------------------------
    #
    # Inserts a manual page break
    #
    # --------------------------------------------------------------------
    def page_break(self):
        self.file.write("\\page\n")

    # --------------------------------------------------------------------
    #
    # Starts boldfaced text, enclosed the braces
    #
    # --------------------------------------------------------------------
    def start_bold(self):
        LOG.debug(
            "start_bold: opened: %d saved text: %s",
            self.opened,
            "}" if self.opened else "" + "{%s\\b " % self.font_type,
        )
        if self.opened:
            self.text += "}"
        self.text += "{%s\\b " % self.font_type
        self.opened = 1

    # --------------------------------------------------------------------
    #
    # Ends boldfaced text, closing the braces
    #
    # --------------------------------------------------------------------
    def end_bold(self):
        LOG.debug("end_bold: opened: %d saved text: %s", self.opened, self.text + "}")
        if not self.opened == 1:
            print(self.opened)
            raise RuntimeError
        self.opened = 0
        self.text += "}"

    def start_superscript(self):
        self.text += "{{\\*\\updnprop5801}\\up10 "

    def end_superscript(self):
        self.text += "}"

    # --------------------------------------------------------------------
    #
    # Start a table. Grab the table style, and store it. Keep a flag to
    # indicate that we are in a table. This helps us deal with paragraphs
    # internal to a table. RTF does not require anything to start a
    # table, since a table is treated as a bunch of rows.
    #
    # --------------------------------------------------------------------
    def start_table(self, name, style_name):
        self.in_table = 1
        styles = self.get_style_sheet()
        table_style = styles.get_table_style(style_name)
        self._cells = []
        if self.get_rtl_doc():
            cell_percent = 100.0
        else:
            cell_percent = 0.0
        for cell in range(table_style.get_columns()):
            if self.get_rtl_doc():
                cell_percent -= float(table_style.get_column_width(cell))
            else:
                cell_percent += float(table_style.get_column_width(cell))
            self._cells.append(twips((self.p_wide * cell_percent) / 100.0))
        if self._cells[-1:] == [0]:
            self._cells[-1:] = [twips(self.p_wide)]  # left edge => right edge

    # --------------------------------------------------------------------
    #
    # End a table. Turn off the table flag
    #
    # --------------------------------------------------------------------
    def end_table(self):
        self.in_table = 0

    # --------------------------------------------------------------------
    #
    # Start a row. RTF uses the \trowd to start a row. RTF also specifies
    # all the cell data after it has specified the cell definitions for
    # the row. Therefore it is necessary to keep a list of cell contents
    # that is to be written after all the cells are defined.  It is also
    # necessary to keep a list of the row columns definitions, since for
    # RTL columns the columns which are processed last (in LTR) come first,
    # and we don't know which will be skipped with a non-one "span" argument
    # until we process them
    #
    # --------------------------------------------------------------------
    def start_row(self):
        self.contents = []
        self.columns = []
        self.cell = 0
        self.text = ""
        self.file.write("\\trowd\n")

    # --------------------------------------------------------------------
    #
    # End a row. Write the cell contents, separated by the \cell marker,
    # then terminate the row with a \row marker
    #
    # --------------------------------------------------------------------
    def end_row(self):
        for column in sorted(self.columns):
            for line in column[1]:
                self.file.write(line)
        if self.get_rtl_doc():
            self.contents.reverse()
        self.file.write("{")
        for line in self.contents:
            self.file.write(line)
            self.file.write("\\cell ")
        self.file.write("}\\row\n")

    # --------------------------------------------------------------------
    #
    # Start a cell. Dump out the cell specifics, such as borders. Cell
    # widths are kind of interesting. RTF doesn't specify how wide a cell
    # is, but rather where its right edge is in relationship to the
    # left margin. This means that each cell is the cumlative of the
    # previous cells plus its own width.
    #
    # --------------------------------------------------------------------
    def start_cell(self, style_name, span=1):
        cell_data = []
        styles = self.get_style_sheet()
        s = styles.get_cell_style(style_name)
        if s.get_top_border():
            cell_data.append("\\clbrdrt\\brdrs\\brdrw10\n")
        if s.get_bottom_border():
            cell_data.append("\\clbrdrb\\brdrs\\brdrw10\n")
        if s.get_left_border():
            cell_data.append("\\clbrdrl\\brdrs\\brdrw10\n")
        if s.get_right_border():
            cell_data.append("\\clbrdrr\\brdrs\\brdrw10\n")
        self.need_nl = False
        cell_data.append("\\cellx%d\n" % self._cells[self.cell + span - 1])
        self.columns.append([self._cells[self.cell + span - 1], cell_data])
        self.cell += 1

    # --------------------------------------------------------------------
    #
    # End a cell. Save the current text in the content lists, since data
    # must be saved until all cells are defined.
    #
    # --------------------------------------------------------------------
    def end_cell(self):
        if self.opened == 1:  # We defered paragraph end and now need it.
            self.text += "}"
            self.opened = 0
        self.contents.append(self.text)
        self.text = ""

    # --------------------------------------------------------------------
    #
    # Add a photo. Embed the photo in the document. Use the Python
    # imaging library to load and scale the photo. The image is converted
    # to JPEG, since it is smaller, and supported by RTF. The data is
    # dumped as a string of HEX numbers.
    #
    # --------------------------------------------------------------------
    def add_media(self, name, pos, x_cm, y_cm, alt="", style_name=None, crop=None):
        width, height = image_size(name)

        if (width, height) == (0, 0):
            return

        (act_width, act_height) = image_actual_size(x_cm, y_cm, width, height)

        act_width = twips(act_width)
        act_height = twips(act_height)

        size = [act_width, act_height]
        buf = resize_to_jpeg_buffer(name, size, crop=crop)
        # The size may change because of cropping or keeping the ratio
        act_width = size[0]
        act_height = size[1]

        if self.in_table:
            self.text += "{\\*\\shppict{\\pict\\jpegblip"
            self.text += "\\picwgoal%d\\pichgoal%d\n" % (act_width, act_height)
            index = 1
            for i in buf:
                self.text += "%02x" % i
                if index % 32 == 0:
                    self.text += "\n"
                index = index + 1
            self.text += "}}\\par\n"
        else:
            self.file.write("{\\*\\shppict{\\pict\\jpegblip")
            self.file.write("\\picwgoal%d\\pichgoal%d\n" % (act_width, act_height))
            index = 1
            for i in buf:
                self.file.write("%02x" % i)
                if index % 32 == 0:
                    self.file.write("\n")
                index = index + 1
            self.file.write("}}\\par\n")

        if len(alt):
            self.file.write("%s\n\\par\n" % "\\par".join(alt))

    def write_styled_note(
        self, styledtext, format, style_name, contains_html=False, links=False
    ):
        """
        Convenience function to write a styledtext to the RTF doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. RTFDoc prints the html without handling it
        links: bool, make URLs clickable if True
        """
        text = str(styledtext)
        self.start_paragraph(style_name)
        linenb = 1
        for line in text.split("\n"):
            [line, sigcount] = process_spaces(line, format)
            if sigcount == 0:
                if self.in_table:
                    #    # Add LF when in table as in indiv_complete report
                    self.write_text("\n")
                self.end_paragraph()
                self.start_paragraph(style_name)
                linenb = 1
            else:
                if linenb > 1:
                    self.write_text("\n")
                self.write_text(line, links=links)
                linenb += 1
        # FIXME: I don't understand why these newlines are necessary.
        # It may be related to the behaviour of end_paragraph inside tables,
        # and write_text converting \n to end paragraph.
        # This code prevents the whole document going wrong, but seems to
        # produce an extra paragraph mark at the end of each table cell.
        if self.in_table:
            #    # Add LF when in table as in indiv_complete report
            self.write_text("\n")
        self.end_paragraph()

    # --------------------------------------------------------------------
    #
    # Writes text. If braces are not currently open, open them. Loop
    # character by character (terribly inefficient, but it works). If a
    # character is 8 bit (>127), convert it to a hex representation in
    # the form of \`XX. Make sure to escape braces.
    #
    # --------------------------------------------------------------------
    def write_text(self, text, mark=None, links=False):
        # Convert to unicode, just in case it's not. Fix of bug 2449.
        text = str(text)
        LOG.debug("write_text: opened: %d input text: %s", self.opened, text)
        if self.opened == 0:
            self.opened = 1
            self.text += "{%s " % self.font_type

        for i in text:
            if ord(i) > 127:
                if ord(i) < 256:
                    self.text += "\\'%2x" % ord(i)
                else:
                    # If (uni)code with more than 8 bits:
                    # RTF req valus in decimal, not hex.
                    self.text += "{\\uc0\\u%d}" % ord(i)
            elif i == "\n":
                self.text += "\n\\par "
            elif i == "{" or i == "}" or i == "\\":
                self.text += "\\%s" % i
            else:
                self.text += i

        if links is True:
            import re

            self.text = re.sub(URL_PATTERN, _CLICKABLE, self.text)
        LOG.debug("write_text, exit: opened: %d saved text: %s", self.opened, self.text)


def process_spaces(line, format):
    """
    Function to process spaces in text lines for flowed and pre-formatted notes.
    line : text to process
    format : = 0 : Flowed, = 1 : Preformatted

    If the text is flowed (format==0), then leading spaces
    are removed, and multiple spaces are reduced to one.
    If the text is pre-formatted (format==1). then all spaces are preserved

    Note that xml is just treated like any other text, because it will be from
    the original note, and it is just printed, not interpreted.
    Returns the processed text, and the number of significant
    (i.e. non-white-space) chars.
    """
    txt = ""
    xml = False
    space = False
    sigcount = 0
    # we loop through every character, which is very inefficient, but an
    # attempt to use a regex replace didn't always work.
    for char in line:
        if char == " " or char == "\t":
            if format == 1:
                txt += char
            elif format == 0 and sigcount == 0:
                pass
            elif format == 0 and space is False:
                space = True
                txt += char
            elif format == 0 and space is True:
                pass
        else:
            sigcount += 1
            space = False
            txt += char
    return [txt, sigcount]
