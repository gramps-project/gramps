#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Martin Hawlisch, Donald N. Allingham
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

"Create person and family testcases"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import re
import time
from random import randint,choice
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import RelLib
import latin_utf8 
import Utils
import const
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class TestcaseGenerator:
    def __init__(self,database,active_person,callback,parent):
        print "__init__"
        self.db = database
        self.person_count = 0
        
    def run(self):
        print "run"
        self.trans = self.db.transaction_begin()
        self.generate_broken_relations()
        person1_h = self.generate_person(0)
        self.generate_family(person1_h)
        self.db.transaction_commit(self.trans,_("Testcase generator"))
 

    def generate_broken_relations(self):
        # Create a family, that links to father and mother, but father does not link back
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken1","Family links to this person, but person does not link back")
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken1",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        #person1 = self.db.get_person_from_handle(person1_h)
        #person1.add_family_handle(fam_h)
        #self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        # Create a family, that misses the link to the father
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken2",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken2",None)
        fam = RelLib.Family()
        #fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        # Create a family, that misses the link to the mother
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken3",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken3",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        #fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        # Create a family, that links to father and mother, but father does not link back
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken4",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken4","Family links to this person, but person does not link back")
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        #person2 = self.db.get_person_from_handle(person2_h)
        #person2.add_family_handle(fam_h)
        #self.db.commit_person(person2,self.trans)

        # Create two married people of same sex.
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken5",None)
        person2_h = self.generate_person(RelLib.Person.MALE,"Broken5",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        # Create a family, that contains an invalid handle to for the father
        #person1_h = self.generate_person(RelLib.Person.MALE,"Broken6",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken6",None)
        fam = RelLib.Family()
        fam.set_father_handle("InvalidHandle1")
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        #person1 = self.db.get_person_from_handle(person1_h)
        #person1.add_family_handle(fam_h)
        #self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        # Create a family, that contains an invalid handle to for the mother
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken7",None)
        #person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken7",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle("InvalidHandle2")
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        #person2 = self.db.get_person_from_handle(person2_h)
        #person2.add_family_handle(fam_h)
        #self.db.commit_person(person2,self.trans)


        # Creates a family where the child does not link back to the family
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken8",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken8",None)
        child_h = self.generate_person(None,"Broken8",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam.add_child_handle(child_h)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        #child = self.db.get_person_from_handle(child_h)
        #person2.add_parent_family_handle(fam_h)
        #self.db.commit_person(child,self.trans)

        # Creates a family where the child is not linked, but the child links to the family
        person1_h = self.generate_person(RelLib.Person.MALE,"Broken9",None)
        person2_h = self.generate_person(RelLib.Person.FEMALE,"Broken9",None)
        child_h = self.generate_person(None,"Broken9",None)
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        #fam.add_child_handle(child_h)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        child = self.db.get_person_from_handle(child_h)
        person2.add_parent_family_handle(fam_h,RelLib.Person.CHILD_REL_BIRTH,RelLib.Person.CHILD_REL_BIRTH)
        self.db.commit_person(child,self.trans)

        # Creates a person with an event having a witness reference to a nonexisting person
        person_h = self.generate_person(None,"Broken10",None)
        witness = RelLib.Witness()
        witness.set_type(RelLib.Event.ID)
        witness.set_value("InvalidHandle3")
        witness.set_comment("Pointing to non existing person");
        event = RelLib.Event()
        event.add_witness(witness)
        event.set_name("Christening")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_handle(event_h)
        self.db.commit_person(person,self.trans)

    
    def generate_person(self,gender=None,lastname=None,note=None):
        print "generate_person"
        np = RelLib.Person()
        
        # Note
        if note:
            np.set_note(note)
            
        # Gender
        if gender == None:
            gender = randint(0,1)
            print "Random gender"
        np.set_gender(gender)
        
        # Name
        syllables1 = ["sa","li","na","ma","no","re","mi","cha","ki","du"]
        syllables2 = ["as","il","an","am","on","er","im","ach","ik","ud"]

        name = RelLib.Name()
        firstname = ""
        for i in range(0,randint(2,5)):
            firstname = firstname + choice(syllables1)
        if not lastname:
            lastname = ""
            for i in range(0,randint(2,5)):
                lastname = lastname + choice(syllables1)
        name.set_first_name(firstname)
        name.set_surname(lastname)
        np.set_primary_name(name)

        self.person_count = self.person_count+1

        return( self.db.add_person(np,self.trans))
        
    def generate_family(self,person1_h):
        print "generate_family"
        person1 = self.db.get_person_from_handle(person1_h)
        if person1.get_gender() == 1:
            person2_h = self.generate_person(0)
        else:
            person2_h = person1_h
            person1_h = self.generate_person(1)
        
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam_h = self.db.add_family(fam,self.trans)
        fam = self.db.commit_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        lastname = person1.get_primary_name().get_surname()     
        
        if self.person_count < 20:
            for i in range(0,randint(1,10)):
                child_h = self.generate_person(None, lastname)
                fam = self.db.get_family_from_handle(fam_h)
                fam.add_child_handle(child_h)
                self.db.commit_family(fam,self.trans)
                child = self.db.get_person_from_handle(child_h)
                child.add_parent_family_handle(fam_h,RelLib.Person.CHILD_REL_BIRTH,RelLib.Person.CHILD_REL_BIRTH)
                self.db.commit_person(child,self.trans)
                if randint(0,3) > 0:
                    self.generate_family(child_h)
        

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def TestcaseGeneratorPlugin(database,active_person,callback,parent=None):
    print "TestcaseGeneratorPlugin"
    fg = TestcaseGenerator(database,active_person,callback,parent)
    fg.run()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    TestcaseGeneratorPlugin,
    _("Generate Testcases for persons and families"),
    category=_("Debug"),
    description=_("The testcase generator will generate some persons and families."
                    "that habe brolen links in the database or data that is in conflict to a relation.")
    )
