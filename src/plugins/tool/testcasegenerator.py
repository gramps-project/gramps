# encoding: utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Tim G L Lyons
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

"""Tools/Debug/Generate Testcases for Persons and Families"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from random import randint,choice,random
from gen.ggettext import gettext as _
import time

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
import gtk 

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gen.db import DbTxn
import gen.mime
from gui.plug import tool
import Utils
from gui.utils import ProgressMeter
from gen.utils.lds import TEMPLES
from gen.db.dbconst import *
import const

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class TestcaseGenerator(tool.BatchTool):
    NUMERIC = 0
    FIRSTNAME = 1
    FIRSTNAME_FEMALE = 2
    FIRSTNAME_MALE = 3
    LASTNAME = 4
    NOTE = 5
    SHORT = 6
    LONG = 7
    TAG = 8
    STYLED_TEXT = 9
    
#    GEDCON definition:
#    
#    FAMILY_EVENT_STRUCTURE:=
#    [
#    n [ ANUL | CENS | DIV | DIVF ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n [ ENGA | MARR | MARB | MARC ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n [ MARL | MARS ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n EVEN {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    ]

    FAMILY_EVENTS = set([
            gen.lib.EventType.ANNULMENT,
            gen.lib.EventType.CENSUS,
            gen.lib.EventType.DIVORCE,
            gen.lib.EventType.DIV_FILING,
            gen.lib.EventType.ENGAGEMENT,
            gen.lib.EventType.MARRIAGE,
            gen.lib.EventType.MARR_BANNS,
            gen.lib.EventType.MARR_CONTR,
            gen.lib.EventType.MARR_LIC,
            gen.lib.EventType.MARR_SETTL,
            gen.lib.EventType.CUSTOM            ])

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.person = None
        if dbstate.db.readonly:
            return

        tool.BatchTool.__init__(self, dbstate, options_class, name)

        if self.fail:
            return

        self.person_count = 0
        self.persons_todo = []
        self.parents_todo = []
        self.person_dates = {}
        self.generated_repos = []
        self.generated_sources = []
        self.generated_citations = []
        self.generated_media = []
        self.generated_places = []
        self.generated_events = []
        self.generated_families = []
        self.generated_notes = []
        self.generated_tags = []
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
        title = "%s - Gramps" % _("Generate testcases")
        self.top = gtk.Dialog(title)
        self.top.set_default_size(400,150)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % _("Generate testcases"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label,0,0,5)

        self.check_lowlevel = gtk.CheckButton( _("Generate low level database "
                                "errors\nCorrection needs database reload"))
        self.check_lowlevel.set_active( self.options.handler.options_dict['lowlevel'])
        self.top.vbox.pack_start(self.check_lowlevel,0,0,5)

        self.check_bugs = gtk.CheckButton( _("Generate database errors"))
        self.check_bugs.set_active( self.options.handler.options_dict['bugs'])
        self.top.vbox.pack_start(self.check_bugs,0,0,5)

        self.check_persons = gtk.CheckButton( _("Generate dummy data"))
        self.check_persons.set_active( self.options.handler.options_dict['persons'])
        self.check_persons.connect('clicked', self.on_dummy_data_clicked)
        self.top.vbox.pack_start(self.check_persons,0,0,5)

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

        self.label = gtk.Label(_("Number of people to generate\n"
                                 "(Number is approximate because families "
                                 "are generated)"))
        self.label.set_alignment(0.0, 0.5)
        self.top.vbox.pack_start(self.label,0,0,5)

        self.entry_count = gtk.Entry()
        self.entry_count.set_text( unicode( self.options.handler.options_dict['person_count']))
        self.on_dummy_data_clicked(self.check_persons)
        self.top.vbox.pack_start(self.entry_count,0,0,5)

        self.top.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.top.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        self.top.show_all()

        response = self.top.run()
        self.options.handler.options_dict['lowlevel']  = int(
            self.check_lowlevel.get_active())
        self.options.handler.options_dict['bugs']  = int(
            self.check_bugs.get_active())
        self.options.handler.options_dict['persons']  = int(
            self.check_persons.get_active())
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

    def on_dummy_data_clicked(self, obj):
        self.label.set_sensitive(obj.get_active())
        self.entry_count.set_sensitive(obj.get_active())
        
    def run_tool(self, cli=False):
        self.cli = cli
        if( not cli):
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.progress = ProgressMeter(_('Generating testcases'),'')
        self.transaction_count = 0;
        
        if self.options.handler.options_dict['lowlevel']:
            self.progress.set_pass(_('Generating low level database errors'),
                            1)
            self.test_low_level(); self.progress.step()

        if self.options.handler.options_dict['bugs'] or \
            self.options.handler.options_dict['persons']:
            self.generate_tags()

        if self.options.handler.options_dict['bugs']:
            self.generate_data_errors()
        
        if self.options.handler.options_dict['persons']:
            self.progress.set_pass(_('Generating families'),
                            self.options.handler.options_dict['person_count'])
            self.person_count = 0
            self.progress_step = self.progress.step

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
        self.progress.close()
            
        if( not cli):
            self.top.destroy()
        
    def generate_data_errors(self):
        """This generates errors in the database to test src/plugins/tool/Check
        The module names correspond to the checking methods in 
        src/plugins/tool/Check.CheckIntegrity """
        self.progress.set_pass(_('Generating database errors'),
                               18)
        # The progress meter is normally stepped every time a person is
        # generated by generate_person. However in this case, generate_person is
        # called by some of the constituent functions, but we only want the
        # meter to be stepped every time a test function has been completed.
        self.progress_step = lambda: None

        self.test_fix_encoding(); self.progress.step()
        self.test_fix_ctrlchars_in_notes(); self.progress.step()
        self.test_cleanup_missing_photos(); self.progress.step()
        self.test_cleanup_deleted_name_formats(); self.progress.step()
        self.test_cleanup_empty_objects(); self.progress.step()
        self.test_check_for_broken_family_links(); self.progress.step()
        self.test_check_parent_relationships(); self.progress.step()
        self.test_cleanup_empty_families(); self.progress.step()
        self.test_cleanup_duplicate_spouses(); self.progress.step()
        self.test_check_events(); self.progress.step()
        self.test_check_person_references(); self.progress.step()
        self.test_check_family_references(); self.progress.step()
        self.test_check_place_references(); self.progress.step()
        self.test_check_source_references(); self.progress.step()
        self.test_check_citation_references(); self.progress.step()
        self.test_check_media_references(); self.progress.step()
        self.test_check_repo_references(); self.progress.step()
        self.test_check_note_references(); self.progress.step()
        self.progress.close()
        
    def test_low_level(self):
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            o = gen.lib.Note()
            o.set("dup 1" + self.rand_text(self.NOTE))
            o.set_format( choice( (gen.lib.Note.FLOWED,gen.lib.Note.FORMATTED)))
            o.set_type( self.rand_type(gen.lib.NoteType()))
            h = self.db.add_note(o, self.trans)
            print "object %s, handle %s, Gramps_Id %s" % (o, o.handle, 
                                                          o.gramps_id)
            
            handle = o.get_handle()
    
            o = gen.lib.Source()
            o.set_title("dup 2" + self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_author( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_publication_info( self.rand_text(self.LONG))
            if randint(0,1) == 1:
                o.set_abbreviation( self.rand_text(self.SHORT))
            while randint(0,1) == 1:
                o.set_data_item( self.rand_text(self.SHORT), self.rand_text(self.SHORT))
            o.set_handle(handle)
            self.db.add_source(o, self.trans)
            print "object %s, handle %s, Gramps_Id %s" % (o, o.handle, 
                                                          o.gramps_id)

    def test_fix_encoding(self):
        # Creates a media object with character encoding errors. This tests
        # Check.fix_encoding() and also cleanup_missing_photos
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            m = gen.lib.MediaObject()
            self.fill_object(m)
            m.set_description("leave this media object invalid description\x9f")
            m.set_path("/tmp/click_on_keep_reference.png\x9f")
            m.set_mime_type("image/png\x9f")
            self.db.add_object(m, self.trans)

            m = gen.lib.MediaObject()
            self.fill_object(m)
            m.set_description("reselect this media object invalid description\x9f")
            m.set_path("/tmp/click_on_select_file.png\x9f")
            m.set_mime_type("image/png\x9f")
            self.db.add_object(m, self.trans)
            
            # setup media attached to Source and Citation to be removed
            
            m = gen.lib.MediaObject()
            self.fill_object(m)
            m.set_description(u'remove this media object')
            m.set_path(u"/tmp/click_on_remove_object.png")
            m.set_mime_type("image/png")
            self.db.add_object(m, self.trans)
            
            s = gen.lib.Source()
            s.set_title(u'media should be removed from this source')
            r = gen.lib.MediaRef()
            r.set_reference_handle(m.handle)
            s.add_media_reference(r)
            self.db.add_source( s, self.trans)

            c = gen.lib.Citation()
            self.fill_object(c)
            c.set_reference_handle(s.handle)
            c.set_page(u'media should be removed from this citation')
            r = gen.lib.MediaRef()
            r.set_reference_handle(m.handle)
            c.add_media_reference(r)
            self.db.add_citation(c, self.trans)

    def test_fix_ctrlchars_in_notes(self):
        # Creates a note with control characters. This tests
        # Check.fix_ctrlchars_in_notes()
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            o = gen.lib.Note()
            o.set("This is a text note with a \x03 control character")
            o.set_format(choice( (gen.lib.Note.FLOWED,gen.lib.Note.FORMATTED)))
            o.set_type(self.rand_type(gen.lib.NoteType()))
            self.db.add_note(o, self.trans)

    def test_cleanup_missing_photos(self):
        pass
    
    def test_cleanup_deleted_name_formats(self):
        pass
    
    def test_cleanup_empty_objects(self):
        # Generate empty objects to test their deletion
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            p = gen.lib.Person()
            self.db.add_person( p, self.trans)
    
            f = gen.lib.Family()
            self.db.add_family( f, self.trans)
    
            e = gen.lib.Event()
            self.db.add_event( e, self.trans)
    
            p = gen.lib.Place()
            self.db.add_place( p, self.trans)
    
            s = gen.lib.Source()
            self.db.add_source( s, self.trans)
    
            c = gen.lib.Citation()
            self.db.add_citation( c, self.trans)
    
            m = gen.lib.MediaObject()
            self.db.add_object( m, self.trans)
    
            r = gen.lib.Repository()
            self.db.add_repository( r, self.trans)
    
            n = gen.lib.Note()
            self.db.add_note( n, self.trans)
    
    def test_check_for_broken_family_links(self):
        # Create a family, that links to father and mother, but father does not
        # link back
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken1","Family links to this person, but person does not link back")
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken1",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            #person1 = self.db.get_person_from_handle(person1_h)
            #person1.add_family_handle(fam_h)
            #self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        # Create a family, that misses the link to the father
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken2",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken2",None)
            fam = gen.lib.Family()
            #fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        # Create a family, that misses the link to the mother
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken3",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken3",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            #fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        # Create a family, that links to father and mother, but mother does not
        # link back
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken4",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken4","Family links to this person, but person does not link back")
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
            #person2 = self.db.get_person_from_handle(person2_h)
            #person2.add_family_handle(fam_h)
            #self.db.commit_person(person2,self.trans)

        # Create two married people of same sex.
        # This is NOT detected as an error by plugins/tool/Check.py
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken5",None)
            person2_h = self.generate_person(gen.lib.Person.MALE,"Broken5",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        # Create a family, that contains an invalid handle to for the father
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            #person1_h = self.generate_person(gen.lib.Person.MALE,"Broken6",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken6",None)
            fam = gen.lib.Family()
            fam.set_father_handle("InvalidHandle1")
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            #person1 = self.db.get_person_from_handle(person1_h)
            #person1.add_family_handle(fam_h)
            #self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2,self.trans)

        # Create a family, that contains an invalid handle to for the mother
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken7",None)
            #person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken7",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle("InvalidHandle2")
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1,self.trans)
            #person2 = self.db.get_person_from_handle(person2_h)
            #person2.add_family_handle(fam_h)
            #self.db.commit_person(person2,self.trans)

        # Creates a family where the child does not link back to the family
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken8",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken8",None)
            child_h = self.generate_person(None,"Broken8",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            child_ref = gen.lib.ChildRef()
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

        # Creates a family where the child is not linked, but the child links to the family
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken9",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken9",None)
            child_h = self.generate_person(None,"Broken9",None)
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            # child_ref = gen.lib.ChildRef()
            # child_ref.set_reference_handle(child_h)
            # self.fill_object(child_ref)
            # fam.add_child_ref(child_ref)
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

        # Creates a family where the child is one of the parents
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken19",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken19",None)
            child_h = person2_h
            fam = gen.lib.Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
            child_ref = gen.lib.ChildRef()
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

        # Creates a couple that refer to a family that does not exist in the
        # database.
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(gen.lib.Person.MALE,"Broken20",None)
            person2_h = self.generate_person(gen.lib.Person.FEMALE,"Broken20",None)
#            fam = gen.lib.Family()
#            fam.set_father_handle(person1_h)
#            fam.set_mother_handle(person2_h)
#            fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
#            child_ref = gen.lib.ChildRef()
#            # child_ref.set_reference_handle(child_h)
#            # self.fill_object(child_ref)
#            # fam.add_child_ref(child_ref)
#            fam_h = self.db.add_family(fam,self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle("InvalidHandle3")
            self.db.commit_person(person1,self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle("InvalidHandle3")
            self.db.commit_person(person2,self.trans)
#            child = self.db.get_person_from_handle(child_h)
#            child.add_parent_family_handle(fam_h)
#            self.db.commit_person(child,self.trans)

    def test_check_parent_relationships(self):
        pass
    
    def test_cleanup_empty_families(self):
        pass
    
    def test_cleanup_duplicate_spouses(self):
        pass
    
    def test_check_events(self):
        # Creates a person having a non existing birth event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken11",None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle("InvalidHandle4")
            person.set_birth_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person having a non existing death event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken12",None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle("InvalidHandle5")
            person.set_death_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person having a non existing event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken13",None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle("InvalidHandle6")
            person.add_event_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person with a birth event having an empty type
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken14",None)
            event = gen.lib.Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken14")
            event_h = self.db.add_event(event,self.trans)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person with a death event having an empty type
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken15",None)
            event = gen.lib.Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken15")
            event_h = self.db.add_event(event,self.trans)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_death_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person with an event having an empty type
        # This is NOT detected as an error by plugins/tool/Check.py
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken16",None)
            event = gen.lib.Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken16")
            event_h = self.db.add_event(event,self.trans)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.add_event_ref(event_ref)
            self.db.commit_person(person,self.trans)

    def test_check_person_references(self):
        pass
    
    def test_check_family_references(self):
        pass
    
    def test_check_place_references(self):
        # Creates a person with a birth event pointing to nonexisting place
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken17",None)
            event = gen.lib.Event()
            event.set_type(gen.lib.EventType.BIRTH)
            event.set_place_handle("InvalidHandle7")
            event.set_description("Test for Broken17")
            event_h = self.db.add_event(event,self.trans)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_ref(event_ref)
            self.db.commit_person(person,self.trans)

        # Creates a person with an event pointing to nonexisting place
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None,"Broken18",None)
            event = gen.lib.Event()
            event.set_type(gen.lib.EventType.BIRTH)
            event.set_place_handle("InvalidHandle8")
            event.set_description("Test for Broken18")
            event_h = self.db.add_event(event,self.trans)
            event_ref = gen.lib.EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.add_event_ref(event_ref)
            self.db.commit_person(person,self.trans)

    def test_check_source_references(self):

        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            c = gen.lib.Citation()
            self.fill_object(c)
            c.set_reference_handle("unknownsourcehandle")
            c.set_page(u'unreferenced citation with invalid source ref')
            self.db.add_citation(c, self.trans)
            
            c = gen.lib.Citation()
            self.fill_object(c)
            c.set_reference_handle(None)
            c.set_page(u'unreferenced citation with invalid source ref')
            self.db.add_citation(c, self.trans)
            
            c = gen.lib.Citation()
            self.fill_object(c)
            c.set_reference_handle("unknownsourcehandle")
            c.set_page(u'citation and references to it should be removed')
            c_h1 = self.db.add_citation(c, self.trans)
            
            c = gen.lib.Citation()
            self.fill_object(c)
            c.set_reference_handle(None)
            c.set_page(u'citation and references to it should be removed')
            c_h2 = self.db.add_citation(c, self.trans)

            self.create_all_possible_citations([c_h1, c_h2], "Broken21",
                                               u'non-existent source')

    def test_check_citation_references(self):
        # Generate objects that refer to non-existant citations
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            
            c_h = "unknowncitationhandle"
            self.create_all_possible_citations([c_h, None], "Broken22",
                                               u'non-existent citation')
        
    def create_all_possible_citations(self, c_h_list, name, message):
        # Create citations attached to each of the following objects:
        #        Person
        #         Name
        #         Address
        #         Attribute
        #         PersonRef
        #         MediaRef
        #          Attribute
        #         LdsOrd
        #        
        #        Family
        #         Attribute
        #         ChildRef
        #         MediaRef
        #          Attribute
        #         LdsOrd
        #        
        #        Event
        #         Attribute
        #         MediaRef
        #          Attribute
        #        
        #        MediaObject
        #         Attribute
        #        
        #        Place
        #         MediaRef
        #          Attribute
        #        
        #        Repository (Repositories themselves do not have SourceRefs)
        #         Address
        m = gen.lib.MediaObject()
        m.set_description(message)
        m.set_path(unicode(const.ICON))
        m.set_mime_type(gen.mime.get_type(m.get_path()))
        m.add_citation(choice(c_h_list))
        # MediaObject : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        m.add_attribute(a)
        self.db.add_object(m, self.trans)
        
        person1_h = self.generate_person(gen.lib.Person.MALE,name,None)
        person2_h = self.generate_person(gen.lib.Person.FEMALE,name,None)
        child_h = self.generate_person(None,name,None)
        fam = gen.lib.Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship((gen.lib.FamilyRelType.MARRIED,''))
        # Family
        fam.add_citation(choice(c_h_list))
        # Family : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        fam.add_attribute(a)
        # Family : ChildRef
        child_ref = gen.lib.ChildRef()
        child_ref.set_reference_handle(child_h)
        self.fill_object(child_ref)
        child_ref.add_citation(choice(c_h_list))
        fam.add_child_ref(child_ref)
        # Family : MediaRef
        mr = gen.lib.MediaRef()
        mr.set_reference_handle(m.handle)
        mr.add_citation(choice(c_h_list))
        # Family : MediaRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        mr.add_attribute(a)
        fam.add_media_reference(mr)
        # Family : LDSORD
        ldsord = gen.lib.LdsOrd()
        self.fill_object( ldsord)
        # TODO: adapt type and status to family/person
        #if isinstance(o,gen.lib.Person):
        #if isinstance(o,gen.lib.Family):
        ldsord.set_type( choice(
            [item[0] for item in gen.lib.LdsOrd._TYPE_MAP] ))
        ldsord.set_status( randint(0,len(gen.lib.LdsOrd._STATUS_MAP)-1))
        ldsord.add_citation(choice(c_h_list))
        fam.add_lds_ord(ldsord)
        # Family : EventRef
        e = gen.lib.Event()
        e.set_type(gen.lib.EventType.MARRIAGE)
        (year, d) = self.rand_date()
        e.set_date_object(d)
        e.set_description(message)
        event_h = self.db.add_event(e, self.trans)
        er = gen.lib.EventRef()
        er.set_reference_handle(event_h)
        er.set_role(self.rand_type(gen.lib.EventRoleType()))
        # Family : EventRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        er.add_attribute(a)
        fam.add_event_ref(er)
        fam_h = self.db.add_family(fam,self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        # Person
        person1.add_citation(choice(c_h_list))
        # Person : Name
        alt_name = gen.lib.Name(person1.get_primary_name())
        alt_name.set_first_name(message)
        alt_name.add_citation(choice(c_h_list))
        person1.add_alternate_name(alt_name)
        # Person : Address
        a = gen.lib.Address()
        a.set_street(message)
        a.add_citation(choice(c_h_list))
        person1.add_address(a)
        # Person : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        person1.add_attribute(a)
        # Person : PersonRef
        asso_h = self.generate_person()
        asso = gen.lib.PersonRef()
        asso.set_reference_handle(asso_h)
        asso.set_relation(self.rand_text(self.SHORT))
        self.fill_object(asso)
        asso.add_citation(choice(c_h_list))
        person1.add_person_ref(asso)
        # Person : MediaRef
        mr = gen.lib.MediaRef()
        mr.set_reference_handle(m.handle)
        mr.add_citation(choice(c_h_list))
        # Person : MediaRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(self.rand_text(self.SHORT))
        a.add_citation(choice(c_h_list))
        mr.add_attribute(a)
        person1.add_media_reference(mr)
        # Person : LDSORD
        ldsord = gen.lib.LdsOrd()
        self.fill_object( ldsord)
        # TODO: adapt type and status to family/person
        #if isinstance(o,gen.lib.Person):
        #if isinstance(o,gen.lib.Family):
        ldsord.set_type( choice(
            [item[0] for item in gen.lib.LdsOrd._TYPE_MAP] ))
        ldsord.set_status( randint(0,len(gen.lib.LdsOrd._STATUS_MAP)-1))
        ldsord.add_citation(choice(c_h_list))
        person1.add_lds_ord(ldsord)
        # Person : EventRef
        e = gen.lib.Event()
        e.set_type(gen.lib.EventType.ELECTED)
        (year, d) = self.rand_date()
        e.set_date_object(d)
        e.set_description(message)
        event_h = self.db.add_event(e, self.trans)
        er = gen.lib.EventRef()
        er.set_reference_handle(event_h)
        er.set_role(self.rand_type(gen.lib.EventRoleType()))
        # Person : EventRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        er.add_attribute(a)
        person1.add_event_ref(er)
        self.db.commit_person(person1,self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2,self.trans)

        e = gen.lib.Event()
        e.set_description(message)
        e.set_type(gen.lib.EventType.MARRIAGE)
        # Event
        e.add_citation(choice(c_h_list))
        # Event : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(message)
        a.add_citation(choice(c_h_list))
        e.add_attribute(a)
        # Event : MediaRef
        mr = gen.lib.MediaRef()
        mr.set_reference_handle(m.handle)
        mr.add_citation(choice(c_h_list))
        # Event : MediaRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(self.rand_text(self.SHORT))
        a.add_citation(choice(c_h_list))
        mr.add_attribute(a)
        e.add_media_reference(mr)
        self.db.add_event(e, self.trans)

        p = gen.lib.Place()
        p.set_title(message)
        p.add_citation(choice(c_h_list))
        # Place : MediaRef
        mr = gen.lib.MediaRef()
        mr.set_reference_handle(m.handle)
        mr.add_citation(choice(c_h_list))
        # Place : MediaRef : Attribute
        a = gen.lib.Attribute()
        a.set_type(self.rand_type(gen.lib.AttributeType()))
        a.set_value(self.rand_text(self.SHORT))
        a.add_citation(choice(c_h_list))
        mr.add_attribute(a)
        p.add_media_reference(mr)
        self.db.add_place(p, self.trans)

        r = gen.lib.Repository()
        r.set_name(message)
        r.set_type(gen.lib.RepositoryType.LIBRARY)
        # Repository : Address
        a = gen.lib.Address()
        a.set_street(message)
        a.add_citation(choice(c_h_list))
        r.add_address(a)
        self.db.add_repository(r, self.trans)

    def test_check_media_references(self):
        pass
    
    def test_check_repo_references(self):
        pass
    
    def test_check_note_references(self):
        pass
    

    def generate_person(self,gender=None,lastname=None, note=None, alive_in_year=None):
        if not self.cli:
            if self.person_count % 10 == 0:
                while gtk.events_pending():
                    gtk.main_iteration()

        np = gen.lib.Person()
        self.fill_object(np)
        
        # Gender
        if gender is None:
            gender = randint(0,1)
        if randint(0,10) == 1:  # Set some persons to unknown gender
            np.set_gender(gen.lib.Person.UNKNOWN)
        else:
            np.set_gender(gender)
        
        # Name
        name = gen.lib.Name()
        (firstname,lastname) = self.rand_name(lastname, gender)
        name.set_first_name(firstname)
        surname = gen.lib.Surname()
        surname.set_surname(lastname)
        name.add_surname(surname)
        self.fill_object( name)
        np.set_primary_name(name)
        
        # generate some slightly different alternate name
        firstname2 = firstname.replace("m", "n").replace("l", "i").replace("b", "d")
        if firstname2 != firstname:
            alt_name = gen.lib.Name(name)
            self.fill_object( alt_name)
            if randint(0,2) == 1:
                surname = gen.lib.Surname()
                surname.set_surname(self.rand_text(self.LASTNAME))
                alt_name.add_surname(surname)
            elif randint(0,2) == 1:
                surname = gen.lib.Surname()
                surname.set_surname(lastname)
                alt_name.add_surname(surname)
            if randint(0,1) == 1:
                alt_name.set_first_name( firstname2)
            if randint(0,1) == 1:
                alt_name.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                patronymic = gen.lib.Surname()
                patronymic.set_surname( self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(gen.lib.NameOriginType.PATRONYMIC)
                alt_name.add_surname(patronymic)
            if randint(0,1) == 1:
                alt_name.get_primary_surname().set_prefix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_suffix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                alt_name.set_call_name( self.rand_text(self.FIRSTNAME))
            np.add_alternate_name( alt_name)
        firstname2 = firstname.replace("a", "e").replace("o", "u").replace("r", "p")
        if firstname2 != firstname:
            alt_name = gen.lib.Name(name)
            self.fill_object( alt_name)
            if randint(0,2) == 1:
                surname = gen.lib.Surname()
                surname.set_surname(self.rand_text(self.LASTNAME))
                alt_name.add_surname(surname)
            elif randint(0,2) == 1:
                surname = gen.lib.Surname()
                surname.set_surname(lastname)
                alt_name.add_surname(surname)
            if randint(0,1) == 1:
                alt_name.set_first_name( firstname2)
            if randint(0,1) == 1:
                alt_name.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                patronymic = gen.lib.Surname()
                patronymic.set_surname(self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(gen.lib.NameOriginType.PATRONYMIC)
                alt_name.add_surname(patronymic)
            if randint(0,1) == 1:
                alt_name.get_primary_surname().set_prefix( self.rand_text(self.SHORT))
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
            (birth_year, eref) = self.rand_personal_event( gen.lib.EventType.BIRTH, by,by)
            np.set_birth_ref(eref)

        # baptism
        if randint(0,1) == 1:
            (bapt_year, eref) = self.rand_personal_event(
                choice( (gen.lib.EventType.BAPTISM, gen.lib.EventType.CHRISTEN)), by, by+2)
            np.add_event_ref(eref)

        # death
        death_year = None
        if randint(0,1) == 1:
            (death_year, eref) = self.rand_personal_event( gen.lib.EventType.DEATH, dy,dy)
            np.set_death_ref(eref)

        # burial
        if randint(0,1) == 1:
            (bur_year, eref) = self.rand_personal_event(
                choice( (gen.lib.EventType.BURIAL, gen.lib.EventType.CREMATION)), dy, dy+2)
            np.add_event_ref(eref)
        
        # some other events
        while randint(0,5) == 1:
            (birth_year, eref) = self.rand_personal_event( None, by,dy)
            np.add_event_ref(eref)

        # some shared events
        if self.generated_events:
            while randint(0,5) == 1:
                e_h = choice(self.generated_events)
                eref = gen.lib.EventRef()
                self.fill_object( eref)
                eref.set_reference_handle(e_h)
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
                asso = gen.lib.PersonRef()
                asso.set_reference_handle(asso_h)
                asso.set_relation(self.rand_text(self.SHORT))
                self.fill_object(asso)
                np.add_person_ref(asso)
                if randint(0,2) == 0:
                    self.persons_todo.append(asso_h)
        
        person_handle = self.db.add_person(np,self.trans)
        
        self.person_count = self.person_count+1
        self.progress_step()
        if self.person_count % 10 == 1:
            print "person count", self.person_count
        self.person_dates[person_handle] = (by,dy)

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
            
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            fam = gen.lib.Family()
            self.add_defaults(fam)
            if person1_h:
                fam.set_father_handle(person1_h)
            if person2_h:
                fam.set_mother_handle(person2_h)
            
            # Avoid adding the same event more than once to the same family
            event_set = set()
            
            # Generate at least one family event with a probability of 75%
            if randint(0, 3) > 0:
                (birth_year, eref) = self.rand_family_event(None)
                fam.add_event_ref(eref)
                event_set.add(eref.get_reference_handle())
            
            # generate some more events with a lower probability
            while randint(0, 3) == 1:
                (birth_year, eref) = self.rand_family_event(None)
                if eref.get_reference_handle() in event_set:
                    continue
                fam.add_event_ref(eref)
                event_set.add(eref.get_reference_handle())
    
            # some shared events
            if self.generated_events:
                while randint(0, 5) == 1:
                    typeval = gen.lib.EventType.UNKNOWN
                    while int(typeval) not in self.FAMILY_EVENTS:
                        e_h = choice(self.generated_events)
                        typeval = self.db.get_event_from_handle(e_h).get_type()
                    if e_h in event_set:
                        break
                    eref = gen.lib.EventRef()
                    self.fill_object( eref)
                    eref.set_reference_handle(e_h)
                    fam.add_event_ref(eref)
                    event_set.add(e_h)

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
                child_ref = gen.lib.ChildRef()
                child_ref.set_reference_handle(child_h)
                self.fill_object(child_ref)
                fam.add_child_ref(child_ref)
                self.db.commit_family(fam,self.trans)
                child = self.db.get_person_from_handle(child_h)
                child.add_parent_family_handle(fam_h)
                self.db.commit_person(child,self.trans)
                if randint(0,3) > 0:
                    self.persons_todo.append(child_h)
                
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
            
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            fam = gen.lib.Family()
            self.add_defaults(fam)
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            child_ref = gen.lib.ChildRef()
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

    def generate_tags(self):
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            for counter in range(10):
                tag = gen.lib.Tag()
                tag.set_name(self.rand_text(self.TAG))
                tag.set_color(self.rand_color())
                tag.set_priority(self.db.get_number_of_tags())
                tag_handle = self.db.add_tag(tag, self.trans)
                self.generated_tags.append(tag_handle)

    def add_defaults(self, object):
        self.fill_object( object)
    
    def rand_name( self, lastname=None, gender=None):
        if gender == gen.lib.Person.MALE:
            firstname = self.rand_text( self.FIRSTNAME_MALE)
        elif gender == gen.lib.Person.FEMALE:
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
        
        ndate = gen.lib.Date()
        if randint(0,10) == 1:
            # Some get a textual date
            ndate.set_as_text( choice((self.rand_text(self.SHORT),"Unknown","??","Don't know","TODO!")))
        else:
            if randint(0,10) == 1:
                # some get an empty date
                pass
            else:
                # regular dates
                calendar = gen.lib.Date.CAL_GREGORIAN
                quality = choice( (gen.lib.Date.QUAL_NONE,
                                   gen.lib.Date.QUAL_ESTIMATED,
                                   gen.lib.Date.QUAL_CALCULATED))
                modifier = choice( (gen.lib.Date.MOD_NONE,
                                    gen.lib.Date.MOD_BEFORE,
                                    gen.lib.Date.MOD_AFTER,\
                                    gen.lib.Date.MOD_ABOUT,
                                    gen.lib.Date.MOD_RANGE,
                                    gen.lib.Date.MOD_SPAN))
                day = randint(0,28)
                if day > 0: # avoid days without month
                    month = randint(1,12)
                else:
                    month = randint(0,12)
                
                if modifier in (gen.lib.Date.MOD_RANGE, gen.lib.Date.MOD_SPAN):
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
    
        
        if issubclass(o.__class__,gen.lib.addressbase.AddressBase):
            while randint(0,1) == 1:
                a = gen.lib.Address()
                self.fill_object(a)
                o.add_address( a)

        if isinstance(o,gen.lib.Attribute):
            o.set_type( self.rand_type(gen.lib.AttributeType()))
            o.set_value( self.rand_text(self.SHORT))

        if issubclass(o.__class__,gen.lib.attrbase.AttributeBase):
            while randint(0,1) == 1:
                a = gen.lib.Attribute()
                self.fill_object(a)
                o.add_attribute( a)

        if isinstance(o,gen.lib.ChildRef):
            if randint(0,3) == 1:
                o.set_mother_relation( self.rand_type( gen.lib.ChildRefType()))
            if randint(0,3) == 1:
                o.set_father_relation( self.rand_type( gen.lib.ChildRefType()))

        if issubclass(o.__class__,gen.lib.datebase.DateBase):
            if randint(0,1) == 1:
                (y,d) = self.rand_date()
                o.set_date_object( d)

        if isinstance(o,gen.lib.Event):
            if randint(0,1) == 1:
                o.set_description( self.rand_text(self.LONG))

        if issubclass(o.__class__,gen.lib.eventref.EventRef):
            o.set_role( self.rand_type(gen.lib.EventRoleType()))

        if isinstance(o,gen.lib.Family):
            if randint(0,2) == 1:
                o.set_relationship( self.rand_type(gen.lib.FamilyRelType()))
            else:
                o.set_relationship(gen.lib.FamilyRelType(gen.lib.FamilyRelType.MARRIED))

        if isinstance(o,gen.lib.LdsOrd):
            if randint(0,1) == 1:
                o.set_temple( choice(TEMPLES.name_code_data())[1])

        if issubclass(o.__class__,gen.lib.ldsordbase.LdsOrdBase):
            while randint(0,1) == 1:
                ldsord = gen.lib.LdsOrd()
                self.fill_object( ldsord)
                # TODO: adapt type and status to family/person
                #if isinstance(o,gen.lib.Person):
                #if isinstance(o,gen.lib.Family):
                ldsord.set_type( choice(
                    [item[0] for item in gen.lib.LdsOrd._TYPE_MAP] ))
                ldsord.set_status( randint(0,len(gen.lib.LdsOrd._STATUS_MAP)-1))
                if self.generated_families:
                    ldsord.set_family_handle( choice(self.generated_families))
                o.add_lds_ord( ldsord)

        if isinstance(o,gen.lib.Location):
            if randint(0,1) == 1:
                o.set_parish( self.rand_text(self.SHORT))

        if issubclass(o.__class__,gen.lib.locationbase.LocationBase):
            if randint(0,1) == 1:
                o.set_street( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_city( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_postal_code( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_phone( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_state( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_country( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_county( self.rand_text(self.SHORT))

        if issubclass(o.__class__,gen.lib.mediabase.MediaBase):
            # FIXME: frequency changed to prevent recursion
            while randint(0,10) == 1:
                o.add_media_reference( self.fill_object( gen.lib.MediaRef()))

        if isinstance(o,gen.lib.MediaObject):
            if randint(0,3) == 1:
                o.set_description(unicode(self.rand_text(self.LONG)))
                path = choice((const.ICON, const.LOGO, const.SPLASH))
                o.set_path(unicode(path))
                mime = gen.mime.get_type(path)
                o.set_mime_type(mime)
            else:
                o.set_description(unicode(self.rand_text(self.SHORT)))
                o.set_path(unicode(const.ICON))
                o.set_mime_type("image/png")

        if isinstance(o,gen.lib.MediaRef):
            if not self.generated_media or randint(0,10) == 1:
                m = gen.lib.MediaObject()
                self.fill_object(m)
                self.db.add_object( m, self.trans)
                self.generated_media.append( m.get_handle())
            o.set_reference_handle( choice( self.generated_media))
            if randint(0,1) == 1:
                o.set_rectangle( (randint(0,200),randint(0,200),randint(0,200),randint(0,200)))
        
        if isinstance(o,gen.lib.Name):
            o.set_type( self.rand_type( gen.lib.NameType()))
            if randint(0,1) == 1:
                o.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                patronymic = gen.lib.Surname()
                patronymic.set_surname(self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(gen.lib.NameOriginType.PATRONYMIC)
                o.add_surname(patronymic)
            if randint(0,1) == 1:
                o.get_primary_surname().set_prefix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_suffix( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                o.set_call_name( self.rand_text(self.FIRSTNAME))
            if randint(0,1) == 1:
                o.set_group_as( o.get_surname()[:1])
            # o.set_display_as()
            # o.set_sort_as()

        if isinstance(o,gen.lib.Note):
            type = self.rand_type(gen.lib.NoteType())
            if type == gen.lib.NoteType.HTML_CODE:
                o.set( self.rand_text(self.NOTE))
            else:
                o.set_styledtext(self.rand_text(self.STYLED_TEXT))
            o.set_format( choice( (gen.lib.Note.FLOWED,gen.lib.Note.FORMATTED)))
            o.set_type(type)

        if issubclass(o.__class__,gen.lib.notebase.NoteBase):
            while randint(0,1) == 1:
                if not self.generated_notes or randint(0,10) == 1:
                    n = gen.lib.Note()
                    self.fill_object(n)
                    self.db.add_note( n, self.trans)
                    self.generated_notes.append( n.get_handle())
                n_h = choice(self.generated_notes)
                o.add_note(n_h)
        
        if isinstance(o,gen.lib.Place):
            o.set_title( self.rand_text(self.SHORT))
            if randint(0,1) == 1:
                if randint(0,4) == 1:
                    o.set_longitude( self.rand_text(self.SHORT))
                else:
                    o.set_longitude( str(random()*360.0-180.0))
            if randint(0,1) == 1:
                if randint(0,4) == 1:
                    o.set_latitude( self.rand_text(self.SHORT))
                else:
                    o.set_latitude( str(random()*180.0-90.0))
            o.set_main_location( self.fill_object( gen.lib.Location()))
            while randint(0,1) == 1:
                o.add_alternate_locations( self.fill_object( gen.lib.Location()))

        if issubclass(o.__class__,gen.lib.placebase.PlaceBase):
            if randint(0,1) == 1:
                o.set_place_handle( self.rand_place())

        if issubclass(o.__class__,gen.lib.primaryobj.BasicPrimaryObject):
            if randint(0,1) == 1:
                o.set_gramps_id( self.rand_text(self.SHORT))

        if issubclass(o.__class__,gen.lib.privacybase.PrivacyBase):
            o.set_privacy( randint(0,5) == 1)
            
        if isinstance(o,gen.lib.RepoRef):
            if not self.generated_repos or randint(0,10) == 1:
                r = gen.lib.Repository()
                self.fill_object(r)
                self.db.add_repository( r, self.trans)
                self.generated_repos.append(r.get_handle())
            o.set_reference_handle( choice( self.generated_repos))
            if randint(0,1) == 1:
                o.set_call_number( self.rand_text(self.SHORT))
            o.set_media_type( self.rand_type(gen.lib.SourceMediaType()))

        if isinstance(o,gen.lib.Repository):
            o.set_type( self.rand_type(gen.lib.RepositoryType()))
            o.set_name( self.rand_text(self.SHORT))

        if isinstance(o,gen.lib.Source):
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
                r = gen.lib.RepoRef()
                self.fill_object(r)
                o.add_repo_reference( r)

        if issubclass(o.__class__,gen.lib.citationbase.CitationBase):
            while randint(0,1) == 1:
                if not self.generated_citations or randint(1,10) == 1:
                    s = gen.lib.Citation()
                    self.fill_object(s)
                    self.db.add_citation( s, self.trans)
                    self.generated_citations.append(s.get_handle())
                s_h = choice(self.generated_citations)
                o.add_citation(s_h)

        if isinstance(o,gen.lib.Citation):
            if not self.generated_sources or randint(0,10) == 1:
                s = gen.lib.Source()
                self.fill_object(s)
                self.db.add_source( s, self.trans)
                self.generated_sources.append( s.get_handle())
            o.set_reference_handle( choice( self.generated_sources))
            if randint(0,1) == 1:
                o.set_page( self.rand_text(self.NUMERIC))
            #if randint(0,1) == 1:
            #    o.set_text( self.rand_text(self.SHORT))
            #if randint(0,1) == 1:
            #    (year, d) = self.rand_date( )
            #    o.set_date_object( d)
            o.set_confidence_level(choice(Utils.confidence.keys()))

        if issubclass(o.__class__,gen.lib.tagbase.TagBase):
            if randint(0,1) == 1:
                o.set_tag_list(self.rand_tags())

        if issubclass(o.__class__,gen.lib.urlbase.UrlBase):
            while randint(0,1) == 1:
                u = gen.lib.Url()
                self.fill_object(u)
                o.add_url(u)
        
        if isinstance(o,gen.lib.Url):
            o.set_path("http://www.gramps-project.org/?test=%s" % self.rand_text(self.SHORT))
            o.set_description( self.rand_text(self.SHORT))
            o.set_type( self.rand_type(gen.lib.UrlType()))

        return o

    def rand_personal_event( self, type=None, start=None, end=None):
        if type:
            typeval = gen.lib.EventType(type)
        else:
            typeval = self.rand_type(gen.lib.EventType())
        return self._rand_event( typeval, start, end)
        
    def rand_family_event( self, type=None, start=None, end=None):
        if type:
            typeval = gen.lib.EventType(type)
        else:
            typeval = gen.lib.EventType.UNKNOWN
            while int(typeval) not in self.FAMILY_EVENTS:
                typeval = self.rand_type(gen.lib.EventType())
        return self._rand_event( typeval, start, end)
    
    def _rand_event( self, type, start, end):
        e = gen.lib.Event()
        self.fill_object(e)
        e.set_type( type)
        (year, d) = self.rand_date( start, end)
        e.set_date_object( d)
        event_h = self.db.add_event(e, self.trans)
        self.generated_events.append(event_h)
        event_ref = gen.lib.EventRef()
        self.fill_object(event_ref)
        event_ref.set_reference_handle(event_h)
        return (year, event_ref)
    
    def rand_type( self, list):
        if issubclass( list.__class__, gen.lib.GrampsType):
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
            place = gen.lib.Place()
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

        if type == self.STYLED_TEXT:
            result = StyledText("")
        else:
            result = ""
        
        if self.options.handler.options_dict['specialchars']:
            result = result + u"ä<ö&ü%ß'\""

        if self.options.handler.options_dict['add_serial'] and type <> self.TAG:
            result = result + "#+#%06d#-#" % self.text_serial_number
            self.text_serial_number = self.text_serial_number + 1
        
        if not type:
            type = self.SHORT
            
        if type == self.SHORT or type == self.TAG:
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

        if type == self.NOTE or type == self.STYLED_TEXT:
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
            if randint(0,3) == 1:
                word = word.title()
            if type == self.NOTE:
                if randint(0,10) == 1:
                    word = "<b>%s</b>" % word
                elif randint(0,10) == 1:
                    word = "<i>%s</i>" % word
                elif randint(0,10) == 1:
                    word = "<i>%s</i>" % word
                if randint(0,20) == 1:
                    word = word + "."
                elif randint(0,30) == 1:
                    word = word + ".\n"
            if type == self.STYLED_TEXT:
                tags = []
                if randint(0,10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.BOLD, True,
                                                [(0, len(word))])]
                elif randint(0,10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.ITALIC, True,
                                                [(0, len(word))])]
                elif randint(0,10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.UNDERLINE, True,
                                                [(0, len(word))])]
                word = StyledText(word, tags)
                if randint(0,20) == 1:
                    word = word + "."
                elif randint(0,30) == 1:
                    word = word + ".\n"
            if type == self.STYLED_TEXT:
                result = StyledText("").join((result, word))
            else:
                result += word
        
        if type == self.LASTNAME:
            n = randint(0,2)
            if n == 0:
                result = result.title()
            elif n == 1:
                result = result.upper()

        if self.options.handler.options_dict['add_linebreak'] and \
                type <> self.TAG:
            result = result + u"\nNEWLINE"

        return result
    
    def rand_color(self):
        return '#%012X' % randint(0, 281474976710655)

    def rand_tags(self):
        maxtags = 5
        taglist = []
        for counter in range(0, randint(1, maxtags)):
            tag = choice(self.generated_tags)
            if tag not in taglist:
                taglist.append(tag)
        return taglist

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TestcaseGeneratorOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'lowlevel'      : 0,
            'bugs'          : 0,
            'persons'       : 1,
            'person_count'  : 2000,
            'long_names'    : 0,
            'specialchars'  : 0,
            'add_serial'    : 0,
            'add_linebreak' : 0,
        }
        self.options_help = {
            'lowlevel'      : ("=0/1",
                                "Whether to create low level database errors.",
                                ["Skip test","Create low level database errors"],
                                True),
            'bugs'          : ("=0/1",
                                "Whether to create invalid database references.",
                                ["Skip test","Create invalid Database references"],
                                True),
            'persons'       : ("=0/1",
                                "Whether to create a bunch of dummy persons",
                                ["Dont create persons","Create dummy persons"],
                                True),
            'person_count'  : ("=int",
                                "Number of dummy persons to generate",
                                "Number of persons"),
            'long_names'    : ("=0/1",
                                "Whether to create short or long names",
                                ["Short names","Long names"],
                                True),
            'specialchars'    : ("=0/1",
                                "Whether to ass some special characters to every text field",
                                ["No special characters","Add special characters"],
                                True),
            'add_serial'    : ("=0/1",
                                "Whether to add a serial number to every text field",
                                ["No serial","Add serial number"],
                                True),
            'add_linebreak' : ("=0/1",
                                "Whether to add a line break to every text field",
                                ["No linebreak","Add line break"],
                                True),
        }
