#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import sets

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
from ReportBase import ReportUtils
import NameDisplay
import const
import DateHandler
import QuestionDialog
import GrampsDisplay
import ManagedWindow
import GrampsDb

sex = ( _("female"), _("male"), _("unknown"))

class PersonCompare(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, person1, person2, update=None) :

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        self.glade = gtk.glade.XML(const.merge_glade, "merge")
        window = self.glade.get_widget('merge')
        self.text1 = self.glade.get_widget('text1')
        self.text2 = self.glade.get_widget('text2')
        self.db = dbstate.db

        self.p1 = person1
        self.p2 = person2
        self.update = update
        
        self.set_window(window,self.glade.get_widget('title'),
                        _("Compare People"))
        self.display(self.text1.get_buffer(), person1)
        self.display(self.text2.get_buffer(), person2)

        self.glade.get_widget('cancel').connect('clicked',self.close)
        self.glade.get_widget('close').connect('clicked',self.merge)
        self.glade.get_widget('help').connect('clicked',self.help)

    def help(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-merge-people')

    def merge(self,obj):
        if check_for_spouse(self.p1,self.p2):
            QuestionDialog.ErrorDialog(
                _("Cannot merge people"),
                _("Spouses cannot be merged. To merge these people, "
                  "you must first break the relationship between them."))
        elif check_for_child(self.p1,self.p2):
            QuestionDialog.ErrorDialog(
                _("Cannot merge people"),
                _("A parent and child cannot be merged. To merge these "
                  "people, you must first break the relationship between "
                  "them."))
        else:
            if self.glade.get_widget('select1').get_active():
                merge = MergePeople(self.db,self.p1,self.p2)
            else:
                merge = MergePeople(self.db,self.p2,self.p1)
            self.close()
            merge.merge()
            if self.update:
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
        bref = person.get_birth_ref()
        if bref:
            self.add(tobj,normal,"%s:\t%s" % (_('Birth'),self.get_event_info(bref.ref)))
        dref = person.get_death_ref()
        if dref:
            self.add(tobj,normal,"%s:\t%s" % (_('Death'),self.get_event_info(dref.ref)))

        nlist = person.get_alternate_names()
        if len(nlist) > 0:
            self.add(tobj,title,_("Alternate Names"))
            for name in nlist:
                self.add(tobj,normal,NameDisplay.displayer.display_name(name))

        elist = person.get_event_ref_list()
        if len(elist) > 0:
            self.add(tobj,title,_("Events"))
            for event_ref in person.get_event_ref_list():
                event_handle = event_ref.ref
                name = str(
                    self.db.get_event_from_handle(event_handle).get_type())
                self.add(tobj,normal,"%s:\t%s" % (name,self.get_event_info(event_handle)))
        plist = person.get_parent_family_handle_list()

        if len(plist) > 0:
            self.add(tobj,title,_("Parents"))
            for fid in person.get_parent_family_handle_list():
                (fn,mn,gid) = self.get_parent_info(fid)
                self.add(tobj,normal,"%s:\t%s" % (_('Family ID'),gid))
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
                (fn,mn,pid) = self.get_parent_info(fid)
                family = self.db.get_family_from_handle(fid)
                self.add(tobj,normal,"%s:\t%s" % (_('Family ID'),pid))
                spouse_id = ReportUtils.find_spouse(person,family)
                if spouse_id:
                    spouse = self.db.get_person_from_handle(spouse_id)
                    self.add(tobj,indent,"%s:\t%s" % (_('Spouse'),name_of(spouse)))
                relstr = str(family.get_relationship())
                self.add(tobj,indent,"%s:\t%s" % (_('Type'),relstr))
                event = ReportUtils.find_marriage(self.db,family)
                if event:
                    self.add(tobj,indent,"%s:\t%s" % (
                        _('Marriage'), self.get_event_info(event.get_handle())))
                for child_ref in family.get_child_ref_list():
                    child = self.db.get_person_from_handle(child_ref.ref)
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
            date = DateHandler.get_date(event)
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


def check_for_spouse(p1, p2):

    f1 = sets.Set(p1.get_family_handle_list())
    f2 = sets.Set(p2.get_family_handle_list())

    return len(f1.intersection(f2)) != 0

def check_for_child(p1, p2):

    fs1 = sets.Set(p1.get_family_handle_list())
    fp1 = sets.Set(p1.get_parent_family_handle_list())

    fs2 = sets.Set(p2.get_family_handle_list())
    fp2 = sets.Set(p2.get_parent_family_handle_list())

    return len(fs1.intersection(fp2)) != 0 or len(fs2.intersection(fp1))

#-------------------------------------------------------------------------
#
# Merge People UI
#
#-------------------------------------------------------------------------
class MergePeopleUI(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, person1, person2, update=None):

        if check_for_spouse(person1, person2):
            QuestionDialog.ErrorDialog(
                _("Cannot merge people"),
                _("Spouses cannot be merged. To merge these people, "
                  "you must first break the relationship between them."))
            return

        if check_for_child(person1, person2):
            QuestionDialog.ErrorDialog(
                _("Cannot merge people"),
                _("A parent and child cannot be merged. To merge these "
                  "people, you must first break the relationship between "
                  "them."))
            return

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)
        
        glade = gtk.glade.XML(const.merge_glade, 'merge_people')
        window = glade.get_widget('merge_people')

        self.set_window(window, glade.get_widget('title'), _("Merge People"))

        p1 = glade.get_widget('person1')
        p2 = glade.get_widget('person2')
        n1 = name_of(person1)
        n2 = name_of(person2)

        p1.set_label(n1)
        p2.set_label(n2)

        glade.get_widget('help').connect('clicked',self.help)

        ret = gtk.RESPONSE_HELP
        while ret == gtk.RESPONSE_HELP:
            ret = self.window.run()
        
        if ret == gtk.RESPONSE_OK:

            if check_for_spouse(person1,person2):
                QuestionDialog.ErrorDialog(
                    _("Cannot merge people"),
                    _("Spouses cannot be merged. To merge these people, "
                      "you must first break the relationship between them."))
            elif check_for_child(person1,person2):
                QuestionDialog.ErrorDialog(
                    _("Cannot merge people"),
                    _("A parent and child cannot be merged. To merge these "
                      "people, you must first break the relationship between "
                      "them."))
            else:
                if p1.get_active():
                    merge = MergePeople(dbstate.db,person1,person2)
                else:
                    merge = MergePeople(dbstate.db,person2,person1)
                merge.merge()
                if update:
                    update()
        self.close()

    def build_menu_names(self,obj):
        return (_('Merge People'),None)

    def help(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-merge-people')


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
        text1 = one.get_note()
        text2 = two.get_note()
        
        if text1 and text1 != text2:
            one.set_note("%s\n\n%s" % (text1,text2))
        else:
            one.set_note(two.get_note())

    def copy_sources(self,one,two):
        slist = one.get_source_references()[:]
        for xsrc in two.get_source_references():
            for src in slist:
                if src.are_equal(xsrc):
                    break
            else:
                one.add_source_reference(xsrc)

    def debug_person(self,person, msg=""):
        if __debug__:
            print "## %s person handle %s" % (msg,person.get_handle())
            for h in person.get_family_handle_list():
                fam = self.db.get_family_from_handle(h)
                print " - family %s has father: %s, mother: %s" % \
                      (h,fam.get_father_handle(),fam.get_mother_handle())
            for h in person.get_parent_family_handle_list():
                print " - parent family %s" % h

    def merge(self):
        """
        Perform the actual merge. A new person is created to store the
        merged data. First, the person information is merged. This is a
        very straight forward process. Second, the families associated
        with the merged people must be modified to handle the family
        information. This process can be tricky.

        Finally, the merged person is delete from the database and the
        entire transaction is committed.
        """

        self.debug_person(self.p1, "P1")
        self.debug_person(self.p2, "P2")
        
        new = RelLib.Person()
        trans = self.db.transaction_begin()

        self.merge_person_information(new,trans)
        self.debug_person(new, "NEW")

        self.merge_family_information(new,trans)
        self.debug_person(new, "NEW")

        self.db.commit_person(new,trans)
        self.debug_person(new, "NEW")
        self.db.remove_person(self.old_handle,trans)
        self.db.transaction_commit(trans,"Merge Person")

    def merge_person_information(self,new,trans):
        """
        Merging the person's individual information is pretty simple. The
        person 'new' is a new, empty person. The data is loaded in this
        new person. The idea is that all information that can possibly be
        preserved is preserved.
        """
        self.old_handle = self.p2.get_handle()
        self.new_handle = self.p1.get_handle()

        # Choose the handle from the target person. Since this is internal
        # only information, no user visible information is lost.
        new.set_handle(self.new_handle)

        # The gender is chosen from the primary person. This is one case
        # where data may be lost if you merge the data from two people of
        # opposite genders.
        new.set_gender(self.p1.get_gender())

        # copy the GRAMPS Ids
        self.merge_gramps_ids(new)

        # copy names
        self.merge_names(new)

        # merge the event lists
        self.merge_event_lists(new)

        GrampsDb.set_birth_death_index(self.db, new)

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
        
    def merge_gramps_ids(self,new):
        """
        Merges the GRAMPS IDs. The new GRAMPS ID is taken from
        destination person. The GRAMPS ID of the other person is added
        to the merged person as an attribute.
        """
        # copy of GRAMPS ID as an attribute
        attr = RelLib.Attribute()
        attr.set_type('Merged GRAMPS ID')
        attr.set_value(self.p2.get_gramps_id())
        new.add_attribute(attr)

        # store GRAMPS ID of the destination person
        new.set_gramps_id(self.p1.get_gramps_id())

    def merge_names(self, new):
        """
        Merges the names of the two people into the destination. The
        primary name of the destination person is kept as the primary
        name.

        The other person's name is stored as an alternate name if it is
        not entirely identical to the destination person's primary name.

        Remaining alternate names are then added to the merged
        person's alternate names.
        """
        p1_name = self.p1.get_primary_name()
        p2_name = self.p2.get_primary_name()

        new.set_primary_name(self.p1.get_primary_name())
        if not p2_name.is_equal(p1_name):
            new.add_alternate_name(p2_name)
            
        for name in self.p1.get_alternate_names():
            new.add_alternate_name(name)
        for name in self.p2.get_alternate_names():
            new.add_alternate_name(name)

    def merge_birth(self, new,trans):
        """
        Merges the birth events of the two people. If the primary
        person does not have a birth event, then the birth event from
        the secodnary person is selected. If the primary person has
        a birth date, then the merged person gets the primary person's
        birth event, and the secondary person's birth event is added
        as a 'Alternate Birth' event.
        """
        ref1 = self.p1.get_birth_ref()
        ref2 = self.p2.get_birth_ref()

        if not ref1.is_equal(ref2):
            new.add_event_ref(ref2)

    def merge_death(self, new, trans):
        """
        Merges the death events of the two people. If the primary
        person does not have a death event, then the death event from
        the secodnary person is selected. If the primary person has
        a death date, then the merged person gets the primary person's
        death event, and the secondary person's death event is added
        as a 'Alternate Death' event.
        """
        ref1 = self.p1.get_death_ref()
        ref2 = self.p2.get_death_ref()

        if not ref1.is_equal(ref2):
            new.add_event_ref(ref2)

    def merge_event_lists(self, new):
        """
        Merges the events from the two people into the destination
        person.  Duplicates are not transferred.
        """
        data_list = new.get_event_ref_list()
        data_handle_list = [ref.ref for ref in data_list]

        add_ref_list1 = [ref for ref in self.p1.get_event_ref_list()
                         if ref.ref not in data_handle_list]

        add_ref_list2 = [ref for ref in self.p2.get_event_ref_list()
                         if ref.ref not in data_handle_list]

        new.set_event_ref_list(data_list+add_ref_list1+add_ref_list2)

    def merge_family_information(self, new, trans):
        """
        Merge the parent families and the relationship families of the
        selected people.
        """
        self.merge_parents(new, trans)
        self.merge_relationships(new, trans)
        self.debug_person(new, "NEW")
        
    def merge_parents(self, new, trans):
        """
        Merging the parent list is not too difficult. We grab the
        parent list of the destination person. We then loop through
        the parent list of the secondary person, adding to the parent
        list any parents that are not already there. This eliminates
        any duplicates.

        Once this has been completed, we loop through each family,
        converting any child handles referring to the secondary person
        to the destination person.
        """
        parent_list = self.p1.get_parent_family_handle_list()

        # copy handles of families that are not common between the
        # two lists
        for fid in self.p2.get_parent_family_handle_list():
            if fid not in parent_list:
                parent_list.append(fid)
                if __debug__:
                    print "Adding family to parent list", fid

        # loop through the combined list, converting the child handles
        # of the families, and adding the families to the merged
        # person
        
        for family_handle in parent_list:
            self.convert_child_ids(family_handle, self.new_handle,
                                   self.old_handle, trans)
            new.add_parent_family_handle(family_handle)
                    
    def convert_child_ids(self, fhandle, new_handle, old_handle, trans):
        """
        Search the family associated with fhandle, and replace 
        old handle with the new handle in all child references.
        """
        family = self.db.get_family_from_handle(fhandle)
        orig_ref_list = family.get_child_ref_list()
        new_ref_list = []

        # loop through original child list. If a handle matches the
        # old handle, replace it with the new handle if the new handle
        # is not already in the list

        for child_ref in orig_ref_list:
            if child_ref.ref == old_handle:
                if new_handle not in [ref.ref for ref in new_ref_list]:
                    new_ref = RelLib.ChildRef()
                    new_ref.ref = new_handle
                    new_ref_list.append(new_ref)
            elif child_ref.ref not in [ref.ref for ref in new_ref_list]:
                new_ref_list.append(child_ref)

        # compare the new list with the original list. If this list
        # is different, we need to save the changes to the database.
        if [ref.ref for ref in new_ref_list] \
               != [ref.ref for ref in orig_ref_list]:
            family.set_child_ref_list(new_ref_list)
            self.db.commit_family(family,trans)
    
    def merge_relationships(self,new,trans):
        """
        Merges the relationships associated with the merged people.
        """
        
        family_num = 0
        family_list = self.p1.get_family_handle_list()
        new.set_family_handle_list(family_list)
        
        for src_handle in self.p2.get_family_handle_list():

            src_family = self.db.get_family_from_handle(src_handle)
            family_num += 1

            if not src_family or src_family in family_list:
                continue

            tgt_family = self.find_modified_family(src_family)

            # existing family is found
            if tgt_family:
                # The target family is already a family in the person's
                # family list. 
                if tgt_family.get_handle() in self.p1.get_family_handle_list():
                    self.merge_existing_family(new, src_family, tgt_family, trans)
                    continue
            
                # This is the case the family is not already in the person's
                # family list.
                else:
                    self.merge_family_pair(tgt_family,src_family,trans)
                    
                    # change parents of the family to point to the new
                    # family
                    self.adjust_family_pointers(tgt_family, src_family, trans)
                                                
                    new.remove_family_handle(src_handle)
                    self.db.remove_family(src_handle,trans)
                    if __debug__:
                        print "Deleted src_family %s" % src_handle
            else:
                for fid in self.p1.get_family_handle_list():
                    if fid not in new.get_family_handle_list():
                        new.add_family_handle(fid)
                        if __debug__:
                            print "Adding family %s" % fid

            if src_handle in new.get_family_handle_list():
                continue
            src_family = self.db.get_family_from_handle(src_handle)
            new.add_family_handle(src_handle)
            if src_family.get_father_handle() == self.old_handle:
                src_family.set_father_handle(self.new_handle)
                if __debug__:
                    print "Family %s now has father %s" % (
                        src_handle, self.new_handle)
            if src_family.get_mother_handle() == self.old_handle:
                src_family.set_mother_handle(self.new_handle)
                if __debug__:
                    print "Family %s now has mother %s" % (
                        src_handle, self.new_handle)
            self.db.commit_family(src_family,trans)

        # a little debugging here

##         cursor = self.db.get_family_cursor()
##         data = cursor.first()
##         while data:
##             fam = RelLib.Family()
##             fam.unserialize(data[1])
##             if self.p2 in [ref.ref for ref in fam.get_child_ref_list()]:
##                 fam.remove_child_ref(self.p2)
##                 fam.add_child_ref(self.p1)
##             if self.p2 == fam.get_father_handle():
##                 fam.set_father_handle(self.p1)
##             if self.p2 == fam.get_mother_handle():
##                 fam.set_mother_handle(self.p1)
##             if fam.get_father_handle() == None and fam.get_mother_handle() == None:
##                 self.delete_empty_family(fam,trans)
##             data = cursor.next()

    def find_modified_family(self,family):
        """
        Look for a existing family that matches the merged person. This means
        looking at the current family, and replacing the secondary person's
        handle with the merged person's handle. Search the family table for
        a family that matches this new mother/father pair.

        If no family is found, return None
        """

        family_handle = family.get_handle()

        if __debug__:
            print "SourceFamily: %s" % family_handle

        # Determine the mother and father handles for the search.
        # This is determined by replacing the secodnary person's
        # handle with the primary person's handle in the mother/father
        # pair.
        
        mhandle = family.get_mother_handle()
        if mhandle == self.old_handle:
            mhandle = self.new_handle

        fhandle = family.get_father_handle()
        if fhandle == self.old_handle:
            fhandle = self.new_handle

        # loop through the families using a cursor. Check the handles
        # for a mother/father match.
        
        cursor = self.db.get_family_cursor()
        node = cursor.next()
        myfamily = None
        while node:
            # data[2] == father_handle field, data[2] == mother_handle field
            (thandle,data) = node
            if data[2] == fhandle and data[3] == mhandle and thandle != family_handle:
                myfamily = RelLib.Family()
                myfamily.unserialize(data)
                break
            node = cursor.next()

        if __debug__:
            if myfamily:
                print "TargetFamily: %s" % myfamily.get_handle()
            else:
                print "TargetFamily: None"
            
        cursor.close()
        return myfamily

    def merge_existing_family(self, new, src_family, tgt_family, trans):

        src_family_handle = src_family.get_handle()
        
        father_id = tgt_family.get_father_handle()
        father = self.db.get_person_from_handle(father_id)
                    
        mother_id = tgt_family.get_mother_handle()
        mother = self.db.get_person_from_handle(mother_id)

        if father and src_family_handle in father.get_family_handle_list():
            father.remove_family_handle(src_family_handle)
            if __debug__:
                print "Removed family %s from father %s" % (src_family_handle, father_id)
            self.db.commit_person(father,trans)
        if mother and src_family_handle in mother.get_family_handle_list():
            mother.remove_family_handle(src_family_handle)
            if __debug__:
                print "Removed family %s from mother %s" % (src_family_handle, mother_id)
            self.db.commit_person(mother,trans)
                        
        self.merge_family_pair(tgt_family,src_family,trans)
                        
        for child_ref in src_family.get_child_ref_list():
            child_handle = child_ref.ref
            if child_handle != self.new_handle:
                child = self.db.get_person_from_handle(child_handle)
            if child.remove_parent_family_handle(src_family_handle):
                if __debug__:
                    print "Remove parent family %s from %s" \
                          % (src_family_handle,child_handle)
                self.db.commit_person(child,trans)

        # delete the old source family
        self.db.remove_family(src_family_handle,trans)
        if __debug__:
            print "Deleted src_family %s" % src_family_handle
        self.db.commit_family(tgt_family,trans)
        if tgt_family.get_handle() not in new.get_family_handle_list():
            new.add_family_handle(tgt_family.get_handle())

    def merge_family_pair(self,tgt_family,src_family,trans):

        tgt_family_child_handles = [ref.ref
                                    for ref in tgt_family.get_child_ref_list()]
        # copy children from source to target
        for child_ref in src_family.get_child_ref_list():
            child_handle = child_ref.ref
            if child_handle not in tgt_family_child_handles:
                child = self.db.get_person_from_handle(child_handle)
                parents = child.get_parent_family_handle_list()
                tgt_family.add_child_ref(child_ref)
                if child.get_main_parents_family_handle() == src_family.get_handle():
                    child.set_main_parent_family_handle(tgt_family.get_handle())
                i = 0
                for fam in parents[:]:
                    if fam[0] == src_family.get_handle():
                        parents[i] = (tgt_family.get_handle(),fam[1],fam[2])
                    i += 1
                self.db.commit_person(child,trans)

        # merge family events

        ereflist = tgt_family.get_event_ref_list()
        eref_handle_list = [ref.ref for ref in ereflist]

        add_ref_list = [ref for ref in src_family.get_event_ref_list()
                        if ref.ref not in eref_handle_list]
        tgt_family.set_event_ref_list(ereflist+add_ref_list)
        

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

    def adjust_family_pointers(self, tgt_family, src_family, trans):
        """
        Remove the people from one family and merge them into the other.
        It is not necessary to remove from the src_family, since the
        src_family is going to be removed.
        """
        src_family_handle = src_family.get_handle()
        tgt_family_handle = tgt_family.get_handle()
        
        father_handle = src_family.get_father_handle()
        if father_handle:
            father = self.db.get_person_from_handle(father_handle)

            # add to new family
            father.add_family_handle(tgt_family_handle)
            if __debug__:
                print "Added family %s to father %s" % (
                    tgt_family_handle, father_handle)

            # commit the change
            self.db.commit_person(father,trans)

        mother_handle = src_family.get_mother_handle()
        if mother_handle:
            mother = self.db.get_person_from_handle(mother_handle)

            # add to new family
            mother.add_family_handle(tgt_family_handle)
            if __debug__:
                print "Added family %s to mother %s" % (
                    tgt_family_handle, mother_handle)

            # commit the change
            self.db.commit_person(mother,trans)

        # remove the children from the old family
        for child_ref in src_family.get_child_ref_list():
            child_handle = child_ref.ref
            if child_handle != self.new_handle:
                child = self.db.get_person_from_handle(child_handle)
                if child.remove_parent_family_handle(src_family_handle):
                    self.db.commit_person(child,trans)


    def remove_marriage(self,family,person,trans):
        if person:
            person.remove_family_handle(family.get_handle())
            if family.get_father_handle() == None and family.get_mother_handle() == None:
                self.delete_empty_family(family,trans)

    def delete_empty_family(self,family,trans):
        family_handle = family.get_handle()
        for child_ref in family.get_child_ref_list():
            child_handle = child_ref.ref
            child = self.db.get_person_from_handle(child_handle)
            if child.get_main_parents_family_handle() == family_handle:
                child.set_main_parent_family_handle(None)
            else:
                child.remove_parent_family_handle(family_handle)
            self.db.commit_person(child,trans)
        self.db.remove_family(family_handle,trans)
        if __debug__:
            print "Deleted empty family %s" % family_handle

    def merge_notes(self, note1, note2):
        t1 = note1.get()
        t2 = note2.get()
        if not t2:
            return note1
        elif not t1:
            return note2
        elif t1 and t2:
            note1.append("\n" + t2)
            note1.set_format(note1.get_format() or note2.get_format())
            return note1
        return None

