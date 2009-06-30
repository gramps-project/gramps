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

# $Id:$

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
from __future__ import with_statement
import os, sys
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import time, datetime
import locale
import shutil
import codecs
import tarfile
import tempfile
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
from gen.lib import UrlType, EventType, Person, date, Date, ChildRefType, \
                    FamilyRelType, NameType, Name
import const
import Sort
from gen.plug import PluginManager
from gen.plug.menu import PersonOption, NumberOption, StringOption, \
                          BooleanOption, EnumeratedListOption, FilterOption, \
                          NoteOption, MediaOption, DestinationOption
from ReportBase import (Report, ReportUtils, MenuReportOptions, CATEGORY_WEB,
                        Bibliography, CSS_FILES )
import Utils
from gui.utils import ProgressMeter
import ThumbNails
import ImgManip
import Mime
from Utils import probably_alive, xml_lang
from QuestionDialog import ErrorDialog, WarningDialog
from BasicUtils import name_displayer as _nd
from DateHandler import displayer as _dd
from DateHandler import parser as _dp
from gen.proxy import PrivateProxyDb, LivingProxyDb
from gen.lib.eventroletype import EventRoleType
from libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS

# import HTML Class from
# src/plugins/lib/libhtml.py
from libhtml import Html

# import styled notes from
# src/plugins/lib/libhtmlbackend.py
from libhtmlbackend import HtmlBackend
#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
# define clear blank line for proper styling
fullclear = Html('div', class_='fullclear', inline=True)

# Names for stylesheets
_NARRATIVESCREEN = 'narrative-screen.css'
_NARRATIVEPRINT = 'narrative-print.css'

# variables for alphabet_navigation()
_PERSON, _PLACE = 0, 1

# Web page filename extensions
_WEB_EXT = ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']

_INCLUDE_LIVING_VALUE = 99 # Arbitrary number
_NAME_COL  = 3

_DEFAULT_MAX_IMG_WIDTH = 800   # resize images that are wider than this (settable in options)
_DEFAULT_MAX_IMG_HEIGHT = 600  # resize images that are taller than this (settable in options)
_WIDTH = 160
_HEIGHT = 50
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5

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

def conf_priv(obj):
    if obj.get_privacy() != 0:
        return ' priv="%d"' % obj.get_privacy()
    else:
        return ''

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

class BasePage(object):
    """
    This is the base class to write certain HTML pages.
    """
    
    def __init__(self, report, title, gid=None):
        """
        report - instance of NavWebReport
        title - text for the <title> tag
        gid - Gramps ID
        """

        # class to do conversion of styled notes to html markup
        self._backend = HtmlBackend()

        self.report = report
        self.title_str = title
        self.gid = gid
        self.src_list = {}

        self.page_title = ""

        self.author = Utils.get_researcher().get_name()
        if self.author:
            self.author = self.author.replace(',,,', '')
        self.up = False

        # TODO. All of these attributes are not necessary, because we have
        # also the options in self.options.  Besides, we need to check which
        # are still required.
        self.html_dir = report.options['target']
        self.ext = report.options['ext']
        self.noid = report.options['nogid']
        self.linkhome = report.options['linkhome']
        self.create_media = report.options['gallery']

#################################################
#
# Will produce styled notes for NarrativeWeb by using:
# src/plugins/lib/libhtmlbackend.py
#
#################################################

    def styled_note(self, styledtext, format):
        """
         styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        """
        text = str(styledtext)

        if not text:
            return ''

        s_tags = styledtext.get_tags()
        #FIXME: following split should be regex to match \n\s*\n instead?
        markuptext = self._backend.add_markup_from_styled(text, s_tags,
                                                         split='\n\n')
        htmllist = Html('div', id='grampsstylednote')
        if format == 1:
            #preformatted, retain whitespace.
            #so use \n\n for paragraph detection
            #FIXME: following split should be regex to match \n\s*\n instead?
            htmllist += Html('pre', indent=None, inline=True)
            for line in markuptext.split('\n\n'):
                htmllist += Html('p')
                for realline in line.split('\n'):
                    htmllist += realline
                    htmllist += Html('br')

        elif format == 0:
            #flowed
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                htmllist += Html('p')
                htmllist += line

        return htmllist

# ---------------------------------------------------------------------------------------
#
#              # Web Page Fortmatter and writer                   
#
# ---------------------------------------------------------------------------------------

    def mywriter(self, htmlinstance, of):
        """
        Will format, write, and close the file

        of -- open file that is being written to
        htmlinstance -- web page created with libhtml
            src/plugins/lib/libhtml.py
        """
 
        htmlinstance.write(lambda line: of.write(line + '\n')) 

        # closes the file
        self.report.close_file(of)

    def write_repository(self, repo, handle):
        """
        will write the repository information
        """

        # begin repositories table and table head
        with Html('table', class_='infolist repolist') as table:

            # begin table body
            tbody = Html('tbody')
            table += tbody

            # repository Type   
            rtype = repo.type.xml_str()
            if rtype:
                trow = Html('tr')
                tbody += trow
                tcell1 = Html('td', _('Type'), class_='ColumnAttribute',inline=True)
                tcell2 = Html('td', rtype, class_='ColumnValue', inline=True)
                trow += (tcell1, tcell2)

            # begin summaryarea division
            with Html('div', id='summaryarea') as summaryarea:
                table += summaryarea

                index = 0
                # repository address division
                addresses = self.write_address_list(repo, index+1)
                if addresses is not None:
                    summaryarea += addresses   

                # repository: urllist
                urllist = self.display_url_list(repo.get_url_list())
                if urllist is not None:
                    summaryarea += urllist

                # reposity: notelist
                notelist = self.display_note_list(repo.get_note_list()) 
                if notelist is not None:
                    summaryarea += notelist

