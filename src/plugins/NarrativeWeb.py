#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007       Gary Burton <gary.burton@zen.co.uk>
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

# $Id$

"""
Narrative Web Page generator.
"""

#------------------------------------------------------------------------
#
# Suggested pylint usage:
#      --max-line-length=100     Yes, I know PEP8 suggest 80, but this has longer lines
#      --argument-rgx='[a-z_][a-z0-9_]{1,30}$'    Several identifiers are two characters
#      --variable-rgx='[a-z_][a-z0-9_]{1,30}$'    Several identifiers are two characters
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import md5
import time
import locale
import shutil
import codecs
import tarfile
import operator
from gettext import gettext as _
from cStringIO import StringIO
from textwrap import TextWrapper
from unicodedata import normalize

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WebPage")

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import gen.lib
import const
from GrampsCfg import get_researcher
import Sort
from PluginUtils import (register_report, FilterOption, EnumeratedListOption,
                         PersonOption, BooleanOption, NumberOption,
                         StringOption, DestinationOption, NoteOption,
                         MediaOption)
from ReportBase import (Report, ReportUtils, MenuReportOptions, CATEGORY_WEB,
                        MODE_GUI, MODE_CLI, Bibliography)
import Utils
import ThumbNails
import ImgManip
import Mime
from QuestionDialog import ErrorDialog, WarningDialog
from BasicUtils import name_displayer as _nd
from DateHandler import displayer as _dd
from DateHandler import parser as _dp
from gen.proxy import PrivateProxyDb, LivingProxyDb
from gen.lib.eventroletype import EventRoleType

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_NARRATIVE = "narrative.css"
_NARRATIVEPRINT = "narrative-print.css"
_NAME_COL  = 3

_MAX_IMG_WIDTH = 800   # resize images that are wider than this
_MAX_IMG_HEIGHT = 600  # resize images that are taller than this
_WIDTH = 160
_HEIGHT = 50
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5

# This information defines the list of styles in the Narrative Web
# options dialog as well as the location of the corresponding SCREEN
# stylesheets.
_CSS_FILES = [
    # First is used as default selection.
    [_("Basic - Ash"),     'NWeb-Screen_Basic-Ash.css'],
    [_("Basic - Cypress"), 'NWeb-Screen_Basic-Cypress.css'],
    [_("Basic - Lilac"),   'NWeb-Screen_Basic-Lilac.css'],
    [_("Basic - Peach"),   'NWeb-Screen_Basic-Peach.css'],
    [_("Basic - Spruce"),  'NWeb-Screen_Basic-Spruce.css'],
    [_("Mainz"),           'NWeb-Screen_Mainz.css'],
    [_("Nebraska"),        'NWeb-Screen_Nebraska.css'],
    [_("No style sheet"),  ''],
    ]

_CHARACTER_SETS = [
    # First is used as default selection.
    [_('Unicode (recommended)'), 'utf-8'],
    ['ISO-8859-1',  'iso-8859-1' ],
    ['ISO-8859-2',  'iso-8859-2' ],
    ['ISO-8859-3',  'iso-8859-3' ],
    ['ISO-8859-4',  'iso-8859-4' ],
    ['ISO-8859-5',  'iso-8859-5' ],
    ['ISO-8859-6',  'iso-8859-6' ],
    ['ISO-8859-7',  'iso-8859-7' ],
    ['ISO-8859-8',  'iso-8859-8' ],
    ['ISO-8859-9',  'iso-8859-9' ],
    ['ISO-8859-10', 'iso-8859-10' ],
    ['ISO-8859-13', 'iso-8859-13' ],
    ['ISO-8859-14', 'iso-8859-14' ],
    ['ISO-8859-15', 'iso-8859-15' ],
    ['koi8_r',      'koi8_r',     ],
    ]

_CC = [
    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" '
    'title="Creative Commons License - By attribution" '
    'src="#PATH#images/somerights20.gif" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="#PATH#images/somerights20.gif" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="#PATH#images/somerights20.gif" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="#PATH#images/somerights20.gif" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'title="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'src="#PATH#images/somerights20.gif" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'title="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'src="#PATH#images/somerights20.gif" /></a>'
    ]

_COPY_OPTIONS = [
        _('Standard copyright'),
        _('Creative Commons - By attribution'),
        _('Creative Commons - By attribution, No derivations'),
        _('Creative Commons - By attribution, Share-alike'),
        _('Creative Commons - By attribution, Non-commercial'),
        _('Creative Commons - By attribution, Non-commercial, No derivations'),
        _('Creative Commons - By attribution, Non-commercial, Share-alike'),
        _('No copyright notice'),
        ]


wrapper = TextWrapper()
wrapper.break_log_words = True
wrapper.width = 20

# This list of characters defines which hexadecimal entity certain
# 'special characters' with be transformed into for valid HTML
# rendering.  The variety of quotes with spaces are to assist in
# appropriately typesetting curly quotes and apostrophes.
html_escape_table = {
    "&"  : "&#38;",
    ' "' : " &#8220;",
    '" ' : "&#8221; ",
    " '" : " &#8216;",
    "' " : "&#8217; ",
    "'s ": "&#8217;s ",
    '"'  : "&quot;",
    "'"  : "&apos;",
    ">"  : "&gt;",
    "<"  : "&lt;",
    }

# This command then defines the 'html_escape' option for escaping
# special characters for presentation in HTML based on the above list.
def html_escape(text):
    """Convert the text and replace some characters with a &# variant."""
    return ''.join([html_escape_table.get(c, c) for c in text])


