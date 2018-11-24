#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2009-2010  Benny Malengier <benny.malengier@gramps-project.org>
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2010       Tim Lyons
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


"""
Report output generator for html documents, based on Html and HtmlBackend
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import os
import shutil
import logging

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.utils.image import resize_to_jpeg
from gramps.gen.const import DATA_DIR, IMAGE_DIR, PROGRAM_NAME, URL_HOMEPAGE
from gramps.gen.errors import ReportError
from gramps.version import VERSION
from gramps.gen.plug.docgen import BaseDoc, TextDoc, URL_PATTERN
from gramps.plugins.lib.libhtmlbackend import HtmlBackend, process_spaces
from gramps.plugins.lib.libhtml import Html
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
LOG = logging.getLogger(".htmldoc")

_TEXTDOCSCREEN = 'grampstextdoc.css'
_HTMLSCREEN = 'grampshtml.css'

#------------------------------------------------------------------------
#
# Set up to make links clickable
#
#------------------------------------------------------------------------
_CLICKABLE = r'''<a href="\1">\1</a>'''

#------------------------------------------------------------------------
#
# HtmlDoc
#
#------------------------------------------------------------------------
class HtmlDoc(BaseDoc, TextDoc):
    """Implementation of the BaseDoc and TextDoc gen.plug.docgen api for the
    creation of Html files. This is achieved by writing on a HtmlBackend
    object

    div id's defined here:
        id="grampstextdoc" : the entire text report
        id="grampsheading" : a small defined heading, but not h1 to h6 !
        id="grampsstylednote" : start of part with a styled note, divided in
                                paragraphs
        id="grampsnote" : start of part with a note. This id is normally not
                          used

    The styles as defined in the stylesheed of the textdoc, will be converted
    to css class. Color is removed to avoid conflicts with the css. Also
    Fontface is removed. Size, italic, bold, margins, borders are retained
    """

    def __init__(self, styles, paper_style, uistate=None):
        BaseDoc.__init__(self, styles, None, uistate=uistate)
        self.style_declaration = ''
        self.htmllist = []
        self._backend = None
        self.css_filename = ''
        self.warn_dir = True
        self._col = 0
        self._tbl = None
        self._empty = 1
        self.title = ''
        self.__title_written = -1  # -1 = not written, 0 = writing, 1 = written
        self.__link_attrs = {}     # additional link attrs, eg {"style": "...", "class": "..."}
        self.use_table_headers = False # th, td
        self.first_row = True

    def set_css_filename(self, css_filename):
        """
        Set the css file to use. The path must be included.
        Note: DocReportDialog sets this for html doc
        """
        if css_filename and os.path.basename(css_filename):
            self.css_filename = css_filename
        else:
            self.css_filename = ''

    def open(self, filename):
        """
        Overwrite base method
        """
        self._backend = HtmlBackend(filename)
        self._backend.open()
        self.htmllist += [self._backend.html_body]
        #start a gramps report
        self.htmllist += [Html('div', id="grampstextdoc")]

        self.build_header()

    def build_header(self):
        """
        Build up the header of the html file over the defaults of Html()
        """
        # add additional meta tags and stylesheet links to head section
        # create additional meta tags
        _meta1 = 'name="generator" content="%s %s %s"' % (
            PROGRAM_NAME, VERSION, URL_HOMEPAGE)
        meta = Html('meta', attr=_meta1)

        #set styles of the report as inline css
        self.build_style_declaration()


        # Gramps favicon en css
        fname1 = '/'.join([self._backend.datadir(), 'favicon.ico'])
        fname2 = '/'.join([self._backend.datadir(), _TEXTDOCSCREEN])
        fname3 = '/'.join([self._backend.datadir(), _HTMLSCREEN])

        # links for Gramps favicon and stylesheets
        links = Html('link', rel='shortcut icon', href=fname1,
                     type='image/x-icon') + (
                         Html('link', rel='stylesheet', href=fname2,
                              type='text/css', media='screen', indent=False),)
        if self.css_filename:
            links += (Html('link', rel='stylesheet', href=fname3,
                           type='text/css', media='screen', indent=False),)
        self._backend.html_header += (meta, links)

    def build_style_declaration(self, id="grampstextdoc"):
        """
        Convert the styles of the report into inline css for the html doc
        """
        styles = self.get_style_sheet()

        text = []

        for sname in sorted(styles.get_cell_style_names()):
            style = styles.get_cell_style(sname)
            pad = "%.3fcm"  % style.get_padding()
            top = bottom = left = right = 'none'
            if style.get_top_border():
                top = 'thin solid #000000'
            if style.get_bottom_border():
                bottom = 'thin solid #000000'
            if style.get_left_border():
                left = 'thin solid #000000'
            if style.get_right_border():
                right = 'thin solid #000000'
            text.append('#%s .%s {\n'
                        '\tpadding: %s %s %s %s;\n'
                        '\tborder-top:%s; border-bottom:%s;\n'
                        '\tborder-left:%s; border-right:%s;\n}'
                        % (id, sname, pad, pad, pad, pad, top, bottom,
                           left, right))


        for style_name in sorted(styles.get_paragraph_style_names()):
            style = styles.get_paragraph_style(style_name)
            font = style.get_font()
            font_size = font.get_size()
            #font_color = '#%02x%02x%02x' % font.get_color()
            align = style.get_alignment_text()
            text_indent = "%.2f" % style.get_first_indent()
            right_margin = "%.2f" % style.get_right_margin()
            left_margin = "%.2f" % style.get_left_margin()
            top_margin = "%.2f" % style.get_top_margin()
            bottom_margin = "%.2f" % style.get_bottom_margin()

            top = bottom = left = right = 'none'
            if style.get_top_border():
                top = 'thin solid #000000'
            if style.get_bottom_border():
                bottom = 'thin solid #000000'
            if style.get_left_border():
                left = 'thin solid #000000'
            if style.get_right_border():
                right = 'thin solid #000000'

            italic = bold = ''
            if font.get_italic():
                italic = 'font-style:italic; '
            if font.get_bold():
                bold = 'font-weight:bold; '
            #if font.get_type_face() == FONT_SANS_SERIF:
            #    family = '"Helvetica","Arial","sans-serif"'
            #else:
            #    family = '"Times New Roman","Times","serif"'
            # do not allow color, set in base css !
            #    so no : 'color: %s' % font_color
            #    so no : 'font-family:%s;' % family
            text.append('#%s .%s {\n'
                        '\tfont-size: %dpt;\n'
                        '\ttext-align: %s; text-indent: %scm;\n'
                        '\tmargin-right: %scm; margin-left: %scm;\n'
                        '\tmargin-top: %scm; margin-bottom: %scm;\n'
                        '\tborder-top:%s; border-bottom:%s;\n'
                        '\tborder-left:%s; border-right:%s;\n'
                        '\t%s%s\n}'
                        % (id, style_name, font_size,
                           align, text_indent,
                           right_margin, left_margin,
                           top_margin, bottom_margin,
                           top, bottom, left, right,
                           italic, bold))

        self.style_declaration = '\n'.join(text)

    def close(self):
        """
        Overwrite base method
        """
        while len(self.htmllist) > 1:
            self.__reduce_list()
        #now write the actual file
        self._backend.close()
        self.write_support_files()

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination. If to_dir is not
        present, then the destination directory will be created.

        Normally 'to_fname' will be just a filename, without directory path.

        'to_dir' is the relative path name in the destination root. It will
        be prepended before 'to_fname'.
        """
        #build absolute path
        dest = os.path.join(self._backend.datadirfull(), to_dir, to_fname)

        destdir = os.path.dirname(dest)
        if not os.path.isdir(destdir):
            os.makedirs(destdir)

        if from_fname != dest:
            shutil.copyfile(from_fname, dest)
        elif self.warn_dir:
            raise ReportError(
                _("Possible destination error"),
                _("You appear to have set your target directory "
                  "to a directory used for data storage. This "
                  "could create problems with file management. "
                  "It is recommended that you consider using "
                  "a different directory to store your generated "
                  "web pages."))
            self.warn_dir = False

    def write_support_files(self):
        """
        Copy support files to the datadir that needs to hold them
        """
        #css of textdoc styles
        with open(os.path.join(self._backend.datadirfull(),
                               _TEXTDOCSCREEN), 'w') as tdfile:
            tdfile.write(self.style_declaration)
        #css file
        if self.css_filename:
            #we do an extra check in case file does not exist, eg cli call
            fullpath = os.path.join(DATA_DIR, self.css_filename)
            if os.path.exists(fullpath):
                self.copy_file(fullpath, _HTMLSCREEN)
        #favicon
        self.copy_file(os.path.join(IMAGE_DIR, 'webstuff', 'favicon.ico'),
                       'favicon.ico')

    def __reduce_list(self):
        """
        Takes the internal list of html objects, and adds the last to the
        previous. This closes the upper tag
        """
        self.htmllist[-2] += self.htmllist[-1]
        self.htmllist.pop()

    def __write_text(self, text, mark=None, markup=False, links=False):
        """
        @param text: text to write.
        @param mark:  IndexMark to use for indexing (not supported)
        @param markup: True if text already contains markup info.
                       Then text will no longer be escaped
        @param links: make URLs clickable if True
        """
        if not markup:
            text = self._backend.ESCAPE_FUNC()(text)
        if self.__title_written == 0:
            self.title += text
        if links is True:
            import re
            text = re.sub(URL_PATTERN, _CLICKABLE, text)
        self.htmllist[-1] += text

    def __empty_char(self):
        """
        Output a non breaking whitespace so as to have browser behave ok on
        empty content
        """
        self.__write_text('&nbsp;', markup=True)

    def write_text(self, text, mark=None, links=False):
        """
        Overwrite base method
        """
        if text != "":
            self._empty = 0
        self.__write_text(text, mark, links=links)

    def write_markup(self, text, s_tags, mark=None):
        """
        Overwrite base method
        Writes the text in the current paragraph.  Should only be used after a
        start_paragraph and before an end_paragraph.

        @param text: text to write. The text is assumed to be _not_ escaped
        @param s_tags:  assumed to be list of styledtexttags to apply to the
                        text
        @param mark:  IndexMark to use for indexing
        """
        markuptext = self._backend.add_markup_from_styled(text, s_tags)
        self.__write_text(markuptext, mark=mark, markup=True)

    def write_title(self):
        """
        Add title field to header
        """
        self._backend.html_header += Html('title', self.title,
                                          inline=True)

    def start_table(self, name, style):
        """
        Overwrite base method
        """
        self.first_row = True
        styles = self.get_style_sheet()
        self._tbl = styles.get_table_style(style)
        self.htmllist += [Html('table', width=str(self._tbl.get_width())+'%',
                               cellspacing='0')]

    def end_table(self):
        """
        Overwrite base method
        """
        self.__reduce_list()

    def start_row(self):
        """
        Overwrite base method
        """
        self.htmllist += [Html('tr')]
        self._col = 0

    def end_row(self):
        """
        Overwrite base method
        """
        self.first_row = False
        self.__reduce_list()

    def start_cell(self, style_name, span=1):
        """
        Overwrite base method
        """
        if self.use_table_headers and self.first_row:
            tag = "th"
        else:
            tag = "td"
        self._empty = 1
        if span > 1:
            self.htmllist += (Html(tag, colspan=str(span), class_=style_name),)
            self._col += span
        else:
            self.htmllist += (Html(tag, colspan=str(span),
                                   width=str(self._tbl.get_column_width(
                                       self._col))+ '%',
                                   class_=style_name),)
        self._col += 1

    def end_cell(self):
        """
        Overwrite base method
        """
        self.__reduce_list()

    def start_paragraph(self, style_name, leader=None):
        """
        Overwrite base method
        """
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)
        level = style.get_header_level()
        if level == 0:
            #a normal paragraph
            self.htmllist += (Html('p', class_=style_name, inline=True),)
        elif level == 1:
            if self.__title_written == -1 and \
                    style_name.upper().find('TITLE') != -1:
                self.__title_written = 0
                self.htmllist += (Html('div', id="header"),)
                self.htmllist += (Html('h1', class_=style_name, id='SiteTitle',
                                       inline=True),)
            else:
                self.htmllist += (Html('h1', class_=style_name, inline=True),)
        elif 2 <= level <= 5:
            tag = 'h'+str(level+1)
            self.htmllist += (Html(tag, class_=style_name, inline=True),)
        else:
            # a low level header
            self.htmllist += (Html('div', id='grampsheading',
                                   class_=style_name),)
        if leader is not None:
            self.write_text(leader+' ')

    def end_paragraph(self):
        """
        Overwrite base method
        """
        if self._empty == 1:
            self.__empty_char()
        self._empty = 0
        self.__reduce_list()
        if self.__title_written == 0:
            self.__title_written = 1
            #close div statement
            self.__reduce_list()
            self.write_title()

    def start_bold(self):
        """
        Overwrite base method
        """
        self.htmllist += [Html('strong')]

    def end_bold(self):
        """
        Overwrite base method
        """
        self.__reduce_list()

    def start_superscript(self):
        """
        Overwrite base method
        """
        self.htmllist += [Html('sup')]

    def end_superscript(self):
        """
        Overwrite base method
        """
        self.__reduce_list()

    def write_styled_note(self, styledtext, format, style_name,
                          contains_html=False, links=False):
        """
        Convenience function to write a styledtext to the html doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. HtmlDoc will show the html as pure text, so
            no escaping will happen.
        links: bool, make URLs clickable if True
        """
        text = str(styledtext)

        self.htmllist += [Html('div', id='grampsstylednote')]
        if contains_html:
            #just dump the note out as it is. Adding markup would be dangerous
            # as it could destroy the html. If html code, one can do the
            self.start_paragraph(style_name)
            self.__write_text(text, markup=True, links=links)
            self.end_paragraph()
        else:
            s_tags = styledtext.get_tags()
            markuptext = self._backend.add_markup_from_styled(text, s_tags,
                                                              split='\n')
            self.start_paragraph(style_name)
            inpara = True
            self._empty = 1   # para is empty
            # we explicitly set _empty because start and end para do not seem
            # to do a very good job at setting them
            linenb = 1
            # The code is tricky here, because we don't want to start a new para
            # at the end of the last line if there is no newline there.
            # Instead, we want to just end the current para.
            for line in markuptext.split('\n'):
                [line, sigcount] = process_spaces(line, format)
                if sigcount == 0:
                    if inpara is False:
                        # needed for runs of three or more newlines
                        self.start_paragraph(style_name)
                        inpara = True
                        self._empty = 1   # para is empty
                    self.end_paragraph()
                    inpara = False
                    linenb = 1
                else:
                    if inpara is False:
                        self.start_paragraph(style_name)
                        inpara = True
                        self._empty = 1   # para is empty
                    if linenb > 1:
                        self.htmllist[-1] += Html('br')
                    self.__write_text(line, markup=True, links=links)
                    self._empty = 0  # para is not empty
                    linenb += 1
            if inpara is True:
                self.end_paragraph()
            if sigcount == 0:
                # if the last line was blank, then as well as outputting the
                # previous para, which we have just done, we also output a new
                # blank para
                self.start_paragraph(style_name)
                self._empty = 1   # para is empty
                self.end_paragraph()
        #end div element
        self.__reduce_list()

    def add_media(self, name, pos, w_cm, h_cm, alt='', style_name=None,
                  crop=None):
        """
        Overwrite base method
        """
        self._empty = 0
        size = int(max(w_cm, h_cm) * float(150.0/2.54))
        refname = "is%s" % os.path.basename(name)

        imdir = self._backend.datadirfull()

        try:
            resize_to_jpeg(name, imdir + os.sep + refname, size, size,
                           crop=crop)
        except:
            LOG.warning(_("Could not create jpeg version of image %(name)s"),
                        name)
            return

        if len(alt):
            alt = '<br />'.join(alt)

        if pos not in ["right", "left"]:
            if len(alt):
                self.htmllist[-1] += Html('div') + (
                    Html('img', src=imdir + os.sep + refname,
                         border='0', alt=alt),
                    Html('p', class_="DDR-Caption") + alt
                )
            else:
                self.htmllist[-1] += Html('img', src=imdir + os.sep + refname,
                                          border='0', alt=alt)
        else:
            if len(alt):
                self.htmllist[-1] += Html(
                    'div', style_="float: %s; padding: 5px; margin: 0;" % pos
                    ) + (Html('img', src=imdir + os.sep + refname,
                              border='0', alt=alt),
                         Html('p', class_="DDR-Caption") + alt)
            else:
                self.htmllist[-1] += Html('img', src=imdir + os.sep + refname,
                                          border='0', alt=alt, align=pos)

    def page_break(self):
        """
        overwrite base method so page break has no effect
        """
        pass

    def start_link(self, link):
        """
        Starts a section to add a link. Link is a URI.
        """
        self.htmllist += [Html('a', href=link, **self.__link_attrs)]

    def stop_link(self):
        """
        Stop a section of a link.
        """
        self.__reduce_list()

    def start_underline(self):
        """
        Starts a section of underlining.
        """
        self.htmllist += [Html('u')]

    def stop_underline(self):
        """
        Stop underlining.
        """
        self.__reduce_list()

    def set_link_attrs(self, attrs):
        """
        Set some a attributes/values. attrs is a dictionary, eg
          {"style": "...", "class": "..."}
        """
        self.__link_attrs = attrs