#                # repository: references
#                # TODO: see if possible?
#                references = self.display_references(repo.get_references())
#                if references is not None:
#                    summaryarea += references

        # return table to its callers
        return table

    def get_copyright_license(self, copyright, up=False):
        """
        will return either the text or image of the copyright license
        """

        text = ''
        if copyright == 0:
            if self.author:
                year = date.Today().get_year()
                text = '&copy; %(year)d %(person)s' % {
                    'person' : self.author,
                    'year' : year}
        elif 0 < copyright <= len(_CC):
            # Note. This is a URL
            fname = '/'.join(["images", "somerights20.gif"])
            url = self.report.build_url_fname(fname, None, up=False)
            text = _CC[copyright] % {'gif_fname' : url}

        # return text or image to its callers
        return text

    def get_name(self, person, maiden_name = None):
        """ 
        Return person's name, unless maiden_name given, unless married_name 
        listed. 
        """

        # name_format is the name format that you set in options
        name_format = self.report.options['name_format']

        # Get all of a person's names
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == NameType.MARRIED:
                married_name = name
                break # use first
        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = Name(married_name)
            else:
                name = Name(primary_name)
                name.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def write_footer(self):
        """
        Will create and display the footer section of each page...
        """
        db = self.report.database

        # begin footer division
        with Html('div', id='footer') as section:

            footer_note = self.report.options['footernote']
            if footer_note:
                note = db.get_note_from_gramps_id(footer_note)
                note_text = note.get()
                if note_text: 
                    user_footer = Html('div', id='user_footer')
                    section += user_footer
 
                    # styled notes
                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                     note.get_format())
                    if htmlnotetext:
                        text = htmlnotetext
                    else:
                        text = Html('p', note_text) 
                    user_footer += text

            value = _dd.display(date.Today())
            msg = _('Generated by <a href="%(homepage)s">'
                          'GRAMPS</a> on %(date)s') % {
                          'date': value, 'homepage' : const.URL_HOMEPAGE
                          }

            # optional "link-home" feature; see bug report #2736
            if self.report.options['linkhome']:
                home_person = db.get_default_person()
                if home_person:
                    home_person_url = self.report.build_url_fname_html(home_person.handle, 'ppl', self.up)
                    home_person_name = self.get_name(home_person)
                    msg += _(' Created for <a href="%s">%s</a>') % (
                                home_person_url, home_person_name)

            # creation date
            section += Html('p', msg, id='createdate')

            # get copyright license for all pages
            copy_nr = self.report.copyright

            text = ''
            if copy_nr == 0:
                if self.author:
                    year = date.Today().get_year()
                    text = '&copy; %(year)d %(person)s' % {
                               'person' : self.author,
                               'year' : year}
            elif 0 < copy_nr <= len(_CC):
                # Note. This is a URL
                fname = '/'.join(["images", "somerights20.gif"])
                url = self.report.build_url_fname(fname, None, self.up)
                text = _CC[copy_nr] % {'gif_fname' : url}
            section += Html('p', text, id='copyright')

            # add clear line for proper styling
            section += fullclear

        # return footer to its caller
        return section

    def write_header(self, title):
        """
        Note. 'title' is used as currentsection in the navigation links and
        as part of the header title.
        """
        db = self.report.database

        # Header contants
        xmllang = xml_lang()
        _META1 = 'name="generator" content="%s %s %s"' % (
                    const.PROGRAM_NAME, const.VERSION, const.URL_HOMEPAGE
                    )
        _META2 = 'name="author" content="%s"' % self.author

        page, head, body = Html.page('%s - %s' % 
                                    (html_escape(self.title_str), 
                                     html_escape(title)),
                                    self.report.encoding, xmllang
                                    )

        # create additional meta tags
        meta = (Html('meta', attr = _META1) + 
                Html('meta', attr = _META2, indent=False)
               )

        # Link to media reference regions behaviour stylesheet
        fname = '/'.join(["styles", "behaviour.css"])
        url1= self.report.build_url_fname(fname, None, self.up)

        # Link to _NARRATIVESCREEN  stylesheet
        fname = '/'.join(["styles", _NARRATIVESCREEN])
        url2 = self.report.build_url_fname(fname, None, self.up)

        # Link to _NARRATIVEPRINT stylesheet
        fname = '/'.join(["styles", _NARRATIVEPRINT])
        url3 = self.report.build_url_fname(fname, None, self.up)

        # Link to GRAMPS favicon
        fname = '/'.join(['images', 'favicon.ico'])
        url4 = self.report.build_url_image('favicon.ico', 'images', self.up)

        # create stylesheet and favicon links
        links = [Html('link', href=url4, type='image/x-icon', rel='shortcut icon'),
             Html('link', href=url1, type='text/css', media='screen', rel='stylesheet'),
             Html('link', href=url2, type='text/css', media='screen', rel='stylesheet'),
             Html('link', href=url3, type='text/css', media='print', rel='stylesheet')
             ]

        # add additional meta and link tags
        head += meta
        head += links

        # replace standard body element with custom one
        body.attr = 'id= "NarrativeWeb"'

        # begin header section
        headerdiv = (Html('div', id='header') +
            Html('h1', html_escape(self.title_str), id='SiteTitle', inline=True)
            )
        body += headerdiv

        header_note = self.report.options['headernote']
        if header_note:
            note = db.get_note_from_gramps_id(header_note)
            note_text = note.get()
            if note_text:
                user_header = Html('div', id='user_header')
                headerdiv += user_header  
 
                # styled notes
                htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                         note.get_format())
                if htmlnotetext:
                    text = htmlnotetext
                else:
                    text = Html('p', note_text) 
                user_header += text

        # Begin Navigation Menu
        navigation = self.display_nav_links(title)
        body += navigation

        # return to its caller, page and body
        return page, body

    def display_nav_links(self, currentsection):
        """
        Creates the navigation menu
        """

        navs = [
            (self.report.index_fname,   _('Home'),         self.report.use_home),
            (self.report.intro_fname,   _('Introduction'), self.report.use_intro),
            (self.report.surname_fname, _('Surnames'),     True),
            ('individuals',             _('Individuals'),  True),
            ('places',                  _('Places'),       True),
            ('media',                   _('Media'),        self.create_media),
            ('download',                _('Download'),     self.report.inc_download),
            ('contact',                 _('Contact'),      self.report.use_contact),
            ('sources',                 _('Sources'),      True),
            ('repositories',            _('Repositories'), self.report.inc_repository), 
                ]

        navigation = Html('div', id='navigation')
        ul = Html('ul')

        navs = ((u, n) for u, n, c in navs if c)
        for url_fname, nav_text in navs:

            if not _has_webpage_extension(url_fname):
                url_fname += self.ext

            url = self.report.build_url_fname(url_fname, None, self.up)

            # Define 'currentsection' to correctly set navlink item CSS id
            # 'CurrentSection' for Navigation styling.
            # Use 'self.report.cur_fname' to determine 'CurrentSection' for individual
            # elements for Navigation styling.

            # Figure out if we need <li class="CurrentSection"> of just plain <li>
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

            cs = cs and 'class="CurrentSection"' or ''
            ul += (Html('li', attr=cs, inline=True) +
                   Html('a', nav_text, href=url)
                  )

        navigation += ul

        # return navigation menu bar to its caller
        return navigation

    def display_first_image_as_thumbnail( self, photolist=None):
        db = self.report.database 

        if not photolist or not self.create_media:
            return None

        photo_handle = photolist[0].get_reference_handle()
        photo = db.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        # begin snapshot division
        with Html('div', class_='snapshot') as snapshot:

            if mime_type:
                try:
                    lnkref = (self.report.cur_fname, self.page_title, self.gid)
                    self.report.add_lnkref_to_photo(photo, lnkref)
                    real_path, newpath = self.report.prepare_copy_media(photo)

                    # TODO. Check if build_url_fname can be used.
                    newpath = '/'.join(['..']*3 + [newpath])

                    # begin hyperlink
                    # description is given only for the purpose of the alt tag in img element
                    snapshot += self.media_link(photo_handle, newpath, '', up=True)

                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))
            else:

                # get media description
                descr = photo.get_description()

                # begin hyperlink
                snapshot += self.doc_link(photo_handle, descr, up=True)

                lnk = (self.report.cur_fname, self.page_title, self.gid)
                # FIXME. Is it OK to add to the photo_list of report?
                photo_list = self.report.photo_list
                if photo_handle in photo_list:
                    if lnk not in photo_list[photo_handle]:
                        photo_list[photo_handle].append(lnk)
                else:
                    photo_list[photo_handle] = [lnk]

        # return snapshot division to its callers
        return snapshot

    def display_additional_images_as_gallery( self, photolist=None):

        if not photolist or not self.create_media:
            return None
        db = self.report.database

        # begin individualgallery division
        with Html('div', class_='subsection', id='indivgallery') as section: 

            # begin section title
            section += Html('h4', _('Gallery'), inline=True)

            # begin table row
            trow = Html('tr')
            section += trow

            displayed = []
            for mediaref in photolist:

                photo_handle = mediaref.get_reference_handle()
                photo = db.get_object_from_handle(photo_handle)
                if photo_handle in displayed:
                    continue
                mime_type = photo.get_mime_type()

                # get media description
                descr = photo.get_description()

                if mime_type:
                    try:
                        lnkref = (self.report.cur_fname, self.page_title, self.gid)
                        self.report.add_lnkref_to_photo(photo, lnkref)
                        real_path, newpath = self.report.prepare_copy_media(photo)
                        # TODO. Check if build_url_fname can be used.
                        newpath = '/'.join(['..']*3 + [newpath])
     
                        # begin hyperlink
                        trow += self.media_link(photo_handle, newpath, descr, up=True)

                    except (IOError, OSError), msg:
                        WarningDialog(_("Could not add photo to page"), str(msg))
                else:
                    try:

                        # begin hyperlink
                        trow += self.doc_link(photo_handle, descr, up=True)

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

        # add clearline for proper styling
        section += fullclear

        # return indivgallery division to its caller
        return section

    def display_note_list(self, notelist=None):

        if not notelist:
            return None
        db = self.report.database

        # begin narrative division
        with Html('div', class_='subsection', id='narrative') as section:

            for notehandle in notelist:
                note = db.get_note_from_handle(notehandle)
                note_text = note.get()
                try:
                    note_text = unicode(note_text)
                except UnicodeDecodeError:
                    note_text = unicode(str(note_text), errors='replace')

                if note_text:
                    section += Html('h4', _('Narrative'), inline=True)

                    # styled notes
                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                         note.get_format())
                    if htmlnotetext:
                        section += htmlnotetext
                    else:
                        section += Html('p', note_text)

        # return notes to its callers
        return section

    def display_url_list(self, urllist=None):

        if not urllist:
            return None

        # begin web links division
        with Html('div', class_='subsection', id='weblinks') as section:

            # begin web title
            title = Html('h4', _('Weblinks'), inline=True)  
            section += title

            # ordered list
            ordered = Html('ol')
            section += ordered

            for url in urllist:
                uri = url.get_path()
                descr = url.get_description()
                if not descr:
                    descr = uri
                if url.get_type() == UrlType.EMAIL and not uri.startswith("mailto:"):
                    ordered += Html('li') + Html('a',descr,  href='mailto:%s' % url)

                elif url.get_type() == UrlType.WEB_HOME and not uri.startswith("http://"):
                    ordered += Html('li') + Html('a', descr, href='http://%s' % url)

                elif url.get_type() == UrlType.WEB_FTP and not uri.startswith("ftp://"):
                    ordered += Html('li') + Html('a', descr, href='ftp://%s' % url)
                else:
                    ordered += Html('li') + Html('a', descr, href=url)
                
        # return web links to its caller
        return section

    def display_source_refs(self, bibli):

        if bibli.get_citation_count() == 0:
            return None

        db = self.report.database 

        # Source References division and title
        with Html('div', class_='subsection', id='sourcerefs') as section:
            section += Html('h4', _('Source References'), inline=True)

            ordered = Html('ol')
            section += ordered
            list = Html('li')
            ordered += list

            for cindex, citation in enumerate(bibli.get_citation_list()):
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
            
                list += self.source_link(source.handle, title, cindex+1, source.gramps_id, True)

                ordered1 = Html('ol')
                list += ordered1
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
                        note_text = note.get()
                        if note_text:
         
                            # styled notes
                            htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                            note.get_format())
                            if htmlnotetext:
                                text = htmlnotetext
                            else:
                                text = Html('p', note_text) 
                            tmp.append("%s: %s" % (_('Text'), text))
                    if len(tmp):
                        ordered1 += Html('li') + (
                            Html('a', tmp, name="sref%d%s" % (cindex+1, key))
                            )

        # return sourcerefs division to its caller
        return section

    def display_references(self, handlelist, up=False):

        if not handlelist:
            return None

        # begin references division and title
        with Html('div', class_='subsection', id='references') as section:
            section += Html('h4', _('References'), inline=True)

            ordered = Html('ol')
            section += ordered 
            sortlist = sorted(handlelist, key=lambda x:locale.strxfrm(x[1]))
        
            for (path, name, gid) in sortlist:
                list = Html('li')
                ordered += list

                # Note. 'path' already has a filename extension
                url = self.report.build_url_fname(path, None, self.up)
                list += self.person_link(url, name, None, gid)

        # return references division to its caller
        return section

    def person_link(self, url, person, name_style, gid=None, thumbnailUrl=None):
        """
        creates a hyperlink for a person
        namestyle = False -- first and suffix only
                         = True  -- name displayed in name_format variable
                         = None -- person is name 
        """

        # see above for explanation
        if name_style:
            person_name = self.get_name(person)
        elif name_style == False:
            person_name = _get_short_name(person.gender, person.primary_name)
        elif name_style == None:    # abnormal specialty situation
            person_name = person

        # 1. start building link to image or person
        hyper = Html('a', href=url)

        # 2. insert thumbnail if there is one, otherwise insert class = "noThumb"
        if thumbnailUrl:
            hyper += (Html('span', class_="thumbnail") +
                      Html('img', src= thumbnailUrl, alt = "Image of " + person_name)
                    )
        else:
            # for proper spacing, force a new line after hyperlink url
            hyper.attr += ' class= "noThumb"'

        # 3. insert the person's name
        hyper += person_name

        # 3. insert gramps id if requested and available
        if not self.noid and gid:
            hyper += Html('span', '[%s]' % gid, class_="grampsid", inline=True)

        # return hyperlink to its caller
        return hyper

    # TODO. Check img_url of callers
    def media_link(self, handle, img_url, name, up, usedescr=True):
        url = self.report.build_url_fname_html(handle, 'img', up)

        # begin thumbnail division
        with Html('div', class_='thumbnail') as thumbnail:

            # begin hyperlink
            hyper = (Html('a', href=url, title=name) +
                     Html('img', src=img_url, alt=name) +
                     (Html('p', inline=True) + 
                          html_escape(name) if usedescr else ' [Untitled] '
                     )
                    )
            # add hyperlink and description to thumbnail division
            thumbnail += hyper

        # return thumbnail division to its callers
        return thumbnail

    def doc_link(self, handle, name, up, usedescr=True):
        # TODO. Check extension of handle
        url = self.report.build_url_fname(handle, 'img', up)

        # begin thumbnail division
        thumbnail = Html('div', class_='thumbnail')

        # begin hyperlink
        hyper = Html('a', href=url, title=name)
        url = self.report.build_url_image('document.png', 'images', up)
        hyper += Html('img', src=url, alt=html_escape(name))
        if usedescr:
            descr = Html('p', html_escape(name), inline=True)
        else:
            descr = ''

        # add hyperlink and description to thumbnail division
        thumbnail += (hyper, descr)

        # return thumbnail division to its callers
        return thumbnail

    def source_link(self, handle, name, cindex, gid=None, up=False):

        url = self.report.build_url_fname_html(handle, 'src', up)
        # begin hyperlink
        hyper = Html('a', html_escape(name), href=url, title=name)
        if not self.noid and gid:
            hyper += Html('span', '[%s]' % gid, class_='grampsid', inline=True)

        # return hyperlink to its callers
        return hyper

    def repository_link(self, handle, name, cindex, gid=None, up=False):

        url = self.report.build_url_fname_html(handle, 'repo', up)
        # begin hyperlink
        hyper = Html('a', html_escape(name), href=url, title=name)
        if not self.noid and gid:
            hyper += Html('span', '[%s]' % gid, class_='grampsid', inline=True)

        # return hyperlink to its callers
        return hyper

    def place_link(self, handle, name, gid=None, up=False):
        url = self.report.build_url_fname_html(handle, 'plc', up)

        hyper = Html('a', html_escape(name), href=url, title=name)
        if not self.noid and gid:
            hyper += Html('span', ' [%s] ' % gid, class_='grampsid', inline=True)

        # return hyperlink to its callers
        return hyper

class IndividualListPage(BasePage):

    def __init__(self, report, title, person_handle_list):
        BasePage.__init__(self, report, title)
        db = report.database

        # handles for this module for use in partner column
        report_handle_list = person_handle_list

        # plugin variables for this module
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        of = self.report.create_file("individuals")
        indlistpage, body = self.write_header(_('Individuals'))

        # begin Individuals division
        with Html('div', class_='content', id='Individuals') as section:
            body += section

            # Individual List description
            msg = _("This page contains an index of all the individuals in the "
                          "database, sorted by their last names. Selecting the person&#8217;s "
                          "name will take you to that person&#8217;s individual page.")
            section += Html('p', msg, id='description')

            # add alphabet navigation after page msg
            alpha_nav = alphabet_navigation(db, person_handle_list, _PERSON) 
            if alpha_nav is not None:
                section += alpha_nav

            # begin table and table head
            with Html('table', class_='infolist IndividualList') as table:
                section += table
                thead = Html('thead')
                table += thead

                trow = Html('tr')
                thead += trow    

                # Table Header -- Surname and Given name columns
                tcell1 = Html('th', _('Surname'), class_='ColumnSurname', inline=True)
                tcell2 = Html('th', _('Name'), class_='ColumnName', inline=True)
                trow += (tcell1, tcell2)

                # table header -- show birth column
                if showbirth:
                    trow += Html('th', _('Birth'), class_='ColumnBirth', inline=True)

                # table header -- show death column
                if showdeath:
                    trow += Html('th', _('Death'), class_='ColumnDeath', inline=True)

                # table header -- show partmer column
                if showpartner:
                    trow += Html('th', _('Partner'), class_='ColumnPartner', inline=True)

                # table header -- show parents column
                if showparents:
                    trow += Html('th', _('Parents'), class_='ColumnParents', inline=True)

            # begin table body
            tbody = Html('tbody')
            table += tbody

            # list of person handles for this report
            person_handle_list = sort_people(db, person_handle_list)

            for (surname, handle_list) in person_handle_list:
                first = True
                if surname:
                    letter = normalize('NFKC', surname)[0].upper()
                else:
                    letter = u' '
                # See : http://www.gramps-project.org/bugs/view.php?id=2933
                (lang_country, modifier ) = locale.getlocale()
                if lang_country == "sv_SE" and ( letter == u'W' or letter == u'V' ):
                    letter = u'V,W'
                for person_handle in handle_list:
                    person = db.get_person_from_handle(person_handle)

                    # surname column
                    trow = Html('tr')
                    tcell = Html('td', class_='ColumnSurname', inline=True)
                    if first:
                        trow.attr = 'class="BeginSurname"'
                        if surname:
                                    tcell += Html('a', surname, name=letter, title='Letter %s' % letter,
                                        inline=True)
                        else:
                            tcell += '&nbsp;'
                    else:
                        tcell += '&nbsp;'
                    tbody += trow
                    trow += tcell

                    first = False
                    # firstname column
                    tcell = Html('td', class_='ColumnName')
                    trow += tcell
                    url = self.report.build_url_fname_html(person.handle, 'ppl')
                    tcell += self.person_link(url, person, False, person.gramps_id)

                    # birth column
                    if showbirth:
                        tcell = Html('td', class_='ColumnBirth', inline=True)
                        birth = ReportUtils.get_birth_or_fallback(db, person)
                        if birth:
                            birth_date = _dd.display(birth.get_date_object())
                            if birth.get_type() == EventType.BIRTH:
                                tcell += birth_date
                            else:
                                tcell += Html('em', birthdate)
                        else:
                            tcell += '&nbsp;'
                        trow += tcell

                    # death column
                    if showdeath:
                        tcell = Html('td', class_='ColumnDeath', inline=True)
                        death = ReportUtils.get_death_or_fallback(db, person)
                        if death:
                            death_date = _dd.display(death.get_date_object())
                            if death.get_type() == EventType.DEATH:
                                tcell += death_date
                            else:
                                tcell += Html('em', death_date)
                        else:
                            tcell += '&nbsp;'
                        trow += tcell

                    # partner column
                    if showpartner:
                        tcell = Html('td', class_='ColumnPartner')
                        family_list = person.get_family_handle_list()
                        first_family = True
                        partner_name = None
                        if family_list:
                            for family_handle in family_list:
                                family = db.get_family_from_handle(family_handle)
                                partner_handle = ReportUtils.find_spouse(person, family)
                                if partner_handle:
                                    partner = db.get_person_from_handle(partner_handle)
                                    partner_name = self.get_name(partner)
                                    if not first_family:
                                        tcell += ', '  
                                    if partner_handle in report_handle_list:
                                        url = self.report.build_url_fname_html(partner_handle, 'ppl')
                                        tcell += self.person_link(url, partner, name_style=True)
                                    else:
                                        tcell += partner_name
                                    first_family = False
                                else:
                                    tcell += '&nbsp;'
                        else:
                            tcell += '&nbsp;'
                        trow += tcell

                    # parents column
                    if showparents:
                        tcell = Html('td', class_='ColumnParents')
                        parent_handle_list = person.get_parent_family_handle_list()
                        if parent_handle_list:
                            parent_handle = parent_handle_list[0]
                            family = db.get_family_from_handle(parent_handle)
                            father_handle = family.get_father_handle()
                            mother_handle = family.get_mother_handle()
                            father = db.get_person_from_handle(father_handle)
                            mother = db.get_person_from_handle(mother_handle)
                            if father:
                                father_name = self.get_name(father)
                            if mother:
                                mother_name = self.get_name(mother)
                            if mother and father:
                                fathercell = Html('span', father_name, class_='father fatherNmother')
                                mothercell = Html('span', mother_name, class_='mother')
                                tcell += (fathercell, mothercell)
                            elif mother:
                                tcell += Html('span', mother_name, class_='mother')
                            elif father:
                                tcell += Html('span', father_name, class_='father')
                        else:
                            tcell += '&nbsp;'
                        trow += tcell  

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(indlistpage, of)