class BasePage:
    """
    This the base class to write certain HTML pages.
    """

    def __init__(self, report, title, gid=None):
        """
        report - instance of NavWebReport
        title - text for the <title> tag
        gid - Gramps ID
        """

        self.report = report
        self.title_str = title
        self.gid = gid
        self.src_list = {}

        self.page_title = ""

        self.author = get_researcher().get_name()
        if self.author:
            self.author = self.author.replace(',,,', '')
        self.up = False

        # TODO. All of these attributes are not necessary, because we have
        # also the options in self.options.  Besides, we need to check which
        # are still required.
        options = report.options
        self.inc_download = options['incdownload']
        self.html_dir = options['target']
        self.copyright = options['cright']
        self.ext = options['ext']
        self.encoding = options['encoding']
        self.css = options['css']
        self.noid = options['nogid']
        self.linkhome = options['linkhome']
        self.showbirth = options['showbirth']
        self.showdeath = options['showdeath']
        self.showspouse = options['showspouse']
        self.showparents = options['showparents']
        self.showhalfsiblings = options['showhalfsiblings']
        self.use_intro = options['intronote'] != u""\
                    or options['introimg'] != u""
        self.use_contact = options['contactnote'] != u""\
                    or options['contactimg'] != u""
        self.use_gallery = options['gallery']
        self.header = options['headernote']
        self.footer = options['footernote']
        self.usegraph = options['graph']
        self.graphgens = options['graphgens']
        self.use_home = options['homenote'] != "" or \
                        options['homeimg'] != ""

    def copy_media(self, photo, store_ref=True):
        handle = photo.get_handle()
        if store_ref:
            lnk = (self.cur_fname, self.page_title, self.gid)
            # FIXME. Is it OK to add to the photo_list of report?
            photo_list = self.report.photo_list
            if handle in photo_list:
                if lnk not in photo_list[handle]:
                    photo_list[handle].append(lnk)
            else:
                photo_list[handle] = [lnk]

        ext = os.path.splitext(photo.get_path())[1]
        real_path = "%s/%s" % (self.build_path('images', handle), handle+ext)
        thumb_path = "%s/%s.png" % (self.build_path('thumb', handle), handle)
        return (real_path, thumb_path)

    def create_file(self, name):
        self.cur_fname = name + self.ext
        if self.report.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io, 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        else:
            page_name = os.path.join(self.html_dir, self.cur_fname)
            of = codecs.EncodedFile(open(page_name, "w"), 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        return of

    def build_path(self, dirroot, name, up=False):
        path = '%s/%s/%s' % (dirroot, name[0].lower(), name[1].lower())
        if up:
            path = '../../../' + path
        return path

    def build_path_fname(self, path, name, up=False):
        """
        Create a filename in a directory tree using the first to characters
        for the first two directory levels.  For example
        0/2/02c0d8f888f566ae95ffbdca64274b51
        """
        path = self.build_path(path, name, up)
        return path + '/' + name + self.ext

    def link_path(self, path, name):
        path = "%s/%s/%s" % (path, name[0].lower(), name[1].lower())
        return path + '/' + name + self.ext

    def create_link_file(self, path, name):
        """
        Create a file in a directory tree using the first to characters
        for the first two directory levels.  For example
        0/2/02c0d8f888f566ae95ffbdca64274b51
        """
        self.cur_fname = self.link_path(path, name)
        if self.report.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io, 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        else:
            dirname = os.path.join(self.html_dir,
                                   path, name[0].lower(), name[1].lower())
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            page_name = dirname + '/' + name + self.ext
            of = codecs.EncodedFile(open(page_name, "w"), 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        return of

    def close_file(self, of):
        if self.report.archive:
            tarinfo = tarfile.TarInfo(self.cur_fname)
            tarinfo.size = len(self.string_io.getvalue())
            tarinfo.mtime = time.time()
            if os.sys.platform != "win32":
                tarinfo.uid = os.getuid()
                tarinfo.gid = os.getgid()
            self.string_io.seek(0)
            self.report.archive.addfile(tarinfo, self.string_io)
            of.close()
        else:
            of.close()
        self.cur_fname = None

    def lnkfmt(self, text):
        """This creates an MD5 hex string to be used as filename."""
        return md5.new(text).hexdigest()

    def display_footer(self, of):
        of.write('</div>\n\n')          # Terminate div_content

        of.write('<div id="footer">\n')
        if self.footer:
            note = self.report.database.get_note_from_gramps_id(self.footer)
            of.write('\t<div id="user_footer">\n')
            of.write('\t\t<p>')
            of.write(note.get())
            of.write('</p>\n')
            of.write('\t</div>\n')

        if self.copyright == 0:
            of.write('\t<div id="copyright">\n')
            of.write('\t\t<p>')
            if self.author:
                year = time.localtime(time.time())[0]
                cright = _('&copy; %(year)d %(person)s') % {
                    'person' : self.author,
                    'year' : year }
                of.write('%s' % cright)
            of.write('</p>\n')
            of.write('\t</div>\n')
        elif self.copyright <= 6:
            of.write('\t<div id="copyright">')
            text = _CC[self.copyright-1]
            if self.up:
                text = text.replace('#PATH#', '../../../')
            else:
                text = text.replace('#PATH#', '')
            of.write(text)
            of.write('</div>\n')

        of.write('\t<div class="fullclear"></div>\n')
        of.write('</div>\n\n')
        of.write('</body>\n')
        of.write('</html>')

    def display_header(self, of, title):
        if self.up:
            path = "../../.."
        else:
            path = ""

        of.write('<!DOCTYPE html PUBLIC ')
        of.write('"-//W3C//DTD XHTML 1.0 Strict//EN" ')
        of.write('"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        of.write('<html xmlns="http://www.w3.org/1999/xhtml" ')
        xmllang = Utils.xml_lang()
        of.write('xml:lang="%s" lang="%s">\n\n' % (xmllang, xmllang))
        of.write('<head>\n')
        of.write('<title>%s - %s</title>\n' % (html_escape(self.title_str), html_escape(title)))
        of.write('<meta http-equiv="Content-Type" content="text/html; ')
        of.write('charset=%s" />\n' % self.encoding)
        # Link to narrative.css
        if path:
            of.write('<link href="%s/%s" ' % (path, _NARRATIVE))
        else:
            of.write('<link href="%s" ' % _NARRATIVE)
        of.write('rel="stylesheet" type="text/css" title="GRAMPS Style" media="screen" />\n')

        # Link to narrativePrint.css
        if path:
            of.write('<link href="%s/%s" ' % (path, _NARRATIVEPRINT))
        else:
            of.write('<link href="%s" ' % _NARRATIVEPRINT)
        of.write('rel="stylesheet" type="text/css" media="print" />\n')

        # Link to favicon.ico
        if path:
            of.write('<link href="%s/images/favicon.ico" rel="Shortcut Icon" />\n' % path)
        else:
            of.write('<link href="images/favicon.ico" rel="Shortcut Icon" />\n')
        of.write('<!-- %sId%s -->\n' % ('$', '$'))
        of.write('</head>\n\n')
        of.write('<body>\n')

        of.write('<div id="Header">\n')

        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)

        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % { 'date' : value }

        db = self.report.database
        if self.linkhome:
            home_person = db.get_default_person()
            if home_person:
                fname = self.build_path_fname('ppl', home_person.handle, self.up)
                home_person_url = fname
                home_person_name = home_person.get_primary_name().get_regular_name()
                msg += _('<br />for <a href="%s">%s</a>') % (home_person_url, home_person_name)

        of.write('\t<div id="GRAMPSinfo">%s</div>\n' % msg)
        of.write('\t<h1 id="SiteTitle">%s</h1>\n' % html_escape(self.title_str))
        if self.header:
            note = db.get_note_from_gramps_id(self.header)
            of.write('\t<p id="user_header">')
            of.write(note.get())
            of.write('</p>\n')
        of.write('</div>\n\n')

        of.write('<div id="Navigation">\n')
        of.write('\t<ol>\n')

        if self.use_home:
            index_page = "index"
            surname_page = "surnames"
            intro_page = "introduction"
        elif self.use_intro:
            index_page = ""
            surname_page = "surnames"
            intro_page = "index"
        else:
            index_page = ""
            surname_page = "index"
            intro_page = ""

        # Define 'self.currentsection' to correctly set navlink item CSS id
        # 'CurrentSection' for Navigation styling.
        # Use 'self.cur_fname' to determine 'CurrentSection' for individual
        # elements for Navigation styling.

        # TODO. This currentsection can be better determined from the caller
        # of display_header. Notice that the caller uses a language translation
        # of the title.
        if self.use_home:
            self.show_navlink(of, index_page, _('Home'), path, title)
        if self.use_intro:
            self.show_navlink(of, intro_page, _('Introduction'), path, title)
        self.show_navlink(of, surname_page, _('Surnames'), path, title)
        self.show_navlink(of, 'individuals', _('Individuals'), path, title)
        self.show_navlink(of, 'sources', _('Sources'), path, title)
        self.show_navlink(of, 'places', _('Places'), path, title)
        if self.use_gallery:
            self.show_navlink(of, 'gallery', _('Gallery'), path, title)
        if self.inc_download:
            self.show_navlink(of, 'download', _('Download'), path, title)
        if self.use_contact:
            self.show_navlink(of, 'contact', _('Contact'),  path, title)

        of.write('\t</ol>\n')
        of.write('</div>\n\n')

        self.start_div_content(of, self.cur_fname)

    def start_div_content(self, of, fname):
        """
        Give unique ID to 'content' div for styling specific sections separately.
        Because of how this script was originally written, the appropriate section
        ID is determined by looking for a directory or HTML file name to associate
        with that section.
        """

        if "index" in fname:
            divid = "Home"
        elif "introduction" in fname:
            divid = "Introduction"
        elif "surnames" in fname:
            divid = "Surnames"
        elif "srn" in fname:
            divid = "SurnameDetail"
        elif "individuals" in fname:
            divid = "Individuals"
        elif "ppl" in fname:
            divid = "IndividualDetail"
        elif "sources" in fname:
            divid = "Sources"
        elif "src" in fname:
            divid = "SourceDetail"
        elif "places" in fname:
            divid = "Places"
        elif "plc" in fname:
            divid = "PlaceDetail"
        elif "gallery" in fname:
            divid = "Gallery"
        elif "img" in fname:
            divid = "GalleryDetail"
        elif "download" in fname:
            divid = "Download"
        elif "contact" in fname:
            divid = "Contact"
        else:
            divid = ''

        if divid:
            divid = ' id="%s"' % divid
        of.write('<div%s class="content">\n' % divid)

    def show_link(self, of, lpath, title, path):
        if path:
            lpath = path + '/' + lpath
        of.write('<a href="%s%s">%s</a>\n' % (lpath, self.ext, title))

    # TODO. Move this logic to a higher level (caller of display_header).
    def show_navlink(self, of, lpath, title, path, currentsection):
        if path:
            lpath = path + '/' + lpath

        # Figure out if we need <li id="CurrentSection"> of just plain <li>
        cs = False
        if currentsection == title:
            cs = True
        elif title == "Surnames":
            if "srn" in self.cur_fname:
                cs = True
            elif "Surnames" in currentsection:
                cs = True
        elif title == "Individuals":
            if "ppl" in self.cur_fname:
                cs = True
        elif title == "Sources":
            if "src" in self.cur_fname:
                cs = True
        elif title == "Places":
            if "plc" in self.cur_fname:
                cs = True
        elif title == "Gallery":
            if "img" in self.cur_fname:
                cs = True

        cs = cs and ' id="CurrentSection"' or ''
        of.write('\t\t<li%s><a href="%s%s">%s</a></li>\n' % (cs, lpath, self.ext, title))

    def display_first_image_as_thumbnail( self, of, photolist=None):
        if not photolist or not self.use_gallery:
            return

        photo_handle = photolist[0].get_reference_handle()
        photo = self.report.database.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        if mime_type:
            try:
                (real_path, newpath) = self.copy_media(photo)
                of.write('\t<div class="snapshot">\n')
                self.media_link(of, photo_handle, newpath, '', up=True)
                of.write('\t</div>\n\n')
            except (IOError, OSError), msg:
                WarningDialog(_("Could not add photo to page"), str(msg))
        else:
            of.write('\t<div class="snapshot">\n')
            descr = " ".join(wrapper.wrap(photo.get_description()))
            self.doc_link(of, photo_handle, descr, up=True)
            of.write('\t</div>\n\n')

            lnk = (self.cur_fname, self.page_title, self.gid)
            # FIXME. Is it OK to add to the photo_list of report?
            photo_list = self.report.photo_list
            if photo_handle in photo_list:
                if lnk not in photo_list[photo_handle]:
                    photo_list[photo_handle].append(lnk)
            else:
                photo_list[photo_handle] = [lnk]

    def display_additional_images_as_gallery( self, of, photolist=None):
        if not photolist or not self.use_gallery:
            return

        db = self.report.database
        of.write('\t<div id="indivgallery" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Gallery'))
        for mediaref in photolist:
            photo_handle = mediaref.get_reference_handle()
            photo = db.get_object_from_handle(photo_handle)
            mime_type = photo.get_mime_type()
            title = photo.get_description()
            if title == "":
                title = "(untitled)"
            if mime_type:
                try:
                    (real_path, newpath) = self.copy_media(photo)
                    descr = " ".join(wrapper.wrap(title))
                    self.media_link(of, photo_handle, newpath, descr, up=True)
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))
            else:
                try:
                    descr = " ".join(wrapper.wrap(title))
                    self.doc_link(of, photo_handle, descr, up=True)

                    lnk = (self.cur_fname, self.page_title, self.gid)
                    # FIXME. Is it OK to add to the photo_list of report?
                    photo_list = self.report.photo_list
                    if photo_handle in photo_list:
                        if lnk not in photo_list[photo_handle]:
                            photo_list[photo_handle].append(lnk)
                    else:
                        photo_list[photo_handle] = [lnk]
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        of.write('\t\t<div class="fullclear"></div>\n')
        of.write('\t</div>\n\n')

    def display_note_list(self, of, notelist=None):
        if not notelist:
            return

        db = self.report.database
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            format = note.get_format()
            text = note.get()
            try:
                text = unicode(text)
            except UnicodeDecodeError:
                text = unicode(str(text), errors='replace')

            if text:
                of.write('\t<div id="narrative" class="subsection">\n')
                of.write('\t\t<h4>%s</h4>\n' % _('Narrative'))
                if format:
                    text = u"<pre>%s</pre>" % text
                else:
                    text = u"</p>\n\t\t<p>".join(text.split("\n"))
                of.write('\t\t<p>%s</p>\n' % text)
                of.write('\t</div>\n\n')

    def display_url_list(self, of, urllist=None):
        if not urllist:
            return
        of.write('\t<div id="weblinks" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Weblinks'))
        of.write('\t\t<ol>\n')

        index = 1
        for url in urllist:
            uri = url.get_path()
            descr = url.get_description()
            if not descr:
                descr = uri
            if url.get_type() == gen.lib.UrlType.EMAIL and not uri.startswith("mailto:"):
                of.write('\t\t\t<li><a href="mailto:%s">%s</a>' % (uri, descr))
            elif url.get_type() == gen.lib.UrlType.WEB_HOME and not uri.startswith("http://"):
                of.write('\t\t\t<li><a href="http://%s">%s</a>' % (uri, descr))
            elif url.get_type() == gen.lib.UrlType.WEB_FTP and not uri.startswith("ftp://"):
                of.write('\t\t\t<li><a href="ftp://%s">%s</a>' % (uri, descr))
            else:
                of.write('\t\t\t<li><a href="%s">%s</a>' % (uri, descr))
            of.write('</li>\n')
            index = index + 1
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n\n')

    # Only used in IndividualPage.display_ind_sources
    # and MediaPage.display_media_sources
    def display_source_refs(self, of, bibli):
        if bibli.get_citation_count() == 0:
            return

        db = self.report.database
        of.write('\t<div id="sourcerefs" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Source References'))
        of.write('\t\t<ol>\n')

        cindex = 0
        for citation in bibli.get_citation_list():
            cindex += 1
            # Add this source to the global list of sources to be displayed
            # on each source page.
            lnk = (self.cur_fname, self.page_title, self.gid)
            shandle = citation.get_source_handle()
            if shandle in self.src_list:
                if lnk not in self.src_list[shandle]:
                    self.src_list[shandle].append(lnk)
            else:
                self.src_list[shandle] = [lnk]

            # Add this source and its references to the page
            source = db.get_source_from_handle(shandle)
            title = source.get_title()
            of.write('\t\t\t<li><a name="sref%d"' % cindex)
            self.source_link(of, source.handle, title, source.gramps_id, True)

            of.write('\n')
            of.write('\t\t\t\t<ol>\n')
            for key, sref in citation.get_ref_list():

                tmp = []
                confidence = Utils.confidence.get(sref.confidence, _('Unknown'))
                if confidence == _('Normal'):
                    confidence = None
                for (label, data) in [(_('Date'), _dd.display(sref.date)),
                                      (_('Page'), sref.page),
                                      (_('Confidence'), confidence)]:
                    if data:
                        tmp.append("%s: %s" % (label, data))
                notelist = sref.get_note_list()
                for notehandle in notelist:
                    note = db.get_note_from_handle(notehandle)
                    tmp.append("%s: %s" % (_('Text'), note.get()))
                if len(tmp) > 0:
                    of.write('\t\t\t\t\t<li><a name="sref%d%s">' % (cindex, key))
                    of.write('; &nbsp; '.join(tmp))
                    of.write('</a></li>\n')
            of.write('\t\t\t\t</ol>\n')
            of.write('\t\t\t</li>\n')
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n\n')

    def display_references(self, of, handlelist):
        if not handlelist:
            return

        of.write('\t<div id="references" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('References'))
        of.write('\t\t<ol>\n')

        sortlist = sorted(handlelist,
                          key = operator.itemgetter(1),
                          cmp = locale.strcoll)

        index = 1
        for (path, name, gid) in sortlist:
            of.write('\t\t\t<li>')
            self.person_link(of, "../../../" + path, name, gid)
            of.write('</li>\n')
            index = index + 1
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n')

    def person_link(self, of, path, name, gid=None):
        of.write('<a href="%s">%s' % (path, name))
        if not self.noid and gid:
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def surname_link(self, of, name, opt_val=None, up=False):
        handle = self.lnkfmt(name)
        dirpath = self.build_path('srn', handle, up)
        of.write('<a href="%s/%s%s">%s' % (dirpath, handle, self.ext, name))
        if opt_val != None:
            of.write('&nbsp;(%d)' % opt_val)
        of.write('</a>')

    def galleryNav_link(self, of, handle, name, up=False):
        dirpath = self.build_path('img', handle, up)
        of.write('<a id="%s" href="%s/%s%s">%s</a>' % (html_escape(name), dirpath, handle, self.ext, html_escape(name)))

    def media_ref_link(self, of, handle, name, up=False):
        dirpath = self.build_path('img', handle, up)
        of.write('<a href="%s/%s%s">%s</a>' % (dirpath, handle, self.ext, html_escape(name)))

    def media_link(self, of, handle, path, name, up, usedescr=True):
        dirpath = self.build_path('img', handle, up)
        of.write('\t\t<div class="thumbnail">\n')
        of.write('\t\t\t<a href="%s/%s%s">' % (dirpath, handle, self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a>\n' % name)
        if usedescr:
            of.write('\t\t\t<p>%s</p>\n' % html_escape(name))
        of.write('\t\t</div>\n')

    def doc_link(self, of, handle, name, up, usedescr=True):
        path = os.path.join('images', 'document.png')
        dirpath = self.build_path('img', handle, up)
        of.write('\t\t<div class="thumbnail">\n')
        of.write('\t\t\t<a href="%s/%s%s">' % (dirpath, handle, self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a>\n' % html_escape(name))
        if usedescr:
            of.write('\t\t\t<p>%s</p>\n' % html_escape(name))
        of.write('\t\t</div>\n')

    def source_link(self, of, handle, name, gid="", up=False):
        dirpath = self.build_path('src', handle, up)
        of.write(' href="%s/%s%s">%s' % (dirpath, handle, self.ext, html_escape(name)))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link(self, of, handle, name, gid="", up=False):
        dirpath = self.build_path('plc', handle, up)
        of.write('<a href="%s/%s%s">%s' % (dirpath, handle, self.ext, html_escape(name)))

        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link_str(self, handle, name, gid="", up=False):
        dirpath = self.build_path('plc', handle, up)
        retval = '<a href="%s/%s%s">%s' % (dirpath, handle, self.ext, html_escape(name))

        if not self.noid and gid != "":
            retval = retval + '&nbsp;<span class="grampsid">[%s]</span>' % gid
        return retval + '</a>'

class IndividualListPage(BasePage):

    def __init__(self, report, title, person_handle_list):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.create_file("individuals")
        self.display_header(of, _('Individuals'))

        msg = _("This page contains an index of all the individuals in the "
                "database, sorted by their last names. Selecting the person&#8217;s "
                "name will take you to that person&#8217;s individual page.")

        of.write('\t<h2>%s</h2>\n' % _('Individuals'))
        of.write('\t<p id="description">%s</p>\n' % msg)
        of.write('\t<table class="infolist individuallist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnSurname">%s</th>\n' % _('Surname'))
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        column_count = 2
        if self.showbirth:
            of.write('\t\t\t<th class="ColumnBirth">%s</th>\n' % _('Birth'))
            column_count += 1
        if self.showdeath:
            of.write('\t\t\t<th class="ColumnDeath">%s</th>\n' % _('Death'))
            column_count += 1
        if self.showspouse:
            of.write('\t\t\t<th class="ColumnPartner">%s</th>\n' % _('Partner'))
            column_count += 1
        if self.showparents:
            of.write('\t\t\t<th class="ColumnParents">%s</th>\n' % _('Parents'))
            column_count += 1
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')

        person_handle_list = sort_people(db, person_handle_list)

        for (surname, handle_list) in person_handle_list:
            first = True
            for person_handle in handle_list:
                person = db.get_person_from_handle(person_handle)

                # surname column
                if first:
                    of.write('\t\t<tr class="BeginSurname">\n')
                    of.write('\t\t\t<td class="ColumnSurname"><a name="%s">%s</a>' % (self.lnkfmt(surname), surname))
                else:
                    of.write('\t\t<tr>\n')
                    of.write('\t\t\t<td class="ColumnSurname">&nbsp;')
                of.write('</td>\n')

                # firstname column
                of.write('\t\t\t<td class="ColumnName">')
                fname = self.build_path_fname('ppl', person.handle)
                self.person_link(of, fname,
                                 _nd.display_given(person), person.gramps_id)
                of.write('</td>\n')

                # birth column
                if self.showbirth:
                    of.write('\t\t\t<td class="ColumnBirth">')
                    birth = ReportUtils.get_birth_or_fallback(db, person)
                    if birth:
                        if birth.get_type() == gen.lib.EventType.BIRTH:
                            of.write(_dd.display(birth.get_date_object()))
                        else:
                            of.write('<em>')
                            of.write(_dd.display(birth.get_date_object()))
                            of.write('</em>')
                    of.write('</td>\n')

                # death column
                if self.showdeath:
                    of.write('\t\t\t<td class="ColumnDeath">')
                    death = ReportUtils.get_death_or_fallback(db, person)
                    if death:
                        if death.get_type() == gen.lib.EventType.DEATH:
                            of.write(_dd.display(death.get_date_object()))
                        else:
                            of.write('<em>')
                            of.write(_dd.display(death.get_date_object()))
                            of.write('</em>')
                    of.write('</td>\n')

                # spouse (partner) column
                if self.showspouse:
                    of.write('\t\t\t<td class="ColumnPartner">')
                    family_list = person.get_family_handle_list()
                    first_family = True
                    spouse_name = None
                    if family_list:
                        for family_handle in family_list:
                            family = db.get_family_from_handle(family_handle)
                            spouse_id = ReportUtils.find_spouse(person, family)
                            if spouse_id:
                                spouse = db.get_person_from_handle(spouse_id)
                                spouse_name = spouse.get_primary_name().get_regular_name()
                                if not first_family:
                                    of.write(', ')
                                of.write('%s' % spouse_name)
                                first_family = False
                    of.write('</td>\n')

                # parents column
                if self.showparents:
                    of.write('\t\t\t<td class="ColumnParents">')
                    parent_handle_list = person.get_parent_family_handle_list()
                    if parent_handle_list:
                        parent_handle = parent_handle_list[0]
                        family = db.get_family_from_handle(parent_handle)
                        father_name = ''
                        mother_name = ''
                        father_id = family.get_father_handle()
                        mother_id = family.get_mother_handle()
                        father = db.get_person_from_handle(father_id)
                        mother = db.get_person_from_handle(mother_id)
                        if father:
                            father_name = father.get_primary_name().get_regular_name()
                        if mother:
                            mother_name = mother.get_primary_name().get_regular_name()
                        if mother and father:
                            of.write('<span class="father fatherNmother">%s</span> <span class="mother">%s</span>' % (father_name, mother_name))
                        elif mother:
                            of.write('<span class="mother">%s</span>' % mother_name)
                        elif father:
                            of.write('<span class="father">%s</span>' % father_name)
                    of.write('</td>\n')

                # finished writing all columns
                of.write('\t\t</tr>\n')
                first = False

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class SurnamePage(BasePage):

    def __init__(self, report, title, surname, person_handle_list):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.create_link_file('srn', self.lnkfmt(surname))
        self.up = True
        self.display_header(of, "%s - %s" % (_('Surname'), surname))

        msg = _("This page contains an index of all the individuals in the "
                "database with the surname of %s. Selecting the person&#8217;s name "
                "will take you to that person&#8217;s individual page.") % surname

        of.write('\t<h2>%s:</h2>\n' % _('Surnames'))
        of.write('\t<h3>%s</h3>\n' % html_escape(surname))
        of.write('\t<p id="description">%s</p>\n' % msg)
        of.write('\t<table class="infolist surname">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        if self.showbirth:
            of.write('\t\t\t<th class="ColumnBirth">%s</th>\n' % _('Birth'))
        if self.showdeath:
            of.write('\t\t\t<th class="ColumnDeath">%s</th>\n' % _('Death'))
        if self.showspouse:
            of.write('\t\t\t<th class="ColumnPartner">%s</th>\n' % _('Partner'))
        if self.showparents:
            of.write('\t\t\t<th class="ColumnParents">%s</th>\n' % _('Parents'))
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')

        for person_handle in person_handle_list:

            # firstname column
            person = db.get_person_from_handle(person_handle)
            of.write('\t\t<tr>\n')
            of.write('\t\t\t<td class="ColumnName">')
            fname = self.build_path_fname('ppl', person.handle, True)
            self.person_link(of, fname,
                             person.get_primary_name().get_first_name(),
                             person.gramps_id)
            of.write('</td>\n')

            # birth column
            if self.showbirth:
                of.write('\t\t\t<td class="ColumnBirth">')
                birth = ReportUtils.get_birth_or_fallback(db, person)
                if birth:
                    if birth.get_type() == gen.lib.EventType.BIRTH:
                        of.write(_dd.display(birth.get_date_object()))
                    else:
                        of.write('<em>')
                        of.write(_dd.display(birth.get_date_object()))
                        of.write('</em>')
                of.write('</td>\n')

            # death column
            if self.showdeath:
                of.write('\t\t\t<td class="ColumnDeath">')
                death = ReportUtils.get_death_or_fallback(db, person)
                if death:
                    if death.get_type() == gen.lib.EventType.DEATH:
                        of.write(_dd.display(death.get_date_object()))
                    else:
                        of.write('<em>')
                        of.write(_dd.display(death.get_date_object()))
                        of.write('</em>')
                of.write('</td>\n')

            # spouse (partner) column
            if self.showspouse:
                of.write('\t\t\t<td class="ColumnPartner">')
                family_list = person.get_family_handle_list()
                first_family = True
                spouse_name = None
                if family_list:
                    for family_handle in family_list:
                        family = db.get_family_from_handle(family_handle)
                        spouse_id = ReportUtils.find_spouse(person, family)
                        if spouse_id:
                            spouse = db.get_person_from_handle(spouse_id)
                            spouse_name = spouse.get_primary_name().get_regular_name()
                            if not first_family:
                                of.write(', ')
                            of.write('%s' % spouse_name)
                            first_family = False
                of.write('</td>\n')

            # parents column
            if self.showparents:
                of.write('\t\t\t<td class="ColumnParents">')
                parent_handle_list = person.get_parent_family_handle_list()
                if parent_handle_list:
                    parent_handle = parent_handle_list[0]
                    family = db.get_family_from_handle(parent_handle)
                    father_name = ''
                    mother_name = ''
                    father_id = family.get_father_handle()
                    mother_id = family.get_mother_handle()
                    father = db.get_person_from_handle(father_id)
                    mother = db.get_person_from_handle(mother_id)
                    if father:
                        father_name = father.get_primary_name().get_regular_name()
                    if mother:
                        mother_name = mother.get_primary_name().get_regular_name()
                    if mother and father:
                        of.write('<span class="father fatherNmother">%s</span> <span class="mother">%s</span>' % (father_name, mother_name))
                    elif mother:
                        of.write('<span class="mother">%s</span>' % mother_name)
                    elif father:
                        of.write('<span class="father">%s</span>' % father_name)
                of.write('</td>\n')

            # finished writing all columns
            of.write('\t\t</tr>\n')
        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class PlaceListPage(BasePage):

    def __init__(self, report, title, place_handles, src_list):
        BasePage.__init__(self, report, title)
        self.src_list = src_list        # TODO verify that this is correct

        db = report.database
        of = self.create_file("places")
        self.display_header(of, _('Places'))

        msg = _("This page contains an index of all the places in the "
                "database, sorted by their title. Clicking on a place&#8217;s "
                "title will take you to that place&#8217;s page.")

        of.write('\t<h2>%s</h2>\n' % _('Places'))
        of.write('\t<p id="description">%s</p>\n' % msg )

        of.write('\t<table class="infolist placelist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnLetter">%s</th>\n' % _('Letter'))
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n\n')

        sort = Sort.Sort(db)
        handle_list = place_handles.keys()
        handle_list.sort(sort.by_place_title)
        last_letter = ''

        for handle in handle_list:
            place = db.get_place_from_handle(handle)
            n = ReportUtils.place_name(db, handle)

            if not n or len(n) == 0:
                continue

            letter = normalize('NFD', n)[0].upper()

            if letter != last_letter:
                last_letter = letter
                of.write('\t\t<tr class="BeginLetter">\n')
                of.write('\t\t\t<td class="ColumnLetter">%s</td>\n' % last_letter)
                of.write('\t\t\t<td class="ColumnName">')
                self.place_link(of, place.handle, n, place.gramps_id)
                of.write('</td>\n')
                of.write('\t\t</tr>\n')
            else:
                of.write('\t\t<tr>\n')
                of.write('\t\t\t<td class="ColumnLetter">&nbsp;</td>\n')
                of.write('\t\t\t<td class="ColumnName">')
                self.place_link(of, place.handle, n, place.gramps_id)
                of.write('</td>\n')
                of.write('\t\t</tr>\n')

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class PlacePage(BasePage):

    def __init__(self, report, title, place_handle, src_list, place_list):
        db = report.database
        place = db.get_place_from_handle(place_handle)
        BasePage.__init__(self, report, title, place.gramps_id)
        self.src_list = src_list        # TODO verify that this is correct

        of = self.create_link_file('plc', place.get_handle())
        self.page_title = ReportUtils.place_name(db, place_handle)
        self.up = True
        self.display_header(of, "%s - %s" % (_('Places'), self.page_title))

        media_list = place.get_media_list()
        self.display_first_image_as_thumbnail(of, media_list)

        of.write('\t<h2>Places:</h2>\n')
        of.write('\t<h3>%s</h3>\n\n' % html_escape(self.page_title.strip()))
        of.write('\t<div id="summaryarea">\n')
        of.write('\t\t<table class="infolist place">\n')

        if not self.noid:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('GRAMPS ID'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % place.gramps_id)
            of.write('\t\t\t</tr>\n')

        if place.main_loc:
            ml = place.main_loc
            for val in [(_('Street'), ml.street),
                        (_('City'), ml.city),
                        (_('Church Parish'), ml.parish),
                        (_('County'), ml.county),
                        (_('State/Province'), ml.state),
                        (_('Postal Code'), ml.postal),
                        (_('Country'), ml.country)]:
                if val[1]:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % val[0])
                    of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % val[1])
                    of.write('\t\t\t</tr>\n')

        if place.long:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Longitude'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % place.long)
            of.write('\t\t\t</tr>\n')

        if place.lat:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Latitude'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % place.lat)
            of.write('\t\t\t</tr>\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n')

        if self.use_gallery:
            self.display_additional_images_as_gallery(of, media_list)
        self.display_note_list(of, place.get_note_list())
        self.display_url_list(of, place.get_url_list())
        self.display_references(of, place_list[place.handle])

        self.display_footer(of)
        self.close_file(of)

class MediaPage(BasePage):

    def __init__(self, report, title, handle, src_list, my_media_list, info):
        (prev, next, page_number, total_pages) = info
        db = report.database
        photo = db.get_object_from_handle(handle)
        # TODO. How do we pass my_media_list down for use in BasePage?
        BasePage.__init__(self, report, title, photo.gramps_id)
        of = self.create_link_file('img', handle)

        self.src_list = src_list
        self.bibli = Bibliography()

        mime_type = photo.get_mime_type()

        if mime_type:
            note_only = False
            newpath = self.copy_source_file(handle, photo)
            target_exists = newpath != None
        else:
            note_only = True
            target_exists = False

        self.copy_thumbnail(handle, photo)
        self.page_title = photo.get_description()
        self.up = True
        self.display_header(of, "%s - %s" % (_('Gallery'), self.page_title))

        of.write('\t<h2>%s:</h2>\n' % _('Gallery'))

        # gallery navigation
        of.write('\t<div id="GalleryNav">\n')
        of.write('\t\t')
        if prev:
            self.galleryNav_link(of, prev, _('Previous'), True)
        data = _('<strong id="GalleryCurrent">%(page_number)d</strong> of <strong id="GalleryTotal">%(total_pages)d</strong>' ) % {
            'page_number' : page_number, 'total_pages' : total_pages }
        of.write(' <span id="GalleryPages">%s</span> ' % data)
        if next:
            self.galleryNav_link(of, next, _('Next'), True)
        of.write('\n')
        of.write('\t</div>\n\n')

        of.write('\t<div id="summaryarea">\n')
        if mime_type:
            if mime_type.startswith("image/"):
                of.write('\t\t<div id="GalleryDisplay">\n')
                if target_exists:
                    # if the image is spectacularly large, then force the client
                    # to resize it, and include a "<a href=" link to the actual
                    # image; most web browsers will dynamically resize an image
                    # and provide zoom-in/zoom-out functionality when the image
                    # is displayed directly
                    (width, height) = ImgManip.image_size(
                            Utils.media_path_full(db, photo.get_path()))
                    scale = 1.0
                    of.write('\t\t\t')
                    if width > _MAX_IMG_WIDTH or height > _MAX_IMG_HEIGHT:
                        # image is too large -- scale it down and link to the full image
                        scale = min(float(_MAX_IMG_WIDTH)/float(width), float(_MAX_IMG_HEIGHT)/float(height))
                        width = int(width * scale)
                        height = int(height * scale)
                        of.write('<a href="../../../%s">' % newpath)
                    of.write('<img width="%d" height="%d" src="../../../%s" alt="%s" />' % (width, height, newpath, html_escape(self.page_title)))
                    if scale != 1.0:
                        of.write('</a>')
                    of.write('\n')

                else:
                    of.write('\t\t\t<span class="MissingImage">(%s)</span>' % _("The file has been moved or deleted"))
                of.write('\t\t</div>\n\n')
            else:
                import tempfile

                dirname = tempfile.mkdtemp()
                thmb_path = os.path.join(dirname, "temp.png")
                if ThumbNails.run_thumbnailer(mime_type,
                                              Utils.media_path_full(db,
                                                            photo.get_path()),
                                              thmb_path, 320):
                    try:
                        path = "%s/%s.png" % (self.build_path("preview", photo.handle), photo.handle)
                        self.report.store_file(thmb_path, path)
                        os.unlink(thmb_path)
                    except IOError:
                        path = os.path.join('images', 'document.png')
                else:
                    path = os.path.join('images', 'document.png')
                os.rmdir(dirname)

                of.write('\t\t<div id="GalleryDisplay">\n')
                if target_exists:
                    of.write('\t\t\t<a href="../../../%s" alt="%s" />\n' % (newpath, html_escape(self.page_title)))
                of.write('\t\t\t\t<img src="../../../%s" alt="%s" />\n' % (path, html_escape(self.page_title)))
                if target_exists:
                    of.write('\t\t\t</a>\n')
                else:
                    of.write('\t\t\t<span class="MissingImage">(%s)</span>' % _("The file has been moved or deleted"))
                of.write('\t\t</div>\n\n')
        else:
            path = os.path.join('images', 'document.png')
            of.write('\t\t<div id="GalleryDisplay">\n')
            of.write('\t\t\t<img src="../../../%s" alt="%s" />\n' % (path, html_escape(self.page_title)))
            of.write('\t\t</div>\n\n')

        of.write('\t\t<h3>%s</h3>\n' % html_escape(self.page_title.strip()))
        of.write('\t\t<table class="infolist gallery">\n')

        if not self.noid:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('GRAMPS ID'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % photo.gramps_id)
            of.write('\t\t\t</tr>\n')

        if not note_only and not mime_type.startswith("image/"):
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('File type'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % Mime.get_description(mime_type))
            of.write('\t\t\t</tr>\n')

        date = _dd.display(photo.get_date_object())
        if date != "":
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Date'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % date)
            of.write('\t\t\t</tr>\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

        self.display_note_list(of, photo.get_note_list())
        self.display_attr_list(of, photo.get_attribute_list())
        self.display_media_sources(of, photo)
        self.display_references(of, my_media_list)

        self.display_footer(of)
        self.close_file(of)

    def display_media_sources(self, of, photo):
        for sref in photo.get_source_references():
            self.bibli.add_reference(sref)
        self.display_source_refs(of, self.bibli)

    def display_attr_list(self, of, attrlist=None):
        if not attrlist:
            return
        of.write('\t<div id="attributes">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Attributes'))
        of.write('\t\t<table class="infolist">\n')

        for attr in attrlist:
            atType = str( attr.get_type() )
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % atType)
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % attr.get_value())
            of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def copy_source_file(self, handle, photo):
        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.build_path('images', handle)
        newpath = to_dir + "/" + handle + ext

        db = self.report.database
        fullpath = Utils.media_path_full(db, photo.get_path())
        try:
            if self.report.archive:
                self.report.archive.add(fullpath, str(newpath))
            else:
                to_dir = os.path.join(self.html_dir, to_dir)
                if not os.path.isdir(to_dir):
                    os.makedirs(to_dir)
                shutil.copyfile(fullpath,
                                os.path.join(self.html_dir, newpath))
            return newpath
        except (IOError, OSError), msg:
            error = _("Missing media object:") +                               \
                     "%s (%s)" % (photo.get_description(), photo.get_gramps_id())
            WarningDialog(error, str(msg))
            return None

    def copy_thumbnail(self, handle, photo):
        to_dir = self.build_path('thumb', handle)
        to_path = os.path.join(to_dir, handle+".png")
        if photo.get_mime_type():
            db = self.report.database
            from_path = ThumbNails.get_thumbnail_path(Utils.media_path_full(
                                                            db,
                                                            photo.get_path()),
                                                      photo.get_mime_type())
            if not os.path.isfile(from_path):
                from_path = os.path.join(const.IMAGE_DIR, "document.png")
        else:
            from_path = os.path.join(const.IMAGE_DIR, "document.png")

        # FIXME. Why not use copy_file()?
        if self.report.archive:
            self.report.archive.add(from_path, to_path)
        else:
            to_dir = os.path.join(self.html_dir, to_dir)
            dest = os.path.join(self.html_dir, to_path)
            if not os.path.isdir(to_dir):
                os.makedirs(to_dir)
            try:
                shutil.copyfile(from_path, dest)
            except IOError:
                print "Could not copy file"

class SurnameListPage(BasePage):
    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1

    def __init__(self, report, title, person_handle_list, order_by=ORDER_BY_NAME, filename="surnames"):
        BasePage.__init__(self, report, title)
        db = report.database
        if order_by == self.ORDER_BY_NAME:
            of = self.create_file(filename)
            self.display_header(of, _('Surnames'))
            of.write('\t<h2>%s</h2>\n' % _('Surnames'))
        else:
            of = self.create_file("surnames_count")
            self.display_header(of, _('Surnames by person count'))
            of.write('\t<h2>%s</h2>\n' % _('Surnames by person count'))

        of.write('\t<p id="description">%s</p>\n' % _(
            'This page contains an index of all the '
            'surnames in the database. Selecting a link '
            'will lead to a list of individuals in the '
            'database with this same surname.'))

        if order_by == self.ORDER_BY_COUNT:
            of.write('\t<table id="SortByCount" class="infolist surnamelist">\n')
            of.write('\t<thead>\n')
            of.write('\t\t<tr>\n')
        else:
            of.write('\t<table id="SortByName" class="infolist surnamelist">\n')
            of.write('\t<thead>\n')
            of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnLetter">%s</th>\n' % _('Letter'))

        if not self.use_home and not self.use_intro:
            of.write('\t\t\t<th class="ColumnSurname"><a href="%s%s">%s</a></th>\n' % ("index", self.ext,  _('Surname')))
        else:
            of.write('\t\t\t<th class="ColumnSurname"><a href="%s%s">%s</a></th>\n' % ("surnames", self.ext, _('Surname')))
        of.write('\t\t\t<th class="ColumnQuantity"><a href="%s%s">%s</a></th>\n' % ("surnames_count", self.ext, _('Number of people')))
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')

        person_handle_list = sort_people(db, person_handle_list)
        if order_by == self.ORDER_BY_COUNT:
            temp_list = {}
            for (surname, data_list) in person_handle_list:
                index_val = "%90d_%s" % (999999999-len(data_list), surname)
                temp_list[index_val] = (surname, data_list)
            temp_keys = temp_list.keys()
            temp_keys.sort()
            person_handle_list = []
            for key in temp_keys:
                person_handle_list.append(temp_list[key])

        last_letter = ''
        last_surname = ''

        for (surname, data_list) in person_handle_list:
            if len(surname) == 0:
                continue

            # Get a capital normalized version of the first letter of
            # the surname
            letter = normalize('NFD', surname)[0].upper()

            if letter != last_letter:
                last_letter = letter
                of.write('\t\t<tr class="BeginLetter">\n')
                of.write('\t\t\t<td class="ColumnLetter">%s</td>\n' % last_letter)
                of.write('\t\t\t<td class="ColumnSurname">')
                self.surname_link(of, surname)
                of.write('</td>\n')
            elif surname != last_surname:
                of.write('\t\t<tr>\n')
                of.write('\t\t\t<td class="ColumnLetter">&nbsp;</td>\n')
                of.write('\t\t\t<td class="ColumnSurname">')
                self.surname_link(of, surname)
                of.write('</td>\n')
                last_surname = surname
            of.write('\t\t\t<td class="ColumnQuantity">%d</td>\n' % len(data_list))
            of.write('\t\t</tr>\n')

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class IntroductionPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        if self.use_home:
            of = self.create_file("introduction")
        else:
            of = self.create_file("index")
        self.display_header(of, _('Introduction'))

        of.write('\t<h2>%s</h2>\n' % _('Introduction'))

        pic_id = report.options['introimg']
        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath, thumb_path) = self.copy_media(obj, False)
                    self.report.store_file(Utils.media_path_full(db,
                                                                 obj.get_path()),
                                    newpath)
                    of.write('\t<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />\n' % obj.get_description())
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        note_id = report.options['intronote']
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get()
            if note_obj.get_format():
                of.write('\t<pre>\n%s\n' % text)
                of.write('\t</pre>\n')
            else:
                of.write('\t<p>')
                of.write(u'</p>\n\t<p>'.join(text.split("\n")))
                of.write('</p>\n')

        self.display_footer(of)
        self.close_file(of)

class HomePage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.create_file("index")
        self.display_header(of, _('Home'))

        of.write('\t<h2>%s</h2>\n' % _('Home'))

        pic_id = report.options['homeimg']
        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath, thumb_path) = self.copy_media(obj, False)
                    self.report.store_file(Utils.media_path_full(db,
                                                                 obj.get_path()),
                                    newpath)
                    of.write('\t<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />\n' % obj.get_description())
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        note_id = report.options['homenote']
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get()
            if note_obj.get_format():
                of.write('\t<pre>\n%s\n' % text)
                of.write('\t</pre>\n')
            else:
                of.write('\t<p>')
                of.write(u'</p>\n\t<p>'.join(text.split("\n")))
                of.write('</p>\n')

        self.display_footer(of)
        self.close_file(of)

