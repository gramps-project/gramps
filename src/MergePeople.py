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
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import ReportUtils
import Utils
import ListModel
import NameDisplay
import const
import gtk
import pango

sex = ( _("male"), _("female"), _("unknown"))

class Compare:

    def __init__(self, db, person1, person2, update) :
        self.glade = gtk.glade.XML(const.mergeFile,"merge")
        self.top = self.glade.get_widget('merge')
        self.text1 = self.glade.get_widget('text1')
        self.text2 = self.glade.get_widget('text2')
        self.db = db

        self.p1 = person1
        self.p2 = person2
        self.update = update
        
        Utils.set_titles(self.top,self.glade.get_widget('title'),
                         _("Compare People"))
        self.display(self.text1.get_buffer(), person1)
        self.display(self.text2.get_buffer(), person2)

        self.glade.get_widget('cancel').connect('clicked',self.cancel)
        self.glade.get_widget('close').connect('clicked',self.merge)

    def cancel(self,obj):
        self.top.destroy()

    def merge(self,obj):
        if self.glade.get_widget('select1').get_active():
            merge = MergePeople(self.db,self.p1,self.p2)
        else:
            merge = MergePeople(self.db,self.p2,self.p1)
        self.top.destroy()
        merge.merge()
        self.update()

    def add(self, tobj, tag, text):
        text += "\n"
        tobj.insert_with_tags(tobj.get_end_iter(),text,tag)
        
    def display(self, tobj, person):
        normal = tobj.create_tag()
        normal.set_property('indent',10)
        normal.set_property('pixels-above-lines',1)
        normal.set_property('pixels-below-lines',1)
        indent = tobj.create_tag()
        indent.set_property('indent',30)
        indent.set_property('pixels-above-lines',1)
        indent.set_property('pixels-below-lines',1)
        title = tobj.create_tag()
        title.set_property('weight',pango.WEIGHT_BOLD)
        title.set_property('scale',pango.SCALE_LARGE)
        self.add(tobj,title,NameDisplay.displayer.display(person))
        self.add(tobj,normal,"%s:\t%s" % (_('ID'),person.get_gramps_id()))
        self.add(tobj,normal,"%s:\t%s" % (_('Gender'),sex[person.get_gender()]))
        bhandle = person.get_birth_handle()
        self.add(tobj,normal,"%s:\t%s" % (_('Birth'),self.get_event_info(bhandle)))
        dhandle = person.get_death_handle()
        self.add(tobj,normal,"%s:\t%s" % (_('Death'),self.get_event_info(dhandle)))

        nlist = person.get_alternate_names()
        if len(nlist) > 0:
            self.add(tobj,title,_("Alternate Names"))
            for name in nlist:
                self.add(tobj,normal,NameDisplay.displayer.display_name(name))

        elist = person.get_event_list()
        if len(elist) > 0:
            self.add(tobj,title,_("Events"))
            for event_handle in person.get_event_list():
                name = self.db.get_event_from_handle(event_handle).get_name()
                self.add(tobj,normal,"%s:\t%s" % (name,self.get_event_info(event_handle)))
        plist = person.get_parent_family_handle_list()

        if len(plist) > 0:
            self.add(tobj,title,_("Parents"))
            for fid in person.get_parent_family_handle_list():
                (fn,mn,id) = self.get_parent_info(fid[0])
                self.add(tobj,normal,"%s:\t%s" % (_('Family ID'),id))
                if fn:
                    self.add(tobj,indent,"%s:\t%s" % (_('Father'),fn))
                if mn:
                    self.add(tobj,indent,"%s:\t%s" % (_('Mother'),mn))
        else:
            self.add(tobj,normal,_("No parents found"))
            
        self.add(tobj,title,_("Spouses"))
        slist = person.get_family_handle_list()
        if len(slist) > 0:
            for fid in slist:
                (fn,mn,id) = self.get_parent_info(fid)
                family = self.db.get_family_from_handle(fid)
                self.add(tobj,normal,"%s:\t%s" % (_('Family ID'),id))
                spouse_id = ReportUtils.find_spouse(person,family)
                if spouse_id:
                    spouse = self.db.get_person_from_handle(spouse_id)
                    self.add(tobj,indent,"%s:\t%s" % (_('Spouse'),name_of(spouse)))
                relstr = const.family_relations[family.get_relationship()][0]
                self.add(tobj,indent,"%s:\t%s" % (_('Type'),relstr))
                event = ReportUtils.find_marriage(self.db,family)
                if event:
                    self.add(tobj,indent,"%s:\t%s" % (_('Marriage'),
                                                      self.get_event_info(event.get_handle())))
                for child_id in family.get_child_handle_list():
                    child = self.db.get_person_from_handle(child_id)
                    self.add(tobj,indent,"%s:\t%s" % (_('Child'),name_of(child)))
        else:
            self.add(tobj,normal,_("No spouses or children found"))

        alist = person.get_address_list()
        if len(alist) > 0:
            self.add(tobj,title,_("Addresses"))
            for addr in alist:
                location = ", ".join([addr.get_street(),addr.get_city(),
                                     addr.get_state(),addr.get_country()])
                self.add(tobj,normal,location.strip())

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

    def get_event_info(self,handle):
        date = ""
        place = ""
        if handle:
            event = self.db.get_event_from_handle(handle)
            date = event.get_date()
            place = self.place_name(event)
            if date:
                if place:
                    return "%s, %s" % (date,place)
                else:
                    return date
            else:
                if place:
                    return place
                else:
                    return ""
        else:
            return ""

    def place_name(self,event):
        place_id = event.get_place_handle()
        if place_id:
            place = self.db.get_place_from_handle(place_id)
            return place.get_title()
        else:
            return ""