class SurnamePage(BasePage):

    def __init__(self, report, title, surname, person_handle_list, report_handle_list):
        BasePage.__init__(self, report, title)
        db = report.database

        # module variables
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        of = self.report.create_file(name_to_md5(surname), 'srn')
        self.up = True
        surnamepage, body = self.write_header("%s - %s" % (_('Surname'), surname))

        # begin SurnameDetail division
        with Html('div', id='SurnameDetail', class_='contente') as surnamedetail:
            body += surnamedetail

            # section title
            surnamedetail += Html('h3', html_escape(surname), inline=True)

            msg = _("This page contains an index of all the individuals in the "
                    "database with the surname of %s. Selecting the person&#8217;s name "
                    "will take you to that person&#8217;s individual page.") % surname
            surnamedetail += Html('p', msg, id='description')

            # begin surname table and thead
            with Html('table', class_='infolist surname') as surname_table:
                surnamedetail += surname_table
                with Html('thead') as thead:
                    surname_table += thead
                    tabhead = []
                    tabhead.append('Name')
                    if report.options['showbirth']:
                        tabhead.append('Birth')
                    if report.options['showdeath']:
                        tabhead.append('Death')
                    if report.options['showpartner']:
                        tabhead.append('Partner')
                    if report.options['showparents']:
                        tabhead.append('Parents')
                    with Html('tr') as trow:
                        thead += trow   

                        # now spit out whatever is in table head
                        for column in tabhead:
                            trow += Html('th', _(column), class_='Column%s' % column, 
                                inline=True)

                # begin table body 
                with Html('tbody') as tbody:
                    surname_table += tbody

                    for person_handle in person_handle_list:
 
                        # firstname column
                        person = db.get_person_from_handle(person_handle)
                        trow = Html('tr')
                        tcell = Html('td', class_='ColumnName')
                        url = self.report.build_url_fname_html(person.handle, 'ppl', True)
                        tcell += self.person_link(url, person, False, person.gramps_id)
                        trow += tcell 

                        # birth column
                        if showbirth:
                            tcell = Html('td', class_='ColumnBirth', inline=True)
                            birth = ReportUtils.get_birth_or_fallback(db, person)
                            if birth:
                                birth_date = _dd.display(birth.get_date_object())
                                if birth.get_type() == EventType.BIRTH:
                                    tcell += birth_date
                                else:
                                    tcell += Html('em', birth_date)
                            else:
                                tcell += '&nbsp;'
                            trow += tcell

                        # death column
                        if showdeath:
                            tcell = Html('td', class_='ColumnDeath', inline=True)
                            death = ReportUtils.get_death_or_fallback(db, person)
                            if death:
                                death_date = _dd.display(death.get_date_object())
                                if death.get_type() == EventType.DEATH:
                                    tcell += death_date
                                else:
                                    tcell += Html('em', death_date)
                            else:
                                tcell += '&nbsp;'
                            trow += tcell

                        # partner column
                        if showpartner:
                            tcell = Html('td', class_='ColumnPartner')
                            family_list = person.get_family_handle_list()
                            first_family = True
                            if family_list:
                                for family_handle in family_list:
                                    family = db.get_family_from_handle(family_handle)
                                    partner_handle = ReportUtils.find_spouse(person, family)
                                    if partner_handle:
                                        partner = db.get_person_from_handle(partner_handle)
                                        partner_name = self.get_name(partner)
                                        if not first_family:
                                            tcell += ','
                                        if partner_handle in report_handle_list:
                                            url = self.report.build_url_fname_html(
                                                partner_handle, 'ppl', True) 
                                            tcell += self.person_link(url, partner, name_style=True)
                                        else:
                                            tcell += partner_name
                                    else:
                                        tcell += '&nbsp;'
                            else:
                                tcell += '&nbsp;' 
                            trow += tcell

                        # parents column
                        if report.options['showparents']:
                            tcell = Html('td', class_='ColumnParents')
                            parent_handle_list = person.get_parent_family_handle_list()
                            if parent_handle_list:
                                parent_handle = parent_handle_list[0]
                                family = db.get_family_from_handle(parent_handle)
                                father_id = family.get_father_handle()
                                mother_id = family.get_mother_handle()
                                father = db.get_person_from_handle(father_id)
                                mother = db.get_person_from_handle(mother_id)
                                if father:
                                    father_name = self.get_name(father)
                                if mother:
                                    mother_name = self.get_name(mother)
                                if mother and father:
                                    tcell += Html('span', father_name, 
                                        class_='father fatherNmother') + (
                                        Html('span', mother_name, class_='mother')
                                        )
                                elif mother:
                                    tcell += Html('span', mother_name, class_='mother')
                                elif father:
                                    tcell += Html('span', father_name, class_='father')
                            else:
                                tcell += '&nbsp;'
                            trow += tcell
                        tbody += trow

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(surnamepage, of)  

class PlaceListPage(BasePage):

    def __init__(self, report, title, place_handles, src_list):
        BasePage.__init__(self, report, title)
        self.src_list = src_list        # TODO verify that this is correct
        db = report.database

        of = self.report.create_file("places")
        placelistpage, body = self.write_header(_('Places'))

        # begin places division
        with Html('div', class_='content', id='Places') as section:
            body += section

            msg = _("This page contains an index of all the places in the "
                          "database, sorted by their title. Clicking on a place&#8217;s "
                          "title will take you to that place&#8217;s page.")
            section += Html('p', msg, id='description')

            # begin alphabet navigation
            alpha_nav = alphabet_navigation(db, place_handles, _PLACE) 
            if alpha_nav is not None:
                section += alpha_nav

            # begin places table and table head
            with Html('table', class_='infolist placelist') as table:
                section += table

                # begin table head
                thead = Html('thead')
                table += thead

                trow = Html('tr')  + (
                    Html('th', _('Letter'), class_='ColumnLetter', inline=True),
                    Html('th', _('Name'), class_='ColumnName', inline=True)
                    )
                thead += trow

                sort = Sort.Sort(db)
                handle_list = sorted(place_handles, key=sort.by_place_title_key)
                last_letter = ''

                # begin table body
                tbody = Html('tbody')
                table += tbody

                for handle in handle_list:
                    place = db.get_place_from_handle(handle)
                    place_title = ReportUtils.place_name(db, handle)

                    if not place_title:
                        continue

                    letter = normalize('NFKC', place_title)[0].upper()
                    # See : http://www.gramps-project.org/bugs/view.php?id=2933
                    (lang_country, modifier ) = locale.getlocale()
                    if lang_country == "sv_SE" and ( letter == u'W' or letter == u'V' ):
                        letter = u'V,W'

                    if letter != last_letter:
                        last_letter = letter
                        trow = Html('tr', class_='BeginLetter')
                        tbody += trow
                        tcell = Html('td', class_='ColumnLetter', inline=True) + (
                            Html('a', last_letter, name=last_letter, title="Letter %s" % last_letter)
                            )
                    else:
                        trow = Html('tr')
                        tbody += trow
                        tcell = Html('td', '&nbsp;', class_='ColumnLetter', inline=True)
                    trow += tcell

                    tcell = Html('td', class_='ColumnName') + \
                    self.place_link(place.handle, place_title, place.gramps_id)
                    trow += tcell

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(placelistpage, of)

