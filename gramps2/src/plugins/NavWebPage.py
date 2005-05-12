#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

"Web Site/Generate Web Site"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import shutil
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk
import gnome.ui

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import os
import RelLib
import const
import GrampsKeys
import GenericFilter
import Sort
import Report
import Errors
import Utils
from QuestionDialog import ErrorDialog
import ReportOptions
import BaseDoc
from NameDisplay import displayer as _nd
from DateHandler import displayer as _dd
import ReportUtils
import sets

_NARRATIVE = "narrative.css"

_css = [
    'BODY {\nfont-family: "Arial", "Helvetica", sans-serif;',
    'letter-spacing: 0.05em;\nbackground-color: #fafaff;',
    'color: #003;\n}',
    'P,BLOCKQUOTE {\nfont-size: 14px;\n}',
    'DIV {\nmargin: 2px;\npadding: 2px;\n}',
    'TD {\nvertical-align: top;\n}',
    'H1 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;\nfont-size: 160%;\nmargin: 2px;\n}\n',
    'H2 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;\nfont-style: italic;\nfont-size: 150%;\n}',
    'H3 {\nfont-weight: bold;\nmargin: 0;\npadding-top: 10px;',
    'padding-bottom: 10px;\ncolor: #336;\n}',
    'H4 {\nmargin-top: 1em;\nmargin-bottom: 0.3em;',
    'padding-left: 4px;\nbackground-color: #667;\ncolor: #fff;\n}',
    'H5 {\nmargin-bottom: 0.5em;\n}',
    'H6 {\nfont-weight: normal;\nfont-style: italic;',
    'font-size: 100%;\nmargin-left: 1em;\nmargin-top: 1.3em;',
    'margin-bottom: 0.8em;\n}',
    'HR {\nheight: 0;\nwidth: 0;\nmargin: 0;\nmargin-top: 1px;',
    'margin-bottom: 1px;\npadding: 0;\nborder-top: 0;',
    'border-color: #e0e0e9;\n}',
    'A:link {\ncolor: #006;\ntext-decoration: underline;\n}',
    'A:visited {\ncolor: #669;\ntext-decoration: underline;\n}',
    'A:hover {\nbackground-color: #eef;\ncolor: #000;',
    'text-decoration: underline;\n}',
    'A:active {\nbackground-color: #eef;\ncolor: #000;\ntext-decoration: none;\n}',
    '.navheader {\npadding: 4px;\nbackground-color: #e0e0e9;',
    'margin: 2px;\n}',
    '.navtitle {\nfont-size: 160%;\ncolor: #669;\nmargin: 2px;\n}',
    '.navbyline {\nfloat: right;\nfont-size: 14px;\nmargin: 2px;',
    'padding: 4px;\n}',
    '.nav {\nmargin: 0;\nmargin-bottom: 4px;\npadding: 0;',
    'font-size: 14px;\nfont-weight: bold;\n}',
    '.summaryarea {',
    'min-height: 100px;',
    'height: expression(document.body.clientHeight < 1 ? "100px" : "100px" );',
    '}',
    '.portrait {\njustify: center;\nmargin: 5px;\nmargin-right: 20px;',
    'padding: 3px;\nborder-color: #336;\nborder-width: 1px;\n}',
    '.snapshot {\nfloat: right;\nmargin: 5px;\nmargin-right: 20px;',
    'padding: 3px;\n}',
    '.thumbnail {\nheight: 100px;\nborder-color: #336;\nborder-width: 1px;\n}',
    '.leftwrap {\nfloat: left;\nmargin: 2px;\nmargin-right: 10px;\n}',
    '.rightwrap {\nfloat: right;\nmargin: 2px;\nmargin-left: 10px;\n}',
    'TABLE.infolist {\nborder: 0;\nfont-size: 14px;\n}',
    'TD.category {\npadding: 3px;\npadding-right: 3em;',
    'font-weight: bold;\n}',
    'TD.field {\npadding: 3px;\npadding-right: 3em;\n}',
    'TD.data {\npadding: 3px;\npadding-right: 3em;',
    'font-weight: bold;\n}',
    '.pedigree {\nmargin: 0;\nmargin-left: 2em;\npadding: 0;',
    'background-color: #e0e0e9;\nborder: 1px;\n}',
    '.pedigreeind {\nfont-size: 14px;\nmargin: 0;\npadding: 2em;',
    'padding-top: 0.25em;\npadding-bottom: 0.5em;\n}',
    '.footer {\nmargin: 1em;\nfont-size: 12px;\nfloat: right;\n}',
    ]