class SourcesPage(BasePage):

    def __init__(self, report, title, handle_set):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.create_file("sources")
        self.display_header(of, _('Sources'))

        handle_list = list(handle_set)
        source_dict = {}

        #Sort the sources
        for handle in handle_list:
            source = db.get_source_from_handle(handle)
            key = source.get_title() + str(source.get_gramps_id())
            source_dict[key] = (source, handle)
        keys = source_dict.keys()
        keys.sort(locale.strcoll)

        msg = _("This page contains an index of all the sources in the "
                "database, sorted by their title. Clicking on a source&#8217;s "
                "title will take you to that source&#8217;s page.")

        of.write('\t<h2>%s</h2>\n' % _('Sources'))
        of.write('\t<p id="description">')
        of.write(msg)
        of.write('</p>\n')
        of.write('\t<table class="infolist sourcelist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnLabel">&nbsp;</th>\n')
        of.write('\t\t\t<th class="ColumnName">Name</th>\n')
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')
        index = 1
        for key in keys:
            (source, handle) = source_dict[key]
            of.write('\t\t<tr>\n')
            of.write('\t\t\t<td class="ColumnRowLabel">%d.</td>\n' % index)
            of.write('\t\t\t<td class="ColumnName"><a ')
            self.source_link(of, handle, source.get_title(), source.gramps_id)
            of.write('</td>\n')
            of.write('\t\t</tr>\n')
            index += 1

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class SourcePage(BasePage):

    def __init__(self, report, title, handle, src_list):
        db = report.database
        source = db.get_source_from_handle( handle)
        BasePage.__init__(self, report, title, source.gramps_id)

        of = self.create_link_file('src', source.get_handle())
        self.page_title = source.get_title()
        self.up = True
        self.display_header(of, "%s - %s" % (_('Sources'), self.page_title))

        media_list = source.get_media_list()
        self.display_first_image_as_thumbnail(of, media_list)

        of.write('\t<h2>%s:</h2>\n' % _('Sources'))
        of.write('\t<h3>%s</h3>\n\n' % html_escape(self.page_title.strip()))
        of.write('\t<div id="summaryarea">\n')
        of.write('\t\t<table class="infolist source">\n')

        grampsid = None
        if not self.noid:
            grampsid = source.gramps_id

        for (label, val) in [(_('GRAMPS ID'), grampsid),
                            (_('Author'), source.author),
                            (_('Publication information'), source.pubinfo),
                            (_('Abbreviation'), source.abbrev)]:
            if val:
                of.write('\t\t\t<tr>\n')
                of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % label)
                of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % val)
                of.write('\t\t\t</tr>\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

        self.display_additional_images_as_gallery(of, media_list)
        self.display_note_list(of, source.get_note_list())
        self.display_references(of, src_list[source.handle])

        self.display_footer(of)
        self.close_file(of)

class GalleryPage(BasePage):

    def __init__(self, report, title, handle_set):
        BasePage.__init__(self, report, title)

        # TODO. What to do with handle_set?

        db = report.database
        of = self.create_file("gallery")
        self.display_header(of, _('Gallery'))

        of.write('\t<h2>%s</h2>\n\n' % _('Gallery'))
        of.write('\t<p id="description">')

        of.write(_("This page contains an index of all the media objects "
                   "in the database, sorted by their title. Clicking on "
                   "the title will take you to that media object&#8217;s page."))
        of.write('</p>\n\n')
        of.write('\t<table class="infolist gallerylist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnRowLabel">&nbsp;</th>\n')
        of.write('\t\t\t<th class="ColumnName">Name</th>\n')
        of.write('\t\t\t<th class="ColumnDate">Date</th>\n')
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')

        index = 1
        mlist = self.report.photo_list.keys()
        sort = Sort.Sort(db)
        mlist.sort(sort.by_media_title)
        for handle in mlist:
            media = db.get_object_from_handle(handle)
            date = _dd.display(media.get_date_object())
            title = media.get_description()
            if title == "":
                title = "untitled"
            of.write('\t\t<tr>\n')

            of.write('\t\t\t<td class="ColumnRowLabel">%d.</td>\n' % index)

            of.write('\t\t\t<td class="ColumnName">')
            self.media_ref_link(of, handle, title)
            of.write('</td>\n')

            of.write('\t\t\t<td class="ColumnDate">%s</td>\n' % date)

            of.write('\t\t</tr>\n')
            index += 1

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.display_footer(of)
        self.close_file(of)

class DownloadPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        of = self.create_file("download")
        self.display_header(of, _('Download'))

        of.write('\t<h2>%s</h2>\n\n' % _('Download'))

        self.display_footer(of)
        self.close_file(of)

class ContactPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.create_file("contact")
        self.display_header(of, _('Contact'))

        of.write('\t<h2>%s</h2>\n\n' % _('Contact'))
        of.write('\t<div id="summaryarea">\n')

        pic_id = report.options['contactimg']
        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath, thumb_path) = self.copy_media(obj, False)
                    self.report.store_file(Utils.media_path_full(db,
                                                                 obj.get_path()),
                                            newpath)
                    of.write('\t\t<img height="200" ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />\n' % obj.get_description())
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        r = get_researcher()

        of.write('\t\t<div id="researcher">\n')
        if r.name:
            of.write('\t\t\t<h3>%s</h3>\n' % r.name.replace(',,,', ''))
        if r.addr:
            of.write('\t\t\t<span id="streetaddress">%s</span>\n' % r.addr)
        text = "".join([r.city, r.state, r.postal])
        if text:
            of.write('\t\t\t<span id="city">%s</span>\n' % r.city)
            of.write('\t\t\t<span id="state">%s</span>\n' % r.state)
            of.write('\t\t\t<span id="postalcode">%s</span>\n' % r.postal)
        if r.country:
            of.write('\t\t\t<span id="country">%s</span>\n' % r.country)
        if r.email:
            of.write('\t\t\t<span id="email"><a href="mailto:%s?subject=from GRAMPS Web Site">%s</a></span>\n' % (r.email, r.email))
        of.write('\t\t</div>\n')
        of.write('\t\t<div class="fullclear"></div>\n')

        note_id = report.options['contactnote']
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get()
            if note_obj.get_format():
                text = u"\t\t<pre>%s</pre>" % text
            else:
                text = u"<br />".join(text.split("\n"))
            of.write('\t\t<p>%s</p>\n' % text)

        of.write('\t</div>\n')

        self.display_footer(of)
        self.close_file(of)

