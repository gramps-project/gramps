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
    'font-weight: bolder;\nfont-size:	160%;\nmargin: 2px;\n}\n',
    'H2 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;\nfont-style: italic;\nfont-size: 150%;\n}',
    'H3 {\nfont-weight: bold;\nmargin: 0;\npadding-top: 10px;',
    'padding-bottom: 10px;\ncolor: #336;\n}',
    'H4 {\nmargin-top: 1em;\nmargin-bottom: 0.3em;',
    'padding-left: 4px;\nbackground-color: #667;\ncolor: #fff;\n}',
    'H5 {\nmargin-bottom: 0.5em;\n}',
    'H6 {\nfont-weight: normal;\nfont-style: italic;',
    'font-size:	100%;\nmargin-left: 1em;\nmargin-top: 1.3em;',
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
    def __init__(self):
        pass

    def lnkfmt(self,text):
        return text.replace(' ','%20')

    def display_footer(self,ofile):
	ofile.write('<br>\n')
	ofile.write('<br>\n')
	ofile.write('<hr>\n')
	ofile.write('<div class="footer">')
        ofile.write('Generated by <a href="http://gramps.sourceforge.net">GRAMPS</a> on 13 December 2004.')
        ofile.write('</div>\n')
        ofile.write('</body>\n')
        ofile.write('</html>\n')
    
    def display_header(self,ofile,title,author=""):
        ofile.write('<!DOCTYPE HTML PUBLIC ')
        ofile.write('"-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        ofile.write('<html>\n')
        ofile.write('<head>\n')
	ofile.write('<title>My Family Tree</title>\n')
	ofile.write('<meta http-equiv="Content-Type" content="text/html; ')
        ofile.write('charset=ISO-8859-1">\n')
	ofile.write('<link href="%s" ' % _NARRATIVE)
        ofile.write('rel="stylesheet" type="text/css">\n')
	ofile.write('<link href="favicon.png" rel="Shortcut Icon">\n')
        ofile.write('</head>\n')
        ofile.write('<body>\n')
	ofile.write('<div class="navheader">\n')
        ofile.write('  <div class="navbyline">By: %s</div>\n' % author)
        ofile.write('  <h1 class="navtitle">%s</h1>\n' % title)
        ofile.write('  <hr>\n')
        ofile.write('    <div class="nav">\n')
        ofile.write('    <a href="index.html">Home</a> &nbsp;\n')
        ofile.write('    <a href="introduction.html">Introduction</a> &nbsp;\n')
        ofile.write('    <a href="surnames.html">Surnames</a> &nbsp;\n')
        ofile.write('    <a href="individuals.html">Individuals</a> &nbsp;\n')
        ofile.write('    <a href="sources.html">Sources</a> &nbsp;\n')
        ofile.write('    <a href="download.html">Download</a> &nbsp;\n')
        ofile.write('    <a href="contact.html">Contact</a> &nbsp;\n')
        ofile.write('    </div>\n')
	ofile.write('  </div>\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualListPage(BasePage):

    def __init__(self, db, person_handle_list, html_dir):
        page_name = os.path.join(html_dir,"individuals.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Individuals'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Individuals'))
        ofile.write('<p>%s</p>\n' % _('Index of individuals, sorted by last name.'))
	ofile.write('<blockquote>\n')
	ofile.write('<table class="infolist" cellspacing="0" ')
        ofile.write('cellpadding="0" border="0">\n')
	ofile.write('<tr><td class="field"><u><b>Surname</b></u></td>\n')
        ofile.write('<td class="field"><u><b>Name</b></u></td>\n')
        ofile.write('</tr>\n')

        self.sort = Sort.Sort(db)
        person_handle_list.sort(self.sort.by_last_name)
        last_surname = ""
        
        for person_handle in person_handle_list:
            person = db.get_person_from_handle(person_handle)
            n = person.get_primary_name().get_surname()
            if n != last_surname:
                ofile.write('<tr><td colspan="2">&nbsp;</td></tr>\n')
            ofile.write('<tr><td class="category">')
            if n != last_surname:
                ofile.write('<a name="%s">%s</a>' % (self.lnkfmt(n),n))
            else:
                ofile.write('&nbsp')
            ofile.write('</td><td class="data">')
            ofile.write(person.get_primary_name().get_first_name())
            ofile.write(' <a href="%s.html">' % person.gramps_id)
            ofile.write("<sup>[%s]</sup>" % person.gramps_id)
            ofile.write('</a></td></tr>\n')
            last_surname = n
            
        ofile.write('</table>\n</blockquote>\n')
        self.display_footer(ofile)
        ofile.close()
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SurnameListPage(BasePage):

    def __init__(self, db, person_handle_list, html_dir):
        page_name = os.path.join(html_dir,"surnames.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Surnames'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Surnames'))
        ofile.write('<p>%s</p>\n' % _('Index of all the surnames in the '
                                      'project. The links lead to a list '
                                      'of individuals in the database with '
                                      'this same surname.'))

	ofile.write('<blockquote>\n')
	ofile.write('<table class="infolist" cellspacing="0" ')
        ofile.write('cellpadding="0" border="0">\n')
	ofile.write('<tr><td class="field"><u>')
        ofile.write('<b>%s</b></u></td>\n' % _('Surname'))
        ofile.write('<td class="field"><u>')
        ofile.write('<b>%s</b></u></td>\n' % _('Name'))
        ofile.write('</tr>\n')

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
                ofile.write('<tr><td class="category">%s</td>' % last_letter)
                ofile.write('<td class="data">')
                ofile.write('<a href="individuals.html#%s">' % self.lnkfmt(n))
                ofile.write(n)
                ofile.write('</a></td></tr>')
            elif n != last_surname:
                last_surname = n
                ofile.write('<tr><td class="category">&nbsp;</td>')
                ofile.write('<td class="data">')
                ofile.write('<a href="individuals.html#%s">' % self.lnkfmt(n))
                ofile.write(n)
                ofile.write('</a></td></tr>')
            
        ofile.write('</table>\n</blockquote>\n')
        self.display_footer(ofile)
        ofile.close()
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IntroductionPage(BasePage):

    def __init__(self, db, html_dir):
        page_name = os.path.join(html_dir,"introduction.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Introduction'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Introduction'))

        self.display_footer(ofile)
        ofile.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HomePage(BasePage):

    def __init__(self, db, html_dir):
        page_name = os.path.join(html_dir,"index.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Home'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Home'))

        self.display_footer(ofile)
        ofile.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SourcesPage(BasePage):

    def __init__(self, db, html_dir):
        page_name = os.path.join(html_dir,"sources.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Sources'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Sources'))

        self.display_footer(ofile)
        ofile.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DownloadPage(BasePage):

    def __init__(self, db, html_dir):
        page_name = os.path.join(html_dir,"download.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Download'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Download'))

        self.display_footer(ofile)
        ofile.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ContactPage(BasePage):

    def __init__(self, db, html_dir):
        page_name = os.path.join(html_dir,"contact.html")

        ofile = open(page_name, "w")
        self.display_header(ofile,_('Contact'),
                            db.get_researcher().get_name())

	ofile.write('<h3>%s</h3>\n' % _('Contact'))

        self.display_footer(ofile)
        ofile.close()

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
    
    def __init__(self, db, person, dirpath, ind_list):
        self.person = person
        self.db = db
        self.ind_list = ind_list
        self.dirpath = dirpath

        gramps_id = self.person.get_gramps_id()
        self.sort_name = _nd.sorted(self.person)
        self.name = _nd.sorted(self.person)
        
        ofile = open(os.path.join(dirpath,"%s.html" % gramps_id), "w")
        self.display_header(ofile, 'My Family Tree',
                            self.db.get_researcher().get_name())
        self.display_ind_general(ofile)
        self.display_ind_events(ofile)
        self.display_ind_relationships(ofile)
        self.display_ind_narrative(ofile)
        self.display_ind_sources(ofile)
        self.display_ind_pedigree(ofile)
        self.display_footer(ofile)
        ofile.close()

    def display_ind_sources(self,ofile):
        sreflist = self.person.get_source_references()
        if not sreflist:
            return
	ofile.write('<h4>%s</h4>\n' % _('Sources'))
	ofile.write('<hr>\n')
	ofile.write('<table class="infolist" cellpadding="0" ')
        ofile.write('cellspacing="0" border="0">\n')

        index = 1
        for sref in sreflist:
            source = self.db.get_source_from_handle(sref.get_base_handle())
            author = source.get_author()
            title = source.get_title()
            publisher = source.get_publication_info()
            date = _dd.display(sref.get_date())
            ofile.write('<tr><td class="field">%d. ' % index)
            values = []
            if author:
                values.append(author)
            if title:
                values.append(title)
            if publisher:
                values.append(publisher)
            if date:
                values.append(date)
            ofile.write(', '.join(values))
            ofile.write('</td></tr>\n')
	ofile.write('</table>\n')

    def display_ind_pedigree(self,ofile):

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
        
        ofile.write('<h4>%s</h4>\n' % _('Pedigree'))
	ofile.write('<hr>\n<br>\n')
	ofile.write('<table class="pedigree">\n')
        ofile.write('<tr><td>\n')
        if father or mother:
            ofile.write('<blockquote class="pedigreeind">\n')
            if father:
                self.pedigree_person(ofile,father)
            if mother:
                self.pedigree_person(ofile,mother)
        ofile.write('<blockquote class="pedigreeind">\n')
        if family:
            for child_handle in family.get_child_handle_list():
                if child_handle == self.person.handle:
                    ofile.write('| <strong>%s</strong><br>\n' % self.name)
                    self.pedigree_family(ofile)
                else:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(ofile,child)
        else:
            ofile.write('| <strong>%s</strong><br>\n' % self.name)
            self.pedigree_family(ofile)

        ofile.write('</blockquote>\n')
        if father or mother:
            ofile.write('</blockquote>\n')
        ofile.write('</td>\n</tr>\n</table>\n')


    def display_ind_general(self,ofile):
        photolist = self.person.get_media_list()
        if photolist:
            photo_handle = photolist[0].get_reference_handle()
            photo = self.db.get_object_from_handle(photo_handle)
            
            newpath = self.person.gramps_id + os.path.splitext(photo.get_path())[1]
            shutil.copyfile(photo.get_path(),os.path.join(self.dirpath,newpath))
            ofile.write('<div class="snapshot">\n')
            ofile.write('<a href="%s">' % newpath)
            ofile.write('<img class="thumbnail"  border="0" src="%s" ' % newpath)
            ofile.write('height="100"></a>')
            ofile.write('</div>\n')

	ofile.write('<div class="summaryarea">\n')
        ofile.write('<h3>%s</h3>\n' % self.sort_name)
        ofile.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        ofile.write('border="0">\n')

        # Gender
        ofile.write('<tr><td class="field">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        ofile.write('<td class="data">%s</td>\n' % gender)
        ofile.write('</tr>\n')

        # Gramps ID
        ofile.write('<tr><td class="field">%s</td>\n' % _('GRAMPS ID'))
        ofile.write('<td class="data">%s</td>\n' % self.person.gramps_id)
        ofile.write('</tr>\n')

        # Birth
        handle = self.person.get_birth_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            ofile.write('<tr><td class="field">%s</td>\n' % _('Birth'))
            ofile.write('<td class="data">%s</td>\n' % self.format_event(event))
            ofile.write('</tr>\n')

        # Death
        handle = self.person.get_death_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            ofile.write('<tr><td class="field">%s</td>\n' % _('Death'))
            ofile.write('<td class="data">%s</td>\n' % self.format_event(event))
            ofile.write('</tr>\n')

        ofile.write('</table>\n')
	ofile.write('</div>\n')

    def display_ind_events(self,ofile):
	ofile.write('<h4>%s</h4>\n' % _('Events'))
	ofile.write('<hr>\n')
	ofile.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        ofile.write('border="0">\n')

        for event_id in self.person.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            ofile.write('<tr><td class="field">%s</td>\n' % event.get_name())
            ofile.write('<td class="data">\n')
            ofile.write(self.format_event(event))
            ofile.write('</td>\n')
            ofile.write('</tr>\n')

	ofile.write('</table>\n')

    def display_ind_narrative(self,ofile):
	ofile.write('<h4>%s</h4>\n' % _('Narrative'))
	ofile.write('<hr>\n')

        noteobj = self.person.get_note_object()
        if noteobj:
            format = noteobj.get_format()
            text = noteobj.get()

            if format:
                text = "<pre>" + "<br>".join(text.split("\n"))
            else:
                text = "</p><p>".join(text.split("\n"))
            ofile.write('<p>%s</p>\n' % text)

        
    def display_parent(self,ofile,handle,title):
        use_link = handle in self.ind_list
        person = self.db.get_person_from_handle(handle)
        ofile.write('<td class="field">%s</td>\n' % title)
        ofile.write('<td class="data">')
        ofile.write(_nd.display(person))
        if use_link:
            val = person.gramps_id
            ofile.write('&nbsp;<sup><a href="%s.html">[%s]</a></sup>' % (val,val))
        ofile.write('</td>\n')

    def display_ind_relationships(self,ofile):
        parent_list = self.person.get_parent_family_handle_list()
        family_list = self.person.get_family_handle_list()

        if not parent_list and not family_list:
            return
        
	ofile.write('<h4>%s</h4>\n' % _("Relationships"))
	ofile.write('<hr>\n')
	ofile.write('<table class="infolist" cellpadding="0" cellspacing="0" border="0">\n')

        if parent_list:
            for (family_handle,mrel,frel) in parent_list:
                family = self.db.get_family_from_handle(family_handle)
                
                ofile.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
                ofile.write('<tr><td class="category">%s</td>\n' % _("Parents"))

                father_handle = family.get_father_handle()
                if father_handle:
                    self.display_parent(ofile,father_handle,_('Father'))
                ofile.write('</tr><tr><td>&nbsp;</td>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.display_parent(ofile,mother_handle,_('Mother'))
                ofile.write('</tr>\n')
            ofile.write('<tr><td colspan="3">&nbsp;</td></tr>\n')

        if family_list:
            ofile.write('<tr><td class="category">%s</td>\n' % _("Spouses"))
            first = True
            for family_handle in family_list:
                family = self.db.get_family_from_handle(family_handle)
                self.display_spouse(ofile,family,first)
                first = False
                childlist = family.get_child_handle_list()
                if childlist:
                    ofile.write('<tr><td>&nbsp;</td>\n')
                    ofile.write('<td class="field">%s</td>\n' % _("Children"))
                    ofile.write('<td class="data">\n')
                    for child_handle in childlist:
                        use_link = child_handle in self.ind_list
                        child = self.db.get_person_from_handle(child_handle)
                        if use_link:
                            ofile.write('<a href="%s.html">' % child.get_gramps_id())
                        ofile.write(_nd.display(child))
                        if use_link:
                            ofile.write('</a>\n')
                        ofile.write("<br>\n")
                    ofile.write('</td>\n</tr>\n')
	ofile.write('</table>\n')

    def display_spouse(self,ofile,family,first=True):
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
            ofile.write('<tr><td>&nbsp;</td></tr>\n')
            ofile.write('<td>&nbsp;</td>')
        ofile.write('<td class="field">%s</td>\n' % relstr)
        ofile.write('<td class="data">')
        use_link = spouse_id in self.ind_list
        if use_link:
            ofile.write('<a href="%s.html">' % spouse.get_gramps_id())
        ofile.write(name)
        if use_link:
            ofile.write('</a>')
        
        ofile.write('</td>\n</tr>\n')

        for event_id in family.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            ofile.write('<tr><td>&nbsp;</td>\n')
            ofile.write('<td class="field">%s</td>\n' % event.get_name())
            ofile.write('<td class="data">\n')
            ofile.write(self.format_event(event))
            ofile.write('</td>\n</tr>\n')

    def pedigree_person(self,ofile,person,bullet='|'):
        person_link = person.handle in self.ind_list
        ofile.write('%s ' % bullet)
        if person_link:
            ofile.write('<a href="%s.html">' % person.gramps_id)
        ofile.write(_nd.display(person))
        if person_link:
            ofile.write('</a>')
        ofile.write('<br>\n')

    def pedigree_family(self,ofile):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                self.pedigree_person(ofile,spouse,'&bull;')
            childlist = rel_family.get_child_handle_list()
            if childlist:
                ofile.write('<blockquote class="pedigreeind">\n')
                for child_handle in childlist:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(ofile,child)
                ofile.write('</blockquote>\n')

    def format_event(self,event):
        descr = event.get_description()
        place = ReportUtils.place_name(self.db,event.get_place_handle())
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
        HTMLgendex
        HTMLidxbirth
        yearso
        """
#    self,db,person,target_path,max_gen,photos,filter,restrict,
#                 private, srccomments, include_link, include_mini_tree,
#                 style, image_dir, template_name,use_id,id_link,gendex,places,ext,
#                 include_alpha_links,separate_alpha,n_cols,ind_template_name,
#                 depth,birth_dates,year_only):
        self.database = database
        self.start_person = person
        self.options_class = options_class

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(GenericFilter.CustomFilters.get_filters())
        self.filter = filters[filter_num]

        default_style = BaseDoc.StyleSheet()
        self.options_class.make_default_style(default_style)
        style_file = self.options_class.handler.get_stylesheet_savefile()
        style_list = BaseDoc.StyleSheetList(style_file,default_style)
        style_name = self.options_class.handler.get_default_stylesheet_name()
        self.selected_style = style_list.get_style_sheet(style_name)

        self.template_name = options_class.handler.template_name

        self.target_path = options_class.handler.options_dict['HTMLod']
        self.ext = options_class.handler.options_dict['HTMLext']
        self.use_id = options_class.handler.options_dict['HTMLincid']
        self.id_link = options_class.handler.options_dict['HTMLlinktidx']
        self.photos = options_class.handler.options_dict['HTMLimg']
        self.restrict = options_class.handler.options_dict['HTMLrestrictinfo']
        self.private = options_class.handler.options_dict['HTMLincpriv']
        self.srccomments = options_class.handler.options_dict['HTMLcmtxtsi']
        self.include_link = options_class.handler.options_dict['HTMLlinktidx']
        self.include_mini_tree = options_class.handler.options_dict['HTMLshorttree']
        self.image_dir = options_class.handler.options_dict['HTMLimagedir']
        self.use_gendex = options_class.handler.options_dict['HTMLgendex']
        self.use_places = options_class.handler.options_dict['HTMLplaceidx']
        self.include_alpha_links = options_class.handler.options_dict['HTMLlnktoalphabet']
        self.separate_alpha = options_class.handler.options_dict['HTMLsplita']
        self.n_cols = options_class.handler.options_dict['HTMLidxcol']
        self.ind_template_name = options_class.handler.options_dict['HTMLidxt']
        self.depth = options_class.handler.options_dict['HTMLtreed']
        self.birth_dates = options_class.handler.options_dict['HTMLidxbirth']
        self.year_only = options_class.handler.options_dict['HTMLyearso']
        self.sort = Sort.Sort(self.database)

    def get_progressbar_data(self):
        return (_("Generate HTML reports - GRAMPS"),
                '<span size="larger" weight="bold">%s</span>' %
                _("Creating Web Pages"))
    
    def dump_gendex(self,person_handle_list,html_dir):
        fname = "%s/gendex.txt" % html_dir
        try:
            f = open(fname,"w")
        except:
            return
        for p_id in person_handle_list:
            p = self.database.get_person_from_handle(p_id)
            name = p.get_primary_name()
            firstName = name.get_first_name()
            surName = name.get_surname()
            suffix = name.get_suffix()

            f.write("%s.%s|" % (p_id,self.ext))
            f.write("%s|" % surName)
            if suffix == "":
                f.write("%s /%s/|" % (firstName,surName))
            else:
                f.write("%s /%s/, %s|" % (firstName,surName, suffix))
            for e_id in [p.get_birth_handle(),p.get_death_handle()]:
                if e_id:
                    e = self.database.get_event_from_handle(e_id)
                else:
                    continue
                if e:
                    f.write("%s|" % DateHander.displayer.display(e.get_date_object()))
                    if e.get_place_handle():
                        f.write('%s|' % self.database.get_place_from_handle(e.get_place_handle()).get_title())
                    else:
                        f.write('|')
                else:
                    f.write('||')
            f.write('\n')
        f.close()

    def dump_places(self,person_handle_list,styles,template,html_dir):
        """Writes an index file, listing all places and the referenced persons."""

        doc = HtmlLinkDoc(self.selected_style,None,template,None)
        doc.set_extension(self.ext)
        doc.set_title(_("Place Index"))
    
        doc.open("%s/loc.%s" % (html_dir,self.ext))
        doc.start_paragraph("Title")
        doc.write_text(_("Place Index"))
        doc.end_paragraph()

        used_places = {}
        for person_handle in person_handle_list:
            person = self.database.get_person_from_handle(person_handle)
            for event_handle in [person.get_birth_handle(), person.get_death_handle()] + person.get_event_list():
                event = self.database.get_event_from_handle(event_handle)
                if event:
                    if event.get_place_handle() not in used_places:
                        used_places[event.get_place_handle()] = []
                    used_places[event.get_place_handle()].append((person_handle, event.get_name()))
            for family_handle in person.get_family_handle_list():
                family = self.database.get_family_from_handle(family_handle)
                for event_handle in family.get_event_list():
                    event = self.database.get_event_from_handle(event_handle)
                    if event:
                        if event.get_place_handle() not in used_places:
                            used_places[event.get_place_handle()] = []
                        used_places[event.get_place_handle()].append((person_handle, event.get_name()))
        
        for key in self.database.get_place_handles():
            if key in used_places:
                myplace = self.database.get_place_from_handle(key)
                doc.start_paragraph("IndexLabel")
                doc.write_linktarget(myplace.get_gramps_id())
                doc.write_text(myplace.get_title())
                doc.end_paragraph()

                for match in used_places[key]:
                    person_handle = match[0]
                    event_name = match[1]
                    person = self.database.get_person_from_handle(person_handle)
                    name = person.get_primary_name().get_name()

                    if self.birth_dates:
                        birth_handle = self.database.get_person_from_handle(person_handle).get_birth_handle()
                        if birth_handle:
                            birth_event = self.database.get_event_from_handle(birth_handle)
                            if self.year_only:
                                birth_dobj = birth_event.get_date_object()
                                if birth_dobj.get_year_valid():
                                    birth_date = birth_dobj.get_year()
                                else:
                                    birth_date = ""
                            else:
                                birth_date = birth_event.get_date()
                        else:
                            birth_date = ""
                    doc.start_link("%s.%s" % (person.get_gramps_id(),self.ext))
                    doc.write_text(name)
                    if self.birth_dates and birth_date:
                        doc.write_text(' (%s %s)' % (_BORN,birth_date))
                    doc.end_link()
                    doc.write_text(' (%s)' % _(event_name))
                    doc.newline()


        if self.include_link:
            doc.start_paragraph("Data")
            doc.start_link("index.%s" % self.ext)
            doc.write_text(_("Return to the index of people"))
            doc.end_link()
            doc.end_paragraph()
        doc.close()

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
    
        ind_list = self.filter.apply(self.database,self.database.get_person_handles(sort_handles=False))
        progress_steps = len(ind_list)
        if len(ind_list) > 1:
            progress_steps = progress_steps+1
        if self.use_gendex == 1:
            progress_steps = progress_steps+1
        if self.use_places == 1:
            progress_steps = progress_steps+1
        self.progress_bar_setup(float(progress_steps))

        self.write_css(dir_name)

        HomePage(self.database,dir_name)
        SourcesPage(self.database,dir_name)
        ContactPage(self.database,dir_name)
        DownloadPage(self.database,dir_name)
        IntroductionPage(self.database,dir_name)
        
        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            idoc = IndividualPage(self.database,person, dir_name, ind_list)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
            
        if len(ind_list) > 1:
            IndividualListPage(self.database, ind_list, dir_name)
            SurnameListPage(self.database, ind_list, dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
        if self.use_gendex == 1:
            self.dump_gendex(ind_list,dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
        if 0:
            self.dump_places(ind_list,self.selected_style,
                            self.ind_template_name,dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
        self.progress_bar_done()

    def write_css(self,dir_name):
        f = open(os.path.join(dir_name,_NARRATIVE), "w")
        f.write('\n'.join(_css))
        f.close()
                 
    def add_styles(self,doc):
        tbl = BaseDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_column_widths([15,85])
        doc.add_table_style("IndTable",tbl)

        cell = BaseDoc.TableCellStyle()
        doc.add_cell_style("NormalCell",cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        doc.add_cell_style("ImageCell",cell)

        cell = BaseDoc.TableCellStyle()
        cell.set_padding(0.2)
        doc.add_cell_style("NoteCell",cell)

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
            'HTMLincid'         : 0,
            'HTMLidurl'         : '',
            'HTMLlinktidx'      : 1,
            'HTMLext'           : 'html',
            'HTMLtreed'         : 3,
            'HTMLidxt'          : '',
            'HTMLidxcol'        : 2,
            'HTMLgendex'        : 0,
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
        lnk_msg = _("Include a link to the index page")
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        no_img_msg = _("Do not use images")
        no_limg_msg = _("Do not use images for living people")
        no_com_msg = _("Do not include comments and text in source information")
        include_id_msg = _("Include the GRAMPS ID in the report")
        gendex_msg = _("Create a GENDEX index")
        places_msg = _("Create an index of all Places")
        imgdir_msg = _("Image subdirectory")
        depth_msg = _("Ancestor tree depth")
        ext_msg = _("File extension")
        alpha_links_msg = _("Links to alphabetical sections in index page")
        sep_alpha_msg = _("Split alphabetical sections to separate pages")
        birth_date_msg = _("Append birth dates to the names")
        year_only_msg = _("Use only year of birth")
        tree_msg = _("Include short ancestor tree")

        self.mini_tree = gtk.CheckButton(tree_msg)
        self.mini_tree.set_active(self.options_dict['HTMLshorttree'])

        self.depth = gtk.SpinButton()
        self.depth.set_digits(0)
        self.depth.set_increments(1,2)
        self.depth.set_range(1,10)
        self.depth.set_numeric(gtk.TRUE)
        self.depth.set_value(self.options_dict['HTMLtreed'])

        self.use_link = gtk.CheckButton(lnk_msg)
        self.use_link.set_active(self.options_dict['HTMLlinktidx'])

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

        self.include_id = gtk.CheckButton(include_id_msg)
        self.include_id.set_active(self.options_dict['HTMLincid'])

        self.gendex = gtk.CheckButton(gendex_msg)
        self.gendex.set_active(self.options_dict['HTMLgendex'])

        self.places = gtk.CheckButton(places_msg)
        self.places.set_active(self.options_dict['HTMLplaceidx'])

        self.imgdir = gtk.Entry()
        self.imgdir.set_text(self.options_dict['HTMLimagedir'])

        self.linkpath = gtk.Entry()
        self.linkpath.set_sensitive(self.options_dict['HTMLincid'])
        self.linkpath.set_text(self.options_dict['HTMLidurl'])

        self.include_id.connect('toggled',self.show_link)
        self.ext = gtk.combo_box_new_text()
        for text in ['.html','.htm','.php','.php3','.cgi']:
            self.ext.append_text(text)
        
        #self.ext.set_active(self.options_dict['HTMLext'])

        self.use_alpha_links = gtk.CheckButton(alpha_links_msg)
        self.use_alpha_links.set_active(self.options_dict['HTMLlnktoalphabet'])

        self.use_sep_alpha = gtk.CheckButton(sep_alpha_msg)
        self.use_sep_alpha.set_sensitive(self.options_dict['HTMLlnktoalphabet'])
        self.use_sep_alpha.set_active(self.options_dict['HTMLsplita'])

        self.use_n_cols = gtk.SpinButton()
        self.use_n_cols.set_digits(0)
        self.use_n_cols.set_increments(1,2)
        self.use_n_cols.set_range(1,5)
        self.use_n_cols.set_numeric(gtk.TRUE)
        self.use_n_cols.set_value(self.options_dict['HTMLidxcol'])

        self.ind_template = gtk.Combo()
        template_list = [ Report._default_template ]
        tlist = Report._template_map.keys()
        tlist.sort()
        for template in tlist:
            if template != Report._user_template:
                template_list.append(template)
        template_list.append(Report._user_template)
        self.ind_template.set_popdown_strings(template_list)
        self.ind_template.entry.set_editable(0)
        self.ind_user_template = gnome.ui.FileEntry("HTML_Template",_("Choose File"))
        self.ind_user_template.set_sensitive(0)

        self.add_birth_date = gtk.CheckButton(birth_date_msg)
        self.add_birth_date.set_active(self.options_dict['HTMLidxbirth'])

        self.use_year_only = gtk.CheckButton(year_only_msg)
        self.use_year_only.set_active(self.options_dict['HTMLyearso'])
        self.use_year_only.set_sensitive(self.options_dict['HTMLidxbirth'])

        self.add_birth_date.connect('toggled',self.on_birth_date_toggled)

        dialog.add_option(imgdir_msg,self.imgdir)
        dialog.add_option('',self.mini_tree)
        dialog.add_option(depth_msg,self.depth)
        dialog.add_option('',self.use_link)

        self.mini_tree.connect('toggled',self.on_mini_tree_toggled)

        self.use_alpha_links.connect('toggled',self.on_use_alpha_links_toggled)
        self.ind_template.entry.connect('changed',self.ind_template_changed)

        title = _("Privacy")
        dialog.add_frame_option(title,None,self.no_private)
        dialog.add_frame_option(title,None,self.restrict_living)
        dialog.add_frame_option(title,None,self.no_images)
        dialog.add_frame_option(title,None,self.no_living_images)
        dialog.add_frame_option(title,None,self.no_comments)

        title = _('Index page')
        dialog.add_frame_option(title,_('Template'),self.ind_template)
        dialog.add_frame_option(title,_("User Template"),self.ind_user_template)
        dialog.add_frame_option(title,None,self.use_alpha_links)
        dialog.add_frame_option(title,None,self.use_sep_alpha)
        dialog.add_frame_option(title,_('Number of columns'),self.use_n_cols)
        dialog.add_frame_option(title,None,self.add_birth_date)
        dialog.add_frame_option(title,None,self.use_year_only)

        title = _('Advanced')
        dialog.add_frame_option(title,'',self.include_id)
        dialog.add_frame_option(title,_('GRAMPS ID link URL'),self.linkpath)
        dialog.add_frame_option(title,'',self.gendex)
        dialog.add_frame_option(title,'',self.places)
        dialog.add_frame_option(title,ext_msg,self.ext)

        self.no_images.connect('toggled',self.on_nophotos_toggled)

    def parse_user_options(self,dialog):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        
        self.options_dict['HTMLrestrictinfo'] = int(self.restrict_living.get_active())
        self.options_dict['HTMLincpriv'] = int(not self.no_private.get_active())
        self.options_dict['HTMLimagedir'] = unicode(self.imgdir.get_text())
        self.options_dict['HTMLshorttree'] = int(self.mini_tree.get_active())
        self.options_dict['HTMLtreed'] = self.depth.get_value_as_int()
        self.options_dict['HTMLlinktidx'] = int(self.use_link.get_active())

        #html_ext = unicode(self.ext.entry.get_text().strip())
        html_ext = ".html"
        if html_ext[0] == '.':
            html_ext = html_ext[1:]
        self.options_dict['HTMLext'] = html_ext

        self.options_dict['HTMLincid'] = int(self.include_id.get_active())
        self.options_dict['HTMLgendex'] = int(self.gendex.get_active())
        self.options_dict['HTMLplaceidx'] = int(self.places.get_active())
        self.options_dict['HTMLidurl'] = unicode(self.linkpath.get_text().strip())

        self.options_dict['HTMLcmtxtsi'] = int(not self.no_comments.get_active())
        if self.no_images.get_active():
            photos = 0
        elif self.no_living_images.get_active():
            photos = 1
        else:
            photos = 2
        self.options_dict['HTMLimg'] = photos

        text = unicode(self.ind_template.entry.get_text())
        if Report._template_map.has_key(text):
            if text == Report._user_template:
                ind_template_name = dialog.ind_user_template.get_full_path(0)
            else:
                ind_template_name = "%s/%s" % (const.template_dir,Report._template_map[text])
        else:
            ind_template_name = None
        self.options_dict['HTMLidxt'] = ind_template_name

        self.options_dict['HTMLlnktoalphabet'] = int(self.use_alpha_links.get_active())

        if self.options_dict['HTMLlnktoalphabet']:
            separate_alpha = int(self.use_sep_alpha.get_active())
        else:
            separate_alpha = 0
        self.options_dict['HTMLsplita'] = int(separate_alpha)

        self.options_dict['HTMLidxcol'] = self.use_n_cols.get_value_as_int()
        self.options_dict['HTMLidxbirth'] = int(self.add_birth_date.get_active())
        self.options_dict['HTMLyearso'] = int(self.use_year_only.get_active())
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

    def on_use_alpha_links_toggled(self,obj):
        """Keep the 'split alpha sections to separate pages' checkbox in 
        line with the 'use alpha links' checkbox.  If there are no alpha
        links included, it makes no sense to worry about splitting or not
        the alpha link target to separate pages."""
        self.use_sep_alpha.set_sensitive(obj.get_active())

    def on_mini_tree_toggled(self,obj):
        """Keep the 'Mini tree depth' spin button in line with 
        the 'include short tree' checkbox.  If there is no mini tree included, 
        it makes no sense to worry about its depth."""
        self.depth.set_sensitive(obj.get_active())

    def ind_template_changed(self,obj):
        text = unicode(obj.get_text())
        if Report._template_map.has_key(text):
            if Report._template_map[text]:
                self.ind_user_template.set_sensitive(0)
            else:
                self.ind_user_template.set_sensitive(1)
        else:
            self.ind_user_template.set_sensitive(0)

    def on_birth_date_toggled(self,obj):
        """Keep the 'User year only' check button in line with
        the 'Add birth date' checkbox.  If no mini birth date is added
        then it makes no sense to worry about its format."""
        self.use_year_only.set_sensitive(obj.get_active())

    def make_default_style(self,default_style):
        """Make the default output style for the Web Pages Report."""
        font = BaseDoc.FontStyle()
        font.set(bold=1, face=BaseDoc.FONT_SANS_SERIF, size=16)
        p = BaseDoc.ParagraphStyle()
        p.set(align=BaseDoc.PARA_ALIGN_CENTER,font=font)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_style("Title",p)
        
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header that identifies "
                            "facts and events."))
        default_style.add_style("EventsTitle",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the notes section."))
        default_style.add_style("NotesTitle",p)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=10)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,align=BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the copyright notice."))
        default_style.add_style("Copyright",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the sources section."))
        default_style.add_style("SourcesTitle",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font)
        p.set_description(_("The style used on the index page that labels each section."))
        default_style.add_style("IndexLabel",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,align=BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used on the index page that labels links to each section."))
        default_style.add_style("IndexLabelLinks",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the image section."))
        default_style.add_style("GalleryTitle",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the siblings section."))
        default_style.add_style("SiblingsTitle",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the marriages "
                            "and children section."))
        default_style.add_style("FamilyTitle",p)
        
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the spouse's name."))
        default_style.add_style("Spouse",p)
    
        font = BaseDoc.FontStyle()
        font.set(size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the general data labels."))
        default_style.add_style("Label",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the general data."))
        default_style.add_style("Data",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the description of images."))
        default_style.add_style("PhotoDescription",p)
    
        font = BaseDoc.FontStyle()
        font.set(size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the notes associated with images."))
        default_style.add_style("PhotoNote",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(10)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the source information."))
        default_style.add_style("SourceParagraph",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the note information."))
        default_style.add_style("NotesParagraph",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the URL section."))
        default_style.add_style("UrlTitle",p)

        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the URL information."))
        default_style.add_style("UrlList",p)

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

        response = self.window.run()
        if response == gtk.RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.window.destroy()

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
            MyReport = WebReport(self.database,self.person,self.options_class)
            """
            self.target_path,
                                 self.max_gen, self.photos, self.filter,
                                 self.restrict, self.private, self.srccomments,
                                 self.include_link, self.include_mini_tree,
                                 self.selected_style,
                                 self.img_dir_text,self.template_name,
                                 self.use_id,self.id_link,self.use_gendex,self.use_places,
                                 self.html_ext,self.include_alpha_links,
                                 self.separate_alpha,self.n_cols,
                                 self.ind_template_name,self.depth_value,
                                 self.birth_dates,self.year_only)
            """
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class MiniTree:
    """
    This is one dirty piece of code, that is why I made it it's own
    class.  I'm sure that someone with more knowledge of GRAMPS can make
    it much cleaner.
    """
    def __init__(self,db,person,doc,the_map,depth):
        self.map = the_map
        self.db = db
        self.doc = doc
        self.depth = depth
        self.person = person
        self.lines_map = {} 
        self.draw_parents(person,2**(self.depth-1),'',self.depth,1)
        keys = self.lines_map.keys()
        keys.sort()
        self.lines = [ self.lines_map[key] for key in keys ]

    def draw_parents(self,person,position,indent,generations,topline):

        name = person.get_primary_name().get_regular_name()
        self.lines_map[position] = ""

        if topline and indent:
            # if we're on top (father's) line, replace last '|' with space
            self.lines_map[position] += indent[:-1] + ' '
        else:
            self.lines_map[position] += indent

        if person and person.get_handle() and self.map.has_key(person.get_handle()):
            self.lines_map[position] += "<A HREF='%s%s'>%s</A>" % (person.get_gramps_id(),
                                                           self.doc.ext, name)
        else:
            self.lines_map[position] += "<U>%s</U>" % name

        # We are done with this generation
        generations = generations - 1
        if not generations: return

        offset = 2**(generations-1)

        family_handle = person.get_main_parents_family_handle()
        if not family_handle: return

        family = self.db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()

        if topline:
            # if we're on top (father's) line, replace last '|' with space
            # then add '|' to the end for the next generation
            if indent:
                father_indent = indent[:-1] + ' ' + ' ' * len(name) + '|'
            else:
                father_indent = ' ' * len(name) + '|'
            mother_indent = indent + ' ' * len(name) + '|'
        else:
            # if we're not on top (i.e. mother's) line, remove last '|'
            # from next mother's indent, then add '|' to both
            father_indent = indent + ' ' * len(name) + '|'
            mother_indent = indent[:-1] + ' ' + ' ' * len(name) + '|'

        if father_handle:
            father = self.db.get_person_from_handle(father_handle)
            next_pos = position - offset 
            self.lines_map[position] += '|'
            self.draw_parents(father,next_pos,father_indent,generations,1)
            
        if mother_handle:
            mother = self.db.get_person_from_handle(mother_handle)
            next_pos = position + offset
            self.draw_parents(mother,next_pos,mother_indent,generations,0)

    def draw_father(self, person, name, line, indent):
        self.draw_string(line, indent, '|')
        self.draw_string(line-1, indent+1, "")
        self.draw_link(line-1, person, name)

    def draw_mother(self, person, name, line, indent):
        self.draw_string(line+1, indent, '|')
        self.draw_link(line+1, person, name)

    def draw_string(self, line, indent, text):
        self.lines[line] += ' ' * (indent-len(self.lines[line])) + text

    def draw_link(self, line, person, name):
        if person and person.get_handle() and self.map.has_key(person.get_handle()):
            self.lines[line] += "<A HREF='%s%s'>%s</A>" % (person.get_gramps_id(),
                                                           self.doc.ext, name)
        else:
            self.lines[line] += "<U>%s</U>" % name

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