class PlacePage(BasePage):

    def __init__(self, report, title, place_handle, src_list, place_list):
        db = report.database

        place = db.get_place_from_handle(place_handle)
        BasePage.__init__(self, report, title, place.gramps_id)
        self.src_list = src_list        # TODO verify that this is correct

        of = self.report.create_file(place.get_handle(), 'plc')
        self.up = True
        self.page_title = ReportUtils.place_name(db, place_handle)
        placepage, body = self.write_header("%s - %s" % (_('Places'), self.page_title))

        # begin PlaceDetail Division
        with Html('div', class_='content', id='PlaceDetail') as section:
            body += section

            media_list = place.get_media_list()
            thumbnail = self.display_first_image_as_thumbnail(media_list)
            if thumbnail is not None:
                section += thumbnail

            # section title
            section += Html('h3', html_escape(self.page_title.strip()))

            # begin summaryarea division and places table
            with Html('div', id='summaryarea') as summaryarea:
                section += summaryarea

                with Html('table', class_='infolist place') as table:
                    summaryarea += table

                    if not self.noid:
                        trow = Html('tr') + (
                            Html('td', _('GRAMPS ID'), class_='ColumnAttribute', inline=True),
                            Html('td', place.gramps_id, class_='ColumnValue', inline=True)
                            )
                        table += trow

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
                                trow = Html('tr') + (
                                    Html('td', val[0], class_='ColumnAttribute', inline=True),
                                    Html('td', val[1], class_='ColumnValue', inline=True)
                                    )
                                table += trow

                    if place.lat:
                        trow = Html('tr') + (
                            Html('td', _('Latitude'), class_='ColumnAttribute', inline=True),
                            Html('td', place.lat, class_='ColumnValue', inline=True)
                            ) 
                        table += trow

                    if place.long:
                        trow = Html('tr') + (
                            Html('td', _('Longitude'), class_='ColumnAttribute', inline=True),
                            Html('td', place.long, class_='ColumnValue', inline=True)
                            )
                        table += trow

            # place gallery
            if self.create_media:
                placegallery = self.display_additional_images_as_gallery(media_list)
                if placegallery is not None:
                    section += placegallery

            # place notes
            notelist = self.display_note_list(place.get_note_list())
            if notelist is not None:
                section += notelist 

            # place urls
            urllinks = self.display_url_list(place.get_url_list())
            if urllinks is not None:
                section += urllinks

            # place references
            referenceslist = self.display_references(place_list[place.handle])
            if referenceslist is not None:
                section += referenceslist

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(placepage, of)

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

        # get media type to be used primarily with 'img' tags
        mime_type = photo.get_mime_type()
        mtype = Mime.get_description(mime_type)

        if mime_type:
            note_only = False
            newpath = self.copy_source_file(handle, photo)
            target_exists = newpath is not None
        else:
            note_only = True
            target_exists = False

        self.copy_thumbnail(handle, photo)
        self.page_title = photo.get_description()
        mediapage, body = self.write_header("%s - %s" % (_('Media'), self.page_title))

        # begin GalleryDetail division
        mediadetail = Html('div', class_='content', id='GalleryDetail')
        body += mediadetail

        # gallery navigation
        gallerynav = Html('div', id='GalleryNav')
        mediadetail += gallerynav
        if prev:
            gallerynav += self.gallery_nav_link(prev, _('Previous'), True)
        data = _('<strong id="GalleryCurrent">%(page_number)d</strong> of '
            '<strong id="GalleryTotal">%(total_pages)d</strong>' ) % {
            'page_number' : page_number, 'total_pages' : total_pages }
        gallerynav += Html('span', data, id='GalleryPages')
        if next:
            gallerynav += self.gallery_nav_link(next, _('Next'), True)

        # missing media error msg
        errormsg = _('The file has been moved or deleted.')
        missingimage = Html('span', errormsg, class_='MissingImage')  

        # begin summaryarea division
        summaryarea = Html('div', id='summaryarea')
        mediadetail += summaryarea
        if mime_type:
            if mime_type.startswith("image/"):
                if not target_exists:
                    mediadisplay = Html('div', id='GalleryDisplay') + \
                        missingimage
                    summaryarea += mediadisplay
                else:
                    # Check how big the image is relative to the requested 'initial'
                    # image size. If it's significantly bigger, scale it down to
                    # improve the site's responsiveness. We don't want the user to
                    # have to await a large download unnecessarily. Either way, set
                    # the display image size as requested.
                    orig_image_path = Utils.media_path_full(db, photo.get_path())
                    (width, height) = ImgManip.image_size(orig_image_path)
                    max_width = self.report.options['maxinitialimagewidth']
                    max_height = self.report.options['maxinitialimageheight']
                    scale_w = (float(max_width)/width) or 1    # the 'or 1' is so that a max of zero is ignored
                    scale_h = (float(max_height)/height) or 1
                    scale = min(scale_w, scale_h)
                    new_width = int(width*scale)
                    new_height = int(height*scale)
                    if scale < 0.8:
                        # scale factor is significant enough to warrant making a smaller image
                        initial_image_path = '%s_init.jpg' % os.path.splitext(newpath)[0]
                        initial_image_data = ImgManip.resize_to_jpeg_buffer(orig_image_path,
                                new_width, new_height)
                        if self.report.archive:
                            filed, dest = tempfile.mkstemp()
                            os.write(filed, initial_image_data)
                            os.close(filed)
                            self.report.archive.add(dest, initial_image_path)
                        else:
                            filed = open(os.path.join(self.html_dir, initial_image_path), 'w')
                            filed.write(initial_image_data)
                            filed.close()
                    else:
                        # not worth actually making a smaller image
                        initial_image_path = newpath

                    # TODO. Convert disk path to URL.
                    url = self.report.build_url_fname(initial_image_path, None, self.up)
                    if initial_image_path != newpath:
                        scalemsg = Html('p', '(%d x %d).' % (width, height), inline=True)
                        summaryarea += scalemsg
                    mediadisplay = Html('div', style='width:%dpx; height:%dpx;' % (new_width, new_height))
                    summaryarea += mediadisplay

                    # Feature #2634; display the mouse-selectable regions.
                    # See the large block at the top of this function where
                    # the various regions are stored in _region_items
                    if len(_region_items):
                        ordered = Html('ol', class_='RegionBox')
                        mediadisplay += ordered
                        while len(_region_items) > 0:
                            (name, x, y, w, h, linkurl) = _region_items.pop()
                            ordered += Html('li', style='left:%d%%; top:%d%%; width:%d%%; height:%d%%;'
                                % (x, y, w, h)) +(
                                    Html('a', name, href=linkurl)
                                    )       

                    # display the image
                    if initial_image_path != newpath:
                        url = self.report.build_url_fname(newpath, None, self.up)
                        mediadisplay += Html('a', href=url) + (
                            Html('img', width=new_width, height=new_height, src=url,
                                alt=html_escape(self.page_title))
                                )
            else:
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

                mediadisplay = Html('div', id='GalleryDisplay')
                summaryarea += mediadisplay
                if target_exists:
                    # TODO. Convert disk path to URL
                    url = self.report.build_url_fname(newpath, None, self.up)
                    hyper = Html('a', href=url)
                # TODO. Mixup url and path
                # path = convert_disk_path_to_url(path)
                url = self.report.build_url_fname(path, None, self.up)
                hyper += Html('img', src=url, alt=html_escape(self.page_title) 
                if target_exists:
                    mediadisplay += hyper  
                else:
                    mediadisplay += missingimage
        else:
            mediadisplay = Html('div', id='GalleryDisplay')
            summaryarea += mediadisplay
            url = self.report.build_url_image('document.png', 'images', self.up)
            mediadisplay += Html('img', src=url, alt=html_escape(self.page_title))

        # media title
        title = Html('h3', html_escape(self.page_title.strip()), inline=True)
        summaryarea += title

        # begin media table
        with Html('table', class_='infolist gallery') as table: 
            summaryarea += table

            if not self.noid:
                with Html('tr') as trow:
                    table += trow
                    trow += Html('td', _('GRAMPS ID'), class_='ColumnAttribute', inline=True)
                    trow += Html('td', photo.gramps_id, class_='ColumnValue', inline=True)

            if not note_only and not mime_type.startswith("image/"):
                with Html('tr') as trow:
                    table += trow
                    trow += Html('td', _('File Type'), class_='ColumnAttribute', inline=True)
                    trow += Html('td', mtype, class_='ColumnValue', unline=True)  

            date = _dd.display(photo.get_date_object())
            if date:
                with Html('tr') as trow:
                    table += trow
                    trow += Html('td', _('Date'), class_='ColumnAttribute', inline=True)
                    trow += Html('td', date, class_='ColumnValue', inline=True)

        # get media notes
        notes = self.display_note_list(photo.get_note_list())
        if notes is not None:
            mediadetail += notes

        # get media attributes
        attrib = self.display_attr_list(photo.get_attribute_list())
        if attrib is not None:
            mediadetail += attrib

        # get media sources
        sources = self.display_media_sources(photo)
        if sources is not None:
            mediadetail += sources

        # get media references 
        references = self.display_references(my_media_list)
        if references is not None:
            mediadetail += references

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(mediapage, of)

    def gallery_nav_link(self, handle, name, up=False):

        url = self.report.build_url_fname_html(handle, 'img', up)
        name = html_escape(name)
        hyper = Html('a', name, id=name, href=url,  title=name, inline=True)

        # return hyperlink to its callers
        return hyper

    def display_media_sources(self, photo):

        for sref in photo.get_source_references():
            self.bibli.add_reference(sref)
        sourcerefs = self.display_source_refs(self.bibli)

        # return source references to its callers
        return sourcerefs

    def display_attr_list(self, attrlist=None):

        if not attrlist:
            return None

        # begin attributes division
        with Html('div', id='attributes') as section:

            # section section title
            section += Html('h4', _('Attributes'), inline=True)

            # begin attrib table
            with Html('table', class_='infolist') as table:
                section += table

                # begin table body
                tbody = Html('tbody')

                for attr in attrlist:
                    atType = str( attr.get_type() )
                    trow = Html('tr') + (
                        Html('td', atType, class_='ColumnAttribute', inline=True),
                        Html('td', attr.get_value(), class_='ColumnValue', inline=True)
                        )
                    tbody += trow
                table += tbody

        # return attributes division to its caller
        return section

    def copy_source_file(self, handle, photo):
        db = self.report.database   

        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.report.build_path('images', handle)
        newpath = os.path.join(to_dir, handle) + ext

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
        db = self.report.database 

        to_dir = self.report.build_path('thumb', handle)
        to_path = os.path.join(to_dir, handle) + '.png'
        if photo.get_mime_type():
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
            surnamelist, body = self.write_header(_('Surnames'))
        else:
            of = self.report.create_file("surnames_count")
            surnamelist, body = self.write_header(_('Surnames by person count'))

        # begin surnames division
        with Html('div', class_='content', id='surnames') as section:
            body += section

            # page description
            msg = _( 'This page contains an index of all the '
                           'surnames in the database. Selecting a link '
                           'will lead to a list of individuals in the '
                           'database with this same surname.')
            section += Html('p', msg, id='description')

            # add alphabet navigation after page msg
            # only if surname list not surname count
            if order_by == self.ORDER_BY_NAME:
                alpha_nav = alphabet_navigation(db, person_handle_list, _PERSON) 
                if alpha_nav is not None:
                    section += alpha_nav

            if order_by == self.ORDER_BY_COUNT:
                table_id = 'SortByCount'
            else:
                table_id = 'SortByName'
            with Html('table', class_='infolist surnamelist', id=table_id) as table:
                section += table
                with Html('thead') as thead:
                    table += thead
                    with Html('tr') as trow:
                        thead += trow
                        with Html('th', _('Letter'), class_='ColumnLetter', inline=True) as tcell:
                            trow += tcell

                        fname = self.report.surname_fname + self.ext
                        with Html('th', class_='ColumnSurname', inline=True) as tcell:
                            trow += tcell
                            hyper = Html('a', _('Surname'), href=fname)
                            tcell += hyper
                        fname = "surnames_count" + self.ext
                        with Html('th', class_='ColumnQuantity', inline=True) as tcell:
                            trow += tcell
                            hyper = Html('a', _('Number of People'), href=fname)
                            tcell += hyper

                # begin table body
                with Html('tbody') as tbody:
                    table += tbody

                    person_handle_list = sort_people(db, person_handle_list)
                    if order_by == self.ORDER_BY_COUNT:
                        temp_list = {}
                        for (surname, data_list) in person_handle_list:
                            index_val = "%90d_%s" % (999999999-len(data_list), surname)
                            temp_list[index_val] = (surname, data_list)

                        person_handle_list = []
                        for key in sorted(temp_list, key=locale.strxfrm):
                            person_handle_list.append(temp_list[key])

                    last_letter = ''
                    last_surname = ''

                    for (surname, data_list) in person_handle_list:
                        if len(surname) == 0:
                            continue

                        # Get a capital normalized version of the first letter of
                        # the surname
                        if surname:
                            letter = normalize('NFKC', surname)[0].upper()
                        else:
                            letter = u' '
                        # See : http://www.gramps-project.org/bugs/view.php?id=2933
                        (lang_country, modifier ) = locale.getlocale()
                        if lang_country == "sv_SE" and ( letter == u'W' or letter == u'V' ):
                            letter = u'V,W'

                        if letter != last_letter:
                            last_letter = letter
                            with Html('tr', class_='BeginLetter') as trow:
                                tbody += trow
                                with Html('td', class_='ColumnLetter', inline=True) as tcell:
                                    trow += tcell
                                    tcell += Html('a', last_letter, name=last_letter)
                                with Html('td', class_='ColumnSurname') as tcell:
                                    trow += tcell
                                    tcell += self.surname_link(name_to_md5(surname), surname)
                        elif surname != last_surname:
                            with Html('tr') as trow:
                                tbody += trow
                                with Html('td', '&nbsp;', class_='ColumnLetter', inline=True) as tcell:
                                    trow += tcell
                                with Html('td', class_='ColumnSurname') as tcell:
                                    trow += tcell
                                    tcell += self.surname_link(name_to_md5(surname), surname)
                                last_surname = surname
                        with Html('td', len(data_list), class_='ColumnQuantity', inline=True) as tcell:
                            trow += tcell

        # create footer section
        # add clearline for proper styling
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(surnamelist, of)  

    def surname_link(self, fname, name, opt_val=None, up=False):
        url = self.report.build_url_fname_html(fname, 'srn', up)
        hyper = Html('a', name, href=url, title=name)
        if opt_val is not None:
            hyper += opt_val

        # return hyperlink to its caller
        return hyper

class IntroductionPage(BasePage):
    """
    This class will create the Introduction page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file(report.intro_fname)
        # Note. In old NarrativeWeb.py the content_divid depended on filename.
        intropage, body = self.write_header(_('Introduction'))

        # begin Introduction division
        with Html('div', class_='content', id='Introduction') as section:
            body += section

            introimg = report.add_image('introimg')
            if introimg is not None:
                section += introimg

            note_id = report.options['intronote']
            note = db.get_note_from_gramps_id(note_id) 
            if note:
                note_text = note.get()
                if note_text:
 
                    # styled notes
                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                         note.get_format())
                    if htmlnotetext:
                        text = htmlnotetext
                    else:
                        text = Html('p', note_text) 
                    section += text

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(intropage, of)

class HomePage(BasePage):
    """
    This class will create the Home Page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("index")
        homepage, body = self.write_header(_('Home'))

        # begin home division
        with Html('div', class_='content', id='Home') as section:
            body += section

            homeimg = report.add_image('homeimg')
            if homeimg is not None:
                section += homeimg

            note_id = report.options['homenote']
            if note_id:
                note = db.get_note_from_gramps_id(note_id)
                note_text = note.get()
                if note_text: 
 
                    # styled notes
                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                         note.get_format())
                    if htmlnotetext:
                        text = htmlnotetext
                    else:
                        text = Html('p', note_text) 
                    section += text

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(homepage, of)  

class SourceListPage(BasePage):

    def __init__(self, report, title, handle_set):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("sources")
        sourcelistpage, body = self.write_header(_('Sources'))

        # begin source list division
        with Html('div', class_='content', id='sources') as section:
            body += section

            handle_list = list(handle_set)
            source_dict = {}

            # Sort the sources
            for handle in handle_list:
                source = db.get_source_from_handle(handle)
                key = source.get_title() + str(source.get_gramps_id())
                source_dict[key] = (source, handle)
            
            keys = sorted(source_dict, key=locale.strxfrm)

            msg = _("This page contains an index of all the sources in the "
                         "database, sorted by their title. Clicking on a source&#8217;s "
                         "title will take you to that source&#8217;s page.")
            section += Html('p', msg, id='description')

            # begin sourcelist table and table head
            with Html('table', class_='infolist sourcelist') as table:
                section += table 
                thead = Html('thead')
                table += thead
                trow = Html('tr') + (
                    Html('th',  '&nbsp;', class_='ColumnAttrubyte', inline=True),
                    Html('th', _('Name'), class_='ColumnValue', inline=True)
                    )
                thead += trow
   
                # begin table body
                tbody = Html('tbody')
                table += tbody

                for index, key in enumerate(keys):
                    (source, handle) = source_dict[key]
                    trow = Html('tr') + (
                        Html('td', index+1, class_='ColumnRowLabel', inline=True)
                        )
                    tbody += trow 
                    tcell = Html('td', class_='ColumnName') + \
                       self.source_link(handle, source.get_title(), source.gramps_id)
                    trow += tcell

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(sourcelistpage, of)

class SourcePage(BasePage):

    def __init__(self, report, title, handle, src_list):
        db = report.database 

        source = db.get_source_from_handle(handle)
        BasePage.__init__(self, report, title, source.gramps_id)

        of = self.report.create_file(source.get_handle(), 'src')
        self.up = True
        self.page_title = source.get_title()
        sourcepage, body = self.write_header("%s - %s" % (_('Sources'), self.page_title))

        # begin source detail division
        with Html('div', class_='content', id='SourceDetail') as section:
            body += section 

            media_list = source.get_media_list()
            thumbnail = self.display_first_image_as_thumbnail(media_list)
            if thumbnail is not None:
                section += thumbnail

            # add section title
            section += Html('h3', html_escape(self.page_title.strip()), inline=True)
 
            # begin summaryarea division
            with Html('div', id='summaryarea') as summaryarea:
                section += summaryarea

                # begin sources table
                with Html('table', class_='infolist source') as table:
                    summaryarea += table

                    grampsid = None
                    if not self.noid:
                        grampsid = source.gramps_id

                        for (label, val) in [(_('GRAMPS ID'), grampsid),
                                                      (_('Author'), source.author),
                                                      (_('Publication information'), source.pubinfo),
                                                      (_('Abbreviation'), source.abbrev)]:
                            if val:
                                trow = Html('tr') + (
                                    Html('td',  label, class_='ColumnAttribute'),
                                    Html('td', val, class_='ColumnValue')
                                    )
                                table += trow

            # additional gallery
            sourcegallery = self.display_additional_images_as_gallery(media_list)
            if sourcegallery is not None:
                section += sourcegallery

            # additional notes
            sourcenotes = self.display_note_list(source.get_note_list())
            if sourcenotes is not None:
                section += sourcenotes

#            # get source repositories
#            # TODO: Figure if this is possible 
#            for handle in source.get_repository_handles():
#                repo = db.get_repository_from_handle(handle)
#                sourcerepo = self.write_repositories(repo, handle)
#                if sourcerepo is not None:
#                    section += sourcerepo

            # references
            source_references = self.display_references(src_list[source.handle])
            if source_references is not None:
                section += source_references

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(sourcepage, of)

class MediaListPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        # add bottom and top links
        counter = len(self.report.photo_list)

        of = self.report.create_file("gallery")
        medialistpage, body = self.write_header(_('Gallery'))

        # begin gallery division
        with Html('div', class_='content', id='Gallery') as section:
            body += section

            msg = _("This page contains an index of all the media objects "
                          "in the database, sorted by their title. Clicking on "
                          "the title will take you to that media object&#8217;s page.\n\n")
            section += Html('p', msg, id='description')

            msg = _("if you see media dimensions, Click on the image to see the "
                          "full- sized version.\n")
            section += Html('p', msg, id='description')

            # begin gallery table and table head
            with Html('table', class_='infolist gallerylist') as table:
                section += table

                # begin table head
                thead = Html('thead')
                table += thead

                trow = Html('tr') + (
                    Html('th', '&nbsp;', class_='ColumnRowLabel', inline=True),
                    Html('th', _('Name'), class_='ColumnName', inline=True),
                    Html('th', _('Date'), class_='ColumnDate', inline=True)
                    )
                thead += trow

                # begin table body
                tbody = Html('tbody')
                table += tbody

                index = 1
                sort = Sort.Sort(db)
                mlist = sorted(self.report.photo_list, key=sort.by_media_title_key)
        
                for handle in mlist:
                    media = db.get_object_from_handle(handle)
                    date = _dd.display(media.get_date_object())
                    title = media.get_description()
                    if not title:
                        title = "[untitled]"

                    trow = Html('tr') + (
                        Html('td', index, class_='ColumnRowLabel', inline=True),
                        )
                    tbody += trow
                    tcell = Html('td', class_='ColumnName') + \
                        self.media_ref_link(handle, title)
                    trow += tcell
                    trow += Html('td', date, class_='ColumnDate', inline=True)
                    index += 1

        # add footer section
        # add clearline for proper styling
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(medialistpage, of)

    def media_ref_link(self, handle, name, up=False):

        # get media url
        url = self.report.build_url_fname_html(handle, 'img', up)

        # get name
        name = html_escape(name)

        # begin hyper link
        hyper = Html('a', name, href=url, title=name)

        # return hyperlink to its callers
        return hyper

