#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007       Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2009  Rob G. Healey <robhealey1@gmail.com>	
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
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import time
import locale
import shutil
import codecs
import tarfile
import operator
from TransUtils import sgettext as _
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
from gen.plug import PluginManager
from gen.plug.menu import PersonOption, NumberOption, StringOption, \
                          BooleanOption, EnumeratedListOption, FilterOption, \
                          NoteOption, MediaOption, DestinationOption
from ReportBase import (Report, ReportUtils, MenuReportOptions, CATEGORY_WEB,
                        Bibliography)
import Utils
import ThumbNails
import ImgManip
import Mime
from Utils import probably_alive
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
# Names for stylesheets
_NARRATIVESCREEN = 'narrative-screen.css'
_NARRATIVEPRINT = 'narrative-print.css'

# variables for alphabet_navigation
_PERSON = 0
_PLACE = 1

# graphics for Maiz stylesheet
_WEBBKGD = 'Web_Mainz_Bkgd.png'
_WEBHEADER = 'Web_Mainz_Header.png'
_WEBMID = 'Web_Mainz_Mid.png'
_WEBMIDLIGHT = 'Web_Mainz_MidLight.png'

_INCLUDE_LIVING_VALUE = 99 # Arbitrary number
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
    [_("Basic-Ash"),            'Web_Basic-Ash.css'],
    [_("Basic-Cypress"),        'Web_Basic-Cypress.css'],
    [_("Basic-Lilac"),          'Web_Basic-Lilac.css'],
    [_("Basic-Peach"),          'Web_Basic-Peach.css'],
    [_("Basic-Spruce"),         'Web_Basic-Spruce.css'],
    [_("Mainz"),                'Web_Mainz.css'],
    [_("Nebraska"),             'Web_Nebraska.css'],
    [_("Visually Impaired"),    'Web_Visually.css'],

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
    '',

    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" '
    'title="Creative Commons License - By attribution" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'title="Creative Commons License - By attribution, Non-commercial, No derivations" '
    'src="%(gif_fname)s" /></a>',

    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'title="Creative Commons License - By attribution, Non-commerical, Share-alike" '
    'src="%(gif_fname)s" /></a>'
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


_html_dbl_quotes = re.compile(r'([^"]*) " ([^"]*) " (.*)', re.VERBOSE)
_html_sng_quotes = re.compile(r"([^']*) ' ([^']*) ' (.*)", re.VERBOSE)
_html_replacement = {
    "&"  : "&#38;",
    ">"  : "&#62;",
    "<"  : "&#60;",
    }

# This command then defines the 'html_escape' option for escaping
# special characters for presentation in HTML based on the above list.
def html_escape(text):
    """Convert the text and replace some characters with a &# variant."""

    # First single characters, no quotes
    text = ''.join([_html_replacement.get(c, c) for c in text])

    # Deal with double quotes.
    while 1:
        m = _html_dbl_quotes.match(text)
        if not m:
            break
        text = m.group(1) + '&#8220;' + m.group(2) + '&#8221;' + m.group(3)
    # Replace remaining double quotes.
    text = text.replace('"', '&#34;')

    # Deal with single quotes.
    text = text.replace("'s ", '&#8217;s ')
    while 1:
        m = _html_sng_quotes.match(text)
        if not m:
            break
        text = m.group(1) + '&#8216;' + m.group(2) + '&#8217;' + m.group(3)
    # Replace remaining single quotes.
    text = text.replace("'", '&#39;')

    return text

def name_to_md5(text):
    """This creates an MD5 hex string to be used as filename."""
    return md5(text).hexdigest()