class BasePage:
    def __init__(self,title):
        self.title_str = title

    def lnkfmt(self,text):
        return text.replace(' ','%20')

    def display_footer(self,of):
        of.write('<br>\n')
        of.write('<br>\n')
        of.write('<hr>\n')
        of.write('<div class="footer">Generated by ')
        of.write('<a href="http://gramps.sourceforge.net">GRAMPS</a> ')
        of.write('on 13 December 2004.')
        of.write('</div>\n')
        of.write('</body>\n')
        of.write('</html>\n')
    
    def display_header(self,of,title,author=""):
        of.write('<!DOCTYPE HTML PUBLIC ')
        of.write('"-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        of.write('<html>\n<head>\n')
        of.write('<title>%s</title>\n' % self.title_str)
        of.write('<meta http-equiv="Content-Type" content="text/html; ')
        of.write('charset=ISO-8859-1">\n')
        of.write('<link href="%s" ' % _NARRATIVE)
        of.write('rel="stylesheet" type="text/css">\n')
        of.write('<link href="favicon.png" rel="Shortcut Icon">\n')
        of.write('</head>\n')
        of.write('<body>\n')
        of.write('<div class="navheader">\n')
        of.write('  <div class="navbyline">By: %s</div>\n' % author)
        of.write('  <h1 class="navtitle">%s</h1>\n' % self.title_str)
        of.write('  <hr>\n')
        of.write('    <div class="nav">\n')
        of.write('    <a href="index.html">Home</a> &nbsp;\n')
        of.write('    <a href="introduction.html">Introduction</a> &nbsp;\n')
        of.write('    <a href="surnames.html">Surnames</a> &nbsp;\n')
        of.write('    <a href="individuals.html">Individuals</a> &nbsp;\n')
        of.write('    <a href="sources.html">Sources</a> &nbsp;\n')
        of.write('    <a href="places.html">Places</a> &nbsp;\n')
        of.write('    <a href="download.html">Download</a> &nbsp;\n')
        of.write('    <a href="contact.html">Contact</a> &nbsp;\n')
        of.write('    </div>\n')
        of.write('  </div>\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualListPage(BasePage):

    def __init__(self, db, title, person_handle_list, html_dir):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"individuals.html")

        of = open(page_name, "w")
        self.display_header(of,_('Individuals'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Individuals'))
        of.write('<p>%s</p>\n' % _('Index of individuals, sorted by last name.'))
        of.write('<blockquote>\n')
        of.write('<table class="infolist" cellspacing="0" ')
        of.write('cellpadding="0" border="0">\n')
        of.write('<tr><td class="field"><u><b>%s</b></u></td>\n' % _('Surname'))
        of.write('<td class="field"><u><b>%s</b></u></td>\n' % _('Name'))
        of.write('</tr>\n')

        self.sort = Sort.Sort(db)
        person_handle_list.sort(self.sort.by_last_name)
        last_surname = ""
        
        for person_handle in person_handle_list:
            person = db.get_person_from_handle(person_handle)
            n = person.get_primary_name().get_surname()
            if n != last_surname:
                of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
            of.write('<tr><td class="category">')
            if n != last_surname:
                of.write('<a name="%s">%s</a>' % (self.lnkfmt(n),n))
            else:
                of.write('&nbsp')
            of.write('</td><td class="data">')
            of.write(person.get_primary_name().get_first_name())
            of.write(' <a href="%s.html">' % person.gramps_id)
            of.write("<sup>[%s]</sup>" % person.gramps_id)
            of.write('</a></td></tr>\n')
            last_surname = n
            
        of.write('</table>\n</blockquote>\n')
        self.display_footer(of)
        of.close()
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PlaceListPage(BasePage):

    def __init__(self, db, title, place_handles, html_dir, src_list):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"places.html")
        of = open(page_name, "w")
        self.display_header(of,_('Places'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Places'))
        of.write('<p>%s</p>\n' % _('Index of all the places in the '
                                      'project.'))

        of.write('<blockquote>\n')
        of.write('<table class="infolist" cellspacing="0" ')
        of.write('cellpadding="0" border="0">\n')
        of.write('<tr><td class="field"><u>')
        of.write('<b>%s</b></u></td>\n' % _('Letter'))
        of.write('<td class="field"><u>')
        of.write('<b>%s</b></u></td>\n' % _('Place'))
        of.write('</tr>\n')

        self.sort = Sort.Sort(db)
        handle_list = list(place_handles)
        handle_list.sort(self.sort.by_place_title)
        last_name = ""
        last_letter = ''
        
        for handle in handle_list:
            place = db.get_place_from_handle(handle)
            n = place.title

            if len(n) == 0:
                continue
            
            if n[0] != last_letter:
                last_letter = n[0]
                of.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
                of.write('<tr><td class="category">%s</td>' % last_letter)
                of.write('<td class="data">')
                of.write(n)
                of.write(' <sup><a href="%s.html">' % place.gramps_id)
                of.write('[%s]' % place.gramps_id)
                of.write('</a></sup></td></tr>')
            elif n != last_letter:
                last_surname = n
                of.write('<tr><td class="category">&nbsp;</td>')
                of.write('<td class="data">')
                of.write(n)
                of.write(' <sup><a href="%s">' % place.gramps_id)
                of.write('[%s]' % place.gramps_id)
                of.write('</a></sup></td></tr>')
            
        of.write('</table>\n</blockquote>\n')
        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SurnameListPage(BasePage):

    def __init__(self, db, title, person_handle_list, html_dir):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"surnames.html")

        of = open(page_name, "w")
        self.display_header(of,_('Surnames'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Surnames'))
        of.write('<p>%s</p>\n' % _('Index of all the surnames in the '
                                      'project. The links lead to a list '
                                      'of individuals in the database with '
                                      'this same surname.'))

        of.write('<blockquote>\n')
        of.write('<table class="infolist" cellspacing="0" ')
        of.write('cellpadding="0" border="0">\n')
        of.write('<tr><td class="field"><u>')
        of.write('<b>%s</b></u></td>\n' % _('Letter'))
        of.write('<td class="field"><u>')
        of.write('<b>%s</b></u></td>\n' % _('Surname'))
        of.write('</tr>\n')

        self.sort = Sort.Sort(db)
        person_handle_list.sort(self.sort.by_last_name)
        last_surname = ""
        last_letter = ''
        
        for person_handle in person_handle_list:
            person = db.get_person_from_handle(person_handle)
            n = person.get_primary_name().get_surname()

            if len(n) == 0:
                continue
            
            if n[0] != last_letter:
                last_letter = n[0]
                of.write('<tr><td class="category">%s</td>' % last_letter)
                of.write('<td class="data">')
                of.write('<a href="individuals.html#%s">' % self.lnkfmt(n))
                of.write(n)
                of.write('</a></td></tr>')
            elif n != last_surname:
                last_surname = n
                of.write('<tr><td class="category">&nbsp;</td>')
                of.write('<td class="data">')
                of.write('<a href="individuals.html#%s">' % self.lnkfmt(n))
                of.write(n)
                of.write('</a></td></tr>')
            
        of.write('</table>\n</blockquote>\n')
        self.display_footer(of)
        of.close()
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IntroductionPage(BasePage):

    def __init__(self, db, title, html_dir, note_id):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"introduction.html")

        of = open(page_name, "w")
        self.display_header(of,_('Introduction'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Introduction'))

        if note_id:
            obj = db.get_object_from_gramps_id(note_id)
            if not obj:
                print "%s object not found" % note_id
            else:
                note_obj = obj.get_note_object()
                text = note_obj.get()
                if note_obj.get_format():
                    of.write('<pre>\n%s\n</pre>\n' % text)
                else:
                    of.write('<p>')
                    of.write('</p><p>'.join(text.split('\n')))
                    of.write('</p>')

        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HomePage(BasePage):

    def __init__(self, db, title, html_dir, note_id):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"index.html")

        of = open(page_name, "w")
        self.display_header(of,_('Home'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Home'))

        if note_id:
            obj = db.get_object_from_gramps_id(note_id)

            if not obj:
                print "%s object not found" % note_id
            else:
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    newpath = obj.gramps_id + os.path.splitext(obj.get_path())[1]
                    shutil.copyfile(obj.get_path(),
                                    os.path.join(html_dir,newpath))
                    of.write('<div align="center">\n')
                    of.write('<img border="0" ')
                    of.write('src="%s" />' % newpath)
                    of.write('</div>\n')
    
                note_obj = obj.get_note_object()
                if note_obj:
                    text = note_obj.get()
                    if note_obj.get_format():
                        of.write('<pre>\n%s\n</pre>\n' % text)
                    else:
                        of.write('<p>')
                        of.write('</p><p>'.join(text.split('\n')))
                        of.write('</p>')

        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SourcesPage(BasePage):

    def __init__(self, db, title, handle_set, html_dir):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"sources.html")

        of = open(page_name, "w")
        self.display_header(of,_('Sources'),
                            db.get_researcher().get_name())

        handle_list = list(handle_set)

        of.write('<h3>%s</h3>\n<p>' % _('Sources'))
        of.write(_('All sources cited in the project.'))
        of.write('</p>\n<blockquote>\n<table class="infolist">\n')

        index = 1
        for handle in handle_list:
            of.write('<tr><td class="category">%d.</td>\n' % index)
            of.write('<td class="data">')
            of.write('</td></tr>\n')
            
        of.write('</table>\n<blockquote>\n')

        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DownloadPage(BasePage):

    def __init__(self, db, title, html_dir):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"download.html")

        of = open(page_name, "w")
        self.display_header(of,_('Download'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Download'))

        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ContactPage(BasePage):

    def __init__(self, db, title, html_dir):
        BasePage.__init__(self,title)
        page_name = os.path.join(html_dir,"contact.html")

        of = open(page_name, "w")
        self.display_header(of,_('Contact'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Contact'))

        self.display_footer(of)
        of.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage(BasePage):

    gender_map = {
        RelLib.Person.MALE    : const.male,
        RelLib.Person.FEMALE  : const.female,
        RelLib.Person.UNKNOWN : const.unknown,
        }
    
    def __init__(self, db, person, title, dirpath, ind_list,
                 place_list, src_list):
        BasePage.__init__(self,title)
        self.person = person
        self.db = db
        self.ind_list = ind_list
        self.dirpath = dirpath
        self.src_list = src_list
        self.place_list = place_list
        self.sort_name = _nd.sorted(self.person)
        self.name = _nd.sorted(self.person)
        
        of = open(os.path.join(dirpath,"%s.html" % person.gramps_id), "w")
        self.display_header(of, title,
                            self.db.get_researcher().get_name())
        self.display_ind_general(of)
        self.display_ind_events(of)
        self.display_ind_relationships(of)
        self.display_ind_narrative(of)
        self.display_ind_sources(of)
        self.display_ind_pedigree(of)
        self.display_footer(of)
        of.close()

    def display_ind_sources(self,of):
        sreflist = self.person.get_source_references()
        if not sreflist:
            return
        of.write('<h4>%s</h4>\n' % _('Sources'))
        of.write('<hr>\n')
        of.write('<table class="infolist" cellpadding="0" ')
        of.write('cellspacing="0" border="0">\n')

        index = 1
        for sref in sreflist:
            self.src_list.add(sref.get_base_handle())

            source = self.db.get_source_from_handle(sref.get_base_handle())
            author = source.get_author()
            title = source.get_title()
            publisher = source.get_publication_info()
            date = _dd.display(sref.get_date_object())
            of.write('<tr><td class="field">%d. ' % index)
            values = []
            if author:
                values.append(author)
            if title:
                values.append(title)
            if publisher:
                values.append(publisher)
            if date:
                values.append(date)
            of.write(', '.join(values))
            of.write('</td></tr>\n')
        of.write('</table>\n')

    def display_ind_pedigree(self,of):

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            (parent_handle, mrel,frel) = parent_handle_list[0]
            family = self.db.get_family_from_handle(parent_handle)
            father_id = family.get_father_handle()
            mother_id = family.get_mother_handle()
            mother = self.db.get_person_from_handle(mother_id)
            father = self.db.get_person_from_handle(father_id)
        else:
            family = None
            father = None
            mother = None
        
        of.write('<h4>%s</h4>\n' % _('Pedigree'))
        of.write('<hr>\n<br>\n')
        of.write('<table class="pedigree">\n')
        of.write('<tr><td>\n')
        if father or mother:
            of.write('<blockquote class="pedigreeind">\n')
            if father:
                self.pedigree_person(of,father)
            if mother:
                self.pedigree_person(of,mother)
        of.write('<blockquote class="pedigreeind">\n')
        if family:
            for child_handle in family.get_child_handle_list():
                if child_handle == self.person.handle:
                    of.write('| <strong>%s</strong><br>\n' % self.name)
                    self.pedigree_family(of)
                else:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(of,child)
        else:
            of.write('| <strong>%s</strong><br>\n' % self.name)
            self.pedigree_family(of)

        of.write('</blockquote>\n')
        if father or mother:
            of.write('</blockquote>\n')
        of.write('</td>\n</tr>\n</table>\n')


    def display_ind_general(self,of):
        photolist = self.person.get_media_list()
        if photolist:
            photo_handle = photolist[0].get_reference_handle()
            photo = self.db.get_object_from_handle(photo_handle)
            
            newpath = self.person.gramps_id + os.path.splitext(photo.get_path())[1]
            shutil.copyfile(photo.get_path(),os.path.join(self.dirpath,newpath))
            of.write('<div class="snapshot">\n')
            of.write('<a href="%s">' % newpath)
            of.write('<img class="thumbnail"  border="0" src="%s" ' % newpath)
            of.write('height="100"></a>')
            of.write('</div>\n')

        of.write('<div class="summaryarea">\n')
        of.write('<h3>%s</h3>\n' % self.sort_name)
        of.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        of.write('border="0">\n')

        # Gender
        of.write('<tr><td class="field">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        of.write('<td class="data">%s</td>\n' % gender)
        of.write('</tr>\n')

        # Birth
        handle = self.person.get_birth_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            of.write('<tr><td class="field">%s</td>\n' % _('Birth'))
            of.write('<td class="data">%s</td>\n' % self.format_event(event))
            of.write('</tr>\n')

        # Death
        handle = self.person.get_death_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            of.write('<tr><td class="field">%s</td>\n' % _('Death'))
            of.write('<td class="data">%s</td>\n' % self.format_event(event))
            of.write('</tr>\n')

        of.write('</table>\n')
        of.write('</div>\n')

    def display_ind_events(self,of):
        of.write('<h4>%s</h4>\n' % _('Events'))
        of.write('<hr>\n')
        of.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        of.write('border="0">\n')

        for event_id in self.person.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            of.write('<tr><td class="field">%s</td>\n' % event.get_name())
            of.write('<td class="data">\n')
            of.write(self.format_event(event))
            of.write('</td>\n')
            of.write('</tr>\n')

        of.write('</table>\n')

    def display_ind_narrative(self,of):
        of.write('<h4>%s</h4>\n' % _('Narrative'))
        of.write('<hr>\n')

        noteobj = self.person.get_note_object()
        if noteobj:
            format = noteobj.get_format()
            text = noteobj.get()

            if format:
                text = "<pre>" + "<br>".join(text.split("\n"))
            else:
                text = "</p><p>".join(text.split("\n"))
            of.write('<p>%s</p>\n' % text)

        
    def display_parent(self,of,handle,title):
        use_link = handle in self.ind_list
        person = self.db.get_person_from_handle(handle)
        of.write('<td class="field">%s</td>\n' % title)
        of.write('<td class="data">')
        of.write(_nd.display(person))
        if use_link:
            val = person.gramps_id
            of.write('&nbsp;<sup><a href="%s.html">[%s]</a></sup>' % (val,val))
        of.write('</td>\n')

    def display_ind_relationships(self,of):
        parent_list = self.person.get_parent_family_handle_list()
        family_list = self.person.get_family_handle_list()

        if not parent_list and not family_list:
            return
        
        of.write('<h4>%s</h4>\n' % _("Relationships"))
        of.write('<hr>\n')
        of.write('<table class="infolist" cellpadding="0" ')
        of.write('cellspacing="0" border="0">\n')

        if parent_list:
            for (family_handle,mrel,frel) in parent_list:
                family = self.db.get_family_from_handle(family_handle)
                
                of.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
                of.write('<tr><td class="category">%s</td>\n' % _("Parents"))

                father_handle = family.get_father_handle()
                if father_handle:
                    self.display_parent(of,father_handle,_('Father'))
                of.write('</tr><tr><td>&nbsp;</td>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.display_parent(of,mother_handle,_('Mother'))
                of.write('</tr>\n')
            of.write('<tr><td colspan="3">&nbsp;</td></tr>\n')

        if family_list:
            of.write('<tr><td class="category">%s</td>\n' % _("Spouses"))
            first = True
            for family_handle in family_list:
                family = self.db.get_family_from_handle(family_handle)
                self.display_spouse(of,family,first)
                first = False
                childlist = family.get_child_handle_list()
                if childlist:
                    of.write('<tr><td>&nbsp;</td>\n')
                    of.write('<td class="field">%s</td>\n' % _("Children"))
                    of.write('<td class="data">\n')
                    for child_handle in childlist:
                        use_link = child_handle in self.ind_list
                        child = self.db.get_person_from_handle(child_handle)
                        if use_link:
                            of.write('<a href="%s.html">' % child.get_gramps_id())
                        of.write(_nd.display(child))
                        if use_link:
                            of.write('</a>\n')
                        of.write("<br>\n")
                    of.write('</td>\n</tr>\n')
        of.write('</table>\n')

    def display_spouse(self,of,family,first=True):
        gender = self.person.get_gender()
        reltype = family.get_relationship()

        if reltype == RelLib.Family.MARRIED:
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
            name = _nd.display(spouse)
        else:
            name = _("unknown")
        if not first:
            of.write('<tr><td>&nbsp;</td></tr>\n')
            of.write('<td>&nbsp;</td>')
        of.write('<td class="field">%s</td>\n' % relstr)
        of.write('<td class="data">')
        use_link = spouse_id in self.ind_list
        if use_link:
            of.write('<a href="%s.html">' % spouse.get_gramps_id())
        of.write(name)
        if use_link:
            of.write('</a>')
        
        of.write('</td>\n</tr>\n')

        for event_id in family.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            of.write('<tr><td>&nbsp;</td>\n')
            of.write('<td class="field">%s</td>\n' % event.get_name())
            of.write('<td class="data">\n')
            of.write(self.format_event(event))
            of.write('</td>\n</tr>\n')

    def pedigree_person(self,of,person,bullet='|'):
        person_link = person.handle in self.ind_list
        of.write('%s ' % bullet)
        if person_link:
            of.write('<a href="%s.html">' % person.gramps_id)
        of.write(_nd.display(person))
        if person_link:
            of.write('</a>')
        of.write('<br>\n')

    def pedigree_family(self,of):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                self.pedigree_person(of,spouse,'&bull;')
            childlist = rel_family.get_child_handle_list()
            if childlist:
                of.write('<blockquote class="pedigreeind">\n')
                for child_handle in childlist:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(of,child)
                of.write('</blockquote>\n')

    def format_event(self,event):
        descr = event.get_description()
        place_handle = event.get_place_handle()
        if place_handle:
            self.place_list.add(place_handle)
        place = ReportUtils.place_name(self.db,place_handle)

        date = _dd.display(event.get_date_object())
        tmap = {'description' : descr, 'date' : date, 'place' : place}
        
        if descr and date and place:
            text = _('%(description)s, &nbsp;&nbsp; %(date)s &nbsp;&nbsp; at &nbsp&nbsp; %(place)s') % tmap
        elif descr and date:
            text = _('%(description)s, &nbsp;&nbsp; %(date)s &nbsp;&nbsp;') % tmap
        elif descr:
            text = descr
        elif date and place:
            text = _('%(date)s &nbsp;&nbsp; at &nbsp&nbsp; %(place)s') % tmap
        elif date:
            text = date
        elif place:
            text = place
        else:
            text = '\n'
        return text
            
#------------------------------------------------------------------------
#
# WebReport
#
#------------------------------------------------------------------------
class WebReport(Report.Report):
    def __init__(self,database,person,options_class):
        """
        Creates WebReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter
        od
        HTMLimg
        HTMLrestrictinfo
        HTMLincpriv
        HTMLnotxtsi
        HTMLlnktoalphabet
        HTMLsplita
        HTMLplaceidx
        HTMLshorttree
        HTMLidxcol
        HTMLimagedir
        HTMLincid
        HTMLidurl
        HTMLlinktidx
        HTMLext
        HTMLtreed
        HTMLidxt
        HTMLidxbirth
        HTMLintronote
        HTMLhomenote
        yearso
        """
        self.database = database
        self.start_person = person
        self.options_class = options_class

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(GenericFilter.CustomFilters.get_filters())
        self.filter = filters[filter_num]
        self.template_name = options_class.handler.template_name

        self.target_path = options_class.handler.options_dict['HTMLod']
        self.ext = options_class.handler.options_dict['HTMLext']
        self.id_link = options_class.handler.options_dict['HTMLlinktidx']
        self.photos = options_class.handler.options_dict['HTMLimg']
        self.restrict = options_class.handler.options_dict['HTMLrestrictinfo']
        self.private = options_class.handler.options_dict['HTMLincpriv']
        self.srccomments = options_class.handler.options_dict['HTMLcmtxtsi']
        self.image_dir = options_class.handler.options_dict['HTMLimagedir']
        self.title = options_class.handler.options_dict['HTMLtitle']
        self.separate_alpha = options_class.handler.options_dict['HTMLsplita']
        self.depth = options_class.handler.options_dict['HTMLtreed']
        self.intro_id = options_class.handler.options_dict['HTMLintronote']
        self.home_id = options_class.handler.options_dict['HTMLhomenote']
        self.sort = Sort.Sort(self.database)

    def get_progressbar_data(self):
        return (_("Generate HTML reports - GRAMPS"),
                '<span size="larger" weight="bold">%s</span>' %
                _("Creating Web Pages"))

    def write_report(self):
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

        if self.image_dir:
            image_dir_name = os.path.join(dir_name, self.image_dir)
        else:
            image_dir_name = dir_name
        if not os.path.isdir(image_dir_name) and self.photos != 0:
            try:
                os.mkdir(image_dir_name)
            except IOError, value:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name + "\n" + value[1])
                return
            except:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name)
                return

        ind_list = self.database.get_person_handles(sort_handles=False)
        ind_list = self.filter.apply(self.database,ind_list)
        progress_steps = len(ind_list)
        if len(ind_list) > 1:
            progress_steps = progress_steps+1
        progress_steps = progress_steps+1
        self.progress_bar_setup(float(progress_steps))

        self.write_css(dir_name)

        HomePage(self.database,self.title,dir_name,self.home_id)
        ContactPage(self.database,self.title,dir_name)
        DownloadPage(self.database,self.title,dir_name)
        
        IntroductionPage(self.database,self.title,dir_name,
                         self.intro_id)
        
        place_list = sets.Set()
        source_list = sets.Set()

        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            if not self.private:
                person = ReportUtils.sanitize_person(self.database,person)
                
            idoc = IndividualPage(self.database, person, self.title,
                                  dir_name, ind_list, place_list, source_list)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
            
        if len(ind_list) > 1:
            IndividualListPage(self.database, self.title, ind_list, dir_name)
            SurnameListPage(self.database, self.title, ind_list, dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()

        PlaceListPage(self.database, self.title, place_list,
                      dir_name, source_list)
        SourcesPage(self.database,self.title, source_list, dir_name)
        self.progress_bar_done()

    def write_css(self,dir_name):
        f = open(os.path.join(dir_name,_NARRATIVE), "w")
        f.write('\n'.join(_css))
        f.close()
                 
    def add_styles(self,doc):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'HTMLod'            : '',
            'HTMLimg'           : 2,
            'HTMLrestrictinfo'  : 0,
            'HTMLincpriv'       : 0,
            'HTMLcmtxtsi'       : 0, 
            'HTMLlnktoalphabet' : 0, 
            'HTMLsplita'        : 0, 
            'HTMLshorttree'     : 1,
            'HTMLimagedir'      : 'images', 
            'HTMLtitle'         : 'My Family Tree', 
            'HTMLincid'         : 0,
            'HTMLidurl'         : '',
            'HTMLlinktidx'      : 1,
            'HTMLext'           : 'html',
            'HTMLtreed'         : 3,
            'HTMLidxt'          : '',
            'HTMLintronote'     : '',
            'HTMLhomenote'      : '',
            'HTMLidxbirth'      : 0,
            'HTMLplaceidx'      : 0,
            'HTMLyearso'        : 1,
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
            handle = person.get_handle()
        else:
            name = 'PERSON'
            handle = ''

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([handle,1]))

        df = GenericFilter.GenericFilter()
        df.set_name(_("Descendant Families of %s") % name)
        df.add_rule(GenericFilter.IsDescendantFamilyOf([handle]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([handle,1]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([handle]))

        return [all,des,df,ans,com]

    def add_user_options(self,dialog):
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        no_img_msg = _("Do not use images")
        no_limg_msg = _("Do not use images for living people")
        no_com_msg = _("Do not include comments and text in source information")
        imgdir_msg = _("Image subdirectory")
        title_msg = _("Web site title")
        ext_msg = _("File extension")
        sep_alpha_msg = _("Split alphabetical sections to separate pages")
        tree_msg = _("Include short ancestor tree")

        self.no_private = gtk.CheckButton(priv_msg)
        self.no_private.set_active(not self.options_dict['HTMLincpriv'])

        self.restrict_living = gtk.CheckButton(restrict_msg)
        self.restrict_living.set_active(self.options_dict['HTMLrestrictinfo'])

        # FIXME: document this:
        # 0 -- no images of any kind
        # 1 -- no living images, but some images
        # 2 -- any images
        images = self.options_dict['HTMLimg']
        self.no_images = gtk.CheckButton(no_img_msg)
        self.no_images.set_active(not images)

        self.no_living_images = gtk.CheckButton(no_limg_msg)
        self.no_living_images.set_sensitive(not images)
        self.no_living_images.set_active(images in (0,1))

        self.no_comments = gtk.CheckButton(no_com_msg)
        self.no_comments.set_active(not self.options_dict['HTMLcmtxtsi'])

        self.imgdir = gtk.Entry()
        self.imgdir.set_text(self.options_dict['HTMLimagedir'])

        self.intro_note = gtk.Entry()
        self.intro_note.set_text(self.options_dict['HTMLintronote'])

        self.home_note = gtk.Entry()
        self.home_note.set_text(self.options_dict['HTMLhomenote'])

        self.title = gtk.Entry()
        self.title.set_text(self.options_dict['HTMLtitle'])

        self.linkpath = gtk.Entry()
        self.linkpath.set_sensitive(self.options_dict['HTMLincid'])
        self.linkpath.set_text(self.options_dict['HTMLidurl'])

        self.ext = gtk.combo_box_new_text()
        ext_options = ['.html','.htm','.shtml','.php','.php3','.cgi']
        for text in ext_options:
            self.ext.append_text(text)

        def_ext = "." + self.options_dict['HTMLext']
        self.ext.set_active(ext_options.index(def_ext))

        dialog.add_option(title_msg,self.title)
        dialog.add_option(imgdir_msg,self.imgdir)
        dialog.add_option(ext_msg,self.ext)

        title = _("Text")
        dialog.add_frame_option(title,_('Home Note ID'),
                                self.home_note)
        dialog.add_frame_option(title,_('Introduction Note ID'),
                                self.intro_note)

        title = _("Privacy")
        dialog.add_frame_option(title,None,self.no_private)
        dialog.add_frame_option(title,None,self.restrict_living)
        dialog.add_frame_option(title,None,self.no_images)
        dialog.add_frame_option(title,None,self.no_living_images)
        dialog.add_frame_option(title,None,self.no_comments)
        self.no_images.connect('toggled',self.on_nophotos_toggled)

    def parse_user_options(self,dialog):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        
        self.options_dict['HTMLrestrictinfo'] = int(self.restrict_living.get_active())
        self.options_dict['HTMLincpriv'] = int(not self.no_private.get_active())
        self.options_dict['HTMLimagedir'] = unicode(self.imgdir.get_text())
        self.options_dict['HTMLtitle'] = unicode(self.title.get_text())
        self.options_dict['HTMLintronote'] = unicode(self.intro_note.get_text())
        self.options_dict['HTMLhomenote'] = unicode(self.home_note.get_text())

        #html_ext = unicode(self.ext.entry.get_text().strip())
        html_ext = ".html"
        if html_ext[0] == '.':
            html_ext = html_ext[1:]
        self.options_dict['HTMLext'] = html_ext

        self.options_dict['HTMLidurl'] = unicode(self.linkpath.get_text().strip())

        self.options_dict['HTMLcmtxtsi'] = int(not self.no_comments.get_active())
        if self.no_images.get_active():
            photos = 0
        elif self.no_living_images.get_active():
            photos = 1
        else:
            photos = 2
        self.options_dict['HTMLimg'] = photos
        self.options_dict['HTMLod'] = dialog.target_path

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def show_link(self,obj):
        self.linkpath.set_sensitive(obj.get_active())

    def on_nophotos_toggled(self,obj):
        """Keep the 'restrict photos' checkbox in line with the 'no
        photos' checkbox.  If there are no photos included, it makes
        no sense to worry about restricting which photos are included,
        now does it?"""
        self.no_living_images.set_sensitive(not obj.get_active())

    def make_default_style(self,default_style):
        """Make the default output style for the Web Pages Report."""
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportDialog(Report.ReportDialog):

    def __init__(self,database,person):
        self.database = database 
        self.person = person
        name = "navwebpage"
        translated_name = _("Generate Web Site")
        self.options_class = WebReportOptions(name)
        self.category = const.CATEGORY_WEB
        Report.ReportDialog.__init__(self,database,person,self.options_class,
                                    name,translated_name)
        self.style_name = None

        response = self.window.run()
        if response == gtk.RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.window.destroy()

    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
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
        return self.options_class.handler.options_dict['HTMLod']    

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass

    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame (HTML only)"""
        pass
    
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        self.output_notebook.set_current_page(1)

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        pass
    
    def make_report(self):
        """Create the object that will produce the web pages."""

        try:
            MyReport = WebReport(self.database,self.person,
                                 self.options_class)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = Report.CommandLineReport(database,name,category,WebReportOptions,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    try:
        MyReport = WebReport(database,clr.person,clr.option_class)
        MyReport.write_report()
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

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
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_report
register_report(
    name = 'navwebpage',
    category = const.CATEGORY_WEB,
    report_class = WebReportDialog,
    options_class = cl_report,
    modes = Report.MODE_GUI | Report.MODE_CLI,
    translated_name = _("Narrative Web Site"),
    status=(_("Beta")),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    )
