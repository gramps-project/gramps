#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME
#
#-------------------------------------------------------------------------
import gtk
import gnome
from gnome.ui import Druid, DruidPageEdge, DruidPageStandard

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import ListModel
import NameDisplay
import const

#-------------------------------------------------------------------------
#
# Merge People
#
#-------------------------------------------------------------------------
class MergePeople:

    def __init__(self,parent,db,person1,person2,update,ep_update=None):
        self.parent = parent
        self.db = db
        self.p1 = person1
        self.p2 = person2
        self.update = update
        self.ep_update = ep_update
        self.parent = parent

        self.need_birth = self.p1.get_birth_handle() and self.p2.get_birth_handle()
        self.need_death = self.p1.get_death_handle() and self.p2.get_death_handle()
        self.need_spouse = len(self.p1.get_family_handle_list()) + \
                           len(self.p2.get_family_handle_list()) > 1

        self.need_parents = len(self.p1.get_parent_family_handle_list()) + \
                            len(self.p2.get_parent_family_handle_list()) > 1
        self.build_interface()

    def build_interface(self):

        self.w = gtk.Window()

        self.fg_color = gtk.gdk.color_parse('#7d684a')
        self.bg_color = gtk.gdk.color_parse('#e1dbc5')
        self.logo = gtk.gdk.pixbuf_new_from_file("%s/gramps.png" % const.rootDir)
        self.splash = gtk.gdk.pixbuf_new_from_file("%s/splash.jpg" % const.rootDir)

        self.d = Druid()
        self.w.add(self.d)
        self.w.set_title(_('GRAMPS - Merge People'))
        self.d.add(self.build_info_page())
        self.d.add(self.build_name_page())
        self.d.add(self.build_id_page())
        if self.need_birth:
            self.d.add(self.build_birth_page())
        if self.need_death:
            self.d.add(self.build_death_page())
        if self.need_parents:
            self.d.add(self.build_parents_page())
        if self.need_spouse:
            self.d.add(self.build_spouse_page())
        self.last_page = self.build_last_page()
        self.d.add(self.last_page)

        self.d.set_show_help(True)
        self.d.connect('cancel',self.close)
        #self.d.connect('help',self.help)
        self.w.connect("destroy_event",self.close)
        self.w.show_all()

    def close(self,obj,obj2=None):
        """
        Close and delete handler.
        """
        self.w.destroy()

    def build_last_page(self):
        """
        Build the last druid page. The actual text will be added after the
        save is performed and the success status us known. 
        """
        p = DruidPageEdge(1)
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.set_text(_('Pressing APPLY will merge the two selected people '
                     'into a single person. If you do not wish to do this, '
                     'press CANCEL'))
        p.connect('finish',self.close)
        return p

    def build_name_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        self.format_buttons = []

        p = DruidPageStandard()
        p.set_title(_('Select primary name'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        fname = NameDisplay.displayer.display(self.p1)
        mname = NameDisplay.displayer.display(self.p2)

        self.name1 = gtk.RadioButton(None,fname)
        self.name2 = gtk.RadioButton(self.name1,mname)
        self.altnames = gtk.CheckButton(_('Keep unselected name as an alternate name'))
        
        table = gtk.Table(6,2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' % _('Primary name'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,0,1,xoptions=gtk.EXPAND|gtk.FILL)

        label = gtk.Label('<b>%s</b>' % _('Options'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,3,4,xoptions=gtk.EXPAND|gtk.FILL)

        table.attach(self.name1,1,2,1,2)
        table.attach(self.name2,1,2,2,3)
        table.attach(self.altnames,1,2,4,5)
        
        box.add(table)
        box.show_all()
        return p

    def build_id_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        p = DruidPageStandard()
        p.set_title(_('Select GRAMPS ID'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        self.id1 = gtk.RadioButton(None,self.p1.get_gramps_id())
        self.id2 = gtk.RadioButton(self.id1,self.p2.get_gramps_id())
        self.keepid = gtk.CheckButton(_('Keep old ID as an Attribute'))
        
        table = gtk.Table(6,2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' % _('GRAMPS ID'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,0,1,xoptions=gtk.EXPAND|gtk.FILL)

        label = gtk.Label('<b>%s</b>' % _('Options'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,3,4,xoptions=gtk.EXPAND|gtk.FILL)

        table.attach(self.id1,1,2,1,2)
        table.attach(self.id2,1,2,2,3)
        table.attach(self.keepid,1,2,4,5)
        
        box.add(table)
        box.show_all()
        return p

    def build_birth_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        p = DruidPageStandard()
        p.set_title(_('Select Birth Event'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        (birth1,bplace1) = self.get_event_info(self.p1,
                                               self.p1.get_birth_handle())
        (birth2,bplace2) = self.get_event_info(self.p2,
                                               self.p2.get_birth_handle())
        bstr1 = ", ".join([birth1,bplace1])
        bstr2 = ", ".join([birth2,bplace2])

        self.birth1 = gtk.RadioButton(None,bstr1)
        self.birth2 = gtk.RadioButton(self.birth1,bstr2)
        self.keepbirth = gtk.CheckButton(_('Add unselected birth event as '
                                           'an Alternate Birth event'))
        
        table = gtk.Table(6,2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' % _('Birth Event'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,0,1,xoptions=gtk.EXPAND|gtk.FILL)

        label = gtk.Label('<b>%s</b>' % _('Options'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,3,4,xoptions=gtk.EXPAND|gtk.FILL)

        table.attach(self.birth1,1,2,1,2)
        table.attach(self.birth2,1,2,2,3)
        table.attach(self.keepbirth,1,2,4,5)
        
        box.add(table)
        box.show_all()
        return p

    def build_death_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        p = DruidPageStandard()
        p.set_title(_('Select Death Event'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        (birth1,bplace1) = self.get_event_info(self.p1,
                                               self.p1.get_death_handle())
        (birth2,bplace2) = self.get_event_info(self.p2,
                                               self.p2.get_death_handle())
        bstr1 = ", ".join([birth1,bplace1])
        bstr2 = ", ".join([birth2,bplace2])

        self.death1 = gtk.RadioButton(None,bstr1)
        self.death2 = gtk.RadioButton(self.death1,bstr2)
        self.keepdeath = gtk.CheckButton(_('Add unselected death event as '
                                           'an Alternate Death event'))
        
        table = gtk.Table(6,2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' % _('Death Event'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,0,1,xoptions=gtk.EXPAND|gtk.FILL)

        label = gtk.Label('<b>%s</b>' % _('Options'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,5,3,4,xoptions=gtk.EXPAND|gtk.FILL)

        table.attach(self.death1,1,2,1,2)
        table.attach(self.death2,1,2,2,3)
        table.attach(self.keepdeath,1,2,4,5)
        
        box.add(table)
        box.show_all()
        return p

    def build_spouse_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        p = DruidPageStandard()
        p.set_title(_('Select Spouses'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        import ReportUtils

        table = gtk.Table(3,3)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' %
                          _('Select spouse relationships'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,3,0,1,xoptions=gtk.EXPAND|gtk.FILL)
        
        self.spouse_view = gtk.TreeView()
        self.spouse_list = gtk.ListStore(bool,str,str,str,str,str)
        self.spouse_view.set_model(self.spouse_list)
        self.spouse_view.set_reorderable(True)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,
                          gtk.POLICY_AUTOMATIC)
        scroll.add(self.spouse_view)
        table.attach(scroll,0,3,2,3,xoptions=gtk.EXPAND|gtk.FILL,
                     yoptions=gtk.EXPAND|gtk.FILL)
        
        celltoggle = gtk.CellRendererToggle()
        celltoggle.set_property('activatable',True)
        celltoggle.connect('toggled',self.parent_toggle,
                           (self.spouse_list,0))
        celltext = gtk.CellRendererText()
        col0 = gtk.TreeViewColumn(_('Select'),celltoggle,active=0)
        col1 = gtk.TreeViewColumn(_('ID'),celltext,text=1)
        col2 = gtk.TreeViewColumn(_('Spouse'),celltext,text=2)
        col3 = gtk.TreeViewColumn(_('Children'),celltext,text=3)
        col4 = gtk.TreeViewColumn(_('From'),celltext,text=4)
        self.spouse_view.append_column(col0)
        self.spouse_view.append_column(col1)
        self.spouse_view.append_column(col2)
        self.spouse_view.append_column(col3)
        self.spouse_view.append_column(col4)

        for fid in self.p1.get_family_handle_list():
            family = self.db.get_family_from_handle(fid)
            fgid = family.get_gramps_id()
            spouse_id = ReportUtils.find_spouse(self.p1,family)
            sname = name_of(self.db.get_person_from_handle(spouse_id))
            children = str(len(family.get_child_handle_list()))
            self.spouse_list.append(row=[True,fgid,sname,
                                         children,self.p1.get_gramps_id(),fid])

        for fid in self.p2.get_family_handle_list():
            family = self.db.get_family_from_handle(fid)
            fgid = family.get_gramps_id()
            spouse_id = ReportUtils.find_spouse(self.p1,family)
            sname = name_of(self.db.get_person_from_handle(spouse_id))
            children = str(len(family.get_child_handle_list()))
            self.spouse_list.append(row=[True,fgid,sname,
                                         children,self.p2.get_gramps_id(),fid])
        box.add(table)
        
        box.show_all()
        return p

    def build_parents_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        p = DruidPageStandard()
        p.set_title(_('Select parents'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        table = gtk.Table(3,3)
        table.set_row_spacings(6)
        table.set_col_spacings(6)

        label = gtk.Label('<b>%s</b>' %
                          _('Select parent relationships'))
        label.set_use_markup(True)
        label.set_alignment(0.0,0.5)
        table.attach(label,0,3,0,1,xoptions=gtk.EXPAND|gtk.FILL)

        label = gtk.Label(_('You can choose which sets of parents '
                            'are included in the merged person by selecting '
                            'the checkboxes. You can order the sets of parents '
                            'by dragging and dropping the rows. The first '
                            'set of parents in the list is considered to be '
                            'the primary set of parents used for reporting.'))
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_alignment(0.0,0.5)
        table.attach(label,1,3,1,2,xoptions=gtk.EXPAND|gtk.FILL)

        self.parent_view = gtk.TreeView()
        self.parent_view.set_reorderable(True)
        self.parent_list = gtk.ListStore(bool,str,str,str,str,str)
        self.parent_view.set_model(self.parent_list)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,
                          gtk.POLICY_AUTOMATIC)
        scroll.add(self.parent_view)

        table.attach(scroll,0,3,2,3,xoptions=gtk.EXPAND|gtk.FILL,
                     yoptions=gtk.EXPAND|gtk.FILL)

        celltoggle = gtk.CellRendererToggle()
        celltoggle.set_property('activatable',True)
        celltoggle.connect('toggled',self.parent_toggle,
                           (self.parent_list,0))

        celltext = gtk.CellRendererText()
        col0 = gtk.TreeViewColumn(_('Select'),celltoggle,active=0)
        col1 = gtk.TreeViewColumn(_('ID'),celltext,text=1)
        col2 = gtk.TreeViewColumn(_('Father'),celltext,text=2)
        col3 = gtk.TreeViewColumn(_('Mother'),celltext,text=3)
        col4 = gtk.TreeViewColumn(_('From'),celltext,text=4)

        self.parent_view.append_column(col0)
        self.parent_view.append_column(col1)
        self.parent_view.append_column(col2)
        self.parent_view.append_column(col3)
        self.parent_view.append_column(col4)

        for fid in self.p1.get_parent_family_handle_list():
            fname,mname,fgid = self.get_parent_info(fid[0])
            self.parent_list.append(row=[True, fgid, fname, mname,
                                         self.p1.get_gramps_id(), fid[0]])

        for fid in self.p2.get_parent_family_handle_list():
            fname,mname,fgid = self.get_parent_info(fid[0])
            self.parent_list.append(row=[True, fgid, fname, mname,
                                         self.p2.get_gramps_id(), fid[0]])

        box.add(table)
        box.show_all()
        return p

    def get_parent_info(self,fid):
        family = self.db.get_family_from_handle(fid)
        father_id = family.get_father_handle()
        mother_id = family.get_mother_handle()
        if father_id:
            father = self.db.get_person_from_handle(father_id)
            fname = name_of(father)
        else:
            fname = u""
        if mother_id:
            mother = self.db.get_person_from_handle(mother_id)
            mname = name_of(mother)
        else:
            mname = u""
        return (fname,mname,family.get_gramps_id())

    def parent_toggle(self,celltoggle,path,data):
        model, column = data
        if column == 0:
            model[path][column] = not model[path][column]
        else:
            if not model[path][column]:
                for index in range(0,len(model)):
                    model[index][column] = int(path)==int(index)

    def build_info_page(self):
        """
        Build initial druid page with the overall information about the process.
        This is a static page, nothing fun here :-)
        """
        p = DruidPageEdge(0)
        p.set_title(_('Merge people'))
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.set_text(_('This document will help you through the '
                     'the process of merging two people.'))
        return p

    def get_event_info(self,person,handle):
        date = ""
        place = ""
        if handle:
            event = self.db.get_event_from_handle(handle)
            return (event.get_date(),self.place_name(event))
        else:
            return (u"",u"")

    def build_spouse_list(self,person,widget):

        widget.clear()
        for fam_handle in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_handle)
            if person.get_gender() == RelLib.Person.MALE:
                spouse_handle = fam.get_mother_handle()
            else:
                spouse_handle = fam.get_father_handle()

            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
            else:
                spouse = None

            if spouse == None:
                name = "unknown"
            else:
                sname = NameDisplay.displayer.display(spouse)
                name = "%s [%s]" % (sname,spouse.get_gramps_id())
            widget.add([name])

    def set_field(self,widget,value):
        """Sets the string of the entry field at positions it a space 0"""
        widget.set_text(value)

    def place_name(self,event):
        place_id = event.get_place_handle()
        if place_id:
            place = self.db.get_place_from_handle(place_id)
            return "%s [%s]" % (place.get_title(),place.get_gramps_id())
        else:
            return ""

    def on_merge_edit_clicked(self,obj):
        import EditPerson
        self.on_merge_clicked(obj)
        # This needs to be fixed to provide an update call
        EditPerson.EditPerson(self.parent,self.p1,self.db,self.ep_update)

    def copy_note(self,one,two):
        if one.get_note() != two.get_note():
            one.set_note("%s\n\n%s" % (one.get_note(),two.get_note()))

    def copy_sources(self,one,two):
        slist = one.get_source_references()[:]
        for xsrc in two.get_source_references():
            for src in slist:
                if src.are_equal(xsrc):
                    break
            else:
                one.add_source_reference(xsrc)

    def merge_person_information(self,new,trans):
        self.old_handle = self.p2.get_handle()
        self.new_handle = self.p1.get_handle()
        
        new.set_handle(new_handle)
        new.set_gender(self.p1.get_gender())
        self.merge_gramps_ids(new)
        self.merge_names(new)
        self.merge_birth(new)
        self.merge_death(new)
        self.merge_event_lists(new)

        # copy attributes
        new.set_attribute_list(self.p1.get_attribute_list() +
                               self.p2.get_attribute_list())

        # copy addresses
        new.set_address_list(self.p1.get_address_list() + self.p2.get_address_list())

        # copy urls
        new.set_url_list(self.p1.get_url_list() + self.p2.get_url_list())

        # privacy
        new.set_privacy(self.p1.get_privacy() or self.p2.get_privacy())

        # sources
        new.set_source_reference_list(self.p1.get_source_references() +
                                      self.p2.get_source_references())

        # note
        note1 = self.p1.get_note_object()
        note2 = self.p2.get_note_object()
        new.set_note_object(self.merge_notes(note1,note2))
        
    def on_merge_clicked(self,obj):

        new = RelLib.Person()
        trans = self.db.transaction_begin()

        self.merge_person_information(new,trans)
        self.merge_family_information(new,trans)

    def convert_child_ids(self, family_id, id1, id2, trans):
        new_list = []
        change = False
        family = self.db.get_family_from_handle(family_id)
        for child_id in family.get_child_handle_list():
            if child_id == id2:
                new_list.append(id1)
                change = True
            else:
                new_list.append(id2)
        if change:
            family.set_child_handle_list(new_list)
            self.db.commit_family(family,trans)
    
    def merge_parents(self, new, trans):
        """
        Process for merging parents:

        Case 1: Person 1 has parents, Person 2 doesn't
                - Assign Person 1 list to new person
                - Assign Person 1 al
        Case 2: Person 2 has parents, Person 2 doesn't
                - Assign Person 2 list to new person
                - Loop through family list of Person 2, replacing ID2
                  with ID2 and recommitting the data
        Case 3: Person 1 and Person 2 have parents, One select, the
                other is not.
                - Assign selected to list, changed ID references
                - Remove ID from other family
        Case 4: Person 1 and Person 2 have parents, one selected, other kept
                - Assign selected to list, change IDs
                - Assign second to list, change IDs
        """
        f1_list = self.p1.get_parent_family_handle_list()
        f2_list = self.p2.get_parent_family_handle_list()

        if self.need_parents: # cases 1 and 2
            if len(f1_list) == 0 and len(f2_list) > 0:
                new.add_parent_family_handle(f2_list[0])
                self.convert_child_ids(f2_list[0],self.new_handle,
                                       self.old_handle, trans)
            el
                
        else: # cases 3 and 4
            if len(f1_list) > 0:
                new.set_parent_family_handle_list(f1_list)
            elif len(f2_list) > 0:
                new.set_parent_family_handle_list(f2_list)
                for fid in f2:
                    family = self.db.get_family_from_id(fid)
                    if family.get_father_handle() == self.old_handle:
                        family.set_father_handle(self.new_handle)
                    if family.get_mother_handle() == self.old_handle:
                        family.set_mother_handle(self.new_handle)
                    self.db.commit_family(family, trans)
                    
    def merge_family_information(self, new, trans):
        self.merge_parents(new, trans)
        return
    
        if self.glade.get_widget("bfather2").get_active():
            orig_family_handle = self.p1.get_main_parents_family_handle()
            if orig_family_handle:
                orig_family = self.db.get_family_from_handle(orig_family_handle)
                orig_family.remove_child_handle(new_handle)
                self.db.commit_family(orig_family,trans)
           
            (src_handle,mrel,frel) = self.p2.get_main_parents_family_handle()
            if src_handle:
                source_family = self.db.get_family_from_handle(src_handle)
                if self.old_handle in source_family.get_child_handle_list():
                    source_family.remove_child_handle(self.old_handle)
                    self.p2.remove_parent_family_handle(src_handle)
                if new_handle not in source_family.get_child_handle_list():
                    source_family.add_child_handle(new_handle)
                    new.add_parent_family_handle(src_handle,mrel,frel)
                self.db.commit_family(source_family,trans)
            new.set_main_parent_family_handle(src_handle)
        else:
            src_handle = self.p2.get_main_parents_family_handle()
            if src_handle:
                source_family = self.db.get_family_from_handle(src_handle)
                source_family.remove_child_handle(self.p2)
                self.p2.set_main_parent_family_handle(None)
                self.db.commit_family(source_family,trans)

        self.merge_families(trans)

        for photo in self.p2.get_media_list():
            self.p1.add_media_reference(photo)

        if self.p1.get_nick_name() == "":
            self.p1.set_nick_name(self.p2.get_nick_name())
            
        if self.p2.get_note() != "":
            old_note = self.p1.get_note()
            if old_note:
                old_note = old_note + "\n\n"
            self.p1.set_note(old_note + self.p2.get_note())

        self.copy_sources(self.p1,self.p2)

        self.db.remove_person(self.p2.get_handle(),trans)
        self.db.commit_person(self.p1,trans)

        self.update(self.p1,self.p2,old_id)

        self.db.transaction_commit(trans,_("Merge Person"))
        Utils.destroy_passed_object(self.top)
        
    def find_family(self,family):
        if self.p1.get_gender() == RelLib.Person.MALE:
            mother = family.get_mother_handle()
            father = self.p1.get_handle()
        else:
            father = family.get_father_handle()
            mother = self.p1.get_handle()

        for myfamily_handle in self.db.get_family_handles():
            myfamily = self.db.get_family_from_handle(myfamily_handle)
            if (myfamily.get_father_handle() == father and
                myfamily.get_mother_handle() == mother):
                return myfamily
        return None

    def merge_family_pair(self,tgt_family,src_family,trans):

        # copy children from source to target

        for child_handle in src_family.get_child_handle_list():
            if child_handle not in tgt_family.get_child_handle_list():
                child = self.db.get_person_from_handle(child_handle)
                parents = child.get_parent_family_handle_list()
                tgt_family.add_child_handle(child)
                if child.get_main_parents_family_handle() == src_family:
                    child.set_main_parent_family_handle(tgt_family)
                i = 0
                for fam in parents[:]:
                    if fam[0] == src_family.get_handle():
                        parents[i] = (tgt_family,fam[1],fam[2])
                    i += 1
                self.db.commit_person(child,trans)

        # merge family events

        lst = tgt_family.get_event_list()[:]
        for xdata in src_family.get_event_list():
            for data in lst:
                if data.are_equal(xdata):
                    self.copy_note(data,xdata)
                    self.copy_sources(data,xdata)
                    break
            else:
                tgt_family.add_event(xdata)

        # merge family attributes

        lst = tgt_family.get_attribute_list()[:]
        for xdata in src_family.get_attribute_list():
            for data in lst:
                if data.get_type() == xdata.get_type() and \
                   data.getValue() == xdata.get_value():
                    self.copy_note(data,xdata)
                    self.copy_sources(data,xdata)
                    break
            else:
                tgt_family.add_attribute(xdata)

        # merge family notes

        if src_family.get_note() != "":
            old_note = tgt_family.get_note()
            if old_note:
                old_note = old_note + "\n\n"
            tgt_family.set_note(old_note + src_family.get_note())

        # merge family top-level sources

        self.copy_sources(tgt_family,src_family)

        # merge multimedia objects

        for photo in src_family.get_media_list():
            tgt_family.add_media_reference(photo)

    def merge_families(self,trans):
        
        family_num = 0
        for src_family_handle in self.p2.get_family_handle_list():

            src_family = self.db.get_family_from_handle(src_family_handle)
            family_num += 1

            if not src_family:
                continue
            if src_family in self.p1.get_family_handle_list():
                continue

            tgt_family = self.find_family(src_family)

            #
            # This is the case where a new family to be added to the
            # p1 as a result of the merge already exists as a
            # family.  In this case, we need to remove the old source
            # family (with the pre-merge identity of the p1) from
            # both the parents
            #
            if tgt_family in self.p1.get_family_handle_list():
                if tgt_family.get_father_handle() != None and \
                   src_family in tgt_family.get_family_handle_list():
                    tgt_family.get_father_handle().remove_family_handle(src_family)
                if tgt_family.get_mother_handle() != None and \
                   src_family in tgt_family.get_mother_handle().get_family_handle_list():
                    tgt_family.get_mother_handle().remove_family_handle(src_family)

                self.merge_family_pair(tgt_family,src_family,trans)
                        
                # delete the old source family
                self.db.remove_family(src_family,trans)
                self.db.commit_family(tgt_family,trans)

                continue
            
            # This is the case where a new family to be added 
            # and it is not already in the list.

            if tgt_family:

                # tgt_family a duplicate family, transfer children from
                # the p2 family, and delete the family.  Not sure
                # what to do about marriage/divorce date/place yet.

                # transfer child to new family, alter children to
                # point to the correct family
                
                self.merge_family_pair(tgt_family,src_family,trans)

                # change parents of the family to point to the new
                # family

                father_handle = src_family.get_father_handle()
                if father_handle:
                    father = self.db.get_father_from_handle(father_handle)
                    father.remove_family_handle(src_family.get_handle())
                    father.add_family_handle(tgt_family.get_handle())
                    self.db.commit_person(father,trans)

                mother_handle = src_family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_mother_from_handle(mother_handle)
                    mother.remove_family_handle(src_family.get_handle())
                    mother.add_family_handle(tgt_family.get_handle())
                    self.db.commit_person(mother,trans)

                self.db.remove_family(src_family.get_handle())
            else:
                if src_family not in self.p1.get_family_handle_list():
                    self.p1.add_family_handle(src_family)
                    if self.p1.get_gender() == RelLib.Person.MALE:
                        src_family.set_father_handle(self.p1)
                    else:
                        src_family.set_mother_handle(self.p1)
                self.remove_marriage(src_family,self.p2,trans)

        # a little debugging here

        cursor = self.db.get_family_cursor()
        data = cursor.first()
        while data:
            fam = RelLib.Family()
            fam.unserialize(data[1])
            if self.p2 in fam.get_child_handle_list():
                fam.remove_child_handle(self.p2)
                fam.add_child_handle(self.p1)
            if self.p2 == fam.get_father_handle():
                fam.set_father_handle(self.p1)
            if self.p2 == fam.get_mother_handle():
                fam.set_mother_handle(self.p1)
            if fam.get_father_handle() == None and fam.get_mother_handle() == None:
                self.delete_empty_family(fam)
            data = cursor.next()
                
    def remove_marriage(self,family,person,trans):
        if person:
            person.remove_family_handle(family)
            if family.get_father_handle() == None and family.get_mother_handle() == None:
                self.delete_empty_family(family,trans)

    def delete_empty_family(self,family,trans):
        for child_handle in family.get_child_handle_list():
            child = self.db.get_person_from_handle(child_handle)
            if child.get_main_parents_family_handle() == family_handle:
                child.set_main_parent_family_handle(None)
            else:
                child.remove_parent_family_handle(family_handle)
            self.db.commit_person(child,trans)
        self.db.remove_family(family_handle,trans)

    def merge_gramps_ids(self,new):
        if self.id1.get_active():
            new.set_gramps_id(self.p1.get_gramps_id())
            other_id = self.p2.get_gramps_id()
        else:
            new.set_gramps_id(self.p2.get_gramps_id())
            other_id = self.p1.get_gramps_id()

        if self.keepid:
            attr = RelLib.Attribute()
            attr.set_type('Merged GRAMPS ID')
            attr.set_value(other_id)
            new.add_attribute(attr)

    def merge_notes(self, note1, note2):
        if note1 and not note2:
            return note1
        elif not note1 and note2:
            return note2
        elif note1 and note2:
            note1.append("\n" + note2.get())
            note1.set_format(note1.get_format() or note2.get_format())
            return note1
        return None

    def merge_names(self, new):
        if self.name1.get_active():
            new.set_primary_name(self.p1.get_primary_name())
            alt = self.p2.get_primary_name()
        else:
            new.set_primary_name(self.p2.get_primary_name())
            alt = self.p1.get_primary_name()

        if self.altnames.get_active():
            new.add_alternate_name(alt)

        for name in self.p1.get_alternate_names():
            new.add_alternate_name(name)
        for name in self.p2.get_alternate_names():
            new.add_alternate_name(name)

    def merge_death(self, new):
        handle1 = self.p1.get_death_handle()
        handle2 = self.p2.get_death_handle()

        if not self.need_death:
            if handle1:
                new.set_death_handle(handle1)
            if handle2:
                new.set_death_handle(handle2)
        else:
            if self.death1.get_active():
                new.set_death_handle(handle1)
                alt_handle = handle2
            else:
                new.set_death_handle(handle2)
                alt_handle = handle1

            if self.keepdeath:
                event = self.db.get_event_from_handle(alt_handle)
                event.set_handle(None)
                event.db.set_name('Alternate Death')
                self.db.add_event(event,trans)
                new.add_event_handle(event.get_handle())

    def merge_birth(self, new):
        handle1 = self.p1.get_birth_handle()
        handle2 = self.p2.get_birth_handle()

        if not self.need_birth:
            if handle1:
                new.set_birth_handle(handle1)
            if handle2:
                new.set_birth_handle(handle2)
        else:
            if self.birth1.get_active():
                new.set_birth_handle(handle1)
                alt_handle = handle2
            else:
                new.set_birth_handle(handle2)
                alt_handle = handle1

            if self.keepbirth:
                event = self.db.get_event_from_handle(alt_handle)
                event.set_handle(None)
                event.set_name('Alternate Birth')
                self.db.add_event(event,trans)
                new.add_event_handle(event.get_handle())

    def merge_event_lists(self, new):
        data_list = self.p1.get_event_list()
        for handle in self.p2.get_event_list():
            if handle not in data_list:
                events.append(handle)
        new.set_event_list(data_list)

def compare_people(p1,p2):

    name1 = p1.get_primary_name()
    name2 = p2.get_primary_name()
                
    chance = name_match(name1,name2)
    if chance == -1.0  :
        return -1.0

    birth1 = p1.get_birth_handle()
    death1 = p1.get_death_handle()
    birth2 = p2.get_birth_handle()
    death2 = p2.get_death_handle()

    value = date_match(birth1.get_date_object(),birth2.get_date_object()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = date_match(death1.get_date_object(),death2.get_date_object()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(birth1.get_place_handle(),birth2.get_place_handle()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    value = place_match(death1.get_place_handle(),death2.get_place_handle()) 
    if value == -1.0 :
        return -1.0
    chance = chance + value

    ancestors = []
    ancestors_of(p1,ancestors)
    if p2 in ancestors:
        return -1.0

    ancestors = []
    ancestors_of(p2,ancestors)
    if p1 in ancestors:
        return -1.0
        
    f1 = p1.get_main_parents_family_handle()
    f2 = p2.get_main_parents_family_handle()

    if f1 and f1.get_father_handle():
        dad1 = f1.get_father_handle().get_primary_name()
    else:
        dad1 = None

    if f2 and f2.get_father_handle():
        dad2 = f2.get_father_handle().get_primary_name()
    else:
        dad2 = None
        
    value = name_match(dad1,dad2)
            
    if value == -1.0:
        return -1.0

    chance = chance + value
            
    if f1 and f1.get_mother_handle():
        mom1 = f1.get_mother_handle().get_primary_name()
    else:
        mom1 = None

    if f2 and f2.get_mother_handle():
        mom2 = f2.get_mother_handle().get_primary_name()
    else:
        mom2 = None

    value = name_match(mom1,mom2)
    if value == -1.0:
        return -1.0
            
    chance = chance + value

    for f1 in p1.get_family_handle_list():
        for f2 in p2.get_family_handle_list():
            if p1.get_gender() == RelLib.Person.FEMALE:
                father1 = f1.get_father_handle()
                father2 = f2.get_father_handle()
                if father1 and father2:
                    if father1 == father2:
                        chance = chance + 1.0
                    else:
                        fname1 = NameDisplay.displayer.display(father1)
                        fname2 = NameDisplay.displayer.display(father2)
                        value = name_match(fname1,fname2)
                        if value != -1.0:
                            chance = chance + value
            else:
                mother1 = f1.get_mother_handle()
                mother2 = f2.get_mother_handle()
                if mother1 and mother2:
                    if mother1 == mother2:
                        chance = chance + 1.0
                    else:
                        mname1 = NameDisplay.displayer.display(mother1)
                        mname2 = NameDisplay.displayer.display(mother2)
                        value = name_match(mname1,mname2)
                        if value != -1.0:
                            chance = chance + value

    return chance

#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def name_compare(s1,s2):
    return s1 == s2

#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def date_match(date1,date2):
    if date1.get_date() == "" or date2.get_date() == "":
        return 0.0
    if date1.get_date() == date2.get_date():
        return 1.0
    
    if date1.isRange() or date2.isRange():
        return range_compare(date1,date2)

    date1 = date1.get_start_date()
    date2 = date2.get_start_date()
        
    if date1.getYear() == date2.getYear():
        if date1.getMonth() == date2.getMonth():
            return 0.75
        if not date1.getMonthValid() or not date2.getMonthValid():
            return 0.75
        else:
            return -1.0
    else:
        return -1.0

#-----------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------
def range_compare(date1,date2):
    d1_start = date1.get_start_date()
    d2_start = date2.get_start_date()
    d1_stop  = date1.get_stop_date()
    d2_stop  = date2.get_stop_date()

    if date1.isRange() and date2.isRange():
        if d1_start >= d2_start and d1_start <= d2_stop or \
           d2_start >= d1_start and d2_start <= d1_stop or \
           d1_stop >= d2_start and d1_stop <= d2_stop or \
           d2_stop >= d1_start and d2_stop <= d1_stop:
            return 0.5
        else:
            return -1.0
    elif date2.isRange():
        if d1_start >= d2_start and d1_start <= d2_stop:
            return 0.5
        else:
            return -1.0
    else:
        if d2_start >= d1_start and d2_start <= d1_stop:
            return 0.5
        else:
            return -1.0

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def name_match(name,name1):

    if not name1 or not name:
        return 0
    
    srn1 = name.get_surname()
    sfx1 = name.get_suffix()
    srn2 = name1.get_surname()
    sfx2 = name1.get_suffix()

    if not name_compare(srn1,srn2):
        return -1
    if sfx1 != sfx2:
        if sfx1 != "" and sfx2 != "":
            return -1

    if name.get_first_name() == name1.get_first_name():
        return 1
    else:
        list1 = name.get_first_name().split()
        list2 = name1.get_first_name().split()

        if len(list1) < len(list2):
            return list_reduce(list1,list2)
        else:
            return list_reduce(list2,list1)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def list_reduce(list1,list2):
    value = 0
    for name in list1:
        for name2 in list2:
            if is_initial(name) and name[0] == name2[0]:
                value = value + 0.25
                break
            if is_initial(name2) and name2[0] == name[0]:
                value = value + 0.25
                break
            if name == name2:
                value = value + 0.5
                break
            if name[0] == name2[0] and name_compare(name,name2):
                value = value + 0.25
                break
    if value == 0:
        return -1
    else:
        return min(value,1)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def place_match(p1,p2):
    if p1 == p2:
        return 1
    
    if p1 == None:
        name1 = ""
    else:
        name1 = p1.get_title()
        
    if p2 == None:
        name2 = ""
    else:
        name2 = p2.get_title()
        
    if name1 == "" or name2 == "":
        return 0
    if name1 == name2:
        return 1

    list1 = name1.replace(","," ").split()
    list2 = name2.replace(","," ").split()

    value = 0
    for name in list1:
        for name2 in list2:
            if name == name2:
                value = value + 0.5
                break
            if name[0] == name2[0] and name_compare(name,name2):
                value = value + 0.25
                break
    if value == 0:
        return -1
    else:
        return min(value,1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def is_initial(name):
    if len(name) > 2:
        return 0
    elif len(name) == 2:
        if name[0].isupper() and name[1] == '.':
            return 1
    else:
        return name[0].isupper()

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def ancestors_of(p1,lst):
    if p1 == None:
        return
    lst.append(p1)
    f1 = p1.get_main_parents_family_handle()
    if f1 != None:
        ancestors_of(f1.get_father_handle(),lst)
        ancestors_of(f1.get_mother_handle(),lst)

#---------------------------------------------------------------------
#
#
#
#---------------------------------------------------------------------
def name_of(p):
    if not p:
        return ""
    return "%s [%s]" % (NameDisplay.displayer.display(p),p.get_gramps_id())

#-------------------------------------------------------------------------
#
# Merge Places
#
#-------------------------------------------------------------------------
class MergePlaces:
    """
    Merges to places into a single place. Displays a dialog box that
    allows the places to be combined into one.
    """
    def __init__(self,database,place1,place2,update):
        self.db = database
        self.p1 = place1
        self.p2 = place2
        self.update = update

        self.glade = gtk.glade.XML(const.mergeFile,"merge_places","gramps")
        self.top = self.glade.get_widget("merge_places")
        self.glade.get_widget("title1_text").set_text(place1.get_title())
        self.glade.get_widget("title2_text").set_text(place2.get_title())
        self.t3 = self.glade.get_widget("title3_text")
        self.t3.set_text(place1.get_title())
        
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_merge_places_clicked" : self.on_merge_places_clicked,
            })
        self.top.show()

    def on_merge_places_clicked(self,obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """
        t2active = self.glade.get_widget("title2").get_active()

        old_id = self.p1.get_handle()
        
        if t2active:
            self.p1.set_title(self.p2.get_title())
        elif self.glade.get_widget("title3").get_active():
            self.p1.set_title(unicode(self.t3.get_text()))

        # Set longitude
        if self.p1.get_longitude() == "" and self.p2.get_longitude() != "":
            self.p1.set_longitude(self.p2.get_longitude())

        # Set latitude
        if self.p1.get_latitude() == "" and self.p2.get_latitude() != "":
            self.p1.set_latitude(self.p2.get_latitude())

        # Add URLs from P2 to P1
        for url in self.p2.get_url_list():
            self.p1.add_url(url)

        # Copy photos from P2 to P1
        for photo in self.p2.get_media_list():
            self.p1.add_media_reference(photo)

        # Copy sources from P2 to P1
        for source in self.p2.get_source_references():
            self.p1.add_source(source)

        # Add notes from P2 to P1
        note = self.p2.get_note()
        if note != "":
            if self.p1.get_note() == "":
                self.p1.set_note(note)
            elif self.p1.get_note() != note:
                self.p1.set_note("%s\n\n%s" % (self.p1.get_note(),note))

        if t2active:
            lst = [self.p1.get_main_location()] + self.p1.get_alternate_locations()
            self.p1.set_main_location(self.p2.get_main_location())
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)
        else:
            lst = [self.p2.get_main_location()] + self.p2.get_alternate_locations()
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)

        # loop through people, changing event references to P2 to P1
        for key in self.db.get_person_handles(sort_handles=False):
            p = self.db.get_person_from_handle(key)
            for event in [p.get_birth_handle(), p.get_death_handle()] + p.get_event_list():
                if event.get_place_handle() == self.p2:
                    event.set_place_handle(self.p1)

        # loop through families, changing event references to P2 to P1
        for f in self.db.get_family_handle_map().values():
            for event in f.get_event_list():
                if event.get_place_handle() == self.p2:
                    event.set_place_handle(self.p1)
                    
        self.db.remove_place(self.p2.get_handle())
        self.db.build_place_display(self.p1.get_handle(),old_id)
        
        self.update(self.p1.get_handle())
        Utils.destroy_passed_object(obj)


#-------------------------------------------------------------------------
#
# Merge Sources
#
#-------------------------------------------------------------------------
class MergeSources:
    """
    Merges to places into a single place. Displays a dialog box that
    allows the places to be combined into one.
    """
    def __init__(self,database,src1,src2,update):
        self.db = database
        self.p1 = src1
        self.p2 = src2
        self.update = update

        self.glade = gtk.glade.XML(const.mergeFile,"merge_sources","gramps")
        self.top = self.glade.get_widget("merge_sources")

        self.title1 = self.glade.get_widget("title1")
        self.title2 = self.glade.get_widget("title2")
        self.title1.set_text(src1.get_title())
        self.title2.set_text(src2.get_title())

        self.author1 = self.glade.get_widget("author1")
        self.author2 = self.glade.get_widget("author2")
        self.author1.set_text(src1.get_author())
        self.author2.set_text(src2.get_author())

        self.abbrev1 = self.glade.get_widget("abbrev1")
        self.abbrev2 = self.glade.get_widget("abbrev2")
        self.abbrev1.set_text(src1.get_abbreviation())
        self.abbrev2.set_text(src2.get_abbreviation())

        self.pub1 = self.glade.get_widget("pub1")
        self.pub2 = self.glade.get_widget("pub2")
        self.pub1.set_text(src1.get_publication_info())
        self.pub2.set_text(src2.get_publication_info())

        self.gramps1 = self.glade.get_widget("gramps1")
        self.gramps2 = self.glade.get_widget("gramps2")
        self.gramps1.set_text(src1.get_gramps_id())
        self.gramps2.set_text(src2.get_gramps_id())
        
        self.glade.get_widget('ok').connect('clicked',self.merge)
        self.glade.get_widget('close').connect('clicked',self.close)
        self.top.show()

    def close(self,obj):
        self.top.destroy()

    def merge(self,obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """

        use_title1 = self.glade.get_widget("title_btn1").get_active()
        use_author1 = self.glade.get_widget("author_btn1").get_active()
        use_abbrev1 = self.glade.get_widget("abbrev_btn1").get_active()
        use_pub1 = self.glade.get_widget("pub_btn1").get_active()
        use_gramps1 = self.glade.get_widget("gramps_btn1").get_active()

        old_id = self.p1.get_handle()
        
        if not use_title1:
            self.src1.set_title(self.src2.get_title())

        if not use_author1:
            self.src1.set_author(self.src2.get_author())

        if not use_abbrev1:
            self.src1.set_abbreviation(self.src2.get_abbreviation())

        if not use_pub1:
            self.src1.set_publication_info(self.src2.get_publication_info())

        if not use_gramps1:
            self.src1.set_gramps_id(self.src2.get_gramps_id())

        # Copy photos from src2 to src1
        for photo in self.src2.get_media_list():
            self.src1.add_media_reference(photo)

        # Add notes from P2 to P1
        note = self.src2.get_note()
        if note != "":
            if self.src1.get_note() == "":
                self.src1.set_note(note)
            elif self.src1.get_note() != note:
                self.src1.set_note("%s\n\n%s" % (self.src1.get_note(),note))

        src2_map = self.src2.get_data_map()
        src1_map = self.src1.get_data_map()
        for key in src2_map.keys():
            if not src1_map.has_key(key):
                src1_map[key] = src2_map[key]

        # replace handles
        old_handle = self.src2.get_handle()
        new_handle = self.src1.get_handle()

        # people
        for handle in self.db.get_person_handles(sort_handles=False):
            person = self.db.get_person_from_handle(handle)
            person.replace_source_references(old_handle,new_handle)

        # family
        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            family.replace_source_references(old_handle,new_handle)

        # events
        for handle in self.db.get_event_handles():
            event = self.db.get_event_from_handle(handle)
            event.replace_source_references(old_handle,new_handle)

        # sources
        for handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(handle)
            source.replace_source_references(old_handle,new_handle)

        # places
        for handle in self.db.get_place_handles():
            place = self.db.get_place_from_handle(handle) 
            place.replace_source_references(old_handle,new_handle)

        # media
        for handle in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(handle)
            obj.replace_source_references(old_handle,new_handle)
        
        self.top.destroy()