class BasePage:
    """
    This is the base class to write certain HTML pages.
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
        self.html_dir = options['target']
        self.ext = options['ext']
        self.noid = options['nogid']
        self.linkhome = options['linkhome']
        self.use_gallery = options['gallery']

    def alphabet_navigation(self, of, db, handle_list, key):
        """
        Will create the alphabetical navigation bar...
        """

        sorted_set = {}

        for ltr in get_first_letters(db, handle_list, key):
            try:
                sorted_set[ltr] += 1
            except KeyError:
                sorted_set[ltr] = 1

        sorted_first_letter = sorted_set.keys()
        sorted_first_letter.sort(locale.strcoll)

        num_ltrs = len(sorted_first_letter)
        if num_ltrs <= 26:
            of.write('\t<div id="navigation">\n')
            of.write('\t\t<ul>\n')
            for ltr in  sorted_first_letter:
                of.write('\t\t\t<li><a href="#%s">%s</a> </li>\n' % (ltr, ltr))
            of.write('\t\t</ul>\n')
            of.write('\t</div>\n')
        else:
            nrows = (num_ltrs / 26)
            index = 0
            for rows in range(0, nrows):
                of.write('\t<div id="navigation">\n')
                of.write('\t\t<ul>\n')
                cols = 0
                while (cols <= 26 and index <= num_ltrs):
                    of.write('\t\t\t<li><a href="#%s">%s</a></li>\n'
                        % (sorted_first_letter[index], sorted_first_letter[index]))
                    cols += 1
                    index += 1
                of.write('\t\t<ul>\n')
                of.write('\t</div>\n')

    def write_footer(self, of):

        of.write('</div>\n')          # Terminate div_content

        of.write('<div id="footer">\n')
        footer = self.report.options['footernote']
        if footer:
            note = self.report.database.get_note_from_gramps_id(footer)
            of.write('\t<div id="user_footer">\n')
            of.write('\t\t<p>')
            of.write(note.get())
            of.write('</p>\n')
            of.write('\t</div>\n')

        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)
        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % {'date' : value}

        # optional "link-home" feature; see bug report #2736
        if self.report.options['linkhome']:
            home_person = self.report.database.get_default_person()
            if home_person:
                home_person_url = self.report.build_url_fname_html(home_person.handle, 'ppl', self.up)
                home_person_name = home_person.get_primary_name().get_regular_name()
                msg += '<br />'
                msg += _('Created for <a href="%s">%s</a>') % (home_person_url, home_person_name)

        of.write('\t<p id="createdate">%s</p>\n' % msg)

        copy_nr = self.report.copyright
        text = ''
        if copy_nr == 0:
            if self.author:
                year = time.localtime()[0]
                text = '&copy; %(year)d %(person)s' % {
                    'person' : self.author,
                    'year' : year}
        elif 0 < copy_nr < len(_CC):
            fname = os.path.join("images", "somerights20.gif")
            fname = self.report.build_url_fname(fname, None, self.up)
            text = _CC[copy_nr] % {'gif_fname' : fname}
        of.write('\t<p id="copyright">%s</p>\n' % text)

        of.write('\t\t<div class="fullclear"></div>\n')

        of.write('</div>\n')
        of.write('</body>\n')
        of.write('</html>')

    def write_header(self, of, title):
        """
        Note. 'title' is used as currentsection in the navigation links.
        """

        of.write('<!DOCTYPE html PUBLIC \n')
        of.write('\t"-//W3C//DTD XHTML 1.0 Strict//EN" \n')
        of.write('\t\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        xmllang = Utils.xml_lang()
        of.write('<html xmlns="http://www.w3.org/1999/xhtml" '
            'xml:lang="%s" lang="%s">\n' % (xmllang, xmllang))

        of.write('<head>\n')
        of.write('\t<title>%s - %s</title>\n' % (html_escape(self.title_str), html_escape(title)))
        of.write('\t<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n'
            % self.report.encoding)
        of.write('\t<meta name="generator" content="%s %s %s" />\n' %
            (const.PROGRAM_NAME, const.VERSION, const.URL_HOMEPAGE))
        of.write('\t<meta name="author" content="%s" />\n' % self.author)

        # Link to media reference regions behaviour stylesheet
        fname = os.path.join("styles", "behaviour.css")
        url = self.report.build_url_fname(fname, None, self.up)
        of.write('\t<link href="%s" rel="stylesheet" \n'
            '\t\ttype="text/css" media="screen" />\n' % url)

        # Link to screen stylesheet
        fname = os.path.join("styles", _NARRATIVESCREEN)
        url = self.report.build_url_fname(fname, None, self.up)
        of.write('\t<link href="%s" rel="stylesheet" \n'
            '\t\ttype="text/css" media="screen" />\n' % url)

        # Link to printer stylesheet
        fname = os.path.join("styles", _NARRATIVEPRINT)
        url = self.report.build_url_fname(fname, None, self.up)
        of.write('\t<link href="%s" rel="stylesheet" \n'
            '\t\ttype="text/css" media="print" />\n' % url)

        # Link to GRAMPS favicon
        url = self.report.build_url_image('favicon.ico', 'images', self.up)
        of.write('\t<link href="%s" rel="Shortcut Icon" \n'
            '\t\ttype="image/icon" />\n' % url)
        of.write('</head>\n\n')

        of.write('<body id="NarrativeWeb">\n')        # Terminated in write_footer()

        # begin header section
        of.write('<div id="header">\n')
        of.write('\t<h1 id="SiteTitle">%s</h1>\n' % html_escape(self.title_str))
        header = self.report.options['headernote']
        if header:
            note = self.report.database.get_note_from_gramps_id(header)
            of.write('\t<p id="user_header">%s</p>\n' % note.get())
        of.write('</div>\n')

        # Begin Navigation Menu
        self.display_nav_links(of, title)

    def display_nav_links(self, of, currentsection):
        """
        Creates the navigation menu
        """

        navs = [
            (self.report.index_fname,      _('Home'),            self.report.use_home),
            (self.report.intro_fname,      _('Introduction'),    self.report.use_intro),
            (self.report.surname_fname,    _('Surnames'),        True),
            ('individuals',                _('Individuals'),     True),
            ('places',                     _('Places'),          True),
            ('gallery',                    _('Gallery'),         self.use_gallery),
            ('download',                   _('Download'),         self.report.inc_download),
            ('contact',                    _('Contact'),          self.report.use_contact),
            ('sources',                    _('Sources'),          True),
                ]

        of.write('\t<div id="navigation">\n')
        of.write('\t\t<ul>\n') 

        for url_fname, nav_text, cond in navs:
            if cond:

                if not url_fname.endswith(self.ext):
                    url_fname += self.ext

                if self.up:
                    # TODO. Check if build_url_fname can be used.
                    url_fname = '/'.join(['..']*3 + [url_fname])

                # TODO. Move this logic to a higher level (caller of write_header).

                # Define 'currentsection' to correctly set navlink item CSS id
                # 'CurrentSection' for Navigation styling.
                # Use 'self.report.cur_fname' to determine 'CurrentSection' for individual
                # elements for Navigation styling.

                # Figure out if we need <li id="CurrentSection"> of just plain <li>
                cs = False
                if nav_text == currentsection:
                    cs = True
                elif nav_text == _('Surnames'):
                    if "srn" in self.report.cur_fname:
                        cs = True
                    elif _('Surnames') in currentsection:
                        cs = True
                elif nav_text == _('Individuals'):
                    if "ppl" in self.report.cur_fname:
                        cs = True
                elif nav_text == _('Sources'):
                    if "src" in self.report.cur_fname:
                        cs = True
                elif nav_text == _('Places'):
                    if "plc" in self.report.cur_fname:
                        cs = True
                elif nav_text == _('Gallery'):
                    if "img" in self.report.cur_fname:
                        cs = True

                cs = cs and ' id="CurrentSection"' or ''
                of.write('\t\t\t<li%s><a href="%s">%s</a></li>\n' % (cs, url_fname, nav_text))

        of.write('\t\t</ul>\n')
        of.write('\t</div>\n') # End Navigation Menu

    def display_first_image_as_thumbnail( self, of, photolist=None):
        if not photolist or not self.use_gallery:
            return

        photo_handle = photolist[0].get_reference_handle()
        photo = self.report.database.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        if mime_type:
            try:
                lnkref = (self.report.cur_fname, self.page_title, self.gid)
                self.report.add_lnkref_to_photo(photo, lnkref)
                real_path, newpath = self.report.prepare_copy_media(photo)
                of.write('\t<div class="snapshot">\n')
                # TODO. Check if build_url_fname can be used.
                newpath = '/'.join(['..']*3 + [newpath])
                self.media_link(of, photo_handle, newpath, '', up=True)
                of.write('\t</div>\n\n')
            except (IOError, OSError), msg:
                WarningDialog(_("Could not add photo to page"), str(msg))
        else:
            of.write('\t<div class="snapshot">\n')
            descr = " ".join(wrapper.wrap(photo.get_description()))
            self.doc_link(of, photo_handle, descr, up=True)
            of.write('\t</div>\n\n')

            lnk = (self.report.cur_fname, self.page_title, self.gid)
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
        displayed = []
        for mediaref in photolist:

            photo_handle = mediaref.get_reference_handle()
            photo = db.get_object_from_handle(photo_handle)
            if photo_handle in displayed:
                continue
            mime_type = photo.get_mime_type()

            title = photo.get_description()
            if title == "":
                title = "(untitled)"
            if mime_type:
                try:
                    lnkref = (self.report.cur_fname, self.page_title, self.gid)
                    self.report.add_lnkref_to_photo(photo, lnkref)
                    real_path, newpath = self.report.prepare_copy_media(photo)
                    descr = " ".join(wrapper.wrap(title))
                    # TODO. Check if build_url_fname can be used.
                    newpath = '/'.join(['..']*3 + [newpath])
                    self.media_link(of, photo_handle, newpath, descr, up=True)
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))
            else:
                try:
                    descr = " ".join(wrapper.wrap(title))
                    self.doc_link(of, photo_handle, descr, up=True)

                    lnk = (self.report.cur_fname, self.page_title, self.gid)
                    # FIXME. Is it OK to add to the photo_list of report?
                    photo_list = self.report.photo_list
                    if photo_handle in photo_list:
                        if lnk not in photo_list[photo_handle]:
                            photo_list[photo_handle].append(lnk)
                    else:
                        photo_list[photo_handle] = [lnk]
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))
            displayed.append(photo_handle)

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
                    text = u"<br />".join(text.split("\n"))
                of.write('\t\t<p>%s</p>\n' % text)
                of.write('\t</div>\n\n')

    def display_url_list(self, of, urllist=None):
        if not urllist:
            return
        of.write('\t<div id="weblinks" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Weblinks'))
        of.write('\t\t<ol>\n')

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
            lnk = (self.report.cur_fname, self.page_title, self.gid)
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
            # Note. The closing > is done in source_link()
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

    def display_references(self, of, handlelist, up=False):
        if not handlelist:
            return

        of.write('\t<div id="references" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('References'))
        of.write('\t\t<ol>\n')

        sortlist = sorted(handlelist,
                          key = operator.itemgetter(1),
                          cmp = locale.strcoll)

        for (path, name, gid) in sortlist:
            of.write('\t\t\t<li>')
            # Note. 'path' already has a filename extension
            url = self.report.build_url_fname(path, None, self.up)
            self.person_link(of, url, name, gid)
            of.write('</li>\n')
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n')

    def person_link(self, of, url, name, gid=None, thumbnailUrl=None):
        of.write('<a href="%s"' % url)
        if not thumbnailUrl:
            of.write(' class="noThumb"')
        of.write('>')
        if thumbnailUrl:
            of.write('<span class="thumbnail"><img src="%s" width="" height="" alt="Image of %s" /></span>' % (thumbnailUrl, name))
        of.write('%s' % name)
        if not self.noid and gid:
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    # TODO. Check img_url of callers
    def media_link(self, of, handle, img_url, name, up, usedescr=True):
        url = self.report.build_url_fname_html(handle, 'img', up)
        of.write('\t\t<div class="thumbnail">\n')
        of.write('\t\t\t<a href="%s">' % url)
        of.write('<img src="%s" ' % img_url)
        of.write('alt="%s" /></a>\n' % name)
        if usedescr:
            of.write('\t\t\t<p>%s</p>\n' % html_escape(name))
        of.write('\t\t</div>\n')

    def doc_link(self, of, handle, name, up, usedescr=True):
        # TODO. Check extension of handle
        url = self.report.build_url_fname(handle, 'img', up)
        of.write('\t\t<div class="thumbnail">\n')
        of.write('\t\t\t<a href="%s">' % url)
        url = self.report.build_url_image('document.png', 'images', up)
        of.write('<img src="%s" ' % url)
        of.write('alt="%s" /></a>\n' % html_escape(name))
        if usedescr:
            of.write('\t\t\t<p>%s</p>\n' % html_escape(name))
        of.write('\t\t</div>\n')

    def source_link(self, of, handle, name, gid=None, up=False):
        url = self.report.build_url_fname_html(handle, 'src', up)
        of.write(' href="%s">%s' % (url, html_escape(name)))
        if not self.noid and gid:
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link(self, of, handle, name, gid=None, up=False):
        url = self.report.build_url_fname_html(handle, 'plc', up)
        of.write('<a href="%s">%s' % (url, html_escape(name)))
        if not self.noid and gid:
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link_str(self, handle, name, gid=None, up=False):
        url = self.report.build_url_fname_html(handle, 'plc', up)
        retval = '<a href="%s">%s' % (url, html_escape(name))
        if not self.noid and gid:
            retval = retval + '&nbsp;<span class="grampsid">[%s]</span>' % gid
        return retval + '</a>'

class IndividualListPage(BasePage):

    def __init__(self, report, title, person_handle_list):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file("individuals")
        self.write_header(of, _('Individuals'))

        # begin alphabetic navigation
        self.alphabet_navigation(of, db, person_handle_list, _PERSON) 

        of.write('<div id="Individuals" class="content">\n')

        msg = _("This page contains an index of all the individuals in the "
                "database, sorted by their last names. Selecting the person&#8217;s "
                "name will take you to that person&#8217;s individual page.")

        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showspouse = report.options['showspouse']
        showparents = report.options['showparents']

        of.write('\t<p id="description">%s</p>\n' % msg)
        of.write('\t<table class="infolist individuallist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnSurname">%s</th>\n' % _('Surname'))
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        column_count = 2
        if showbirth:
            of.write('\t\t\t<th class="ColumnBirth">%s</th>\n' % _('Birth'))
            column_count += 1
        if showdeath:
            of.write('\t\t\t<th class="ColumnDeath">%s</th>\n' % _('Death'))
            column_count += 1
        if showspouse:
            of.write('\t\t\t<th class="ColumnPartner">%s</th>\n' % _('Partner'))
            column_count += 1
        if showparents:
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
                    if surname:
                        of.write('\t\t\t<td class="ColumnSurname"><a name="%s">%s</a></td>\n' 
                            % (surname[0], surname))
                    else:
                        of.write('\t\t\t<td class="ColumnSurname">&nbsp;\n')
                else:
                    of.write('\t\t<tr>\n')
                    of.write('\t\t\t<td class="ColumnSurname">&nbsp;')
                of.write('</td>\n')

                # firstname column
                of.write('\t\t\t<td class="ColumnName">')
                url = self.report.build_url_fname_html(person.handle, 'ppl')
                first_suffix = _get_prefix_suffix_name(person.gender, person.primary_name)
                self.person_link(of, url, first_suffix, person.gramps_id)
                of.write('</td>\n')

                # birth column
                if showbirth:
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
                if showdeath:
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
                if showspouse:
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
                if showparents:
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

        self.write_footer(of)
        self.report.close_file(of)

class SurnamePage(BasePage):

    def __init__(self, report, title, surname, person_handle_list):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file(name_to_md5(surname), 'srn')
        self.up = True
        self.write_header(of, "%s - %s" % (_('Surname'), surname))

        of.write('<div id="SurnameDetail" class="content">\n')

        msg = _("This page contains an index of all the individuals in the "
                "database with the surname of %s. Selecting the person&#8217;s name "
                "will take you to that person&#8217;s individual page.") % surname

        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showspouse = report.options['showspouse']
        showparents = report.options['showparents']

        of.write('\t<h3>%s</h3>\n' % html_escape(surname))
        of.write('\t<p id="description">%s</p>\n' % msg)
        of.write('\t<table class="infolist surname">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        if showbirth:
            of.write('\t\t\t<th class="ColumnBirth">%s</th>\n' % _('Birth'))
        if showdeath:
            of.write('\t\t\t<th class="ColumnDeath">%s</th>\n' % _('Death'))
        if showspouse:
            of.write('\t\t\t<th class="ColumnPartner">%s</th>\n' % _('Partner'))
        if showparents:
            of.write('\t\t\t<th class="ColumnParents">%s</th>\n' % _('Parents'))
        of.write('\t\t</tr>\n')
        of.write('\t</thead>\n')
        of.write('\t<tbody>\n')

        for person_handle in person_handle_list:

            # firstname column
            person = db.get_person_from_handle(person_handle)
            of.write('\t\t<tr>\n')
            of.write('\t\t\t<td class="ColumnName">')
            url = self.report.build_url_fname_html(person.handle, 'ppl', True)
            first_suffix = _get_prefix_suffix_name(person.gender, person.primary_name)
            self.person_link(of, url, first_suffix, person.gramps_id)
            of.write('</td>\n')

            # birth column
            if showbirth:
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
            if showdeath:
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
            if showspouse:
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
            if showparents:
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

        self.write_footer(of)
        self.report.close_file(of)

class PlaceListPage(BasePage):

    def __init__(self, report, title, place_handles, src_list):
        BasePage.__init__(self, report, title)
        self.src_list = src_list        # TODO verify that this is correct

        db = report.database
        of = self.report.create_file("places")
        self.write_header(of, _('Places'))

        # begin alphabetic navigation
        self.alphabet_navigation(of, db, place_handles, _PLACE) 

        of.write('<div id="Places" class="content">\n')

        msg = _("This page contains an index of all the places in the "
                "database, sorted by their title. Clicking on a place&#8217;s "
                "title will take you to that place&#8217;s page.")

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
            place_title = ReportUtils.place_name(db, handle)

            if not place_title:
                continue

            letter = normalize('NFKC', place_title)[0].upper()

            if letter != last_letter:
                last_letter = letter
                of.write('\t\t<tr class="BeginLetter">\n')
                of.write('\t\t\t<td class="ColumnLetter"><a name="%s">%s</a></td>\n' 
                    % (last_letter, last_letter))
            else:
                of.write('\t\t<tr>\n')
                of.write('\t\t\t<td class="ColumnLetter">&nbsp;</td>\n')

            of.write('\t\t\t<td class="ColumnName">')
            self.place_link(of, place.handle, place_title, place.gramps_id)
            of.write('</td>\n')
            of.write('\t\t</tr>\n')

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.write_footer(of)
        self.report.close_file(of)

class PlacePage(BasePage):

    def __init__(self, report, title, place_handle, src_list, place_list):
        db = report.database
        place = db.get_place_from_handle(place_handle)
        BasePage.__init__(self, report, title, place.gramps_id)
        self.src_list = src_list        # TODO verify that this is correct

        of = self.report.create_file(place.get_handle(), 'plc')
        self.up = True
        self.page_title = ReportUtils.place_name(db, place_handle)
        self.write_header(of, "%s - %s" % (_('Places'), self.page_title))

        of.write('<div id="PlaceDetail" class="content">\n')

        media_list = place.get_media_list()
        self.display_first_image_as_thumbnail(of, media_list)

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
                        (_('ZIP/Postal Code'), ml.postal),
                        (_('Country'), ml.country)]:
                if val[1]:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % val[0])
                    of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % val[1])
                    of.write('\t\t\t</tr>\n')

        if place.lat:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Latitude'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % place.lat)
            of.write('\t\t\t</tr>\n')

        if place.long:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Longitude'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % place.long)
            of.write('\t\t\t</tr>\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n')

        if self.use_gallery:
            self.display_additional_images_as_gallery(of, media_list)
        self.display_note_list(of, place.get_note_list())
        self.display_url_list(of, place.get_url_list())
        self.display_references(of, place_list[place.handle])

        self.write_footer(of)
        self.report.close_file(of)

class MediaPage(BasePage):

    def __init__(self, report, title, handle, src_list, my_media_list, info):
        (prev, next, page_number, total_pages) = info
        db = report.database
        photo = db.get_object_from_handle(handle)
        # TODO. How do we pass my_media_list down for use in BasePage?
        BasePage.__init__(self, report, title, photo.gramps_id)

        """
        *************************************
        GRAMPS feature #2634 -- attempt to highlight subregions in media
        objects and link back to the relevant web page.

        This next section of code builds up the "records" we'll need to
        generate the html/css code to support the subregions
        *************************************
        """

        # get all of the backlinks to this media object; meaning all of
        # the people, events, places, etc..., that use this image
        _region_items = set()
        for (classname, newhandle) in db.find_backlink_handles(handle):

            # for each of the backlinks, get the relevant object from the db
            # and determine a few important things, such as a text name we
            # can use, and the URL to a relevant web page
            _obj     = None
            _name    = ""
            _linkurl = "#"
            if classname == "Person":
                _obj = db.get_person_from_handle( newhandle )
                # what is the shortest possible name we could use for this person?
                _name = _obj.get_primary_name().get_call_name()
                if not _name or _name == "":
                    _name = _obj.get_primary_name().get_first_name()
                _linkurl = report.build_url_fname_html(_obj.handle, 'ppl', True)
            if classname == "Event":
                _obj = db.get_event_from_handle( newhandle )
                _name = _obj.get_description()

            # keep looking if we don't have an object
            if _obj is None:
                continue

            # get a list of all media refs for this object
            medialist = _obj.get_media_list()

            # go media refs looking for one that points to this image
            for mediaref in medialist:

                # is this mediaref for this image?  do we have a rect?
                if mediaref.ref == handle and mediaref.rect is not None:

                    (x1, y1, x2, y2) = mediaref.rect
                    # GRAMPS gives us absolute coordinates,
                    # but we need relative width + height
                    w = x2 - x1
                    h = y2 - y1

                    # remember all this information, cause we'll need
                    # need it later when we output the <li>...</li> tags
                    item = (_name, x1, y1, w, h, _linkurl)
                    _region_items.add(item)
        """
        *************************************
        end of code that looks for and prepares the media object regions
        *************************************
        """

        of = self.report.create_file(handle, 'img')
        self.up = True

        self.src_list = src_list
        self.bibli = Bibliography()

        mime_type = photo.get_mime_type()

        if mime_type:
            note_only = False
            newpath = self.copy_source_file(handle, photo)
            target_exists = newpath is not None
        else:
            note_only = True
            target_exists = False

        self.copy_thumbnail(handle, photo)
        self.page_title = photo.get_description()
        self.write_header(of, "%s - %s" % (_('Gallery'), self.page_title))

        of.write('<div id="GalleryDetail" class="content">\n')

        # gallery navigation
        of.write('\t<div id="GalleryNav">\n')
        of.write('\t\t')
        if prev:
            self.gallery_nav_link(of, prev, _('Previous'), True)
        data = _('<strong id="GalleryCurrent">%(page_number)d</strong> of <strong id="GalleryTotal">%(total_pages)d</strong>' ) % {
            'page_number' : page_number, 'total_pages' : total_pages }
        of.write(' <span id="GalleryPages">%s</span> ' % data)
        if next:
            self.gallery_nav_link(of, next, _('Next'), True)
        of.write('\n')
        of.write('\t</div>\n\n')

        of.write('\t<div id="summaryarea">\n')
        if mime_type:
            if mime_type.startswith("image/"):
                if not target_exists:
                    of.write('\t\t<div id="GalleryDisplay">\n')
                    of.write('\t\t\t<span class="MissingImage">(%s)</span>' % _("The file has been moved or deleted"))
                else:
                    # if the image is spectacularly large, then force the client
                    # to resize it, and include a "<a href=" link to the actual
                    # image; most web browsers will dynamically resize an image
                    # and provide zoom-in/zoom-out functionality when the image
                    # is displayed directly
                    (width, height) = ImgManip.image_size(
                            Utils.media_path_full(db, photo.get_path()))
                    scale = 1.0
                    # TODO. Convert disk path to URL.
                    url = self.report.build_url_fname(newpath, None, self.up)
                    if width > _MAX_IMG_WIDTH or height > _MAX_IMG_HEIGHT:
                        # image is too large -- scale it down and link to the full image
                        scale = min(float(_MAX_IMG_WIDTH)/float(width), float(_MAX_IMG_HEIGHT)/float(height))
                        width = int(width * scale)
                        height = int(height * scale)
                    of.write('\t\t<div id="GalleryDisplay" style="width:%dpx; height:%dpx;">\n' % (width, height))

                    # Feature #2634; display the mouse-selectable regions.
                    # See the large block at the top of this function where
                    # the various regions are stored in _region_items
                    if len(_region_items) > 0:
                        of.write('\t\t\t<ol class="RegionBox">\n')
                        while len(_region_items) > 0:
                            (name, x, y, w, h, linkurl) = _region_items.pop()
                            of.write('\t\t\t\t<li style="'
                                'left:%d%%; '
                                'top:%d%%; '
                                'width:%d%%; '
                                'height:%d%%;">'
                                '<a href="%s">%s</a></li>\n' %
                                (x, y, w, h, linkurl, name))
                        of.write('\t\t\t</ol>\n')

                    # display the image
                    of.write('\t\t\t')
                    if scale != 1.0:
                        of.write('<a href="%s">' % url)
                    of.write('<img width="%d" height="%d" src="%s" alt="%s" />' % (width, height, url, html_escape(self.page_title)))
                    if scale != 1.0:
                        of.write('</a>')
                    of.write('\n')

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
                        path = self.report.build_path('preview', photo.handle)
                        npath = os.path.join(path, photo.handle) + '.png'
                        self.report.copy_file(thmb_path, npath)
                        path = npath
                        os.unlink(thmb_path)
                    except IOError:
                        path = os.path.join('images', 'document.png')
                else:
                    path = os.path.join('images', 'document.png')
                os.rmdir(dirname)

                of.write('\t\t<div id="GalleryDisplay">\n')
                if target_exists:
                    # TODO. Convert disk path to URL
                    url = self.report.build_url_fname(newpath, None, self.up)
                    of.write('\t\t\t<a href="%s" alt="%s" />\n' % (url, html_escape(self.page_title)))
                # TODO. Mixup url and path
                # path = convert_disk_path_to_url(path)
                url = self.report.build_url_fname(path, None, self.up)
                of.write('\t\t\t\t<img src="%s" alt="%s" />\n' % (url, html_escape(self.page_title)))
                if target_exists:
                    of.write('\t\t\t</a>\n')
                else:
                    of.write('\t\t\t<span class="MissingImage">(%s)</span>' % _("The file has been moved or deleted"))
                of.write('\t\t</div>\n\n')
        else:
            of.write('\t\t<div id="GalleryDisplay">\n')
            url = self.report.build_url_image('document.png', 'images', self.up)
            of.write('\t\t\t<img src="%s" alt="%s" />\n' % (url, html_escape(self.page_title)))
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
        if date:
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

        self.write_footer(of)
        self.report.close_file(of)

    def gallery_nav_link(self, of, handle, name, up=False):
        url = self.report.build_url_fname_html(handle, 'img', up)
        of.write('<a id="%s" href="%s">%s</a>' % (html_escape(name), url, html_escape(name)))

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
        to_dir = self.report.build_path('images', handle)
        newpath = os.path.join(to_dir, handle) + ext

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
        to_dir = self.report.build_path('thumb', handle)
        to_path = os.path.join(to_dir, handle) + '.png'
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

        self.report.copy_file(from_path, to_path)

class SurnameListPage(BasePage):
    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1

    def __init__(self, report, title, person_handle_list, order_by=ORDER_BY_NAME, filename="surnames"):
        BasePage.__init__(self, report, title)
        db = report.database
        if order_by == self.ORDER_BY_NAME:
            of = self.report.create_file(filename)
            self.write_header(of, _('Surnames'))
            self.alphabet_navigation(of, db, person_handle_list, _PERSON) 
        else:
            of = self.report.create_file("surnames_count")
            self.write_header(of, _('Surnames by person count'))

        of.write('<div id="Surnames" class="content">\n')

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

        fname = self.report.surname_fname + self.ext
        of.write('\t\t\t<th class="ColumnSurname"><a href="%s">%s</a></th>\n' % (fname, _('Surname')))
        fname = "surnames_count" + self.ext
        of.write('\t\t\t<th class="ColumnQuantity"><a href="%s">%s</a></th>\n' % (fname, _('Number of people')))
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
            letter = normalize('NFKC', surname)[0].upper()

            if letter is not last_letter:
                last_letter = letter
                of.write('\t\t<tr class="BeginLetter">\n')
                of.write('\t\t\t<td class="ColumnLetter"><a name="%s">%s</a></td>\n' 
                    % (last_letter, last_letter))
                of.write('\t\t\t<td class="ColumnSurname">')
                self.surname_link(of, name_to_md5(surname), surname)
                of.write('</td>\n')
            elif surname != last_surname:
                of.write('\t\t<tr>\n')
                of.write('\t\t\t<td class="ColumnLetter">&nbsp;</td>\n')
                of.write('\t\t\t<td class="ColumnSurname">')
                self.surname_link(of, name_to_md5(surname), surname)
                of.write('</td>\n')
                last_surname = surname
            of.write('\t\t\t<td class="ColumnQuantity">%d</td>\n' % len(data_list))
            of.write('\t\t</tr>\n')

        of.write('\t</tbody>\n')
        of.write('\t</table>\n')

        self.write_footer(of)
        self.report.close_file(of)

    def surname_link(self, of, fname, name, opt_val=None, up=False):
        url = self.report.build_url_fname_html(fname, 'srn', up)
        of.write('<a href="%s">%s' % (url, name))
        if opt_val is not None:
            of.write('&nbsp;(%d)' % opt_val)
        of.write('</a>')

class IntroductionPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file(report.intro_fname)
        # Note. In old NarrativeWeb.py the content_divid depended on filename.
        self.write_header(of, _('Introduction'))

        of.write('<div id="Introduction" class="content">\n')

        report.add_image(of, 'introimg')

        note_id = report.options['intronote']
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get()
            if note_obj.get_format():
                of.write(u'\t<pre>%s</pre>\n' % text)
            else:
                of.write(u'<br />'.join(text.split("\n")))

        self.write_footer(of)
        self.report.close_file(of)

class HomePage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file("index")
        self.write_header(of, _('Home'))

        of.write('<div id="Home" class="content">\n')

        report.add_image(of, 'homeimg')

        note_id = report.options['homenote']
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get()
            if note_obj.get_format():
                of.write(u'\t<pre>%s</pre>' % text)
            else:
                of.write(u'<br />'.join(text.split("\n")))

        self.write_footer(of)
        self.report.close_file(of)

class SourcesPage(BasePage):

    def __init__(self, report, title, handle_set):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file("sources")
        self.write_header(of, _('Sources'))

        of.write('<div id="Sources" class="content">\n')

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

        of.write('\t<p id="description">')
        of.write(msg)
        of.write('</p>\n')
        of.write('\t<table class="infolist sourcelist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnLabel">&nbsp;</th>\n')
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
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

        self.write_footer(of)
        self.report.close_file(of)

class SourcePage(BasePage):

    def __init__(self, report, title, handle, src_list):
        db = report.database
        source = db.get_source_from_handle(handle)
        BasePage.__init__(self, report, title, source.gramps_id)

        of = self.report.create_file(source.get_handle(), 'src')
        self.up = True
        self.page_title = source.get_title()
        self.write_header(of, "%s - %s" % (_('Sources'), self.page_title))

        of.write('<div id="SourceDetail" class="content">\n')

        media_list = source.get_media_list()
        self.display_first_image_as_thumbnail(of, media_list)

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

        self.write_footer(of)
        self.report.close_file(of)

class GalleryPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file("gallery")
        self.write_header(of, _('Gallery'))

        of.write('<div id="Gallery" class="content">\n')

        of.write('\t<p id="description">')

        of.write(_("This page contains an index of all the media objects "
                   "in the database, sorted by their title. Clicking on "
                   "the title will take you to that media object&#8217;s page."))
        of.write('</p>\n\n')
        of.write('\t<table class="infolist gallerylist">\n')
        of.write('\t<thead>\n')
        of.write('\t\t<tr>\n')
        of.write('\t\t\t<th class="ColumnRowLabel">&nbsp;</th>\n')
        of.write('\t\t\t<th class="ColumnName">%s</th>\n' % _('Name'))
        of.write('\t\t\t<th class="ColumnDate">%s</th>\n' % _('Date'))
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

        self.write_footer(of)
        self.report.close_file(of)

    def media_ref_link(self, of, handle, name, up=False):
        url = self.report.build_url_fname_html(handle, 'img', up)
        of.write('<a href="%s">%s</a>' % (url, html_escape(name)))

class DownloadPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        of = self.report.create_file("download")
        self.write_header(of, _('Download'))

        of.write('<div id="Download" class="content">\n')

        self.write_footer(of)
        self.report.close_file(of)

class ContactPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file("contact")
        self.write_header(of, _('Contact'))

        of.write('<div id="Contact" class="content">\n')

        of.write('\t<div id="summaryarea">\n')

        report.add_image(of, 'contactimg', 200)

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

        self.write_footer(of)
        self.report.close_file(of)

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
        of = self.report.create_file(person.handle, 'ppl')
        self.up = True
        self.write_header(of, self.sort_name)

        of.write('<div id="IndividualDetail" class="content">\n')

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
        if report.options['graph']:
            self.display_tree(of)

        self.write_footer(of)
        self.report.close_file(of)

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
        sex = person.gender
        if sex == gen.lib.Person.MALE:
            divclass = "male"
        elif sex == gen.lib.Person.FEMALE:
            divclass = "female"
        else:
            divclass = "unknown"
        of.write('\t\t\t<div class="boxbg %s AncCol%s" style="top: %dpx; left: %dpx;">\n' 
            % (divclass, col, top, xoff+1))
        of.write('\t\t\t\t')
        if person.handle in self.ind_list:
            thumbnailUrl = None
            if self.use_gallery and col < 5:
                photolist = person.get_media_list()
                if photolist:
                    photo_handle = photolist[0].get_reference_handle()
                    photo = self.report.database.get_object_from_handle(photo_handle)
                    mime_type = photo.get_mime_type()
                    if mime_type:
                        (photoUrl, thumbnailUrl) = self.report.prepare_copy_media(photo)
                        thumbnailUrl = '/'.join(['..']*3 + [thumbnailUrl])
            person_name = _nd.display(person)
            url = self.report.build_url_fname_html(person.handle, 'ppl', True)
            self.person_link(of, url, person_name, thumbnailUrl=thumbnailUrl)
        else:
            of.write('<span class="unlinked">')
            of.write(_nd.display(person))
            of.write('</span>')
        of.write('\n\t\t\t</div>\n')
        of.write('\t\t\t<div class="shadow" style="top: %dpx; left: %dpx;"></div>\n' 
            % (top+_SHADOW, xoff+_SHADOW))

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

        generations = self.report.options['graphgens']
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        of.write('\t<div id="tree" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Ancestors'))
        of.write('\t\t<div id="treeContainer" style="width:%dpx; height:%dpx;">\n' 
            % (_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP, max_size))

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

            family = db.get_family_from_handle(family_handle)

            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            self.draw_tree(of, gen_nr+1, maxgen, max_size, new_center, f_center, f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            self.draw_tree(of, gen_nr+1, maxgen, max_size, new_center, m_center, m_handle)

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

        if father and mother:
            of.write('\t\t\t<li>')
            self.pedigree_person(of, father)
            of.write('\n')
            of.write('\t\t\t\t<ol>\n')
            of.write('\t\t\t\t\t')
            of.write('<li class="spouse">')
            self.pedigree_person(of, mother)
            of.write('\n')
            of.write('\t\t\t\t\t\t<ol>\n')
        elif father:
            of.write('\t\t\t<li>')
            self.pedigree_person(of, father)
            of.write('\n')
            of.write('\t\t\t\t<ol>\n')
        elif mother:
            of.write('\t\t\t<li class="spouse">')
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
        if father or mother:
            of.write('\t\t\t</li>\n')
        of.write('\t\t</ol>\n')
        of.write('\t</div>\n\n')

    def display_ind_general(self, of):
        self.page_title = self.sort_name
        self.display_first_image_as_thumbnail(of, self.person.get_media_list())

        of.write('\t<h3>%s</h3>\n' % self.sort_name.strip())
        of.write('\t<div id="summaryarea">\n')
        of.write('\t\t<table class="infolist">\n')

        primary_name = self.person.get_primary_name()
        # Names [and their sources]
        for name in [primary_name] + self.person.get_alternate_names():
            pname = _nd.display_name(name)
            pname += self.get_citation_links( name.get_source_references() )

            # if we have just a firstname, then the name is preceeded by ", "
            # which doesn't exactly look very nice printed on the web page
            if pname[:2] == ', ':
                pname = pname[2:]

            type_ = str( name.get_type() )
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % type_)
            of.write('\t\t\t\t<td class="ColumnValue">%s' % pname)

            # display any notes associated with this name
            notelist = name.get_note_list()
            if len(notelist) > 0:
                of.write('\n')
                of.write('\t\t\t\t\t<ul>\n')
                for notehandle in notelist:
                    note = self.report.database.get_note_from_handle(notehandle)
                    if note:
                        note_text = note.get()
                        if note_text:
                            txt = u" ".join(note_text.split("\n"))
                            of.write('\t\t\t\t\t\t<li>%s</li>\n' % txt)
                of.write('\t\t\t\t\t</ul>\n')
                of.write('\t\t\t\t')

            # finished with this name
            of.write('</td>\n')
            of.write('\t\t\t</tr>\n')

        # display call names
        first_name = primary_name.get_first_name()
        for name in [primary_name] + self.person.get_alternate_names():
            call_name = name.get_call_name()
            if call_name and call_name != first_name:
                call_name += self.get_citation_links( name.get_source_references() )
                of.write('\t\t\t<tr>\n')
                of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n'
                    % _('Name'))
                of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n'
                    % call_name)
                of.write('\t\t\t</tr>\n')

        # display the nickname attribute
        nick_name = self.person.get_nick_name()
        if nick_name and nick_name != first_name:
            nick_name += self.get_citation_links( self.person.get_source_references() )
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n'
                % _('Name'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n'
                % nick_name)
            of.write('\t\t\t</tr>\n')

        # GRAMPS ID
        if not self.noid:
            of.write('\t\t\t<tr>\n')
            of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('GRAMPS ID'))
            of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % self.person.gramps_id)
            of.write('\t\t\t</tr>\n')

        # Gender
        of.write('\t\t\t<tr>\n')
        of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % gender)
        of.write('\t\t\t</tr>\n')

        # Age At Death???
        birth_ref = self.person.get_birth_ref()
        birth_date = None
        if birth_ref:
            birth_event = self.report.database.get_event_from_handle(birth_ref.ref)
            birth_date = birth_event.get_date_object()

        if (birth_date is not None and birth_date.get_valid()):
            alive = probably_alive(self.person, self.report.database, gen.lib.date.Today())
            death_ref = self.person.get_death_ref()
            death_date = None
            if death_ref:
                death_event = self.report.database.get_event_from_handle(death_ref.ref)
                death_date = death_event.get_date_object()

            if not alive and (death_date is not None and death_date.is_valid()):
                of.write('\t\t\t<tr>\n')
                of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n'
                    % _('Age at Death'))
                nyears = death_date - birth_date
                nyears.format(precision=3)
                of.write('\t\t\t\t<td class="ColumnValue">%s</td>\n' % nyears)
                of.write('\t\t\t</tr>\n') 

        # close table, and end section...
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_ind_events(self, of):
        evt_ref_list = self.person.get_event_ref_list()

        if not evt_ref_list:
            return

        db = self.report.database

        of.write('\t<div id="events" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Events'))
        of.write('\t\t<table class="infolist">\n')

        # table head
        of.write('\t\t\t<thead>\n')
        of.write('\t\t\t\t<tr>\n')
        for h in (_('event|Type'), _('Date'), _('Place'), _('Description'), _('Notes')):
            of.write('\t\t\t\t\t<th>%s</th>\n' % h)
        of.write('\t\t\t\t</tr>\n')
        of.write('\t\t\t</thead>\n')
        of.write('\t\t\t<tbody>\n')

        for event_ref in evt_ref_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event:
                self.display_event_row(of, db, event, event_ref)

        of.write('\t\t\t</tbody>\n')
        of.write('\t\t\t<tfoot />\n')

        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_event_row(self, of, db, event, event_ref):
        evt_name = str(event.get_type())

        of.write('\t\t\t\t<tr>\n')

        # Type
        if event_ref.get_role() == EventRoleType.PRIMARY:
            txt = u"%(evt_name)s" % locals()
        else:
            evt_role = event_ref.get_role()
            txt = u"%(evt_name)s (%(evt_role)s)" % locals()
        txt = txt or '&nbsp;'
        of.write('\t\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % txt)

        # Date
        txt = _dd.display(event.get_date_object())
        txt = txt or '&nbsp;'
        of.write('\t\t\t\t\t<td class="ColumnValue Date">%s</td>\n' % txt)

        # Place
        place_handle = event.get_place_handle()
        if place_handle:

            lnk = (self.report.cur_fname, self.page_title, self.gid)
            if place_handle in self.place_list:
                if lnk not in self.place_list[place_handle]:
                    self.place_list[place_handle].append(lnk)
            else:
                self.place_list[place_handle] = [lnk]

            place = self.place_link_str(place_handle,
                                        ReportUtils.place_name(self.report.database, place_handle),
                                        up=True)
        else:
            place = None
        txt = place or '&nbsp;'
        of.write('\t\t\t\t\t<td class="ColumnValue Place">%s</td>\n' % txt)

        # Get the links in super script to the Source References section in the same page
        sref_links = self.get_citation_links(event.get_source_references())
        # Description
        txt = event.get_description()
        txt = txt or '&nbsp;'
        of.write('\t\t\t\t\t<td class="ColumnValue Description">%(txt)s%(sref_links)s</td>\n'
                 % locals())

        # Attributes
        # TODO. See format_event

        # Notes. Deal with list of notes.
        of.write('\t\t\t\t\t<td class="ColumnValue Notes">\n')
        done_first_note = False
        notelist = event.get_note_list()
        notelist.extend(event_ref.get_note_list())
        if notelist:
            of.write('\t\t\t\t\t\t<ol>\n')
        else:
            of.write('\t\t\t\t\t\t&nbsp;\n')
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            if note:
                note_text = note.get()
                if note_text:
                    if note.get_format():
                        txt = u"<pre>%s</pre>" % note_text
                    else:
                        # TODO. Decide what to do with multiline notes.
                        txt = u" ".join(note_text.split("\n"))
                    txt = txt or '&nbsp;'
                    of.write('\t\t\t\t\t\t\t<li>%s</li>\n' % txt)
        if notelist:
            of.write('\t\t\t\t\t\t</ol>\n')
        of.write('\t\t\t\t\t</td>\n')

        of.write('\t\t\t\t</tr>\n')

    def display_addresses(self, of):
        alist = self.person.get_address_list()

        if not alist:
            return

        of.write('\t<div id="addresses" class="subsection">\n')
        of.write('\t\t<h4>%s</h4>\n' % _('Addresses'))
        of.write('\t\t<table class="infolist">\n')

        for addr in alist:
            location = ReportUtils.get_address_str(addr)
            location += self.get_citation_links(addr.get_source_references())
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
        of.write("\t\t\t\t\t\t<li>")
        if child_handle in self.ind_list:
            child_name = _nd.display(child)
            url = self.report.build_url_fname_html(child_handle, 'ppl', True)
            self.person_link(of, url, child_name, gid)
        else:
            of.write(_nd.display(child))
        of.write(u"</li>\n")

    def display_parent(self, of, handle, title, rel):
        db = self.report.database
        person = db.get_person_from_handle(handle)
        of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % title)
        of.write('\t\t\t\t<td class="ColumnValue">')
        gid = person.gramps_id
        if handle in self.ind_list:
            url = self.report.build_url_fname_html(handle, 'ppl', True)
            self.person_link(of, url, _nd.display(person), gid)
        else:
            of.write(_nd.display(person))
        if rel and rel != gen.lib.ChildRefType(gen.lib.ChildRefType.BIRTH):
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
                frel = None
                mrel = None
                sibling = set()
                child_handle = self.person.get_handle()
                child_ref_list = family.get_child_ref_list()
                for child_ref in child_ref_list:
                    if child_ref.ref == child_handle:
                        frel = child_ref.get_father_relation()
                        mrel = child_ref.get_mother_relation()
                        break

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
                    childlist = [child_ref.ref for child_ref in child_ref_list]
                    for child_handle in childlist:
                        sibling.add(child_handle)   # remember that we've already "seen" this child
                        if child_handle != self.person.handle:
                            self.display_child_link(of, child_handle)
                    of.write('\t\t\t\t\t</ol>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')

                # Also try to identify half-siblings
                half_siblings = set()

                # if we have a known father...
                showallsiblings = self.report.options['showhalfsiblings']
                if father_handle and showallsiblings:
                    # 1) get all of the families in which this father is involved
                    # 2) get all of the children from those families
                    # 3) if the children are not already listed as siblings...
                    # 4) then remember those children since we're going to list them
                    father = db.get_person_from_handle(father_handle)
                    for family_handle in father.get_family_handle_list():
                        family = db.get_family_from_handle(family_handle)
                        for half_child_ref in family.get_child_ref_list():
                            half_child_handle = half_child_ref.ref
                            if half_child_handle not in sibling:
                                if half_child_handle != self.person.handle:
                                    # we have a new step/half sibling
                                    half_siblings.add(half_child_handle)

                # do the same thing with the mother (see "father" just above):
                if mother_handle and showallsiblings:
                    mother = db.get_person_from_handle(mother_handle)
                    for family_handle in mother.get_family_handle_list():
                        family = db.get_family_from_handle(family_handle)
                        for half_child_ref in family.get_child_ref_list():
                            half_child_handle = half_child_ref.ref
                            if half_child_handle not in sibling:
                                if half_child_handle != self.person.handle:
                                    # we have a new half sibling
                                    half_siblings.add(half_child_handle)

                # now that we have all of the half-siblings, print them out
                if len(half_siblings) > 0:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Half Siblings"))
                    of.write('\t\t\t\t<td class="ColumnValue">\n')
                    of.write('\t\t\t\t\t<ol>\n')
                    for child_handle in half_siblings:
                        self.display_child_link(of, child_handle)
                    of.write('\t\t\t\t\t</ol>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')

                # get step-siblings
                step_siblings = set()
                if showallsiblings:

                    # to find the step-siblings, we need to identify
                    # all of the families that can be linked back to
                    # the current person, and then extract the children
                    # from those families
                    all_family_handles = set()
                    all_parent_handles = set()
                    tmp_parent_handles = set()

                    # first we queue up the parents we know about
                    if mother_handle:
                        tmp_parent_handles.add(mother_handle)
                    if father_handle:
                        tmp_parent_handles.add(father_handle)

                    while len(tmp_parent_handles) > 0:
                        # pop the next parent from the set
                        parent_handle = tmp_parent_handles.pop()

                        # add this parent to our official list
                        all_parent_handles.add(parent_handle)

                        # get all families with this parent
                        parent = db.get_person_from_handle(parent_handle)
                        for family_handle in parent.get_family_handle_list():

                            all_family_handles.add(family_handle)

                            # we already have 1 parent from this family
                            # (see "parent" above) so now see if we need
                            # to queue up the other parent
                            family = db.get_family_from_handle(family_handle)
                            tmp_mother_handle = family.get_mother_handle()
                            if  tmp_mother_handle and \
                                tmp_mother_handle != parent and \
                                tmp_mother_handle not in tmp_parent_handles and \
                                tmp_mother_handle not in all_parent_handles:
                                tmp_parent_handles.add(tmp_mother_handle)
                            tmp_father_handle = family.get_father_handle()
                            if  tmp_father_handle and \
                                tmp_father_handle != parent and \
                                tmp_father_handle not in tmp_parent_handles and \
                                tmp_father_handle not in all_parent_handles:
                                tmp_parent_handles.add(tmp_father_handle)

                    # once we get here, we have all of the families
                    # that could result in step-siblings; note that
                    # we can only have step-siblings if the number
                    # of families involved is > 1

                    if len(all_family_handles) > 1:
                        while len(all_family_handles) > 0:
                            # pop the next family from the set
                            family_handle = all_family_handles.pop()
                            # look in this family for children we haven't yet seen
                            family = db.get_family_from_handle(family_handle)
                            for step_child_ref in family.get_child_ref_list():
                                step_child_handle = step_child_ref.ref
                                if step_child_handle not in sibling and \
                                       step_child_handle not in half_siblings and \
                                       step_child_handle != self.person.handle:
                                    # we have a new step sibling
                                    step_siblings.add(step_child_handle)

                # now that we have all of the step-siblings, print them out
                if len(step_siblings) > 0:
                    of.write('\t\t\t<tr>\n')
                    of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Step Siblings"))
                    of.write('\t\t\t\t<td class="ColumnValue">\n')
                    of.write('\t\t\t\t\t<ol>\n')

                    for child_handle in step_siblings:
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
        for family_handle in family_list:
            family = db.get_family_from_handle(family_handle)
            self.display_spouse(of, family)
            childlist = family.get_child_ref_list()
            if childlist:
                of.write('\t\t\t<tr>\n')
                of.write('\t\t\t\t<td class="ColumnType">&nbsp;</td>\n')
                of.write('\t\t\t\t<td class="ColumnAttribute">%s</td>\n' % _("Children"))
                of.write('\t\t\t\t<td class="ColumnValue">\n')
                of.write('\t\t\t\t\t<ol>\n')
                childlist = [child_ref.ref for child_ref in childlist]
                # TODO. Optionally sort on birthdate
                for child_handle in childlist:
                    self.display_child_link(of, child_handle)
                of.write('\t\t\t\t\t</ol>\n')
                of.write('\t\t\t\t</td>\n')
                of.write('\t\t\t</tr>\n')
        of.write('\t\t</table>\n')
        of.write('\t</div>\n\n')

    def display_spouse(self, of, family):
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
                url = self.report.build_url_fname_html(spouse.handle, 'ppl', True)
                self.person_link(of, url, spouse_name, gid)
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
            if attrType:
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
                        of.write(u"<br />".join(text.split("\n")))
                    of.write('</p>\n')
                    of.write('\t\t\t\t</td>\n')
                    of.write('\t\t\t</tr>\n')

    def pedigree_person(self, of, person):
        person_name = _nd.display(person)
        if person.handle in self.ind_list:
            url = self.report.build_url_fname_html(person.handle, 'ppl', True)
            self.person_link(of, url, person_name)
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
                of.write('\t\t\t\t\t\t\t\t\t\t</ol>\n')
                of.write('\t\t\t\t\t\t\t\t\t</li>\n')
            else:
                of.write('</li>\n')

    # TODO. This function must be converted similar to display_ind_events and display_event_row
    def format_event(self, event, event_ref):
        db = self.report.database
        lnk = (self.report.cur_fname, self.page_title, self.gid)
        descr = event.get_description()
        place_handle = event.get_place_handle()
        if place_handle:
            if place_handle in self.place_list:
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

        if date and place:
            text = _('%(date)s <span class="preposition">at</span> %(place)s') % { 'date': date, 'place': place }
        elif place:
            text = _('<span class="preposition">at</span> %(place)s') % { 'place': place }
        elif date:
            text = date
        else:
            text = ''
        if descr:
            if text:
                text += "<br />"
            text += descr

        text += self.get_citation_links(event.get_source_references())

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
                    text += u'\n\t\t\t\t\t<p class="EventNote">\n\t\t\t\t\t'
                    if format:
                        text += u"<pre>%s</pre>" % note_text
                    else:
                        text += "<br />"
                        text += u"<br />".join(note_text.split("\n"))
                    text += u'\n\t\t\t\t\t</p>\n\t\t\t\t'
        return text

    def get_citation_links(self, source_ref_list):
        gid_list = []
        lnk = (self.report.cur_fname, self.page_title, self.gid)

        for sref in source_ref_list:
            handle = sref.get_reference_handle()
            gid_list.append(sref)

            if handle in self.src_list:
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

        if livinginfo != _INCLUDE_LIVING_VALUE:
            self.database = LivingProxyDb(self.database,
                                          livinginfo,
                                          None,
                                          yearsafterdeath)

        filters_option = menu.get_option_by_name('filter')
        self.filter = filters_option.get_filter()

        self.copyright = self.options['cright']
        self.target_path = self.options['target']
        self.ext = self.options['ext']
        self.css = self.options['css']
        self.encoding = self.options['encoding']
        self.title = self.options['title']
        self.inc_gallery = self.options['gallery']
        self.inc_contact = self.options['contactnote'] or \
                           self.options['contactimg']
        self.inc_download = self.options['incdownload']
        self.use_archive = self.options['archive']
        self.use_intro = self.options['intronote'] or \
                         self.options['introimg']
        self.use_home = self.options['homenote'] or \
                        self.options['homeimg']
        self.use_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # either include the gender graphics or not?
        self.graph = self.options['graph']

        if self.use_home:
            self.index_fname = "index"
            self.surname_fname = "surnames"
            self.intro_fname = "introduction"
        elif self.use_intro:
            self.index_fname = None
            self.surname_fname = "surnames"
            self.intro_fname = "index"
        else:
            self.index_fname = None
            self.surname_fname = "index"
            self.intro_fname = None

        self.archive = None
        self.cur_fname = None            # Internal use. The name of the output file, 
                                         # to be used for the tar archive.
        self.string_io = None
        if self.use_archive:
            self.html_dir = None
        else:
            self.html_dir = self.target_path
        self.warn_dir = True        # Only give warning once.
        self.photo_list = {}

    def write_report(self):
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name is None:
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

        self.progress = Utils.ProgressMeter(_("Narrated Web Site Report"), '')

        # Build the person list
        ind_list = self.build_person_list()

        # copy all of the neccessary files
        self.copy_narrated_files()

        place_list = {}
        source_list = {}

        self.base_pages()
        self.person_pages(ind_list, place_list, source_list)
        self.surname_pages(ind_list)
        self.place_pages(place_list, source_list)
        self.source_pages(source_list)
        if self.inc_gallery:
            self.gallery_pages(source_list)
        # Build source pages a second time to pick up sources referenced
        # by galleries
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
        self.progress.set_pass(_('Applying Filter...'), len(ind_list))
        ind_list = self.filter.apply(self.database, ind_list, self.progress)

        return ind_list

    def copy_narrated_files(self):
        """
        Copy all of the CSS and image files for Narrated Web
        """

        # copy behaviour stylesheet
        fname = os.path.join(const.DATA_DIR, "behaviour.css")
        self.copy_file(fname, "behaviour.css", "styles")

        # copy screen stylesheet
        if self.css:
            fname = os.path.join(const.DATA_DIR, self.css)
            self.copy_file(fname, _NARRATIVESCREEN, "styles")

        # copy printer stylesheet
        fname = os.path.join(const.DATA_DIR, "Web_Print-Default.css")
        self.copy_file(fname, _NARRATIVEPRINT, "styles")

        imgs = []

        # Copy Mainz Style Images
        if self.css == "Web_Mainz.css":
            imgs += [_WEBBKGD, _WEBHEADER, _WEBMID, _WEBMIDLIGHT]

        # Copy the Creative Commons icon if the Creative Commons
        # license is requested???
        if 0 < self.copyright < len(_CC):
            imgs += ["somerights20.gif"]

        # include GRAMPS favicon
        imgs += ["favicon.ico"]

        # we need the blank image gif neede by behaviour.css
        imgs += ["blank.gif"]

        # copy Ancestor Tree graphics if needed???
        if self.graph:
            imgs += ["Web_Gender_Female.png",
                 "Web_Gender_FemaleFFF.png",
                 "Web_Gender_Male.png",
                 "Web_Gender_MaleFFF.png"]

        for f in imgs:
            from_path = os.path.join(const.IMAGE_DIR, f)
            self.copy_file(from_path, f, "images")

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

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_NAME, self.surname_fname)

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_COUNT, "surnames_count")

        for (surname, handle_list) in local_list:
            SurnamePage(self, self.title, surname, handle_list)
            self.progress.step()

    def source_pages(self, source_list):

        self.progress.set_pass(_("Creating source pages"), len(source_list))

        SourcesPage(self, self.title, source_list.keys())

        for key in source_list:
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

        GalleryPage(self, self.title)

        prev = None
        total = len(self.photo_list)
        photo_keys = self.photo_list.keys()
        sort = Sort.Sort(self.database)
        photo_keys.sort(sort.by_media_title)

        index = 1
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

    def add_image(self, of, option_name, height=0):
        pic_id = self.options[option_name]
        if pic_id:
            db = self.database
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    newpath, thumb_path = self.prepare_copy_media(obj)
                    self.copy_file(Utils.media_path_full(db, obj.get_path()),
                                    newpath)
                    of.write('\t<img')
                    if height:
                        of.write(' height="%d"' % height)
                    of.write(' src="%s"' % newpath)
                    of.write(' alt="%s"' % obj.get_description())
                    of.write(' />\n')
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

    def build_subdirs(self, subdir, fname, up=False):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.

        For example, this may return "8/1/aec934857df74d36618"
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())
        if up:
            subdirs = ['..']*3 + subdirs
        return subdirs

    def build_path(self, subdir, fname, up=False):
        """
        Return the name of the subdirectory.

        Notice that we DO use os.path.join() here.
        """
        return os.path.join(*self.build_subdirs(subdir, fname, up))

    def build_url_image(self, fname, subdir=None, up=False):
        subdirs = []
        if subdir:
            subdirs.append(subdir)
        if up:
            subdirs = ['..']*3 + subdirs
        return '/'.join(subdirs + [fname])

    def build_url_fname_html(self, fname, subdir=None, up=False):
        return self.build_url_fname(fname, subdir, up) + self.ext

    def build_url_fname(self, fname, subdir=None, up=False):
        """
        Create part of the URL given the filename and optionally the subdirectory.
        If the subdirectory is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.
        If 'up' is True, then "../../../" is inserted in front of the result. 

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        Imagine we run gramps on Windows (heaven forbits), we don't want to
        see backslashes in the URL.
        """
        subdirs = self.build_subdirs(subdir, fname, up)
        return '/'.join(subdirs + [fname])

    def create_file(self, fname, subdir=None):
        if subdir:
            subdir = self.build_path(subdir, fname)
            self.cur_fname = os.path.join(subdir, fname) + self.ext
        else:
            self.cur_fname = fname + self.ext
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io, 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        else:
            if subdir:
                subdir = os.path.join(self.html_dir, subdir)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
            fname = os.path.join(self.html_dir, self.cur_fname)
            of = codecs.EncodedFile(open(fname, "w"), 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        return of

    def close_file(self, of):
        if self.archive:
            tarinfo = tarfile.TarInfo(self.cur_fname)
            tarinfo.size = len(self.string_io.getvalue())
            tarinfo.mtime = time.time()
            if os.sys.platform != "win32":
                tarinfo.uid = os.getuid()
                tarinfo.gid = os.getgid()
            self.string_io.seek(0)
            self.archive.addfile(tarinfo, self.string_io)
            self.string_io = None
            of.close()
        else:
            of.close()
        self.cur_fname = None

    def add_lnkref_to_photo(self, photo, lnkref):
        handle = photo.get_handle()
        # FIXME. Is it OK to add to the photo_list of report?
        photo_list = self.photo_list
        if handle in photo_list:
            if lnkref not in photo_list[handle]:
                photo_list[handle].append(lnkref)
        else:
            photo_list[handle] = [lnkref]

    def prepare_copy_media(self, photo):
        handle = photo.get_handle()
        ext = os.path.splitext(photo.get_path())[1]
        real_path = os.path.join(self.build_path('images', handle), handle + ext)
        thumb_path = os.path.join(self.build_path('thumb', handle), handle + '.png')
        return real_path, thumb_path

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present and if the target is not an archive,
        then the destination directory will be created.

        Normally 'to_fname' will be just a filename, without directory path.

        'to_dir' is the relative path name in the destination root. It will
        be prepended before 'to_fname'.
        """
        if self.archive:
            dest = os.path.join(to_dir, to_fname)
            self.archive.add(from_fname, dest)
        else:
            dest = os.path.join(self.html_dir, to_dir, to_fname)

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

class NavWebOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

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
        Add options to the menu for the web site.
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

        title = StringOption(_("Web site title"), _('My Family Tree'))
        title.set_help(_("The title of the web site"))
        menu.add_option(category_name, "title", title)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on web site"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self.__update_filters()

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1] )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)

        css = EnumeratedListOption(_('StyleSheet'), _CSS_FILES[0][1])
        for style in _CSS_FILES:
            css.add_item(style[1], style[0])
        css.set_help( _('The stylesheet to be used for the web page'))
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
                                             _INCLUDE_LIVING_VALUE )
        self.__living.add_item(LivingProxyDb.MODE_EXCLUDE_ALL, 
                               _("Exclude"))
        self.__living.add_item(LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY, 
                               _("Include Last Name Only"))
        self.__living.add_item(LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY, 
                               _("Include Full Name Only"))
        self.__living.add_item(_INCLUDE_LIVING_VALUE, 
                               _("Include"))
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

        showallsiblings = BooleanOption(_("Include half and/ or "
                                           "step-siblings on the individual "
                                           "pages"), False)
        showallsiblings.set_help(_( "Whether to include half and/ or "
                                    "step-siblings with the parents and "
                                    "siblings"))
        menu.add_option(category_name, 'showhalfsiblings', showallsiblings)

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
        if self.__living.get_value() == _INCLUDE_LIVING_VALUE:
            self.__yearsafterdeath.set_available(False)
        else:
            self.__yearsafterdeath.set_available(True)

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

        if surname in sname_sub:
            sname_sub[surname].append(person_handle)
        else:
            sname_sub[surname] = [person_handle]

    sorted_lists = []
    temp_list = sname_sub.keys()
    temp_list.sort(locale.strcoll)
    for name in temp_list:
        slist = [(sortnames[x], x) for x in sname_sub[name]]
        slist.sort(lambda x, y: locale.strcoll(x[0], y[0]))
        entries = [x[1] for x in slist]
        sorted_lists.append((name, entries))

    return sorted_lists

