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
import RelLib
import HtmlDoc
import BaseDoc
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

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_month = [
    "",    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]

_hline = " "    # Everything is underlined, so use blank
_BORN = _('b.')

_ext = ['.html','.htm','.php','.php3','.cgi']

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

    def __init__(self,db,person,photos,restrict,private,uc,link,places,mini_tree,map,
                 dir_name,imgdir,doc,id,idlink,ext,depth):
        self.person = person
        self.db = db
        self.ext = ext
        self.doc = doc
        self.use_id = id
        self.id_link = idlink
        self.list = map
        self.private = private
        self.alive = Utils.probably_alive(person,db) and restrict
        self.photos = (photos == 2) or (photos == 1 and not self.alive)
        self.usecomments = not uc
        self.dir = dir_name
        self.link = link
        self.places = places
        self.mini_tree = mini_tree
        self.slist = []
        self.scnt = 1
        self.image_dir = imgdir
        self.depth = depth

        name = person.get_primary_name().get_regular_name()
        self.doc.set_title(_("Summary of %s") % name)
        self.doc.fix_title()
        self.sort = Sort.Sort(self.db)
        
    #------------------------------------------------------------------------
    #
    # 
    #
    #------------------------------------------------------------------------
    def write_flexible_row(self,label,data,sreflist=None):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(label)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        if len(data) > 0:
            for part in data:
                if part[1] != "":
                    self.doc.start_link(part[1])
                    self.doc.write_text(part[0])
                    self.doc.end_link()
                else:
                    self.doc.write_text(part[0])
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
    def write_normal_row(self,label,data,sreflist):
        val = []
        val.append((data,""))
        self.write_flexible_row(label,val,sreflist)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_id_row(self,label,data):
        val = []
        val.append((data,""))
        self.write_flexible_row(label,val)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_marriage_row(self,list):
        val = []
        val.append((list[1],""))
        self.write_flexible_row(list[0],val)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_link_row(self,title,person_handle):
        val = []
        if person_handle:
            person = self.db.get_person_from_handle(person_handle)
            if self.list.has_key(person_handle):
                val.append((person.get_primary_name().get_regular_name(),"%s.%s" % (person.get_gramps_id(),self.ext)))
            else:
                val.append((person.get_primary_name().get_regular_name(),""))

        self.write_flexible_row(title,val)

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
            base_handle = sref.get_base_handle()
            base = self.db.get_source_from_handle(base_handle)
            self.write_info(base.get_title())
            self.write_info(base.get_author())
            self.write_info(base.get_publication_info())
            self.write_info(DateHandler.displayer.display(sref.get_date_object()))
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
        if not self.mini_tree or not self.person.get_main_parents_family_handle():
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
        
        filebase = "%s.%s" % (self.person.get_gramps_id(),self.ext)
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
            object_handle = media_list[0].get_reference_handle()
            object = self.db.get_object_from_handle(object_handle)
            if object.get_mime_type()[0:5] == "image":
                src = object.get_path()
                junk,ext = os.path.splitext(src)
                base = '%s%s' % (object.get_gramps_id(),ext)

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
                val = '<a href="%s">%s</a>' % (self.id_link,self.person.get_gramps_id())
                val = val.replace('*',self.person.get_gramps_id())
            else:
                val = self.person.get_gramps_id()
            self.write_id_row("%s:" % _("ID Number"),val)
            
        if self.person.get_gender() == RelLib.Person.MALE:
            self.write_normal_row("%s:" % _("Gender"), _("Male"),None)
        elif self.person.get_gender() == RelLib.Person.FEMALE:
            self.write_normal_row("%s:" % _("Gender"), _("Female"),None)
        else:
            self.write_normal_row("%s:" % _("Gender"), _("Unknown"),None)

        family_handle = self.person.get_main_parents_family_handle()
        if family_handle:
            family = self.db.get_family_from_handle(family_handle)
            self.write_link_row("%s:" % _("Father"), family.get_father_handle())
            self.write_link_row("%s:" % _("Mother"), family.get_mother_handle())
        else:
            self.write_link_row("%s:" % _("Father"), None)
            self.write_link_row("%s:" % _("Mother"), None)
        self.doc.end_table()

        # Another blank line between the tables
        
        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()
        
        self.write_urls()
        self.write_facts()
        self.write_notes()
        self.write_families()
        self.write_sibling()

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
            if self.places:
                self.doc.newline()
                self.doc.start_link("loc.%s" % self.ext)
                self.doc.write_text(_("Return to the index of places"))
                self.doc.end_link()
            self.doc.end_paragraph()

    def close(self):
        """Close the document"""
        self.doc.close()

    def write_gallery(self):
        """Write the image gallery. Add images that are not marked
           as private, creating a thumbnail and copying the original
           image to the directory."""

        index = 0
        for object_ref in self.person.get_media_list():
            obj_id = object_ref.get_reference_handle()
            obj = self.db.get_object_from_handle(obj_id)
            if obj.get_mime_type()[0:5] != "image":
                continue
            if object_ref.get_privacy():
                continue

            try:
                src = obj.get_path()
                junk,ext = os.path.splitext(src)
                base = '%s%s' % (obj.get_gramps_id(),ext)
                
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
                elif index == 1:
                    # If there's a second image then we need to start out
                    # Gallery section and the table
                    self.doc.start_paragraph("Data")
                    self.doc.end_paragraph()

                    self.doc.start_paragraph("GalleryTitle")
                    self.doc.write_text(_("Gallery"))
                    self.doc.end_paragraph()

                    self.doc.start_table("gallery","IndTable")
                    index = 2

                description = obj.get_description()

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
                if description:
                    self.doc.start_paragraph("PhotoDescription")
                    self.doc.write_text(description)
                    self.doc.end_paragraph()
                if obj.get_note():
                    self.doc.write_note(obj.get_note(),obj.get_note_format(),"PhotoNote")
                elif object_ref.get_note():
                    self.doc.write_note(object_ref.get_note(),object_ref.get_note_format(),"PhotoNote")
                self.doc.end_cell()
                self.doc.end_row()
            except IOError:
                pass
        if index == 2:
            self.doc.end_table()
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_urls(self):

        first = 1

        for url in self.person.get_url_list():
            if url.get_privacy() and self.private:
                continue

            if first:
                first = 0    
                self.doc.start_paragraph("UrlTitle")
                self.doc.write_text(_("Links"))
                self.doc.end_paragraph()
                self.doc.start_paragraph("UrlList")

            self.doc.start_link(url.get_path())
            self.doc.write_text(url.get_description())
            self.doc.end_link()
            self.doc.newline()

        if not first:
            self.doc.end_paragraph()

    def write_facts(self):

        if self.alive:
            return
        count = 0
        
        event_handle_list = [ self.person.get_birth_handle(), self.person.get_death_handle() ]
        event_handle_list = event_handle_list + self.person.get_event_list()
        event_handle_list.sort(self.sort.by_date)
        for event_handle in event_handle_list:
            if not event_handle:
                continue
            event = self.db.get_event_from_handle(event_handle)
            if event.get_privacy():
                continue
            name = _(event.get_name())
            date_text = event.get_date()
            descr = event.get_description()
            place_handle = event.get_place_handle()
            place_url = ""
            if place_handle:
                place = self.db.get_place_from_handle(place_handle).get_title()
                if self.places:
                    place_gramps_id = self.db.get_place_from_handle(place_handle).get_gramps_id()
                    place_url = "loc.%s#%s" % (self.ext, place_gramps_id)
            else:
                place = ""
            srcref = event.get_source_references()

            if date_text == "" and descr == "" and place == "" and len(srcref) == 0:
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

            val = []
            
            if date_text != "":
                if place != "":
                    val.append(("%s, " % date_text,""))
                    val.append((place,place_url))
                    val.append((".",""))
                else:
                    val.append(("%s." % date_text,""))
            elif place != "":
                val.append((place,place_url))
                val.append((".",""))
                
            if descr != "":
                val.append(("%s." % descr,""))

            self.write_flexible_row(name, val, srcref)

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
        date_text = event.get_date()
        place_handle = event.get_place_handle()
        place_url = ""
        if place_handle:
            place = self.db.get_place_from_handle(place_handle).get_title()
            if self.places:
                place_gramps_id = self.db.get_place_from_handle(place_handle).get_gramps_id()
                place_url = "loc.%s#%s" % (self.ext, place_gramps_id)
        else:
            place = ""
        descr = event.get_description()
        if descr != "" and descr[-1] == ".":
            descr = descr[0:-1]
        if place != "" and place[-1] == ".":
            place = place[0:-1]

        if date_text == "" and place == "" and descr == "":
            return
        
        val = []
        if date_text == "":
            if place == "":
                if descr != "":
                    val.append(("%s." % descr,""))
            else:
                if descr == "":
                    val.append((place,place_url))
                    val.append((".",""))
                else:
                    val.append((place,place_url))
                    val.append((".",""))
                    val.append(("%s." % descr,""))
        else:
            if place == "":
                if descr == "":
                    val.append(("%s." % date_text,""))
                else:
                    val.append(("%s. %s." % (date_text,descr),""))
            else:
                if descr == "":
                    val.append(("%s, " % date_text,""))
                    val.append((place,place_url))
                    val.append((".",""))
                else:
                    val.append(("%s, " % date_text,""))
                    val.append((place,place_url))
                    val.append((".",""))
                    val.append(("%s." % descr,""))

        self.write_flexible_row(name, val)

    def write_families(self):
        if len(self.person.get_family_handle_list()) == 0:
            return
        
        self.doc.start_paragraph("FamilyTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()

        self.doc.start_table("three","IndTable")
        
        for family_handle in self.person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if self.person.get_handle() == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
            self.doc.start_row()
            self.doc.start_cell("NormalCell",2)
            self.doc.start_paragraph("Spouse")
            if spouse_id:
                spouse = self.db.get_person_from_handle(spouse_id)
                if self.list.has_key(spouse_id):
                    self.doc.start_link("%s.%s" % (spouse.get_gramps_id(),self.ext))
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
                for event_handle in family.get_event_list():
                    if event_handle:
                        event = self.db.get_event_from_handle(event_handle)
                        if event.get_privacy() == 0:
                            self.write_fam_fact(event)

            child_list = family.get_child_handle_list()
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
                for child_handle in family.get_child_handle_list():
                    child = self.db.get_person_from_handle(child_handle)
                    name = child.get_primary_name().get_regular_name()
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    if self.list.has_key(child_handle):
                        self.doc.start_link("%s.%s" % (child.get_gramps_id(),self.ext))
                        self.doc.write_text(name)
                        self.doc.end_link()
                    else:
                        self.doc.write_text(name)
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()

    def write_sibling(self):
        if len(self.person.get_parent_family_handle_list()) == 0:
            return
        
        """collect all siblings into an array"""
        all_sisters = []
        for (family_handle,mrel,frel) in self.person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if len( family.get_child_handle_list() ) > 0:
                for child_handle in family.get_child_handle_list():
                    all_sisters.append(child_handle)
        
        """if more than one person_handle exists, the person has siblings"""
        if len(all_sisters) > 1:
            self.doc.start_paragraph("SiblingsTitle")
            self.doc.write_text(_("Siblings"))
            self.doc.end_paragraph()
    
            self.doc.start_table("three","IndTable")
        
            for child_handle in all_sisters:
                child = self.db.get_person_from_handle(child_handle)
                self.doc.start_paragraph("Data")
                name = child.get_primary_name().get_regular_name()
                if self.person.get_handle() == child_handle:
                    self.doc.write_text(name)
                elif self.list.has_key(child_handle):
                    self.doc.start_link("%s.%s" % (child.get_gramps_id(),self.ext))
                    self.doc.write_text(name)
                    self.doc.end_link()
                else:
                    self.doc.write_text(name)
                self.doc.end_paragraph()
                

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
        
        doc = HtmlLinkDoc(self.selected_style,None,self.template_name,None)
        doc.set_extension(self.ext)
        doc.set_image_dir(self.image_dir)
        
        self.add_styles(doc)
        doc.build_style_declaration()

        my_map = {}
        for l in ind_list:
            my_map[l] = l
        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            tdoc = HtmlLinkDoc(self.selected_style,None,None,None,doc)
            tdoc.set_extension(self.ext)
            tdoc.set_keywords([person.get_primary_name().get_surname(),
                               person.get_primary_name().get_regular_name()])
            idoc = IndividualPage(self.database,person, self.photos, self.restrict,
                                  self.private, self.srccomments,
                                  self.include_link, self.use_places,
                                  self.include_mini_tree, my_map, dir_name,
                                  self.image_dir, tdoc, self.use_id,
                                  self.id_link, self.ext, self.depth)
            idoc.create_page(my_map)
            idoc.close()
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.mainiteration()
            
        if len(ind_list) > 1:
            self.dump_index(ind_list,self.selected_style,
                            self.ind_template_name,dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.mainiteration()
        if self.use_gendex == 1:
            self.dump_gendex(ind_list,dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.mainiteration()
        if self.use_places == 1:
            self.dump_places(ind_list,self.selected_style,
                            self.ind_template_name,dir_name)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.mainiteration()
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
        self.depth.set_numeric(True)
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

        the_ext = self.options_dict['HTMLext']
        self.ext = gtk.combo_box_new_text()
        index = 0
        active_index = 0
        for item in _ext:
            self.ext.append_text(item)
            if item == the_ext:
                active_index = index
            index = index + 1
        self.ext.set_active(active_index)

        self.use_alpha_links = gtk.CheckButton(alpha_links_msg)
        self.use_alpha_links.set_active(self.options_dict['HTMLlnktoalphabet'])

        self.use_sep_alpha = gtk.CheckButton(sep_alpha_msg)
        self.use_sep_alpha.set_sensitive(self.options_dict['HTMLlnktoalphabet'])
        self.use_sep_alpha.set_active(self.options_dict['HTMLsplita'])

        self.use_n_cols = gtk.SpinButton()
        self.use_n_cols.set_digits(0)
        self.use_n_cols.set_increments(1,2)
        self.use_n_cols.set_range(1,5)
        self.use_n_cols.set_numeric(True)
        self.use_n_cols.set_value(self.options_dict['HTMLidxcol'])

        tlist = Report._template_map.keys()
        tlist.sort()
        
        ind_template_name = self.options_dict['HTMLidxt']
        self.ind_template = gtk.combo_box_new_text()
        self.ind_template.append_text(Report._default_template)
        template_index = 1
        active_index = 0
        for template in tlist:
            if template != Report._user_template:
                self.ind_template.append_text(template)
                if Report._template_map[template] == ind_template_name:
                    active_index = template_index
                template_index = template_index + 1
        self.ind_template.append_text(Report._user_template)

        self.ind_user_template = gnome.ui.FileEntry("HTML_Template",_("Choose File"))
        if ind_template_name and not active_index:
            active_index = template_index
            user_template = ind_template_name
            self.ind_user_template.set_sensitive(1)
        else:
            user_template = ''
            self.ind_user_template.set_sensitive(0)

        if os.path.isfile(user_template):
            self.ind_user_template.set_filename(user_template)
        self.ind_user_template.set_modal(True)
        self.ind_template.set_active(active_index)

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
        self.ind_template.connect('changed',self.ind_template_changed)

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

        html_ext = _ext[self.ext.get_active()]
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

        active = self.ind_template.get_active()
        text = unicode(self.ind_template.get_model()[active][0])
        if Report._template_map.has_key(text):
            if text == Report._user_template:
                ind_template_name = self.ind_user_template.get_full_path(0)
            else:
                ind_template_name = "%s/%s" % (const.template_dir,Report._template_map[text])
        else:
            ind_template_name = ""
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
        active = obj.get_active()
        text = unicode(obj.get_model()[active][0])
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
        if response == True:
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
    translated_name = _("Generate Web Site"),
    status=(_("Beta")),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    )
