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
import re
import string
import time
import shutil

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
import RelLib
import HtmlDoc
import BaseDoc
import const
import GrampsCfg
import GenericFilter
import Date
import sort
import Report
import Errors
from QuestionDialog import ErrorDialog
from gettext import gettext as _

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_month = [
    "",    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]

_hline = " "    # Everything is underlined, so use blank

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def by_date(a,b):
    return Date.compare_dates(a.get_date_object(),b.get_date_object())

#------------------------------------------------------------------------
#
# HtmlLinkDoc
#
#------------------------------------------------------------------------
class HtmlLinkDoc(HtmlDoc.HtmlDoc):
    """
    Version of the HtmlDoc class that provides the ability to create a link
    """
    def write_linktarget(self,path):
        self.f.write('<A NAME="%s"></A>' % path)

    def start_link(self,path):
        self.f.write('<A HREF="%s">' % path)

    def end_link(self):
        self.f.write('</A>')

    def newline(self):
        self.f.write('<BR>\n')

    def write_raw(self,text):
        self.f.write(text)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage:

    def __init__(self,db,person,photos,restrict,private,uc,link,mini_tree,map,
                 dir_name,imgdir,doc,id,idlink,ext,depth):
        self.person = person
        self.db = db
        self.ext = ext
        self.doc = doc
        self.use_id = id
        self.id_link = idlink
        self.list = map
        self.private = private
        self.alive = person.probably_alive() and restrict
        self.photos = (photos == 2) or (photos == 1 and not self.alive)
        self.usecomments = not uc
        self.dir = dir_name
        self.link = link
        self.mini_tree = mini_tree
        self.slist = []
        self.scnt = 1
        self.image_dir = imgdir
        self.depth = depth

        name = person.get_primary_name().get_regular_name()
        self.doc.set_title(_("Summary of %s") % name)
        self.doc.fix_title()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_normal_row(self,label,data,sreflist):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(label)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        self.doc.write_text(data)
        if sreflist:
            first = 1
            for sref in sreflist:
                self.doc.write_raw('<SUP>')
                if first:
                    first = 0
                else:
                    self.doc.write_text(', ')
                self.doc.start_link("#s%d" % self.scnt)
                self.doc.write_text('%d' % self.scnt)
                self.doc.end_link()
                self.doc.write_raw('</SUP>')
                self.scnt = self.scnt + 1
                self.slist.append(sref)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_id_row(self,label,data):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(label)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        self.doc.write_raw(data)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_marriage_row(self,list):
        self.doc.start_row()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(list[0])
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        self.doc.write_text(list[1])
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.end_row()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_link_row(self,title,person_id):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(title)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        if person_id:
            person = self.db.find_person_from_id(person_id)
            if self.list.has_key(person.get_id()):
                self.doc.start_link("%s.%s" % (person.get_id(),self.ext))
                self.doc.write_text(person.get_primary_name().get_regular_name())
                self.doc.end_link()
            else:
                self.doc.write_text(person.get_primary_name().get_regular_name())

        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

    def write_sources(self):
        self.doc.start_paragraph("SourcesTitle")
        self.doc.write_text(_("Sources"))
        self.doc.end_paragraph()

        index = 1
        for sref in self.slist:
            self.doc.start_paragraph("SourceParagraph")
            self.doc.write_linktarget("s%d" % index)
            self.doc.write_text('%d. ' % index)
            index = index + 1
            base_id = sref.get_base_id()
            base = self.db.find_source_from_id(base_id)
            self.write_info(base.get_title())
            self.write_info(base.get_author())
            self.write_info(base.get_publication_info())
            self.write_info(sref.get_date().get_date())
            self.write_info(sref.get_page())
            if self.usecomments:
                self.write_info(sref.get_text())
                self.write_info(sref.get_comments())
            self.doc.end_paragraph()

    def write_info(self,info):
        """Writes a line of text, after stripping leading and trailing
           spaces. If the last character is not a period, the period is
           appended to produce a sentance"""
        
        info = info.strip()
        if info != "":
            if info[-1] == '.':
                self.doc.write_text("%s " % info)
            else:
                self.doc.write_text("%s. " % info)
                
    def write_tree(self,ind_list):
        if not self.mini_tree or not self.person.get_main_parents_family_id():
            return
        self.doc.start_paragraph("FamilyTitle")
        self.doc.end_paragraph()

        self.doc.start_paragraph("Data")
        self.doc.write_raw('<PRE>\n')
        tree = MiniTree(self.db,self.person,self.doc,ind_list,self.depth)
        for line in tree.lines:
            if line: self.doc.write_raw(line + '\n')
        self.doc.write_raw('</PRE>\n')
        self.doc.end_paragraph()

    def create_page(self,ind_list):
        """Generate the HTML page for the specific person"""
        
        filebase = "%s.%s" % (self.person.get_id(),self.ext)
        self.doc.open("%s/%s" % (self.dir,filebase))

        media_list = self.person.get_media_list()
        name_obj = self.person.get_primary_name()
        name = name_obj.get_regular_name()

        # Write out the title line.
        
        self.doc.start_paragraph("Title")
        self.doc.write_text(_("Summary of %s") % name)
        self.doc.end_paragraph()

        # blank line for spacing

        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()

        # look for the primary media object if photos have been requested.
        # make sure that the media object is an image. If so, insert it
        # into the document.
        
        if self.photos and len(media_list) > 0:
            object_id = media_list[0].get_reference_id()
            object = self.database.find_object_from_id(object_id)
            if object.get_mime_type()[0:5] == "image":
                src = object.get_path()
                junk,ext = os.path.splitext(src)
                base = '%s%s' % (object.get_id(),ext)

                if os.path.isfile(src):
                    self.doc.start_paragraph("Data")
                    if self.image_dir:
                        self.doc.start_link("%s/%s" % (self.image_dir,base))
                    else:
                        self.doc.start_link("%s" % base)
                    description = object.get_description()
                    self.doc.add_media_object(src,"row",4.0,4.0,description)
                    self.doc.end_link()
                    self.doc.end_paragraph()

        # Start the first table, which consists of basic information, including
        # name, gender, and parents
        
        self.doc.start_table("one","IndTable")
        self.write_normal_row("%s:" % _("Name"), name, name_obj.get_source_references())
        if self.use_id:
            if self.id_link:
                val = '<a href="%s">%s</a>' % (self.id_link,self.person.get_id())
                val = val.replace('*',self.person.get_id())
            else:
                val = self.person.get_id()
            self.write_id_row("%s:" % _("ID Number"),val)
            
        if self.person.get_gender() == RelLib.Person.male:
            self.write_normal_row("%s:" % _("Gender"), _("Male"),None)
        elif self.person.get_gender() == RelLib.Person.female:
            self.write_normal_row("%s:" % _("Gender"), _("Female"),None)
        else:
            self.write_normal_row("%s:" % _("Gender"), _("Unknown"),None)

        family_id = self.person.get_main_parents_family_id()
        if family_id:
            family = self.db.find_family_from_id(family_id)
            self.write_link_row("%s:" % _("Father"), family.get_father_id())
            self.write_link_row("%s:" % _("Mother"), family.get_mother_id())
        else:
            self.write_link_row("%s:" % _("Father"), None)
            self.write_link_row("%s:" % _("Mother"), None)
        self.doc.end_table()

        # Another blank line between the tables
        
        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()
        
        self.write_facts()
        self.write_notes()
        self.write_families()

        # if inclusion of photos has been enabled, write the photo
        # gallery.

        if self.photos:
            self.write_gallery()

        # write source information
        
        if self.scnt > 1:
            self.write_sources()

        # draw mini-tree
        self.write_tree(ind_list)

        if self.link:
            self.doc.start_paragraph("Data")
            self.doc.start_link("index.%s" % self.ext)
            self.doc.write_text(_("Return to the index of people"))
            self.doc.end_link()
            self.doc.end_paragraph()

    def close(self):
        """Close the document"""
        self.doc.close()

    def write_gallery(self):
        """Write the image gallery. Add images that are not marked
           as private, creating a thumbnail and copying the original
           image to the directory."""

        # build a list of the images to add, but skip the first image,
        # since it has been used at the top of the page.
        
        my_list = []
        for object_ref in self.person.get_media_list():
            object = self.database.find_object_from_id(object_ref.get_ref())
            if object.get_mime_type()[0:5] == "image":
                if object.get_privacy() == 0:
                    my_list.append(object)
            
        # if no images were found, return
        
        if len(my_list) == 0:
            return

        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()

        self.doc.start_paragraph("GalleryTitle")
        self.doc.write_text(_("Gallery"))
        self.doc.end_paragraph()

        self.doc.start_table("gallery","IndTable")
        index = 0
        for obj_id in my_list:
            try:
                obj = self.database.find_object_from_id(obj_id)
                src = obj.get_reference().get_path()
                junk,ext = os.path.splitext(src)
                base = '%s%s' % (obj.get_reference().get_id(),ext)
                
                if self.image_dir:
                    shutil.copyfile(src,"%s/%s/%s" % (self.dir,self.image_dir,base))
                    try:
                        shutil.copystat(src,"%s/%s/%s" % (self.dir,self.image_dir,base))
                    except:
                        pass
                else:
                    shutil.copyfile(src,"%s/%s" % (self.dir,base))
                    try:
                        shutil.copystat(src,"%s/%s" % (self.dir,base))
                    except:
                        pass

                # First image should not appear in the gallery, but needs
                # the source to be linked to, hence the copy-only.
                if index == 0: 
                    index = 1
                    continue

                description = obj.get_reference().get_description()

                self.doc.start_row()
                self.doc.start_cell("ImageCell")
                self.doc.start_paragraph("Data")
                if self.image_dir:
                    self.doc.start_link("%s/%s" % (self.image_dir,base))
                else:
                    self.doc.start_link("%s" % base)
                self.doc.add_media_object(src,"row",1.5,1.5,description)
                self.doc.end_link()
                
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.start_cell("NoteCell")
                if description != "":
                    self.doc.start_paragraph("PhotoDescription")
                    self.doc.write_text(description)
                    self.doc.end_paragraph()
                if obj.get_note() != "":
                    self.doc.write_note(obj.get_note(),obj.get_note_format(),"PhotoNote")
                elif obj.get_reference().get_note() != "":
                    self.doc.write_note(obj.get_reference().get_note(),obj.get_reference().get_note_format(),"PhotoNote")
                self.doc.end_cell()
                self.doc.end_row()
            except IOError:
                pass
        self.doc.end_table()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_facts(self):

        if self.alive:
            return
        count = 0
        
        event_list = [ self.person.get_birth(), self.person.get_death() ]
        event_list = event_list + self.person.get_event_list()
        event_list.sort(by_date)
        for event in event_list:
            if event.get_privacy():
                continue
            name = _(event.get_name())
            date = event.get_date()
            descr = event.get_description()
            place_id = event.get_place_id()
            if place_id:
                place = self.db.find_place_from_id(place_id).get_title()
            else:
                place = ""
            srcref = event.get_source_references()

            if date == "" and descr == "" and place == "" and len(srcref) == 0:
                continue

            if count == 0:
                self.doc.start_paragraph("EventsTitle")
                self.doc.write_text(_("Facts and Events"))
                self.doc.end_paragraph()
                self.doc.start_table("two","IndTable")
                count = 1

            if place != "" and place[-1] == ".":
                place = place[0:-1]
            if descr != "" and descr[-1] == ".":
                descr = descr[0:-1]

            if date != "":
                if place != "":
                    val = "%s, %s." % (date,place)
                else:
                    val = "%s." % date
            elif place != "":
                val = "%s." % place
            else:
                val = ""
                
            if descr != "":
                val = val + ("%s." % descr)

            self.write_normal_row(name, val, srcref)

        if count != 0:
            self.doc.end_table()

    def write_notes(self):

        if self.person.get_note() == "" or self.alive:
            return
        
        self.doc.start_paragraph("NotesTitle")
        self.doc.write_text(_("Notes"))
        self.doc.end_paragraph()

        self.doc.write_note(self.person.get_note(),self.person.get_note_format(),"NotesParagraph")

    def write_fam_fact(self,event):

        if event == None:
            return
        name = _(event.get_name())
        date = event.get_date()
        place_id = event.get_place_id()
        if place_id:
            place = self.db.find_place_from_id(place_id).get_title()
        else:
            place = ""
        descr = event.get_description()
        if descr != "" and descr[-1] == ".":
            descr = descr[0:-1]
        if place != "" and place[-1] == ".":
            place = place[0:-1]

        if date == "" and place == "" and descr == "":
            return
        
        if date == "":
            if place == "":
                if descr == "":
                    val = ""
                else:
                    val = "%s." % descr
            else:
                if descr == "":
                    val = "%s." % place
                else:
                    val = "%s. %s." % (place,descr)
        else:
            if place == "":
                if descr == "":
                    val = "%s." % date
                else:
                    val = "%s. %s." % (date,descr)
            else:
                if descr == "":
                    val = "%s, %s." % (date,place)
                else:
                    val = "%s, %s. %s." % (date,place,descr)

        self.write_marriage_row([name, val])

    def write_families(self):
        if len(self.person.get_family_id_list()) == 0:
            return
        
        self.doc.start_paragraph("FamilyTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()

        self.doc.start_table("three","IndTable")
        
        for family_id in self.person.get_family_id_list():
            family = self.db.find_family_from_id(family_id)
            if self.person.get_id() == family.get_father_id():
                spouse_id = family.get_mother_id()
            else:
                spouse_id = family.get_father_id()
            self.doc.start_row()
            self.doc.start_cell("NormalCell",2)
            self.doc.start_paragraph("Spouse")
            if spouse_id:
                spouse = self.db.find_person_from_id(spouse_id)
                if self.list.has_key(spouse_id):
                    self.doc.start_link("%s.%s" % (spouse_id,self.ext))
                    self.doc.write_text(spouse.get_primary_name().get_regular_name())
                    self.doc.end_link()
                else:
                    self.doc.write_text(spouse.get_primary_name().get_regular_name())
            else:
                self.doc.write_text(_("unknown"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            if not self.alive:
                for event in family.get_event_list():
                    if event.get_privacy() == 0:
                        self.write_fam_fact(event)

            child_list = family.get_child_id_list()
            if len(child_list) > 0:
                
                self.doc.start_row()
                self.doc.start_cell("NormalCell")
                self.doc.start_paragraph("Label")
                self.doc.write_text(_("Children"))
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell("NormalCell")
                self.doc.start_paragraph("Data")
                
                first = 1
                for child_id in family.get_child_id_list():
                    child = self.db.find_person_from_id(child_id)
                    name = child.get_primary_name().get_regular_name()
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    if self.list.has_key(child_id):
                        self.doc.start_link("%s.%s" % (child_id,self.ext))
                        self.doc.write_text(name)
                        self.doc.end_link()
                    else:
                        self.doc.write_text(name)
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()

#------------------------------------------------------------------------
#
# WebReport
#
#------------------------------------------------------------------------
class WebReport(Report.Report):
    def __init__(self,db,person,target_path,max_gen,photos,filter,restrict,
                 private, srccomments, include_link, include_mini_tree,
                 style, image_dir, template_name,use_id,id_link,gendex,ext,
                 include_alpha_links,separate_alpha,n_cols,ind_template_name,depth):
        self.db = db
        self.ext = ext
        self.use_id = use_id
        self.id_link = id_link
        self.person = person
        self.target_path = target_path
        self.max_gen = max_gen
        self.photos = photos
        self.filter = filter
        self.restrict = restrict
        self.private = private
        self.srccomments = srccomments
        self.include_link = include_link
        self.include_mini_tree = include_mini_tree
        self.selected_style = style
        self.image_dir = image_dir
        self.use_gendex = gendex
        self.template_name = template_name
        self.include_alpha_links = include_alpha_links
        self.separate_alpha = separate_alpha
        self.n_cols = n_cols
        self.ind_template_name = ind_template_name
        self.depth = depth

    def get_progressbar_data(self):
        return (_("Generate HTML reports - GRAMPS"), _("Creating Web Pages"))
    
    def make_date(self,date):
        start = date.get_start_date()
        if date.is_empty():
            val = date.get_text()
        elif date.isRange():
            val = "FROM %s TO %s" % (self.subdate(start),
                                     self.subdate(date.get_stop_date()))
        else:
            val = self.subdate(start)
        return val

    def subdate(self,subdate):
        retval = ""
        day = subdate.getDay()
        mon = subdate.getMonth()
        year = subdate.getYear()
        mode = subdate.getModeVal()
        day_valid = subdate.getDayValid()
        mon_valid = subdate.getMonthValid()
        year_valid = subdate.getYearValid()
        
        if not day_valid:
            try:
                if not mon_valid:
                    retval = str(year)
                elif not year_valid:
                    retval = _month[mon]
                else:
                    retval = "%s %d" % (_month[mon],year)
            except IndexError:
                print "Month index error - %d" % mon
                retval = str(year)
        elif not mon_valid:
            retval = str(year)
        else:
            try:
                month = _month[mon]
                if not year_valid:
                    retval = "%d %s ????" % (day,month)
                else:
                    retval = "%d %s %d" % (day,month,year)
            except IndexError:
                print "Month index error - %d" % mon
                retval = str(year)
        if mode == Date.Calendar.ABOUT:
            retval = "ABT %s"  % retval
        elif mode == Date.Calendar.BEFORE:
            retval = "BEF %s" % retval
        elif mode == Date.Calendar.AFTER:
            retval = "AFT %s" % retval
        return retval

    def dump_gendex(self,person_list,html_dir):
        fname = "%s/gendex.txt" % html_dir
        try:
            f = open(fname,"w")
        except:
            return
        for p in person_list:
            name = p.get_primary_name()
            firstName = name.get_first_name()
            surName = name.get_surname()
            suffix = name.get_suffix()

            f.write("%s.%s|" % (p.get_id(),self.ext))
            f.write("%s|" % surName)
            if suffix == "":
                f.write("%s /%s/|" % (firstName,surName))
            else:
                f.write("%s /%s/, %s|" % (firstName,surName, suffix))
            for e in [p.get_birth(),p.get_death()]:
                if e:
                    f.write("%s|" % self.make_date(e.get_date_object()))
                    if e.get_place_id():
                        f.write('%s|' % e.get_place_id().get_title())
                    else:
                        f.write('|')
                else:
                    f.write('||')
            f.write('\n')
        f.close()

    def dump_index(self,person_list,styles,template,html_dir):
        """Writes an index file, listing all people in the person list."""
    
        doc = HtmlLinkDoc(self.selected_style,None,template,None)
        doc.set_extension(self.ext)
        doc.set_title(_("Family Tree Index"))
    
        doc.open("%s/index.%s" % (html_dir,self.ext))
        doc.start_paragraph("Title")
        doc.write_text(_("Family Tree Index"))
        doc.end_paragraph()
    
        person_list.sort(sort.by_last_name)

        a = {}
        for person in person_list:
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
                p_list = [ p for p in person_list if \
                            (p.get_primary_name().get_surname() \
                            and (p.get_primary_name().get_surname()[0] == n) ) ]
                doc = HtmlLinkDoc(self.selected_style,None,template,None)
                doc.set_extension(self.ext)
                doc.set_title(_("Section %s") % n)

                doc.open("%s/index_%03d.%s" % (html_dir,a[n],self.ext))
                doc.start_paragraph("Title")
                doc.write_text(_("Section %s") % n)
                doc.end_paragraph()

                n_rows = len(p_list)/self.n_cols
                td_width = 100/self.n_cols

                doc.write_raw('<table width="100%" border="0">')
                doc.write_raw('<tr><td width="%d%%" valign="top">' % td_width)
                col_len = n_rows

                for person in p_list:
                    name = person.get_primary_name().get_name()

                    doc.start_link("%s.%s" % (person.get_id(),self.ext))
                    doc.write_text(name)
                    doc.end_link()

                    if col_len <= 0:
                        doc.write_raw('</td><td width="%d%%" valign="top">' % td_width)
                        col_len = n_rows
                    else:
                        doc.newline()
                    col_len = col_len - 1
                doc.write_raw('</td></tr></table>')
                doc.close()
        else:
            n_rows = len(person_list) + len(link_keys)
            n_rows = n_rows/self.n_cols
            td_width = 100/self.n_cols

            doc.write_raw('<table width="100%" border="0">')
            doc.write_raw('<tr><td width="%d%%" valign="top">' % td_width)
            col_len = n_rows
            for n in link_keys:
                p_list = [ p for p in person_list if \
                            (p.get_primary_name().get_surname() \
                            and (p.get_primary_name().get_surname()[0] == n) ) ]
                doc.start_paragraph('IndexLabel')
                if self.include_alpha_links:
                    doc.write_linktarget("%03d" % a[n])
                doc.write_text(n)
                doc.end_paragraph()
                col_len = col_len - 1

                for person in p_list:
                    name = person.get_primary_name().get_name()

                    doc.start_link("%s.%s" % (person.get_id(),self.ext))
                    doc.write_text(name)
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
    
        ind_list = self.filter.apply(self.db,self.db.get_person_id_map().values())
        self.progress_bar_setup(float(len(ind_list)))
        
        doc = HtmlLinkDoc(self.selected_style,None,self.template_name,None)
        doc.set_extension(self.ext)
        doc.set_image_dir(self.image_dir)
        
        self.add_styles(doc)
        doc.build_style_declaration()

        my_map = {}
        for l in ind_list:
            my_map[l.get_id()] = l
        for person in ind_list:
            tdoc = HtmlLinkDoc(self.selected_style,None,None,None,doc)
            tdoc.set_extension(self.ext)
            tdoc.set_keywords([person.get_primary_name().get_surname(),
                               person.get_primary_name().get_regular_name()])
            idoc = IndividualPage(self.db,person, self.photos, self.restrict,
                                  self.private, self.srccomments,
                                  self.include_link, self.include_mini_tree,
                                  my_map, dir_name, self.image_dir, tdoc,
                                  self.use_id,self.id_link,self.ext,self.depth)
            idoc.create_page(my_map)
            idoc.close()
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.mainiteration()
            
        if len(ind_list) > 1:
            self.dump_index(ind_list,self.selected_style,
                            self.ind_template_name,dir_name)
        if self.use_gendex == 1:
            self.dump_gendex(ind_list,dir_name)
        self.progress_bar_done()

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
class WebReportDialog(Report.ReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.ReportDialog.__init__(self,database,person, self.report_options)

    def add_user_options(self):
        lnk_msg = _("Include a link to the index page")
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        no_img_msg = _("Do not use images")
        no_limg_msg = _("Do not use images for living people")
        no_com_msg = _("Do not include comments and text in source information")
        include_id_msg = _("Include the GRAMPS ID in the report")
        gendex_msg = _("Create a GENDEX index")
        imgdir_msg = _("Image subdirectory")
        depth_msg = _("Ancestor tree depth")
        ext_msg = _("File extension")
        alpha_links_msg = _("Links to alphabetical sections in index page")
        sep_alpha_msg = _("Split alphabetical sections to separate pages")

        tree_msg = _("Include short ancestor tree")
        self.mini_tree = gtk.CheckButton(tree_msg)
        self.mini_tree.set_active(1)
        self.depth = gtk.SpinButton()
        self.depth.set_digits(0)
        self.depth.set_increments(1,2)
        self.depth.set_range(1,10)
        self.depth.set_numeric(gtk.TRUE)
        self.depth.set_value(3)

        self.use_link = gtk.CheckButton(lnk_msg)
        self.use_link.set_active(1) 
        self.no_private = gtk.CheckButton(priv_msg)
        self.no_private.set_active(1)
        self.restrict_living = gtk.CheckButton(restrict_msg)
        self.no_images = gtk.CheckButton(no_img_msg)
        self.no_living_images = gtk.CheckButton(no_limg_msg)
        self.no_comments = gtk.CheckButton(no_com_msg)
        self.include_id = gtk.CheckButton(include_id_msg)
        self.gendex = gtk.CheckButton(gendex_msg)
        self.imgdir = gtk.Entry()
        self.imgdir.set_text("images")
        self.linkpath = gtk.Entry()
        self.linkpath.set_sensitive(0)
        self.include_id.connect('toggled',self.show_link)
        self.ext = gtk.Combo()
        self.ext.set_popdown_strings(['.html','.htm','.php','.php3',
                                      '.cgi'])

        self.use_alpha_links = gtk.CheckButton(alpha_links_msg)
        self.use_sep_alpha = gtk.CheckButton(sep_alpha_msg)
        self.use_sep_alpha.set_sensitive(0)
        self.use_n_cols = gtk.SpinButton()
        self.use_n_cols.set_value(2)
        self.use_n_cols.set_digits(0)
        self.use_n_cols.set_increments(1,2)
        self.use_n_cols.set_range(1,5)
        self.use_n_cols.set_numeric(gtk.TRUE)
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

        self.add_option(imgdir_msg,self.imgdir)
        self.add_option('',self.mini_tree)
        self.add_option(depth_msg,self.depth)
        self.add_option('',self.use_link)

        self.mini_tree.connect('toggled',self.on_mini_tree_toggled)

        self.use_alpha_links.connect('toggled',self.on_use_alpha_links_toggled)
        self.ind_template.entry.connect('changed',self.ind_template_changed)

        title = _("Privacy")
        self.add_frame_option(title,None,self.no_private)
        self.add_frame_option(title,None,self.restrict_living)
        self.add_frame_option(title,None,self.no_images)
        self.add_frame_option(title,None,self.no_living_images)
        self.add_frame_option(title,None,self.no_comments)

        title = _('Index page')
        self.add_frame_option(title,_('Template'),self.ind_template)
        self.add_frame_option(title,_("User Template"),self.ind_user_template)
        self.add_frame_option(title,None,self.use_alpha_links)
        self.add_frame_option(title,None,self.use_sep_alpha)
        self.add_frame_option(title,_('Number of columns'),self.use_n_cols)

        title = _('Advanced')
        self.add_frame_option(title,'',self.include_id)
        self.add_frame_option(title,_('GRAMPS ID link URL'),self.linkpath)
        self.add_frame_option(title,'',self.gendex)
        self.add_frame_option(title,ext_msg,self.ext)

        self.no_images.connect('toggled',self.on_nophotos_toggled)

    def show_link(self,obj):
        self.linkpath.set_sensitive(obj.get_active())

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
    
    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "webpage.xml"
    
    def get_report_generations(self):
        """No generations, no page break box."""
        return (0, 0)

    def get_report_filters(self):
        """Set up the list of possible content filters."""

        name = self.person.get_primary_name().get_name()
        
        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Direct Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([self.person.get_id()]))

        df = GenericFilter.GenericFilter()
        df.set_name(_("Descendant Families of %s") % name)
        df.add_rule(GenericFilter.IsDescendantFamilyOf([self.person.get_id()]))
        
        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([self.person.get_id()]))

        return [all,des,df,ans]

    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return GrampsCfg.web_dir
    
    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        GrampsCfg.web_dir = value
    
    def make_default_style(self):
        """Make the default output style for the Web Pages Report."""
        font = BaseDoc.FontStyle()
        font.set(bold=1, face=BaseDoc.FONT_SANS_SERIF, size=16)
        p = BaseDoc.ParagraphStyle()
        p.set(align=BaseDoc.PARA_ALIGN_CENTER,font=font)
        p.set_description(_("The style used for the title of the page."))
        self.default_style.add_style("Title",p)
        
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header that identifies "
                            "facts and events."))
        self.default_style.add_style("EventsTitle",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the notes section."))
        self.default_style.add_style("NotesTitle",p)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=10)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,align=BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the copyright notice."))
        self.default_style.add_style("Copyright",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the sources section."))
        self.default_style.add_style("SourcesTitle",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font)
        p.set_description(_("The style used on the index page that labels each section."))
        self.default_style.add_style("IndexLabel",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,align=BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used on the index page that labels links to each section."))
        self.default_style.add_style("IndexLabelLinks",p)

        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the image section."))
        self.default_style.add_style("GalleryTitle",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set(font=font,bborder=1)
        p.set_description(_("The style used for the header for the marriages "
                            "and children section."))
        self.default_style.add_style("FamilyTitle",p)
        
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the spouse's name."))
        self.default_style.add_style("Spouse",p)
    
        font = BaseDoc.FontStyle()
        font.set(size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the general data labels."))
        self.default_style.add_style("Label",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the general data."))
        self.default_style.add_style("Data",p)
    
        font = BaseDoc.FontStyle()
        font.set(bold=1,face=BaseDoc.FONT_SANS_SERIF,size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the description of images."))
        self.default_style.add_style("PhotoDescription",p)
    
        font = BaseDoc.FontStyle()
        font.set(size=12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the notes associated with images."))
        self.default_style.add_style("PhotoNote",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(10)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the source information."))
        self.default_style.add_style("SourceParagraph",p)
    
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_description(_("The style used for the note information."))
        self.default_style.add_style("NotesParagraph",p)

    #------------------------------------------------------------------------
    #
    # Functions related to selecting/changing the current file format
    #
    #------------------------------------------------------------------------
    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass


    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame (HTML only)"""
        pass
    
    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window
    #
    #------------------------------------------------------------------------
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        self.output_notebook.set_current_page(1)

    #------------------------------------------------------------------------
    #
    # Functions related to retrieving data from the dialog window
    #
    #------------------------------------------------------------------------

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        pass
    
    def parse_report_options_frame(self):
        """Parse the report options frame of the dialog.  Save the
        user selected choices for later use."""
        Report.ReportDialog.parse_report_options_frame(self)
        self.include_link = self.use_link.get_active()
        self.include_mini_tree = self.mini_tree.get_active()

    def parse_other_frames(self):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        self.restrict = self.restrict_living.get_active()
        self.private = self.no_private.get_active()
        self.img_dir_text = unicode(self.imgdir.get_text())
        self.depth_value = self.depth.get_value()

        self.html_ext = unicode(self.ext.entry.get_text().strip())
        if self.html_ext[0] == '.':
            self.html_ext = self.html_ext[1:]
        self.use_id = self.include_id.get_active()
        self.use_gendex = self.gendex.get_active()
        self.id_link = unicode(self.linkpath.get_text().strip())
        self.srccomments = self.no_comments.get_active()
        if self.no_images.get_active() == 1:
            self.photos = 0
        elif self.no_living_images.get_active() == 1:
            self.photos = 1
        else:
            self.photos = 2

        text = unicode(self.ind_template.entry.get_text())
        if Report._template_map.has_key(text):
            if text == Report._user_template:
                self.ind_template_name = self.ind_user_template.get_full_path(0)
            else:
                self.ind_template_name = "%s/%s" % (const.template_dir,Report._template_map[text])
        else:
            self.ind_template_name = None
        self.include_alpha_links = self.use_alpha_links.get_active()
        if self.include_alpha_links:
            self.separate_alpha = self.use_sep_alpha.get_active()
        else:
            self.separate_alpha = 0
        self.n_cols = self.use_n_cols.get_value()

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def on_nophotos_toggled(self,obj):
        """Keep the 'restrict photos' checkbox in line with the 'no
        photos' checkbox.  If there are no photos included, it makes
        no sense to worry about restricting which photos are included,
        now does it?"""
        if obj.get_active():
            self.no_living_images.set_sensitive(0)
        else:
            self.no_living_images.set_sensitive(1)

    def on_use_alpha_links_toggled(self,obj):
        """Keep the 'split alpha sections to separate pages' checkbox in 
        line with the 'use alpha links' checkbox.  If there are no alpha
        links included, it makes no sense to worry about splitting or not
        the alpha link target to separate pages."""
        if obj.get_active():
            self.use_sep_alpha.set_sensitive(1)
        else:
            self.use_sep_alpha.set_sensitive(0)

    def on_mini_tree_toggled(self,obj):
        """Keep the 'Mini tree depth' spin button in line with 
        the 'include short tree' checkbox.  If there is no mini tree included, 
        it makes no sense to worry about its depth."""
        if obj.get_active():
            self.depth.set_sensitive(1)
        else:
            self.depth.set_sensitive(0)

    def ind_template_changed(self,obj):
        text = unicode(obj.get_text())
        if Report._template_map.has_key(text):
            if Report._template_map[text]:
                self.ind_user_template.set_sensitive(0)
            else:
                self.ind_user_template.set_sensitive(1)
        else:
            self.ind_user_template.set_sensitive(0)

    #------------------------------------------------------------------------
    #
    # Functions related to creating the actual report document.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the web pages."""

        try:
            MyReport = WebReport(self.db, self.person, self.target_path,
                                 self.max_gen, self.photos, self.filter,
                                 self.restrict, self.private, self.srccomments,
                                 self.include_link, self.include_mini_tree,
                                 self.selected_style,
                                 self.img_dir_text,self.template_name,
                                 self.use_id,self.id_link,self.use_gendex,
                                 self.html_ext,self.include_alpha_links,
                                 self.separate_alpha,self.n_cols,
                                 self.ind_template_name,self.depth_value)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

class MiniTree:
    """
    This is one dirty piece of code, that is why I made it it's own
    class.  I'm sure that someone with more knowledge of GRAMPS can make
    it much cleaner.
    """
    def __init__(self,db,person,doc,map,depth):
        self.map = map
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

        if person and person.get_id() and self.map.has_key(person.get_id()):
            self.lines_map[position] += "<A HREF='%s%s'>%s</A>" % (person.get_id(),
                                                           self.doc.ext, name)
        else:
            self.lines_map[position] += "<U>%s</U>" % name

        # We are done with this generation
        generations = generations - 1
        if not generations: return

        offset = 2**(generations-1)

        family_id = person.get_main_parents_family_id()
        if not family_id: return

        family = self.db.find_family_from_id(family_id)
        father_id = family.get_father_id()
        mother_id = family.get_mother_id()

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

        if father_id:
            father = self.db.find_person_from_id(father_id)
            next_pos = position - offset 
            self.lines_map[position] += '|'
            self.draw_parents(father,next_pos,father_indent,generations,1)
            
        if mother_id:
            mother = self.db.find_person_from_id(mother_id)
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
        if person and person.get_id() and self.map.has_key(person.get_id()):
            self.lines[line] += "<A HREF='%s%s'>%s</A>" % (person.get_id(),
                                                           self.doc.ext, name)
        else:
            self.lines[line] += "<U>%s</U>" % name

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    WebReportDialog(database,person)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #191B1E",
        "+	c #746F5F",
        "@	c #6EA2C9",
        "#	c #F2E8DA",
        "$	c #B4A766",
        "%	c #2F383A",
        "&	c #9F8F53",
        "*	c #BBB774",
        "=	c #6E614B",
        "-	c #506E8C",
        ";	c #2B559A",
        ">	c #E1CB95",
        ",	c #5992CD",
        "'	c #5A584F",
        ")	c #86827D",
        "!	c #CBCAC7",
        "~	c #294A76",
        "{	c #E3D0B6",
        "]	c #7B7D7C",
        "^	c #D5BE97",
        "/	c #FBFAF8",
        "(	c #EADECB",
        "_	c #4E84C7",
        ":	c #474943",
        "<	c #95A992",
        "[	c #ADA69B",
        "}	c #3F72B7",
        "|	c #C4A985",
        "1	c #9B9383",
        "2	c #213C60",
        "3	c #BBB9AF",
        "4	c #7F959D",
        "            )11)1))))))]]+++=='=''              ",
        "            13!!!{!!!!^!!!!!33[<]')=            ",
        "            1!////////////#/##!![]<4:           ",
        "            1!////////////////#(![[3):          ",
        "            )!////////////////##(33(3]%         ",
        "            1!//////////////////#3</!3]%        ",
        "            1!///////////////////3[//{3]%       ",
        "            )[<<33<3#////////////!4///(3)%      ",
        "           ::';__]}-)+[//////////!1(#//{3):     ",
        "          =$$&1$<<_}}::2!#///////{-:::'-]]':    ",
        "        :)&^^^^**<__};-:~-(////////{!331]]:%    ",
        "       ~=|^^>>>$4,4<,};;~2-#///////#!!331)=:    ",
        "      ;-$>>>>>>><@4<*];}~22;!///////#!!33[]'    ",
        "     ;_@>>##((>>*@4$*<-;;~2%-!#/////#((!33):.   ",
        "    ~},<(##(##(>>*$*$+-;;~22%[##/////#(!!^1'.   ",
        "    -_@!(####(>>>>**$-}};;2222!(#////#(({3['.   ",
        "   ;}_,!##//#(>(>**&&]}}};2222)!(#/#/##{!![=.   ",
        "   ;_,@>/#//##>>>^$)}}}};;~22%;!!(/#/##({^['.   ",
        "   ;_,@!#///#>>>>*&__}}};;;22.:<!!##/##((![=.   ",
        "  ';_,@>###/#>>>*&___}_};;~22%%+3!(####({{|'.   ",
        "  ~}_,@@(###><<<$4,_,_}}};;22%.+[!{###(({{[=.   ",
        "  2},,,@*#((@@@@4,_,___};;~22%%+[3!(###({{|=.   ",
        "  ~}_,,@@*(><@<@@4,,_}}};;~2.2.-[3!{(##({{[=.   ",
        "  2;_,,,@@*>*<*,,,____}};~~2.%%'[[!{((#({{|=.   ",
        "  ~}__,@,@,<*!<,___}}}};;~~22..-[[3{((((({[=.   ",
        "   ;}_,,,@@@,<<<_}}}}}};;~2222%+[[!{(((({{|=.   ",
        "   ~}}_,,,@,,,,<}]44};;;;222..:11[^!((({{{|=.   ",
        "   ;;}_,,,,@@@,,$&&&)-;22222.2'1[[^{{{(({{|=.   ",
        "    ;}}___,,,,_)&<&&+='~222..211[[^{({{({>|=.   ",
        "    ~;}}____,__&&&&+++'22.2.%=11[3^{({({{>|=.   ",
        "     ;}}}}}}}}}]&&]+=:::22..2)11|3{{{{{{{{|=.   ",
        "      ;;}}}}}}}=]]+='::%%.2%)11[|^{{({{{>>|=.   ",
        "       ;;;;;};;;=''::::%.%.)11[[|!>{{>{>>>|=.   ",
        "        ;;;};;;~%::%%:%%%%1111[|^{{({{>{>>|=.   ",
        "         ~~;~;~~2%:%%%%.=]11[[|3{{{{{{{>>^|=.   ",
        "           '~~~~%%:%%.')1111[[^^>{{{{>>>>^|=.   ",
        "            :+-''::'&111[1[||3{{{{{>>>>^>^|=.   ",
        "            '1*$[$[1[1[1[[[3^^{{{{{>{>^>^^|=.   ",
        "            '<333[[[[[[||3^^{{{{{{>>>^>^^^|=.   ",
        "            '3({!!^^3^3^^!{{{{{{{>>>>^>^^^|=.   ",
        "            =3((({!{!{!{{{{{{{{{>>>^^>^^^^|=.   ",
        "            '3###((({(({((({{{{{>{>>^^^^^^|=.   ",
        "            =3!!!!!^!^^^^|^^|^|||||||||||||'.   ",
        "            :++++++=+======================:.   ",
        "               .............................    ",
        "                                                ",
        "                                                ",
        "                                                "]


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Generate Web Site"),
    category=_("Web Page"),
    status=(_("Beta")),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    xpm=get_xpm_image()
    )

