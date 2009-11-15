#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2009       Benny Malengier <benny.malengier@gramps-project.org>
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

# $Id:HtmlDoc.py 9912 2008-01-22 09:17:46Z acraphae $


"""
Report output generator for html documents, based on Html and HtmlBackend
"""

#------------------------------------------------------------------------
#
# python modules 
#
#------------------------------------------------------------------------
import os
import shutil
import time
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules 
#
#------------------------------------------------------------------------
from gui.utils import open_file_with_default_application
import ImgManip
import const
from gen.plug.docgen import BaseDoc, TextDoc, FONT_SANS_SERIF
from libhtmlbackend import HtmlBackend
from libhtml import Html
from QuestionDialog import WarningDialog

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".htmldoc")

_TEXTDOCSCREEN = 'grampstextdoc.css'
_HTMLSCREEN = 'grampshtml.css'

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

    def __init__(self, styles, paper_style):
        BaseDoc.__init__(self, styles, None)
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

    def set_css_filename(self, css_filename):
        """
        Set the css file to use. The path must be included. 
        Note: DocReportDialog sets this for html doc
        """
        if os.path.basename(css_filename):
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
        _meta1 = 'name="generator" content="%s %s %s"' % (const.PROGRAM_NAME,
                    const.VERSION, const.URL_HOMEPAGE)
        meta = Html('meta', attr = _meta1) 
        
        #set styles of the report as inline css
        self.build_style_declaration()
        
        
        # GRAMPS favicon en css
        fname1 = '/'.join([self._backend.datadir(), 'favicon.ico'])
        fname2 = '/'.join([self._backend.datadir(), _TEXTDOCSCREEN])
        fname3 = '/'.join([self._backend.datadir(), _HTMLSCREEN])
        
        # links for GRAMPS favicon and stylesheets
        links = Html('link', rel='shortcut icon', href=fname1,
                        type='image/x-icon') + (
                Html('link', rel='stylesheet', href=fname2, type='text/css',
                        media='screen', indent=False),)
        if self.css_filename:
            links += (Html('link', rel='stylesheet', href=fname3, 
                      type='text/css', media='screen', indent=False),
                )
        self._backend.html_header += (meta, links)

    def build_style_declaration(self):
        """
        Convert the styles of the report into inline css for the html doc
        """
        styles = self.get_style_sheet()
        
        text = []

        for sname in styles.get_cell_style_names():
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
            text.append('#grampstextdoc .%s {\n'
                        '\tpadding: %s %s %s %s;\n'
                        '\tborder-top:%s; border-bottom:%s;\n' 
                        '\tborder-left:%s; border-right:%s;\n}' 
                    % (sname, pad, pad, pad, pad, top, bottom, left, right))


        for style_name in styles.get_paragraph_style_names():
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
            text.append('#grampstextdoc .%s {\n'
                        '\tfont-size: %dpt;\n' 
                        '\ttext-align: %s; text-indent: %scm;\n' 
                        '\tmargin-right: %scm; margin-left: %scm;\n' 
                        '\tmargin-top: %scm; margin-bottom: %scm;\n' 
                        '\tborder-top:%s; border-bottom:%s;\n' 
                        '\tborder-left:%s; border-right:%s;\n' 
                        '\t%s%s\n}' 
                        % (style_name, font_size, 
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
        while len(self.htmllist)>1 :
            self.__reduce_list()
        #now write the actual file
        self._backend.close()
        self.write_support_files()

        if self.open_req:
            import Utils
            open_file_with_default_application(self._backend.getf())

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present, then the destination directory will be created.

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
            WarningDialog(
                _("Possible destination error") + "\n" +
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
        tdfile = open(os.path.join(self._backend.datadirfull(), 
                      _TEXTDOCSCREEN), 'w')
        tdfile.write(self.style_declaration)
        tdfile.close()
        #css file
        if self.css_filename:
            #we do an extra check in case file does not exist, eg cli call
            fullpath = os.path.join(const.DATA_DIR, self.css_filename)
            if os.path.exists(fullpath):
                self.copy_file(fullpath, _HTMLSCREEN)
        #favicon
        self.copy_file(os.path.join(const.IMAGE_DIR, 'favicon.ico'), 
                        'favicon.ico')

    def __reduce_list(self):
        """
        Takes the internal list of html objects, and adds the last to the 
        previous. This closes the upper tag
        """
        self.htmllist[-2] += self.htmllist[-1]
        self.htmllist.pop()
    
    def __write_text(self, text, mark=None, markup=False):
        """
        @param text: text to write.
        @param mark:  IndexMark to use for indexing (if supported)
        @param markup: True if text already contains markup info. 
                       Then text will no longer be escaped
        """
        if not markup:            
            text = self._backend.ESCAPE_FUNC()(text)
        if self.__title_written == 0 :
            self.title += text
        self.htmllist[-1] += text
    
    def __empty_char(self):
        """
        Output a non breaking whitespace so as to have browser behave ok on 
        empty content
        """
        self.__write_text('&nbsp;', markup=True)
    
    def write_text(self, text, mark=None):
        """
        Overwrite base method
        """
        if text != "":
            self._empty = 0
        self.__write_text(text, mark)

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
        styles = self.get_style_sheet()
        self._tbl = styles.get_table_style(style)
        self.htmllist += [Html('table', width=str(self._tbl.get_width())+'%%',
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
        self.__reduce_list()

    def start_cell(self, style_name, span=1):
        """
        Overwrite base method
        """
        self._empty = 1
        if span > 1:
            self.htmllist += (Html('td', colspan=str(span), 
                                    class_=style_name),)
            self._col += span
        else:
            self.htmllist += (Html('td', colspan=str(span), 
                                width=str(self._tbl.get_column_width(
                                            self._col))+ '%%',
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
        elif 2<= level <= 5:
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

    def write_note(self, text, format, style_name):
        """
        Overwrite base method
        """
        self.htmllist += [Html('div', id='grampsstylednote')]
        if format == 1:
            #preformatted, retain whitespace.
            #  User should use write_styled_note for correct behavior, in this 
            #    more basic method we convert all to a monospace character
            self.htmllist += [Html('pre', class_=style_name, 
                                style = 'font-family: courier, monospace',
                                indent=None, inline=True)]
            self.write_text(text)
            #end pre element
            self.__reduce_list()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
        else:
            raise NotImplementedError
        #end div element
        self.__reduce_list()

    def write_styled_note(self, styledtext, format, style_name):
        """
        Convenience function to write a styledtext to the html doc. 
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        """
        text = str(styledtext)

        s_tags = styledtext.get_tags()
        #FIXME: following split should be regex to match \n\s*\n instead?
        markuptext = self._backend.add_markup_from_styled(text, s_tags, 
                                                          split='\n\n')
        self.htmllist += [Html('div', id='grampsstylednote')]
        if format == 1:
            #preformatted, retain whitespace.
            #so use \n\n for paragraph detection
            #FIXME: following split should be regex to match \n\s*\n instead?
            self.htmllist += [Html('pre', indent=None, inline=True)]
            for line in markuptext.split('\n\n'):
                self.start_paragraph(style_name)
                for realline in line.split('\n'):
                    self.__write_text(realline, markup=True)
                    self.htmllist[-1] += Html('br')
                self.end_paragraph()
            #end pre element
            self.__reduce_list()
        elif format == 0:
            #flowed
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                self.start_paragraph(style_name)
                self.__write_text(line, markup=True)
                self.end_paragraph()
        #end div element
        self.__reduce_list()

    def add_media_object(self, name, pos, w_cm, h_cm, alt=''):
        """
        Overwrite base method
        """
        self._empty = 0
        size = int(max(w_cm, h_cm) * float(150.0/2.54))
        refname = "is%s" % os.path.basename(name)

        imdir = self._backend.datadirfull()

        try:
            ImgManip.resize_to_jpeg(name, imdir + os.sep + refname, size, size)
        except:
            LOG.warn(_("Could not create jpeg version of image %(name)s") % 
                        {'name' : name})
            return

        if pos not in ["right", "left"] :
            self.htmllist[-1] += Html('img', src= imdir + os.sep + refname, 
                            border = '0', alt=alt)
        else:
            self.htmllist[-1] += Html('img', src= imdir + os.sep + refname, 
                            border = '0', alt=alt, align=pos)

    def page_break(self):
        """
        overwrite base method so page break has no effect
        """
        pass

    def start_link(self, link):
        """
        Starts a section to add a link. Link is a URI.
        """
        self.htmllist += [Html('a', href=link)]

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
