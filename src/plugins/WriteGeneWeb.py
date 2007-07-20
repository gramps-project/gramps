#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2004-2006 Donald N. Allingham
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

"Export to GeneWeb"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WriteGeneWeb")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
from Filters import GenericFilter, Rules, build_filter_menu
import const
import Utils
import Errors
from QuestionDialog import ErrorDialog
from PluginUtils import register_export

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GeneWebWriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self,person):
        self.person = person

    def get_option_box(self):
        self.restrict = 1
        self.private = 1

        glade_file = "%s/genewebexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/genewebexport.glade"

        self.topDialog = gtk.glade.XML(glade_file,"genewebExport","gramps")
        self.topDialog.signal_autoconnect({
                "on_restrict_toggled": self.on_restrict_toggled
                })

        filter_obj = self.topDialog.get_widget("filter")
        self.copy = 0

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        the_filters = [all]

        if self.person:
            des = GenericFilter()
            des.set_name(_("Descendants of %s") %
                         self.person.get_primary_name().get_name())
            des.add_rule(Rules.Person.IsDescendantOf(
                [self.person.get_gramps_id(),1]))

            ans = GenericFilter()
            ans.set_name(_("Ancestors of %s") %
                         self.person.get_primary_name().get_name())
            ans.add_rule(Rules.Person.IsAncestorOf(
                [self.person.get_gramps_id(),1]))

            com = GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         self.person.get_primary_name().get_name())
            com.add_rule(Rules.Person.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))

            the_filters += [all,des,ans,com]

        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))
        self.filter_menu = build_filter_menu(the_filters)
        filter_obj.set_menu(self.filter_menu)

        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("genewebExport").destroy()
        return the_box

    def on_restrict_toggled(self,restrict):
        active = restrict.get_active ()
        map (lambda x: x.set_sensitive (active),
             [self.topDialog.get_widget("living"),
              self.topDialog.get_widget("notes"),
              self.topDialog.get_widget("sources")])

    def parse_options(self):
        self.restrict = self.topDialog.get_widget("restrict").get_active()
        self.living = (self.restrict and
                       self.topDialog.get_widget("living").get_active())
        self.exclnotes = (self.restrict and
                          self.topDialog.get_widget("notes").get_active())
        self.exclsrcs = (self.restrict and
                         self.topDialog.get_widget("sources").get_active())
        self.private = self.topDialog.get_widget("private").get_active()

        self.cfilter = self.filter_menu.get_active().get_data("filter")

        self.images = self.topDialog.get_widget ("images").get_active ()
        if self.images:
            images_path = self.topDialog.get_widget ("images_path")
            self.images_path = unicode(images_path.get_text ())
        else:
            self.images_path = ""

