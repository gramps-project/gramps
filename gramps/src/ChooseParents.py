#
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

"""
ChooseParents interface allows users to select the paretns of an
individual.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import sort
import Utils
import GrampsCfg
import Sorter

#-------------------------------------------------------------------------
#
# ChooseParents
#
#-------------------------------------------------------------------------
class ChooseParents:
    """
    Displays the Choose Parents dialog box, allowing the parents
    to be edited.
    """
    def __init__(self,db,person,family,family_update,full_update):
        """
        Creates a ChoosePerson dialog box.

        db - database associated the person
        person - person whose parents we are selecting
        family - current family
        family_update - task that updates the family display
        full_update - task that updates the main display 
        """
        self.db = db
        self.person = person
        self.family = family
        self.family_update = family_update
        self.full_update = full_update
        self.old_type = ""
        self.type = ""
        
        if self.family:
            self.father = self.family.getFather()
            self.mother = self.family.getMother()
        else:
            self.mother = None
            self.father = None

        self.glade = libglade.GladeXML(const.gladeFile,"familyDialog")
        self.top = self.glade.get_widget("familyDialog")
	self.mother_rel = self.glade.get_widget("mrel")
	self.father_rel = self.glade.get_widget("frel")
        self.fcombo = self.glade.get_widget("prel_combo")
        self.prel = self.glade.get_widget("prel")
        self.title = self.glade.get_widget("chooseTitle")
        self.father_list = self.glade.get_widget("fatherList")
        self.mother_list = self.glade.get_widget("motherList")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")
        self.fcombo.set_popdown_strings(const.familyRelations)

        fmap = [(2,self.glade.get_widget('fname_arrow')),
                (3,self.glade.get_widget('fbirth_arrow'))]
        self.fsort = Sorter.Sorter(self.father_list,fmap,'flist')
        mmap = [(2,self.glade.get_widget('mname_arrow')),
                (3,self.glade.get_widget('mbirth_arrow'))]
        self.msort = Sorter.Sorter(self.mother_list,mmap,'mlist')
        self.mother_list.set_column_visibility(2,0)
        self.father_list.set_column_visibility(2,0)
        self.mother_list.set_column_visibility(3,0)
        self.father_list.set_column_visibility(3,0)
        self.mother_list.set_sort_column(2)
        self.father_list.set_sort_column(2)
        
        for (f,mr,fr) in self.person.getParentList():
            if f == self.family:
                self.mother_rel.set_text(_(mr))
                self.father_rel.set_text(_(fr))
                break
        else:
            self.mother_rel.set_text(_("Birth"))
            self.father_rel.set_text(_("Birth"))

        if self.family:
            self.type = self.family.getRelationship()
        else:
            self.type = "Married"
        self.prel.set_text(_(self.type))
        self.redraw()
        
        self.glade.signal_autoconnect({
            "on_motherList_select_row" : self.mother_list_select_row,
            "on_fatherList_select_row" : self.father_list_select_row,
            "on_save_parents_clicked"  : self.save_parents_clicked,
            "on_add_parent_clicked"    : self.add_parent_clicked,
            "on_prel_changed"          : self.parent_relation_changed,
            "on_combo_insert_text"     : Utils.combo_insert_text,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        text = _("Choose the Parents of %s") % GrampsCfg.nameof(self.person)
        self.title.set_text(text)
        self.top.show()

    def redraw(self):
        """Redraws the potential father and mother lists"""
        self.father_list.freeze()
        self.mother_list.freeze()
        self.father_list.clear()
        self.mother_list.clear()

        self.father_list.append(["Unknown","","",""])
        self.father_list.set_row_data(0,None)

        self.mother_list.append(["Unknown","","",""])
        self.mother_list.set_row_data(0,None)

        father_index = 1
        mother_index = 1
        fsel = 0
        msel = 0
        pkey = self.person.getId()
        gender = self.person.getGender()
        if self.father:
            fid = self.father.getId()
        else:
            fid = None
        if self.mother:
            mid = self.mother.getId()
        else:
            mid = None
            
        for key in self.db.getPersonKeys():
            if pkey == key:
                continue
            if gender == const.unknown:
                continue
            if fid == key:
                fsel = father_index
            if mid == key:
                msel = mother_index
            dinfo = self.db.getPersonDisplay(key)
            rdata = [dinfo[0],dinfo[3],dinfo[5],dinfo[6]]
            if self.type == "Partners":
                self.father_list.append(rdata)
                self.father_list.set_row_data(father_index,dinfo[1])
                father_index = father_index + 1
                self.mother_list.append(rdata)
                self.mother_list.set_row_data(mother_index,dinfo[1])
                mother_index = mother_index + 1
            elif dinfo[2] == const.male:
                self.father_list.append(rdata)
                self.father_list.set_row_data(father_index,dinfo[1])
                father_index = father_index + 1
            else:
                self.mother_list.append(rdata)
                self.mother_list.set_row_data(mother_index,dinfo[1])
                mother_index = mother_index + 1

        self.mother_list.select_row(msel,0)
        self.mother_list.sort()
        self.father_list.select_row(fsel,0)
        self.father_list.sort()
        self.mother_list.thaw()
        self.father_list.thaw()
        if self.father_list.selection:
            self.father_list.moveto(self.father_list.selection[0],0)
        if self.mother_list.selection:
            self.mother_list.moveto(self.mother_list.selection[0],0)

        if self.type == "Partners":
            self.mlabel.set_label(_("Parent"))
            self.flabel.set_label(_("Parent"))
        else:
            self.mlabel.set_label(_("Mother"))
            self.flabel.set_label(_("Father"))

    def parent_relation_changed(self,obj):
        """Called everytime the parent relationship information is changegd"""
        self.old_type = self.type
        self.type = const.save_frel(obj.get_text())
        if self.old_type == "Partners" or self.type == "Partners":
            self.redraw()
        
    def find_family(self,father,mother):
        """
        Finds the family associated with the father and mother.
        If one does not exist, it is created.
        """
        if not father and not mother:
            return None
	
        families = self.db.getFamilyMap().values()
        for family in families:
            if family.getFather() == father and family.getMother() == mother:
                return family
            elif family.getFather() == mother and family.getMother() == father:
                return family

        family = self.db.newFamily()
        family.setFather(father)
        family.setMother(mother)
        family.addChild(self.person)
    
        if father:
            father.addFamily(family)
        if mother:
            mother.addFamily(family)
        return family

    def mother_list_select_row(self,obj,a,b,c):
        """Called when a row is selected in the mother list. Sets the
        active mother based off the id associated with the row."""
        
        id = obj.get_row_data(a)
        if id:
            self.mother = self.db.getPerson(id)
        else:
            self.mother = None

    def father_list_select_row(self,obj,a,b,c):
        """Called when a row is selected in the father list. Sets the
        active father based off the id associated with the row."""
        id = obj.get_row_data(a)
        if id:
            self.father = self.db.getPerson(id)
        else:
            self.father = None

    def save_parents_clicked(self,obj):
        """
        Called with the OK button nis pressed. Saves the selected people as parents
        of the main perosn.
        """
        mother_rel = const.childRelations[self.mother_rel.get_text()]
        father_rel = const.childRelations[self.father_rel.get_text()]

        if self.father or self.mother:
            if self.mother and not self.father:
                if self.mother.getGender() == RelLib.Person.male:
                    self.father = self.mother
                    self.mother = None
                self.family = self.find_family(self.father,self.mother)
            elif self.father and not self.mother: 
                if self.father.getGender() == RelLib.Person.female:
                    self.mother = self.father
                    self.father = None
                self.family = self.find_family(self.father,self.mother)
            elif self.mother.getGender() != self.father.getGender():
                if self.type == "Partners":
                    self.type = "Unknown"
                if self.father.getGender() == RelLib.Person.female:
                    x = self.father
                    self.father = self.mother
                    self.mother = x
                self.family = self.find_family(self.father,self.mother)
            else:
                self.type = "Partners"
                self.family = self.find_family(self.father,self.mother)
        else:    
            self.family = None

        Utils.destroy_passed_object(obj)
        if self.family:
            self.family.setRelationship(self.type)
            self.change_family_type(self.family,mother_rel,father_rel)
        self.family_update(None)

    def add_new_parent(self,person):
        """Adds a new person to either the father list or the mother list,
        depending on the gender of the person."""
        id = person.getId()
        self.type = const.save_frel(self.prel.get_text())
        dinfo = self.db.getPersonDisplay(id)
        rdata = [dinfo[0],dinfo[3],dinfo[5],dinfo[6]]

        if self.type == "Partners":
            self.parent_relation_changed(self.prel)
        elif person.getGender() == RelLib.Person.male:
            self.father_list.insert(0,rdata)
            self.father_list.set_row_data(0,id)
            self.father_list.select_row(0,0)
            self.father_list.sort()
            self.father_list.moveto(self.father_list.selection[0],0)
        else:
            self.mother_list.insert(0,rdata)
            self.mother_list.set_row_data(0,id)
            self.mother_list.select_row(0,0)
            self.mother_list.moveto(0,0)
            self.mother_list.sort()
            self.mother_list.moveto(self.mother_list.selection[0],0)
        self.full_update()
        
    def add_parent_clicked(self,obj):
        """Called with the Add New Person button is pressed. Calls the QuickAdd
        class to create a new person."""
        
        import QuickAdd
        QuickAdd.QuickAdd(self.db,"male",self.add_new_parent)

    def change_family_type(self,family,mother_rel,father_rel):
        """
        Changes the family type of the specified family. If the family
        is None, the the relationship type shoud be deleted.
        """
        if self.person not in family.getChildList():
            family.addChild(self.person)
        for fam in self.person.getParentList():
            if family == fam[0]:
                if mother_rel == fam[1] and father_rel == fam[2]:
                    return
                if mother_rel != fam[1] or father_rel != fam[2]:
                    self.person.removeAltFamily(family)
                    self.person.addAltFamily(family,mother_rel,father_rel)
                    break
        else:
            self.person.addAltFamily(family,mother_rel,father_rel)
        Utils.modified()

