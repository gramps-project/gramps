
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Web Site/Generate Web Site"

from RelLib import *
from HtmlDoc import *

import const
import utils
import Config
import intl
_ = intl.gettext

import os
import re
import sort
import string
import time
import shutil

from gtk import *
from gnome.ui import *
from libglade import *
from Report import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def by_date(a,b):
    return compare_dates(a.getDateObj(),b.getDateObj())

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HtmlLinkDoc(HtmlDoc):

    def start_link(self,path):
        self.f.write('<A HREF="%s">' % path)

    def end_link(self):
        self.f.write('</A>')

    def newline(self):
        self.f.write('<BR>\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage:

    def __init__(self,person,photos,restrict,private,uc,link,map,dir_name,doc):
        self.person = person
        self.doc = doc
	self.list = map
        self.private = private
        self.alive = person.probablyAlive() and restrict
        self.photos = (photos == 2) or (photos == 1 and not self.alive)
        self.usecomments = not uc
        self.dir = dir_name
        self.link = link
        self.slist = []
        self.scnt = 1

        name = person.getPrimaryName().getRegularName()
        self.doc.set_title(_("Summary of %s") % name)

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
            for sref in sreflist:
                self.doc.start_link("#s%d" % self.scnt)
                self.doc.write_text("<SUP>%d</SUP>" % self.scnt)
                self.doc.end_link()
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
    def write_link_row(self,title,person):
        self.doc.start_row()
        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Label")
        self.doc.write_text(title)
        self.doc.end_paragraph()
        self.doc.end_cell()

        self.doc.start_cell("NormalCell")
        self.doc.start_paragraph("Data")
        if person:
            if self.list.has_key(person):
                self.doc.start_link("%s.html" % person.getId())
	        self.doc.write_text(person.getPrimaryName().getRegularName())
                self.doc.end_link()
            else:
	        self.doc.write_text(person.getPrimaryName().getRegularName())

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
            self.doc.write_text('<A NAME="s%d">%d. ' % (index,index))
            index = index + 1
            self.write_info(sref.getBase().getTitle())
            self.write_info(sref.getBase().getAuthor())
            self.write_info(sref.getBase().getPubInfo())
            self.write_info(sref.getDate().getDate())
            self.write_info(sref.getPage())
            if self.usecomments:
                self.write_info(sref.getText())
                self.write_info(sref.getComments())
            self.doc.end_paragraph()

    def write_info(self,info):
        """Writes a line of text, after stripping leading and trailing
           spaces. If the last character is not a period, the period is
           appended to produce a sentance"""
        
        info = string.strip(info)
        if info != "":
            if info[-1] == '.':
                self.doc.write_text("%s " % info)
            else:
                self.doc.write_text("%s. " % info)
                
    def create_page(self):
        """Generate the HTML page for the specific person"""
        
        filebase = "%s.html" % self.person.getId()
        self.doc.open("%s%s%s" % (self.dir,os.sep,filebase))

        photo_list = self.person.getPhotoList()
        name_obj = self.person.getPrimaryName()
        name = name_obj.getRegularName()

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
        
        if self.photos and len(photo_list) > 0:
            object = photo_list[0].getReference()
            if object.getMimeType()[0:5] == "image":
                file = object.getPath()
                self.doc.start_paragraph("Data")
                self.doc.add_photo(file,"row",4.0,4.0)
                self.doc.end_paragraph()

        # Start the first table, which consists of basic information, including
        # name, gender, and parents
        
        self.doc.start_table("one","IndTable")
        self.write_normal_row("%s:" % _("Name"), name, name_obj.getSourceRefList())
        if self.person.getGender() == Person.male:
            self.write_normal_row("%s:" % _("Gender"), _("Male"),None)
        else:
            self.write_normal_row("%s:" % _("Gender"), _("Female"),None)

        family = self.person.getMainFamily()
        if family:
            self.write_link_row("%s:" % _("Father"), family.getFather())
            self.write_link_row("%s:" % _("Mother"), family.getMother())
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

        if self.link:
            self.doc.start_paragraph("Data")
            self.doc.start_link("index.html")
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
        index = 0
        for object in self.person.getPhotoList():
            if object.getReference().getMimeType()[0:5] == "image":
                if object.getPrivacy() == 0 and index != 0:
                    my_list.append(object)
            index = 1
            
        # if no images were found, return
        
        if len(my_list) == 0:
            return

        self.doc.start_paragraph("Data")
        self.doc.end_paragraph()

        self.doc.start_paragraph("GalleryTitle")
        self.doc.write_text(_("Gallery"))
        self.doc.end_paragraph()

        self.doc.start_table("gallery","IndTable")
        for obj in my_list:
            try:
                src = obj.getReference().getPath()
                base = os.path.basename(src)
                shutil.copy(src,"%s/images/%s" % (self.dir,base))
                self.doc.start_row()
                self.doc.start_cell("ImageCell")
                self.doc.start_paragraph("Data")
                self.doc.start_link("images/%s" % base)
                self.doc.add_photo(src,"row",1.5,1.5)
                self.doc.end_link()
                
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.start_cell("NoteCell")
                description = obj.getReference().getDescription()
                if description != "":
                    self.doc.start_paragraph("PhotoDescription")
                    self.doc.write_text(description)
                    self.doc.end_paragraph()
                if obj.getNote() != "":
                    self.doc.start_paragraph("PhotoNote")
                    self.doc.write_text(obj.getNote())
                    self.doc.end_paragraph()
                elif obj.getReference().getNote() != "":
                    self.doc.start_paragraph("PhotoNote")
                    self.doc.write_text(obj.getReference().getNote())
                    self.doc.end_paragraph()
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
        
        event_list = [ self.person.getBirth(), self.person.getDeath() ]
        event_list = event_list + self.person.getEventList()
        event_list.sort(by_date)
        for event in event_list:
            if event.getPrivacy():
                continue
            name = _(event.getName())
            date = event.getDate()
            descr = event.getDescription()
            place = event.getPlaceName()
            srcref = event.getSourceRefList()

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

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_notes(self):

        if self.person.getNote() == "" or self.alive:
            return
        
        self.doc.start_paragraph("NotesTitle")
        self.doc.write_text(_("Notes"))
        self.doc.end_paragraph()

        self.doc.start_paragraph("NotesParagraph")
        self.doc.write_text(self.person.getNote())
        self.doc.end_paragraph()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_fam_fact(self,event):

        if event == None:
            return
        name = _(event.getName())
        date = event.getDate()
        place = event.getPlaceName()
        descr = event.getDescription()
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

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_families(self):
        if len(self.person.getFamilyList()) == 0:
            return
        
        self.doc.start_paragraph("FamilyTitle")
        self.doc.write_text(_("Marriages/Children"))
        self.doc.end_paragraph()

        self.doc.start_table("three","IndTable")
        
        for family in self.person.getFamilyList():
            if self.person == family.getFather():
                spouse = family.getMother()
            else:
                spouse = family.getFather()
            self.doc.start_row()
            self.doc.start_cell("NormalCell",2)
            self.doc.start_paragraph("Spouse")
            if spouse:
                if self.list.has_key(spouse):
                    self.doc.start_link("%s.html" % spouse.getId())
                    self.doc.write_text(spouse.getPrimaryName().getRegularName())
                    self.doc.end_link()
                else:
                    self.doc.write_text(spouse.getPrimaryName().getRegularName())
            else:
                self.doc.write_text(_("unknown"))
            self.doc.end_paragraph()
            self.doc.end_cell()
            self.doc.end_row()
            
            if not self.alive:
                for event in family.getEventList():
                    if event.getPrivacy() == 0:
                        self.write_fam_fact(event)

            child_list = family.getChildList()
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
                for child in family.getChildList():
                    if first == 1:
                        first = 0
                    else:
                        self.doc.write_text('\n')
                    if self.list.has_key(child):
                        self.doc.start_link("%s.html" % child.getId())
                        self.doc.write_text(child.getPrimaryName().getRegularName())
                        self.doc.end_link()
                    else:
                        self.doc.write_text(child.getPrimaryName().getRegularName())
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()
        self.doc.end_table()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def individual_filter(database,person,list,generations):
    list.append(person)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def ancestor_filter(database,person,list,generations):

    if person == None:
        return
    if person not in list:
        list.append(person)
    if generations <= 1:
        return

    family = person.getMainFamily()
    if family != None:
        ancestor_filter(database,family.getFather(),list,generations-1)
        ancestor_filter(database,family.getMother(),list,generations-1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def descendant_filter(database,person,list,generations):

    if person == None or person in list:
        return
    if person not in list:
        list.append(person)
    if generations <= 1:
        return
    
    for family in person.getFamilyList():
        for child in family.getChildList():
            descendant_filter(database,child,list,generations-1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_filter(database,person,list,generations):

    descendant_filter(database,person,list,generations)
    ancestor_filter(database,person,list,generations)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def entire_db_filter(database,person,list,generations):

    for entry in database.getPersonMap().values():
        list.append(entry)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def an_des_of_gparents_filter(database,person,list,generations):

    my_list = []

    family = person.getMainFamily()
    if family == None:
        return

    for p in [ family.getMother(), family.getFather() ]:
	if p:
            pf = p.getMainFamily()
            if pf:
                if pf.getFather():
                    my_list.append(pf.getFather())
                if pf.getMother():
                    my_list.append(pf.getMother())

    for person in my_list:
        descendant_filter(database,person,list,generations)
        ancestor_filter(database,person,list,generations)

#------------------------------------------------------------------------
#
# Mams menu items to filter functions
#
#------------------------------------------------------------------------

filter_map = {
    _("Individual") : individual_filter,
    _("Ancestors") : ancestor_filter,
    _("Descendants") : descendant_filter,
    _("Ancestors and descendants") : an_des_filter,
    _("Grandparent's ancestors and descendants") : an_des_of_gparents_filter,
    _("Entire database") : entire_db_filter
    }
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReport(Report):
    def __init__(self,db,person,target_path,max_gen,photos,filter,restrict,
                 private, srccomments, include_link, style, template_name):
        self.db = db
        self.person = person
        self.target_path = target_path
        self.max_gen = max_gen
        self.photos = photos
        self.filter = filter
        self.restrict = restrict
        self.private = private
        self.srccomments = srccomments
        self.include_link = include_link
        self.selected_style = style
        self.template_name = template_name

    def get_progressbar_data(self):
        return (_("Gramps - Generate HTML reports"), _("Creating Web Pages"))
    
    #------------------------------------------------------------------------
    #
    # Writes a index file, listing all people in the person list.
    #
    #------------------------------------------------------------------------
    def dump_index(self,person_list,styles,template,html_dir):
    
        doc = HtmlLinkDoc(styles,template)
        doc.set_title(_("Family Tree Index"))
    
        doc.open(html_dir + os.sep + "index.html")
        doc.start_paragraph("Title")
        doc.write_text(_("Family Tree Index"))
        doc.end_paragraph()
    
        person_list.sort(sort.by_last_name)
        for person in person_list:
            name = person.getPrimaryName().getName()
            doc.start_link("%s.html" % person.getId())
            doc.write_text(name)
            doc.end_link()
            doc.newline()
        doc.close()
        
    def write_report(self):
        dir_name = self.target_path
        if dir_name == None:
            dir_name = os.getcwd()
        elif not os.path.isdir(dir_name):
            parent_dir = os.path.dirname(dir_name)
            if not os.path.isdir(parent_dir):
                GnomeErrorDialog(_("Neither %s nor %s are directories") % \
                                 (dir_name,parent_dir))
                return
            else:
                try:
                    os.mkdir(dir_name)
                except IOError, value:
                    GnomeErrorDialog(_("Could not create the directory : %s") % \
                                     dir_name + "\n" + value[1])
                    return
                except:
                    GnomeErrorDialog(_("Could not create the directory : %s") % \
                                     dir_name)
                    return
    
        image_dir_name = os.path.join(dir_name, "images")
        if not os.path.isdir(image_dir_name) and self.photos != 0:
            try:
                os.mkdir(image_dir_name)
            except IOError, value:
                GnomeErrorDialog(_("Could not create the directory : %s") % \
                                 image_dir_name + "\n" + value[1])
                return
            except:
                GnomeErrorDialog(_("Could not create the directory : %s") % \
                                 image_dir_name)
                return
    
        filter = filter_map[self.filter]
        ind_list = []
        filter(self.db,self.person,ind_list,self.max_gen)
        self.progress_bar_setup(float(len(ind_list)))
        
        doc = HtmlLinkDoc(self.selected_style,self.template_name)
        self.add_styles(doc)
        doc.build_style_declaration()

        my_map = {}
        for l in ind_list:
            my_map[l] = 1
        for person in ind_list:
            tdoc = HtmlLinkDoc(self.selected_style,None,doc)
            idoc = IndividualPage(person, self.photos, self.restrict,
                                  self.private, self.srccomments,
                                  self.include_link, my_map, dir_name, tdoc)
            idoc.create_page()
            idoc.close()
            self.progress_bar_step()
            while events_pending():
                mainiteration()
            
        if len(ind_list) > 1:
            self.dump_index(ind_list,self.selected_style,self.template_name,dir_name)
    
        self.progress_bar_done()

    def add_styles(self,doc):
        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_column_widths([15,85])
        doc.add_table_style("IndTable",tbl)

        cell = TableCellStyle()
        doc.add_cell_style("NormalCell",cell)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        doc.add_cell_style("ImageCell",cell)

        cell = TableCellStyle()
        cell.set_padding(0.2)
        doc.add_cell_style("NoteCell",cell)


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportDialog(ReportDialog):
    def __init__(self,database,person):
        ReportDialog.__init__(self,database,person)

    def add_user_options(self):
        lnk_msg = _("Include a link to the index page")
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        no_img_msg = _("Do not use images")
        no_limg_msg = _("Do not use images for living people")
        no_com_msg = _("Do not include comments and text in source information")

        self.use_link = GtkCheckButton(lnk_msg)
        self.use_link.set_active(1) 
        self.no_private = GtkCheckButton(priv_msg)
        self.no_private.set_active(1)
        self.restrict_living = GtkCheckButton(restrict_msg)
        self.no_images = GtkCheckButton(no_img_msg)
        self.no_living_images = GtkCheckButton(no_limg_msg)
        self.no_comments = GtkCheckButton(no_com_msg)

        self.add_option('',self.use_link)
        title = _("Privacy Options")
        self.add_frame_option(title,None,self.no_private)
        self.add_frame_option(title,None,self.restrict_living)
        self.add_frame_option(title,None,self.no_images)
        self.add_frame_option(title,None,self.no_living_images)
        self.add_frame_option(title,None,self.no_comments)

        self.no_images.connect('toggled',self.on_nophotos_toggled)
        
    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
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
        """Default to ten generations, no page break box."""
        return (10, 0)

    def get_report_filter_strings(self):
        """Set up the list of possible content filters."""
        return filter_map.keys()

    #------------------------------------------------------------------------
    #
    # Functions related to the default directory
    #
    #------------------------------------------------------------------------
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return Config.web_dir
    
    def set_default_directory(self, value):
        """Save the name of the current directory, so that any future
        reports will default to the most recently used directory.
        This also changes the directory name that will appear in the
        preferences panel, but does not change the preference in disk.
        This means that the last directory used will only be
        remembered for this session of gramps unless the user saves
        his/her preferences."""
        Config.web_dir = value
    
    #------------------------------------------------------------------------
    #
    # Create output style appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make the default output style for the Web Pages Report."""
        font = FontStyle()
        font.set(bold=1, face=FONT_SANS_SERIF, size=16)
        p = ParagraphStyle()
        p.set(align=PARA_ALIGN_CENTER,font=font)
        self.default_style.add_style("Title",p)
        
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
        p = ParagraphStyle()
        p.set(font=font,bborder=1)
        self.default_style.add_style("EventsTitle",p)
    
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
        p = ParagraphStyle()
        p.set(font=font,bborder=1)
        self.default_style.add_style("NotesTitle",p)
    
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
        p = ParagraphStyle()
        p.set(font=font,bborder=1)
        self.default_style.add_style("SourcesTitle",p)
    
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
        p = ParagraphStyle()
        p.set(font=font,bborder=1)
        self.default_style.add_style("GalleryTitle",p)
    
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12,italic=1)
        p = ParagraphStyle()
        p.set(font=font,bborder=1)
        self.default_style.add_style("FamilyTitle",p)
        
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("Spouse",p)
    
        font = FontStyle()
        font.set(size=12,italic=1)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("Label",p)
    
        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("Data",p)
    
        font = FontStyle()
        font.set(bold=1,face=FONT_SANS_SERIF,size=12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("PhotoDescription",p)
    
        font = FontStyle()
        font.set(size=12)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("PhotoNote",p)
    
        font = FontStyle()
        font.set_size(10)
        p = ParagraphStyle()
        p.set_font(font)
        self.default_style.add_style("SourceParagraph",p)
    
        font = FontStyle()
        font.set_size(12)
        p = ParagraphStyle()
        p.set_font(font)
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
        
    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window
    #
    #------------------------------------------------------------------------
    def setup_format_frame(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        self.output_notebook.set_page(1)

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
        ReportDialog.parse_report_options_frame(self)
        self.include_link = self.use_link.get_active()

    def parse_other_frames(self):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        self.restrict = self.restrict_living.get_active()
        self.private = self.no_private.get_active()
        self.srccomments = self.no_comments.get_active()
        if self.no_images.get_active() == 1:
            self.photos = 0
        elif self.no_living_images.get_active() == 1:
            self.photos = 1
        else:
            self.photos = 2

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

    #------------------------------------------------------------------------
    #
    # Functions related to creating the actual report document.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the web pages."""
        MyReport = WebReport(self.db, self.person, self.target_path,
                             self.max_gen, self.photos, self.filter,
                             self.restrict, self.private, self.srccomments,
                             self.include_link, self.selected_style,
                             self.template_name)
        MyReport.write_report()
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    WebReportDialog(database,person)

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
    description=_("Generates web (HTML) pages for individuals, or a set of individuals.")
    )

