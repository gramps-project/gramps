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
import traceback
import sys
from random import randint,choice
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
import gtk 
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import Date
import RelLib
import Tool
import const
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp
from DateHandler import displayer as _dd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class TestcaseGenerator(Tool.Tool):

    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        if db.readonly:
            return
        
        Tool.Tool.__init__(self,db,person,options_class,name)

        self.person_count = 0
        self.persons_todo = []
        self.parents_todo = []
        if person:
            self.persons_todo.append(person.get_handle())
            self.parents_todo.append(person.get_handle())

        if parent:
            self.init_gui(parent)
        else:
            self.run_tool(cli=True)

    def init_gui(self,parent):
        title = "%s - GRAMPS" % _("Generate testcases")
        self.top = gtk.Dialog(title)
        self.top.set_default_size(400,150)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % _("Generate testcases"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label,0,0,5)

        self.check_bugs = gtk.CheckButton( _("Generate Database errors"))
        self.check_bugs.set_active( self.options.handler.options_dict['bugs'])
        self.top.vbox.pack_start(self.check_bugs,0,0,5)

        self.check_dates = gtk.CheckButton( _("Generate date tests"))
        self.check_dates.set_active( self.options.handler.options_dict['dates'])
        self.top.vbox.pack_start(self.check_dates,0,0,5)

        self.check_persons = gtk.CheckButton( _("Generate dummy families"))
        self.check_persons.set_active( self.options.handler.options_dict['persons'])
        self.top.vbox.pack_start(self.check_persons,0,0,5)

        self.check_trans = gtk.CheckButton( _("Don't block transactions"))
        self.check_trans.set_active( self.options.handler.options_dict['no_trans'])
        self.top.vbox.pack_start(self.check_trans,0,0,5)

        self.check_longnames = gtk.CheckButton( _("Generate long names"))
        self.check_longnames.set_active( self.options.handler.options_dict['long_names'])
        self.top.vbox.pack_start(self.check_longnames,0,0,5)

        self.entry_count = gtk.Entry()
        self.entry_count.set_text( unicode( self.options.handler.options_dict['person_count']))
        self.top.vbox.pack_start(self.entry_count,0,0,5)

        self.top.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.top.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        self.top.show_all()

        response = self.top.run()
        self.options.handler.options_dict['bugs']  = int(
            self.check_bugs.get_active())
        self.options.handler.options_dict['dates']  = int(
            self.check_dates.get_active())
        self.options.handler.options_dict['persons']  = int(
            self.check_persons.get_active())
        self.options.handler.options_dict['no_trans']  = int(
            self.check_trans.get_active())
        self.options.handler.options_dict['long_names']  = int(
            self.check_longnames.get_active())
        self.options.handler.options_dict['person_count']  = int(
            self.entry_count.get_text())
        self.top.destroy()

        if response == gtk.RESPONSE_OK:
            self.run_tool( cli=False)
            # Save options
            self.options.handler.save_options()
        
    def run_tool(self, cli=False):
        self.cli = cli
        if( not cli):
            title = "%s - GRAMPS" % _("Generate testcases")
            self.top = gtk.Window()
            self.top.set_title(title)
            self.top.set_position(gtk.WIN_POS_MOUSE)
            self.top.set_modal(True)
            self.top.set_default_size(400,150)
            vbox = gtk.VBox()
            self.top.add(vbox)
            label = gtk.Label(_("Generating persons and families.\nPlease wait."))
            vbox.pack_start(label,0,0,5)
            self.progress = gtk.ProgressBar()
            self.progress.set_fraction(0.0)
            vbox.pack_end(self.progress,0,0,5)
            self.top.show_all()
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.transaction_count = 0;
        
        self.trans = self.db.transaction_begin()
        if not self.options.handler.options_dict['no_trans']:
            self.trans.set_batch(True)
            self.db.disable_signals()

        if self.options.handler.options_dict['no_trans']:
    
            print "TESTING SIGNALS..."
    
            print "\nCREATE PERSON"
            p = RelLib.Person()
            self.db.add_person( p, self.trans)
            print "\nUPDATE PERSON"
            self.db.commit_person( p, self.trans)
            print "\nDELETE PERSON"
            self.db.remove_person( p.get_handle(), self.trans)
    
            print "\nCREATE FAMILY"
            f = RelLib.Family()
            self.db.add_family( f, self.trans)
            print "\nUPDATE FAMILY"
            self.db.commit_family( f, self.trans)
            print "\nDELETE FAMILY"
            self.db.remove_family( f.get_handle(), self.trans)
    
            print "\nCREATE EVENT"
            e = RelLib.Event()
            self.db.add_event( e, self.trans)
            print "\nUPDATE EVENT"
            self.db.commit_event( e, self.trans)
            print "\nDELETE EVENT"
            self.db.remove_event( e.get_handle(), self.trans)
    
            print "\nCREATE PLACE"
            p = RelLib.Place()
            self.db.add_place( p, self.trans)
            print "\nUPDATE PLACE"
            self.db.commit_place( p, self.trans)
            print "\nDELETE PLACE"
            self.db.remove_place( p.get_handle(), self.trans)
    
            print "\nCREATE SOURCE"
            s = RelLib.Source()
            self.db.add_source( s, self.trans)
            print "\nUPDATE SOURCE"
            self.db.commit_source( s, self.trans)
            print "\nDELETE SOURCE"
            self.db.remove_source( s.get_handle(), self.trans)
    
            print "\nCREATE MEDIA"
            m = RelLib.MediaObject()
            self.db.add_object( m, self.trans)
            print "\nUPDATE MEDIA"
            self.db.commit_media_object( m, self.trans)
            print "\nDELETE MEDIA"
            self.db.remove_object( m.get_handle(), self.trans)
    
            print "DONE."
    
    
            print "TESTING DB..."
    
            print "\nCREATE PERSON None"
            self.db.add_person( None, self.trans)
            print "\nUPDATE PERSON None"
            self.db.commit_person( None, self.trans)
            print "\nDELETE PERSON Invalid Handle"
            self.db.remove_person( "Invalid Handle", self.trans)
    
            print "\nCREATE FAMILY None"
            self.db.add_family( None, self.trans)
            print "\nUPDATE FAMILY None"
            self.db.commit_family( None, self.trans)
            print "\nDELETE FAMILY Invalid Handle"
            self.db.remove_family( "Invalid Handle", self.trans)
    
            print "\nCREATE EVENT None"
            self.db.add_event( None, self.trans)
            print "\nUPDATE EVENT None"
            self.db.commit_event( None, self.trans)
            print "\nDELETE EVENT Invalid Handle"
            self.db.remove_event( "Invalid Handle", self.trans)
    
            print "\nCREATE PLACE None"
            self.db.add_place( None, self.trans)
            print "\nUPDATE PLACE None"
            self.db.commit_place( None, self.trans)
            print "\nDELETE PLACE Invalid Handle"
            self.db.remove_place( "Invalid Handle", self.trans)
    
            print "\nCREATE SOURCE None"
            self.db.add_source( None, self.trans)
            print "\nUPDATE SOURCE None"
            self.db.commit_source( None, self.trans)
            print "\nDELETE SOURCE Invalid Handle"
            self.db.remove_source( "Invalid Handle", self.trans)
    
            print "\nCREATE MEDIA None"
            self.db.add_object( None, self.trans)
            print "\nUPDATE MEDIA None"
            self.db.commit_media_object( None, self.trans)
            print "\nDELETE MEDIA Invalid Handle"
            self.db.remove_object( "Invalid Handle", self.trans)
    
            print "DONE."
        
        
        if self.options.handler.options_dict['bugs']\
            or self.options.handler.options_dict['dates']\
            or self.options.handler.options_dict['persons']:
            
            self.default_url = RelLib.Url()
            self.default_url.set_path("http://www.gramps-project.org/")
            self.default_url.set_description("GRAMPS Project Homepage")
            self.default_source = RelLib.Source()
            self.default_source.set_title("TestcaseGenerator")
            self.default_source.set_note("Generated by TestcaseGenerator")
            self.default_source.set_data_item("Testcase Attribute", "Value test")
            self.db.add_source(self.default_source, self.trans)
            self.default_sourceref = RelLib.SourceRef()
            self.default_sourceref.set_base_handle(self.default_source.get_handle())
            self.default_attribute = RelLib.Attribute()
            self.default_attribute.set_type("Testcase Attribute")
            self.default_attribute.set_value("Value test")
            self.default_attribute.set_note("Generated by TestcaseGenerator")
            self.default_attribute.add_source_reference(self.default_sourceref)
            self.default_media = RelLib.MediaObject()
            self.default_media.set_description("TestcaseGenerator media")
            self.default_media.set_path("/tmp/TestcaseGenerator.png")
            self.default_media.set_mime_type("image/png")
            self.default_media.set_note("Generated by TestcaseGenerator")
            self.default_media.add_source_reference(self.default_sourceref)
            self.default_media.add_attribute(self.default_attribute)
            self.db.add_object(self.default_media, self.trans)
            self.default_mediaref = RelLib.MediaRef()
            self.default_mediaref.set_reference_handle(self.default_media.get_handle())
            self.default_mediaref.set_note("Generated by TestcaseGenerator")
            self.default_mediaref.add_source_reference(self.default_sourceref)
            self.default_mediaref.add_attribute(self.default_attribute)
            self.default_source.add_media_reference(self.default_mediaref)
            self.db.commit_source(self.default_source, self.trans)
            self.default_place = RelLib.Place()
            self.default_place.set_title("TestcaseGenerator place")
            self.default_place.set_note("Generated by TestcaseGenerator")
            self.default_place.add_source_reference(self.default_sourceref)
            self.default_place.add_media_reference(self.default_mediaref)
            self.default_place.add_url(self.default_url)
            self.db.add_place(self.default_place, self.trans)
            self.default_address = RelLib.Address()
            self.default_address.set_street("Teststreet")
            self.default_address.set_phone("012 34 56 78")
            self.default_address.set_city("Testcity")
            self.default_address.set_state("Teststate")
            self.default_address.set_country("Testcountry")
            self.default_address.set_postal_code("12345")
            self.default_address.set_note("Generated by TestcaseGenerator")
            self.default_address.add_source_reference(self.default_sourceref)

        if self.options.handler.options_dict['bugs']:
            self.generate_broken_relations()
        
        if self.options.handler.options_dict['dates']:
            self.generate_date_tests()

        if self.options.handler.options_dict['persons']:
            if not self.persons_todo:
                self.persons_todo.append( self.generate_person(0))
            for person_h in self.persons_todo:
                self.generate_family(person_h)
                if randint(0,3) == 0:
                    self.generate_family(person_h)
                if randint(0,7) == 0:
                    self.generate_family(person_h)
                if self.person_count > self.options.handler.options_dict['person_count']:
                    break
                for child_h in self.parents_todo:
                    self.generate_parents(child_h)
                    if self.person_count > self.options.handler.options_dict['person_count']:
                        break
            
        self.db.transaction_commit(self.trans,_("Testcase generator"))
        if not self.options.handler.options_dict['no_trans']:
            self.db.enable_signals()
            self.db.request_rebuild()
        if( not cli):
            self.top.destroy()
        

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP


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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        child.add_parent_family_handle(fam_h,RelLib.Person.CHILD_REL_BIRTH,RelLib.Person.CHILD_REL_BIRTH)
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

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
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing birth event handle set
        person_h = self.generate_person(None,"Broken11",None)
        person = self.db.get_person_from_handle(person_h)
        person.set_birth_handle("InvalidHandle4")
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing death event handle set
        person_h = self.generate_person(None,"Broken12",None)
        person = self.db.get_person_from_handle(person_h)
        person.set_death_handle("InvalidHandle5")
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing event handle set
        person_h = self.generate_person(None,"Broken13",None)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_handle("InvalidHandle6")
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a birth event having an empty type
        person_h = self.generate_person(None,"Broken14",None)
        event = RelLib.Event()
        event.set_description("Test for Broken14")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.set_birth_handle(event_h)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a death event having an empty type
        person_h = self.generate_person(None,"Broken15",None)
        event = RelLib.Event()
        event.set_description("Test for Broken15")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.set_death_handle(event_h)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with an event having an empty type
        person_h = self.generate_person(None,"Broken16",None)
        event = RelLib.Event()
        event.set_description("Test for Broken16")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_handle(event_h)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a birth event pointing to nonexisting place
        person_h = self.generate_person(None,"Broken17",None)
        event = RelLib.Event()
        event.set_name("Birth")
        event.set_place_handle("InvalidHandle7")
        event.set_description("Test for Broken17")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.set_birth_handle(event_h)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with an event pointing to nonexisting place
        person_h = self.generate_person(None,"Broken18",None)
        event = RelLib.Event()
        event.set_name("Birth")
        event.set_place_handle("InvalidHandle8")
        event.set_description("Test for Broken18")
        event_h = self.db.add_event(event,self.trans)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_handle(event_h)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP


    def generate_date_tests(self):
        dates = []
        # first some valid dates
        calendar = Date.CAL_GREGORIAN
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
            for modifier in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, Date.MOD_ABOUT):
                for slash1 in (False,True):
                    d = Date.Date()
                    d.set(quality,modifier,calendar,(4,7,1789,slash1),"Text comment")
                    dates.append( d)
            for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
                for slash1 in (False,True):
                    for slash2 in (False,True):
                        d = Date.Date()
                        d.set(quality,modifier,calendar,(4,7,1789,slash1,5,8,1876,slash2),"Text comment")
                        dates.append( d)
            modifier = Date.MOD_TEXTONLY
            d = Date.Date()
            d.set(quality,modifier,calendar,Date.EMPTY,"This is a textual date")
            dates.append( d)
        
        # test invalid dates
        dateval = (4,7,1789,False,5,8,1876,False)
        for l in range(1,len(dateval)):
            d = Date.Date()
            try:
                d.set(Date.QUAL_NONE,Date.MOD_NONE,Date.CAL_GREGORIAN,dateval[:l],"Text comment")
                dates.append( d)
            except Errors.DateError, e:
                d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
                dates.append( d)
            except:
                d = Date.Date()
                d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                dates.append( d)
        for l in range(1,len(dateval)):
            d = Date.Date()
            try:
                d.set(Date.QUAL_NONE,Date.MOD_SPAN,Date.CAL_GREGORIAN,dateval[:l],"Text comment")
                dates.append( d)
            except Errors.DateError, e:
                d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
                dates.append( d)
            except:
                d = Date.Date()
                d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                dates.append( d)
        d = Date.Date()
        d.set(Date.QUAL_NONE,Date.MOD_NONE,Date.CAL_GREGORIAN,(44,7,1789,False),"Text comment")
        dates.append( d)
        d = Date.Date()
        d.set(Date.QUAL_NONE,Date.MOD_NONE,Date.CAL_GREGORIAN,(4,77,1789,False),"Text comment")
        dates.append( d)
        d = Date.Date()
        d.set(Date.QUAL_NONE,Date.MOD_SPAN,Date.CAL_GREGORIAN,(4,7,1789,False,55,8,1876,False),"Text comment")
        dates.append( d)
        d = Date.Date()
        d.set(Date.QUAL_NONE,Date.MOD_SPAN,Date.CAL_GREGORIAN,(4,7,1789,False,5,88,1876,False),"Text comment")
        dates.append( d)
        
        # now add them as birth to new persons
        for dateval in dates:
            bevent = RelLib.Event()
            bevent.set_name("Birth")
            bevent.set_date_object(dateval)
            bevent_h = self.db.add_event(bevent,self.trans)
            # for the death event display the date as text and parse it back to a new date
            ndate = None
            try:
                datestr = _dd.display( dateval)
                try:
                    ndate = _dp.parse( datestr)
                    if not ndate:
                        ndate = Date.Date()
                        ndate.set_as_text("DateParser None")
                except:
                    ndate = Date.Date()
                    ndate.set_as_text("DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
            except:
                ndate = Date.Date()
                ndate.set_as_text("DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
            
            if dateval.get_modifier() != Date.MOD_TEXTONLY and ndate.get_modifier() == Date.MOD_TEXTONLY:
                # parser was unable to correctly parse the string
                ndate.set_as_text( "TEXTONLY: "+ndate.get_text())
                
            
            devent = RelLib.Event()
            devent.set_name("Death")
            devent.set_date_object(ndate)
            devent_h = self.db.add_event(devent,self.trans)
            person_h = self.generate_person(None, "DateTest")
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_handle(bevent_h)
            person.set_death_handle(devent_h)
            self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP
    
    def generate_person(self,gender=None,lastname=None,note=None):
        if not self.cli:
            self.progress.set_fraction(min(1.0,max(0.0, 1.0*self.person_count/self.options.handler.options_dict['person_count'])))
            if self.person_count % 10 == 0:
                while gtk.events_pending():
                    gtk.main_iteration()

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        np = RelLib.Person()
        
        self.add_defaults(np)
        
        # Note
        if note:
            np.set_note(note)
            
        # Gender
        if gender == None:
            gender = randint(0,1)
        np.set_gender(gender)
        
        # Name
        syllables1 = ["sa","li","na","ma","no","re","mi","cha","ki","du","ba","ku","el"]
        syllables2 = ["as","il","an","am","on","er","im","ach","ik","ud","ab","ul","le"]

        name = RelLib.Name()
        firstname = ""
        maxnames = 5
        maxsyllables = 5
        if not self.options.handler.options_dict['long_names']:
            maxnames = 2
            maxsyllables = 3
        for i in range(0,randint(1,maxnames)):
            for j in range(0,randint(2,maxsyllables)):
                firstname = firstname + choice(syllables2)
            if gender == RelLib.Person.FEMALE:
                firstname = firstname + choice(("a","e","i","o","u"))
            firstname = firstname + " "
        firstname = firstname.title().strip()
        if not lastname:
            lastname = ""
            for i in range(0,randint(2,maxsyllables)):
                lastname = lastname + choice(syllables1)
        n = randint(0,2)
        if n == 0:
            lastname = lastname.title()
        elif n == 1:
            lastname = lastname.upper()
        name.set_first_name(firstname)
        name.set_surname(lastname)
        name.add_source_reference(self.default_sourceref)
        name.set_note("Generated by TestcaseGenerator")
        np.set_primary_name(name)
        
        # generate some slightly different alternate name
        alt_name = RelLib.Name(name)
        firstname2 = firstname.replace("m", "n").replace("l", "i").replace("b", "d")
        if firstname2 != firstname:
            alt_name.set_first_name( firstname2)
            alt_name.set_title( "Testtitle")
            alt_name.set_patronymic( "Testpatronymic")
            alt_name.set_surname_prefix( "van")
            alt_name.set_suffix( "the second")
            alt_name.add_source_reference(self.default_sourceref)
            alt_name.set_note("Generated by TestcaseGenerator")
            np.add_alternate_name( alt_name)

        self.person_count = self.person_count+1

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        return( self.db.add_person(np,self.trans))
        
    def generate_family(self,person1_h):
        person1 = self.db.get_person_from_handle(person1_h)
        if person1.get_gender() == 1:
            person2_h = self.generate_person(0)
        else:
            person2_h = person1_h
            person1_h = self.generate_person(1)
        
        if randint(0,2) > 0:
            self.parents_todo.append(person1_h)
        if randint(0,2) > 0:
            self.parents_todo.append(person2_h)
            
        fam = RelLib.Family()
        self.add_defaults(fam)
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
        
        for i in range(0,randint(1,10)):
            child_h = self.generate_person(None, lastname)
            fam = self.db.get_family_from_handle(fam_h)
            fam.add_child_handle(child_h)
            self.db.commit_family(fam,self.trans)
            child = self.db.get_person_from_handle(child_h)
            child.add_parent_family_handle(fam_h,RelLib.Person.CHILD_REL_BIRTH,RelLib.Person.CHILD_REL_BIRTH)
            self.db.commit_person(child,self.trans)
            if randint(0,3) > 0:
                self.persons_todo.append(child_h)
        self.commit_transaction()   # COMMIT TRANSACTION STEP
                
    def generate_parents(self,child_h):
        child = self.db.get_person_from_handle(child_h)
        if child.get_parent_family_handle_list():
            return

        lastname = child.get_primary_name().get_surname()     

        person1_h = self.generate_person(1,lastname)
        person2_h = self.generate_person(0)

        if randint(0,2) > 1:
            self.parents_todo.append(person1_h)
        if randint(0,2) > 1:
            self.parents_todo.append(person2_h)
            
        fam = RelLib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship(RelLib.Family.MARRIED)
        fam.add_child_handle(child_h)
        fam_h = self.db.add_family(fam,self.trans)
        fam = self.db.commit_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        child.add_parent_family_handle(fam_h,RelLib.Person.CHILD_REL_BIRTH,RelLib.Person.CHILD_REL_BIRTH)
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

    def add_defaults(self,object,ref_text = ""):
        object.add_source_reference(self.default_sourceref)
        object.add_media_reference(self.default_mediaref)
        e = RelLib.Event()
        e.set_name("TestcaseGenerator")
        e.set_note("Generated by TestcaseGenerator")
        e.set_cause("Test cause")
        e.set_description("Test description")
        e.add_source_reference(self.default_sourceref)
        e.add_media_reference(self.default_mediaref)
        e.set_place_handle(self.default_place.get_handle())
        self.db.add_event(e, self.trans)
        object.add_event_handle(e.get_handle())
        object.add_attribute( self.default_attribute)
        try:
            object.add_url(self.default_url)
            object.add_address(self.default_address)
        except AttributeError:
            pass    # family does not have an url
        object.set_note("Generated by TestcaseGenerator")
        
    def commit_transaction(self):
        if self.options.handler.options_dict['no_trans']:
            self.db.transaction_commit(self.trans,_("Testcase generator step %d") % self.transaction_count)
            self.transaction_count += 1
            self.trans = self.db.transaction_begin()


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TestcaseGeneratorOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'bugs'          : 0,
            'dates'         : 1,
            'persons'       : 1,
            'person_count'  : 2000,
            'no_trans'      : 0,
            'long_names'    : 0,
        }
        self.options_help = {
            'bugs'          : ("=0/1",
                                "Whether to create invalid database references.",
                                ["Skip test","Create invalid Database references"],
                                True),
            'dates'         : ("=0/1",
                                "Whether to create test for date handling.",
                                ["Skip test","Create date tests"],
                                True),
            'persons'       : ("=0/1",
                                "Whether to create a bunch of dummy persons",
                                ["Dont create persons","Create dummy persons"],
                                True),
            'person_count'  : ("=int",
                                "Number of dummy persons to generate",
                                "Number of persons"),
            'no_trans'      : ("=0/1",
                                "Wheter to use one transaction or multiple small ones",
                                ["One transaction","Multiple transactions"],
                                True),
            'long_names'    : ("=0/1",
                                "Wheter to create short or long names",
                                ["Short names","Long names"],
                                True),
        }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    name = 'testcasegenerator',
    category = Tool.TOOL_DEBUG,
    tool_class = TestcaseGenerator,
    options_class = TestcaseGeneratorOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Generate Testcases for persons and families"),
    status = _("Beta"),
    author_name = "Martin Hawlisch",
    author_email = "martin@hawlisch.de",
    description = _("The testcase generator will generate some persons and families"
                    " that have broken links in the database or data that is in conflict to a relation.")
    )