class DownloadPage(BasePage):
    """
    This class will produce the Download Page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)

        # do NOT include a Download Page
        if not self.report.inc_download:
            return None

        # menu options for class
        # download and description #1
        dlfname1 = self.report.dl_fname1
        dldescr1 = self.report.dl_descr1
        dldescr = ''.join(wrapper.wrap(dldescr1))

        # download and description #2
        dlfname2 = self.report.dl_fname2
        dldescr2 = self.report.dl_descr2
        dldescr2 = ''.join(wrapper.wrap(dldescr2))

        # download copyright
        dlcopy = self.report.dl_copy

        # if no filenames at all, return???
        if not dlfname1 and not dlfname2:
            return

        of = self.report.create_file("download")
        downloadpage, body = self.write_header(_('Download'))

        # begin download page and table
        with Html('div', class_='content', id='Download') as section:
            body += section

            # begin download table
            with Html('table', class_='infolist download') as table:
                section += table

                # table head
                thead = Html('thead')
                table += thead
                trow = Html('tr')
                thead += trow 
                for title in ['Description', 'License',  'Filename', 'Last Modified']:
                    trow += Html('th', title, class_='%s' % title, inline=True)

                # if dlfname1 is not None, show it???
                if dlfname1:

                    # table body
                    tbody = Html('tbody')
                    table += tbody
                    trow = Html('tr', id='Row01')
                    tbody += trow

                    # table Row 1, column 1 -- File Description
                    tcell = Html('td', id='Col01', class_='Description', 
                        inline=True)
                    if dldescr1:
                        tcell += dldescr1
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

                    # table row 1, column 2 -- Copyright License
                    tcell = Html('td', id='Col02', class_='License')
                    copyright = self.get_copyright_license(dlcopy)
                    if copyright:
                        tcell += copyright
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

                    # table row 1, column 3 -- File
                    fname = os.path.basename(dlfname1)
                    tcell = Html('td', id='Col03', class_='Filename') + (
                        Html('a', fname, href=dlfname1, alt=dldescr1)
                        )
                    trow += tcell

                    # table row 1, column 4 -- Last Modified
                    tcell = Html('td', id='Col04', class_='Modified', inline=True)
                    if os.path.exists(dlfname1):
                        modified = os.stat(dlfname1).st_mtime
                        last_mod = datetime.datetime.fromtimestamp(modified)
                        tcell += last_mod
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

                # if download filename #2, show it???
                if dlfname2:

                    # begin row #2
                    trow = Html('tr', id='Row02')
                    tbody += trow

                    # table row 2, column 1 -- Description
                    tcell = Html('td', id='Col01', class_='Description', 
                        inline=True)
                    if dldescr2:
                        tcell += dldescr2
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

                    # table row 2, column 2 -- Copyright License
                    tcell = Html('td', id='Col02', class_='License')
                    copyright = self.get_copyright_license(dlcopy)
                    if copyright:
                        tcell += copyright
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

                    # table row 2, column 3 -- File
                    fname = os.path.basename(dlfname2)
                    tcell = Html('td', id='Col03', class_='Filename') + (
                        Html('a', fname, href=dlfname2, alt=dldescr2)
                        )  
                    trow += tcell

                    # table row 2, column 4 -- Last Modified
                    tcell = Html('td', id='Col04', class_='Modified',  inline=True)
                    if os.path.exists(dlfname2):
                        modified = os.stat(dlfname2).st_mtime
                        last_mod = datetime.datetime.fromtimestamp(modified)
                        tcell += last_mod
                    else:
                        tcell += '&nbsp;'
                    trow += tcell

        # clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(downloadpage, of)

class ContactPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("contact")
        contactpage, body = self.write_header(_('Contact'))

        # begin contact division
        with Html('div', class_='content', id='Contact') as section:
            body += section 

            # begin summaryarea division
            with Html('div', id='summaryarea') as summaryarea:
                section  += summaryarea

                contactimg = report.add_image('contactimg', 200)
                if contactimg is not None:
                    summaryarea += contactimg

                # get researcher information
                r = Utils.get_researcher()

                with Html('div', id='researcher') as researcher:
                    summaryarea += researcher
                    if r.name:
                        r.name = r.name.replace(',,,', '')
                        researcher += Html('h3', r.name, inline=True)
                    if r.addr:
                        researcher += Html('span', r.addr, id='streetaddress')
                    text = "".join([r.city, r.state, r.postal])
                    if text:
                        city = Html('span', r.city, id='city', inline=True)
                        state = Html('span', r.state, id='state', inline=True)
                        postal = Html('span', r.postal, id='postalcode', inline=True)
                        researcher += (city, state, postal)
                    if r.country:
                        researcher += Html('span', r.country, id='country', inline=True)
                    if r.email:
                        researcher += Html('span', id='email') + (
                            Html('a', r.email, href='mailto:%s?subject="from GRAMPS Web Site"' 
                                % r.email, inline=True)
                            )

                    # add clear line for proper styling
                    summaryarea += fullclear

                    note_id = report.options['contactnote']
                    if note_id:
                        note = db.get_note_from_gramps_id(note_id)
                        note_text = note.get()
                        if note_text: 
 
                            # styled notes
                            htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                                note.get_format())
                            if htmlnotetext:
                                text = htmlnotetext
                            else:
                                text = Html('p', note_text) 
                            summaryarea += text

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for porcessing
        # and close the file
        self.mywriter(contactpage, of)

class IndividualPage(BasePage):
    """
    This class is used to write HTML for an individual.
    """

    gender_map = {
        Person.MALE    : _('male'),
        Person.FEMALE  : _('female'),
        Person.UNKNOWN : _('unknown'),
        }

    def __init__(self, report, title, person, ind_list, place_list, src_list):
        BasePage.__init__(self, report, title, person.gramps_id)
        self.person = person
        self.ind_list = ind_list
        self.src_list = src_list        # Used by get_citation_links()
        self.bibli = Bibliography()
        self.place_list = place_list
        self.sort_name = self.get_name(self.person)
        self.name = self.get_name(self.person)
        db = report.database

        of = self.report.create_file(person.handle, 'ppl')
        self.up = True
        indivdetpage, body = self.write_header(self.sort_name)

        # begin individualdetail division
        with Html('div', class_='content', id='IndividualDetail') as section:
            body += section

            # display a person's general data
            thumbnail, name, summary = self.display_ind_general()

            # if there is a thumbnail, add it also?
            if thumbnail is not None:
                section += (thumbnail, name, summary)
            else:
                section += (name, summary)

            # display a person's events
            sect2 = self.display_ind_events()
            if sect2 is not None:
                section += sect2

            # display attributes
            sect3 = self.display_attr_list(self.person.get_attribute_list())
            if sect3 is not None:
                section += sect3

            # display parents
            sect4 = self.display_ind_parents()
            if sect4 is not None:
                section += sect4

            # display relationships
            sect5 = self.display_ind_families()
            if sect5 is not None:
                section += sect5

            # display address(es)
            sect6 = self.display_addresses()
            if sect6 is not None:
                section += sect6 

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

            # display additional images as gallery
            sect7 = self.display_additional_images_as_gallery(media_list)
            if sect7 is not None:
                section += sect7

            # display notes
            sect8 = self.display_note_list(self.person.get_note_list())
            if sect8 is not None:
                section += sect8

            # display web links
            sect9 = self.display_url_list(self.person.get_url_list())
            if sect9 is not None:
                section += sect9

            # display sources
            sect10 = self.display_ind_sources()
            if sect10 is not None:
                section += sect10

            # display pedigree
            sect11 = self.display_ind_pedigree()
            if sect11 is not None:
                section += sect11

            # display ancestor tree   
            if report.options['graph']:
                sect12 = self.display_tree()
                if sect12 is not None:
                    section += sect12

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(indivdetpage, of)

    def display_attr_list(self, attrlist=None):
        """
        display a person's attributes
        """

        if not attrlist:
            return

        # begin attributes division
        with Html('div', class_='subsection', id='attributes') as section:
            section += Html('h4', _('Attributes'), inline=True)

            #begin attributes table
            with Html('table', class_='infolist') as table:
                section += table

                for attr in attrlist:
                    atType = str( attr.get_type() )
                    trow = Html('tr')
                    table += trow
                    tcell = Html('td', atType, class_='ColumnAttribute', inline=True)
                    trow += tcell
                    value = attr.get_value()
                    value += self.get_citation_links( attr.get_source_references() )
                    tcell = Html('td', value, class_='ColumnValue')
                    trow += tcell

        # return aatributes division to its caller
        return section

    def draw_box(self, center, col, person):
        db = self.report.database

        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)
        sex = person.gender
        if sex == Person.MALE:
            divclass = "male"
        elif sex == Person.FEMALE:
            divclass = "female"
        else:
            divclass = "unknown"
            
        boxbg = Html('div', class_="boxbg %s AncCol%s" % (divclass, col),
                    style="top: %dpx; left: %dpx;" % (top, xoff+1)
                   )
                      
        person_name = self.get_name(person)
        if person.handle in self.ind_list:
            thumbnailUrl = None
            if self.create_media and col < 5:
                photolist = person.get_media_list()
                if photolist:
                    photo_handle = photolist[0].get_reference_handle()
                    photo = db.get_object_from_handle(photo_handle)
                    mime_type = photo.get_mime_type()
                    if mime_type:
                        (photoUrl, thumbnailUrl) = self.report.prepare_copy_media(photo)
                        thumbnailUrl = '/'.join(['..']*3 + [thumbnailUrl])
            url = self.report.build_url_fname_html(person.handle, 'ppl', True)
            boxbg += self.person_link(url, person, name_style=True, 
                thumbnailUrl=thumbnailUrl)
        else:
            boxbg += Html('span', person_name, class_="unlinked", inline=True)
        shadow = Html('div', class_="shadow", inline=True, style="top: %dpx; left: %dpx;"
            % (top+_SHADOW, xoff+_SHADOW) )

        return [boxbg, shadow]

    def extend_line(self, y0, x0):
        style = "top: %dpx; left: %dpx; width: %dpx"
        bv = Html('div', class_="bvline", inline=True,
                      style=style % (y0, x0, _HGAP/2)
                    )
        gv = Html('div', class_="gvline", inline=True,
                      style=style % (y0+_SHADOW, x0, _HGAP/2+_SHADOW)
                    )  
        return [bv, gv]

    def connect_line(self, y0, y1, col):
        y = min(y0, y1)
        stylew = "top: %dpx; left: %dpx; width: %dpx;"
        styleh = "top: %dpx; left: %dpx; height: %dpx;"
        x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        bv = Html('div', class_="bvline", inline=True, style=stylew %
                 (y1, x0, _HGAP/2))
        gv = Html('div', class_="gvline", inline=True, style=stylew %
                 (y1+_SHADOW, x0+_SHADOW, _HGAP/2+_SHADOW))
        bh = Html('div', class_="bhline", inline=True, style=styleh %
                 (y, x0, abs(y0-y1)))
        gh = Html('div', class_="gvline", inline=True, style=styleh %
                 (y+_SHADOW, x0+_SHADOW, abs(y0-y1)))
        return [bv, gv, bh, gh]

    def draw_connected_box(self, center1, center2, col, handle):
        db = self.report.database

        box = []
        if not handle:
            return box
        person = db.get_person_from_handle(handle)
        box = self.draw_box(center2, col, person)
        box += self.connect_line(center1, center2, col)
        return box

    def display_tree(self):
        tree = []
        if not self.person.get_main_parents_family_handle():
            return None

        generations = self.report.options['graphgens']
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        with Html('div', id="tree", class_="subsection") as tree:
            tree += Html('h4', _('Ancestors'), inline=True)
            with Html('div', id="treeContainer",
                    style="width:%dpx; height:%dpx;" %
                        (_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP, 
                        max_size)
                     ) as container:
                tree += container
                container += self.draw_tree(1, generations, max_size, 
                                            0, center, self.person.handle)
        return tree

    def draw_tree(self, gen_nr, maxgen, max_size, old_center, new_center, phandle):
        db = self.report.database

        tree = []
        if gen_nr > maxgen:
            return tree
        gen_offset = int(max_size / pow(2, gen_nr+1))
        person = db.get_person_from_handle(phandle)
        if not person:
            return tree

        if gen_nr == 1:
            tree = self.draw_box(new_center, 0, person)
        else:
            tree = self.draw_connected_box(old_center, new_center, gen_nr-1, phandle)

        if gen_nr == maxgen:
            return tree

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + gen_nr*_WIDTH + (gen_nr-1)*_HGAP
            tree += self.extend_line(new_center, line_offset)

            family = db.get_family_from_handle(family_handle)

            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size, 
                                   new_center, f_center, f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size, 
                                   new_center, m_center, m_handle)
        return tree

    def display_ind_sources(self):

        for sref in self.person.get_source_references():
            self.bibli.add_reference(sref)
        sourcerefs = self.display_source_refs(self.bibli)

        # return to its caller
        return sourcerefs

    def display_ind_pedigree(self):
        """
        Display an individual's pedigree
        """
        db = self.report.database

        # Define helper functions
        
        def children_ped(ol):
            if family:
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    if child_handle == self.person.handle:
                        child_ped(ol)
                    else:
                        child = db.get_person_from_handle(child_handle)
                        ol += Html('li') + self.pedigree_person(child)
            else:
                child_ped(ol)
            return ol
                
        def child_ped(ol):
            ol += Html('li', class_="thisperson", inline=True) + self.name
            family = self.pedigree_family()
            if family:
                ol += Html('ol', class_="spouselist") + family
            return ol
        
        # End of helper functions

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = db.get_family_from_handle(parent_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            mother = db.get_person_from_handle(mother_handle)
            father = db.get_person_from_handle(father_handle)
        else:
            family = None
            father = None
            mother = None

        with Html('div', id="pedigree", class_="subsection") as ped:
            ped += Html('h4', _('Pedigree'), inline=True)
            with Html('ol', class_="pedigreegen") as pedol:
                ped += pedol
                if father and mother:
                    pedfa = Html('li') + self.pedigree_person(father)
                    pedol += pedfa
                    with Html('ol') as pedma:
                        pedfa += pedma
                        pedma += (Html('li', class_="spouse") +
                                      self.pedigree_person(mother) +
                                      children_ped(Html('ol'))
                                 )
                elif father:
                    pedol += (Html('li') + self.pedigree_person(father) +
                                  children_ped(Html('ol'))
                             )
                elif mother:
                    pedol += (Html('li') + self.pedigree_person(mother) +
                                  children_ped(Html('ol'))
                             )
                else:
                    pedol += children_ped(Html('ol'))
        return ped
        
    def display_ind_general(self):
        """
        display an individual's general information...
        """
        db = self.report.database

        self.page_title = self.sort_name
        thumbnail = self.display_first_image_as_thumbnail(self.person.get_media_list())

        sect_name = Html('h3', self.sort_name.strip(), inline=True)

        # begin summaryarea division
        with Html('div', id='summaryarea') as summaryarea:

            # begin general details table
            with Html('table', class_='infolist') as table:
                summaryarea += table

                primary_name = self.person.get_primary_name()
                all_names = [primary_name] + self.person.get_alternate_names()

                # Names [and their sources]
                for name in all_names:
                    pname =  _nd.display_name(name)
                    pname += self.get_citation_links( name.get_source_references() )

                    # if we have just a firstname, then the name is preceeded by ", "
                    # which doesn't exactly look very nice printed on the web page
                    if pname[:2] == ', ':
                        pname = pname[2:]

                    type_ = str( name.get_type() )
                    trow = Html('tr') + (
                        Html('td', type_, class_='ColumnAttribute', inline=True)
                        )
                    table += trow
                    tcell = Html('td', pname, class_='ColumnValue', inline=True)
                    trow += tcell

                    # display any notes associated with this name
                    notelist = name.get_note_list()
                    if len(notelist):
                        unordered = Html('ul')
                        tcell += unordered 
                        for notehandle in notelist:
                            note = db.get_note_from_handle(notehandle)
                            if note:
                                note_text = note.get()
                                if note_text:
 
                                    # styled notes
                                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                                        note.get_format())
                                    if htmlnotetext:
                                        text = htmlnotetext
                                    else:
                                        text = Html('p', note_text) 
                                    unordered += text

                # display call names
                first_name = primary_name.get_first_name()
                for name in all_names:
                    call_name = name.get_call_name()
                    if call_name and call_name != first_name:
                        call_name += self.get_citation_links( 
                            name.get_source_references() )
                        trow = Html('tr') + (
                            Html('td', _('Common Name'), class_='ColumnAttribute', 
                                inline=True),
                            Html('td', call_name, class_='ColumnValue', inline=True)
                            )
                        table += trow
  
                # display the nickname attribute
                nick_name = self.person.get_nick_name()
                if nick_name and nick_name != first_name:
                    nick_name += self.get_citation_links( 
                        self.person.get_source_references() )
                    trow = Html('tr') + (
                        Html('td', _('Nick Name'), class_='ColumnAttribute', 
                            inline=True),
                        Html('td', nick_name, class_='ColumnValue', inline=True)
                        ) 
                    table += trow 

                # GRAMPS ID
                if not self.noid:
                    trow = Html('tr') + (
                        Html('td', _('GRAMPS ID'), class_='ColumnAttribute', 
                            inline=True),
                        Html('td', self.person.gramps_id, class_='ColumnValue', 
                            inline=True)
                        ) 
                    table += trow

                # Gender
                gender = self.gender_map[self.person.gender]
                trow = Html('tr') + (
                    Html('td', _('Gender'), class_='ColumnAttribute', inline=True),
                    Html('td', gender, class_='ColumnValue', inline=True)
                    )
                table += trow

                # Age At Death???
                birth_ref = self.person.get_birth_ref()
                birth_date = None
                if birth_ref:
                    birth_event = db.get_event_from_handle(birth_ref.ref)
                    birth_date = birth_event.get_date_object()

                if birth_date is not None:
                    alive = probably_alive(self.person, db, date.Today())
                    death_ref = self.person.get_death_ref()
                    death_date = None
                    if death_ref:
                        death_event = db.get_event_from_handle(death_ref.ref)
                        death_date = death_event.get_date_object()

                    if not alive and death_date is not None:
                        nyears = death_date - birth_date
                        nyears.format(precision=3)
                        trow = Html('tr') + (
                            Html('td', _('Age at Death'), class_='ColumnAttribute', 
                                inline=True),
                            Html('td', nyears, class_='ColumnValue', inline=True)
                            )
                        table += trow

        # return all three pieces to its caller
        # do NOT combine before returning to class IndividualPage
        return thumbnail, sect_name, summaryarea

    def display_ind_events(self):
        """
        will create the events table
        """

        evt_ref_list = self.person.get_event_ref_list()

        if not evt_ref_list:
            return None
        db = self.report.database
            
        with Html('div', class_='subsection', id='events') as section:
            section += Html('h4', _('Events'), inline=True)
            with Html('table', class_='infolist eventtable') as table:
                section += table
                with Html('thead') as thead:
                    table += thead
                    thead += self.display_event_header()
                with Html('tbody') as tbody:
                    table += tbody
                    for event_ref in evt_ref_list:
                        event = db.get_event_from_handle(event_ref.ref)
                        if event:
                            tbody += self.display_event_row(db, event, event_ref)
        return section

    def display_event_row(self, db, event, event_ref):
        """
        display the event row
        """
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

            place = self.place_link(place_handle,
                                        ReportUtils.place_name(db, place_handle), up=True)
        else:
            place = ''

        # begin table row for either: display_event_row() or format_event()
        with Html('tr') as trow:

            # Event/  Type
            evt_name = str(event.get_type())

            if event_ref.get_role() == EventRoleType.PRIMARY:
                txt = u"%(evt_name)s" % locals()
            else:
                evt_role = event_ref.get_role()
                txt = u"%(evt_name)s (%(evt_role)s)" % locals()
            txt = txt or '&nbsp;'
            trow += Html('td', txt, class_='ColumnValue EventType', inline=True)

            # Date
            event_date = event.get_date_object()
            if event_date:
                txt = _dd.display(event_date)
            else:
                txt = '&nbsp;'
            trow += Html('td', txt, class_='ColumnValue Date', inline=True)

            # Place
            place_handle = event.get_place_handle()
            if place_handle:

                lnk = (self.report.cur_fname, self.page_title, self.gid)
                if place_handle in self.place_list:
                    if lnk not in self.place_list[place_handle]:
                        self.place_list[place_handle].append(lnk)
                else:
                    self.place_list[place_handle] = [lnk]

                place = self.place_link(place_handle,
                                                   ReportUtils.place_name(db, 
                                                   place_handle),
                                                   up=True)
            else:
                place = None
            txt = place or '&nbsp;'
            trow += Html('td', txt, class_='ColumnValue Place') 

            # Description
            # Get the links in super script to the Source References section in the same page
            sref_links = self.get_citation_links(event.get_source_references())
            txt = ''.join(wrapper.wrap(event.get_description()))
            txt = txt or '&nbsp;'
            trow += Html('td', txt, class_='ColumnValue Description')

            # event sources
            citation = self.get_citation_links(event.get_source_references())
            txt = citation or '&nbsp;'
            trow += Html('td', txt, class_='ColumnValue Source')

            # Notes
            # if the event or event reference has a note attached to it,
            # get the text and format it correctly
            notelist = event.get_note_list()
            notelist.extend(event_ref.get_note_list())
            tcell = Html('td', class_='ColumnValue Notes')
            trow += tcell
            if not notelist:
                tcell += '&nbsp;'
            else:
                for notehandle in notelist:
                    note = db.get_note_from_handle(notehandle)
                    if note:
                        note_text = note.get()
                        if note_text:
 
                            # styled notes
                            htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                                note.get_format())
                            if htmlnotetext:
                                text = htmlnotetext
                            else:
                                text = Html('p', note_text) 
                            tcell += text

        # return events table row to its caller
        return trow 

    def display_addresses(self):
        """
        display a person's addresses ...
        """

        alist = self.person.get_address_list()
        if not alist:
            return None

        # begin addresses division and title
        with Html('div', class_='subsection', id='Addresses') as section:
            section += Html('h4', _('Addresses'), inline=True)

            # begin addresses table and table head
            with Html('table', class_='infolist') as table: 
                section += table

                thead = Html('thead')
                table += thead
                trow = Html('tr') + (
                    Html('th', _('Date of Residence'), class_ = 'ColumnAttribute',
                        inline=True),
                    Html('th', _('Address'), class_ = 'ColumnAttribute')
                    )
                thead += trow

                # begin table body
                tbody = Html('tbody')
                table += tbody

                for addr in alist:
                    location = ReportUtils.get_address_str(addr)
                    citation_link = self.get_citation_links(addr.get_source_references())
                    date = _dd.display(addr.get_date_object())

                    trow = Html('tr') + (
                        Html('td', date, class_='ColumnValue Date', inline=True)
                        )
                    tbody += trow
                    tcell = Html('td', location, class_='ColumnValue Citation')
                    trow += tcell  
                    if len(citation_link):
                        for citation in citation_link.splitlines():
                            tcell += Html('sup') + (
                                Html('a', citation, href='#sref%s' % citation)
                                )

        # return address division to its caller
        return section

    def display_child_link(self, child_handle):
        """
        display child link ...
        """
        db = self.report.database

        child = db.get_person_from_handle(child_handle)
        gid = child.gramps_id
        list = Html('li')
        if child_handle in self.ind_list:
            url = self.report.build_url_fname_html(child_handle, 'ppl', True)
            list += self.person_link(url, child, True, gid)
        else:
            child_name = self.get_name(child)
            list += child_name

        # return list to its caller
        return list

    def display_parent(self, handle, title, rel):
        """
        This will display a parent ...
        """
        db = self.report.database

        person = db.get_person_from_handle(handle)
        tcell1 = Html('td', title, class_='ColumnAttribute', inline=True)
        tcell2 = Html('td', class_='ColumnValue')

        gid = person.gramps_id
        if handle in self.ind_list:
            url = self.report.build_url_fname_html(handle, 'ppl', True)
            tcell2 += self.person_link(url, person, True, gid)
        else:
            person_name = self.get_name(person)
            tcell2 += person_name
        if rel and rel != ChildRefType(ChildRefType.BIRTH):
            tcell2 += '&nbsp;&nbsp;&nbsp;(%s)' % str(rel)

        # return table columns to its caller
        return tcell1, tcell2

    def display_ind_parents(self):
        """
        Display a person's parents
        """

        birthorder = self.report.options['birthorder']
        parent_list = self.person.get_parent_family_handle_list()

        if not parent_list:
            return None

        db = self.report.database

        # begin parents division
        with Html('div', class_='subsection', id='parents') as section:
            section += Html('h4', _('Parents'), inline=True)

            # begin parents table
            with Html('table', class_='infolist') as table:
                section += table

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
                            trow = Html('tr') +(
                                Html('td', '&nbsp;', colspan=2, inline=True)
                                )
                            table += trow
                        else:
                            first = False

                        father_handle = family.get_father_handle()
                        if father_handle:
                            trow = Html('tr')
                            table += trow

                            tabcol1, tabcol2 = self.display_parent(father_handle, _('Father'), frel)
                            trow += (tabcol1, tabcol2)
                        mother_handle = family.get_mother_handle()
                        if mother_handle:
                            trow = Html('tr')
                            table += trow
                            tabcol1, tabcol2  = self.display_parent(mother_handle, _('Mother'), mrel)
                            trow += (tabcol1, tabcol2)

                        first = False
                        if len(child_ref_list) > 1:
                            childlist = [child_ref.ref for child_ref in child_ref_list]
                            for child_handle in childlist:
                                sibling.add(child_handle)   # remember that we've already "seen" this child

                    # now that we have all natural siblings, display them...    
                    if len(sibling):
                        trow = Html('tr') + (
                            Html('td', _('Siblings'), class_='ColumnAttribute', inline=True)
                            )
                        table += trow
                        tcell = Html('td', class_='ColumnValue')
                        trow += tcell
                        ordered = Html('ol')
                        tcell += ordered 

                        if birthorder:
                            kids = []
                            kids = sorted(add_birthdate(db, sibling))

                            for birth_date, child_handle in kids:
                                if child_handle != self.person.handle:
                                    ordered += self.display_child_link(child_handle)

                        else:

                            for child_handle in sibling:
                                if child_handle != self.person.handle:
                                    ordered += self.display_child_link(child_handle)

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

                    # now that we have all half- siblings, display them...    
                    if len(half_siblings):
                        trow = Html('tr') + (
                            Html('td', _('Half Siblings'), class_='ColumnAttribute', inline=True),
                            )
                        table += trow
                        tcell = Html('td', class_='ColumnValue')
                        trow += tcell
                        ordered = Html('ol')
                        tcell += ordered

                        if birthorder:
                            kids = []
                            kids = sorted(add_birthdate(db, half_siblings))

                            for birth_date, child_handle in kids:
                                ordered += self.display_child_link(child_handle)

                        else:

                            for child_handle in half_siblings:
                                ordered += self.display_child_link(child_handle)

                    # get step-siblings
                    if showallsiblings:
                        step_siblings = set()

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

                        # now that we have all step- siblings, display them...    
                        if len(step_siblings):
                            trow = Html('tr') + (
                                Html('td', _('Step Siblings'), class_='ColumnAttribute', inline=True)
                                )
                            table += trow
                            tcell = Html('td', class_='ColumnValue')
                            trow += tcell 
                            ordered = Html('ol')
                            tcell += ordered

                            if birthorder:
                                kids = []
                                kids = sorted(add_birthdate(db, step_siblings))

                                for birth_date, child_handle in kids:
                                    ordered += self.display_child_link(child_handle)

                            else:
 
                                for child_handle in step_siblings:
                                    ordered += self.display_child_link(child_handle)

        # return parents division to its caller
        return section

    def display_ind_families(self):
        """
        Displays a person's relationships ...
        """

        family_list = self.person.get_family_handle_list()
        if not family_list:
            return None

        db = self.report.database
        # begin families division and section title
        with Html('div', class_='subsection', id='families') as section:
            section += Html('h4', _('Families'), inline=True)

            # begin families table
            with Html('table', class_='infolist') as table:
                section += table

                for family_handle in family_list:
                    family = db.get_family_from_handle(family_handle)
                    self.display_partner(family, table)
                    childlist = family.get_child_ref_list()
                    if childlist:
                        trow = Html('tr') + (
                            Html('td', '&nbsp;', class_='ColumnType', inline=True),
                            Html('td', _('Children'), class_='ColumnAttribute', inline=True)
                            )
                        table += trow
                        tcell = Html('td', class_='ColumnValue')
                        trow += tcell
                        ordered = Html('ol')
                        tcell += ordered
                        childlist = [child_ref.ref for child_ref in childlist]

                        if self.report.options['birthorder']:
                            kids = []
                            kids = sorted(add_birthdate(db, childlist))

                            for birth_date, child_handle in kids:
                                ordered += self.display_child_link(child_handle)
                        else:

                            for child_handle in childlist:
                                ordered += self.display_child_link(child_handle)

        # return section to its caller
        return section

    def display_partner(self, family, relation_table):
        """
        display an individual's partner
        """

        gender = self.person.gender
        reltype = family.get_relationship()
        db = self.report.database

        if reltype == FamilyRelType.MARRIED:
            if gender == Person.FEMALE:
                relstr = _("Husband")
            elif gender == Person.MALE:
                relstr = _("Wife")
            else:
                relstr = _("Partner")
        else:
            relstr = _("Partner")

        partner_handle = ReportUtils.find_spouse(self.person, family)
        if partner_handle:
            partner = db.get_person_from_handle(partner_handle)
            partner_name = self.get_name(partner)
        else:
            partner_name = _("unknown")
        rtype = str(family.get_relationship())
        trow = Html('tr', class_='BeginFamily') 
        tabcol1 = Html('td', rtype, class_='ColumnType', inline=True)
        tabcol2 = Html('td', relstr, class_='ColumnAttribute', inline=True)  
        tabcol3 = Html('td', class_='ColumnValue')
        if partner_handle:
            gid = partner.gramps_id
            if partner_handle in self.ind_list:
                url = self.report.build_url_fname_html(partner_handle, 'ppl', True)
                tabcol3 += self.person_link(url, partner, True, gid)
            else:
                tabcol3 += partner_name
        trow += (tabcol1, tabcol2, tabcol3)
        relation_table += trow

        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            evtType = str(event.get_type())
            trow = Html('tr')
            tabcol1 = Html('td', '&nbsp;', class_='ColumnType', inline=True)
            tabcol2 = Html('td', '', class_='ColumnAttribute', inline=True)
            tabcol3 = Html('td', class_='ColumnValue')
            formatted_event = self.format_event(event, event_ref) 
            tabcol3 += formatted_event
            trow += (tabcol1, tabcol2, tabcol3)
            relation_table += trow 

        for attr in family.get_attribute_list():
            attrType = str(attr.get_type())
            if attrType:
                trow = Html('tr')
                tabcol1 = Html('td', '&nbsp;', class_='ColumnType', inline=True)
                tabcol2 = Html('td', attrType, class_='ColumnAttribute', inline=True)
                tabcol3 = Html('td', attr.get_value(), class_='ColumnValue', inline=True)
                trow += (tabcol1, tabcol2, tabcol3)
                relation_table += trow

        notelist = family.get_note_list()
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            if note:
                trow = Html('tr') 
                tabcol1 = Html('td', '&nbsp;', class_='ColumnType', inline=True)
                tabcol2 = Html('td', _('Narrative'), class_='ColumnAttribute', inline=True)
                tabcol3 = Html('td', class_='ColumnValue')

                note_text = note.get()
                if note_text:
 
                    # styled notes
                    htmlnotetext = self.styled_note(note.get_styledtext(),
                                                                        note.get_format())
                    if htmlnotetext:
                        text = htmlnotetext
                    else:
                        text = Html('p', note_text) 
                    tabcol3 += text
                trow += (tabcol1, tabcol2, tabcol3)
                relation_table += trow  

        # return table to its caller
        return relation_table

    def pedigree_person(self, person):
        """
        will produce a hyperlink for a pedigree person ...
        """

        person_name = self.get_name(person)
        if person.handle in self.ind_list:
            url = self.report.build_url_fname_html(person.handle, 'ppl', True)
            hyper = self.person_link(url, person, name_style=True)
        else:
            hyper = person_name

        # return hyperlink to its callers
        # can be an actual hyperlink or just a person's name
        return hyper

    def pedigree_family(self):
        """
        Returns a family pedigree
        """
        db = self.report.database

        ped = []
        for family_handle in self.person.get_family_handle_list():
            rel_family = db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person, rel_family)
            if spouse_handle:
                spouse = db.get_person_from_handle(spouse_handle)
                pedsp = (Html('li', class_='spouse') + 
                         self.pedigree_person(spouse)
                        )
                ped += [pedsp]
            else:
                pedsp = ped
            childlist = rel_family.get_child_ref_list()
            if childlist:
                with Html('ol') as childol:
                    pedsp += [childol]
                    for child_ref in childlist:
                        child = db.get_person_from_handle(child_ref.ref)
                        childol += (Html('li') +
                                    self.pedigree_person(child)
                                   )
        return ped

    def display_event_header(self):
        """
        will print the event header row for display_event_row() and
        format_event()
        """

        header_row = [_('EventType'), _('Date'), _('Place'), _('Description'), 
            _('Sources'), _('Notes')]

        # begin table header row
        trow = Html('tr')

        for section in header_row:
            trow += Html('th', section, class_ = 'ColumnAttribute %s' 
                % section, inline = True)

        # return header row to its caller
        return trow

    def format_event(self, event, event_ref):
        db = self.report.database

        with Html('table', class_='infolist eventtable') as table:
            with Html('thead') as thead:
                table += thead
                thead += self.display_event_header()
            with Html('tbody') as tbody:
                table += tbody
                tbody += self.display_event_row(
                          db, 
                          event, event_ref
                          )
        return table

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
        if len(gid_list):
            text = text + " <sup>"
            for ref in gid_list:
                index, key = self.bibli.add_reference(ref)
                id_ = "%d%s" % (index+1, key)
                text = text + '<a href="#sref%s">%s</a>' % (id_, id_)
            text = text + "</sup>"

        return text

class RepositoryListPage(BasePage):
    """
    Will create the repository list page
    """

    def __init__(self, report, title, repos_dict, keys):
        BasePage.__init__(self, report, title)

        db = report.database
        of = self.report.create_file('repositories')
        repolistpage, body = self.write_header(_('Repositories'))

        # begin RepositoryList division
        with Html('div', class_='content', id='RepositoryList') as section:
            body += section

            msg = _("This page contains an index of all the repositories in the "
                    "database, sorted by their title. Clicking on a repositories&#8217;s "
                    "title will take you to that repositories&#8217;s page.")
            section += Html('p', msg, id='description')

            # begin repositories table and table head
            with Html('table', class_='infolist repolist') as table:
                section += table 

                thead = Html('thead')
                table += thead
                trow = Html('tr') + (
                    Html('th', '&nbsp;', class_='ColumnRowLabel', inline=True),
                    Html('th', _('Type'), class_='ColumnType', inline=True),
                    Html('th', _('Name'), class_='ColumnName', inline=True)
                    )
                thead += trow

                # begin table body
                tbody = Html('tbody')
                table += tbody 

                index = 0
                for index, key in enumerate(keys):
                    (repo, handle) = repos_dict[key]

                    trow = Html('tr')
                    tbody += trow

                    # index number
                    tcell = Html('td', index+1, class_='ColumnRowLabel', inline=True)
                    trow += tcell

                    # repository type
                    rtype = repo.type.xml_str()
                    if rtype:
                        tcell = Html('td', rtype, class_='ColumnType')
                        trow += tcell

                    # repository name and hyperlink
                    repo_title = html_escape(repo.name)
                    if repo_title:
                        tcell = Html('td', class_='ColumnName') + \
                           self.repository_link(handle, repo_title, repo.gramps_id)
                        trow += tcell

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(repolistpage, of)

class RepositoryPage(BasePage):
    """
    will create the individual Repository Pages
    """

    def __init__(self, report, title, repo, handle):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file(handle, 'repo')
        self.up = True
        repositorypage, body = self.write_header(name_to_md5(repo.name))

        # begin RepositoryDetail division and page title
        with Html('div', class_='content', id='RepositoryDetail') as section:
            body += section
            section += Html('h3', repo.name)

            # write out repository
            section += self.write_repository(repo, handle)

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.mywriter(repositorypage, of)

    def write_address_list(self, obj,index=1):
        if len(obj.get_address_list()) == 0:
            return None

        # begin addresses division
        with Html('div', id='addresses') as section:

            # begin address table
            with Html('table', class_='infolist') as table:
                section += table

                tbody = Html('tbody')
                table += tbody

                for address in obj.get_address_list():
                    trow = Html('tr')
                    tbody += trow

                    tcell1 = Html('td', _('Address'), class_='ColumnAttribute', inline=True)
                    tcell2 = Html('td', '#%d %s' % (index, conf_priv(address)), 
                        class_='ColumnValue', inline=True)
                    trow += (tcell1, tcell2)

                    # address: date
                    date = _dd.display(address.get_date_object())
                    if date:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('Date'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', date, class_='ColumnValue Date', inline=True)
                        trow += (tcell1, tcell2)

                    # address: street
                    streetaddress = address.get_street()
                    if streetaddress:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('Street'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', streetaddress, class_='ColumnValue')
                        trow += (tcell1, tcell2)

                    # address: city
                    city = address.get_city()
                    if city:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('City'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', city, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2)

                    # address: county
                    county = address.get_county()
                    if county:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('County'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', county, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2)

                    # address: state
                    state = address.get_state()
                    if state:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('State'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', state, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2)

                    # address: country
                    country = address.get_country()
                    if country:
                        trow = Html('tr')
                        tbody += trow       
                        tcell1 = Html('td', _('Country'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', country, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2)

                    # address: ZIP/ Postalcode
                    postalcode = address.get_postal_code()
                    if postalcode:
                        trow = Html('tr')
                        tbody += trow 
                        tcell1 = Html('td', _('Postal code'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', postalcode, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2) 

                    # address: phone
                    phone = address.get_phone()
                    if phone:
                        trow = Html('tr')
                        tbody += trow
                        tcell1 = Html('td', _('Phone'), class_='ColumnAttribute', inline=True)
                        tcell2 = Html('td', phone, class_='ColumnValue', inline=True)
                        trow += (tcell1, tcell2)

                    # address: notes
                    notelist = self.display_note_list(address.get_note_list())
                    if notelist is not None:
                        section += notelist

                    # address: source references
                    sourcerefs = self.write_source_refs(address.get_source_references())
                    if sourcerefs is not None:
                        section += sourcerefs

                    # increase index value
                    index += 1

        # return addresses to its caller
        return section

    def write_source_refs(self, sourcelist):

        if not sourcelist:
            return None

        db = self.report.database 

        # Source References division and title
        with Html('div', class_='subsection', id='sourcerefs') as section:
            section += Html('h4', _('Source References'), inline=True)

            ordered = Html('ol')
            section += ordered
            list = Html('li')
            ordered += list

            source_dict = {}
            # Sort the sources
            for handle in sourcelist:
                source = db.get_source_from_handle(handle)
                key = source.get_title() + str(source.get_gramps_id())
                source_dict[key] = (source, handle)
            keys = sorted(source_dict, key=locale.strxfrm)

            for index, key in enumerate(keys):
                (source, handle) = source_dict[key]
                source_title = source.get_title()
            
                list += self.source_link(handle, title, cindex+1, source.gramps_id, True)

        # return division to its caller
        return section   

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

        self.title = self.options['title']
        self.inc_gallery = self.options['gallery']
        self.inc_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # name format option
        self.name_format = self.options['name_format']

        # include repository page or not?
        self.inc_repository = self.options['inc_repository']

        # Download Options Tab
        self.inc_download = self.options['incdownload']
        self.dl_fname1 = self.options['down_fname1']
        self.dl_descr1 = self.options['dl_descr1']
        self.dl_fname2 = self.options['down_fname2']
        self.dl_descr2 = self.options['dl_descr2']
        self.dl_copy = self.options['dl_cright']

        self.encoding = self.options['encoding']

        self.use_archive = self.options['archive']
        self.use_intro = self.options['intronote'] or \
                         self.options['introimg']
        self.use_home = self.options['homenote'] or \
                        self.options['homeimg']
        self.use_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # either include the gender graphics or not?
        self.graph = self.options['graph']

        # whether to display children in birthorder or entry order?
        self.birthorder = self.options['birthorder']

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

        self.progress = ProgressMeter(_("Narrated Web Site Report"), '')

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

        # repository pages
        repolist = self.database.get_repository_handles()         
        self.repository_pages(repolist)

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

        # Mainz stylesheet graphics
        # will only be used if Mainz is slected as the stylesheet
        Mainz_images = ["Web_Mainz_Bkgd.png", "Web_Mainz_Header.png", 
                                     "Web_Mainz_Mid.png", "Web_Mainz_MidLight.png"]

        # Copy Mainz Style Images
        if self.css == "Web_Mainz.css":
            imgs += Mainz_images

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
            SurnamePage(self, self.title, surname, handle_list, ind_list)
            self.progress.step()

    def source_pages(self, source_list):

        self.progress.set_pass(_("Creating source pages"), len(source_list))

        SourceListPage(self, self.title, source_list.keys())

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

        MediaListPage(self, self.title)

        prev = None
        total = len(self.photo_list)
        sort = Sort.Sort(self.database)
        photo_keys = sorted(self.photo_list, key=sort.by_media_title_key)

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

    def repository_pages(self, repolist):

        db = self.database
        repos_dict = {}

        # Sort the repositories
        for handle in repolist:
            repo = db.get_repository_from_handle(handle)
            key = repo.name + str(repo.get_gramps_id())
            repos_dict[key] = (repo, handle)
            
        keys = sorted(repos_dict, key=locale.strxfrm)

        # set progress bar pass for Repositories
        self.progress.set_pass(_('Creating repository pages'), len(repos_dict))

        # RepositoryListPage Class
        RepositoryListPage(self, self.title, repos_dict, keys)

        index = 0
        for index, key in enumerate(keys):
            (repo, handle) = repos_dict[key]

            # RepositoryPage Class
            RepositoryPage(self, self.title, repo, handle)

            self.progress.step()

    def add_image(self, option_name, height=0):
        pic_id = self.options[option_name]
        if pic_id:
            obj = self.database.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    newpath, thumb_path = self.prepare_copy_media(obj)
                    self.copy_file(Utils.media_path_full(self.database, obj.get_path()),
                                    newpath)

                    # begin image
                    image = Html('img')
                    img_attr = ''
                    if height:
                        img_attr += ' height="%d" ' % height
                    img_attr += ' src="%s" alt="%s" ' % (newpath, obj.get_description())

                    # add image attributes to image
                    image.attr = img_attr

                    # return an image
                    return image   

                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        # no image to return
        return None

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
        self.__add_download_options(menu) 
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

        # We must figure out the value of the first option before we can
        # create the EnumeratedListOption
        fmt_list = _nd.get_name_format()
        name_format = EnumeratedListOption(_("Name format"), fmt_list[0][0])
        for num, name, fmt_str, act in fmt_list:
            name_format.add_item(num, name)
        name_format.set_help(_("Select the format to display names"))
        menu.add_option(category_name, "name_format", name_format)

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in _WEB_EXT:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        css = EnumeratedListOption(_('StyleSheet'), CSS_FILES[0][1])
        for style in CSS_FILES:
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

        self.__gallery = BooleanOption(_("Include images and media objects"), True)
        self.__gallery.set_help(_('Whether to include a gallery of media objects'))
        menu.add_option(category_name, 'gallery', self.__gallery)
        self.__gallery.connect('value-changed', self.__gallery_changed)

        self.__maxinitialimagewidth = NumberOption(_("Max width of initial image"), 
            _DEFAULT_MAX_IMG_WIDTH, 0, 2000)
        self.__maxinitialimagewidth.set_help(_("This allows you to set the maximum width "
                              "of the image shown on the media page. Set to 0 for no limit."))
        menu.add_option(category_name, 'maxinitialimagewidth', self.__maxinitialimagewidth)

        self.__maxinitialimageheight = NumberOption(_("Max height of initial image"), 
            _DEFAULT_MAX_IMG_HEIGHT, 0, 2000)
        self.__maxinitialimageheight.set_help(_("This allows you to set the maximum height "
                              "of the image shown on the media page. Set to 0 for no limit."))
        menu.add_option(category_name, 'maxinitialimageheight', self.__maxinitialimageheight)

        self.__gallery_changed()

        nogid = BooleanOption(_('Suppress GRAMPS ID'), False)
        nogid.set_help(_('Whether to include the Gramps ID of objects'))
        menu.add_option(category_name, 'nogid', nogid)

        inc_repository = BooleanOption(_('Include Repository Pages'), False)
        inc_repository.set_help(_('Whether to include the Repository Pages or not?'))
        menu.add_option(category_name, 'inc_repository', inc_repository)

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

    def __add_download_options(self, menu):
        """
        Options for the download tab ...
        """

        category_name = _("Download")

        self.__incdownload = BooleanOption(_("Include download page"), False)
        self.__incdownload.set_help(_('Whether to include a database download option'))
        menu.add_option(category_name, 'incdownload', self.__incdownload)
        self.__incdownload.connect('value-changed', self.__download_changed)

        self.__down_fname1 = DestinationOption(_("Download Filename #1"),
            os.path.join(const.USER_HOME, ""))
        self.__down_fname1.set_help(_("File to be used for downloading of database"))
        menu.add_option(category_name, "down_fname1", self.__down_fname1)

        self.__dl_descr1 = StringOption(_("Description for this Download"), _('Smith Family Tree'))
        self.__dl_descr1.set_help(_('Give a description for this file.'))
        menu.add_option(category_name, 'dl_descr1', self.__dl_descr1)

        self.__down_fname2 = DestinationOption(_("Download Filename #2"),
            os.path.join(const.USER_HOME, ""))
        self.__down_fname2.set_help(_("File to be used for downloading of database"))
        menu.add_option(category_name, "down_fname2", self.__down_fname2)

        self.__dl_descr2 = StringOption(_("Description for this Download"), _('Johnson Family Tree'))
        self.__dl_descr2.set_help(_('Give a description for this file.'))
        menu.add_option(category_name, 'dl_descr2', self.__dl_descr2)

        self.__dl_cright = EnumeratedListOption(_('Download Copyright License'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            self.__dl_cright.add_item(index, copt)
        self.__dl_cright.set_help( _("The copyright to be used for ths download file?"))
        menu.add_option(category_name, "dl_cright", self.__dl_cright)

        self.__download_changed()

    def __add_advanced_options(self, menu):
        """
        Options on the "Advanced" tab.
        """
        category_name = _("Advanced")

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1] )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)

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

        showpartner = BooleanOption(_("Include a column for partners on the "
                                    "index pages"), False)
        showpartner.set_help(_('Whether to include a partners column'))
        menu.add_option(category_name, 'showpartner', showpartner)

        showparents = BooleanOption(_("Include a column for parents on the "
                                      "index pages"), False)
        showparents.set_help(_('Whether to include a parents column'))
        menu.add_option(category_name, 'showparents', showparents)

        showallsiblings = BooleanOption(_("Include half and/ or "
                                           "step-siblings on the individual pages"), False)
        showallsiblings.set_help(_( "Whether to include half and/ or "
                                    "step-siblings with the parents and siblings"))
        menu.add_option(category_name, 'showhalfsiblings', showallsiblings)

        birthorder = BooleanOption(_('Sort children in birth order'), False)
        birthorder.set_help(_('Whether to display children in birth order'
                                            ' or in entry order?'))
        menu.add_option(category_name, 'birthorder', birthorder)

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

    def __gallery_changed(self):
        """
        Handles the changing nature of gallery
        """

        if self.__gallery.get_value() == False:
            self.__maxinitialimagewidth.set_available(False)
            self.__maxinitialimageheight.set_available(False)
        else:
            self.__maxinitialimagewidth.set_available(True)
            self.__maxinitialimageheight.set_available(True)

    def __living_changed(self):
        """
        Handle a change in the living option
        """
        if self.__living.get_value() == _INCLUDE_LIVING_VALUE:
            self.__yearsafterdeath.set_available(False)
        else:
            self.__yearsafterdeath.set_available(True)

    def __download_changed(self):
        """
        Handles the changing nature of include download page
        """

        if self.__incdownload.get_value() == False:
            self.__down_fname1.set_available(False)
            self.__dl_descr1.set_available(False)
            self.__down_fname2.set_available(False)
            self.__dl_descr2.set_available(False)
            self.__dl_cright.set_available(False)
        else:
            self.__down_fname1.set_available(True)
            self.__dl_descr1.set_available(True)
            self.__down_fname2.set_available(True)
            self.__dl_descr2.set_available(True)
            self.__dl_cright.set_available(True)

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
    temp_list = sorted(sname_sub, key=locale.strxfrm)
    
    for name in temp_list:
        slist = sorted(((sortnames[x], x) for x in sname_sub[name]), 
                    key=lambda x:locale.strxfrm(x[0]))
        entries = [x[1] for x in slist]
        sorted_lists.append((name, entries))

    return sorted_lists

# Modified _get_regular_surname from WebCal.py to get prefix, first name, and suffix
def _get_short_name(gender, name):
    """ Will get prefix and suffix for all people passed through it """

    short_name = name.get_first_name()
    prefix = name.get_surname_prefix()
    if prefix:
        short_name = prefix + " " + short_name
    if gender == Person.FEMALE:
        return short_name
    else: 
        suffix = name.get_suffix()
        if suffix:
            short_name = short_name + ", " + suffix
    return short_name

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
            c = normalize('NFKC', keyname)[0].upper()
            # See : http://www.gramps-project.org/bugs/view.php?id=2933
            (lang_country, modifier ) = locale.getlocale()
            if lang_country == "sv_SE" and ( c == u'W' or c == u'V' ):
                first_letters.append(u'V')
            else:
                first_letters.append(c)

    return first_letters

def _has_webpage_extension(url):
    """
    determine if a filename has an extension or not...

    url = filename to be checked
    """

    for ext in _WEB_EXT:
        if url.endswith(ext):
            return True
    return False

def alphabet_navigation(db, handle_list, key):
    """
    Will create the alphabetical navigation bar...

    handle_list -- a list of people's or Places' handles
    key -- _PERSON or _PLACE
    """

    sorted_set = {}

    # The comment below from the glibc locale sv_SE in
    # localedata/locales/sv_SE :
    #
    # % The letter w is normally not present in the Swedish alphabet. It
    # % exists in some names in Swedish and foreign words, but is accounted
    # % for as a variant of 'v'.  Words and names with 'w' are in Swedish
    # % ordered alphabetically among the words and names with 'v'. If two
    # % words or names are only to be distinguished by 'v' or % 'w', 'v' is
    # % placed before 'w'.
    #
    # See : http://www.gramps-project.org/bugs/view.php?id=2933
    #
    (lang_country, modifier ) = locale.getlocale()
    for ltr in get_first_letters(db, handle_list, key):
        if ltr in sorted_set:
            sorted_set[ltr] += 1
        else:
            sorted_set[ltr] = 1

    # remove the number of each occurance of each letter
    sorted_alpha_index = sorted((l for l in sorted_set if l != ','), 
                                 key=locale.strxfrm)

    # if no letters, return None back to its callers
    if not sorted_alpha_index:
        return None

    # begin alphabet division
    with Html('div', id='alphabet') as section:

        # set up table
        with Html('table', class_='infolist alphabet') as table:
            section += table

            num_ltrs = len(sorted_alpha_index)
            nrows = (num_ltrs / 35) + 1
            index = 0
            for rows in xrange(nrows):
                trow = Html('tr')  
                table += trow
                unordered = Html('ul') 
                trow += unordered
                cols = 0
                while (cols <= 35 and index < num_ltrs):
                    ltr = sorted_alpha_index[index]
                    title_str = _('Surnames')  if key == 0 else _('Places')
                    if lang_country == "sv_SE" and letter == u'V':
                        title_str += _(' starting with %s') % "V,W" 
                        unordered += (Html('li', class_='letters', inline=True) +
                             Html('a', "V,W", href="#V,W", title=title_str)
                             )
                    else:
                        title_str += _(' starting with %s') % ltr 
                        unordered += Html('li', class_='letters', inline=True) + (
                            Html('a', ltr, href='#%s' % ltr, title=title_str)
                            )
                    cols += 1
                    index += 1

    # return alphabet navigation to its callers
    return section

def add_birthdate(db, childlist):
    """
    This will sort a list of child handles in birth order
    """

    sorted_children = []
    for child_handle in childlist:
        child = db.get_person_from_handle(child_handle)

        birth_date = None
        birth_ref = child.get_birth_ref()
        if birth_ref:
            birth_event = db.get_event_from_handle(birth_ref.ref)
            birth_date = birth_event.get_date_object()
        if birth_date is not None:
                year = birth_date.get_year()
                if year:
                    year = str(year)
                else:
                    year = str(1001) 
                month = birth_date.get_month()
                if month:
                    if 0 < month < 10:
                        month = '0' + str(month)
                    else:
                        month = str(month)
                else:
                    month = str(12)
                day = birth_date.get_day()
                if day:
                    if 0 < day < 10:
                        day = '0' + str(day)
                    else:
                        day = str(day)
                else:
                    day = str(31)
        else:
            year, month, day = str(1001), str(12), str(31)
        date_obj = year + month + day
        sorted_children.append((date_obj, child_handle))

    return sorted_children

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