#-------------------------------------------------------------------------
#
# Merge People UI
#
#-------------------------------------------------------------------------
class MergePeopleUI:

    def __init__(self,db,person1,person2,update):
        glade = gtk.glade.XML(const.mergeFile,'merge_people')
        top = glade.get_widget('merge_people')
        p1 = glade.get_widget('person1')
        p2 = glade.get_widget('person2')
        n1 = name_of(person1)
        n2 = name_of(person2)

        p1.set_label(n1)
        p2.set_label(n2)
        Utils.set_titles(top,glade.get_widget('title'),_("Merge People"))

        ret = top.run()
        
        if ret == gtk.RESPONSE_OK:
            if p1.get_active():
                merge = MergePeople(db,person1,person2)
            else:
                merge = MergePeople(db,person2,person1)
            merge.merge()
            update()
        top.destroy()

def name_of(p):
    if not p:
        return ""
    return "%s [%s]" % (NameDisplay.displayer.display(p),p.get_gramps_id())

#-------------------------------------------------------------------------
#
# Merge People
#
#-------------------------------------------------------------------------
class MergePeople:

    def __init__(self,db,person1,person2):
        self.db = db
        self.p1 = person1
        self.p2 = person2
        
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
        
        new.set_handle(self.new_handle)
        new.set_gender(self.p1.get_gender())
        self.merge_gramps_ids(new)
        self.merge_names(new)
        self.merge_birth(new,trans)
        self.merge_death(new,trans)
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

        # media
        for photo in self.p1.get_media_list():
            new.add_media_reference(photo)
        for photo in self.p2.get_media_list():
            new.add_media_reference(photo)


        # note
        note1 = self.p1.get_note_object()
        note2 = self.p2.get_note_object()
        new.set_note_object(self.merge_notes(note1,note2))
        
    def merge(self):

        new = RelLib.Person()
        trans = self.db.transaction_begin()

        self.merge_person_information(new,trans)
        self.merge_family_information(new,trans)
        self.db.commit_person(new,trans)
        self.db.remove_person(self.old_handle,trans)
        self.db.transaction_commit(trans,"Merge Person")

    def convert_child_ids(self, family_id, id1, id2, trans):
        new_list = []
        change = False
        family = self.db.get_family_from_handle(family_id)

        for child_id in family.get_child_handle_list():
            if child_id == id2:
                new_list.append(id1)
                change = True
            else:
                new_list.append(child_id)
        if change:
            family.set_child_handle_list(new_list)
            self.db.commit_family(family,trans)
    
    def merge_parents(self, new, trans):
        f1_list = self.p1.get_parent_family_handle_list()
        f2_list = self.p2.get_parent_family_handle_list()

        parent_list = f1_list

        for fid in f2_list:
            self.convert_child_ids(fid[0], self.new_handle, self.old_handle, trans)
            parent_list.append(fid)
        for fid in parent_list:
            new.add_parent_family_handle(fid[0],fid[1],fid[2])
                    
    def merge_family_information(self, new, trans):
        self.merge_parents(new, trans)
        self.merge_families(new, trans)
        
    def find_family(self,family):
        if self.p1.get_gender() == RelLib.Person.MALE:
            mother_handle = family.get_mother_handle()
            father_handle = self.p1.get_handle()
        else:
            father_handle = family.get_father_handle()
            mother_handle = self.p1.get_handle()

        for myfamily_handle in self.db.get_family_handles():
            myfamily = self.db.get_family_from_handle(myfamily_handle)
            if (myfamily.get_father_handle() == father_handle and
                myfamily.get_mother_handle() == mother_handle):
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

        elist = tgt_family.get_event_list()[:]
        for event_id in src_family.get_event_list():
            if event_id not in elist:
                tgt_family.add_event_handle(event_id)

        # merge family attributes

        for xdata in src_family.get_attribute_list():
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

    def merge_families(self,new,trans):
        
        family_num = 0
        family_list = self.p1.get_family_handle_list()
        
        for src_family_handle in self.p2.get_family_handle_list():

            src_family = self.db.get_family_from_handle(src_family_handle)
            family_num += 1

            if not src_family or src_family in self.p1.get_family_handle_list():
                continue

            tgt_family = self.find_family(src_family)

            #
            # This is the case where a new family to be added to the
            # p1 as a result of the merge already exists as a
            # family.  In this case, we need to remove the old source
            # family (with the pre-merge identity of the p1) from
            # both the parents
            #

            if tgt_family:
                tgt_family_handle = tgt_family.get_handle()
                if tgt_family_handle in self.p1.get_family_handle_list():
                    
                    father_id = tgt_family.get_father_handle()
                    father = self.db.get_person_from_handle(father_id)
                    
                    mother_id = tgt_family.get_mother_handle()
                    mother = self.db.get_person_from_handle(mother_id)

                    if father and src_family_handle in father.get_family_handle_list():
                        father.remove_family_handle(src_family_handle)
                        self.db.commit_person(father,trans)
                    if mother and src_family_handle in mother.get_family_handle_list():
                        mother.remove_family_handle(src_family_handle)
                        self.db.commit_person(mother,trans)
                        
                    self.merge_family_pair(tgt_family,src_family,trans)
                        
                    for child_handle in src_family.get_child_handle_list():
                        if child_handle != self.new_handle:
                            child = self.db.get_person_from_handle(child_handle)
                            if child.remove_parent_family_handle(src_family_handle):
                                self.db.commit_person(child,trans)

                    # delete the old source family
                    self.db.remove_family(src_family_handle,trans)
                    self.db.commit_family(tgt_family,trans)

                    new.add_family_handle(tgt_family_handle)

                    continue
            
                # This is the case where a new family to be added 
                # and it is not already in the list.

                else:

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
                        father = self.db.get_person_from_handle(father_handle)
                        father.remove_family_handle(src_family_handle)
                        father.add_family_handle(tgt_family_handle)
                        self.db.commit_person(father,trans)

                    mother_handle = src_family.get_mother_handle()
                    if mother_handle:
                        mother = self.db.get_person_from_handle(mother_handle)
                        mother.remove_family_handle(src_family_handle)
                        mother.add_family_handle(tgt_family_handle)
                        self.db.commit_person(mother,trans)
                        
                    for child_handle in src_family.get_child_handle_list():
                        if child_handle != self.new_handle:
                            child = self.db.get_person_from_handle(child_handle)
                            if child.remove_parent_family_handle(src_family_handle):
                                self.db.commit_person(child,trans)
                        
                    new.remove_family_handle(src_family_handle)
                    self.db.remove_family(src_family_handle,trans)

            else:

                for fid in self.p1.get_family_handle_list():
                    new.add_family_handle(fid)

                for src_family_handle in self.p2.get_family_handle_list():
                    if src_family_handle in self.p1.get_family_handle_list():
                        continue
                    src_family = self.db.get_family_from_handle(src_family_handle)
                    new.add_family_handle(src_family_handle)
                    if src_family.get_father_handle() == self.old_handle:
                        src_family.set_father_handle(self.new_handle)
                    if src_family.get_mother_handle() == self.old_handle:
                        src_family.set_mother_handle(self.new_handle)
                    self.db.commit_family(src_family,trans)

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
            person.remove_family_handle(family.get_handle())
            if family.get_father_handle() == None and family.get_mother_handle() == None:
                self.delete_empty_family(family,trans)

    def delete_empty_family(self,family,trans):
        family_handle = family.get_handle()
        for child_handle in family.get_child_handle_list():
            child = self.db.get_person_from_handle(child_handle)
            if child.get_main_parents_family_handle() == family_handle:
                child.set_main_parent_family_handle(None)
            else:
                child.remove_parent_family_handle(family_handle)
            self.db.commit_person(child,trans)
        self.db.remove_family(family_handle,trans)

    def merge_gramps_ids(self,new):
        new.set_gramps_id(self.p1.get_gramps_id())
        attr = RelLib.Attribute()
        attr.set_type('Merged GRAMPS ID')
        attr.set_value(self.p2.get_gramps_id())
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
        new.set_primary_name(self.p1.get_primary_name())
        new.add_alternate_name(self.p2.get_primary_name())
        if self.p1.get_nick_name() == "":
            new.set_nick_name(self.p2.get_nick_name())
        else:
            new.set_nick_name(self.p1.get_nick_name())

    def merge_death(self, new, trans):
        handle1 = self.p1.get_death_handle()
        handle2 = self.p2.get_death_handle()

        if handle1:
            new.set_death_handle(handle1)
            if handle2:
                event = self.db.get_event_from_handle(handle2)
                event.set_handle(Utils.create_id())
                event.set_name('Alternate Death')
                new.add_event_handle(event.get_handle())
                self.db.add_event(event,trans)
        elif not handle1 and handle2:
            new.set_death_handle(handle2)

    def merge_birth(self, new,trans):
        handle1 = self.p1.get_birth_handle()
        handle2 = self.p2.get_birth_handle()

        if handle1:
            new.set_birth_handle(handle1)
            if handle2:
                event = self.db.get_event_from_handle(handle2)
                event.set_name('Alternate Birth')
                self.db.add_event(event,trans)
                new.add_event_handle(event.get_handle())
        elif not handle1 and handle2:
            new.set_birth_handle(handle2)

    def merge_event_lists(self, new):
        data_list = new.get_event_list()
        for handle in self.p1.get_event_list():
            if handle not in data_list:
                data_list.append(handle)
        for handle in self.p2.get_event_list():
            if handle not in data_list:
                data_list.append(handle)
        new.set_event_list(data_list)