class GeneWebWriter:
    def __init__(self,database,person,cl=0,filename="",
                 option_box=None,callback=None):
        self.db = database
        self.person = person
        self.option_box = option_box
        self.cl = cl
        self.filename = filename
        self.callback = callback
        if '__call__' in dir(self.callback): # callback is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        self.plist = {}
        self.flist = {}
        
        self.persons_details_done = []
        self.persons_notes_done = []
        self.person_ids = {}
        
        if not option_box:
            self.cl_setup()
        else:
            self.option_box.parse_options()

            self.restrict = self.option_box.restrict
            self.living = self.option_box.living
            self.exclnotes = self.option_box.exclnotes
            self.exclsrcs = self.option_box.exclsrcs
            self.private = self.option_box.private
            self.copy = self.option_box.copy
            self.images = self.option_box.images
            self.images_path = self.option_box.images_path
            
            if self.option_box.cfilter == None:
                for p in self.db.get_person_handles(sort_handles=False):
                    self.plist[p] = 1
            else:
                try:
                    for p in self.option_box.cfilter.apply(self.db, self.db.get_person_handles(sort_handles=False)):
                        self.plist[p] = 1
                except Errors.FilterError, msg:
                    (m1,m2) = msg.messages()
                    ErrorDialog(m1,m2)
                    return

            self.flist = {}
            for key in self.plist:
                p = self.db.get_person_from_handle(key)
                for family_handle in p.get_family_handle_list():
                    self.flist[family_handle] = 1

        # remove families that dont contain father AND mother
        # because GeneWeb requires both to be present
        templist = self.flist
        self.flist = {}
        for family_handle in templist:
            family = self.db.get_family_from_handle(family_handle)
            if family:
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                if father_handle and mother_handle:
                    self.flist[family_handle] = 1


    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100*self.count/self.total)
        if newval != self.oldval:
            self.callback(newval)
            self.oldval = newval

    def cl_setup(self):
        self.restrict = 0
        self.private = 0
        self.copy = 0
        self.images = 0

        for p in self.db.get_person_handles(sort_handles=False):
            self.plist[p] = 1

        self.flist = {}

        for key in self.plist:
            p = self.db.get_person_from_handle(key)
            for family_handle in p.get_family_handle_list():
                self.flist[family_handle] = 1

    def writeln(self,text):
        self.g.write(self.iso8859('%s\n' % (text)))

    def export_data(self):

        self.dirname = os.path.dirname (self.filename)
        try:
            self.g = open(self.filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % self.filename
            ErrorDialog(msg2,str(msg))
            return 0
        except:
            ErrorDialog(_("Could not create %s") % self.filename)
            return 0

        if len(self.flist) < 1:
            ErrorDialog(_("No families matched by selected filter"))
            return 0
        
        self.count = 0
        self.oldval = 0
        self.total = len(self.flist)
        for key in self.flist:
            self.write_family(key)
            self.writeln("")
        
        self.g.close()
        return 1
    
    def write_family(self,family_handle):
        family = self.db.get_family_from_handle(family_handle)
        if family:
            self.update()
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.db.get_person_from_handle(father_handle)
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                    self.writeln("fam %s %s +%s %s %s" % (self.get_ref_name(father), self.get_full_person_info_fam(father), self.get_wedding_data(family), self.get_ref_name(mother), self.get_full_person_info_fam(mother)))
                    self.write_witness( family)
                    self.write_sources( family.get_source_references())
                    self.write_children( family, father)
                    self.write_notes( family, father, mother)
                    if not (self.restrict and self.exclnotes):
                        notelist = family.get_note_list()
                        note = ""
                        for notehandle in notelist:
                            noteobj = self.db.get_note_from_handle(notehandle)
                            note += noteobj.get(False)
                            note += " "
                        if note and note != "":
                            note = note.replace('\n\r',' ')
                            note = note.replace('\r\n',' ')
                            note = note.replace('\n',' ')
                            note = note.replace('\r',' ')
                            self.writeln("comm %s" % note)
                    
    def write_witness(self,family):
        # FIXME: witnesses are not in events anymore
        return
        
        if self.restrict:
            return
        event_ref_list = family.get_event_ref_list()
        for event_ref in event_ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if int(event.get_type()) == RelLib.EventType.MARRIAGE:
                w_list = event.get_witness_list()
                if w_list:
                    for witness in w_list:
                        if witness and witness.type == RelLib.Event.ID:
                            person = self.db.get_person_from_handle(witness.get_value())
                            if person:
                                gender = ""
                                if person.get_gender() == RelLib.Person.MALE:
                                    gender = "h"
                                elif person.get_gender() == RelLib.Person.FEMALE:
                                    gender = "f"
                                self.writeln("wit %s %s %s" % (gender, self.get_ref_name(person), self.get_full_person_info_fam(person)))
                            

    def write_sources(self,reflist):
        if self.restrict and self.exclnotes:
            return
            
        if reflist:
           for sr in reflist:
                sbase = sr.get_reference_handle()
                if sbase:
                    source = self.db.get_source_from_handle(sbase)
                    if source:
                        self.writeln( "src %s" % (self.rem_spaces(source.get_title())))

    def write_children(self,family, father):
        father_lastname = father.get_primary_name().get_surname()
        child_ref_list = family.get_child_ref_list()
        if child_ref_list:
            self.writeln("beg")
            for child_ref in child_ref_list:
                child = self.db.get_person_from_handle(child_ref.ref)
                if child:
                    gender = ""
                    if child.get_gender() == RelLib.Person.MALE:
                        gender = "h"
                    elif child.get_gender() == RelLib.Person.FEMALE:
                        gender = "f"
                    self.writeln("- %s %s %s" % (gender, self.get_child_ref_name(child, father_lastname), self.get_full_person_info_child(child)))
            self.writeln("end")

    def write_notes(self,family, father, mother):
        if self.restrict and self.exclnotes:
            return
            
        self.write_note_of_person(father)
        self.write_note_of_person(mother)
        child_ref_list = family.get_child_ref_list()
        if child_ref_list:
            for child_ref in child_ref_list:
                child = self.db.get_person_from_handle(child_ref.ref)
                if child:
                    self.write_note_of_person(child)
        # FIXME: witnesses do not exist in events anymore
##         event_ref_list = family.get_event_ref_list()
##         for event_ref in event_ref_list:
##             event = self.db.get_event_from_handle(event_ref.ref)
##             if int(event.get_type()) == RelLib.EventType.MARRIAGE:
##                 w_list = event.get_witness_list()
##                 if w_list:
##                     for witness in w_list:
##                         if witness and witness.type == RelLib.Event.ID:
##                             person = self.db.get_person_from_handle(witness.get_value())
##                             if person:
##                                 self.write_note_of_person(person)

    def write_note_of_person(self,person):
        if self.persons_notes_done.count(person.get_handle()) == 0:
            self.persons_notes_done.append(person.get_handle())
            
            notelist = person.get_note_list()
            note = ""
            for notehandle in notelist:
                noteobj = self.db.get_note_from_handle(notehandle)
                note += noteobj.get(False)
                note += " "

            if note and note != "":
                self.writeln("")
                self.writeln("notes %s" % self.get_ref_name(person))
                self.writeln("beg")
                self.writeln(note)
                self.writeln("end notes")
    
    def get_full_person_info(self, person):
        if self.restrict:
            return "0 "
            
        retval = ""

        b_date = "0"
        b_place = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
            if birth:
                b_date = self.format_date( birth.get_date_object())
                place_handle = birth.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    b_place = place.get_title()
        
        if Utils.probably_alive(person,self.db):
            d_date = ""
        else:
            d_date = "0"
        d_place = ""
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.db.get_event_from_handle(death_ref.ref)
            if death:
                d_date = self.format_date( death.get_date_object())
                place_handle = death.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    d_place = place.get_title()
            
        retval = retval + "%s " % b_date
        if b_place != "":
            retval = retval + "#bp %s " % self.rem_spaces(b_place)
        retval = retval + "%s " % d_date
        if d_place != "":
            retval = retval + "#dp %s " % self.rem_spaces(d_place)
        return retval

    def get_full_person_info_fam(self, person):
        """Output full person data of a family member only if the person is not listed as a child"""
        retval = ""
        if self.persons_details_done.count(person.get_handle()) == 0:
            is_child = 0
            pf_list = person.get_parent_family_handle_list()
            if pf_list:
                for family_handle in pf_list:
                    if self.flist.has_key(family_handle):
                        is_child = 1
            if is_child == 0:
                self.persons_details_done.append(person.get_handle())
                retval = self.get_full_person_info(person)
        return retval
                    

    def get_full_person_info_child(self, person):
        """Output full person data for a child, if not printed somewhere else"""
        retval = ""
        if self.persons_details_done.count(person.get_handle()) == 0:
            self.persons_details_done.append(person.get_handle())
            retval = self.get_full_person_info(person)
        return retval

    def rem_spaces(self,str):
        return str.replace(' ','_')
    
    def get_ref_name(self,person):
        surname = self.rem_spaces( person.get_primary_name().get_surname())
        firstname = "Living"
        if not (Utils.probably_alive(person,self.db) and self.restrict and self.living):
            firstname = self.rem_spaces( person.get_primary_name().get_first_name())
        if not self.person_ids.has_key(person.get_handle()):
            self.person_ids[person.get_handle()] = len(self.person_ids)
        ret = "%s %s.%d" % (surname, firstname, self.person_ids[person.get_handle()])
        return ret

    def get_child_ref_name(self,person,father_lastname):
        surname = self.rem_spaces( person.get_primary_name().get_surname())
        firstname = "Living"
        if not (Utils.probably_alive(person,self.db) and self.restrict and self.living):
            firstname = self.rem_spaces( person.get_primary_name().get_first_name())
        if not self.person_ids.has_key(person.get_handle()):
            self.person_ids[person.get_handle()] = len(self.person_ids)
        if surname != father_lastname:
            ret = "%s.%d %s" % (firstname, self.person_ids[person.get_handle()], surname)
        else:
            ret = "%s.%d" % (firstname, self.person_ids[person.get_handle()])
        return ret

    def get_wedding_data(self,family):
        ret = "";
        event_ref_list = family.get_event_ref_list()
        m_date = ""
        m_place = ""
        m_source = ""
        married = 0
        eng_date = ""
        eng_place = ""
        eng_source = ""
        engaged = 0
        div_date = ""
        divorced = 0
        for event_ref in event_ref_list:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event.get_type() == RelLib.EventType.MARRIAGE:
                married = 1
                m_date = self.format_date( event.get_date_object())
                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    m_place = place.get_title()
                m_source = self.get_primary_source( event.get_source_references())
            if event.get_type() == RelLib.EventType.ENGAGEMENT:
                engaged = 1
                eng_date = self.format_date( event.get_date_object())
                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    eng_place = place.get_title()
                eng_source = self.get_primary_source( event.get_source_references())
            if event.get_type() == RelLib.EventType.DIVORCE:
                divorced = 1
                div_date = self.format_date( event.get_date_object())
        if married == 1:
            if m_date != "":
                ret = ret + m_date
            ret = ret + " "
            
            if m_place != "":
                ret = ret + "#mp %s " % self.rem_spaces( m_place)
            
            if m_source != "":
                ret = ret + "#ms %s " % self.rem_spaces( m_source)
        elif engaged == 1:
            """Geneweb only supports either Marriage or engagement"""
            if eng_date != "":
                ret = ret + eng_date
            ret = ret + " "
            
            if eng_place != "":
                ret = ret + "#mp %s " % self.rem_spaces( m_place)
            
            if eng_source != "":
                ret = ret + "#ms %s " % self.rem_spaces( m_source)
        else:
            if family.get_relationship() != RelLib.FamilyRelType.MARRIED:
                """Not married or engaged"""
                ret = ret + " #nm "

        if divorced == 1:
            if div_date != "":
                ret = ret + "-%s " %div_date
            else:
                ret = ret + "-0 "

        return ret

    def get_primary_source(self,reflist):
        ret = ""
        if reflist:
            for sr in reflist:
                sbase = sr.get_reference_handle()
                if sbase:
                    source = self.db.get_source_from_handle(sbase)
                    if source:
                        if ret != "":
                            ret = ret + ", "
                        ret = ret + source.get_title()
        return ret
    
    def format_single_date(self,subdate,cal,mode):
        retval = ""
        (day,month,year,sl) = subdate
        
        cal_type = ""
        if cal == RelLib.Date.CAL_HEBREW:
            cal_type = "H"
        elif cal == RelLib.Date.CAL_FRENCH:
            cal_type = "F"
        elif cal == RelLib.Date.CAL_JULIAN:
            cal_type = "J"
        
        mode_prefix = ""
        if mode == RelLib.Date.MOD_ABOUT:
            mode_prefix = "~"
        elif mode == RelLib.Date.MOD_BEFORE:
            mode_prefix = "<"
        elif mode == RelLib.Date.MOD_AFTER:
            mode_prefix = ">"
            
        if year > 0:
            if month > 0:
                if day > 0:
                    retval = "%s%s/%s/%s%s" % (mode_prefix,day,month,year,cal_type)
                else:
                    retval = "%s%s/%s%s" % (mode_prefix,month,year,cal_type)
            else:
                retval = "%s%s%s" % (mode_prefix,year,cal_type)
        return retval

    
    def format_date(self,date):
        retval = ""
        
        strval = date.get_text()
        if strval:
            retval = "0(%s)" % self.rem_spaces(strval)
        elif not date.is_empty():
            mod = date.get_modifier()
            cal = cal = date.get_calendar()
            if mod == RelLib.Date.MOD_SPAN or mod == RelLib.Date.MOD_RANGE:
                retval = "%s..%s" % (
                    self.format_single_date(date.get_start_date(), cal,mod),
                    self.format_single_date(date.get_stop_date(),cal,mod))
            else:
                retval = self.format_single_date(date.get_start_date(),cal,mod)
        return retval

    def iso8859(self,s):
        return s.encode('iso-8859-1','xmlcharrefreplace')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database,filename,person,option_box,callback=None):
    ret = 0
    gw = GeneWebWriter(database,person,0,filename,option_box,callback)
    ret = gw.export_data()
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('G_eneWeb')
_description = _('GeneWeb is a web based genealogy program.')
_config = (_('GeneWeb export options'),GeneWebWriterOptionBox)
_filename = 'gw'

register_export(exportData,_title,_description,_config,_filename)
