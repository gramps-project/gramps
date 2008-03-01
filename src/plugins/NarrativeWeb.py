#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007       Gary Burton <gary.burton@zen.co.uk>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Pubilc License as published by
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
_NAME_COL  = 3

_MAX_IMG_WIDTH = 800   # resize images that are wider than this
_MAX_IMG_HEIGHT = 600  # resize images that are taller than this
_WIDTH = 160
_HEIGHT = 50
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5

_CSS_FILES = [
    [_("Modern"),         'main1.css'],
    [_("Business"),       'main2.css'],
    [_("Certificate"),    'main3.css'],
    [_("Antique"),        'main4.css'],
    [_("Tranquil"),       'main5.css'],
    [_("Sharp"),          'main6.css'],
    [_("No style sheet"), ''],
    ]

_CHARACTER_SETS = [
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
    '<img alt="Creative Commons License - By attribution" title="Creative '
    'Commons License - By attribution" src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No '
    'derivations" title="Creative Commons License - By attribution, '
    'Non-commercial, No derivations" src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, '
    'Share-alike" title="Creative Commons License - By attribution, '
    'Non-commerical, Share-alike" src="somerights20.gif" /></a>'
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

class BasePage:
    def __init__(self, title, options, archive, photo_list, gid):
        self.title_str = title
        self.gid = gid
        self.inc_download = options['incdownload']
        self.html_dir = options['target']
        self.copyright = options['cright']
        self.options = options
        self.archive = archive
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
        self.photo_list = photo_list
        self.usegraph = options['graph']
        self.graphgens = options['graphgens']
        self.use_home = self.options['homenote'] != "" or \
                        self.options['homeimg'] != ""
        self.page_title = ""
        self.warn_dir = True

    def store_file(self,archive, html_dir,from_path,to_path):
        if archive:
            archive.add(str(from_path),str(to_path))
        else:
            dest = os.path.join(html_dir,to_path)
            dirname = os.path.dirname(dest)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            if from_path != dest:
                shutil.copyfile(from_path,dest)
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

    def copy_media(self,photo,store_ref=True):

        handle = photo.get_handle()
        if store_ref:
            lnk = (self.cur_name,self.page_title,self.gid)
            if self.photo_list.has_key(handle):
                if lnk not in self.photo_list[handle]:
                    self.photo_list[handle].append(lnk)
            else:
                self.photo_list[handle] = [lnk]

        ext = os.path.splitext(photo.get_path())[1]
        real_path = "%s/%s" % (self.build_path(handle,'images'), handle+ext)
        thumb_path = "%s/%s.png" % (self.build_path(handle,'thumb'), handle)
        return (real_path,thumb_path)

    def create_file(self, name):
        self.cur_name = self.build_name("", name)
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io,'utf-8',self.encoding,
                                    'xmlcharrefreplace')
        else:
            page_name = os.path.join(self.html_dir,self.cur_name)
            of = codecs.EncodedFile(open(page_name, "w"),'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        return of

    def link_path(self, name,path):
        path = "%s/%s/%s" % (path, name[0].lower(), name[1].lower())
        path = self.build_name(path, name)
        return path

    def create_link_file(self, name,path):
        self.cur_name = self.link_path(name,path)
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io,'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        else:
            dirname = os.path.join(self.html_dir,
                                   path, name[0].lower(),
                                   name[1].lower())
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            page_name = self.build_name(dirname, name)
            of = codecs.EncodedFile(open(page_name, "w"),'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        return of

    def close_file(self, of):
        if self.archive:
            tarinfo = tarfile.TarInfo(self.cur_name)
            tarinfo.size = len(self.string_io.getvalue())
            tarinfo.mtime = time.time()
            if os.sys.platform != "win32":
                tarinfo.uid = os.getuid()
                tarinfo.gid = os.getgid()
            self.string_io.seek(0)
            self.archive.addfile(tarinfo,self.string_io)
            of.close()
        else:
            of.close()

    def lnkfmt(self,text):
        return md5.new(text).hexdigest()

    def display_footer(self, of,db):

        of.write('</div>\n')
        of.write('<div id="footer">\n')
        if self.copyright == 0:
            if self.author:
                self.author = self.author.replace(',,,','')
                year = time.localtime(time.time())[0]
                cright = _('&copy; %(year)d %(person)s') % {
                    'person' : self.author,
                    'year' : year }
                of.write('<br />%s\n' % cright)
        elif self.copyright <=6:
            of.write('<div id="copyright">')
            text = _CC[self.copyright-1]
            if self.up:
                text = text.replace('#PATH#','../../../')
            else:
                text = text.replace('#PATH#','')
            of.write(text)
            of.write('</div>\n')
        of.write('<div class="fullclear"></div>\n')
        of.write('</div>\n')
        if self.footer:
            note = db.get_note_from_gramps_id(self.footer)
            of.write('<div class="user_footer">\n')
            of.write(note.get(markup=True))
            of.write('</div>\n')
        of.write('</body>\n')
        of.write('</html>\n')
    
    def display_header(self, of,db,title,author="",up=False):
        self.up = up
        if up:
            path = "../../.."
        else:
            path = ""
            
        self.author = author
        of.write('<!DOCTYPE html PUBLIC ')
        of.write('"-//W3C//DTD XHTML 1.0 Strict//EN" ')
        of.write('"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        of.write('<html xmlns="http://www.w3.org/1999/xhtml" ')
        xmllang = Utils.xml_lang()
        of.write('xml:lang="%s" lang="%s">\n<head>\n' % (xmllang,xmllang))
        of.write('<title>%s - %s</title>\n' % (self.title_str, title))
        of.write('<meta http-equiv="Content-Type" content="text/html; ')
        of.write('charset=%s" />\n' % self.encoding)
        if path:
            of.write('<link href="%s/%s" ' % (path,_NARRATIVE))
        else:
            of.write('<link href="%s" ' % _NARRATIVE)
        of.write('rel="stylesheet" type="text/css" />\n')
        of.write('<link href="/favicon.ico" rel="Shortcut Icon" />\n')
        of.write('<!-- %sId%s -->\n' % ('$','$'))
        of.write('</head>\n')
        of.write('<body>\n')
        if self.header:
            note = db.get_note_from_gramps_id(self.header)
            of.write('  <div class="user_header">\n')
            of.write(note.get(markup=True))
            of.write('  </div>\n')
        of.write('<div id="navheader">\n')

        value = _dp.parse(time.strftime('%b %d %Y'))
        value = _dd.display(value)

        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % { 'date' : value }

        if self.linkhome:
            home_person_handle = db.get_default_handle()
            if home_person_handle:
                home_person = db.get_default_person()
                home_person_url = self.build_name(
                        self.build_path(home_person_handle, "ppl", up),
                        home_person.handle)
                home_person_name = home_person.get_primary_name().get_regular_name()
                msg += _('<br>for <a href="%s">%s</a>') % (home_person_url, home_person_name)

        of.write('<div class="navbyline">%s</div>\n' % msg)
        of.write('<h1 class="navtitle">%s</h1>\n' % self.title_str)
        of.write('<div class="nav">\n')

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

        if self.use_home:
            self.show_link(of,index_page,_('Home'),path)
        if self.use_intro:
            self.show_link(of,intro_page,_('Introduction'),path)
        self.show_link(of,surname_page,_('Surnames'),path)
        self.show_link(of,'individuals',_('Individuals'),path)
        self.show_link(of,'sources',_('Sources'),path)
        self.show_link(of,'places',_('Places'),path)
        if self.use_gallery:
            self.show_link(of,'gallery',_('Gallery'),path)
        if self.inc_download:
            self.show_link(of,'download',_('Download'),path)
        if self.use_contact:
            self.show_link(of,'contact',_('Contact'),path)
        of.write('</div>\n</div>\n')
        of.write('<div id="content">\n')

    def show_link(self, of,lpath,title,path):
        if path:
            of.write('<a href="%s/%s%s">%s</a>\n' % (path,lpath,self.ext,title))
        else:
            of.write('<a href="%s%s">%s</a>\n' % (lpath,self.ext,title))

    def display_first_image_as_thumbnail( self, of, db, photolist=None):

        if not photolist or not self.use_gallery:
            return
        
        photo_handle = photolist[0].get_reference_handle()
        photo = db.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        if mime_type:
            try:
                (real_path, newpath) = self.copy_media(photo)
                of.write('<div class="snapshot">\n')
                self.media_link(of,photo_handle, newpath,'',up=True)
                of.write('</div>\n')
            except (IOError,OSError),msg:
                WarningDialog(_("Could not add photo to page"),str(msg))
        else:
            of.write('<div class="snapshot">\n')
            descr = " ".join(wrapper.wrap(photo.get_description()))
            self.doc_link(of, photo_handle, descr, up=True)
            of.write('</div>\n')
            lnk = (self.cur_name, self.page_title, self.gid)
            if self.photo_list.has_key(photo_handle):
                if lnk not in self.photo_list[photo_handle]:
                    self.photo_list[photo_handle].append(lnk)
            else:
                self.photo_list[photo_handle] = [lnk]

    def display_additional_images_as_gallery( self, of, db, photolist=None):

        if not photolist or not self.use_gallery:
            return
            
        of.write('<div id="gallery">\n')
        of.write('<h4>%s</h4>\n' % _('Gallery'))
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
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))
            else:
                try:
                    descr = " ".join(wrapper.wrap(title))
                    self.doc_link(of, photo_handle, descr, up=True)
                    lnk = (self.cur_name,self.page_title,self.gid)
                    if self.photo_list.has_key(photo_handle):
                        if lnk not in self.photo_list[photo_handle]:
                            self.photo_list[photo_handle].append(lnk)
                    else:
                        self.photo_list[photo_handle] = [lnk]
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))
                
        of.write('<br clear="all" />\n')
        of.write('</div>\n')

    def display_note_list(self, of,db, notelist=None):
        if not notelist:
            return
        
        for notehandle in notelist:
            noteobj = db.get_note_from_handle(notehandle)
            format = noteobj.get_format()
            text = noteobj.get(markup=True)
            try:
                text = unicode(text)
            except UnicodeDecodeError:
                text = unicode(str(text),errors='replace')
    
            if text:
                of.write('<div id="narrative">\n')
                of.write('<h4>%s</h4>\n' % _('Narrative'))
                if format:
                    text = u"<pre>%s</pre>" % text
                else:
                    text = u"</p><p>".join(text.split("\n"))
                of.write('<p>%s</p>\n' % text)
                of.write('</div>\n')

    def display_url_list(self, of,urllist=None):
        if not urllist:
            return
        of.write('<div id="weblinks">\n')
        of.write('<h4>%s</h4>\n' % _('Weblinks'))
        of.write('<table class="infolist">\n')

        index = 1
        for url in urllist:
            uri = url.get_path()
            descr = url.get_description()
            if not descr:
                descr = uri
            of.write('<tr><td class="field">%d.</td>' % index)
            if url.get_type() == gen.lib.UrlType.EMAIL and not uri.startswith("mailto:"):
                of.write('<td class="data"><a href="mailto:%s">%s</a>' % (uri,descr))
            elif url.get_type() == gen.lib.UrlType.WEB_HOME and not uri.startswith("http://"):
                of.write('<td class="data"><a href="http://%s">%s</a>' % (uri,descr))
            elif url.get_type() == gen.lib.UrlType.WEB_FTP and not uri.startswith("ftp://"):
                of.write('<td class="data"><a href="ftp://%s">%s</a>' % (uri,descr))
            else:
                of.write('<td class="data"><a href="%s">%s</a>' % (uri,descr))
            of.write('</td></tr>\n')
            index = index + 1
        of.write('</table>\n')
        of.write('</div>\n')

    def display_source_refs(self, of, db, bibli):
        if bibli.get_citation_count() == 0:
            return
        of.write('<div id="sourcerefs">\n')
        of.write('<h4>%s</h4>\n' % _('Source References'))
        of.write('<table class="infolist">\n')

        cindex = 0
        for citation in bibli.get_citation_list():
            cindex += 1
            # Add this source to the global list of sources to be displayed
            # on each source page.
            lnk = (self.cur_name, self.page_title, self.gid)
            shandle = citation.get_source_handle()
            if self.src_list.has_key(shandle):
                if lnk not in self.src_list[shandle]:
                    self.src_list[shandle].append(lnk)
            else:
                self.src_list[shandle] = [lnk]
                
            # Add this source and its references to the page
            source = db.get_source_from_handle(shandle)
            title = source.get_title()
            of.write('<tr><td class="field">')
            of.write('<a name="sref%d"></a>%d.</td>' % (cindex, cindex))
            of.write('<td class="field" colspan=2>')
            self.source_link(of, source.handle, title, source.gramps_id, True)
            of.write('<p/>')
            of.write('</td></tr>\n')

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
                    tmp.append("%s: %s" % (_('Text'), note.get(True)))
                if len(tmp) > 0:
                    of.write('\t<tr><td></td>')
                    of.write('<td class="field">')
                    of.write('<a name="sref%d%s">' % (cindex, key))
                    of.write('</a>%d%s.</td>' % (cindex, key))
                    of.write('<td>')
                    of.write('<br />'.join(tmp))
                    of.write('<p/>')
                    of.write('</td></tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

    def display_references(self, of,db, handlelist):
        if not handlelist:
            return
        of.write('<div id="references">\n')
        of.write('<h4>%s</h4>\n' % _('References'))
        of.write('<table class="infolist">\n')
        
        sortlist = sorted(handlelist, 
                          key = operator.itemgetter(1), 
                          cmp = locale.strcoll)

        index = 1
        for (path, name,gid) in sortlist:
            of.write('<tr><td class="field">%d. ' % index)
            self.person_link(of,path, name,gid)
            of.write('</td></tr>\n')
            index = index + 1
        of.write('</table>\n')
        of.write('</div>\n')

    def build_path(self, handle,dirroot,up=False):
        path = ""
        if up:
            path = '../../../%s/%s/%s' % (dirroot,
                                          handle[0].lower(),
                                          handle[1].lower())
        else:
            path = "%s/%s/%s" % (dirroot, handle[0].lower(), handle[1].lower())           
        return path
            
    def build_name(self,path,base):
        if path:
            return path + "/" + base + self.ext
        else:
            return base + self.ext

    def person_link(self, of,path, name,gid="",up=True):
        if up:
            path = "../../../" + path

        of.write('<a href="%s">%s' % (path, name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def surname_link(self, of, name, opt_val=None,up=False):
        handle = self.lnkfmt(name)
        dirpath = self.build_path(handle,'srn',up)

        of.write('<a href="%s/%s%s">%s' % (dirpath, handle,self.ext, name))
        if opt_val != None:
            of.write('&nbsp;(%d)' % opt_val)
        of.write('</a>')

    def media_ref_link(self, of, handle, name,up=False):
        dirpath = self.build_path(handle,'img',up)
        of.write('<a href="%s/%s%s">%s</a>' % (
            dirpath, handle,self.ext, name))

    def media_link(self, of, handle,path, name,up,usedescr=True):
        dirpath = self.build_path(handle,'img',up)
        of.write('<div class="thumbnail">\n')
        of.write('<p><a href="%s/%s%s">' % (dirpath, handle,self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a></p>\n' % name)
        if usedescr:
            of.write('<p>%s</p>\n' % name)
        of.write('</div>\n')

    def doc_link(self, of, handle, name,up,usedescr=True):
        path = os.path.join('images','document.png')
        dirpath = self.build_path(handle,'img',up)
        of.write('<div class="thumbnail">\n')
        of.write('<p><a href="%s/%s%s">' % (dirpath, handle,self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a>' % name)
        of.write('</p>\n')
        if usedescr:
            of.write('<p>%s</p>\n' % name)
        of.write('</div>\n')

    def source_link(self, of, handle, name,gid="",up=False):
        dirpath = self.build_path(handle,'src',up)
        of.write('<a href="%s/%s%s">%s' % (
            dirpath, handle,self.ext, name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link(self, of, handle, name,gid="",up=False):
        dirpath = self.build_path(handle,'plc',up)
        of.write('<a href="%s/%s%s">%s' % (
            dirpath, handle,self.ext, name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link_str(self, handle, name,gid="",up=False):
        dirpath = self.build_path(handle,'plc',up)
        retval = '<a href="%s/%s%s">%s' % (
            dirpath, handle,self.ext, name)
        if not self.noid and gid != "":
            retval = retval + '&nbsp;<span class="grampsid">[%s]</span>' % gid
        return retval + '</a>'

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualListPage(BasePage):

    def __init__(self, db, title, person_handle_list,
                 options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_file("individuals")
        self.display_header(of,db,_('Individuals'),
                            get_researcher().get_name())

        msg = _("This page contains an index of all the individuals in the "
                "database, sorted by their last names. Selecting the person's "
                "name will take you to that person's individual page.")

        of.write('<h3>%s</h3>\n' % _('Individuals'))
        of.write('<p>%s</p>\n' % msg)
        of.write('<table class="infolist">\n<thead><tr>\n')
        of.write('<th>%s</th>\n' % _('Surname'))
        of.write('<th>%s</th>\n' % _('Name'))
        column_count = 2
        if self.showbirth:
            of.write('<th>%s</th>\n' % _('Birth'))
            column_count += 1
        if self.showdeath:
            of.write('<th>%s</th>\n' % _('Death'))
            column_count += 1
        if self.showspouse:
            of.write('<th>%s</th>\n' % _('Partner'))
            column_count += 1
        if self.showparents:
            of.write('<th>%s</th>\n' % _('Parents'))
            column_count += 1
        of.write('</tr></thead>\n<tbody>\n')

        person_handle_list = sort_people(db,person_handle_list)

        for (surname, handle_list) in person_handle_list:
            first = True
            of.write('<tr><td colspan="%d">&nbsp;</td></tr>\n' % column_count)
            for person_handle in handle_list:
                person = db.get_person_from_handle(person_handle)

                # surname column
                of.write('<tr><td class="category">')
                if first:
                    of.write('<a name="%s">%s</a>' % (self.lnkfmt(surname),surname))
                else:
                    of.write('&nbsp;')
                of.write('</td>')

                # firstname column
                of.write('<td class="data">')
                path = self.build_path(person.handle,"ppl",False)
                self.person_link(of, self.build_name(path,person.handle),
                                 _nd.display_given(person), person.gramps_id,False)
                of.write('</td>')

                # birth column
                if self.showbirth:
                    of.write('<td class="field">')
                    birth = ReportUtils.get_birth_or_fallback(db, person)
                    if birth:
                        if birth.get_type() == gen.lib.EventType.BIRTH:
                            of.write(_dd.display(birth.get_date_object()))
                        else:
                            of.write('<em>')
                            of.write(_dd.display(birth.get_date_object()))
                            of.write('</em>')
                    of.write('</td>')

                # death column
                if self.showdeath:
                    of.write('<td class="field">')
                    death = ReportUtils.get_death_or_fallback(db, person)
                    if death:
                        if death.get_type() == gen.lib.EventType.DEATH:
                            of.write(_dd.display(death.get_date_object()))
                        else:
                            of.write('<em>')
                            of.write(_dd.display(death.get_date_object()))
                            of.write('</em>')
                    of.write('</td>')

                # spouse (partner) column
                if self.showspouse:
                    of.write('<td class="field">')
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
                    of.write('</td>')

                # parents column
                if self.showparents:
                    of.write('<td class="field">')
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
                            of.write('%s, %s' % (father_name, mother_name))
                        elif mother:
                            of.write('%s' % mother_name)
                        elif father:
                            of.write('%s' % father_name)
                    of.write('</td>')

                # finished writing all columns
                of.write('</tr>\n')
                first = False
            
        of.write('</tbody>\n</table>\n')
        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SurnamePage(BasePage):

    def __init__(self, db, title, person_handle_list,
                 options, archive, media_list):
        
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_link_file(md5.new(title).hexdigest(),'srn')
        self.display_header(of,db,title,get_researcher().get_name(),True)

        msg = _("This page contains an index of all the individuals in the "
                "database with the surname of %s. Selecting the person's name "
                "will take you to that person's individual page.") % title

        of.write('<h3>%s</h3>\n' % title)
        of.write('<p>%s</p>\n' % msg)
        of.write('<table class="infolist">\n<thead><tr>\n')
        of.write('<th>%s</th>\n' % _('Name'))
        if self.showbirth:
            of.write('<th>%s</th>\n' % _('Birth'))
        if self.showdeath:
            of.write('<th>%s</th>\n' % _('Death'))
        if self.showspouse:
            of.write('<th>%s</th>\n' % _('Partner'))
        if self.showparents:
            of.write('<th>%s</th>\n' % _('Parents'))
        of.write('</tr></thead>\n<tbody>\n')

        for person_handle in person_handle_list:

            # firstname column
            person = db.get_person_from_handle(person_handle)
            of.write('<tr><td class="category">')
            path = self.build_path(person.handle,"ppl",True)
            self.person_link(of, self.build_name(path,person.handle),
                             person.get_primary_name().get_first_name(),
                             person.gramps_id,False)
            of.write('</td>')

            # birth column
            if self.showbirth:
                of.write('<td class="field">')
                birth = ReportUtils.get_birth_or_fallback(db, person)
                if birth:
                    if birth.get_type() == gen.lib.EventType.BIRTH:
                        of.write(_dd.display(birth.get_date_object()))
                    else:
                        of.write('<em>')
                        of.write(_dd.display(birth.get_date_object()))
                        of.write('</em>')
                of.write('</td>')

            # death column
            if self.showdeath:
                of.write('<td class="field">')
                death = ReportUtils.get_death_or_fallback(db, person)
                if death:
                    if death.get_type() == gen.lib.EventType.DEATH:
                        of.write(_dd.display(death.get_date_object()))
                    else:
                        of.write('<em>')
                        of.write(_dd.display(death.get_date_object()))
                        of.write('</em>')
                of.write('</td>')

            # spouse (partner) column
            if self.showspouse:
                of.write('<td class="field">')
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
                of.write('</td>')

            # parents column
            if self.showparents:
                of.write('<td class="field">')
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
                        of.write('%s, %s' % (father_name, mother_name))
                    elif mother:
                        of.write('%s' % mother_name)
                    elif father:
                        of.write('%s' % father_name)
                of.write('</td>')

            # finished writing all columns
            of.write('</tr>\n')
        of.write('<tbody>\n</table>\n')
        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PlaceListPage(BasePage):

    def __init__(self, db, title, place_handles, src_list, options, archive,
                 media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")
        of = self.create_file("places")
        self.display_header(of,db,_('Places'),
                            get_researcher().get_name())

        msg = _("This page contains an index of all the places in the "
                "database, sorted by their title. Clicking on a place's "
                "title will take you to that place's page.")

        of.write('<h3>%s</h3>\n' % _('Places'))
        of.write('<p>%s</p>\n' % msg )

        of.write('<table class="infolist">\n<thead><tr>\n')
        of.write('<th>%s</th>\n' % _('Letter'))
        of.write('<th>%s</th>\n' % _('Place'))
        of.write('</tr></thead>\n<tbody>\n')

        self.sort = Sort.Sort(db)
        handle_list = place_handles.keys()
        handle_list.sort(self.sort.by_place_title)
        last_letter = ''
        
        for handle in handle_list:
            place = db.get_place_from_handle(handle)
            n = ReportUtils.place_name(db, handle)

            if not n or len(n) == 0:
                continue
            
            letter = normalize('NFD', n)[0].upper()
            
            if letter != last_letter:
                last_letter = letter
                of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
                of.write('<tr><td class="category">%s</td>' % last_letter)
                of.write('<td class="data">')
                self.place_link(of,place.handle, n,place.gramps_id)
                of.write('</td></tr>')
            else:
                of.write('<tr><td class="category">&nbsp;</td>')
                of.write('<td class="data">')
                self.place_link(of,place.handle, n,place.gramps_id)
                of.write('</td></tr>')
            
        of.write('</tbody>\n</table>\n')
        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PlacePage(BasePage):

    def __init__(self, db, title, place_handle, src_list, place_list, options,
                 archive, media_list):
        place = db.get_place_from_handle( place_handle)
        BasePage.__init__(self, title, options, archive, media_list,
                          place.gramps_id)
        of = self.create_link_file(place.get_handle(),"plc")
        self.page_title = ReportUtils.place_name(db,place_handle)
        self.display_header(of,db,"%s - %s" % (_('Places'), self.page_title),
                            get_researcher().get_name(),up=True)

        media_list = place.get_media_list()
        self.display_first_image_as_thumbnail(of, db, media_list)

        of.write('<div id="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % self.page_title.strip())
        of.write('<table class="infolist">\n')

        if not self.noid:
            of.write('<tr><td class="field">%s</td>\n' % _('GRAMPS ID'))
            of.write('<td class="data">%s</td>\n' % place.gramps_id)
            of.write('</tr>\n')

        if place.main_loc:
            ml = place.main_loc
            for val in [(_('Street'),ml.street),
                        (_('City'),ml.city),
                        (_('Church Parish'),ml.parish),
                        (_('County'),ml.county),
                        (_('State/Province'),ml.state),
                        (_('Postal Code'),ml.postal),
                        (_('Country'),ml.country)]:
                if val[1]:
                    of.write('<tr><td class="field">%s</td>\n' % val[0])
                    of.write('<td class="data">%s</td>\n' % val[1])
                    of.write('</tr>\n')
                
        if place.long:
            of.write('<tr><td class="field">%s</td>\n' % _('Longitude'))
            of.write('<td class="data">%s</td>\n' % place.long)
            of.write('</tr>\n')

        if place.lat:
            of.write('<tr><td class="field">%s</td>\n' % _('Latitude'))
            of.write('<td class="data">%s</td>\n' % place.lat)
            of.write('</tr>\n')

        of.write('</table>\n')
        of.write('</div>\n')

        if self.use_gallery:
            self.display_additional_images_as_gallery(of, db, media_list)
        self.display_note_list(of, db, place.get_note_list())
        self.display_url_list(of, place.get_url_list())
        self.display_references(of,db,place_list[place.handle])
        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class MediaPage(BasePage):

    def __init__(self, db, title, handle, src_list, options, archive, media_list,
                 info):

        (prev, next, page_number, total_pages) = info
        photo = db.get_object_from_handle(handle)
        BasePage.__init__(self, title, options, archive, media_list,
                          photo.gramps_id)
        of = self.create_link_file(handle,"img")

        self.db = db
        self.src_list = src_list

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
        self.display_header(of,db, "%s - %s" % (_('Gallery'), title),
                            get_researcher().get_name(),up=True)

        of.write('<div id="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % self.page_title.strip())

        # gallery navigation
        of.write('<div class="img_navbar">')
        if prev:
            self.media_ref_link(of,prev,_('Previous'),True)
        data = _('%(page_number)d of %(total_pages)d' ) % {
            'page_number' : page_number, 'total_pages' : total_pages }
        of.write('&nbsp;&nbsp;%s&nbsp;&nbsp;' % data)
        if next:
            self.media_ref_link(of, next,_('Next'),True)

        of.write('</div>\n')

        if mime_type:
            if mime_type.startswith("image/"):
                of.write('<div class="centered">\n')
                if target_exists:
                    # if the image is spectacularly large, then force the client
                    # to resize it, and include a "<a href=" link to the actual
                    # image; most web browsers will dynamically resize an image
                    # and provide zoom-in/zoom-out functionality when the image
                    # is displayed directly
                    (width, height) = ImgManip.image_size(
                            Utils.media_path_full(self.db, photo.get_path()))
                    scale = 1.0
                    if width > _MAX_IMG_WIDTH or height > _MAX_IMG_HEIGHT:
                        # image is too large -- scale it down and link to the full image
                        scale = min(float(_MAX_IMG_WIDTH)/float(width), float(_MAX_IMG_HEIGHT)/float(height))
                        width = int(width * scale)
                        height = int(height * scale)
                        of.write('<a href="../../../%s">\n' % newpath)

                    of.write('<img width="%d" height="%d"' % (width, height))
                    of.write('src="../../../%s" alt="%s" />\n' % (newpath, self.page_title))

                    if scale <> 1.0:
                        of.write('</a>\n');

                else:
                    of.write('<br /><span>(%s)</span>' % _("The file has been moved or deleted"))
                of.write('</div>\n')
            else:
                import tempfile

                dirname = tempfile.mkdtemp()
                thmb_path = os.path.join(dirname,"temp.png")
                if ThumbNails.run_thumbnailer(mime_type, 
                                              Utils.media_path_full(self.db, 
                                                            photo.get_path()), 
                                              thmb_path, 320):
                    try:
                        path = "%s/%s.png" % (self.build_path(photo.handle,"preview"),photo.handle)
                        self.store_file(archive, self.html_dir, thmb_path, path)
                        os.unlink(thmb_path)
                    except IOError:
                        path = os.path.join('images','document.png')
                else:
                    path = os.path.join('images','document.png')
                os.rmdir(dirname)
                    
                of.write('<div class="centered">\n')
                if target_exists:
                    of.write('<a href="../../../%s" alt="%s" />\n' % (newpath, self.page_title))
                of.write('<img ')
                of.write('src="../../../%s" alt="%s" />\n' % (path, self.page_title))
                if target_exists:
                    of.write('</a>\n')
                else:
                    of.write('<br /><span>(%s)</span>' % _("The file has been moved or deleted"))
                of.write('</div>\n')
        else:
            path = os.path.join('images','document.png')
            of.write('<div class="centered">\n')
            of.write('<img ')
            of.write('src="../../../%s" alt="%s" />\n' % (path, self.page_title))
            of.write('</div>\n')

        of.write('<table class="infolist">\n')

        if not self.noid:
            of.write('<tr>\n')
            of.write('<td class="field">%s</td>\n' % _('GRAMPS ID'))
            of.write('<td class="data">%s</td>\n' % photo.gramps_id)
            of.write('</tr>\n')
        if not note_only and not mime_type.startswith("image/"):
            of.write('<tr>\n')
            of.write('<td class="field">%s</td>\n' % _('File type'))
            of.write('<td class="data">%s</td>\n' % Mime.get_description(mime_type))
            of.write('</tr>\n')
        date = _dd.display(photo.get_date_object())
        if date != "":
            of.write('<tr>\n')
            of.write('<td class="field">%s</td>\n' % _('Date'))
            of.write('<td class="data">%s</td>\n' % date)
            of.write('</tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

        self.display_note_list(of, db, photo.get_note_list())
        self.display_attr_list(of, photo.get_attribute_list())
        self.display_media_sources(of, db, photo)
        self.display_references(of,db,media_list)
        self.display_footer(of,db)
        self.close_file(of)

    def display_media_sources(self, of, db, photo):
        self.bibli = Bibliography()
        for sref in photo.get_source_references():
            self.bibli.add_reference(sref)
        self.display_source_refs(of, db, self.bibli)

    def display_attr_list(self, of,attrlist=None):
        if not attrlist:
            return
        of.write('<div id="attributes">\n')
        of.write('<h4>%s</h4>\n' % _('Attributes'))
        of.write('<table class="infolist">\n')

        for attr in attrlist:
            atType = str( attr.get_type() )
            of.write('<tr><td class="field">%s</td>' % atType)
            of.write('<td class="data">%s</td></tr>\n' % attr.get_value())
        of.write('</table>\n')
        of.write('</div>\n')

    def copy_source_file(self, handle,photo):
        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.build_path(handle,'images')
        newpath = to_dir + "/" + handle + ext

        fullpath = Utils.media_path_full(self.db, photo.get_path())
        try:
            if self.archive:
                self.archive.add(fullpath,str(newpath))
            else:
                to_dir = os.path.join(self.html_dir,to_dir)
                if not os.path.isdir(to_dir):
                    os.makedirs(to_dir)
                shutil.copyfile(fullpath,
                                os.path.join(self.html_dir, newpath))
            return newpath
        except (IOError,OSError),msg:
            error = _("Missing media object:") +                               \
                     "%s (%s)" % (photo.get_description(),photo.get_gramps_id())
            WarningDialog(error,str(msg))            
            return None

    def copy_thumbnail(self, handle,photo):
        to_dir = self.build_path(handle,'thumb')
        to_path = os.path.join(to_dir, handle+".png")
        if photo.get_mime_type():
            from_path = ThumbNails.get_thumbnail_path(Utils.media_path_full(
                                                            self.db, 
                                                            photo.get_path()),
                                                      photo.get_mime_type())
            if not os.path.isfile(from_path):
                from_path = os.path.join(const.IMAGE_DIR,"document.png")
        else:
            from_path = os.path.join(const.IMAGE_DIR,"document.png")
            
        if self.archive:
            self.archive.add(from_path,to_path)
        else:
            to_dir = os.path.join(self.html_dir,to_dir)
            dest = os.path.join(self.html_dir,to_path)
            if not os.path.isdir(to_dir):
                os.makedirs(to_dir)
            try:
                shutil.copyfile(from_path,dest)
            except IOError:
                print "Could not copy file"

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SurnameListPage(BasePage):
    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1
    def __init__(self, db, title, person_handle_list, options, archive,
                 media_list, order_by=ORDER_BY_NAME,filename="surnames"):
        
        BasePage.__init__(self, title, options, archive, media_list, "")
        if order_by == self.ORDER_BY_NAME:
            of = self.create_file(filename)
            self.display_header(of,db,_('Surnames'),get_researcher().get_name())
            of.write('<h3>%s</h3>\n' % _('Surnames'))
        else:
            of = self.create_file("surnames_count")
            self.display_header(of,db,_('Surnames by person count'),
                            get_researcher().get_name())
            of.write('<h3>%s</h3>\n' % _('Surnames by person count'))

        of.write('<p>%s</p>\n' % _(
            'This page contains an index of all the '
            'surnames in the database. Selecting a link '
            'will lead to a list of individuals in the '
            'database with this same surname.'))

        of.write('<table class="infolist">\n<thead><tr>\n')
        of.write('<th>%s</th>\n' % _('Letter'))

        if not self.use_home and not self.use_intro:
            of.write('<th><a href="%s%s">%s</a></th>\n' % ("index", self.ext, 
                                                            _('Surname')))
        else:
            of.write('<th><a href="%s%s">%s</a></th>\n' % ("surnames", 
                                                    self.ext, _('Surname')))

        of.write('<th><a href="%s%s">%s</a></th>\n' % ("surnames_count", self.ext, _('Number of people')))
        of.write('</tr></thead>\n<tbody>\n')

        person_handle_list = sort_people(db,person_handle_list)
        if order_by == self.ORDER_BY_COUNT:
            temp_list = {}
            for (surname,data_list) in person_handle_list:
                index_val = "%90d_%s" % (999999999-len(data_list),surname)
                temp_list[index_val] = (surname,data_list)
            temp_keys = temp_list.keys()
            temp_keys.sort()
            person_handle_list = []
            for key in temp_keys:
                person_handle_list.append(temp_list[key])
        
        last_letter = ''
        last_surname = ''
        
        for (surname,data_list) in person_handle_list:
            if len(surname) == 0:
                continue
            
            # Get a capital normalized version of the first letter of 
            # the surname
            letter = normalize('NFD',surname)[0].upper()
            
            if letter != last_letter:
                last_letter = letter
                of.write('<tr><td class="category">%s</td>' % last_letter)
                of.write('<td class="data">')
                self.surname_link(of,surname)
                of.write('</td>')
            elif surname != last_surname:
                of.write('<tr><td class="category">&nbsp;</td>')
                of.write('<td class="data">')
                self.surname_link(of,surname)
                of.write('</td>')
                last_surname = surname
            of.write('<td class="field">%d</td></tr>' % len(data_list))
            
        of.write('</tbody>\n</table>\n')
        self.display_footer(of,db)
        self.close_file(of)
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IntroductionPage(BasePage):

    def __init__(self, db, title, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")
        note_id = options['intronote']
        pic_id =  options['introimg']

        if self.use_home:
            of = self.create_file("introduction")
        else:
            of = self.create_file("index")
            
        author = get_researcher().get_name()
        self.display_header(of, db, _('Introduction'), author)

        of.write('<h3>%s</h3>\n' % _('Introduction'))

        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath, thumb_path) = self.copy_media(obj, False)
                    self.store_file(archive, self.html_dir, 
                                    Utils.media_path_full(db, 
                                                          obj.get_path()),
                                    newpath)
                    of.write('<div class="centered">\n')
                    of.write('<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</div>\n')
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))
        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get(markup=True)
            if note_obj.get_format():
                of.write('<pre>\n%s\n</pre>\n' % text)
            else:
                of.write('<p>')
                of.write('<br>'.join(text.split('\n')))
                of.write('</p>')

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HomePage(BasePage):

    def __init__(self, db, title, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        note_id = options['homenote']
        pic_id =  options['homeimg']
        of = self.create_file("index")
        author = get_researcher().get_name()
        self.display_header(of,db,_('Home'),author)

        of.write('<h3>%s</h3>\n' % _('Home'))

        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)

            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath,thumb_path) = self.copy_media(obj,False)
                    self.store_file(archive, self.html_dir,
                                    Utils.media_path_full(db, 
                                                          obj.get_path()),
                                    newpath)
                    of.write('<div class="centered">\n')
                    of.write('<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</div>\n')
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get(markup=True)
            if note_obj.get_format():
                of.write('<pre>\n%s\n</pre>\n' % text)
            else:
                of.write('<p>')
                of.write('</p><p>'.join(text.split('\n')))
                of.write('</p>')

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SourcesPage(BasePage):

    def __init__(self, db, title, handle_set, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_file("sources")
        author = get_researcher().get_name()
        self.display_header(of, db, _('Sources'), author)

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
                "database, sorted by their title. Clicking on a source's "
                "title will take you to that source's page.")

        of.write('<h3>%s</h3>\n<p>' % _('Sources'))
        of.write(msg)
        of.write('</p>\n<table class="infolist">\n')

        index = 1
        for key in keys:
            (source, handle) = source_dict[key]
            of.write('<tr><td class="category">%d.</td>\n' % index)
            of.write('<td class="data">')
            self.source_link(of, handle,source.get_title(),source.gramps_id)
            of.write('</td></tr>\n')
            index += 1
            
        of.write('</table>\n')

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SourcePage(BasePage):

    def __init__(self, db, title, handle, src_list, options, archive,
                 media_list):
        source = db.get_source_from_handle( handle)
        BasePage.__init__(self, title, options, archive, media_list,
                          source.gramps_id)
        of = self.create_link_file(source.get_handle(),"src")
        self.page_title = source.get_title()
        self.display_header(of,db,"%s - %s" % (_('Sources'), self.page_title),
                            get_researcher().get_name(),up=True)

        media_list = source.get_media_list()
        self.display_first_image_as_thumbnail(of, db, media_list)

        of.write('<div id="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % self.page_title.strip())
        of.write('<table class="infolist">')

        grampsid = None
        if not self.noid:
            grampsid = source.gramps_id

        for (label,val) in [(_('GRAMPS ID'),grampsid),
                            (_('Author'),source.author),
                            (_('Publication information'),source.pubinfo),
                            (_('Abbreviation'),source.abbrev)]:
            if val:
                of.write('\n<tr><td class="field">%s</td>' % label)
                of.write('<td class="data">%s</td>\n' % val)
                of.write('</tr>')

        of.write('</table></div>')

        self.display_additional_images_as_gallery(of, db, media_list)
        self.display_note_list(of, db, source.get_note_list())
        self.display_references(of,db,src_list[source.handle])
        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class GalleryPage(BasePage):

    def __init__(self, db, title, handle_set, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_file("gallery")
        self.display_header(of,db, _('Gallery'), get_researcher().get_name())

        of.write('<h3>%s</h3>\n<p>' % _('Gallery'))

        of.write(_("This page contains an index of all the media objects "
                   "in the database, sorted by their title. Clicking on "
                   "the title will take you to that media object's page."))
        of.write('</p>\n<table class="infolist">\n')

        self.db = db

        index = 1
        mlist = media_list.keys()
        sort = Sort.Sort(self.db)
        mlist.sort(sort.by_media_title)
        for handle in mlist:
            media = db.get_object_from_handle(handle)
            date = _dd.display(media.get_date_object())
            title = media.get_description()
            if title == "":
                title = "untitled"
            of.write('<tr>\n')
            
            of.write('<td class="category">%d.</td>\n' % index)
            
            of.write('<td class="data">')
            self.media_ref_link(of, handle,title)
            of.write('</td>\n')

            of.write('<td class="data">%s</td>\n' % date)

            of.write('</tr>\n')
            index += 1
            
        of.write('</table>\n')

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DownloadPage(BasePage):

    def __init__(self, db, title, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_file("download")
        self.display_header(of,db,_('Download'),
                            get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Download'))

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ContactPage(BasePage):

    def __init__(self, db, title, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        of = self.create_file("contact")
        self.display_header(of,db,_('Contact'),
                            get_researcher().get_name())

        of.write('<div id="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % _('Contact'))

        note_id = options['contactnote']
        pic_id = options['contactimg']
        if pic_id:
            obj = db.get_object_from_gramps_id(pic_id)
            mime_type = obj.get_mime_type()
        
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath, thumb_path) = self.copy_media(obj, False)
                    self.store_file(archive, self.html_dir, 
                                    Utils.media_path_full(db, 
                                                          obj.get_path()),
                                    newpath)

                    of.write('<div class="rightwrap">\n')
                    of.write('<table><tr>')
                    of.write('<td height="205">')
                    of.write('<img height="200" ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</td></tr></table>\n')
                    of.write('</div>\n')
                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        r = get_researcher()

        of.write('<div id="researcher">\n')
        if r.name:
            of.write('%s<br />\n' % r.name.replace(',,,',''))
        if r.addr:
            of.write('%s<br />\n' % r.addr)

        text = "".join([r.city,r.state,r.postal])
        if text:
            of.write('%s<br />\n' % text)
        if r.country:
            of.write('%s<br />\n' % r.country)
        if r.email:
            of.write('%s<br />\n' % r.email)
        of.write('</div>\n')
        of.write('<div class="fullclear"></div>\n')

        if note_id:
            note_obj = db.get_note_from_gramps_id(note_id)
            text = note_obj.get(markup=True)
            if note_obj.get_format():
                text = u"<pre>%s</pre>" % text
            else:
                text = u"<br>".join(text.split("\n"))
            of.write('<p>%s</p>\n' % text)

        of.write('</div>\n')

        self.display_footer(of,db)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage(BasePage):

    gender_map = {
        gen.lib.Person.MALE    : _('male'),
        gen.lib.Person.FEMALE  : _('female'),
        gen.lib.Person.UNKNOWN : _('unknown'),
        }
    
    def __init__(self, db, person, title, ind_list,
                 place_list, src_list, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list,
                          person.gramps_id)
        self.person = person
        self.db = db
        self.ind_list = ind_list
        self.src_list = src_list
        self.bibli = Bibliography()
        self.place_list = place_list
        self.sort_name = _nd.sorted(self.person)
        self.name = _nd.sorted(self.person)
        
        of = self.create_link_file(person.handle,"ppl")
        self.display_header(of,db, self.sort_name,
                            get_researcher().get_name(),up=True)
        self.display_ind_general(of)
        self.display_ind_events(of)
        self.display_attr_list(of, self.person.get_attribute_list())
        self.display_ind_parents(of)
        self.display_ind_relationships(of)
        self.display_addresses(of)

        media_list = []
        photolist = self.person.get_media_list()
        if len(photolist) > 1:
            media_list = photolist[1:]
        for handle in self.person.get_family_handle_list():
            family = self.db.get_family_from_handle(handle)
            media_list += family.get_media_list()
            for evt_ref in family.get_event_ref_list():
                event = self.db.get_event_from_handle(evt_ref.ref)
                media_list += event.get_media_list()
        for evt_ref in self.person.get_primary_event_ref_list():
            event = self.db.get_event_from_handle(evt_ref.ref)
            if event:
                media_list += event.get_media_list()
                
        self.display_additional_images_as_gallery(of, db, media_list)
        self.display_note_list(of, db, self.person.get_note_list())
        self.display_url_list(of, self.person.get_url_list())
        self.display_ind_sources(of)
        self.display_ind_pedigree(of)
        if self.usegraph:
            self.display_tree(of)
        self.display_footer(of,db)
        self.close_file(of)

    def display_attr_list(self, of,attrlist=None):
        if not attrlist:
            return
        of.write('<div id="attributes">\n')
        of.write('<h4>%s</h4>\n' % _('Attributes'))
        of.write('<table class="infolist">\n')

        for attr in attrlist:
            atType = str( attr.get_type() )
            of.write('<tr><td class="field">%s</td>' % atType)
            value = attr.get_value()
            value += self.get_citation_links( attr.get_source_references() )
            of.write('<td class="data">%s</td></tr>\n' % value)
        of.write('</table>\n')
        of.write('</div>\n')

    def draw_box(self, of,center,col,person):
        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)
        
        of.write('<div class="boxbg" style="top: %dpx; left: %dpx;">\n' % (top,xoff+1))
        of.write('<table><tr><td class="box">')
        person_link = person.handle in self.ind_list
        if person_link:
            person_name = _nd.display(person)
            path = self.build_path(person.handle,"ppl",False)
            fname = self.build_name(path,person.handle)
            self.person_link(of, fname, person_name)
        else:
            of.write(_nd.display(person))
        of.write('</td></tr></table>\n')
        of.write('</div>\n')
        of.write('<div class="shadow" style="top: %dpx; left: %dpx;"></div>\n' % (top+_SHADOW,xoff+_SHADOW))
        of.write('<div class="border" style="top: %dpx; left: %dpx;"></div>\n' % (top-1, xoff))

    def extend_line(self, of,y0,x0):
        of.write('<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y0,x0,_HGAP/2))
        of.write('<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' % 
                 (y0+_SHADOW,x0,_HGAP/2+_SHADOW))

    def connect_line(self, of,y0,y1,col):
        if y0 < y1:
            y = y0
        else:
            y = y1
            
        x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        of.write('<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1,x0,_HGAP/2))
        of.write('<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1+_SHADOW,x0+_SHADOW,_HGAP/2+_SHADOW))
        of.write('<div class="bhline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y,x0,abs(y0-y1)))
        of.write('<div class="ghline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y+_SHADOW,x0+_SHADOW,abs(y0-y1)))

    def draw_connected_box(self, of,center1,center2,col, handle):
        if not handle:
            return None
        person = self.db.get_person_from_handle(handle)
        self.draw_box(of,center2,col,person)
        self.connect_line(of,center1,center2,col)
        return person
    
    def display_tree(self, of):
        if not self.person.get_main_parents_family_handle():
            return
        
        of.write('<div id="tree">\n')
        of.write('<h4>%s</h4>\n' % _('Ancestors'))
        of.write('<div style="position: relative;">\n')

        generations = self.graphgens
        
        max_in_col = 1 <<(generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)
        self.draw_tree(of,1,generations,max_size,0,center,self.person.handle)

        of.write('</div>\n')
        of.write('</div>\n')
        of.write('<table style="height: %dpx; width: %dpx;"><tr><td></td></tr></table>\n' %
                 (max_size,_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP))
    
    def draw_tree(self, of,gen,maxgen,max_size, old_center, new_center,phandle):
        if gen > maxgen:
            return
        gen_offset = int(max_size / pow(2,gen+1))
        person = self.db.get_person_from_handle(phandle)
        if not person:
            return

        if gen == 1:
            self.draw_box(of, new_center,0,person)
        else:
            self.draw_connected_box(of, old_center, new_center,gen-1,phandle)
        
        if gen == maxgen:
            return

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + (gen)*_WIDTH + (gen-1)*_HGAP
            self.extend_line(of, new_center,line_offset)

            gen = gen + 1
            family = self.db.get_family_from_handle(family_handle)
            
            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            self.draw_tree(of,gen,maxgen,max_size, new_center,f_center,f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            self.draw_tree(of,gen,maxgen,max_size, new_center,m_center,m_handle)

    def display_ind_sources(self, of):
        for sref in self.person.get_source_references():
            self.bibli.add_reference(sref)
        if self.bibli.get_citation_count() == 0:
            return
        self.display_source_refs(of, self.db, self.bibli)

    def display_ind_pedigree(self, of):

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = self.db.get_family_from_handle(parent_handle)
            father_id = family.get_father_handle()
            mother_id = family.get_mother_handle()
            mother = self.db.get_person_from_handle(mother_id)
            father = self.db.get_person_from_handle(father_id)
        else:
            family = None
            father = None
            mother = None
        
        of.write('<div id="pedigree">\n')
        of.write('<h4>%s</h4>\n' % _('Pedigree'))
        of.write('<div class="pedigreebox">\n')
        if father or mother:
            of.write('<div class="pedigreegen">\n')
            if father:
                self.pedigree_person(of,father)
            if mother:
                self.pedigree_person(of,mother,True)
        of.write('<div class="pedigreegen">\n')
        if family:
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                if child_handle == self.person.handle:
                    of.write('<span class="thisperson">%s</span><br />\n' % self.name)
                    self.pedigree_family(of)
                else:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(of,child)
        else:
            of.write('<span class="thisperson">%s</span><br />\n' % self.name)
            self.pedigree_family(of)

        of.write('</div>\n')
        if father or mother:
            of.write('</div>\n')
        of.write('</div>\n</div>\n')

    def display_ind_general(self, of):
        self.page_title = self.sort_name
        self.display_first_image_as_thumbnail(of, self.db,
                                              self.person.get_media_list())

        of.write('<div id="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % self.sort_name.strip())
            
        of.write('<table class="infolist">\n')

        # GRAMPS ID
        if not self.noid:
            of.write('<tr><td class="field">%s</td>\n' % _('GRAMPS ID'))
            of.write('<td class="data">%s</td>\n' % self.person.gramps_id)
            of.write('</tr>\n')

        # Names [and their sources]
        for name in [self.person.get_primary_name(),]+self.person.get_alternate_names():
            pname = _nd.display_name(name)
            pname += self.get_citation_links( name.get_source_references() )
            type = str( name.get_type() )
            of.write('<tr><td class="field">%s</td>\n' % _(type))
            of.write('<td class="data">%s' % pname)
            of.write('</td>\n</tr>\n')

        # Gender
        nick = self.person.get_nick_name()
        if nick:
            of.write('<tr><td class="field">%s</td>\n' % _('Nickname'))
            of.write('<td class="data">%s</td>\n' % nick)
            of.write('</tr>\n')

        # Gender
        of.write('<tr><td class="field">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        of.write('<td class="data">%s</td>\n' % gender)
        of.write('</tr>\n</table>\n</div>\n')

    def display_ind_events(self, of):
        evt_ref_list = self.person.get_event_ref_list()
        
        if not evt_ref_list:
            return
        
        of.write('<div id="events">\n')
        of.write('<h4>%s</h4>\n' % _('Events'))
        of.write('<table class="infolist">\n')

        for event_ref in evt_ref_list:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                evt_name = str(event.get_type())

                if event_ref.get_role() == EventRoleType.PRIMARY:
                    of.write('<tr><td class="field">%s</td>\n' % evt_name)
                else:
                    of.write('<tr><td class="field">%s (%s)</td>\n' \
                        % (evt_name, event_ref.get_role()))

                of.write('<td class="data">\n')
                of.write(self.format_event(event, event_ref))
                of.write('</td>\n')
                of.write('</tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')
        
    def display_addresses(self, of):        
        alist = self.person.get_address_list()

        if len(alist) == 0:
            return
        
        of.write('<div id="addresses">\n')
        of.write('<h4>%s</h4>\n' % _('Addresses'))
        of.write('<table class="infolist">\n')
        
        for addr in alist:
            location = ReportUtils.get_address_str(addr)
            location += self.get_citation_links( addr.get_source_references() )
            date = _dd.display(addr.get_date_object())

            of.write('<tr><td class="field">%s</td>\n' % date)
            of.write('<td class="data">%s</td>\n' % location)
            of.write('</tr>\n')

        of.write('</table>\n')
        of.write('</div>\n')

    def display_child_link(self, of, child_handle):
        use_link = child_handle in self.ind_list
        child = self.db.get_person_from_handle(child_handle)
        gid = child.get_gramps_id()
        if use_link:
            child_name = _nd.display(child)
            path = self.build_path(child_handle,"ppl",False)
            self.person_link(of, self.build_name(path,child_handle),
                             child_name, gid)
        else:
            of.write(_nd.display(child))
        of.write(u"<br />\n")

    def display_parent(self, of, handle, title, rel):
        use_link = handle in self.ind_list 
        person = self.db.get_person_from_handle(handle)
        of.write('<td class="field">%s</td>\n' % title)
        of.write('<td class="data">')
        val = person.gramps_id
        if use_link:
            path = self.build_path(handle,"ppl",False)
            fname = self.build_name(path, handle)
            self.person_link(of, fname, _nd.display(person),
                             val)
        else:
            of.write(_nd.display(person))
        if rel != gen.lib.ChildRefType.BIRTH:
            of.write('&nbsp;&nbsp;&nbsp;(%s)' % str(rel))
        of.write('</td>\n')

    def display_ind_parents(self, of):
        parent_list = self.person.get_parent_family_handle_list()

        if not parent_list:
            return
        
        of.write('<div id="parents">\n')
        of.write('<h4>%s</h4>\n' % _("Parents"))
        of.write('<table class="infolist">\n')

        first = True
        if parent_list:
            for family_handle in parent_list:
                family = self.db.get_family_from_handle(family_handle)
                
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
                    of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
                else:
                    first = False

                father_handle = family.get_father_handle()
                if father_handle:
                    of.write('<tr>\n')
                    self.display_parent(of,father_handle,_('Father'),frel)
                    of.write('</tr>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    of.write('<tr>\n')
                    self.display_parent(of,mother_handle,_('Mother'),mrel)
                    of.write('</tr>\n')

                first = False
                if len(child_ref_list) > 1:
                    of.write('<tr>\n')
                    of.write('<td class="field">%s</td>\n' % _("Siblings"))
                    of.write('<td class="data">\n')
                    for child_ref in child_ref_list:
                        child_handle = child_ref.ref
                        sibling.add(child_handle)   # remember that we've already "seen" this child
                        if child_handle != self.person.handle:
                            self.display_child_link(of,child_handle)
                    of.write('</td>\n</tr>\n')

                # Also try to identify half-siblings
                other_siblings = set()

                # if we have a known father...
                if father_handle and self.showhalfsiblings:
                    # 1) get all of the families in which this father is involved
                    # 2) get all of the children from those families
                    # 3) if the children are not already listed as siblings...
                    # 4) then remember those children since we're going to list them
                    father = self.db.get_person_from_handle(father_handle)
                    for family_handle in father.get_family_handle_list():
                        family = self.db.get_family_from_handle(family_handle)
                        for step_child_ref in family.get_child_ref_list():
                            step_child_handle = step_child_ref.ref
                            if step_child_handle not in sibling:
                                if step_child_handle != self.person.handle:
                                    # we have a new step/half sibling
                                    other_siblings.add(step_child_ref.ref)

                # do the same thing with the mother (see "father" just above):
                if mother_handle and self.showhalfsiblings:
                    mother = self.db.get_person_from_handle(mother_handle)
                    for family_handle in mother.get_family_handle_list():
                        family = self.db.get_family_from_handle(family_handle)
                        for step_child_ref in family.get_child_ref_list():
                            step_child_handle = step_child_ref.ref
                            if step_child_handle not in sibling:
                                if step_child_handle != self.person.handle:
                                    # we have a new step/half sibling
                                    other_siblings.add(step_child_ref.ref)

                # now that we have all of the step-siblings/half-siblings, print them out
                if len(other_siblings) > 0:
                    of.write('<tr>\n')
                    of.write('<td class="field">%s</td>\n' % _("Half Siblings"))
                    of.write('<td class="data">\n')
                    for child_handle in other_siblings:
                        self.display_child_link(of, child_handle)
                    of.write('</td>\n</tr>\n')

            of.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

    def display_ind_relationships(self, of):
        family_list = self.person.get_family_handle_list()
        if not family_list:
            return
        
        of.write('<div id="families">\n')
        of.write('<h4>%s</h4>\n' % _("Families"))
        of.write('<table class="infolist">\n')

        first = True
        for family_handle in family_list:
            family = self.db.get_family_from_handle(family_handle)
            self.display_spouse(of,family,first)
            first = False
            childlist = family.get_child_ref_list()
            if childlist:
                of.write('<tr><td>&nbsp;</td>\n')
                of.write('<td class="field">%s</td>\n' % _("Children"))
                of.write('<td class="data">\n')
                for child_ref in childlist:
                    self.display_child_link(of,child_ref.ref)
                of.write('</td>\n</tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

    def display_spouse(self, of,family,first=True):
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

        spouse_id = ReportUtils.find_spouse(self.person,family)
        if spouse_id:
            spouse = self.db.get_person_from_handle(spouse_id)
            name = _nd.display(spouse)
        else:
            name = _("unknown")
        if not first:
            of.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
        rtype = str(family.get_relationship())
        of.write('<tr><td class="category">%s</td>\n' % rtype)
        of.write('<td class="field">%s</td>\n' % relstr)
        of.write('<td class="data">')
        if spouse_id:
            use_link = spouse_id in self.ind_list
            gid = spouse.get_gramps_id()
            if use_link:
                spouse_name = _nd.display(spouse)
                path = self.build_path(spouse.handle,"ppl",False)
                fname = self.build_name(path,spouse.handle)
                self.person_link(of, fname, spouse_name, gid)
            else:
                of.write(name)
        of.write('</td>\n</tr>\n')
        
        for event_ref in family.get_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            evtType = str(event.get_type())
            of.write('<tr><td>&nbsp;</td>\n')
            of.write('<td class="field">%s</td>\n' % evtType)
            of.write('<td class="data">\n')
            of.write(self.format_event(event, event_ref))
            of.write('</td>\n</tr>\n')
        for attr in family.get_attribute_list():
            attrType = str(attr.get_type())
            of.write('<tr><td>&nbsp;</td>\n')
            of.write('<td class="field">%s</td>' % attrType)
            of.write('<td class="data">%s</td>\n</tr>\n' % attr.get_value())
        notelist = family.get_note_list()
        for notehandle in notelist:
            nobj = self.db.get_note_from_handle(notehandle)
            if nobj:
                text = nobj.get(markup=True)
                format = nobj.get_format()
                if text:
                    of.write('<tr><td>&nbsp;</td>\n')
                    of.write('<td class="field">%s</td>\n' % _('Narrative'))
                    of.write('<td class="note">\n')
                    if format:
                        of.write( u"<pre>%s</pre>" % text )
                    else:
                        of.write( u"<br>".join(text.split("\n")))
                    of.write('</td>\n</tr>\n')
            
    def pedigree_person(self, of,person,is_spouse=False):
        person_link = person.handle in self.ind_list
        if is_spouse:
            of.write('<span class="spouse">')
        if person_link:
            person_name = _nd.display(person)
            path = self.build_path(person.handle,"ppl",False)
            fname = self.build_name(path,person.handle)
            self.person_link(of, fname, person_name)
        else:
            of.write(_nd.display(person))
        if is_spouse:
            of.write('</span>')
        of.write('<br />\n')

    def pedigree_family(self, of):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                self.pedigree_person(of,spouse,True)
            childlist = rel_family.get_child_ref_list()
            if childlist:
                of.write('<div class="pedigreegen">\n')
                for child_ref in childlist:
                    child = self.db.get_person_from_handle(child_ref.ref)
                    self.pedigree_person(of,child)
                of.write('</div>\n')

    def format_event(self,event,event_ref):
        lnk = (self.cur_name, self.page_title, self.gid)
        descr = event.get_description()
        place_handle = event.get_place_handle()
        if place_handle:
            if self.place_list.has_key(place_handle):
                if lnk not in self.place_list[place_handle]:
                    self.place_list[place_handle].append(lnk)
            else:
                self.place_list[place_handle] = [lnk]
                
            place = self.place_link_str(place_handle,
                                        ReportUtils.place_name(self.db,place_handle),
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
            text += _("<br>%(type)s: %(value)s") % {
                'type'     : attr.get_type(),
                'value'    : attr.get_value() }

        # if the event or event reference has a note attached to it,
        # get the text and format it correctly
        notelist = event.get_note_list()
        notelist.extend(event_ref.get_note_list())
        for notehandle in notelist:
            nobj = self.db.get_note_from_handle(notehandle)
            if nobj:
                note_text = nobj.get(markup=True)
                format = nobj.get_format()
                if note_text:
                    if format:
                        text += u"<pre>%s</pre>" % note_text
                    else:
                        text += u"<p>"
                        text += u"<br>".join(note_text.split("\n"))
                        text += u"</p>"
        return text
    
    def get_citation_links(self, source_ref_list):
        gid_list = []
        lnk = (self.cur_name, self.page_title, self.gid)
        text = ""

        for sref in source_ref_list:
            handle = sref.get_reference_handle()
            source = self.db.get_source_from_handle(handle)
            gid_list.append(sref)

            if self.src_list.has_key(handle):
                if lnk not in self.src_list[handle]:
                    self.src_list[handle].append(lnk)
            else:
                self.src_list[handle] = [lnk]
            
        if len(gid_list) > 0:
            text = text + " <sup>"
            for ref in gid_list:
                index,key = self.bibli.add_reference(ref)
                id = "%d%s" % (index+1,key)
                text = text + ' <a href="#sref%s">%s</a>' % (id,id)
            text = text + "</sup>"

        return text
            
#------------------------------------------------------------------------
#
# NavWebReport
#
#------------------------------------------------------------------------
class NavWebReport(Report):
    def __init__(self, database, options):
        """
        Create WebReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options         - instance of the Options class for this report
        """
        Report.__init__(self, database, options)
        menu = options.menu
        self.opts = {}

        for optname in menu.get_all_option_names():
            menuopt = menu.get_option_by_name(optname)
            self.opts[optname] = menuopt.get_value()

        if not self.opts['incpriv']:
            self.database = PrivateProxyDb(database)
        else:
            self.database = database
            
        livinginfo = self.opts['living']
        yearsafterdeath = self.opts['yearsafterdeath']
        
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

        self.target_path = self.opts['target']
        self.copyright = self.opts['cright']
        self.ext = self.opts['ext']
        self.encoding = self.opts['encoding']
        self.css = self.opts['css']
        self.noid = self.opts['nogid']
        self.linkhome = self.opts['linkhome']
        self.showbirth = self.opts['showbirth']
        self.showdeath = self.opts['showdeath']
        self.showspouse = self.opts['showspouse']
        self.showparents = self.opts['showparents']
        self.showhalfsiblings = self.opts['showhalfsiblings']
        self.title = self.opts['title']
        self.sort = Sort.Sort(self.database)
        self.inc_gallery = self.opts['gallery']
        self.inc_contact = self.opts['contactnote'] != u""\
                       or self.opts['contactimg'] != u""
        self.inc_download = self.opts['incdownload']
        self.use_archive = self.opts['archive']
        self.use_intro = self.opts['intronote'] != u""\
                    or self.opts['introimg'] != u""
        self.use_home = self.opts['homenote'] != u"" or\
                        self.opts['homeimg'] != u""
        
    def write_report(self):
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name == None:
                dir_name = os.getcwd()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    ErrorDialog(_("Neither %s nor %s are directories") % \
                                (dir_name,parent_dir))
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
            archive = None
        else:
            if os.path.isdir(self.target_path):
                ErrorDialog(_('Invalid file name'),
                            _('The archive file must be a file, not a directory'))
                return
            try:
                archive = tarfile.open(self.target_path,"w:gz")
            except (OSError,IOError),value:
                ErrorDialog(_("Could not create %s") % self.target_path,
                            value)
                return

        self.progress = Utils.ProgressMeter(_("Generate HTML Reports"),'')

        # Build the person list
        ind_list = self.build_person_list()

        # Generate the CSS file if requested
        if self.css != '':
            self.write_css(archive,self.target_path,self.css)

        # Copy the Creative Commons icon if the a Creative Commons
        # license is requested
        if 0 < self.copyright < 7:
            from_path = os.path.join(const.IMAGE_DIR,"somerights20.gif")
            to_path = os.path.join("images","somerights20.gif")
            self.store_file(archive,self.target_path,from_path,to_path)

        from_path = os.path.join(const.IMAGE_DIR,"document.png")
        to_path = os.path.join("images","document.png")
        self.store_file(archive,self.target_path,from_path,to_path)

        place_list = {}
        source_list = {}
        self.photo_list = {}

        self.base_pages(self.photo_list, archive)
        self.person_pages(ind_list, place_list, source_list, archive)
        self.surname_pages(ind_list, archive)
        self.place_pages(place_list, source_list, archive)
        if self.inc_gallery:
            self.gallery_pages(self.photo_list, source_list, archive)
        self.source_pages(source_list, self.photo_list, archive)
        
        if archive:
            archive.close()
        self.progress.close()

    def build_person_list(self):
        """
        Builds the person list. Gets all the handles from the database
        and then applies the cosen filter:
        """

        # gets the person list and applies the requested filter
        ind_list = self.database.get_person_handles(sort_handles=False)
        self.progress.set_pass(_('Filtering'),1)
        ind_list = self.filter.apply(self.database,ind_list)
        return ind_list

    def write_css(self,archive, html_dir,css_file):
        """
        Copy the CSS file to the destination.
        """
        if archive:
            fname = os.path.join(const.DATA_DIR, css_file)
            archive.add(fname,_NARRATIVE)
        else:
            shutil.copyfile(os.path.join(const.DATA_DIR, css_file),
                            os.path.join(html_dir,_NARRATIVE))

    def person_pages(self, ind_list, place_list, source_list, archive):

        self.progress.set_pass(_('Creating individual pages'),len(ind_list) + 1)
        self.progress.step()    # otherwise the progress indicator sits at 100%
                                # for a short while from the last step we did,
                                # which was to apply the privacy filter

        IndividualListPage(
            self.database, self.title, ind_list, 
            self.opts, archive, self.photo_list)

        for person_handle in ind_list:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)

            IndividualPage(
                self.database, person, self.title, ind_list,
                place_list, source_list, self.opts, archive, self.photo_list)
            
    def surname_pages(self, ind_list, archive):
        """
        Generates the surname related pages from list of individual
        people.
        """
        
        local_list = sort_people(self.database,ind_list)
        self.progress.set_pass(_("Creating surname pages"),len(local_list))

        if self.use_home or self.use_intro:
            defname="surnames"
        else:
            defname="index"

        SurnameListPage(
            self.database, self.title, ind_list, self.opts, archive,
            self.photo_list, SurnameListPage.ORDER_BY_NAME,defname)
        
        SurnameListPage(
            self.database, self.title, ind_list, self.opts, archive,
            self.photo_list, SurnameListPage.ORDER_BY_COUNT,"surnames_count")

        for (surname, handle_list) in local_list:
            SurnamePage(self.database, surname, handle_list,
                        self.opts, archive, self.photo_list)
            self.progress.step()
        
    def source_pages(self, source_list, photo_list, archive):
        
        self.progress.set_pass(_("Creating source pages"),len(source_list))

        SourcesPage(self.database,self.title, source_list.keys(),
                    self.opts, archive, photo_list)

        for key in list(source_list):
            SourcePage(self.database, self.title, key, source_list,
                       self.opts, archive, photo_list)
            self.progress.step()
        

    def place_pages(self, place_list, source_list, archive):

        self.progress.set_pass(_("Creating place pages"),len(place_list))

        PlaceListPage(
            self.database, self.title, place_list, source_list, self.opts,
            archive, self.photo_list)

        for place in place_list.keys():
            PlacePage(
                self.database, self.title, place, source_list, place_list,
                self.opts, archive, self.photo_list)
            self.progress.step()

    def gallery_pages(self, photo_list, source_list, archive):
        import gc
        self.progress.set_pass(_("Creating media pages"),len(photo_list))

        GalleryPage(self.database, self.title, source_list,
                    self.opts, archive, self.photo_list)

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
            MediaPage(self.database, self.title, photo_handle, source_list,
                      self.opts, archive, self.photo_list[photo_handle],
                      (prev, next, index, total))
            self.progress.step()
            prev = photo_handle
            index += 1

    def base_pages(self, photo_list, archive):

        if self.use_home:
            HomePage(self.database, self.title, self.opts, archive, photo_list)

        if self.inc_contact:
            ContactPage(self.database, self.title, self.opts, 
                        archive, photo_list)
            
        if self.inc_download:
            DownloadPage(self.database, self.title, self.opts, 
                         archive, photo_list)
        
        if self.use_intro:
            IntroductionPage(self.database, self.title, self.opts,
                             archive, photo_list)

    def store_file(self,archive, html_dir,from_path,to_path):
        """
        Store the file in the destination.
        """
        if archive:
            archive.add(from_path,to_path)
        else:
            shutil.copyfile(from_path, os.path.join(html_dir,to_path))

#------------------------------------------------------------------------
#
# NavWebOptions
#
#------------------------------------------------------------------------
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
                                    os.path.join(const.USER_HOME,"NAVWEB"))
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
        
        encoding = EnumeratedListOption(_('Character set encoding'), 'utf-8' )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)
        
        css = EnumeratedListOption(_('Stylesheet'), 'main1.css' )
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


def sort_people(db, handle_list):
    flist = set(handle_list)

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
        slist = map(lambda x: (sortnames[x],x),sname_sub[name])
        slist.sort(lambda x,y: locale.strcoll(x[0],y[0]))
        entries = map(lambda x: x[1], slist)
        sorted_lists.append((name,entries))
    return sorted_lists

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'navwebpage',
    category = CATEGORY_WEB,
    report_class = NavWebReport,
    options_class = NavWebOptions,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Narrated Web Site..."),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Generates web (HTML) pages for individuals, or a set of "
                    "individuals."),
    )
