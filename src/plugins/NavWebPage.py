#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
import DateHandler
import Sort
import Report
import Errors
import Utils
from QuestionDialog import ErrorDialog
import ReportOptions
import BaseDoc
import NameDisplay
import ReportUtils

_css = [
    'BODY {',
    'font-family: "Arial", "Helvetica", sans-serif;',
    'letter-spacing: 0.05em;',
    'background-color: #fafaff;',
    'color: #003;',
    '}',
    '',
    'P,BLOCKQUOTE {',
    'font-size: 14px;',
    '}',
    '',
    'DIV {',
    'margin: 2px;',
    'padding: 2px;',
    '}',
    '',
    'TD {',
    'vertical-align: top;',
    '}',
    '',
    'H1 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;',
    'font-size:	160%;',
    'margin: 2px;',
    '}',
    'H2 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;',
    'font-style: italic;',
    'font-size:	150%;',
    '}',
    'H3 {',
    'font-weight: bold;',
    'margin: 0;',
    'padding-top: 10px;',
    'padding-bottom: 10px;',
    'color: #336;',
    '}',
    'H4 {',
    'margin-top: 1em;',
    'margin-bottom: 0.3em;',
    'padding-left: 4px;',
    'background-color: #667;',
    'color: #fff;',
    '}',
    'H5 {',
    'margin-bottom: 0.5em;',
    '}',
    'H6 {',
    'font-weight: normal;',
    'font-style: italic;',
    'font-size:	100%;',
    'margin-left: 1em;',
    'margin-top: 1.3em;',
    'margin-bottom: 0.8em;',
    '}',
    '',
    'HR {',
    'height: 0;',
    'width: 0;',
    'margin: 0;',
    'margin-top: 1px;',
    'margin-bottom: 1px;',
    'padding: 0;',
    'border-top: 0;	/* Hack: Mozilla work-around to eliminate "groove" */',
    'border-color: #e0e0e9;',
    '}',
    '',
    'A:link {',
    'color: #006;',
    'text-decoration: underline;',
    '}',
    'A:visited {',
    'color: #669;',
    'text-decoration: underline;',
    '}',
    'A:hover {',
    'background-color: #eef;',
    'color: #000;',
    'text-decoration: underline;',
    '}',
    'A:active {',
    'background-color: #eef;',
    'color: #000;',
    'text-decoration: none;',
    '}',
    '',
    '/* Custom {{{1',
    '*/',
    '',
    '.navheader {',
    'padding: 4px;',
    'background-color: #e0e0e9;',
    'margin: 2px;',
    '}',
    '.navtitle {',
    'font-size:	160%;',
    'color: #669;',
    'margin: 2px;',
    '',
    '}',
    '.navbyline {',
    'float: right;',
    'font-size: 14px;',
    'margin: 2px;',
    'padding: 4px;',
    '}',
    '.nav {',
    'margin: 0;',
    'margin-bottom: 4px;',
    'padding: 0;',
    'font-size: 14px;',
    'font-weight: bold;',
    '',
    '',
    '',
    '}',
    '',
    '',
    '.summaryarea {',
    'min-height: 100px;',
    '/* Hack: IE Dynamic Expression to set the width */',
    'height: expression(document.body.clientHeight < 1 ? "100px" : "100px" );',
    '}',
    '',
    '.portrait {',
    'justify: center;',
    'margin: 5px;',
    'margin-right: 20px;',
    'padding: 3px;',
    'border-color: #336;',
    'border-width: 1px;',
    '}',
    '.snapshot {',
    'float: right;',
    'margin: 5px;',
    'margin-right: 20px;',
    'padding: 3px;',
    '}',
    '.thumbnail {',
    'height: 100px;',
    'border-color: #336;',
    'border-width: 1px;',
    '}',
    '',
    '.leftwrap {',
    'float: left;',
    'margin: 2px;',
    'margin-right: 10px;',
    '}',
    '.rightwrap {',
    'float: right;',
    'margin: 2px;',
    'margin-left: 10px;',
    '}',
    '',
    'TABLE.infolist {',
    'border: 0;',
    '/*width: 100%;*/',
    'font-size: 14px;',
    '}',
    'TD.category {',
    'padding: 3px;	/* Defines spacing between rows */',
    'padding-right: 3em;',
    '/*width: 10%;*/',
    'font-weight: bold;',
    '}',
    'TD.field {',
    'padding: 3px;	/* Defines spacing between rows */',
    'padding-right: 3em;',
    '/*width: 15%;*/',
    '',
    '}',
    'TD.data {',
    'padding: 3px;	/* Defines spacing between rows */',
    'padding-right: 3em;',
    'font-weight: bold;',
    '}',
    '',
    '',
    '.pedigree {',
    'margin: 0;',
    'margin-left: 2em;',
    'padding: 0;',
    'background-color: #e0e0e9;',
    'border: 1px;',
    '}',
    '.pedigreeind {',
    'font-size: 14px;',
    'margin: 0;',
    'padding: 2em;',
    'padding-top: 0.25em;',
    'padding-bottom: 0.5em;',
    '}',
    '',
    '',
    '.footer {',
    'margin: 1em;',
    'font-size: 12px;',
    'float: right;',
    '}',
    ]
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage:

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
        self.sort_name = NameDisplay.displayer.sorted(self.person)
        self.name = NameDisplay.displayer.sorted(self.person)
        
        self.f = open(os.path.join(dirpath,"%s.html" % gramps_id), "w")
        self.f.write('<!DOCTYPE HTML PUBLIC ')
        self.f.write('"-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        self.f.write('<html>\n')
        self.f.write('<head>\n')
	self.f.write('<title>My Family Tree</title>\n')
	self.f.write('<meta http-equiv="Content-Type" content="text/html; ')
        self.f.write('charset=ISO-8859-1">\n')
	self.f.write('<link href="navwebpage.css" ')
        self.f.write('rel="stylesheet" type="text/css">\n')
	self.f.write('<link href="favicon.png" rel="Shortcut Icon">\n')
        self.f.write('</head>\n')
        self.f.write('<body>\n')

        self.display_header()
        self.display_general()
        self.display_events()
        self.display_relationships()
        self.display_narrative()
        self.display_sources()
        self.display_pedigree()
        self.display_footer()

        self.f.write('</body>\n')
        self.f.write('</html>\n')
        self.f.close()

    def display_sources(self):
	self.f.write('<h4>Sources</h4>\n')
	self.f.write('<hr>\n')

	self.f.write('<table class="infolist" cellpadding="0" cellspacing="0" border="0">\n')
	self.f.write('<tr><td class="field">1. Author, Title, Publisher, Date.</td></tr>\n')
	self.f.write('<tr><td class="field">2. Author, Title, Publisher, Date.</td></tr>\n')
	self.f.write('<tr><td class="field">3. Author, Title, Publisher, Date.</td></tr>\n')
	self.f.write('<tr><td class="field">4. Author, Title, Publisher, Date.</td></tr>\n')
	self.f.write('<tr><td class="field">5. Author, Title, Publisher, Date.</td></tr>\n')
	self.f.write('</table>\n')

    def display_pedigree(self):

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
        
	self.f.write('<h4>Pedigree</h4>\n')
	self.f.write('<hr>\n')
        self.f.write('\n')
	self.f.write('<br>\n')
        self.f.write('\n')
	self.f.write('<table class="pedigree">\n')
        self.f.write('<tr><td>\n')
        if father or mother:
            self.f.write('<blockquote class="pedigreeind">\n')
            if father:
                self.pedigree_person(father)
            if mother:
                self.pedigree_person(mother)
        self.f.write('<blockquote class="pedigreeind">\n')
        if family:
            for child_handle in family.get_child_handle_list():
                if child_handle == self.person.handle:
                    self.f.write('| <strong>%s</strong><br>\n' % self.name)
                    self.pedigree_family()
                else:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(child)
        else:
            self.f.write('| <strong>%s</strong><br>\n' % self.name)
            self.pedigree_family()

#         self.f.write('&bull; Spouse 1<br>\n')
#         self.f.write('<blockquote class="pedigreeind">\n')
#         self.f.write('| Child<br>\n')
#         self.f.write('| Child<br>\n')
#         self.f.write('</blockquote>\n')
#         self.f.write('&bull; Spouse 2<br>\n')
#         self.f.write('<blockquote class="pedigreeind">\n')
#         self.f.write('| Child<br>\n')
#         self.f.write('| Child<br>\n')
#         self.f.write('</blockquote>\n')
#         self.f.write('| Sybling, Younger<br>\n')
#        self.f.write('| Sybling, Younger<br>\n')

        self.f.write('</blockquote>\n')
        if father or mother:
            self.f.write('</blockquote>\n')
        self.f.write('</td>\n')
        self.f.write('</tr>\n')
	self.f.write('</table>\n')

    def display_header(self):
        author = self.db.get_researcher().get_name()
	self.f.write('<div class="navheader">\n')
        self.f.write('  <div class="navbyline">By: %s</div>\n' % author)
        self.f.write('  <h1 class="navtitle">My Family Tree</h1>\n')
        self.f.write('  <hr>\n')
        self.f.write('    <div class="nav">\n')
        self.f.write('    <a href="index.html">Home</a> &nbsp;\n')
        self.f.write('    <a href="introduction.html">Introduction</a> &nbsp;\n')
        self.f.write('    <a href="surnames.html">Surnames</a> &nbsp;\n')
        self.f.write('    <a href="individuals.html">Individuals</a> &nbsp;\n')
        self.f.write('    <a href="sources.html">Sources</a> &nbsp;\n')
        self.f.write('    <a href="download.html">Download</a> &nbsp;\n')
        self.f.write('    <a href="contact.html">Contact</a> &nbsp;\n')
        self.f.write('    </div>\n')
	self.f.write('  </div>\n')
        self.f.write('\n')
        self.f.write('\n')

    def display_general(self):
        photolist = self.person.get_media_list()
        if photolist:
            photo_handle = photolist[0].get_reference_handle()
            photo = self.db.get_object_from_handle(photo_handle)
            
            newpath = self.person.gramps_id + os.path.splitext(photo.get_path())[1]
            shutil.copyfile(photo.get_path(),os.path.join(self.dirpath,newpath))
            self.f.write('<div class="snapshot">\n')
            self.f.write('<a href="%s">' % newpath)
            self.f.write('<img class="thumbnail"  border="0" src="%s" ' % newpath)
            self.f.write('height="100"></a>')
            self.f.write('</div>\n')

	self.f.write('<div class="summaryarea">\n')
        self.f.write('<h3>%s</h3>\n' % self.sort_name)
        self.f.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        self.f.write('border="0">\n')

        # Gender
        self.f.write('<tr><td class="field">Gender</td>\n')
        gender = self.gender_map[self.person.gender]
        self.f.write('<td class="data">%s</td>\n' % gender)
        self.f.write('</tr>\n')

        # Birth
        handle = self.person.get_birth_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            self.f.write('<tr><td class="field">%s</td>\n' % _('Birth'))
            self.f.write('<td class="data">%s</td>\n' % self.format_event(event))
            self.f.write('</tr>\n')

        # Death
        handle = self.person.get_death_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            self.f.write('<tr><td class="field">%s</td>\n' % _('Death'))
            self.f.write('<td class="data">%s</td>\n' % self.format_event(event))
            self.f.write('</tr>\n')

        self.f.write('\n')
        self.f.write('</table>\n')
	self.f.write('</div>\n')
        self.f.write('\n')

    def display_events(self):
	self.f.write('<h4>Events</h4>\n')
	self.f.write('<hr>\n')
	self.f.write('<table class="infolist" cellpadding="0" cellspacing="0" ')
        self.f.write('border="0">\n')

        for event_id in self.person.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            self.f.write('<tr><td class="field">%s</td>\n' % event.get_name())
            self.f.write('<td class="data">\n')
            self.f.write(self.format_event(event))
            self.f.write('</td>\n')
            self.f.write('</tr>\n')

	self.f.write('</table>\n')
        self.f.write('\n')

    def display_narrative(self):
	self.f.write('<h4>Narrative</h4>\n')
	self.f.write('<hr>\n')

        noteobj = self.person.get_note_object()
        if noteobj:
            format = noteobj.get_format()
            text = noteobj.get()

            if format:
                text = "<pre>" + "<br>".join(text.split("\n"))
            else:
                text = "</p><p>".join(text.split("\n"))
            self.f.write('<p>%s</p>\n' % text)

    def display_footer(self):
	self.f.write('<br>\n')
	self.f.write('<br>\n')
	self.f.write('<hr>\n')
	self.f.write('<div class="footer">This page generated from <a href="http://gramps.sourceforge.net">GRAMPS</a> on 13 December 2004.</div>\n')
        
    def display_father(self,handle):
        use_link = handle in self.ind_list
        person = self.db.get_person_from_handle(handle)
        self.f.write('<td class="field">%s</td>\n' % _("Father"))
        self.f.write('<td class="data">')
        if use_link:
            self.f.write('<a href="%s.html">' % person.get_gramps_id())
        self.f.write(NameDisplay.displayer.display(person))
        if use_link:
            self.f.write('</a>\n')
        self.f.write('</td>\n')

    def display_mother(self,handle):
        use_link = handle in self.ind_list
        person = self.db.get_person_from_handle(handle)
        self.f.write('<td class="field">%s</td>\n' % _("Mother"))
        self.f.write('<td class="data">')
        if use_link:
            self.f.write('<a href="%s.html">' % person.get_gramps_id())
        self.f.write(NameDisplay.displayer.display(person))
        if use_link:
            self.f.write('</a>\n')
        self.f.write('</td>\n')

    def display_relationships(self):
        parent_list = self.person.get_parent_family_handle_list()
        family_list = self.person.get_family_handle_list()

        if not parent_list and not family_list:
            return
        
	self.f.write('<h4>%s</h4>\n' % _("Relationships"))
	self.f.write('<hr>\n')
	self.f.write('<table class="infolist" cellpadding="0" cellspacing="0" border="0">\n')

        if parent_list:
            for (family_handle,mrel,frel) in parent_list:
                family = self.db.get_family_from_handle(family_handle)
                
                self.f.write('<tr><td colspan="3">&nbsp;</td></tr>\n')
                self.f.write('<tr><td class="category">%s</td>\n' % _("Parents"))

                father_handle = family.get_father_handle()
                if father_handle:
                    self.display_father(father_handle)
                self.f.write('</tr><tr><td>&nbsp;</td>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.display_mother(mother_handle)
                self.f.write('</tr>\n')
            self.f.write('<tr><td colspan="3">&nbsp;</td></tr>\n')

        if family_list:
            self.f.write('<tr><td class="category">%s</td>\n' % _("Spouses"))
            for family_handle in family_list:
                family = self.db.get_family_from_handle(family_handle)
                self.display_spouse(family)
                childlist = family.get_child_handle_list()
                if childlist:
                    self.f.write('<tr><td>&nbsp;</td>\n')
                    self.f.write('<td class="field">%s</td>\n' % _("Children"))
                    self.f.write('<td class="data">\n')
                    for child_handle in childlist:
                        use_link = child_handle in self.ind_list
                        child = self.db.get_person_from_handle(child_handle)
                        if use_link:
                            self.f.write('<a href="%s.html">' % self.person.get_gramps_id())
                        self.f.write(NameDisplay.displayer.display(child))
                        if use_link:
                            self.f.write('</a>\n')
                        self.f.write("<br>\n")
                    self.f.write('</td>\n')
                    self.f.write('</tr>\n')
                    self.f.write('\n')
	self.f.write('</table>\n')
        self.f.write('\n')

    def display_spouse(self,family):
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
            name = NameDisplay.displayer.display(spouse)
        else:
            name = _("unknown")
        self.f.write('<td class="field">%s</td>\n' % relstr)
        self.f.write('<td class="data">')
        use_link = spouse_id in self.ind_list
        if use_link:
            self.f.write('<a href="%s.html">' % spouse.get_gramps_id())
        self.f.write(name)
        if use_link:
            self.f.write('</a>')
        
        self.f.write('</td>\n')
        self.f.write('</tr>\n')

        for event_id in family.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            self.f.write('<tr><td>&nbsp;</td>\n')
            self.f.write('<td class="field">%s</td>\n' % event.get_name())
            self.f.write('<td class="data">\n')
            self.f.write(self.format_event(event))
            self.f.write('</td>\n')
            self.f.write('</tr>\n')

    def pedigree_person(self,person,bullet='|'):
        person_link = person.handle in self.ind_list
        self.f.write('%s ' % bullet)
        if person_link:
            self.f.write('<a href="%s.html">' % person.gramps_id)
        self.f.write(NameDisplay.displayer.display(person))
        if person_link:
            self.f.write('</a>')
        self.f.write('<br>\n')

    def pedigree_family(self):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                self.pedigree_person(spouse,'&bull;')
            childlist = rel_family.get_child_handle_list()
            if childlist:
                self.f.write('<blockquote class="pedigreeind">\n')
                for child_handle in childlist:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(child)
                self.f.write('</blockquote>\n')

    def format_event(self,event):
        descr = event.get_description()
        place = ReportUtils.place_name(self.db,event.get_place_handle())
        date = DateHandler.displayer.display(event.get_date_object())

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

    def dump_index(self,person_handle_list,styles,template,html_dir):
        """Writes an index file, listing all people in the person list."""

        return
    
        doc = HtmlLinkDoc(self.selected_style,None,template,None)
        doc.set_extension(self.ext)
        doc.set_title(_("Family Tree Index"))
    
        doc.open("%s/index.%s" % (html_dir,self.ext))
        doc.start_paragraph("Title")
        doc.write_text(_("Family Tree Index"))
        doc.end_paragraph()
    
        person_handle_list.sort(self.sort.by_last_name)

        a = {}
        for person_handle in person_handle_list:
            person = self.database.get_person_from_handle(person_handle)
            n = person.get_primary_name().get_surname()
            if n:
                a[n[0]] = 1
            else:
                a[''] = 1

        section_number = 1
        link_keys = a.keys()
        link_keys.sort()
        for n in link_keys:
            a[n] = section_number
            section_number = section_number + 1

        if self.include_alpha_links:
            doc.start_paragraph('IndexLabelLinks')
            if self.separate_alpha:
                link_str = "index_%%03d.%s" % self.ext
            else:
                link_str = "#%03d"
            for n in link_keys:
                doc.start_link(link_str % a[n])
                doc.write_text(n)
                doc.end_link()
                doc.write_text(' ')
            doc.end_paragraph()
        
        if self.separate_alpha:
            doc.close()
            for n in link_keys:
                p_id_list = [ p_id for p_id in person_handle_list if \
                            (self.database.get_person_from_handle(p_id).get_primary_name().get_surname() \
                            and (self.database.get_person_from_handle(p_id).get_primary_name().get_surname()[0] == n) ) ]
                doc = HtmlLinkDoc(self.selected_style,None,template,None)
                doc.set_extension(self.ext)
                doc.set_title(_("Section %s") % n)

                doc.open("%s/index_%03d.%s" % (html_dir,a[n],self.ext))
                doc.start_paragraph("Title")
                doc.write_text(_("Section %s") % n)
                doc.end_paragraph()

                n_rows = len(p_id_list)/self.n_cols
                td_width = 100/self.n_cols

                doc.write_raw('<table width="100%" border="0">')
                doc.write_raw('<tr><td width="%d%%" valign="top">' % td_width)
                col_len = n_rows

                for person_handle in p_id_list:
                    the_person = self.database.get_person_from_handle(person_handle)
                    name = the_person.get_primary_name().get_name()

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

                    doc.start_link("%s.%s" % (the_person.get_gramps_id(),self.ext))
                    doc.write_text(name)
                    if self.birth_dates and birth_date:
                        doc.write_text(' (%s %s)' % (_BORN,birth_date))
                    doc.end_link()

                    if col_len <= 0:
                        doc.write_raw('</td><td width="%d%%" valign="top">' % td_width)
                        col_len = n_rows
                    else:
                        doc.newline()
                    col_len = col_len - 1
                doc.write_raw('</td></tr></table>')
        else:
            n_rows = len(person_handle_list) + len(link_keys)
            n_rows = n_rows/self.n_cols
            td_width = 100/self.n_cols

            doc.write_raw('<table width="100%" border="0">')
            doc.write_raw('<tr><td width="%d%%" valign="top">' % td_width)
            col_len = n_rows
            for n in link_keys:
                p_id_list = [ p_id for p_id in person_handle_list if \
                            (self.database.get_person_from_handle(p_id).get_primary_name().get_surname() \
                            and (self.database.get_person_from_handle(p_id).get_primary_name().get_surname()[0] == n) ) ]
                doc.start_paragraph('IndexLabel')
                if self.include_alpha_links:
                    doc.write_linktarget("%03d" % a[n])
                doc.write_text(n)
                doc.end_paragraph()
                col_len = col_len - 1

                for person_handle in p_id_list:
                    the_person = self.database.get_person_from_handle(person_handle)
                    name = the_person.get_primary_name().get_name()

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

                    doc.start_link("%s.%s" % (the_person.get_gramps_id(),self.ext))
                    doc.write_text(name)
                    if self.birth_dates and birth_date:
                        doc.write_text(' (%s %s)' % (_BORN,birth_date))
                    doc.end_link()
                    if col_len <= 0:
                        doc.write_raw('</td><td width="%d%%" valign="top">' % td_width)
                        doc.start_paragraph('IndexLabel')
                        doc.write_text(_("%s (continued)") % n)
                        doc.end_paragraph()
                        col_len = n_rows
                    else:
                        doc.newline()
                    col_len = col_len - 1
            doc.write_raw('</td></tr></table>')
        if self.include_link and self.use_places:
            doc.start_paragraph("Data")
            doc.start_link("loc.%s" % self.ext)
            doc.write_text(_("Return to the index of places"))
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

        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            idoc = IndividualPage(self.database,person, dir_name, ind_list)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
            
        if len(ind_list) > 1:
            self.dump_index(ind_list,self.selected_style,
                            self.ind_template_name,dir_name)
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
        f = open(os.path.join(dir_name,"navwebpage.css"), "w")
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
        name = "webpage"
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
    name = 'webpage',
    category = const.CATEGORY_WEB,
    report_class = WebReportDialog,
    options_class = cl_report,
    modes = Report.MODE_GUI | Report.MODE_CLI,
    translated_name = _("Narrative Web Site"),
    status=(_("Beta")),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    )
