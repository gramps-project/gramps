# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
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
import RelLib
from PluginUtils import Tool, register_tool
import const
import Utils
import LdsUtils
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp
from DateHandler import displayer as _dd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class TestcaseGenerator(Tool.Tool):
    NUMERIC = 0
    FIRSTNAME = 1
    FIRSTNAME_FEMALE = 2
    FIRSTNAME_MALE = 3
    LASTNAME = 4
    NOTE = 5
    SHORT = 6
    LONG = 7

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        if dbstate.db.readonly:
            return

        Tool.Tool.__init__(self, dbstate, options_class, name)

        self.person_count = 0
        self.persons_todo = []
        self.parents_todo = []
        self.person_dates = {}
        self.generated_repos = []
        self.generated_sources = []
        self.generated_media = []
        self.generated_places = []
        self.generated_events = []
        self.generated_families = []
        self.text_serial_number = 1
        
        # If an active persons exists the generated tree is connected to that person
        if self.person:
            # try to get birth and death year
            try:
                bh = self.person.get_birth_handle()
                b = self.db.get_event_from_handle( bh)
                do = b.get_date_object()
                birth = do.get_year()
            except AttributeError:
                birth = None
            try:
                dh = self.person.get_death_handle()
                b = self.db.get_event_from_handle( dh)
                do = b.get_date_object()
                death = do.get_year()
            except AttributeError:
                death = None
            if not birth and not death:
                birth = randint(1700,1900)
            if birth and not death:
                death = birth + randint(20,90)
            if death and not birth:
                birth = death - randint(20,90)
            self.person_dates[self.person.get_handle()] = (birth,death)
            
            self.persons_todo.append(self.person.get_handle())
            self.parents_todo.append(self.person.get_handle())

        if uistate:
            self.init_gui(uistate)
        else:
            self.run_tool(cli=True)

    def init_gui(self,uistate):
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

        self.check_specialchars = gtk.CheckButton( _("Add special characters"))
        self.check_specialchars.set_active( self.options.handler.options_dict['specialchars'])
        self.top.vbox.pack_start(self.check_specialchars,0,0,5)

        self.check_serial = gtk.CheckButton( _("Add serial number"))
        self.check_serial.set_active( self.options.handler.options_dict['add_serial'])
        self.top.vbox.pack_start(self.check_serial,0,0,5)

        self.check_linebreak = gtk.CheckButton( _("Add line break"))
        self.check_linebreak.set_active( self.options.handler.options_dict['add_linebreak'])
        self.top.vbox.pack_start(self.check_linebreak,0,0,5)

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
        self.options.handler.options_dict['specialchars']  = int(
            self.check_specialchars.get_active())
        self.options.handler.options_dict['add_serial']  = int(
            self.check_serial.get_active())
        self.options.handler.options_dict['add_linebreak']  = int(
            self.check_linebreak.get_active())
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
        
        if not self.options.handler.options_dict['no_trans']:
            batch = False
            self.db.disable_signals()
        else:
            batch = False
        self.trans = self.db.transaction_begin("")

        if False and self.options.handler.options_dict['no_trans']:
    
            print "TESTING SIGNALS..."
    
            print "\nCREATE PERSON"
            p = RelLib.Person()
            h = self.db.add_person( p, self.trans)
            print "\nUPDATE PERSON"
            self.db.commit_person( p, self.trans)
            print "\nDELETE PERSON"
            self.db.remove_person( h, self.trans)
    
            print "\nCREATE FAMILY"
            f = RelLib.Family()
            h = self.db.add_family( f, self.trans)
            print "\nUPDATE FAMILY"
            self.db.commit_family( f, self.trans)
            print "\nDELETE FAMILY"
            self.db.remove_family( h, self.trans)
    
            print "\nCREATE EVENT"
            e = RelLib.Event()
            h = self.db.add_event( e, self.trans)
            print "\nUPDATE EVENT"
            self.db.commit_event( e, self.trans)
            print "\nDELETE EVENT"
            self.db.remove_event( h, self.trans)
    
            print "\nCREATE PLACE"
            p = RelLib.Place()
            h = self.db.add_place( p, self.trans)
            print "\nUPDATE PLACE"
            self.db.commit_place( p, self.trans)
            print "\nDELETE PLACE"
            self.db.remove_place( h, self.trans)
    
            print "\nCREATE SOURCE"
            s = RelLib.Source()
            h = self.db.add_source( s, self.trans)
            print "\nUPDATE SOURCE"
            self.db.commit_source( s, self.trans)
            print "\nDELETE SOURCE"
            self.db.remove_source( h, self.trans)
    
            print "\nCREATE MEDIA"
            m = RelLib.MediaObject()
            h = self.db.add_object( m, self.trans)
            print "\nUPDATE MEDIA"
            self.db.commit_media_object( m, self.trans)
            print "\nDELETE MEDIA"
            self.db.remove_object( h, self.trans)
    
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
        
        
       # if self.options.handler.options_dict['bugs']\
       #     or self.options.handler.options_dict['dates']\
       #     or self.options.handler.options_dict['persons']:
       #     # bootstrap random source and media
       #     self.rand_source()
       #     self.rand_media()
            

        if self.options.handler.options_dict['bugs']:
            self.generate_broken_relations()
        
        if self.options.handler.options_dict['dates']:
            self.generate_date_tests()

        if self.options.handler.options_dict['persons']:
            while True:
                if not self.persons_todo:
                    ph = self.generate_person(0)
                    self.persons_todo.append( ph)
                    self.parents_todo.append( ph)
                person_h = self.persons_todo.pop(0)
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
        child_ref = RelLib.ChildRef()
        child_ref.set_reference_handle(child_h)
        self.fill_object(child_ref)
        fam.add_child_ref(child_ref)
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
        fam.set_relationship((RelLib.FamilyRelType.MARRIED,''))
        #fam.add_child_handle(child_h)
        child_ref = RelLib.ChildRef()
        child_ref.set_reference_handle(child_h)
        self.fill_object(child_ref)
        fam.add_child_ref(child_ref)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        child = self.db.get_person_from_handle(child_h)
        child.add_parent_family_handle(fam_h)
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing birth event handle set
        person_h = self.generate_person(None,"Broken11",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle4")
        person.set_birth_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing death event handle set
        person_h = self.generate_person(None,"Broken12",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle5")
        person.set_death_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing event handle set
        person_h = self.generate_person(None,"Broken13",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle6")
        person.add_event_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a birth event having an empty type
        person_h = self.generate_person(None,"Broken14",None)
        event = RelLib.Event()
        event.set_type('')
        event.set_description("Test for Broken14")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        person = self.db.get_person_from_handle(person_h)
        person.set_birth_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a death event having an empty type
        person_h = self.generate_person(None,"Broken15",None)
        event = RelLib.Event()
        event.set_description("Test for Broken15")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        person = self.db.get_person_from_handle(person_h)
        person.set_death_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with an event having an empty type
        person_h = self.generate_person(None,"Broken16",None)
        event = RelLib.Event()
        event.set_description("Test for Broken16")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a birth event pointing to nonexisting place
        person_h = self.generate_person(None,"Broken17",None)
        event = RelLib.Event()
        event.set_type(RelLib.EventType.BIRTH)
        event.set_place_handle("InvalidHandle7")
        event.set_description("Test for Broken17")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        person = self.db.get_person_from_handle(person_h)
        person.set_birth_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with an event pointing to nonexisting place
        person_h = self.generate_person(None,"Broken18",None)
        event = RelLib.Event()
        event.set_type(RelLib.EventType.BIRTH)
        event.set_place_handle("InvalidHandle8")
        event.set_description("Test for Broken18")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        person = self.db.get_person_from_handle(person_h)
        person.add_event_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP


    def generate_date_tests(self):
        dates = []
        # first some valid dates
        calendar = RelLib.Date.CAL_GREGORIAN
        for quality in (RelLib.Date.QUAL_NONE, RelLib.Date.QUAL_ESTIMATED,
                        RelLib.Date.QUAL_CALCULATED):
            for modifier in (RelLib.Date.MOD_NONE, RelLib.Date.MOD_BEFORE,
                             RelLib.Date.MOD_AFTER, RelLib.Date.MOD_ABOUT):
                for slash1 in (False,True):
                    d = RelLib.Date()
                    d.set(quality,modifier,calendar,(4,7,1789,slash1),"Text comment")
                    dates.append( d)
            for modifier in (RelLib.Date.MOD_RANGE, RelLib.Date.MOD_SPAN):
                for slash1 in (False,True):
                    for slash2 in (False,True):
                        d = RelLib.Date()
                        d.set(quality,modifier,calendar,(4,7,1789,slash1,5,8,1876,slash2),"Text comment")
                        dates.append( d)
            modifier = RelLib.Date.MOD_TEXTONLY
            d = RelLib.Date()
            d.set(quality,modifier,calendar,RelLib.Date.EMPTY,
                  "This is a textual date")
            dates.append( d)
        
        # test invalid dates
        dateval = (4,7,1789,False,5,8,1876,False)
        for l in range(1,len(dateval)):
            d = RelLib.Date()
            try:
                d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_NONE,
                      RelLib.Date.CAL_GREGORIAN,dateval[:l],"Text comment")
                dates.append( d)
            except Errors.DateError, e:
                d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
                dates.append( d)
            except:
                d = RelLib.Date()
                d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                dates.append( d)
        for l in range(1,len(dateval)):
            d = RelLib.Date()
            try:
                d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_SPAN,RelLib.Date.CAL_GREGORIAN,dateval[:l],"Text comment")
                dates.append( d)
            except Errors.DateError, e:
                d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
                dates.append( d)
            except:
                d = RelLib.Date()
                d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                dates.append( d)
        d = RelLib.Date()
        d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_NONE,
              RelLib.Date.CAL_GREGORIAN,(44,7,1789,False),"Text comment")
        dates.append( d)
        d = RelLib.Date()
        d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_NONE,
              RelLib.Date.CAL_GREGORIAN,(4,77,1789,False),"Text comment")
        dates.append( d)
        d = RelLib.Date()
        d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_SPAN,
              RelLib.Date.CAL_GREGORIAN,
              (4,7,1789,False,55,8,1876,False),"Text comment")
        dates.append( d)
        d = RelLib.Date()
        d.set(RelLib.Date.QUAL_NONE,RelLib.Date.MOD_SPAN,
              RelLib.Date.CAL_GREGORIAN,
              (4,7,1789,False,5,88,1876,False),"Text comment")
        dates.append( d)
        
        # now add them as birth to new persons
        i = 1
        for dateval in dates:
            person = RelLib.Person()
            name = RelLib.Name()
            name.set_surname("DateTest")
            name.set_first_name("Test %d" % i)
            person.set_primary_name( name)
            self.db.add_person(person,self.trans)
            bevent = RelLib.Event()
            bevent.set_type(RelLib.EventType.BIRTH)
            bevent.set_date_object(dateval)
            bevent_h = self.db.add_event(bevent,self.trans)
            self.generated_events.append(bevent_h)
            bevent_ref = RelLib.EventRef()
            bevent_ref.set_reference_handle(bevent_h)
            # for the death event display the date as text and parse it back to a new date
            ndate = None
            try:
                datestr = _dd.display( dateval)
                try:
                    ndate = _dp.parse( datestr)
                    if not ndate:
                        ndate = RelLib.Date()
                        ndate.set_as_text("DateParser None")
                        person.set_marker(RelLib.MarkerType.TODO_TYPE)
                    else:
                        person.set_marker(RelLib.MarkerType.COMPLETE)
                except:
                    ndate = RelLib.Date()
                    ndate.set_as_text("DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                    person.set_marker(RelLib.MarkerType.TODO_TYPE)
            except:
                ndate = RelLib.Date()
                ndate.set_as_text("DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                person.set_marker(RelLib.MarkerType.TODO_TYPE)
            
            if dateval.get_modifier() != RelLib.Date.MOD_TEXTONLY \
                   and ndate.get_modifier() == RelLib.Date.MOD_TEXTONLY:
                # parser was unable to correctly parse the string
                ndate.set_as_text( "TEXTONLY: "+ndate.get_text())
                person.set_marker(RelLib.MarkerType.TODO_TYPE)
            if dateval.get_modifier() == RelLib.Date.MOD_TEXTONLY \
                    and dateval.get_text().count("Traceback") \
                    and person.get_marker() == RelLib.MarkerType.COMPLETE:
                person.set_marker(RelLib.MarkerType.TODO_TYPE)
            
            devent = RelLib.Event()
            devent.set_type(RelLib.EventType.DEATH)
            devent.set_date_object(ndate)
            devent_h = self.db.add_event(devent,self.trans)
            self.generated_events.append(devent_h)
            devent_ref = RelLib.EventRef()
            devent_ref.set_reference_handle(devent_h)
            person.set_birth_ref(bevent_ref)
            person.set_death_ref(devent_ref)
            self.db.commit_person(person,self.trans)
            i = i + 1
        self.commit_transaction()   # COMMIT TRANSACTION STEP
    
    def generate_person(self,gender=None,lastname=None,note=None, alive_in_year=None):
        if not self.cli:
            self.progress.set_fraction(min(1.0,max(0.0, 1.0*self.person_count/self.options.handler.options_dict['person_count'])))
            if self.person_count % 10 == 0:
                while gtk.events_pending():
                    gtk.main_iteration()

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        np = RelLib.Person()
        self.fill_object(np)
        
        # Gender
        if gender == None:
            gender = randint(0,1)
        if randint(0,10) == 1:  # Set some persons to unknown gender
            np.set_gender(RelLib.Person.UNKNOWN)
        else:
            np.set_gender(gender)
        
        # Name
        name = RelLib.Name()
        self.fill_object( name)
        (firstname,lastname) = self.rand_name(lastname, gender)
        name.set_first_name(firstname)
        name.set_surname(lastname)
        if randint(0,1) == 1:
            name.set_title( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            name.set_patronymic( self.rand_text(self.FIRSTNAME_MALE))
        if randint(0,1) == 1:
            name.set_surname_prefix( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            name.set_suffix( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            name.set_call_name( self.rand_text(self.FIRSTNAME))
        np.set_primary_name(name)
        
        # generate some slightly different alternate name
        firstname2 = firstname.replace("m", "n").replace("l", "i").replace("b", "d")
        if firstname2 != firstname:
            alt_name = RelLib.Name(name)
            self.fill_object( alt_name)
            if randint(0,2) == 1:
                alt_name.set_surname(self.rand_text(self.LASTNAME))
            elif randint(0,2) == 1:
                alt_name.set_surname(lastname)
            if randint(0,1) == 1:
                alt_name.set_first_name( firstname2)
            if randint(0,1) == 1:
                alt_name.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_patronymic( self.rand_text(self.FIRSTNAME_MALE))
            if randint(0,1) == 1:
                alt_name.set_surname_prefix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_suffix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_call_name( self.rand_text(self.FIRSTNAME))
            np.add_alternate_name( alt_name)
        firstname2 = firstname.replace("a", "e").replace("o", "u").replace("r", "p")
        if firstname2 != firstname:
            alt_name = RelLib.Name(name)
            self.fill_object( alt_name)
            if randint(0,2) == 1:
                alt_name.set_surname(self.rand_text(self.LASTNAME))
            elif randint(0,2) == 1:
                alt_name.set_surname(lastname)
            if randint(0,1) == 1:
                alt_name.set_first_name( firstname2)
            if randint(0,1) == 1:
                alt_name.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_patronymic( self.rand_text(self.FIRSTNAME_MALE))
            if randint(0,1) == 1:
                alt_name.set_surname_prefix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_suffix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_call_name( self.rand_text(self.FIRSTNAME))
            np.add_alternate_name( alt_name)

        if not alive_in_year:
            alive_in_year = randint(1700,2000)

        by = alive_in_year - randint(0,60)
        dy = alive_in_year + randint(0,60)
        
        # birth
        if randint(0,1) == 1:
            (birth_year, eref) = self.rand_personal_event( RelLib.EventType.BIRTH, by,by)
            np.set_birth_ref(eref)

        # baptism
        if randint(0,1) == 1:
            (bapt_year, eref) = self.rand_personal_event(
                choice( (RelLib.EventType.BAPTISM, RelLib.EventType.CHRISTEN)), by, by+2)
            np.add_event_ref(eref)

        # death
        death_year = None
        if randint(0,1) == 1:
            (death_year, eref) = self.rand_personal_event( RelLib.EventType.DEATH, dy,dy)
            np.set_death_ref(eref)

        # burial
        if randint(0,1) == 1:
            (bur_year, eref) = self.rand_personal_event(
                choice( (RelLib.EventType.BURIAL, RelLib.EventType.CREMATION)), dy, dy+2)
            np.add_event_ref(eref)
        
        # some other events
        while randint(0,5) == 1:
            (birth_year, eref) = self.rand_personal_event( None, by,dy)
            np.set_birth_ref(eref)

        # some shared events
        if self.generated_events:
            while randint(0,5) == 1:
                e_h = choice(self.generated_events)
                eref = RelLib.EventRef()
                self.fill_object( eref)
                eref.set_reference_handle(e_h)
                eref.set_role( self.rand_type(RelLib.EventRoleType()))
                np.add_event_ref(eref)
        
        # PersonRef
        if randint(0,3) == 1:
            for i in range(0,randint(1,2)):
                if self.person_count > self.options.handler.options_dict['person_count']:
                    break
                if alive_in_year:
                    asso_h = self.generate_person(None, None, alive_in_year = alive_in_year)
                else:
                    asso_h = self.generate_person()
                asso = RelLib.PersonRef()
                asso.set_reference_handle(asso_h)
                asso.set_relation(self.rand_text(self.SHORT))
                self.fill_object(asso)
                np.add_person_ref(asso)
                if randint(0,2) == 0:
                    self.persons_todo.append(asso_h)
        
        person_handle = self.db.add_person(np,self.trans)
        
        self.person_count = self.person_count+1
        self.person_dates[person_handle] = (by,dy)

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        return( person_handle)
        
    def generate_family(self,person1_h):
        person1 = self.db.get_person_from_handle(person1_h)
        if not person1:
            return
        alive_in_year = None
        if person1_h in self.person_dates:
            (born, died) = self.person_dates[person1_h]
            alive_in_year = min( born+randint(10,50), died + randint(-10,10))
            
        if person1.get_gender() == 1:
            if randint(0,7)==1:
                person2_h = None
            else:
                if alive_in_year:
                    person2_h = self.generate_person(0, alive_in_year = alive_in_year)
                else:
                    person2_h = self.generate_person(0)
        else:
            person2_h = person1_h
            if randint(0,7)==1:
                person1_h = None
            else:
                if alive_in_year:
                    person1_h = self.generate_person(1, alive_in_year = alive_in_year)
                else:
                    person1_h = self.generate_person(1)
        
        if person1_h and randint(0,2) > 0:
            self.parents_todo.append(person1_h)
        if person2_h and randint(0,2) > 0:
            self.parents_todo.append(person2_h)
            
        fam = RelLib.Family()
        self.add_defaults(fam)
        if person1_h:
            fam.set_father_handle(person1_h)
        if person2_h:
            fam.set_mother_handle(person2_h)
        fam_h = self.db.add_family(fam,self.trans)
        self.generated_families.append(fam_h)
        fam = self.db.commit_family(fam,self.trans)
        if person1_h:
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
        if person2_h:
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        lastname = person1.get_primary_name().get_surname()     
        
        for i in range(0,randint(1,10)):
            if self.person_count > self.options.handler.options_dict['person_count']:
                break
            if alive_in_year:
                child_h = self.generate_person(None, lastname, alive_in_year = alive_in_year + randint( 16+2*i, 30 + 2*i))
            else:
                child_h = self.generate_person(None, lastname)
                (born,died) = self.person_dates[child_h]
                alive_in_year = born
            fam = self.db.get_family_from_handle(fam_h)
            child_ref = RelLib.ChildRef()
            child_ref.set_reference_handle(child_h)
            self.fill_object(child_ref)
            fam.add_child_ref(child_ref)
            self.db.commit_family(fam,self.trans)
            child = self.db.get_person_from_handle(child_h)
            child.add_parent_family_handle(fam_h)
            self.db.commit_person(child,self.trans)
            if randint(0,3) > 0:
                self.persons_todo.append(child_h)
        self.commit_transaction()   # COMMIT TRANSACTION STEP
                
    def generate_parents(self,child_h):
        if not child_h:
            return
        child = self.db.get_person_from_handle(child_h)
        if not child:
            print "ERROR: Person handle %s does not exist in database" % child_h
            return
        if child.get_parent_family_handle_list():
            return

        lastname = child.get_primary_name().get_surname()
        if child_h in self.person_dates:
            (born,died) = self.person_dates[child_h]
            person1_h = self.generate_person(1,lastname, alive_in_year=born)
            person2_h = self.generate_person(0, alive_in_year=born)
        else:
            person1_h = self.generate_person(1,lastname)
            person2_h = self.generate_person(0)

        if randint(0,2) > 1:
            self.parents_todo.append(person1_h)
        if randint(0,2) > 1:
            self.parents_todo.append(person2_h)
            
        fam = RelLib.Family()
        self.add_defaults(fam)
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        child_ref = RelLib.ChildRef()
        child_ref.set_reference_handle(child_h)
        self.fill_object(child_ref)
        fam.add_child_ref(child_ref)
        fam_h = self.db.add_family(fam,self.trans)
        self.generated_families.append(fam_h)
        fam = self.db.commit_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        child.add_parent_family_handle(fam_h)
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

    def add_defaults(self,object):
        self.fill_object( object)
    
    def rand_name( self, lastname=None, gender=None):
        if gender == RelLib.Person.MALE:
            firstname = self.rand_text( self.FIRSTNAME_MALE)
        elif gender == RelLib.Person.FEMALE:
            firstname = self.rand_text( self.FIRSTNAME_FEMALE)
        else:
            firstname = self.rand_text( self.FIRSTNAME)
        if not lastname:
            lastname = self.rand_text( self.LASTNAME)
        return (firstname,lastname)
    
    def rand_date( self, start=None, end=None):
        """
        Generates a random date object between the given years start and end
        """
        if not start and not end:
            start = randint(1700,2000)
        if start and not end:
            end = start + randint(0,100)
        if end and not start:
            start = end - randint(0,100)
        year = randint(start,end)
        
        ndate = RelLib.Date()
        if randint(0,10) == 1:
            # Some get a textual date
            ndate.set_as_text( choice((self.rand_text(self.SHORT),"Unknown","??","Don't know","TODO!")))
        else:
            if randint(0,10) == 1:
                # some get an empty date
                pass
            else:
                # regular dates
                calendar = RelLib.Date.CAL_GREGORIAN
                quality = choice( (RelLib.Date.QUAL_NONE,
                                   RelLib.Date.QUAL_ESTIMATED,
                                   RelLib.Date.QUAL_CALCULATED))
                modifier = choice( (RelLib.Date.MOD_NONE,
                                    RelLib.Date.MOD_BEFORE,
                                    RelLib.Date.MOD_AFTER,\
                                    RelLib.Date.MOD_ABOUT,
                                    RelLib.Date.MOD_RANGE,
                                    RelLib.Date.MOD_SPAN))
                day = randint(0,28)
                if day > 0: # avoid days without month
                    month = randint(1,12)
                else:
                    month = randint(0,12)
                
                if modifier in (RelLib.Date.MOD_RANGE, RelLib.Date.MOD_SPAN):
                    day2 = randint(0,28)
                    if day2 > 0:
                        month2 = randint(1,12)
                    else:
                        month2 = randint(0,12)
                    year2 = year + randint(1,5)
                    ndate.set(quality,modifier,calendar,(day,month,year,False,day2,month2,year2,False),"")
                else:
                    ndate.set(quality,modifier,calendar,(day,month,year,False),"")
        
        return (year, ndate)
    
    def fill_object( self, o):
    
        if isinstance(o,RelLib.Address):
            if randint(0,1) == 1:
                o.set_street( self.rand_text(self.SHORT))

        if issubclass(o.__class__,RelLib._AddressBase.AddressBase):
            while randint(0,1) == 1:
                a = RelLib.Address()
                self.fill_object(a)
                o.add_address( a)

        if isinstance(o,RelLib.Attribute):
            o.set_type( self.rand_type(RelLib.AttributeType()))
            o.set_value( self.rand_text(self.SHORT))

        if issubclass(o.__class__,RelLib._AttributeBase.AttributeBase):
            while randint(0,1) == 1:
                a = RelLib.Attribute()
                self.fill_object(a)
                o.add_attribute( a)

        if isinstance(o,RelLib.ChildRef):
            if randint(0,3) == 1:
                o.set_mother_relation( self.rand_type( RelLib.ChildRefType()))
            if randint(0,3) == 1:
                o.set_father_relation( self.rand_type( RelLib.ChildRefType()))

        if issubclass(o.__class__,RelLib._DateBase.DateBase):
            if randint(0,1) == 1:
                (y,d) = self.rand_date()
                o.set_date_object( d)

        if isinstance(o,RelLib.Family):
            if randint(0,2) == 1:
                o.set_relationship( self.rand_type(RelLib.FamilyRelType()))
            else:
                o.set_relationship(RelLib.FamilyRelType(RelLib.FamilyRelType.MARRIED))

        if isinstance(o,RelLib.LdsOrd):
            if randint(0,1) == 1:
                o.set_temple( choice( LdsUtils.temple_to_abrev.keys()))

        if issubclass(o.__class__,RelLib._LdsOrdBase.LdsOrdBase):
            while randint(0,1) == 1:
                ldsord = RelLib.LdsOrd()
                self.fill_object( ldsord)
                # TODO: adapt type and status to family/person
                #if isinstance(o,RelLib.Person):
                #if isinstance(o,RelLib.Family):
                ldsord.set_type( choice(
                    [item[0] for item in RelLib.LdsOrd._TYPE_MAP] ))
                ldsord.set_status( randint(0,len(RelLib.LdsOrd._STATUS_MAP)-1))
                if self.generated_families:
                    ldsord.set_family_handle( choice(self.generated_families))
                o.add_lds_ord( ldsord)

        if isinstance(o,RelLib.Location):
            if randint(0,1) == 1:
                o.set_parish( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_county( self.rand_text(self.SHORT))

        if issubclass(o.__class__,RelLib._LocationBase.LocationBase):
            if randint(0,1) == 1:
                o.set_phone( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_city( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_state( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_country( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_postal_code( self.rand_text(self.SHORT))

        if issubclass(o.__class__,RelLib._MediaBase.MediaBase):
            while randint(0,1) == 1:
                o.add_media_reference( self.fill_object( RelLib.MediaRef()))

        if isinstance(o,RelLib.MediaObject):
            if randint(0,3) == 1:
                o.set_description( self.rand_text(self.LONG))
            else:
                o.set_description( self.rand_text(self.SHORT))
                o.set_path("/tmp/TestcaseGenerator.png")
                o.set_mime_type("image/png")

        if isinstance(o,RelLib.MediaRef):
            if not self.generated_media or randint(0,10) == 1:
                m = RelLib.MediaObject()
                self.fill_object(m)
                self.db.add_object( m, self.trans)
                self.generated_media.append( m.get_handle())
            o.set_reference_handle( choice( self.generated_media))
            if randint(0,1) == 1:
                o.set_rectangle( (randint(0,200),randint(0,200),randint(0,200),randint(0,200)))
        
        if isinstance(o,RelLib.Name):
            o.set_type( self.rand_type( RelLib.NameType()))

        if issubclass(o.__class__,RelLib._NoteBase.NoteBase):
            o.set_note( self.rand_text(self.NOTE))
            o.set_note_format( choice( (True,False)))
        
        if isinstance(o,RelLib.Place):
            o.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_longitude( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_latitude( self.rand_text(self.SHORT))
            o.set_main_location( self.fill_object( RelLib.Location()))
            while randint(0,1) == 1:
                o.add_alternate_locations( self.fill_object( RelLib.Location()))

        if issubclass(o.__class__,RelLib._PrivacyBase.PrivacyBase):
            o.set_privacy( randint(0,5) == 1)
            
        if issubclass(o.__class__,RelLib.PrimaryObject):
            o.set_marker( self.rand_type(RelLib.MarkerType()))

        if isinstance(o,RelLib.RepoRef):
            if not self.generated_repos or randint(0,10) == 1:
                r = RelLib.Repository()
                self.fill_object(r)
                self.db.add_repository( r, self.trans)
                self.generated_repos.append(r.get_handle())
            o.set_reference_handle( choice( self.generated_repos))
            if randint(0,1) == 1:
                o.set_call_number( self.rand_text(self.SHORT))
            o.set_media_type( self.rand_type(RelLib.SourceMediaType()))

        if isinstance(o,RelLib.Repository):
            o.set_type( self.rand_type(RelLib.RepositoryType()))
            o.set_name( self.rand_text(self.SHORT))

        if isinstance(o,RelLib.Source):
            o.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_author( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_publication_info( self.rand_text(self.LONG))
            if randint(0,1) == 1:
                o.set_abbreviation( self.rand_text(self.SHORT))
            while randint(0,1) == 1:
                o.set_data_item( self.rand_text(self.SHORT), self.rand_text(self.SHORT))
            while randint(0,1) == 1:
                r = RelLib.RepoRef()
                self.fill_object(r)
                o.add_repo_reference( r)

        if issubclass(o.__class__,RelLib._SourceBase.SourceBase):
            while randint(0,1) == 1:
                s = RelLib.SourceRef()
                self.fill_object(s)
                o.add_source_reference( s)

        if isinstance(o,RelLib.SourceRef):
            if not self.generated_sources or randint(0,10) == 1:
                s = RelLib.Source()
                self.fill_object(s)
                self.db.add_source( s, self.trans)
                self.generated_sources.append( s.get_handle())
            o.set_reference_handle( choice( self.generated_sources))
            if randint(0,1) == 1:
                o.set_page( self.rand_text(self.NUMERIC))
            if randint(0,1) == 1:
                o.set_text( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                (year, d) = self.rand_date( )
                o.set_date_object( d)
            o.set_confidence_level(choice(Utils.confidence.keys()))

        if issubclass(o.__class__,RelLib._UrlBase.UrlBase):
            while randint(0,1) == 1:
                u = RelLib.Url()
                self.fill_object(u)
                o.add_url(u)
        
        if isinstance(o,RelLib.Url):
            o.set_path("http://www.gramps-project.org/?test=%s" % self.rand_text(self.SHORT))
            o.set_description( self.rand_text(self.SHORT))
            o.set_type( self.rand_type(RelLib.UrlType()))

        return o

    def rand_personal_event( self, type=None, start=None, end=None):
        if type:
            typeval = RelLib.EventType(type)
        else:
            typeval = self.rand_type(RelLib.EventType())
        return self._rand_event( typeval, start, end)
        
    def rand_family_event( self, type=None, start=None, end=None):
        if type:
            typeval = RelLib.EventType(type)
        else:
            typeval = self.rand_type(RelLib.EventType())
        return self._rand_event( typeval, start, end)
    
    def _rand_event( self, type, start, end):
        e = RelLib.Event()
        self.fill_object(e)
        e.set_type( type)
        #if randint(0,1) == 1:
        #    e.set_cause( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            e.set_description( self.rand_text(self.LONG))
        if randint(0,1) == 1:
            e.set_place_handle( self.rand_place())
        (year, d) = self.rand_date( start, end)
        e.set_date_object( d)
        event_h = self.db.add_event(e, self.trans)
        self.generated_events.append(event_h)
        event_ref = RelLib.EventRef()
        self.fill_object(event_ref)
        event_ref.set_reference_handle(event_h)
        return (year, event_ref)
    
    def rand_type( self, list):
        if issubclass( list.__class__, RelLib.GrampsType):
            map = list.get_map()
            key = choice( map.keys())
            if key == list.get_custom():
                value = self.rand_text(self.SHORT)
            else:
                value = ''
            list.set( (key,value))
            return list
        
    def rand_place( self):
        if not self.generated_places or randint(0,10) == 1:
            place = RelLib.Place()
            self.fill_object( place)
            self.db.add_place( place, self.trans)
            self.generated_places.append( place.get_handle())
        return choice( self.generated_places)
        
    def rand_text(self, type=None):
        # for lastnamesnames
        syllables1 = ["sa","li","na","ma","no","re","mi","cha","ki","du","ba","ku","el"]
        # for firstnames
        syllables2 = ["as","il","an","am","on","er","im","ach","ik","ud","ab","ul","le"]
        # others
        syllables3 = ["ka", "po", "lo", "chi", "she", "di", "fa", "go", "ja", "ne", "pe"]

        syllables = syllables1 + syllables2 +syllables3
        minwords = 5
        maxwords = 8
        minsyllables = 2
        maxsyllables = 5

        result = ""
        if self.options.handler.options_dict['specialchars']:
            result = result + u"ä<ö&ü%ß'\""
        if self.options.handler.options_dict['add_serial']:
            result = result + "#+#%06d#-#" % self.text_serial_number
            self.text_serial_number = self.text_serial_number + 1
        
        if not type:
            type = self.SHORT
            
        if type == self.SHORT:
            minwords = 1
            maxwords = 3
            minsyllables = 2
            maxsyllables = 4
        
        if type == self.LONG:
            minwords = 5
            maxwords = 8
            minsyllables = 2
            maxsyllables = 5

        if type == self.FIRSTNAME:
            type = choice( (self.FIRSTNAME_MALE,self.FIRSTNAME_FEMALE))

        if type == self.FIRSTNAME_MALE or type == self.FIRSTNAME_FEMALE:
            syllables = syllables2
            minwords = 1
            maxwords = 5
            minsyllables = 2
            maxsyllables = 5
            if not self.options.handler.options_dict['long_names']:
                maxwords = 2
                maxsyllables = 3

        if type == self.LASTNAME:
            syllables = syllables1
            minwords = 1
            maxwords = 1
            minsyllables = 2
            maxsyllables = 5
            if not self.options.handler.options_dict['long_names']:
                maxsyllables = 3

        if type == self.NOTE:
            result = result + "Generated by TestcaseGenerator."
            minwords = 20
            maxwords = 100

        if type == self.NUMERIC:
            if randint(0,1) == 1:
                return "%d %s" % (randint(1,100), result)
            if randint(0,1) == 1:
                return "%d, %d %s" % (randint(1,100), randint(100,1000), result)
            m = randint(100,1000)
            return "%d - %d %s" % (m, m+randint(1,5), result)

        for i in range(0,randint(minwords,maxwords)):
            if result:
                result = result + " "
            word = ""
            for j in range(0,randint(minsyllables,maxsyllables)):
                word = word + choice(syllables)
            if type == self.FIRSTNAME_MALE:
                word = word + choice(("a","e","i","o","u"))
            elif type == self.NOTE:
                if randint(0,20) == 1:
                    word = word + "."
                elif randint(0,30) == 1:
                    word = word + ".\n"
            if randint(0,3) == 1:
                word = word.title()
            result = result + word
        
        if type == self.LASTNAME:
            n = randint(0,2)
            if n == 0:
                result = result.title()
            elif n == 1:
                result = result.upper()

        if self.options.handler.options_dict['add_linebreak']:
            result = result + u"\nNEWLINE"

        return result
    
    def commit_transaction(self):
        #if self.options.handler.options_dict['no_trans']:
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
            'specialchars'  : 0,
            'add_serial'    : 0,
            'add_linebreak' : 0,
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
            'specialchars'    : ("=0/1",
                                "Wheter to ass some special characters to every text field",
                                ["No special characters","Add special characters"],
                                True),
            'add_serial'    : ("=0/1",
                                "Wheter to add a serial number to every text field",
                                ["No serial","Add serial number"],
                                True),
            'add_linebreak' : ("=0/1",
                                "Wheter to add a line break to every text field",
                                ["No linebreak","Add line break"],
                                True),
        }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

if __debug__:
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
        description = _("The testcase generator will generate some persons "
                        "and families that have broken links in the database "
                        "or data that is in conflict to a relation.")
        )
