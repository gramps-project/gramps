#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gettext import gettext as _
from cStringIO import StringIO
from textwrap import TextWrapper

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WebPage")

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import RelLib
import const
from GrampsCfg import get_researcher
from Filters import GenericFilter, Rules
import Sort
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_WEB, MODE_GUI, MODE_CLI
from ReportBase._ReportDialog import ReportDialog
from ReportBase._CommandLineReport import CommandLineReport
import Errors
import Utils
import ImgManip
import GrampsLocale
from QuestionDialog import ErrorDialog, WarningDialog
from NameDisplay import displayer as _nd
from DateHandler import displayer as _dd

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_NARRATIVE = "narrative.css"
_NAME_COL  = 3

WIDTH=160
HEIGHT=50
VGAP=10
HGAP=30
SHADOW=5
XOFFSET=5

_css_files = [
    [_("Modern"),         'main1.css'],
    [_("Business"),       'main2.css'],
    [_("Certificate"),    'main3.css'],
    [_("Antique"),        'main4.css'],
    [_("Tranquil"),       'main5.css'],
    [_("Sharp"),          'main6.css'],
    [_("No style sheet"), ''],
    ]

_character_sets = [
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

_cc = [
    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/"><img alt="Creative Commons License - By attribution" title="Creative Commons License - By attribution" src="#PATH#images/somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/"><img alt="Creative Commons License - By attribution, No derivations" title="Creative Commons License - By attribution, No derivations" src="#PATH#images/somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/"><img alt="Creative Commons License - By attribution, Share-alike" title="Creative Commons License - By attribution, Share-alike" src="#PATH#images/somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/"><img alt="Creative Commons License - By attribution, Non-commercial" title="Creative Commons License - By attribution, Non-commercial" src="#PATH#images/somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/"><img alt="Creative Commons License - By attribution, Non-commercial, No derivations" title="Creative Commons License - By attribution, Non-commercial, No derivations" src="#PATH#images/somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/"><img alt="Creative Commons License - By attribution, Non-commerical, Share-alike" title="Creative Commons License - By attribution, Non-commerical, Share-alike" src="#PATH#images/somerights20.gif" /></a>',
    ]

wrapper = TextWrapper()
wrapper.break_log_words = True
wrapper.width = 20

class BasePage:
    def __init__(self, title, options, archive, photo_list, gid):
        self.title_str = title
        self.gid = gid
        self.inc_download = options.handler.options_dict['NWEBdownload']
        self.html_dir = options.handler.options_dict['NWEBod']
        self.copyright = options.handler.options_dict['NWEBcopyright']
        self.options = options
        self.archive = archive
        self.ext = options.handler.options_dict['NWEBext']
        self.encoding = options.handler.options_dict['NWEBencoding']
        self.css = options.handler.options_dict['NWEBcss']
        self.noid = options.handler.options_dict['NWEBnoid']
        self.use_intro = options.handler.options_dict['NWEBintronote'] != u""
        self.use_contact = options.handler.options_dict['NWEBcontact'] != u""
        self.use_gallery = options.handler.options_dict['NWEBgallery']
        self.header = options.handler.options_dict['NWEBheader']
        self.footer = options.handler.options_dict['NWEBfooter']
        self.photo_list = photo_list
        self.exclude_private = not options.handler.options_dict['NWEBincpriv']
        self.usegraph = options.handler.options_dict['NWEBgraph']
        self.graphgens = options.handler.options_dict['NWEBgraphgens']
        self.use_home = self.options.handler.options_dict['NWEBhomenote'] != ""
        self.page_title = ""
	self.warn_dir = True

    def store_file(self,archive,html_dir,from_path,to_path):
        if archive:
            archive.add(from_path,to_path)
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
        real_path = "%s/%s" % (self.build_path(handle,'images'),handle+ext)
        thumb_path = "%s/%s.png" % (self.build_path(handle,'thumb'),handle)
        return (real_path,thumb_path)

    def create_file(self,name):
        self.cur_name = self.build_name("",name)
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io,'utf-8',self.encoding,
                                    'xmlcharrefreplace')
        else:
            page_name = os.path.join(self.html_dir,self.cur_name)
            of = codecs.EncodedFile(open(page_name, "w"),'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        return of

    def link_path(self,name,path):
        base = self.build_name("",name)
        path = os.path.join(path,name[0],name[1],base)
        if os.sys.platform == "win32":
            path = path.lower()
        return path

    def create_link_file(self,name,path):
        self.cur_name = self.link_path(name,path)
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io,'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        else:
            dirname = os.path.join(self.html_dir,path,name[0],name[1])
            if os.sys.platform == "win32":
                dirname = dirname.lower()
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            page_name = self.build_name(dirname,name)
            of = codecs.EncodedFile(open(page_name, "w"),'utf-8',
                                    self.encoding,'xmlcharrefreplace')
        return of

    def close_file(self,of):
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

    def display_footer(self,of,db):

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
            text = _cc[self.copyright-1]
            if self.up:
                text = text.replace('#PATH#','../../../')
            else:
                text = text.replace('#PATH#','')
            of.write(text)
            of.write('</div>\n')
        of.write('<div class="fullclear"></div>\n')
        of.write('</div>\n')
        if self.footer:
            obj = db.get_object_from_handle(self.footer)
            if obj:
                of.write('<div class="user_footer">\n')
                of.write(obj.get_note())
                of.write('</div>\n')
        of.write('</body>\n')
        of.write('</html>\n')
    
    def display_header(self,of,db,title,author="",up=False):
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
            obj = db.get_object_from_handle(self.header)
            if obj:
                of.write('  <div class="user_header">\n')
                of.write(obj.get_note())
                of.write('  </div>\n')
        of.write('<div id="navheader">\n')

        value = unicode(time.strftime('%x',time.localtime(time.time())),
                        GrampsLocale.codeset)

        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % { 'date' : value }

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

    def show_link(self,of,lpath,title,path):
        if path:
            of.write('<a href="%s/%s.%s">%s</a>\n' % (path,lpath,self.ext,title))
        else:
            of.write('<a href="%s.%s">%s</a>\n' % (lpath,self.ext,title))

    def display_first_image_as_thumbnail( self, of, db, photolist=None):

        if not photolist or not self.use_gallery:
            return
        
        photo_handle = photolist[0].get_reference_handle()
        photo = db.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        if mime_type:
            try:
                (real_path,newpath) = self.copy_media(photo)
                of.write('<div class="snapshot">\n')
                self.media_link(of,photo_handle,newpath,'',up=True)
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
            if mime_type:
                try:
                    (real_path,newpath) = self.copy_media(photo)
                    descr = " ".join(wrapper.wrap(photo.get_description()))
                    self.media_link(of, photo_handle, newpath, descr, up=True)
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))
            else:
                try:
                    descr = " ".join(wrapper.wrap(photo.get_description()))
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

    def display_note_object(self,of,noteobj=None):
        if not noteobj:
            return
        format = noteobj.get_format()
        text = noteobj.get()
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

    def display_url_list(self,of,urllist=None):
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
            if url.get_type() == RelLib.UrlType.EMAIL and not uri.startswith("mailto:"):
                of.write('<td class="data"><a href="mailto:%s">%s</a>' % (uri,descr))
            elif url.get_type() == RelLib.UrlType.WEB_HOME and not uri.startswith("http://"):
                of.write('<td class="data"><a href="http://%s">%s</a>' % (uri,descr))
            elif url.get_type() == RelLib.UrlType.WEB_FTP and not uri.startswith("ftp://"):
                of.write('<td class="data"><a href="ftp://%s">%s</a>' % (uri,descr))
            else:
                of.write('<td class="data"><a href="%s">%s</a>' % (uri,descr))
            of.write('</td></tr>\n')
            index = index + 1
        of.write('</table>\n')
        of.write('</div>\n')

    def display_references(self,of,db,handlelist):
        if not handlelist:
            return
        of.write('<div id="references">\n')
        of.write('<h4>%s</h4>\n' % _('References'))
        of.write('<table class="infolist">\n')

        index = 1
        for (path,name,gid) in handlelist:
            of.write('<tr><td class="field">%d. ' % index)
            self.person_link(of,path,name,gid)
            of.write('</td></tr>\n')
            index = index + 1
        of.write('</table>\n')
        of.write('</div>\n')

    def build_path(self,handle,dirroot,up=False):
        path = ""
        if up:
            path = '../../../%s/%s/%s' % (dirroot,handle[0],handle[1])
        else:
            path = "%s/%s/%s" % (dirroot,handle[0],handle[1])
        
        if os.sys.platform == "win32":
            path = path.lower()
                              
        return path
            
    def build_name(self,path,base):
        if path:
            return path + "/" + base + "." + self.ext
        else:
            return base + "." + self.ext

    def person_link(self,of,path,name,gid="",up=True):
        if up:
            path = "../../../" + path

        of.write('<a href="%s">%s' % (path,name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def surname_link(self,of,name,opt_val=None,up=False):
        handle = self.lnkfmt(name)
        dirpath = self.build_path(handle,'srn',up)

        of.write('<a href="%s/%s.%s">%s' % (dirpath,handle,self.ext,name))
        if opt_val != None:
            of.write('&nbsp;(%d)' % opt_val)
        of.write('</a>')

    def media_ref_link(self,of,handle,name,up=False):
        dirpath = self.build_path(handle,'img',up)
        of.write('<a href="%s/%s.%s">%s</a>' % (
            dirpath,handle,self.ext,name))

    def media_link(self,of,handle,path,name,up,usedescr=True):
        dirpath = self.build_path(handle,'img',up)
        of.write('<div class="thumbnail">\n')
        of.write('<p><a href="%s/%s.%s">' % (dirpath,handle,self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a></p>\n' % name)
        if usedescr:
            of.write('<p>%s</p>\n' % name)
        of.write('</div>\n')

    def doc_link(self,of,handle,name,up,usedescr=True):
        path = os.path.join('images','document.png')
        dirpath = self.build_path(handle,'img',up)
        of.write('<div class="thumbnail">\n')
        of.write('<p><a href="%s/%s.%s">' % (dirpath,handle,self.ext))
        of.write('<img src="../../../%s" ' % path)
        of.write('alt="%s" /></a>' % name)
        of.write('</p>\n')
        if usedescr:
            of.write('<p>%s</p>\n' % name)
        of.write('</div>\n')

    def source_link(self,of,handle,name,gid="",up=False):
        dirpath = self.build_path(handle,'src',up)
        of.write('<a href="%s/%s.%s">%s' % (
            dirpath,handle,self.ext,name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link(self,of,handle,name,gid="",up=False):
        dirpath = self.build_path(handle,'plc',up)
        of.write('<a href="%s/%s.%s">%s' % (
            dirpath,handle,self.ext,name))
        if not self.noid and gid != "":
            of.write('&nbsp;<span class="grampsid">[%s]</span>' % gid)
        of.write('</a>')

    def place_link_str(self,handle,name,gid="",up=False):
        dirpath = self.build_path(handle,'plc',up)
        retval = '<a href="%s/%s.%s">%s' % (
            dirpath,handle,self.ext,name)
        if not self.noid and gid != "":
            retval = retval + '&nbsp;<span class="grampsid">[%s]</span>' % gid
        return retval + '</a>'

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualListPage(BasePage):

    def __init__(self, db, title, person_handle_list, restrict_list,
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
        of.write('<th>%s</th>\n' % _('Birth date'))
        of.write('</tr></thead>\n<tbody>\n')

        person_handle_list = sort_people(db,person_handle_list)

        for (surname,handle_list) in person_handle_list:
            first = True
            of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
            for person_handle in handle_list:
                person = db.get_person_from_handle(person_handle)
                if self.exclude_private:
                    person = ReportUtils.sanitize_person(db,person)
                of.write('<tr><td class="category">')
                if first:
                    of.write('<a name="%s">%s</a>' % (self.lnkfmt(surname),surname))
                else:
                    of.write('&nbsp;')
                of.write('</td><td class="data">')
                path = self.build_path(person.handle,"ppl",False)
                self.person_link(of, self.build_name(path,person.handle),
                                 _nd.display_given(person), person.gramps_id,False)
                of.write('</td><td class="field">')

                if person.handle in restrict_list:
                    of.write(_('restricted'))
                else:
                    birth_ref = person.get_birth_ref()
                    if birth_ref:
                        birth = db.get_event_from_handle(birth_ref.ref)
                        of.write(_dd.display(birth.get_date_object()))
                of.write('</td></tr>\n')
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

    def __init__(self, db, title, person_handle_list, restrict_list,
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
        of.write('<th>%s</th>\n' % _('Birth date'))
        of.write('</tr></thead>\n<tbody>\n')

        for person_handle in person_handle_list:
            person = db.get_person_from_handle(person_handle)
            if self.exclude_private:
                person = ReportUtils.sanitize_person(db,person)
            of.write('<tr><td class="category">')
            path = self.build_path(person.handle,"ppl",True)
            self.person_link(of, self.build_name(path,person.handle),
                             person.get_primary_name().get_first_name(),
                             person.gramps_id,False)
            of.write('</td><td class="field">')
            if person.handle in restrict_list:
                of.write(_('restricted'))
            else:
                birth_ref = person.get_birth_ref()
                if birth_ref:
                    birth = db.get_event_from_handle(birth_ref.ref)
                    birth_date = _dd.display(birth.get_date_object())
                    of.write(birth_date)
            of.write('</td></tr>\n')
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
            n = ReportUtils.place_name(db,handle)

            if not n or len(n) == 0:
                continue
            
            if n[0] != last_letter:
                last_letter = n[0]
                of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
                of.write('<tr><td class="category">%s</td>' % last_letter)
                of.write('<td class="data">')
                self.place_link(of,place.handle,n,place.gramps_id)
                of.write('</td></tr>')
                last_surname = n
            elif n != last_surname:
                of.write('<tr><td class="category">&nbsp;</td>')
                of.write('<td class="data">')
                self.place_link(of,place.handle,n,place.gramps_id)
                of.write('</td></tr>')
                last_surname = n
            
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
        media_list = ReportUtils.sanitize_media_ref_list( db, media_list, self.exclude_private)
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
        self.display_note_object(of, place.get_note_object())
        self.display_url_list(of, ReportUtils.sanitize_list( place.get_url_list(), self.exclude_private))
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
            
        mime_type = photo.get_mime_type()
        note_only = mime_type == None
        
        if not note_only:
            newpath = self.copy_source_file(handle, photo)
            target_exists = newpath != None
        else:
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
            self.media_ref_link(of,next,_('Next'),True)

        of.write('</div>\n')

        if mime_type:
            if mime_type.startswith("image/"):
                of.write('<div class="centered">\n')
                if target_exists:
                    of.write('<img ')
                    of.write('src="../../../%s" alt="%s" />\n' % (newpath, self.page_title))
                else:
                    of.write('<br /><span>(%s)</span>' % _("The file has been moved or deleted"))
                of.write('</div>\n')
            else:
                import tempfile

                dirname = tempfile.mkdtemp()
                thmb_path = os.path.join(dirname,"temp.png")
                if ImgManip.run_thumbnailer(mime_type, photo.get_path(), thmb_path, 320):
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
        if not note_only:
            of.write('<tr>\n')
            of.write('<td class="field">%s</td>\n' % _('MIME type'))
            of.write('<td class="data">%s</td>\n' % photo.mime)
            of.write('</tr>\n')
        date = _dd.display(photo.get_date_object())
        if date != "":
            of.write('<tr>\n')
            of.write('<td class="field">%s</td>\n' % _('Date'))
            of.write('<td class="data">%s</td>\n' % date)
            of.write('</tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

        self.display_note_object(of, photo.get_note_object())
        self.display_attr_list(of, ReportUtils.sanitize_list( photo.get_attribute_list(), self.exclude_private))
        self.display_references(of,db,media_list)
        self.display_footer(of,db)
        self.close_file(of)

    def display_attr_list(self,of,attrlist=None):
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

    def copy_source_file(self,handle,photo):
        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.build_path(handle,'images')
        newpath = os.path.join(to_dir,handle+ext)

        try:
            if self.archive:
                self.archive.add(photo.get_path(),str(newpath))
            else:
                to_dir = os.path.join(self.html_dir,to_dir)
                if not os.path.isdir(to_dir):
                    os.makedirs(to_dir)
                shutil.copyfile(photo.get_path(),
                                os.path.join(self.html_dir,newpath))
            return newpath
        except (IOError,OSError),msg:
            WarningDialog(_("Missing media object"),str(msg))            
            return None

    def copy_thumbnail(self,handle,photo):
        to_dir = self.build_path(handle,'thumb')
        to_path = os.path.join(to_dir,handle+".png")
        if photo.get_mime_type():
            from_path = ImgManip.get_thumbnail_path(photo.get_path(),photo.get_mime_type())
            if not os.path.isfile(from_path):
                from_path = os.path.join(const.data_dir,"document.png")
        else:
            from_path = os.path.join(const.data_dir,"document.png")
            
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
            of.write('<th><a href="%s.%s">%s</a></th>\n' % ("index", self.ext, _('Surname')))
        else:
            of.write('<th><a href="%s.%s">%s</a></th>\n' % ("surnames", self.ext, _('Surname')))

        of.write('<th><a href="%s.%s">%s</a></th>\n' % ("surnames_count", self.ext, _('Number of people')))
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
            
            if surname[0] != last_letter:
                last_letter = surname[0]
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
        note_id = options.handler.options_dict['NWEBintronote']

        if self.use_home:
            of = self.create_file("introduction")
        else:
            of = self.create_file("index")
            
        author = get_researcher().get_name()
        self.display_header(of, db, _('Introduction'), author)

        of.write('<h3>%s</h3>\n' % _('Introduction'))

        if note_id:
            obj = db.get_object_from_handle(note_id)

            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath,thumb_path) = self.copy_media(obj,False)
                    self.store_file(archive,self.html_dir,obj.get_path(),
                                    newpath)
                    of.write('<div class="centered">\n')
                    of.write('<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</div>\n')
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))
    
            note_obj = obj.get_note_object()
            if note_obj:
                text = note_obj.get()
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
class HomePage(BasePage):

    def __init__(self, db, title, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list, "")

        note_id = options.handler.options_dict['NWEBhomenote']
        of = self.create_file("index")
        author = get_researcher().get_name()
        self.display_header(of,db,_('Home'),author)

        of.write('<h3>%s</h3>\n' % _('Home'))

        if note_id:
            obj = db.get_object_from_handle(note_id)

            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath,thumb_path) = self.copy_media(obj,False)
                    self.store_file(archive,self.html_dir,obj.get_path(),
                                    newpath)
                    of.write('<div class="centered">\n')
                    of.write('<img ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</div>\n')
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))

            note_obj = obj.get_note_object()
            if note_obj:
                text = note_obj.get()
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
        keys.sort(strcoll_case_sensitive)

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
            self.source_link(of,handle,source.get_title(),source.gramps_id)
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
        media_list = ReportUtils.sanitize_media_ref_list(db, media_list, self.exclude_private)
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
        self.display_note_object(of, source.get_note_object())
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
        mlist.sort(self.by_media_title)
        for handle in mlist:
            media = db.get_object_from_handle(handle)
            date = _dd.display(media.get_date_object())
            of.write('<tr>\n')
            
            of.write('<td class="category">%d.</td>\n' % index)
            
            of.write('<td class="data">')
            self.media_ref_link(of,handle,media.get_description())
            of.write('</td>\n')

            of.write('<td class="data">%s</td>\n' % date)

            of.write('</tr>\n')
            index += 1
            
        of.write('</table>\n')

        self.display_footer(of,db)
        self.close_file(of)

    def by_media_title(self,a_id,b_id):
        """Sort routine for comparing two events by their dates. """
        if not (a_id and b_id):
            return False
        a = self.db.get_object_from_handle(a_id)
        b = self.db.get_object_from_handle(b_id)
        return cmp(a.desc,b.desc)


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

        note_id = options.handler.options_dict['NWEBcontact']
        if note_id:
            obj = db.get_object_from_handle(note_id)

            mime_type = obj.get_mime_type()
        
            if mime_type and mime_type.startswith("image"):
                try:
                    (newpath,thumb_path) = self.copy_media(obj,False)
                    self.store_file(archive,self.html_dir,obj.get_path(),
                                    newpath)

                    of.write('<div class="rightwrap">\n')
                    of.write('<table><tr>')
                    of.write('<td height="205">')
                    of.write('<img height="200" ')
                    of.write('src="%s" ' % newpath)
                    of.write('alt="%s" />' % obj.get_description())
                    of.write('</td></tr></table>\n')
                    of.write('</div>\n')
                except (IOError,OSError),msg:
                    WarningDialog(_("Could not add photo to page"),str(msg))

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

        if obj:
            nobj = obj.get_note_object()
            if nobj:
                format = nobj.get_format()
                text = nobj.get()
    
                if format:
                    text = u"<pre>%s</pre>" % text
                else:
                    text = u"</p><p>".join(text.split("\n"))
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
        RelLib.Person.MALE    : _('male'),
        RelLib.Person.FEMALE  : _('female'),
        RelLib.Person.UNKNOWN : _('unknown'),
        }
    
    def __init__(self, db, person, title, ind_list, restrict_list,
                 place_list, src_list, options, archive, media_list):
        BasePage.__init__(self, title, options, archive, media_list,
                          person.gramps_id)
        self.person = person
        self.restrict = person.handle in restrict_list
        self.db = db
        self.ind_list = ind_list
        self.src_list = src_list
        self.src_refs = []
        self.place_list = place_list
        self.sort_name = sort_nameof(self.person,self.exclude_private)
        self.name = sort_nameof(self.person,self.exclude_private)
        
        of = self.create_link_file(person.handle,"ppl")
        self.display_header(of,db, self.sort_name,
                            get_researcher().get_name(),up=True)
        self.display_ind_general(of)
        self.display_ind_events(of)
        self.display_attr_list(of, self.person.get_attribute_list())
        self.display_ind_parents(of)
        self.display_ind_relationships(of)
        self.display_addresses(of)

        if not self.restrict:
            media_list = []
            photolist = ReportUtils.sanitize_media_ref_list( db,
                                                             self.person.get_media_list(), 
                                                             self.exclude_private )
            if len(photolist) > 1:
                media_list = photolist[1:]
            for handle in self.person.get_family_handle_list():
                family = self.db.get_family_from_handle(handle)
                media_list += ReportUtils.sanitize_media_ref_list( db,
                                                                   family.get_media_list(), 
                                                                   self.exclude_private )
                for evt_ref in family.get_event_ref_list():
                     event = self.db.get_event_from_handle(evt_ref.ref)
                     media_list += ReportUtils.sanitize_media_ref_list( db,
                                                                        event.get_media_list(), 
                                                                        self.exclude_private )
            for evt_ref in self.person.get_primary_event_ref_list():
                event = self.db.get_event_from_handle(evt_ref.ref)
                if event:
                    media_list += ReportUtils.sanitize_media_ref_list( db,
                                                                       event.get_media_list(), 
                                                                       self.exclude_private )

            self.display_additional_images_as_gallery(of, db, media_list)
            
            self.display_note_object(of, self.person.get_note_object())
            self.display_url_list(of, self.person.get_url_list())
            self.display_ind_sources(of)
        self.display_ind_pedigree(of)
        if self.usegraph:
            self.display_tree(of)
        self.display_footer(of,db)
        self.close_file(of)

    def display_attr_list(self,of,attrlist=None):
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

    def draw_box(self,of,center,col,person):
        top = center - HEIGHT/2
        xoff = XOFFSET+col*(WIDTH+HGAP)
        
        of.write('<div class="boxbg" style="top: %dpx; left: %dpx;">\n' % (top,xoff+1))
        of.write('<table><tr><td class="box">')
        person_link = person.handle in self.ind_list
        if person_link:
            person_name = nameof(person,self.exclude_private)
            path = self.build_path(person.handle,"ppl",False)
            fname = self.build_name(path,person.handle)
            self.person_link(of, fname, person_name)
        else:
            of.write(nameof(person,self.exclude_private))
        of.write('</td></tr></table>\n')
        of.write('</div>\n')
        of.write('<div class="shadow" style="top: %dpx; left: %dpx;"></div>\n' % (top+SHADOW,xoff+SHADOW))
        of.write('<div class="border" style="top: %dpx; left: %dpx;"></div>\n' % (top-1, xoff))

    def extend_line(self,of,y0,x0):
        of.write('<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y0,x0,HGAP/2))
        of.write('<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' % 
                 (y0+SHADOW,x0,HGAP/2+SHADOW))

    def connect_line(self,of,y0,y1,col):
        if y0 < y1:
            y = y0
        else:
            y = y1
            
        x0 = XOFFSET + col * WIDTH + (col-1)*HGAP + HGAP/2
        of.write('<div class="bvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1,x0,HGAP/2))
        of.write('<div class="gvline" style="top: %dpx; left: %dpx; width: %dpx;"></div>\n' %
                 (y1+SHADOW,x0+SHADOW,HGAP/2+SHADOW))
        of.write('<div class="bhline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y,x0,abs(y0-y1)))
        of.write('<div class="ghline" style="top: %dpx; left: %dpx; height: %dpx;"></div>\n' %
                 (y+SHADOW,x0+SHADOW,abs(y0-y1)))

    def draw_connected_box(self,of,center1,center2,col,handle):
        if not handle:
            return None
        person = self.db.get_person_from_handle(handle)
        if self.exclude_private:
            person = ReportUtils.sanitize_person( self.db, person)
        self.draw_box(of,center2,col,person)
        self.connect_line(of,center1,center2,col)
        return person
    
    def display_tree(self,of):
        if not self.person.get_main_parents_family_handle():
            return
        
        of.write('<div id="tree">\n')
        of.write('<h4>%s</h4>\n' % _('Ancestors'))
        of.write('<div style="position: relative;">\n')

        generations = self.graphgens
        
        max_in_col = 1 <<(generations-1)
        max_size = HEIGHT*max_in_col + VGAP*(max_in_col+1)
        center = int(max_size/2)
        self.draw_tree(of,1,generations,max_size,0,center,self.person.handle)

        of.write('</div>\n')
        of.write('</div>\n')
        of.write('<table style="height: %dpx; width: %dpx;"><tr><td></td></tr></table>\n' %
                 (max_size,XOFFSET+(generations)*WIDTH+(generations-1)*HGAP))
    
    def draw_tree(self,of,gen,maxgen,max_size,old_center,new_center,phandle):
        if gen > maxgen:
            return
        gen_offset = int(max_size / pow(2,gen+1))
        person = self.db.get_person_from_handle(phandle)
        if not person:
            return

        if gen == 1:
            self.draw_box(of,new_center,0,person)
        else:
            self.draw_connected_box(of,old_center,new_center,gen-1,phandle)
        
        if gen == maxgen:
            return

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = XOFFSET + (gen)*WIDTH + (gen-1)*HGAP
            self.extend_line(of,new_center,line_offset)

            gen = gen + 1
            family = self.db.get_family_from_handle(family_handle)
            
            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            self.draw_tree(of,gen,maxgen,max_size,new_center,f_center,f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            self.draw_tree(of,gen,maxgen,max_size,new_center,m_center,m_handle)

    def display_ind_sources(self,of):
        sreflist = self.src_refs + self.person.get_source_references()
        if not sreflist or self.restrict:
            return
        of.write('<div id="sourcerefs">\n')
        of.write('<h4>%s</h4>\n' % _('Source References'))
        of.write('<table class="infolist">\n')

        index = 1
        for sref in sreflist:
            lnk = (self.cur_name, self.page_title, self.gid)
            shandle = sref.get_reference_handle()
            if not shandle:
                continue
            if self.src_list.has_key(shandle):
                if lnk not in self.src_list[shandle]:
                    self.src_list[shandle].append(lnk)
            else:
                self.src_list[shandle] = [lnk]

            source = self.db.get_source_from_handle(shandle)
            title = source.get_title()
            of.write('<tr><td class="field">')
            of.write('<a name="sref%d"></a>%d.</td>' % (index,index))
            of.write('<td class="field">')
            self.source_link(of,source.handle,title,source.gramps_id,True)
            tmp = []
            confidence = Utils.confidence.get(sref.confidence, _('Unknown'))
            for (label,data) in [(_('Date'),_dd.display(sref.date)),
                                 (_('Page'),sref.page),
                                 (_('Confidence'),confidence),
                                 (_('Text'),sref.text)]:
                if data:
                    tmp.append("%s: %s" % (label,data))
            if len(tmp) > 0:
                of.write('<br />' + '<br />'.join(tmp))
            of.write('</td></tr>\n')
            index += 1
        of.write('</table>\n')
        of.write('</div>\n')

    def display_ind_pedigree(self,of):

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = self.db.get_family_from_handle(parent_handle)
            father_id = family.get_father_handle()
            mother_id = family.get_mother_handle()
            mother = self.db.get_person_from_handle(mother_id)
            if mother and self.exclude_private:
                mother = ReportUtils.sanitize_person( self.db, mother)
            father = self.db.get_person_from_handle(father_id)
            if father and self.exclude_private:
                father = ReportUtils.sanitize_person( self.db, father)
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
                    if child and self.exclude_private:
                        child = ReportUtils.sanitize_person( self.db, child)
                    self.pedigree_person(of,child)
        else:
            of.write('<span class="thisperson">%s</span><br />\n' % self.name)
            self.pedigree_family(of)

        of.write('</div>\n')
        if father or mother:
            of.write('</div>\n')
        of.write('</div>\n</div>\n')

    def display_ind_general(self,of):
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
            pname = name_nameof(name,self.exclude_private)
            type = str( name.get_type() )
            of.write('<tr><td class="field">%s</td>\n' % _(type))
            of.write('<td class="data">%s' % pname)
            if not self.restrict:
                nshl = []
                for nsref in name.get_source_references():
                    self.src_refs.append(nsref)
                    nsh = nsref.get_reference_handle()
                    lnk = (self.cur_name, self.page_title, self.gid)
                    if self.src_list.has_key(nsh):
                        if self.person.handle not in self.src_list[nsh]:
                            self.src_list[nsh].append(lnk)
                    else:
                        self.src_list[nsh] = [lnk]
                    nshl.append(nsref)
                if nshl:
                    of.write( " <sup>")
                    for nsh in nshl:
                        index = self.src_refs.index(nsh)+1
                        of.write(' <a href="#sref%d">%d</a>' % (index,index))
                    of.write( " </sup>")

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

    def display_ind_events(self,of):
        evt_ref_list = self.person.get_primary_event_ref_list()
        
        if not evt_ref_list:
            return
        if self.restrict:
            return
        
        of.write('<div id="events">\n')
        of.write('<h4>%s</h4>\n' % _('Events'))
        of.write('<table class="infolist">\n')

        for event_ref in evt_ref_list:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                evt_name = str(event.get_type())
                of.write('<tr><td class="field">%s</td>\n' % evt_name)
                of.write('<td class="data">\n')
                of.write(self.format_event(event))
                of.write('</td>\n')
                of.write('</tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')
        
    def display_addresses(self,of):
        if self.restrict:
            return
        
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
        if self.exclude_private:
            child = ReportUtils.sanitize_person( self.db, child)
        gid = child.get_gramps_id()
        if use_link:
            child_name = nameof(child, self.exclude_private)
            path = self.build_path(child_handle,"ppl",False)
            self.person_link(of, self.build_name(path,child_handle),
                             child_name, gid)
        else:
            of.write(nameof(child,self.exclude_private))
        of.write(u"<br />\n")

    def display_parent(self, of, handle, title, rel):
        use_link = handle in self.ind_list 
        person = self.db.get_person_from_handle(handle)
        if self.exclude_private:
            person = ReportUtils.sanitize_person( self.db, person)
        of.write('<td class="field">%s</td>\n' % title)
        of.write('<td class="data">')
        val = person.gramps_id
        if use_link:
            path = self.build_path(handle,"ppl",False)
            fname = self.build_name(path,handle)
            self.person_link(of, fname, nameof(person,self.exclude_private),
                             val)
        else:
            of.write(nameof(person,self.exclude_private))
        if rel != RelLib.ChildRefType.BIRTH:
            of.write('&nbsp;&nbsp;&nbsp;(%s)' % str(rel))
        of.write('</td>\n')

    def display_ind_parents(self,of):
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
                childlist = family.get_child_ref_list()
                if len(childlist) > 1:
                    of.write('<tr>\n')
                    of.write('<td class="field">%s</td>\n' % _("Siblings"))
                    of.write('<td class="data">\n')
                    for child_ref in childlist:
                        child_handle = child_ref.ref
                        if child_handle != self.person.handle:
                            self.display_child_link(of,child_handle)
                    of.write('</td>\n</tr>\n')
            of.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
        of.write('</table>\n')
        of.write('</div>\n')

    def display_ind_relationships(self,of):
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

    def display_spouse(self,of,family,first=True):
        gender = self.person.get_gender()
        reltype = family.get_relationship()

        if reltype == RelLib.FamilyRelType.MARRIED:
            if gender == RelLib.Person.FEMALE:
                relstr = _("Husband")
            elif gender == RelLib.Person.MALE:
                relstr = _("Wife")
            else:
                relstr = _("Partner")
        else:
            relstr = _("Partner")

        spouse_id = ReportUtils.find_spouse(self.person,family)
        if spouse_id:
            spouse = self.db.get_person_from_handle(spouse_id)
            if self.exclude_private:
                spouse = ReportUtils.sanitize_person( self.db, spouse)
            name = nameof(spouse,self.exclude_private)
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
                spouse_name = nameof(spouse,self.exclude_private)
                path = self.build_path(spouse.handle,"ppl",False)
                fname = self.build_name(path,spouse.handle)
                self.person_link(of, fname, spouse_name, gid)
            else:
                of.write(name)
        of.write('</td>\n</tr>\n')

        if self.restrict:
            return
        
        for event_ref in family.get_event_ref_list():
            event = self.db.get_event_from_handle(event_ref.ref)
            if self.exclude_private and event.private:
                continue

            evtType = str(event.get_type())
            of.write('<tr><td>&nbsp;</td>\n')
            of.write('<td class="field">%s</td>\n' % evtType)
            of.write('<td class="data">\n')
            of.write(self.format_event(event))
            of.write('</td>\n</tr>\n')
        for attr in family.get_attribute_list():
            if self.exclude_private and attr.private:
                continue
            attrType = str(attr.get_type())
            of.write('<tr><td>&nbsp;</td>\n')
            of.write('<td class="field">%s</td>' % attrType)
            of.write('<td class="data">%s</td>\n</tr>\n' % attr.get_value())
        nobj = family.get_note_object()
        if nobj:
            text = nobj.get()
            format = nobj.get_format()
            if text:
                of.write('<tr><td>&nbsp;</td>\n')
                of.write('<td class="field">%s</td>\n' % _('Narrative'))
                of.write('<td class="data">\n')
                if format:
                    of.write( u"<pre>%s</pre>" % text )
                else:
                    of.write( u"</p><p>".join(text.split("\n")))
                of.write('</td>\n</tr>\n')
            
    def pedigree_person(self,of,person,is_spouse=False):
        person_link = person.handle in self.ind_list
        if is_spouse:
            of.write('<span class="spouse">')
        if person_link:
            person_name = nameof(person,self.exclude_private)
            path = self.build_path(person.handle,"ppl",False)
            fname = self.build_name(path,person.handle)
            self.person_link(of, fname, person_name)
        else:
            of.write(nameof(person,self.exclude_private))
        if is_spouse:
            of.write('</span>')
        of.write('<br />\n')

    def pedigree_family(self,of):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                if self.exclude_private:
                    spouse = ReportUtils.sanitize_person( self.db, spouse)
                self.pedigree_person(of,spouse,True)
            childlist = rel_family.get_child_ref_list()
            if childlist:
                of.write('<div class="pedigreegen">\n')
                for child_ref in childlist:
                    child = self.db.get_person_from_handle(child_ref.ref)
                    if self.exclude_private:
                        child = ReportUtils.sanitize_person( self.db, child)
                    self.pedigree_person(of,child)
                of.write('</div>\n')

    def format_event(self,event):
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
        return text
    
    def get_citation_links(self, source_ref_list):
        gid_list = []
        lnk = (self.cur_name, self.page_title, self.gid)
        text = ""

        for sref in source_ref_list:
            if self.exclude_private and sref.private:
                continue
            handle = sref.get_reference_handle()
            gid_list.append(sref)

            if self.src_list.has_key(handle):
                if lnk not in self.src_list[handle]:
                    self.src_list[handle].append(lnk)
            else:
                self.src_list[handle] = [lnk]
            self.src_refs.append(sref)
            
        if len(gid_list) > 0:
            text = text + " <sup>"
            for ref in gid_list:
                index = self.src_refs.index(ref)+1
                text = text + ' <a href="#sref%d">%d</a>' % (index,index)
            text = text + "</sup>"

        return text
            
#------------------------------------------------------------------------
#
# WebReport
#
#------------------------------------------------------------------------
class WebReport(Report):
    def __init__(self,database,person,options):
        """
        Creates WebReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter
        od
        NWEBrestrictinfo
        NWEBrestrictyears
        NWEBincpriv
        NWEBnonames
        NWEBidxcol
        NWEBincid
        NWEBext
        NWEBencoding
        NWEBintronote
        NWEBhomenote
        NWEBnoid
        """
        
        self.database = database
        self.start_person = person
        self.options = options

        filter_num = options.get_filter_number()
        filters = options.get_report_filters(person)
        self.filter = filters[filter_num]

        self.target_path = options.handler.options_dict['NWEBod']
        self.copyright = options.handler.options_dict['NWEBcopyright']
        self.ext = options.handler.options_dict['NWEBext']
        self.encoding = options.handler.options_dict['NWEBencoding']
        self.css = options.handler.options_dict['NWEBcss']
        self.restrict = options.handler.options_dict['NWEBrestrictinfo']
        self.restrict_years = options.handler.options_dict['NWEBrestrictyears']
        self.exclude_private = options.handler.options_dict['NWEBincpriv']
        self.noid = options.handler.options_dict['NWEBnoid']
        self.title = options.handler.options_dict['NWEBtitle']
        self.sort = Sort.Sort(self.database)
        self.inc_gallery = options.handler.options_dict['NWEBgallery']
        self.inc_contact = options.handler.options_dict['NWEBcontact'] != u""
        self.inc_download = options.handler.options_dict['NWEBdownload']
        self.user_header = options.handler.options_dict['NWEBheader']
        self.user_footer = options.handler.options_dict['NWEBfooter']
        self.use_archive = options.handler.options_dict['NWEBarchive']
        self.use_intro = options.handler.options_dict['NWEBintronote'] != u""
        self.use_home = options.handler.options_dict['NWEBhomenote'] != u""
        
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

        self.progress = Utils.ProgressMeter(_("Generate HTML reports"),'')

        # Build the person list
        ind_list,restrict_list = self.build_person_list()

        # Generate the CSS file if requested
        if self.css != '':
            self.write_css(archive,self.target_path,self.css)

        # Copy the Creative Commons icon if the a Creative Commons
        # license is requested
        if 0 < self.copyright < 7:
            from_path = os.path.join(const.image_dir,"somerights20.gif")
            to_path = os.path.join("images","somerights20.gif")
            self.store_file(archive,self.target_path,from_path,to_path)

        from_path = os.path.join(const.image_dir,"document.png")
        to_path = os.path.join("images","document.png")
        self.store_file(archive,self.target_path,from_path,to_path)

        place_list = {}
        source_list = {}
        self.photo_list = {}

        self.base_pages(self.photo_list, archive)
        self.person_pages(ind_list, restrict_list, place_list, source_list, archive)
        self.surname_pages(ind_list, restrict_list, archive)
        self.place_pages(place_list, source_list, archive)
        self.source_pages(source_list, self.photo_list, archive)
        if self.inc_gallery:
            self.gallery_pages(self.photo_list, source_list, archive)
        
        if archive:
            archive.close()
        self.progress.close()

    def build_person_list(self):
        """
        Builds the person list. Gets all the handles from the database
        and then:

          1) Applies the chosen filter.
          2) Applies the privacy filter if requested.
          3) Applies the living person filter if requested
        """

        # gets the person list and applies the requested filter
        
        ind_list = self.database.get_person_handles(sort_handles=False)
        self.progress.set_pass(_('Filtering'),1)
        ind_list = self.filter.apply(self.database,ind_list)
        restrict_list = set()

        # if private records need to be filtered out, strip out any person
        # that has the private flag set.
        if not self.exclude_private:
            self.progress.set_pass(_('Applying privacy filter'),len(ind_list))
            ind_list = filter(self.filter_private,ind_list)

        years = time.localtime(time.time())[0]

        # Filter out people who are restricted due to the living
        # people rule
        if self.restrict:
            self.progress.set_pass(_('Filtering living people'),len(ind_list))
            for key in ind_list:
                self.progress.step()
                p = self.database.get_person_from_handle(key)
                if Utils.probably_alive(p,self.database,years,self.restrict_years):
                    restrict_list.add(key)

        return (ind_list,restrict_list)

    def filter_private(self,key):
        """
        Return True if the person is not marked private.
        """
        self.progress.step()
        return not self.database.get_person_from_handle(key).private

    def write_css(self,archive,html_dir,css_file):
        """
        Copy the CSS file to the destination.
        """
        if archive:
            fname = os.path.join(const.data_dir,css_file)
            archive.add(fname,_NARRATIVE)
        else:
            shutil.copyfile(os.path.join(const.data_dir,css_file),
                            os.path.join(html_dir,_NARRATIVE))

    def person_pages(self, ind_list, restrict_list, place_list, source_list, archive):

        self.progress.set_pass(_('Creating individual pages'),len(ind_list))

        IndividualListPage(
            self.database, self.title, ind_list, restrict_list, 
            self.options, archive, self.photo_list)

        for person_handle in ind_list:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)
            
            if not self.exclude_private:
                person = ReportUtils.sanitize_person(self.database,person)

            IndividualPage(
                self.database, person, self.title, ind_list, restrict_list,
                place_list, source_list, self.options, archive, self.photo_list)
            
    def surname_pages(self, ind_list, restrict_list, archive):
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
            self.database, self.title, ind_list, self.options, archive,
            self.photo_list, SurnameListPage.ORDER_BY_NAME,defname)
        
        SurnameListPage(
            self.database, self.title, ind_list, self.options, archive,
            self.photo_list, SurnameListPage.ORDER_BY_COUNT,"surnames_count")

        for (surname,handle_list) in local_list:
            SurnamePage(self.database, surname, handle_list, restrict_list,
                        self.options, archive, self.photo_list)
            self.progress.step()
        
    def source_pages(self, source_list, photo_list, archive):
        
        self.progress.set_pass(_("Creating source pages"),len(source_list))

        SourcesPage(self.database,self.title, source_list.keys(),
                    self.options, archive, photo_list)

        for key in list(source_list):
            SourcePage(self.database, self.title, key, source_list,
                       self.options, archive, photo_list)
            self.progress.step()
        

    def place_pages(self, place_list, source_list, archive):

        self.progress.set_pass(_("Creating place pages"),len(place_list))

        PlaceListPage(
            self.database, self.title, place_list, source_list, self.options,
            archive, self.photo_list)

        for place in place_list.keys():
            PlacePage(
                self.database, self.title, place, source_list, place_list,
                self.options, archive, self.photo_list)
            self.progress.step()

    def gallery_pages(self, photo_list, source_list, archive):
        
        self.progress.set_pass(_("Creating media pages"),len(photo_list))

        GalleryPage(self.database, self.title, source_list,
                    self.options, archive, self.photo_list)

        prev = None
        total = len(self.photo_list)
        index = 1
        photo_keys = self.photo_list.keys()
        photo_keys.sort(self.by_media_title)
        
        for photo_handle in photo_keys:
            if index == total:
                next = None
            else:
                next = photo_keys[index]
            MediaPage(self.database, self.title, photo_handle, source_list,
                      self.options, archive, self.photo_list[photo_handle],
                      (prev, next, index, total))
            self.progress.step()
            prev = photo_handle
            index += 1

    def by_media_title(self,a_id,b_id):
        """Sort routine for comparing two events by their dates. """
        if not (a_id and b_id):
            return False
        a = self.database.get_object_from_handle(a_id)
        b = self.database.get_object_from_handle(b_id)
        return cmp(a.desc,b.desc)

    def base_pages(self, photo_list, archive):

        if self.use_home:
            HomePage(self.database, self.title, self.options, archive, photo_list)

        if self.inc_contact:
            ContactPage(self.database, self.title, self.options, archive, photo_list)
            
        if self.inc_download:
            DownloadPage(self.database, self.title, self.options, archive, photo_list)
        
        if self.use_intro:
            IntroductionPage(self.database, self.title, self.options,
                             archive, photo_list)

    def store_file(self,archive,html_dir,from_path,to_path):
        """
        Store the file in the destination.
        """
        if archive:
            archive.add(from_path,to_path)
        else:
            shutil.copyfile(from_path,os.path.join(html_dir,to_path))

    def add_styles(self,doc):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,database=None,person_id=None):
        ReportOptions.__init__(self,name,person_id)
        self.db = database
        
    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'NWEBarchive'       : 0,
            'NWEBgraph'         : 1,
            'NWEBgraphgens'     : 4,
            'NWEBod'            : './',
            'NWEBcopyright'     : 0,
            'NWEBrestrictinfo'  : 0,
            'NWEBrestrictyears' : 30,
            'NWEBincpriv'       : 0,
            'NWEBnonames'       : 0,
            'NWEBnoid'          : 0,
            'NWEBcontact'       : '', 
            'NWEBgallery'       : 1, 
            'NWEBheader'        : '', 
            'NWEBfooter'        : '', 
            'NWEBdownload'      : 0, 
            'NWEBtitle'         : _('My Family Tree'), 
            'NWEBincid'         : 0,
            'NWEBext'           : 'html',
            'NWEBencoding'      : 'utf-8',
            'NWEBcss'           : 'main0.css',
            'NWEBintronote'     : '',
            'NWEBhomenote'      : '',
        }

        self.options_help = {
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }

    def get_report_filters(self,person):
        """Set up the list of possible content filters."""
        if person:
            name = person.get_primary_name().get_name()
            gramps_id = person.get_gramps_id()
        else:
            name = 'PERSON'
            gramps_id = ''

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        des = GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(Rules.Person.IsDescendantOf([gramps_id,1]))

        df = GenericFilter()
        df.set_name(_("Descendant Families of %s") % name)
        df.add_rule(Rules.Person.IsDescendantFamilyOf([gramps_id,1]))

        ans = GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(Rules.Person.IsAncestorOf([gramps_id,1]))

        com = GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(Rules.Person.HasCommonAncestorWith([gramps_id]))

        the_filters = [all,des,df,ans,com]
        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))
        return the_filters

    def add_user_options(self,dialog):
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        restrict_years = _("Years to restrict from person's death")
        title_msg = _("Web site title")
        ext_msg = _("File extension")
        contact_msg = _("Publisher contact/Note ID")
        gallery_msg = _("Include images and media objects")
        download_msg = _("Include download page")
        graph_msg = _("Include ancestor graph")

        self.no_private = gtk.CheckButton(priv_msg)
        self.no_private.set_active(not self.options_dict['NWEBincpriv'])

        self.inc_graph = gtk.CheckButton(graph_msg)
        self.inc_graph.set_active(self.options_dict['NWEBgraph'])
        
        self.graph_gens = gtk.combo_box_new_text()
        self.graph_gens_options = ['2','3','4','5']
        for text in self.graph_gens_options:
            self.graph_gens.append_text(text)
        def_gens = str(self.options_dict['NWEBgraphgens'])
        if def_gens in self.graph_gens_options:
            self.graph_gens.set_active(self.graph_gens_options.index(def_gens))
        else:
            self.graph_gens.set_active(0)

        self.noid = gtk.CheckButton(_('Suppress GRAMPS ID'))
        self.noid.set_active(self.options_dict['NWEBnoid'])

        self.restrict_living = gtk.CheckButton(restrict_msg)
        self.restrict_living.connect('toggled',self.restrict_toggled)

        self.include_gallery = gtk.CheckButton(gallery_msg)
        self.include_gallery.set_active(self.options_dict['NWEBgallery'])

        self.restrict_years = gtk.Entry()
        self.restrict_years.set_text(str(self.options_dict['NWEBrestrictyears']))
        self.restrict_years.set_sensitive(False)
        
        self.restrict_living.set_active(self.options_dict['NWEBrestrictinfo'])
        self.hbox = gtk.HBox()
        self.hbox.set_spacing(12)
        self.hbox.pack_start(gtk.Label("     "),False,False)
        self.hbox.pack_start(gtk.Label("%s:" % restrict_years),False,False)
        self.hbox.add(self.restrict_years)

        self.inc_download = gtk.CheckButton(download_msg)
        self.inc_download.set_active(self.options_dict['NWEBdownload'])

        # FIXME: document this:
        # 0 -- no images of any kind
        # 1 -- no living images, but some images
        # 2 -- any images

        self.intro_note = gtk.Entry()
        self.intro_note.set_text(self.options_dict['NWEBintronote'])

        self.title = gtk.Entry()
        self.title.set_text(self.options_dict['NWEBtitle'])

        self.ext = gtk.combo_box_new_text()
        self.ext_options = ['.html','.htm','.shtml','.php','.php3','.cgi']
        for text in self.ext_options:
            self.ext.append_text(text)

        self.copy = gtk.combo_box_new_text()
        self.copy_options = [
            _('Standard copyright'),
            _('Creative Commons - By attribution'),
            _('Creative Commons - By attribution, No derivations'),
            _('Creative Commons - By attribution, Share-alike'),
            _('Creative Commons - By attribution, Non-commercial'),
            _('Creative Commons - By attribution, Non-commercial, No derivations'),
            _('Creative Commons - By attribution, Non-commercial, Share-alike'),
            _('No copyright notice'),
            ]
        for text in self.copy_options:
            self.copy.append_text(text)

        def_ext = "." + self.options_dict['NWEBext']
        self.ext.set_active(self.ext_options.index(def_ext))

        index = self.options_dict['NWEBcopyright']
        self.copy.set_active(index)

        cset_node = None
        cset = self.options_dict['NWEBencoding']

        store = gtk.ListStore(str,str)
        for data in _character_sets:
            if data[1] == cset:
                cset_node = store.append(row=data)
            else:
                store.append(row=data)
        self.encoding = GrampsNoteComboBox(store,cset_node)

        cset_node = None
        cset = self.options_dict['NWEBcss']
        store = gtk.ListStore(str,str)
        for data in _css_files:
            if data[1] == cset:
                cset_node = store.append(row=data)
            else:
                store.append(row=data)
        self.css = GrampsNoteComboBox(store,cset_node)

        dialog.add_option(title_msg,self.title)
        dialog.add_option(ext_msg,self.ext)
        dialog.add_option(_('Character set encoding'),self.encoding)
        dialog.add_option(_('Stylesheet'),self.css)
        dialog.add_option(_('Copyright'),self.copy)
        dialog.add_option(_('Ancestor graph generations'),self.graph_gens)
        dialog.add_option(None,self.inc_graph)

        title = _("Page Generation")


        media_list = [['','']]
        html_list = [['','']]
        
        if self.db:
            cursor = self.db.get_media_cursor()
            data = cursor.first()
            while data:
                (handle, value) = data
                if not value[3]:
                    html_list.append([value[4],handle])
                media_list.append([value[4],handle])    

                data = cursor.next()
            cursor.close()
        media_list.sort()
        html_list.sort()

        self.home_note = mk_combobox(media_list,self.options_dict['NWEBhomenote'])
        self.intro_note = mk_combobox(media_list,self.options_dict['NWEBintronote'])
        self.contact = mk_combobox(media_list,self.options_dict['NWEBcontact'])
        self.header = mk_combobox(html_list,self.options_dict['NWEBheader'])
        self.footer = mk_combobox(html_list,self.options_dict['NWEBfooter'])

        dialog.add_frame_option(title,_('Home Media/Note ID'),
                                self.home_note)
        dialog.add_frame_option(title,_('Introduction Media/Note ID'),
                                self.intro_note)
        dialog.add_frame_option(title,contact_msg,self.contact)
        dialog.add_frame_option(title,_('HTML user header'),self.header)
        dialog.add_frame_option(title,_('HTML user footer'),self.footer)
        dialog.add_frame_option(title,'',self.include_gallery)
        dialog.add_frame_option(title,None,self.inc_download)
        dialog.add_frame_option(title,None,self.noid)

        title = _("Privacy")
        dialog.add_frame_option(title,None,self.no_private)
        dialog.add_frame_option(title,None,self.restrict_living)
        dialog.add_frame_option(title,None,self.hbox)

    def restrict_toggled(self,obj):
        self.restrict_years.set_sensitive(obj.get_active())

    def parse_user_options(self,dialog):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        
        self.options_dict['NWEBrestrictinfo'] = int(self.restrict_living.get_active())
        self.options_dict['NWEBrestrictyears'] = int(self.restrict_years.get_text())
        self.options_dict['NWEBincpriv'] = int(not self.no_private.get_active())
        self.options_dict['NWEBnoid'] = int(self.noid.get_active())
        self.options_dict['NWEBcontact'] = unicode(self.contact.get_handle())
        self.options_dict['NWEBgallery'] = int(self.include_gallery.get_active())
        self.options_dict['NWEBheader'] = unicode(self.header.get_handle())
        self.options_dict['NWEBfooter'] = unicode(self.footer.get_handle())
        self.options_dict['NWEBdownload'] = int(self.inc_download.get_active())
        self.options_dict['NWEBtitle'] = unicode(self.title.get_text())
        self.options_dict['NWEBintronote'] = unicode(self.intro_note.get_handle())
        self.options_dict['NWEBhomenote'] = unicode(self.home_note.get_handle())
        self.options_dict['NWEBgraph'] = int(self.inc_graph.get_active())
        
        index = self.graph_gens.get_active()
        generations = 4
        if index >= 0:
            generations = int(self.graph_gens_options[index])
        self.options_dict['NWEBgraphgens'] = generations

        index = self.ext.get_active()
        if index >= 0:
            html_ext = self.ext_options[index]
        else:
            html_ext = "html"
        if html_ext[0] == '.':
            html_ext = html_ext[1:]
        self.options_dict['NWEBext'] = html_ext

        self.options_dict['NWEBencoding'] = self.encoding.get_handle()
        self.options_dict['NWEBcss'] = self.css.get_handle()
        self.options_dict['NWEBod'] = dialog.target_path
        self.options_dict['NWEBcopyright'] = self.copy.get_active()

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def make_default_style(self,default_style):
        """Make the default output style for the Web Pages Report."""
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportDialog(ReportDialog):

    HELP_TOPIC = "rep-web"

    def __init__(self,dbstate,uistate,person):
        self.database = dbstate.db
        self.person = person
        name = "navwebpage"
        translated_name = _("Generate Web Site")
        self.options = WebReportOptions(name,self.database)
        self.category = CATEGORY_WEB
        ReportDialog.__init__(self,dbstate,uistate,person,self.options,
                              name,translated_name)
        self.style_name = None

        while True:
            response = self.window.run()
            if response == gtk.RESPONSE_OK:
                self.make_report()
                break
            elif response != gtk.RESPONSE_HELP:
                break
        self.close()

    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
        self.options.handler.options_dict['NWEBarchive'] = int(
            self.archive.get_active())

    def parse_html_frame(self):
        pass
    
    def parse_paper_frame(self):
        pass
    
    def setup_html_frame(self):
        self.archive = gtk.CheckButton(_('Store web pages in .tar.gz archive'))
        self.archive.set_alignment(0.0,0.5)
        self.archive.set_active(
            self.options.handler.options_dict['NWEBarchive'])
        self.archive.connect('toggled',self.archive_toggle)
        self.add_option(None,self.archive)

    def archive_toggle(self,obj):
        if obj.get_active():
            # The .tar.gz box is on
            # Set doc label, mark file vs dir, add '.tar.gz' to the path
            self.target_fileentry.set_directory_entry(False)
            self.doc_label.set_label("%s:" % _("Filename"))
            fname = self.target_fileentry.get_full_path(0)
            if fname[-7:] != '.tar.gz':
                fname = fname + '.tar.gz'
                self.target_fileentry.set_filename(fname)
        else:
            # The .tar.gz box is off
            # Set doc label, mark dir vs file, remove '.tar.gz' from path
            self.target_fileentry.set_directory_entry(True)
            self.doc_label.set_label("%s:" % _("Directory"))
            fname = self.target_fileentry.get_full_path(0)
            if fname[-7:] == '.tar.gz':
                fname = fname[:-7]
                self.target_fileentry.set_filename(fname)

    def setup_paper_frame(self):
        pass

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Generate Web Site"),_("Web Page"))

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Target Directory")

    def get_target_is_directory(self):
        """This report creates a directory full of files, not a single file."""
        return 1
    
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return self.options.handler.options_dict['NWEBod']    

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass

    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame (NWEB only)"""
        pass
    
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        pass

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        pass

    def make_report(self):
        """Create the object that will produce the web pages."""

        try:
            MyReport = WebReport(self.database,self.person,
                                 self.options)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

def sort_people(db,handle_list):
    flist = set(handle_list)

    sname_sub = {}
    sortnames = {}
    cursor = db.get_person_cursor()
    node = cursor.first()
    while node:
        if node[0] in flist:
            primary_name = RelLib.Name()
            primary_name.unserialize(node[1][_NAME_COL])
            if primary_name.private:
                surname = _('Private')
                sortnames[node[0]] = _('Private')
            else:
                if primary_name.group_as:
                    surname = primary_name.group_as
                else:
                    surname = db.get_name_group_mapping(primary_name.surname)
                sortnames[node[0]] = _nd.sort_string(primary_name)
            if sname_sub.has_key(surname):
                sname_sub[surname].append(node[0])
            else:
                sname_sub[surname] = [node[0]]
        node = cursor.next()
    cursor.close()

    sorted_lists = []
    temp_list = sname_sub.keys()
    temp_list.sort(strcoll_case_sensitive)
    for name in temp_list:
        slist = map(lambda x: (sortnames[x],x),sname_sub[name])
        slist.sort(lambda x,y: strcoll_case_sensitive(x[0],y[0]))
        entries = map(lambda x: x[1], slist)
        sorted_lists.append((name,entries))
    return sorted_lists

def strcoll_case_sensitive(string1,string2):
    """ This function was written because string comparisons
        seem to be case insensitive if the string is longer than 
        one character. """
    if len(string1) > 0 and len(string2) > 0:
        diff = locale.strcoll(string1[0],string2[0])
    else:
        diff = 0

    if diff == 0:
        # If the first character is the same, compare the rest
        diff = locale.strcoll(string1,string2)
    return diff
        

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = CommandLineReport(database,name,category,WebReportOptions,
                            options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    MyReport = WebReport(database,clr.person,clr.option_class)
    MyReport.write_report()

#------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
#
#------------------------------------------------------------------------
class EmptyDoc:
    def __init__(self,styles,type,template,orientation,source=None):
        pass

    def init(self):
        pass

#-------------------------------------------------------------------------
#
# GrampsNoteComboBox
#
#-------------------------------------------------------------------------
class GrampsNoteComboBox(gtk.ComboBox):
    """
    Derived from the ComboBox, this widget provides handling of Report
    Styles.
    """

    def __init__(self,model=None,node=None):
        """
        Initializes the combobox, building the display column.
        """
        gtk.ComboBox.__init__(self,model)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        if node:
            self.set_active_iter(node)
        else:
            self.set_active(0)
        self.local_store = model

    def get_handle(self):
        """
        Returns the selected key (style sheet name).

        @returns: Returns the name of the selected style sheet
        @rtype: str
        """
        active = self.get_active_iter()
        handle = u""
        if active:
            handle = self.local_store.get_value(active,1)
        return handle

def mk_combobox(media_list,select_value):
    store = gtk.ListStore(str,str)
    node = None
    
    for data in media_list:
        if data[1] == select_value:
            node = store.append(row=data)
        else:
            store.append(row=data)
    widget = GrampsNoteComboBox(store,node)
    if len(media_list) == 0:
        widget.set_sensitive(False)
    return widget
    
def nameof(person,private):
    if person.private and private:
        return _("Private")
    else:
        return _nd.display(person)

def name_nameof(name,private):
    if name.private and private:
        return _("Private")
    else:
        return _nd.display_name(name)

def sort_nameof(person, private):
    if person.private and private:
        return _("Private")
    else:
        return _nd.sorted(person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'navwebpage',
    category = CATEGORY_WEB,
    report_class = WebReportDialog,
    options_class = cl_report,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Narrative Web Site"),
    status = _("Stable"),
    author_name="Donald N. Allingham",
    author_email="don@gramps-project.org",
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    )