# Modified _get_regular_surname from WebCal.py to get prefix, first name, and suffix
def _get_prefix_suffix_name(sex, name):
    """ Will get prefix and suffix for all people passed through it """

    first = name.get_first_name()
    prefix = name.get_surname_prefix()
    if prefix:
        first = prefix + " " + first
    if sex == gen.lib.Person.FEMALE:
        return first
    else: 
        suffix = name.get_suffix()
        if suffix:
            first = first + ", " + suffix
    return first

def get_person_keyname(db, handle):
    """ .... """ 
    person = db.get_person_from_handle(handle)
    return person.get_primary_name().surname

def get_place_keyname(db, handle):
    """ ... """

    return ReportUtils.place_name(db, handle)  

def get_first_letters(db, handle_list, key):
    """ key is _PLACE or _PERSON ...."""
 
    first_letters = []

    for handle in handle_list:
        if key == _PERSON:
            keyname = get_person_keyname(db, handle)
        else:
            keyname = get_place_keyname(db, handle) 

        if keyname:
            c = normalize('NFC', keyname)[0].upper()
            first_letters.append(c)

    return first_letters

# ------------------------------------------
#
#            Register Plugin
#
# -------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'navwebpage',
    category = CATEGORY_WEB,
    report_class = NavWebReport,
    options_class = NavWebOptions,
    modes = PluginManager.REPORT_MODE_GUI | PluginManager.REPORT_MODE_CLI,
    translated_name = _("Narrated Web Site"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces web (HTML) pages for individuals, or a set of "
                    "individuals"),
  )
