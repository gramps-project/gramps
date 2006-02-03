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
    NUMERIC = 0
    FIRSTNAME = 1
    FIRSTNAME_FEMALE = 2
    FIRSTNAME_MALE = 3
    LASTNAME = 4
    NOTE = 5
    SHORT = 6
    LONG = 7

    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        if db.readonly:
            return
        
        Tool.Tool.__init__(self,db,person,options_class,name)

        self.person_count = 0
        self.persons_todo = []
        self.parents_todo = []
        self.person_dates = {}
        self.generated_sources = []
        self.generated_media = []
        self.generated_places = []
        self.generated_events = []
        self.text_serial_number = 1
        
        self.random_marrtype_list = (
            (RelLib.Family.UNMARRIED,''),
            (RelLib.Family.CIVIL_UNION,''),
            (RelLib.Family.UNKNOWN,''),
            (RelLib.Family.CUSTOM,'Custom 123')
            )
        self.random_childrel_list = (
            (RelLib.Person.CHILD_NONE,''),
            (RelLib.Person.CHILD_ADOPTED,''),
            (RelLib.Person.CHILD_STEPCHILD,''),
            (RelLib.Person.CHILD_SPONSORED,''),
            (RelLib.Person.CHILD_FOSTER,''),
            (RelLib.Person.CHILD_UNKNOWN,''),
            (RelLib.Person.CHILD_CUSTOM,'Custom 123'),
            )
        self.random_confidence_list = (
            RelLib.SourceRef.CONF_VERY_LOW,
            RelLib.SourceRef.CONF_LOW,
            RelLib.SourceRef.CONF_NORMAL,
            RelLib.SourceRef.CONF_HIGH,
            RelLib.SourceRef.CONF_VERY_HIGH
            )
        self.random_event_role_list = (
            (RelLib.EventRef.UNKNOWN,''),
            (RelLib.EventRef.CUSTOM,'Custom 123'),
            (RelLib.EventRef.PRIMARY,''),
            (RelLib.EventRef.CLERGY,''),
            (RelLib.EventRef.CELEBRANT,''),
            (RelLib.EventRef.AIDE,''),
            (RelLib.EventRef.BRIDE,''),
            (RelLib.EventRef.GROOM,''),
            (RelLib.EventRef.WITNESS,''),
            (RelLib.EventRef.FAMILY,'')
            )
        
        # If an active persons exists the generated tree is connected to that person
        if person:
            # try to get birth and death year
            try:
                bh = person.get_birth_handle()
                b = self.db.get_event_from_handle( bh)
                do = b.get_date_object()
                birth = do.get_year()
            except AttributeError:
                birth = None
            try:
                dh = person.get_death_handle()
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
            self.person_dates[person.get_handle()] = (birth,death)
            
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

        self.check_specialchars = gtk.CheckButton( _("Add special characters"))
        self.check_specialchars.set_active( self.options.handler.options_dict['specialchars'])
        self.top.vbox.pack_start(self.check_specialchars,0,0,5)

        self.check_serial = gtk.CheckButton( _("Add serial number"))
        self.check_serial.set_active( self.options.handler.options_dict['add_serial'])
        self.top.vbox.pack_start(self.check_serial,0,0,5)

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
            batch = True
            self.db.disable_signals()
        else:
            batch = False
        self.trans = self.db.transaction_begin("",batch)

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
            # bootstrap random source and media
            self.rand_source()
            self.rand_media()
            

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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
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
        fam.set_relationship((RelLib.Family.MARRIED,''))
        #fam.add_child_handle(child_h)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        child = self.db.get_person_from_handle(child_h)
        child.add_parent_family_handle(fam_h,(RelLib.Person.CHILD_BIRTH,''),(RelLib.Person.CHILD_BIRTH,''))
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing birth event handle set
        person_h = self.generate_person(None,"Broken11",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle4")
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
        person.set_birth_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing death event handle set
        person_h = self.generate_person(None,"Broken12",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle5")
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
        person.set_death_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person having a non existing event handle set
        person_h = self.generate_person(None,"Broken13",None)
        person = self.db.get_person_from_handle(person_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle("InvalidHandle6")
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
        person.add_event_ref(event_ref)
        self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

        # Creates a person with a birth event having an empty type
        person_h = self.generate_person(None,"Broken14",None)
        event = RelLib.Event()
        event.set_description("Test for Broken14")
        event_h = self.db.add_event(event,self.trans)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
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
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
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
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
        person = self.db.get_person_from_handle(person_h)
        person.add_event_ref(event_ref)
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
        for dateval in dates:
            bevent = RelLib.Event()
            bevent.set_type((RelLib.Event.BIRTH, "Birth"))
            bevent.set_date_object(dateval)
            bevent_h = self.db.add_event(bevent,self.trans)
            self.generated_events.append(bevent_h)
            bevent_ref = RelLib.EventRef()
            bevent_ref.set_reference_handle(bevent_h)
            bevent_ref.set_role((RelLib.EventRef.PRIMARY,''))
            # for the death event display the date as text and parse it back to a new date
            ndate = None
            try:
                datestr = _dd.display( dateval)
                try:
                    ndate = _dp.parse( datestr)
                    if not ndate:
                        ndate = RelLib.Date()
                        ndate.set_as_text("DateParser None")
                except:
                    ndate = RelLib.Date()
                    ndate.set_as_text("DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
            except:
                ndate = RelLib.Date()
                ndate.set_as_text("DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
            
            if dateval.get_modifier() != RelLib.Date.MOD_TEXTONLY \
                   and ndate.get_modifier() == RelLib.Date.MOD_TEXTONLY:
                # parser was unable to correctly parse the string
                ndate.set_as_text( "TEXTONLY: "+ndate.get_text())
                
            
            devent = RelLib.Event()
            devent.set_type((RelLib.Event.DEATH,"Death"))
            devent.set_date_object(ndate)
            devent_h = self.db.add_event(devent,self.trans)
            self.generated_events.append(devent_h)
            devent_ref = RelLib.EventRef()
            devent_ref.set_reference_handle(devent_h)
            devent_ref.set_role((RelLib.EventRef.PRIMARY,''))
            person_h = self.generate_person(None, "DateTest")
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_ref(bevent_ref)
            person.set_death_ref(devent_ref)
            self.db.commit_person(person,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP
    
    def generate_person(self,gender=None,lastname=None,note=None, alive_in_year=None):
        if not self.cli:
            self.progress.set_fraction(min(1.0,max(0.0, 1.0*self.person_count/self.options.handler.options_dict['person_count'])))
            if self.person_count % 10 == 0:
                while gtk.events_pending():
                    gtk.main_iteration()

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        np = RelLib.Person()
        np.set_privacy( randint(0,5) == 1)
        np.set_complete_flag( randint(0,5) == 1)
        
        self.add_defaults(np)
        
        # Note
        if note:
            np.set_note(note)
            
        # Gender
        if gender == None:
            gender = randint(0,1)
        if randint(0,10) == 1:  # Set some persons to unknown gender
            np.set_gender(RelLib.Person.UNKNOWN)
        else:
            np.set_gender(gender)
        
        # Name
        name = RelLib.Name()
        name.set_privacy( randint(0,5) == 1)
        (firstname,lastname) = self.rand_name(lastname, gender)
        name.set_first_name(firstname)
        name.set_surname(lastname)
        name.add_source_reference( self.rand_sourceref())
        name.set_note( self.rand_text(self.NOTE))
        np.set_primary_name(name)
        
        # generate some slightly different alternate name
        alt_name = RelLib.Name(name)
        alt_name.set_privacy( randint(0,5) == 1)
        firstname2 = firstname.replace("m", "n").replace("l", "i").replace("b", "d")
        if firstname2 != firstname:
            alt_name.set_first_name( firstname2)
            alt_name.set_title( self.rand_text(self.SHORT))
            alt_name.set_patronymic( self.rand_text(self.FIRSTNAME_MALE))
            alt_name.set_surname_prefix( self.rand_text(self.SHORT))
            alt_name.set_suffix( self.rand_text(self.SHORT))
            alt_name.add_source_reference( self.rand_sourceref())
            alt_name.set_note( self.rand_text(self.NOTE))
            np.add_alternate_name( alt_name)
        firstname2 = firstname.replace("a", "e").replace("o", "u").replace("r", "p")
        if firstname2 != firstname:
            alt_name.set_first_name( firstname2)
            alt_name.set_title( self.rand_text(self.SHORT))
            alt_name.set_patronymic( self.rand_text(self.FIRSTNAME_MALE))
            alt_name.set_surname_prefix( self.rand_text(self.SHORT))
            alt_name.set_suffix( self.rand_text(self.SHORT))
            alt_name.add_source_reference( self.rand_sourceref())
            alt_name.set_note( self.rand_text(self.NOTE))
            np.add_alternate_name( alt_name)

        if not alive_in_year:
            alive_in_year = randint(1700,2000)

        by = alive_in_year - randint(0,60)
        dy = alive_in_year + randint(0,60)
        
        # birth
        if randint(0,1) == 1:
            (birth_year, eref) = self.rand_event( "Birth", by,by)
            np.set_birth_ref(eref)

        # baptism
        if randint(0,1) == 1:
            (bapt_year, eref) = self.rand_event(
                choice( ("Baptism", "Christening")), by, by+2)
            np.add_event_ref(eref)

        # death
        death_year = None
        if randint(0,1) == 1:
            (death_year, eref) = self.rand_event( "Death", dy,dy)
            np.set_death_ref(eref)

        # burial
        if randint(0,1) == 1:
            (bur_year, eref) = self.rand_event(
                choice( ("Burial", "Cremation")), dy, dy+2)
            np.add_event_handle(eref)
        
        # some shared events
        if randint(0,5) == 1:
            e_h = choice(self.generated_events)
            ref = RelLib.EventRef()
            ref.set_reference_handle(e_h)
            ref.set_role( choice(self.random_event_role_list))
        
        #LDS
        if randint(0,1) == 1:
            lds = self.rand_ldsord( const.lds_baptism)
            np.set_lds_baptism( lds)
        if randint(0,1) == 1:
            lds = self.rand_ldsord( const.lds_baptism)
            np.set_lds_endowment( lds)
        if randint(0,1) == 1:
            lds = self.rand_ldsord( const.lds_csealing)
            np.set_lds_sealing( lds)

        person_handle = self.db.add_person(np,self.trans)
        
        self.person_count = self.person_count+1
        self.person_dates[person_handle] = (by,dy)

        self.commit_transaction()   # COMMIT TRANSACTION STEP

        return( person_handle)
        
    def generate_family(self,person1_h):
        if not person1_h:
            return
        person1 = self.db.get_person_from_handle(person1_h)
        alive_in_year = None
        if person1_h in self.person_dates:
            (born, died) = self.person_dates[person1_h]
            alive_in_year = min( born+randint(10,50), died + randint(-10,10))
            
        if person1.get_gender() == 1:
            if alive_in_year:
                person2_h = self.generate_person(0, alive_in_year = alive_in_year)
            else:
                person2_h = self.generate_person(0)
        else:
            person2_h = person1_h
            if alive_in_year:
                person1_h = self.generate_person(1, alive_in_year = alive_in_year)
            else:
                person1_h = self.generate_person(1)
        
        if randint(0,2) > 0:
            self.parents_todo.append(person1_h)
        if randint(0,2) > 0:
            self.parents_todo.append(person2_h)
            
        fam = RelLib.Family()
        self.add_defaults(fam)
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        if randint(0,2) == 1:
            fam.set_relationship( choice( self.random_marrtype_list))
        else:
            fam.set_relationship((RelLib.Family.MARRIED,''))
        lds = self.rand_ldsord( const.lds_ssealing)
        fam.set_lds_sealing( lds)
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
            if alive_in_year:
                child_h = self.generate_person(None, lastname, alive_in_year = alive_in_year + randint( 16+2*i, 30 + 2*i))
            else:
                child_h = self.generate_person(None, lastname)
                (born,died) = self.person_dates[child_h]
                alive_in_year = born
            fam = self.db.get_family_from_handle(fam_h)
            fam.add_child_handle(child_h)
            self.db.commit_family(fam,self.trans)
            child = self.db.get_person_from_handle(child_h)
            rel1 = (RelLib.Person.CHILD_BIRTH,'')
            if randint(0,2) == 1:
                rel1 = choice( self.random_childrel_list)
            rel2 = (RelLib.Person.CHILD_BIRTH,'')
            if randint(0,2) == 1:
                rel2 = choice( self.random_childrel_list)
            child.add_parent_family_handle(fam_h, rel1, rel2)
            self.db.commit_person(child,self.trans)
            if randint(0,3) > 0:
                self.persons_todo.append(child_h)
        self.commit_transaction()   # COMMIT TRANSACTION STEP
                
    def generate_parents(self,child_h):
        if not child_h:
            return
        child = self.db.get_person_from_handle(child_h)
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
        if randint(0,2) == 1:
            fam.set_relationship( choice( self.random_marrtype_list))
        else:
            fam.set_relationship( (RelLib.Family.MARRIED,'') )
        lds = self.rand_ldsord( const.lds_ssealing)
        fam.set_lds_sealing( lds)
        fam.add_child_handle(child_h)
        fam_h = self.db.add_family(fam,self.trans)
        fam = self.db.commit_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)
        rel1 = (RelLib.Person.CHILD_BIRTH,'')
        if randint(0,2) == 1:
            rel1 = choice( self.random_childrel_list)
        rel2 = (RelLib.Person.CHILD_BIRTH,'')
        if randint(0,2) == 1:
            rel2 = choice( self.random_childrel_list)
        child.add_parent_family_handle(fam_h, rel1, rel2)
        self.db.commit_person(child,self.trans)
        self.commit_transaction()   # COMMIT TRANSACTION STEP

    def add_defaults(self,object,ref_text = ""):
        while randint(0,1) == 1:
            object.add_source_reference( self.rand_sourceref())
        while randint(0,1) == 1:
            object.add_media_reference( self.rand_mediaref())
        while randint(0,1) == 1:
            (year,e) = self.rand_event()
            object.add_event_ref( e)
        while randint(0,1) == 1:
            object.add_attribute( self.rand_attribute())
        try:
            while randint(0,1) == 1:
                object.add_url( self.rand_url())
            while randint(0,1) == 1:
                object.add_address( self.rand_address())
        except AttributeError:
            pass    # family does not have an url and address
        object.set_note( self.rand_text(self.NOTE))
    
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
        
        
    def rand_event( self, type=None, start=None, end=None):
        e = RelLib.Event()
        if not type:
            type = choice( (self.rand_text(self.SHORT),
                            "Census", "Degree", "Emigration", "Immigration"))
        e.set_type( (RelLib.Event.CUSTOM,type) )
        if randint(0,1) == 1:
            e.set_note( self.rand_text(self.NOTE))
        if randint(0,1) == 1:
            e.set_cause( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            e.set_description( self.rand_text(self.LONG))
        while randint(0,1) == 1:
            e.add_source_reference( self.rand_sourceref())
        while randint(0,1) == 1:
            e.add_media_reference( self.rand_mediaref())
        if randint(0,1) == 1:
            e.set_place_handle( self.rand_place())
        (year, d) = self.rand_date( start, end)
        e.set_date_object( d)
        event_h = self.db.add_event(e, self.trans)
        self.generated_events.append(event_h)
        event_ref = RelLib.EventRef()
        event_ref.set_reference_handle(event_h)
        event_ref.set_role((RelLib.EventRef.PRIMARY,''))
        return (year, event_ref)
    
    def rand_ldsord( self, status_list):
        lds = RelLib.LdsOrd()
        if randint(0,1) == 1:
            lds.set_status( randint(0,len(status_list)-1))
        if randint(0,1) == 1:
            lds.set_temple( choice( const.lds_temple_to_abrev.keys()))
        if randint(0,1) == 1:
            lds.set_place_handle( self.rand_place())
        while randint(0,1) == 1:
            lds.add_source_reference( self.rand_sourceref())
        if randint(0,1) == 1:
            lds.set_note( self.rand_text(self.NOTE))
        if randint(0,1) == 1:
            (year,d) = self.rand_date( )
            lds.set_date_object( d)
        return lds

    def rand_source( self):
        source = RelLib.Source()
        source.set_title( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            source.set_author( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            source.set_publication_info( self.rand_text(self.LONG))
        if randint(0,1) == 1:
            source.set_abbreviation( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            source.set_note( self.rand_text(self.NOTE))
        while randint(0,1) == 1:
            source.set_data_item( self.rand_text(self.SHORT), self.rand_text(self.SHORT))
        while randint(0,1) == 1 and self.generated_media:
            source.add_media_reference( self.rand_mediaref())
        self.db.add_source( source, self.trans)
        self.generated_sources.append( source.get_handle())
        return source
    
    def rand_sourceref( self):
        if not self.generated_sources or randint(0,10) == 1:
            self.rand_source()
        sref = RelLib.SourceRef()
        sref.set_base_handle( choice( self.generated_sources))
        if randint(0,1) == 1:
            sref.set_page( self.rand_text(self.NUMERIC))
        if randint(0,1) == 1:
            sref.set_text( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            sref.set_note( self.rand_text(self.NOTE))
        sref.set_privacy( randint(0,5) == 1)
        if randint(0,1) == 1:
            (year, d) = self.rand_date( )
            sref.set_date_object( d)
        sref.set_confidence_level( choice( self.random_confidence_list))
        return sref

    def rand_media( self):
        media = RelLib.MediaObject()
        media.set_description( self.rand_text(self.SHORT))
        media.set_path("/tmp/TestcaseGenerator.png")
        media.set_mime_type("image/png")
        if randint(0,1) == 1:
            media.set_note( self.rand_text(self.NOTE))
        if randint(0,1) == 1:
            (year,d) = self.rand_date()
            media.set_date_object(d)
        while randint(0,1) == 1:
            media.add_source_reference( self.rand_sourceref())
        while randint(0,1) == 1:
            media.add_attribute( self.rand_attribute())
        self.db.add_object( media, self.trans)
        self.generated_media.append( media.get_handle())
        return media
        
    def rand_mediaref( self):
        if not self.generated_media or randint(0,10) == 1:
            self.rand_media()
        mref = RelLib.MediaRef()
        mref.set_reference_handle( choice( self.generated_media))
        if randint(0,1) == 1:
            mref.set_note( self.rand_text(self.NOTE))
        while randint(0,1) == 1:
            mref.add_source_reference( self.rand_sourceref())
        while randint(0,1) == 1:
            mref.add_attribute( self.rand_attribute())
        mref.set_privacy( randint(0,5) == 1)
        return mref

    def rand_address( self):
        addr = RelLib.Address()
        if randint(0,1) == 1:
            addr.set_street( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_phone( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_city( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_state( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_country( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_postal_code( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            addr.set_note( self.rand_text(self.NOTE))
        while randint(0,1) == 1:
            addr.add_source_reference( self.rand_sourceref())
        addr.set_privacy( randint(0,5) == 1)
        return addr
    
    def rand_url( self):
        url = RelLib.Url()
        url.set_path("http://www.gramps-project.org/")
        url.set_description( self.rand_text(self.SHORT))
        url.set_privacy( randint(0,5) == 1)
        return url

    def rand_attribute( self):
        attr = RelLib.Attribute()
        attr.set_type( self.rand_text(self.SHORT))
        attr.set_value( self.rand_text(self.SHORT))
        attr.set_note( self.rand_text(self.NOTE))
        while randint(0,1) == 1:
            attr.add_source_reference( self.rand_sourceref())
        attr.set_privacy( randint(0,5) == 1)
        return attr
        
    def rand_location( self):
        loc = RelLib.Location()
        if randint(0,1) == 1:
            loc.set_city( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_postal_code( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_phone( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_parish( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_county( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_state( self.rand_text(self.SHORT))
        if randint(0,1) == 1:
            loc.set_country( self.rand_text(self.SHORT))
        return loc
    
    def rand_place( self):
        if not self.generated_places or randint(0,10) == 1:
            place = RelLib.Place()
            place.set_main_location( self.rand_location())
            while randint(0,1) == 1:
                place.add_alternate_locations( self.rand_location())
            place.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                place.set_note( self.rand_text(self.NOTE))
            if randint(0,1) == 1:
                place.set_longitude( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                place.set_latitude( self.rand_text(self.SHORT))
            while randint(0,1) == 1:
                    place.add_source_reference( self.rand_sourceref())
            while randint(0,1) == 1:
                    place.add_media_reference( self.rand_mediaref())
            if randint(0,1) == 1:
                place.add_url( self.rand_url())
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
            result = result + "Geberated by TestcaseGenerator."
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
        
        return result
    
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
            'specialchars'  : 0,
            'add_serial'    : 0,
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
        }

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

if __debug__:
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
        description = _("The testcase generator will generate some persons "
                        "and families that have broken links in the database "
                        "or data that is in conflict to a relation.")
        )