class IndividualPage(BasePage):
    """
    This class is used to write HTML for an individual.
    """

    gender_map = {
        gen.lib.Person.MALE    : _('male'),
        gen.lib.Person.FEMALE  : _('female'),
        gen.lib.Person.UNKNOWN : _('unknown'),
        }

    def __init__(self, report, title, person, ind_list, place_list, src_list):
        BasePage.__init__(self, report, title, person.gramps_id)
        self.person = person
        self.ind_list = ind_list
        self.src_list = src_list        # Used by get_citation_links()
        self.bibli = Bibliography()
        self.place_list = place_list
        self.sort_name = _nd.sorted(self.person)
        self.name = _nd.sorted(self.person)

        db = report.database
        of = self.create_link_file('ppl', person.handle)
        self.up = True
        self.display_header(of, self.sort_name)

        self.display_ind_general(of)
        self.display_ind_events(of)
        self.display_attr_list(of, self.person.get_attribute_list())
        self.display_ind_parents(of)
        self.display_ind_relationships(of)
        self.display_addresses(of)

        media_list = []
        photo_list = self.person.get_media_list()
        if len(photo_list) > 1:
            media_list = photo_list[1:]
        for handle in self.person.get_family_handle_list():
            family = db.get_family_from_handle(handle)
            media_list += family.get_media_list()
            for evt_ref in family.get_event_ref_list():
                event = db.get_event_from_handle(evt_ref.ref)
                media_list += event.get_media_list()
        for evt_ref in self.person.get_primary_event_ref_list():
            event = db.get_event_from_handle(evt_ref.ref)
            if event:
                media_list += event.get_media_list()

        self.display_additional_images_as_gallery(of, media_list)
        self.display_note_list(of, self.person.get_note_list())
        self.display_url_list(of, self.person.get_url_list())
        self.display_ind_sources(of)
        self.display_ind_pedigree(of)
        if self.usegraph:
            self.display_tree(of)

        self.display_footer(of)
        self.close_file(of)

    def display_attr_list(self, of, attrlist=None):
        if not attrlist:
            return
        of.write('\t<div id="attributes" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Attributes'))
        of.write('\t\t<table class="infolist">\n')

        for attr in attrlist:
            atType = str( attr.get_type() )
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % atType)
            value = attr.get_value()
            value += self.get_citation_links( attr.get_source_references() )
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % value)
            of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def draw_box(self, of, center, col, person):
        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)

        of.write('\t\t\t<div class="boxbg" style="top: %dpx; left: %dpx;">\n' % (top, xoff+1))
        of.write('\t\t\t\t<div class="box">')
        if person.handle in self.ind_list:
            person_name = _nd.display(person)
            fname = self.build_path_fname('ppl', person.handle, True)
            self.person_link(of, fname, person_name)
        else:
            of.write(_nd.display(person))
        of.write('</div>\n')
        of.write('\t\t\t</div>\n')
        of.write('\t\t\t<div class="shadow" style="top: %dpx; left: %dpx;"></div>\n' % (top+_SHADOW, xoff+_SHADOW))

    def extend_line(self, of, y0, x0):
        of.write('\t\t\t<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y0, x0, _HGAP/2))
        of.write('\t\t\t<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y0+_SHADOW, x0, _HGAP/2+_SHADOW))

    def connect_line(self, of, y0, y1, col):
        if y0 < y1:
            y = y0
        else:
            y = y1

        x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        of.write('\t\t\t<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1, x0, _HGAP/2))
        of.write('\t\t\t<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1+_SHADOW, x0+_SHADOW, _HGAP/2+_SHADOW))
        of.write('\t\t\t<div class="bhline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y, x0, abs(y0-y1)))
        of.write('\t\t\t<div class="ghline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y+_SHADOW, x0+_SHADOW, abs(y0-y1)))

    def draw_connected_box(self, of, center1, center2, col, handle):
        if not handle:
            return None
        db = self.report.database
        person = db.get_person_from_handle(handle)
        self.draw_box(of, center2, col, person)
        self.connect_line(of, center1, center2, col)
        return person

    def display_tree(self, of):
        if not self.person.get_main_parents_family_handle():
            return

        generations = self.graphgens
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        of.write('\t<div id="tree" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Ancestors'))
        of.write('\t\t<div id="treeContainer" style="width:%dpx; height:%dpx;">\n' % (_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP, max_size))

        self.draw_tree(of, 1, generations, max_size, 0, center, self.person.handle)

        of.write('\t\t</div>\n')
        of.write('\t</div>\n')

    def draw_tree(self, of, gen_nr, maxgen, max_size, old_center, new_center, phandle):
        if gen_nr > maxgen:
            return
        gen_offset = int(max_size / pow(2, gen_nr+1))
        db = self.report.database
        person = db.get_person_from_handle(phandle)
        if not person:
            return

        if gen_nr == 1:
            self.draw_box(of, new_center, 0, person)
        else:
            self.draw_connected_box(of, old_center, new_center, gen_nr-1, phandle)

        if gen_nr == maxgen:
            return

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + gen_nr*_WIDTH + (gen_nr-1)*_HGAP
            self.extend_line(of, new_center, line_offset)

            gen_nr = gen_nr + 1
            family = db.get_family_from_handle(family_handle)

            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            self.draw_tree(of, gen_nr, maxgen, max_size, new_center, f_center, f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            self.draw_tree(of, gen_nr, maxgen, max_size, new_center, m_center, m_handle)

    def display_ind_sources(self, of):
        for sref in self.person.get_source_references():
            self.bibli.add_reference(sref)
        self.display_source_refs(of, self.bibli)

    def display_ind_pedigree(self, of):
        db = self.report.database
        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = db.get_family_from_handle(parent_handle)
            father_id = family.get_father_handle()
            mother_id = family.get_mother_handle()
            mother = db.get_person_from_handle(mother_id)
            father = db.get_person_from_handle(father_id)
        else:
            family = None
            father = None
            mother = None

        of.write('\t<div id="pedigree" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Pedigree'))
        of.write('\t\t<ol class="pedigreegen">\n')
        of.write('\t\t\t')

        if father and mother:
            of.write('<li>')
            self.pedigree_person(of, father)
            of.write('\n')
            of.write('\t\t\t\t<ol>\n')
            of.write('\t\t\t\t\t')
            of.write('<li class="spouse">')
            self.pedigree_person(of, mother)
            of.write('\n')
            of.write('\t\t\t\t\t\t<ol>\n')
        elif father:
            of.write('<li>')
            self.pedigree_person(of, father)
            of.write('\n')
            of.write('\t\t\t\t<ol>\n')
        elif mother:
            of.write('<li class="spouse">')
            self.pedigree_person(of, mother)
            of.write('\n')
            of.write('\t\t\t\t<ol>\n')

        if family:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                if child_handle == self.person.handle:
                    of.write('\t\t\t\t\t\t\t<li class="thisperson">%s\n' % self.name)
                    of.write('\t\t\t\t\t\t\t\t<ol class="spouselist">\n')
                    of.write('\t\t\t\t\t\t\t\t\t')
                    self.pedigree_family(of)
                    of.write('\t\t\t\t\t\t\t\t</ol>\n')
                    of.write('\t\t\t\t\t\t\t</li>\n')
                else:
                    of.write('\t\t\t\t\t\t\t')
                    child = db.get_person_from_handle(child_handle)
                    of.write('<li>')
                    self.pedigree_person(of, child)
                    of.write('</li>\n')
            of.write('\t\t\t\t\t\t</ol>\n')
            of.write('\t\t\t\t\t</li>\n')
        else:
            of.write('<li class="thisperson">%s\n' % self.name)
            of.write('\t\t\t\t<ol class="spouselist">\n')
            of.write('\t\t\t\t\t\t')
            self.pedigree_family(of)
        of.write('\t\t\t\t</ol>\n')
        of.write('\t\t\t</li>\n')
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n\n')

    def display_ind_general(self, of):
        self.page_title = self.sort_name
        self.display_first_image_as_thumbnail(of,
                                              self.person.get_media_list())

        of.write('\t<h2>Individuals:</h2>\n')
        of.write('\t<h3>%s</h3>\n' % self.sort_name.strip())
        of.write('\t<div id="summaryarea">\n')
        of.write('\t\t<table class="infolist">\n')

        # GRAMPS ID
        if not self.noid:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('GRAMPS ID'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % self.person.gramps_id)
            of.write('\t\t\t</tr>\n')

        # Names [and their sources]
        for name in [self.person.get_primary_name()] + self.person.get_alternate_names():
            pname = _nd.display_name(name)
            pname += self.get_citation_links( name.get_source_references() )
            type_ = str( name.get_type() )
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % type_)
            of.write('\t\t\t\t<td class="ColumnValue">%s' % pname)
            of.write('</td>\n')
            of.write('\t\t\t</tr>\n')

        # Gender
        nick = self.person.get_nick_name()
        if nick:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Nickname'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % nick)
            of.write('\t\t\t</tr>\n')

        # Gender
        of.write('\t\t\t<tr>\n')
        of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % gender)
        of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_ind_events(self, of):
        evt_ref_list = self.person.get_event_ref_list()

        if not evt_ref_list:
            return

        of.write('\t<div id="events" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Events'))
        of.write('\t\t<table class="infolist">\n')

        db = self.report.database
        for event_ref in evt_ref_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event:
                evt_name = str(event.get_type())

                if event_ref.get_role() == EventRoleType.PRIMARY:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % evt_name)
                else:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s (%s)</td>\n' \
                        % (evt_name, event_ref.get_role()))

                of.write('\t\t\t\t<td class="ColumnValue">')
                of.write(self.format_event(event, event_ref))
                of.write('</td>\n')
                of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_addresses(self, of):
        alist = self.person.get_address_list()

        if not alist:
            return

        of.write('\t<div id="addresses" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Addresses'))
        of.write('\t\t<table class="infolist">\n')

        for addr in alist:
            location = ReportUtils.get_address_str(addr)
            location += self.get_citation_links( addr.get_source_references() )
            date = _dd.display(addr.get_date_object())

            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % date)
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % location)
            of.write('\t\t\t</tr>\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_child_link(self, of, child_handle):
        db = self.report.database
        child = db.get_person_from_handle(child_handle)
        gid = child.get_gramps_id()
        if child_handle in self.ind_list:
            of.write("\t\t\t\t\t\t<li>")
            child_name = _nd.display(child)
            fname = self.build_path_fname('ppl', child_handle, True)
            self.person_link(of, fname, child_name, gid)
        else:
            of.write("\t\t\t\t\t\t<li>")
            of.write(_nd.display(child))
        of.write(u"</li>\n")

    def display_parent(self, of, handle, title, rel):
        db = self.report.database
        person = db.get_person_from_handle(handle)
        of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % title)
        of.write('\t\t\t\t<td class="ColumnValue">')
        gid = person.gramps_id
        if handle in self.ind_list:
            fname = self.build_path_fname('ppl', handle, True)
            self.person_link(of, fname, _nd.display(person), gid)
        else:
            of.write(_nd.display(person))
        if rel != gen.lib.ChildRefType.BIRTH:
            of.write('&nbsp;&nbsp;&nbsp;(%s)' % str(rel))
        of.write('</td>\n')

    def display_ind_parents(self, of):
        parent_list = self.person.get_parent_family_handle_list()

        if not parent_list:
            return

        of.write('\t<div id="parents" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _("Parents"))
        of.write('\t\t<table class="infolist">\n')

        db = self.report.database
        first = True
        if parent_list:
            for family_handle in parent_list:
                family = db.get_family_from_handle(family_handle)

                # Get the mother and father relationships
                frel = ""
                mrel = ""
                sibling = set()
                child_handle = self.person.get_handle()
                child_ref_list = family.get_child_ref_list()
                for child_ref in child_ref_list:
                    if child_ref.ref == child_handle:
                        frel = str(child_ref.get_father_relation())
                        mrel = str(child_ref.get_mother_relation())

                if not first:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td colspan="2">&nbsp;</td>\n')
                    of.write('\t\t\t</tr>\n')
                else:
                    first = False

                father_handle = family.get_father_handle()
                if father_handle:
                    of.write('\t\t\t<tr>\n')
                    self.display_parent(of, father_handle, _('Father'), frel)
                    of.write('\t\t\t</tr>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    of.write('\t\t\t<tr>\n')
                    self.display_parent(of, mother_handle, _('Mother'), mrel)
                    of.write('\t\t\t</tr>\n')

                first = False
                if len(child_ref_list) > 1:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Siblings"))
                    of.write('\t\t\t\t<td class="ColumnValue">\n')
                    of.write('\t\t\t\t\t<ol>\n')
                    for child_ref in child_ref_list:
                        child_handle = child_ref.ref
                        sibling.add(child_handle)   # remember that we've already "seen" this child
                        if child_handle != self.person.handle:
                            self.display_child_link(of, child_handle)
                    of.write('\t\t\t\t\t</ol>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')

                # Also try to identify half-siblings
                other_siblings = set()

                # if we have a known father...
                if father_handle and self.showhalfsiblings:
                    # 1) get all of the families in which this father is involved
                    # 2) get all of the children from those families
                    # 3) if the children are not already listed as siblings...
                    # 4) then remember those children since we're going to list them
                    father = db.get_person_from_handle(father_handle)
                    for family_handle in father.get_family_handle_list():
                        family = db.get_family_from_handle(family_handle)
                        for step_child_ref in family.get_child_ref_list():
                            step_child_handle = step_child_ref.ref
                            if step_child_handle not in sibling:
                                if step_child_handle != self.person.handle:
                                    # we have a new step/half sibling
                                    other_siblings.add(step_child_ref.ref)

                # do the same thing with the mother (see "father" just above):
                if mother_handle and self.showhalfsiblings:
                    mother = db.get_person_from_handle(mother_handle)
                    for family_handle in mother.get_family_handle_list():
                        family = db.get_family_from_handle(family_handle)
                        for step_child_ref in family.get_child_ref_list():
                            step_child_handle = step_child_ref.ref
                            if step_child_handle not in sibling:
                                if step_child_handle != self.person.handle:
                                    # we have a new step/half sibling
                                    other_siblings.add(step_child_ref.ref)

                # now that we have all of the step-siblings/half-siblings, print them out
                if len(other_siblings) > 0:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Half Siblings"))
                    of.write('\t\t\t\t<td class="ColumnValue">\n')
                    of.write('\t\t\t\t\t<ol>\n')
                    for child_handle in other_siblings:
                        self.display_child_link(of, child_handle)
                    of.write('\t\t\t\t\t</ol>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_ind_relationships(self, of):
        family_list = self.person.get_family_handle_list()
        if not family_list:
            return

        of.write('\t<div id="families" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _("Families"))
        of.write('\t\t<table class="infolist">\n')

        db = self.report.database
        first = True
        for family_handle in family_list:
            family = db.get_family_from_handle(family_handle)
            self.display_spouse(of, family, first)
            first = False
            childlist = family.get_child_ref_list()
            if childlist:
                of.write('\t\t\t<tr>\n')
                of.write('\t\t\t\t<td class="ColumnType">&nbsp;</td>\n')
                of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Children"))
                of.write('\t\t\t\t<td class="ColumnValue">\n')
                of.write('\t\t\t\t\t<ol>\n')
                for child_ref in childlist:
                    self.display_child_link(of, child_ref.ref)
                of.write('\t\t\t\t\t</ol>\n')
                of.write('\t\t\t\t</td>\n')
                of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_spouse(self, of, family, first=True):
        db = self.report.database
        gender = self.person.get_gender()
        reltype = family.get_relationship()

        if reltype == gen.lib.FamilyRelType.MARRIED:
            if gender == gen.lib.Person.FEMALE:
                relstr = _("Husband")
            elif gender == gen.lib.Person.MALE:
                relstr = _("Wife")
            else:
                relstr = _("Partner")
        else:
            relstr = _("Partner")

        spouse_id = ReportUtils.find_spouse(self.person, family)
        if spouse_id:
            spouse = db.get_person_from_handle(spouse_id)
            name = _nd.display(spouse)
        else:
            name = _("unknown")
        rtype = str(family.get_relationship())
        of.write('\t\t\t<tr class="BeginFamily">\n')
        of.write('\t\t\t\t<td class="ColumnType">%s</td>\n' % rtype)
        of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % relstr)
        of.write('\t\t\t\t<td class="ColumnValue">')
        if spouse_id:
            gid = spouse.get_gramps_id()
            if spouse_id in self.ind_list:
                spouse_name = _nd.display(spouse)
                fname = self.build_path_fname('ppl', spouse.handle, True)
                self.person_link(of, fname, spouse_name, gid)
            else:
                of.write(name)
        of.write('</td>\n')
        of.write('\t\t\t</tr>\n')

        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            evtType = str(event.get_type())
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnType">&nbsp;</td>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % evtType)
            of.write('\t\t\t\t<td class="ColumnValue">')
            of.write(self.format_event(event, event_ref))
            of.write('</td>\n')
            of.write('\t\t\t</tr>\n')
        for attr in family.get_attribute_list():
            attrType = str(attr.get_type())
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnType">&nbsp;</td>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>' % attrType)
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % attr.get_value())
            of.write('\t\t\t</tr>\n')
        notelist = family.get_note_list()
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            if note:
                text = note.get()
                format = note.get_format()
                if text:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnType">&nbsp;</td>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Narrative'))
                    of.write('\t\t\t\t<td class="ColumnValue">\n')
                    of.write('\t\t\t\t\t<p>')
                    if format:
                        of.write(u"<pre>%s</pre>" % text )
                    else:
                        of.write(u"</p>\n\t\t\t\t\t<p>".join(text.split("\n")))
                    of.write('</p>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')

    def pedigree_person(self, of, person):
        person_name = _nd.display(person)
        if person.handle in self.ind_list:
            fname = self.build_path_fname('ppl', person.handle, True)
            self.person_link(of, fname, person_name)
        else:
            of.write(person_name)

    def pedigree_family(self, of):
        db = self.report.database
        for family_handle in self.person.get_family_handle_list():
            rel_family = db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person, rel_family)
            if spouse_handle:
                spouse = db.get_person_from_handle(spouse_handle)
                of.write('<li class="spouse">')
                self.pedigree_person(of, spouse)
            childlist = rel_family.get_child_ref_list()
            if childlist:
                of.write('\n')
                of.write('\t\t\t\t\t\t\t\t\t\t<ol>\n')
                for child_ref in childlist:
                    of.write('\t\t\t\t\t\t\t\t\t\t\t')
                    child = db.get_person_from_handle(child_ref.ref)
                    of.write('<li>')
                    self.pedigree_person(of, child)
                    of.write('</li>\n')
                of.write('\t\t\t\t\t\t\t\t\t\t</ol>\n\t\t\t\t\t\t\t\t\t</li>\n')
            else:
                of.write('</li>\n')

    def format_event(self, event, event_ref):
        db = self.report.database
        lnk = (self.cur_fname, self.page_title, self.gid)
        descr = event.get_description()
        place_handle = event.get_place_handle()
        if place_handle:
            if self.place_list.has_key(place_handle):
                if lnk not in self.place_list[place_handle]:
                    self.place_list[place_handle].append(lnk)
            else:
                self.place_list[place_handle] = [lnk]

            place = self.place_link_str(place_handle,
                                        ReportUtils.place_name(db, place_handle),
                                        up=True)
        else:
            place = u""

        date = _dd.display(event.get_date_object())
        tmap = {'description' : descr, 'date' : date, 'place' : place}

        if descr and date and place:
            text = _('%(description)s,&nbsp;&nbsp;%(date)s&nbsp;&nbsp;at&nbsp;&nbsp;%(place)s') % tmap
        elif descr and date:
            text = _('%(description)s,&nbsp;&nbsp;%(date)s&nbsp;&nbsp;') % tmap
        elif descr and place:
            text = _('%(description)s&nbsp;&nbsp;at&nbsp;&nbsp;%(place)s') % tmap
        elif descr:
            text = descr
        elif date and place:
            text = _('%(date)s&nbsp;&nbsp;at&nbsp;&nbsp;%(place)s') % tmap
        elif date:
            text = date
        elif place:
            text = place
        else:
            text = '\n'
        text += self.get_citation_links( event.get_source_references() )

        # if the event or event reference has a attributes attached to it,
        # get the text and format it correctly
        attr_list = event.get_attribute_list()
        attr_list.extend(event_ref.get_attribute_list())
        for attr in attr_list:
            text += _("<br />%(type)s: %(value)s") % {
                'type'     : attr.get_type(),
                'value'    : attr.get_value() }

        # if the event or event reference has a note attached to it,
        # get the text and format it correctly
        notelist = event.get_note_list()
        notelist.extend(event_ref.get_note_list())
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            if note:
                note_text = note.get()
                format = note.get_format()
                if note_text:
                    if format:
                        text += u"<pre>%s</pre>" % note_text
                    else:
                        text += u"<p>"
                        text += u"<br />".join(note_text.split("\n"))
                        text += u"</p>"
        return text

    def get_citation_links(self, source_ref_list):
        gid_list = []
        lnk = (self.cur_fname, self.page_title, self.gid)

        for sref in source_ref_list:
            handle = sref.get_reference_handle()
            gid_list.append(sref)

            if self.src_list.has_key(handle):
                if lnk not in self.src_list[handle]:
                    self.src_list[handle].append(lnk)
            else:
                self.src_list[handle] = [lnk]

        text = ""
        if len(gid_list) > 0:
            text = text + " <sup>"
            for ref in gid_list:
                index, key = self.bibli.add_reference(ref)
                id_ = "%d%s" % (index+1, key)
                text = text + ' <a href="#sref%s">%s</a>' % (id_, id_)
            text = text + "</sup>"

        return text

class NavWebReport(Report):
    
    def __init__(self, database, options):
        """
        Create WebReport object that produces the report.

        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        """
        Report.__init__(self, database, options)
        menu = options.menu
        self.options = {}

        for optname in menu.get_all_option_names():
            menuopt = menu.get_option_by_name(optname)
            self.options[optname] = menuopt.get_value()

        if not self.options['incpriv']:
            self.database = PrivateProxyDb(database)
        else:
            self.database = database

        livinginfo = self.options['living']
        yearsafterdeath = self.options['yearsafterdeath']

        if livinginfo == LivingProxyDb.MODE_EXCLUDE:
            self.database = LivingProxyDb(self.database,
                                          LivingProxyDb.MODE_EXCLUDE,
                                          None,
                                          yearsafterdeath)
        elif livinginfo == LivingProxyDb.MODE_RESTRICT:
            self.database = LivingProxyDb(self.database,
                                          LivingProxyDb.MODE_RESTRICT,
                                          None,
                                          yearsafterdeath)

        filters_option = menu.get_option_by_name('filter')
        self.filter = filters_option.get_filter()

        self.target_path = self.options['target']
        self.copyright = self.options['cright']
        self.css = self.options['css']
        self.title = self.options['title']
        self.inc_gallery = self.options['gallery']
        self.inc_contact = self.options['contactnote'] != u"" or \
                           self.options['contactimg'] != u""
        self.inc_download = self.options['incdownload']
        self.use_archive = self.options['archive']
        self.use_intro = self.options['intronote'] != u"" or \
                         self.options['introimg'] != u""
        self.use_home = self.options['homenote'] != u"" or \
                        self.options['homeimg'] != u""

        self.archive = None
        self.cur_fname = None            # Internal use. The name of the output file, to be used for the tar archive.
        if self.use_archive:
            self.html_dir = None
        else:
            self.html_dir = self.target_path
        self.warn_dir = True        # Only give warning once.
        self.photo_list = {}

    def write_report(self):
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name == None:
                dir_name = os.getcwd()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    ErrorDialog(_("Neither %s nor %s are directories") % \
                                (dir_name, parent_dir))
                    return
                else:
                    try:
                        os.mkdir(dir_name)
                    except IOError, value:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name + "\n" + value[1])
                        return
                    except:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name)
                        return

            try:
                image_dir_name = os.path.join(dir_name, 'images')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)

                image_dir_name = os.path.join(dir_name, 'thumb')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)
            except IOError, value:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name + "\n" + value[1])
                return
            except:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name)
                return
        else:
            if os.path.isdir(self.target_path):
                ErrorDialog(_('Invalid file name'),
                            _('The archive file must be a file, not a directory'))
                return
            try:
                self.archive = tarfile.open(self.target_path, "w:gz")
            except (OSError, IOError), value:
                ErrorDialog(_("Could not create %s") % self.target_path,
                            value)
                return

        self.progress = Utils.ProgressMeter(_("Generate HTML reports"), '')

        # Build the person list
        ind_list = self.build_person_list()

        # Generate the CSS file if requested
        if self.css != '':
            self.write_css(self.css)

        # Copy Mainz Style Images
        imgs = ["NWeb_Mainz_Bkgd.png",
                "NWeb_Mainz_Header.png",
                "NWeb_Mainz_Mid.png",
                "NWeb_Mainz_MidLight.png",
                "document.png",
                "favicon.ico"]
        # Copy the Creative Commons icon if the a Creative Commons
        # license is requested
        if 0 < self.copyright < 7:
            imgs += ["somerights20.gif"]

        for f in imgs:
            from_path = os.path.join(const.IMAGE_DIR, f)
            to_path = os.path.join("images", f)
            self.store_file(from_path, to_path)

        place_list = {}
        source_list = {}

        self.base_pages()
        self.person_pages(ind_list, place_list, source_list)
        self.surname_pages(ind_list)
        self.place_pages(place_list, source_list)
        if self.inc_gallery:
            self.gallery_pages(source_list)
        self.source_pages(source_list)

        if self.archive:
            self.archive.close()
        self.progress.close()

    def build_person_list(self):
        """
        Builds the person list. Gets all the handles from the database
        and then applies the chosen filter:
        """

        # gets the person list and applies the requested filter
        ind_list = self.database.get_person_handles(sort_handles=False)
        self.progress.set_pass(_('Filtering'), 1)
        ind_list = self.filter.apply(self.database, ind_list)
        return ind_list

    def write_css(self, css_file):
        """
        Copy the CSS file to the destination.
        """

        if self.archive:
            fname = os.path.join(const.DATA_DIR, css_file)
            self.archive.add(fname, _NARRATIVE)
            gname = os.path.join(const.DATA_DIR, "NWeb-Print_Default.css")
            self.archive.add(gname, _NARRATIVEPRINT)
        else:
            shutil.copyfile(os.path.join(const.DATA_DIR, css_file),
                            os.path.join(self.html_dir, _NARRATIVE))
            shutil.copyfile(os.path.join(const.DATA_DIR, "NWeb-Print_Default.css"),
                            os.path.join(self.html_dir, _NARRATIVEPRINT))

    def person_pages(self, ind_list, place_list, source_list):

        self.progress.set_pass(_('Creating individual pages'), len(ind_list) + 1)
        self.progress.step()    # otherwise the progress indicator sits at 100%
                                # for a short while from the last step we did,
                                # which was to apply the privacy filter

        IndividualListPage(self, self.title, ind_list)

        for person_handle in ind_list:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)

            IndividualPage(self, self.title, person, ind_list, place_list, source_list)

    def surname_pages(self, ind_list):
        """
        Generates the surname related pages from list of individual
        people.
        """

        local_list = sort_people(self.database, ind_list)
        self.progress.set_pass(_("Creating surname pages"), len(local_list))

        if self.use_home or self.use_intro:
            defname = "surnames"
        else:
            defname = "index"

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_NAME, defname)

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_COUNT, "surnames_count")

        for (surname, handle_list) in local_list:
            SurnamePage(self, self.title, surname, handle_list)
            self.progress.step()

    def source_pages(self, source_list):

        self.progress.set_pass(_("Creating source pages"), len(source_list))

        SourcesPage(self, self.title, source_list.keys())

        for key in list(source_list):
            SourcePage(self, self.title, key, source_list)
            self.progress.step()


    def place_pages(self, place_list, source_list):

        self.progress.set_pass(_("Creating place pages"), len(place_list))

        PlaceListPage(self, self.title, place_list, source_list)

        for place in place_list.keys():
            PlacePage(self, self.title, place, source_list, place_list)
            self.progress.step()

    def gallery_pages(self, source_list):
        import gc

        self.progress.set_pass(_("Creating media pages"), len(self.photo_list))

        GalleryPage(self, self.title, source_list)

        prev = None
        total = len(self.photo_list)
        index = 1
        photo_keys = self.photo_list.keys()
        sort = Sort.Sort(self.database)
        photo_keys.sort(sort.by_media_title)

        for photo_handle in photo_keys:
            gc.collect() # Reduce memory usage when there are many images.
            if index == total:
                next = None
            else:
                next = photo_keys[index]
            # Notice. Here self.photo_list[photo_handle] is used not self.photo_list
            MediaPage(self, self.title, photo_handle, source_list, self.photo_list[photo_handle],
                      (prev, next, index, total))
            self.progress.step()
            prev = photo_handle
            index += 1

    def base_pages(self):

        if self.use_home:
            HomePage(self, self.title)

        if self.inc_contact:
            ContactPage(self, self.title)

        if self.inc_download:
            DownloadPage(self, self.title)

        if self.use_intro:
            IntroductionPage(self, self.title)

    def store_file(self, from_path, to_path):
        """
        Store the file in the destination.
        """
        if self.archive:
            self.archive.add(str(from_path), str(to_path))
        else:
            dest = os.path.join(self.html_dir, to_path)
            dirname = os.path.dirname(dest)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            if from_path != dest:
                shutil.copyfile(from_path, dest)
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

class NavWebOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    __INCLUDE_LIVING_VALUE = 99 # Arbitrary number

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__archive = None
        self.__target = None
        self.__pid = None
        self.__filter = None
        self.__graph = None
        self.__graphgens = None
        self.__living = None
        self.__yearsafterdeath = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web calendar.
        """
        self.__add_report_options(menu)
        self.__add_page_generation_options(menu)
        self.__add_privacy_options(menu)
        self.__add_advanced_options(menu)

    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")

        self.__archive = BooleanOption(_('Store web pages in .tar.gz archive'),
                                       False)
        self.__archive.set_help(_('Whether to store the web pages in an '
                                  'archive file'))
        menu.add_option(category_name, 'archive', self.__archive)
        self.__archive.connect('value-changed', self.__archive_changed)

        self.__target = DestinationOption(_("Destination"),
                                    os.path.join(const.USER_HOME, "NAVWEB"))
        self.__target.set_help( _("The destination directory for the web "
                                  "files"))
        menu.add_option(category_name, "target", self.__target)

        self.__archive_changed()

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on calendar"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self.__update_filters()

        title = StringOption(_("Web site title"), _('My Family Tree'))
        title.set_help(_("The title of the web site"))
        menu.add_option(category_name, "title", title)

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0 )
        index = 0
        for copt in _COPY_OPTIONS:
            cright.add_item(index, copt)
            index += 1
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1] )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)

        css = EnumeratedListOption(_('Stylesheet'), _CSS_FILES[0][1])
        for style in _CSS_FILES:
            css.add_item(style[1], style[0])
        css.set_help( _("The style sheet to be used for the web page"))
        menu.add_option(category_name, "css", css)

        self.__graph = BooleanOption(_("Include ancestor graph"), True)
        self.__graph.set_help(_('Whether to include an ancestor graph '
                                      'on each individual page'))
        menu.add_option(category_name, 'graph', self.__graph)
        self.__graph.connect('value-changed', self.__graph_changed)

        self.__graphgens = EnumeratedListOption(_('Graph generations'), 4)
        self.__graphgens.add_item(2, "2")
        self.__graphgens.add_item(3, "3")
        self.__graphgens.add_item(4, "4")
        self.__graphgens.add_item(5, "5")
        self.__graphgens.set_help( _("The number of generations to include in "
                                     "the ancestor graph"))
        menu.add_option(category_name, "graphgens", self.__graphgens)

        self.__graph_changed()

    def __add_page_generation_options(self, menu):
        """
        Options on the "Page Generation" tab.
        """
        category_name = _("Page Generation")

        homenote = NoteOption(_('Home page note'))
        homenote.set_help( _("A note to be used on the home page"))
        menu.add_option(category_name, "homenote", homenote)

        homeimg = MediaOption(_('Home page image'))
        homeimg.set_help( _("An image to be used on the home page"))
        menu.add_option(category_name, "homeimg", homeimg)

        intronote = NoteOption(_('Introduction note'))
        intronote.set_help( _("A note to be used as the introduction"))
        menu.add_option(category_name, "intronote", intronote)

        introimg = MediaOption(_('Introduction image'))
        introimg.set_help( _("An image to be used as the introduction"))
        menu.add_option(category_name, "introimg", introimg)

        contactnote = NoteOption(_("Publisher contact note"))
        contactnote.set_help( _("A note to be used as the publisher contact"))
        menu.add_option(category_name, "contactnote", contactnote)

        contactimg = MediaOption(_("Publisher contact image"))
        contactimg.set_help( _("An image to be used as the publisher contact"))
        menu.add_option(category_name, "contactimg", contactimg)

        headernote = NoteOption(_('HTML user header'))
        headernote.set_help( _("A note to be used as the page header"))
        menu.add_option(category_name, "headernote", headernote)

        footernote = NoteOption(_('HTML user footer'))
        footernote.set_help( _("A note to be used as the page footer"))
        menu.add_option(category_name, "footernote", footernote)

        gallery = BooleanOption(_("Include images and media objects"), True)
        gallery.set_help(_('Whether to include a gallery of media objects'))
        menu.add_option(category_name, 'gallery', gallery)

        incdownload = BooleanOption(_("Include download page"), False)
        incdownload.set_help(_('Whether to include a database download option'))
        menu.add_option(category_name, 'incdownload', incdownload)

        nogid = BooleanOption(_('Suppress GRAMPS ID'), False)
        nogid.set_help(_('Whether to include the Gramps ID of objects'))
        menu.add_option(category_name, 'nogid', nogid)

    def __add_privacy_options(self, menu):
        """
        Options on the "Privacy" tab.
        """
        category_name = _("Privacy")

        incpriv = BooleanOption(_("Include records marked private"), False)
        incpriv.set_help(_('Whether to include private objects'))
        menu.add_option(category_name, 'incpriv', incpriv)

        self.__living = EnumeratedListOption(_("Living People"),
                                             self.__INCLUDE_LIVING_VALUE )
        self.__living.add_item(LivingProxyDb.MODE_EXCLUDE, _("Exclude"))
        self.__living.add_item(LivingProxyDb.MODE_RESTRICT, _("Restrict"))
        self.__living.add_item(self.__INCLUDE_LIVING_VALUE, _("Include"))
        self.__living.set_help(_("How to handle living people"))
        menu.add_option(category_name, "living", self.__living)
        self.__living.connect('value-changed', self.__living_changed)

        self.__yearsafterdeath = NumberOption(_("Years from death to consider "
                                                 "living"), 30, 0, 100)
        self.__yearsafterdeath.set_help(_("This allows you to restrict "
                                          "information on people who have not "
                                          "been dead for very long"))
        menu.add_option(category_name, 'yearsafterdeath',
                        self.__yearsafterdeath)

        self.__living_changed()

    def __add_advanced_options(self, menu):
        """
        Options on the "Advanced" tab.
        """
        category_name = _("Advanced")

        linkhome = BooleanOption(_('Include link to home person on every '
                                   'page'), False)
        linkhome.set_help(_('Whether to include a link to the home person'))
        menu.add_option(category_name, 'linkhome', linkhome)

        showbirth = BooleanOption(_("Include a column for birth dates on the "
                                    "index pages"), True)
        showbirth.set_help(_('Whether to include a birth column'))
        menu.add_option(category_name, 'showbirth', showbirth)

        showdeath = BooleanOption(_("Include a column for death dates on the "
                                    "index pages"), False)
        showdeath.set_help(_('Whether to include a death column'))
        menu.add_option(category_name, 'showdeath', showdeath)

        showspouse = BooleanOption(_("Include a column for partners on the "
                                    "index pages"), False)
        showspouse.set_help(_('Whether to include a partners column'))
        menu.add_option(category_name, 'showspouse', showspouse)

        showparents = BooleanOption(_("Include a column for parents on the "
                                      "index pages"), False)
        showparents.set_help(_('Whether to include a parents column'))
        menu.add_option(category_name, 'showparents', showparents)

        showhalfsiblings = BooleanOption(_("Include a column for half-siblings"
                                           " on the index pages"), False)
        showhalfsiblings.set_help(_("Whether to include a half-siblings "
                                    "column"))
        menu.add_option(category_name, 'showhalfsiblings', showhalfsiblings)

    def __archive_changed(self):
        """
        Update the change of storage: archive or directory
        """
        if self.__archive.get_value() == True:
            self.__target.set_extension(".tar.gz")
            self.__target.set_directory_entry(False)
        else:
            self.__target.set_directory_entry(True)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def __graph_changed(self):
        """
        Handle enabling or disabling the ancestor graph
        """
        self.__graphgens.set_available(self.__graph.get_value())

    def __living_changed(self):
        """
        Handle a change in the living option
        """
        if self.__living.get_value() == self.__INCLUDE_LIVING_VALUE:
            self.__yearsafterdeath.set_available(False)
        else:
            self.__yearsafterdeath.set_available(True)

    def make_default_style(self, default_style):
        """Make the default output style for the Web Pages Report."""
        pass


# FIXME. Why do we need our own sorting? Why not use Sort.Sort?
def sort_people(db, handle_list):
    sname_sub = {}
    sortnames = {}

    for person_handle in handle_list:
        person = db.get_person_from_handle(person_handle)
        primary_name = person.get_primary_name()

        if primary_name.group_as:
            surname = primary_name.group_as
        else:
            surname = db.get_name_group_mapping(primary_name.surname)

        sortnames[person_handle] = _nd.sort_string(primary_name)

        if sname_sub.has_key(surname):
            sname_sub[surname].append(person_handle)
        else:
            sname_sub[surname] = [person_handle]

    sorted_lists = []
    temp_list = sname_sub.keys()
    temp_list.sort(locale.strcoll)
    for name in temp_list:
        slist = map(lambda x: (sortnames[x], x), sname_sub[name])
        slist.sort(lambda x, y: locale.strcoll(x[0], y[0]))
        entries = map(lambda x: x[1], slist)
        sorted_lists.append((name, entries))
    return sorted_lists

register_report(
    name = 'navwebpage',
    category = CATEGORY_WEB,
    report_class = NavWebReport,
    options_class = NavWebOptions,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Narrated Web Site"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces web (HTML) pages for individuals, or a set of "
                    "individuals"),
    )
