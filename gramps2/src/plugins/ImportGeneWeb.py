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

"Import from GeneWeb"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import re
import time
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ImportGeneWeb")

#-------------------------------------------------------------------------
#
# GTK/GNOME Modules
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
import const
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp
from PluginUtils import register_import
from htmlentitydefs import name2codepoint

_date_parse = re.compile('([kmes~?<>]+)?([0-9/]+)([J|H|F])?(\.\.)?([0-9/]+)?([J|H|F])?')
_text_parse = re.compile('0\((.*)\)')

_mod_map = {
    '>' : RelLib.Date.MOD_AFTER,
    '<' : RelLib.Date.MOD_BEFORE,
    '~' : RelLib.Date.MOD_ABOUT,
    }

_cal_map = {
    'J' : RelLib.Date.CAL_JULIAN,
    'H' : RelLib.Date.CAL_HEBREW,
    'F' : RelLib.Date.CAL_FRENCH,
    }

enable_debug = False

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def importData(database, filename, cb=None):

    global callback

    try:
        g = GeneWebParser(database,filename)
    except IOError,msg:
        ErrorDialog(_("%s could not be opened\n") % filename,str(msg))
        return

    try:
        status = g.parse_geneweb_file()
    except IOError,msg:
        errmsg = _("%s could not be opened\n") % filename
        ErrorDialog(errmsg,str(msg))
        return

#-------------------------------------------------------------------------
# For a description of the file format see
# http://cristal.inria.fr/~ddr/GeneWeb/en/gwformat.htm
#-------------------------------------------------------------------------
class GeneWebParser:
    def __init__(self, dbase, file):
        self.db = dbase
        self.f = open(file,"rU")
        self.filename = file

    def get_next_line(self):
        self.lineno += 1
        line = self.f.readline()
        if line:
            try:
                line = unicode(line.strip())
            except UnicodeDecodeError:
                line = unicode(line.strip(),'iso-8859-1')
        else:
            line = None
        return line
        
    def parse_geneweb_file(self):
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        t = time.time()
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        
        self.fkeys = []
        self.ikeys = {}
        self.pkeys = {}
        self.skeys = {}
        
        self.current_mode = None
        self.current_family = None
        self.current_husband_handle = None
        self.current_child_birthplace_handle = None
        self.current_child_source_handle = None
        try:
            while 1:
                line = self.get_next_line()
                if line == None:
                    break
                if line == "":
                    continue
                
                fields = line.split(" ")
            
                self.debug("LINE: %s" %line)
                if fields[0] == "fam":
                    self.current_mode = "fam"
                    self.read_family_line(line,fields)
                elif fields[0] == "rel":
                    self.current_mode = "rel"
                    self.read_relationship_person(line,fields)
                elif fields[0] == "src":
                    self.read_source_line(line,fields)
                elif fields[0] == "wit":
                    self.read_witness_line(line,fields)
                elif fields[0] == "cbp":
                    self.read_children_birthplace_line(line,fields)
                elif fields[0] == "csrc":
                    self.read_children_source_line(line,fields)
                elif fields[0] == "beg" and self.current_mode == "fam":
                    self.read_children_lines()
                elif fields[0] == "beg" and self.current_mode == "rel":
                    self.read_relation_lines()
                elif fields[0] == "comm":
                    self.read_family_comment(line,fields)
                elif fields[0] == "notes":
                    self.read_notes_lines(line,fields)
                elif fields[0] == "end":
                    self.current_mode = None
                else:
                    print "parse_geneweb_file(): Token >%s< unknown. line %d skipped: %s" % (fields[0],self.lineno,line)
        except Errors.GedcomError, err:
            self.errmsg(str(err))
            
        t = time.time() - t
        msg = _('Import Complete: %d seconds') % t

        self.db.transaction_commit(self.trans,_("GeneWeb import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        
        print msg
        print "Families: %d" % len(self.fkeys)
        print "Individuals: %d" % len(self.ikeys)
        return None

    def read_family_line(self,line,fields):
        self.current_husband_handle = None
        self.current_child_birthplace_handle = None
        self.current_child_source_handle = None
        self.current_family = RelLib.Family()
        self.db.add_family(self.current_family,self.trans)
        #self.db.commit_family(self.current_family,self.trans)
        self.fkeys.append(self.current_family.get_handle())
        idx = 1;
        
        self.debug("\nHusband:")
        (idx,husband) = self.parse_person(fields,idx,RelLib.Person.MALE,None)
        if husband:
            self.current_husband_handle = husband.get_handle()
            self.current_family.set_father_handle(husband.get_handle())
            self.db.commit_family(self.current_family,self.trans)
            husband.add_family_handle(self.current_family.get_handle())
            self.db.commit_person(husband,self.trans)
        self.debug("Marriage:")
        idx = self.parse_marriage(fields,idx)
        self.debug("Wife:")
        (idx,wife) = self.parse_person(fields,idx,RelLib.Person.FEMALE,None)
        if wife:
            self.current_family.set_mother_handle(wife.get_handle())
            self.db.commit_family(self.current_family,self.trans)
            wife.add_family_handle(self.current_family.get_handle())
            self.db.commit_person(wife,self.trans)
        return None

    def read_relationship_person(self,line,fields):
        self.debug("\Relationships:")
        (idx,person) = self.parse_person(fields,1,RelLib.Person.UNKNOWN,None)
        if person:
            self.current_relationship_person_handle = person.get_handle()

    def read_relation_lines(self):
        if not self.current_relationship_person_handle:
            print "Unknown person for relationship in line %d!" % self.lineno
            return None
        rel_person = self.db.get_person_from_handle(self.current_relationship_person_handle)
        while 1:
            line = self.get_next_line()
            if line == None or line == "end":
                break
            if line == "":
                continue

            # match relationship type and related person
            line_re = re.compile("^- ([^:]+): (.*)$")
            matches = line_re.match(line)
            if matches:
                #split related person into fields
                fields = matches.groups()[1].split(" ")
                if fields:
                    (idx,asso_p) = self.parse_person(fields,0,RelLib.Person.UNKNOWN,None)
                    pref = RelLib.PersonRef()
                    pref.set_relation(matches.groups()[0])
                    print("TODO: Handle association types properly")
                    pref.set_reference_handle(asso_p.get_handle())
                    rel_person.add_person_ref(pref)
                    self.db.commit_person(rel_person,self.trans)
                else:
                    print "Invalid name of person in line %d" % self.lineno
            else:
                print "Invalid relationship in line %d" % self.lineno
                break
        self.current_mode = None
        return None



    def read_source_line(self,line,fields):
        if not self.current_family:
            print "Unknown family of child in line %d!" % self.lineno
            return None
        source = self.get_or_create_source(self.decode(fields[1]))
        self.current_family.add_source_reference(source)
        self.db.commit_family(self.current_family,self.trans)
        return None
    
    def read_witness_line(self,line,fields):
        self.debug("Witness:")
        if fields[1] == "m:":
            (idx,wit_p) = self.parse_person(fields,2,RelLib.Person.MALE,None)
        elif fields[1] == "f:":
            (idx,wit_p) = self.parse_person(fields,2,RelLib.Person.FEMALE,None)
        else:
            (idx,wit_p) = self.parse_person(fields,1,None,None)
        if wit_p:
            mev = None
            # search marriage event
            for evr in self.current_family.get_event_ref_list():
                ev = self.db.get_event_from_handle(evr.get_reference_handle())
                if ev.get_type() == RelLib.EventType.MARRIAGE:
                    mev = ev # found.
            if not mev: # No marriage event found create a new one
                mev = self.create_event(RelLib.EventType.MARRIAGE, None, None, None, None)
                mar_ref = RelLib.EventRef()
                mar_ref.set_reference_handle(mev.get_handle())
                self.current_family.add_event_ref(mar_ref)
            wit_ref = RelLib.EventRef()
            wit_ref.set_role(RelLib.EventRoleType(RelLib.EventRoleType.WITNESS))
            wit_ref.set_reference_handle(mev.get_handle())
            wit_p.add_event_ref(wit_ref)
            self.db.commit_person(wit_p,self.trans)
        return None

    def read_children_lines(self):
        father_surname = "Dummy"
        if not self.current_husband_handle:
            print "Unknown father for child in line %d!" % self.lineno
            return None
        husb = self.db.get_person_from_handle(self.current_husband_handle)
        father_surname = husb.get_primary_name().get_surname()
        if not self.current_family:
            print "Unknown family of child in line %d!" % self.lineno
            return None
        while 1:
            line = self.get_next_line()
            if line == None:
                break
            if line == "":
                continue

            fields = line.split(" ")
            if fields[0] == "-":
                self.debug("Child:")
                child = None
                if fields[1] == "h":
                    (idx,child) = self.parse_person(fields,2,RelLib.Person.MALE,father_surname)
                elif fields[1] == "f":
                    (idx,child) = self.parse_person(fields,2,RelLib.Person.FEMALE,father_surname)
                else:
                    (idx,child) = self.parse_person(fields,1,RelLib.Person.UNKNOWN,father_surname)

                if child:
                    childref = RelLib.ChildRef()
                    childref.set_reference_handle(child.get_handle())
                    self.current_family.add_child_ref( childref)
                    self.db.commit_family(self.current_family,self.trans)
                    child.add_parent_family_handle( self.current_family.get_handle())
                    if self.current_child_birthplace_handle:
                        birth = None
                        birth_ref = child.get_birth_ref()
                        if birth_ref:
                            birth = self.db.get_event_from_handle(birth_ref.ref)
                        if not birth:
                            birth = self.create_event(RelLib.EventType.BIRTH)
                            birth_ref = RelLib.EventRef()
                            birth_ref.set_reference_handle(birth.get_handle())
                            child.set_birth_ref(birth_ref)
                        birth.set_place_handle(self.current_child_birthplace_handle)
                        self.db.commit_event(birth,self.trans)
                    if self.current_child_source_handle:
                        child.add_source_reference(self.current_child_source_handle)
                    self.db.commit_person(child,self.trans)
            else:
                break
        self.current_mode = None
        return None
            

    def read_children_birthplace_line(self,line,fields):
        cbp = self.get_or_create_place(self.decode(fields[1]))
        if cbp:
            self.current_child_birthplace_handle = cbp.get_handle()
        return None

    def read_children_source_line(self,line,fields):
        csrc = self.get_or_create_source(self.decode(fields[1]))
        self.current_child_source_handle = csrc
        return None

    def read_family_comment(self,line,fields):
        if not self.current_family:
            print "Unknown family of child in line %d!" % self.lineno
            return None
        self.current_family.set_note(line)
        self.db.commit_family(self.current_family,self.trans)
        return None

    def read_notes_lines(self,line,fields):
        (idx,person) = self.parse_person(fields,1,None,None)
        note_txt = ""
        while True:
            line = self.get_next_line()
            if line == None:
                break

            fields = line.split(" ")
            if fields[0] == "end" and fields[1] == "notes":
                break
            elif fields[0] == "beg":
                continue
            else:
                if note_txt:
                    note_txt = note_txt + "\n" + line
                else:
                    note_txt = note_txt + line
        if note_txt:
            person.set_note(note_txt)
            self.db.commit_person(person,self.trans)
        return None
    
    def parse_marriage(self,fields,idx):
        mariageDataRe = re.compile("^[+#-0-9].*$")

        mar_date = None
        mar_place = None
        mar_source = None

        sep_date = None
        div_date = None
        
        married = 1
        engaged = 0

        # skip to marriage date in case person contained unmatches tokens
        #Alex: this failed when fields[idx] was an empty line. Fixed.
        #while idx < len(fields) and not fields[idx][0] == "+":
        while idx < len(fields) and not (fields[idx] and fields[idx][0] == "+"):
            if fields[idx]:
                print "parse_marriage(): Unknown field: '%s' in line %d!" %(fields[idx],self.lineno)
            idx = idx + 1

        while idx < len(fields) and mariageDataRe.match(fields[idx]):
            if fields[idx][0] == "+":
                mar_date = self.parse_date(self.decode(fields[idx]))
                self.debug(" Married at: %s" % fields[idx])
                idx = idx + 1
            elif fields[idx][0] == "-":
                div_date = self.parse_date(self.decode(fields[idx]))
                self.debug(" Div at: %s" % fields[idx])
                idx = idx + 1
            elif fields[idx] == "#mp":
                idx = idx + 1
                mar_place = self.get_or_create_place(self.decode(fields[idx]))
                self.debug(" Marriage place: %s" % fields[idx])
                idx = idx + 1
            elif fields[idx] == "#ms":
                idx = idx + 1
                mar_source = self.get_or_create_source(self.decode(fields[idx]))
                self.debug(" Marriage source: %s" % fields[idx])
                idx = idx + 1
            elif fields[idx] == "#sep":
                idx = idx + 1
                sep_date = self.parse_date(self.decode(fields[idx]))
                self.debug(" Seperated since: %s" % fields[idx])
                idx = idx + 1
            elif fields[idx] == "#nm":
                self.debug(" Are not married.")
                married = 0
                idx = idx + 1
            elif fields[idx] == "#noment":
                self.debug(" Not mentioned.")
                idx = idx + 1
            elif fields[idx] == "#eng":
                self.debug(" Are engaged.")
                engaged = 1
                idx = idx + 1
            else:
                print "parse_marriage(): Unknown field '%s'for mariage in line %d!" % (fields[idx],self.lineno)
                idx = idx + 1

        if mar_date or mar_place or mar_source:
            mar = self.create_event(RelLib.EventType.MARRIAGE, None, mar_date, mar_place, mar_source)
            mar_ref = RelLib.EventRef()
            mar_ref.set_reference_handle(mar.get_handle())
            self.current_family.add_event_ref(mar_ref)

        if div_date:
            div = self.create_event(RelLib.EventType.DIVORCE, None, div_date, None, None)
            div_ref = RelLib.EventRef()
            div_ref.set_reference_handle(div.get_handle())
            self.current_family.add_event_ref(div_ref)

        if sep_date or engaged:
            sep = self.create_event(RelLib.EventType.ENGAGEMENT, None, sep_date, None, None)
            sep_ref = RelLib.EventRef()
            sep_ref.set_reference_handle(sep.get_handle())
            self.current_family.add_event_ref(sep_ref)

        if not married:
            self.current_family.set_relationship(RelLib.FamilyRelType(RelLib.FamilyRelType.UNMARRIED))
            
        self.db.commit_family(self.current_family,self.trans)
        return idx

    def parse_person(self,fields,idx,gender,father_surname):
        
        if not father_surname:
            if not idx < len(fields):
                print "Missing surname of person in line %d!" % self.lineno
                surname =""
            else:
                surname = self.decode(fields[idx])
            idx = idx + 1
        else:
            surname = father_surname
        
        if not idx < len(fields):
            print "Missing firstname of person in line %d!" % self.lineno
            firstname = ""
        else:
            firstname = self.decode(fields[idx])
        idx = idx + 1
        if idx < len(fields) and father_surname:
            noSurnameRe = re.compile("^[({\[~><?0-9#].*$")
            if not noSurnameRe.match(fields[idx]):
                surname = self.decode(fields[idx])
                idx = idx + 1

        self.debug("Person: %s %s" % (firstname, surname))
        person = self.get_or_create_person(firstname,surname)
        name = RelLib.Name()
        name.set_type( RelLib.NameType(RelLib.NameType.BIRTH))
        name.set_first_name(firstname)
        name.set_surname(surname)
        person.set_primary_name(name)
        if person.get_gender() == RelLib.Person.UNKNOWN and gender != None:
            person.set_gender(gender)
        self.db.commit_person(person,self.trans)
        personDataRe = re.compile("^[kmes0-9<>~#\[({!].*$")
        dateRe = re.compile("^[kmes0-9~<>?]+.*$")
        
        source = None
        birth_date = None
        birth_place = None
        birth_source = None

        bapt_date = None
        bapt_place = None
        bapt_source = None

        death_date = None
        death_place = None
        death_source = None
        death_cause = None

        crem_date = None
        bur_date = None
        bur_place = None
        bur_source = None
        
        public_name = None
        firstname_aliases = []
        nick_names = []
        name_aliases = []
        surname_aliases = []
        
        while idx < len(fields) and personDataRe.match(fields[idx]):
            if fields[idx][0] == '(':
                self.debug("Public Name: %s" % fields[idx])
                public_name = self.decode(fields[idx][1:-1])
                idx += 1
            elif fields[idx][0] == '{':
                self.debug("Firstsname Alias: %s" % fields[idx])
                firstname_aliases.append(self.decode(fields[idx][1:-1]))
                idx += 1
            elif fields[idx][0] == '[':
                print "TODO: Titles: %s" % fields[idx]
                idx += 1
            elif fields[idx] == '#nick':
                idx += 1
                self.debug("Nick Name: %s" % fields[idx])
                nick_names.append(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#occu':
                idx += 1
                self.debug("Occupation: %s" % fields[idx])
                occu = self.create_event(RelLib.EventType.OCCUPATION,self.decode(fields[idx]))
                occu_ref = RelLib.EventRef()
                occu_ref.set_reference_handle(occu.get_handle())
                person.add_event_ref(occu_ref)
                idx += 1
            elif fields[idx] == '#alias':
                idx += 1
                self.debug("Name Alias: %s" % fields[idx])
                name_aliases.append(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#salias':
                idx += 1
                self.debug("Surname Alias: %s" % fields[idx])
                surname_aliases.append(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#image':
                idx += 1
                self.debug("Image: %s" % fields[idx])
                idx += 1
            elif fields[idx] == '#src':
                idx += 1
                self.debug("Source: %s" % fields[idx])
                source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#bs':
                idx += 1
                self.debug("Birth Source: %s" % fields[idx])
                birth_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif fields[idx][0] == '!':
                self.debug("Baptize at: %s" % fields[idx])
                bapt_date = self.parse_date(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#bp':
                idx += 1
                self.debug("Birth Place: %s" % fields[idx])
                birth_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#pp':
                idx += 1
                self.debug("Baptize Place: %s" % fields[idx])
                bapt_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#ps':
                idx += 1
                self.debug("Baptize Source: %s" % fields[idx])
                bapt_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#dp':
                idx += 1
                self.debug("Death Place: %s" % fields[idx])
                death_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#ds':
                idx += 1
                self.debug("Death Source: %s" % fields[idx])
                death_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#buri':
                idx += 1
                self.debug("Burial Date: %s" % fields[idx])
                try:
                    bur_date = self.parse_date(self.decode(fields[idx]))
                except IndexError:
                    pass
                idx += 1
            elif fields[idx] == '#crem':
                idx += 1
                self.debug("Cremention Date: %s" % fields[idx])
                crem_date = self.parse_date(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#rp':
                idx += 1
                self.debug("Burial Place: %s" % fields[idx])
                bur_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#rs':
                idx += 1
                self.debug("Burial Source: %s" % fields[idx])
                bur_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif fields[idx] == '#apubl':
                self.debug("This is a public record")
                idx += 1
            elif fields[idx] == '#apriv':
                self.debug("This is a private record")
                person.set_privacy(True)
                idx += 1
            elif fields[idx] == '#h':
                self.debug("This is a restricted record")
                #TODO: Gramps does currently not feature this level
                person.set_privacy(True)
                idx += 1
            elif dateRe.match( fields[idx]):
                if not birth_date:
                    self.debug("Birth Date: %s" % fields[idx])
                    birth_date = self.parse_date(self.decode(fields[idx]))
                else:
                    self.debug("Death Date: %s" % fields[idx])
                    death_date = self.parse_date(self.decode(fields[idx]))
                    if fields[idx][0] == "k":
                        death_cause = "Killed"
                    elif fields[idx][0] == "m":
                        death_cause = "Murdered"
                    elif fields[idx][0] == "e":
                        death_cause = "Executed"
                    elif fields[idx][0] == "d":
                        death_cause = "Disappeared"
                    #TODO: Set special death types more properly
                idx += 1
            else:
                print "parse_person(): Unknown field '%s' for person in line %d!" % (fields[idx],self.lineno)
                idx += 1
        
        if public_name:
            name = person.get_primary_name()
            name.set_type(RelLib.NameType(RelLib.NameType.BIRTH))
            person.add_alternate_name(name)
            name = RelLib.Name()
            name.set_type(RelLib.NameType(RelLib.NameType.AKA))
            name.set_first_name(public_name)
            name.set_surname(surname)
            person.set_primary_name(name)
        
        for aka in nick_names:
            name = RelLib.Attribute()
            name.set_type(RelLib.AttributeType(RelLib.AttributeType.NICKNAME))
            name.set_value(aka)
            person.add_attribute(name)

        for aka in firstname_aliases:
            name = RelLib.Name()
            name.set_type(RelLib.NameType(RelLib.NameType.AKA))
            name.set_first_name(aka)
            name.set_surname(surname)
            person.add_alternate_name(name)

        for aka in name_aliases:
            name = RelLib.Name()
            name.set_type(RelLib.NameType(RelLib.NameType.AKA))
            name.set_first_name(aka)
            name.set_surname(surname)
            person.add_alternate_name(name)

        for aka in surname_aliases:
            name = RelLib.Name()
            name.set_type(RelLib.NameType(RelLib.NameType.AKA))
            if public_name:
                name.set_first_name(public_name)
            else:
                name.set_first_name(firstname)
            name.set_surname(aka)
            person.add_alternate_name(name)

        if source:
            person.add_source_reference(source)

        if birth_date or birth_place or birth_source:
            birth = self.create_event(RelLib.EventType.BIRTH, None, birth_date, birth_place, birth_source)
            birth_ref = RelLib.EventRef()
            birth_ref.set_reference_handle( birth.get_handle())
            person.set_birth_ref( birth_ref)

        if bapt_date or bapt_place or bapt_source:
            babt = self.create_event(RelLib.EventType.BAPTISM, None, bapt_date, bapt_place, bapt_source)
            babt_ref = RelLib.EventRef()
            babt_ref.set_reference_handle( babt.get_handle())
            person.add_event_ref( babt_ref)

        if death_date or death_place or death_source or death_cause:
            death = self.create_event(RelLib.EventType.DEATH, None, death_date, death_place, death_source)
            if death_cause:
                death.set_description(death_cause)
                self.db.commit_event(death,self.trans)
            death_ref = RelLib.EventRef()
            death_ref.set_reference_handle( death.get_handle())
            person.set_death_ref( death_ref)

        if bur_date:
            bur = self.create_event(RelLib.EventType.BURIAL, None, bur_date, bur_place, bur_source)
            bur_ref = RelLib.EventRef()
            bur_ref.set_reference_handle( bur.get_handle())
            person.add_event_ref( bur_ref)

        if crem_date:
            crem = self.create_event(RelLib.EventType.CREMATION, None, crem_date, bur_place, bur_source)
            crem_ref = RelLib.EventRef()
            crem_ref.set_reference_handle( crem.get_handle())
            person.add_event_ref(crem_ref)

        self.db.commit_person(person,self.trans)

        return (idx,person)
        
    def parse_date(self,field):
        if field == "0":
            return None
        date = RelLib.Date()
        matches = _text_parse.match(field)
        if matches:
            groups = matches.groups()
            date.set_as_text(groups[0])
            date.set_modifier(RelLib.Date.MOD_TEXTONLY)
            return date

        matches = _date_parse.match(field)
        if matches:
            groups = matches.groups()
            mod = _mod_map.get(groups[0],RelLib.Date.MOD_NONE)
            if groups[3] == "..":
                mod = RelLib.Date.MOD_SPAN
                cal2 = _cal_map.get(groups[5],RelLib.Date.CAL_GREGORIAN)
                sub2 = self.sub_date(groups[4])
            else:
                sub2 = (0,0,0)
            cal1 = _cal_map.get(groups[2],RelLib.Date.CAL_GREGORIAN)
            sub1 = self.sub_date(groups[1])
            date.set(RelLib.Date.QUAL_NONE,mod, cal1,
                     (sub1[0],sub1[1],sub1[2],None,sub2[0],sub2[1],sub2[2],None))
            return date
        else:
            return None

    def sub_date(self,data):
        vals = data.split('/')
        if len(vals) == 1:
            return (0,0,int(vals[0]))
        elif len(vals) == 2:
            return (0,int(vals[0]),int(vals[1]))
        else:
            return (int(vals[0]),int(vals[1]),int(vals[2]))
        
    def create_event(self,type,desc=None,date=None,place=None,source=None):
        event = RelLib.Event()
        if type:
            event.set_type(RelLib.EventType(type))
        if desc:
            event.set_description(desc)
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if source:
            event.add_source_reference(source)
        self.db.add_event(event,self.trans)
        self.db.commit_event(event,self.trans)
        return event
    
    def get_or_create_person(self,firstname,lastname):
        person = None
        mykey = firstname+lastname
        if mykey in self.ikeys and firstname != "?" and lastname != "?":
            person = self.db.get_person_from_handle(self.ikeys[mykey])
        else:
            person = RelLib.Person()
            self.db.add_person(person,self.trans)
            self.db.commit_person(person,self.trans)
            self.ikeys[mykey] = person.get_handle()
        return person

    def get_or_create_place(self,place_name):
        place = None
        if place_name in self.pkeys:
            place = self.db.get_place_from_handle(self.pkeys[place_name])
        else:
            place = RelLib.Place()
            place.set_title(place_name)
            self.db.add_place(place,self.trans)
            self.db.commit_place(place,self.trans)
            self.pkeys[place_name] = place.get_handle()
        return place

    def get_or_create_source(self,source_name):
        source = None
        if source_name in self.skeys:
            source = self.db.get_source_from_handle(self.skeys[source_name])
        else:
            source = RelLib.Source()
            source.set_title(source_name)
            self.db.add_source(source,self.trans)
            self.db.commit_source(source,self.trans)
            self.skeys[source_name] = source.get_handle()
        sref = RelLib.SourceRef()
        sref.set_reference_handle(source.get_handle())
        return sref

    def decode(self,s):
        s = s.replace('_',' ')
        charref_re = re.compile('(&#)(x?)([0-9a-zA-Z]+)(;)')
        for match in charref_re.finditer(s):
            try:
                if match.group(2):  # HEX
                    nchar = unichr(int(match.group(3),16))
                else:   # Decimal
                    nchar = unichr(int(match.group(3)))
                s = s.replace(match.group(0),nchar)
            except UnicodeDecodeError:
                pass
        
        # replace named entities
        entref_re = re.compile('(&)([a-zA-Z]+)(;)')
        for match in entref_re.finditer(s):
            try:
                if match.group(2) in name2codepoint:
                    nchar = unichr(name2codepoint[match.group(2)])
                s = s.replace(match.group(0),nchar)
            except UnicodeDecodeError:
                pass
        
        return( s)

    def debug( self, txt):
        if enable_debug:
            print txt
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_mime_type = const.app_geneweb
_filter = gtk.FileFilter()
_filter.set_name(_('GeneWeb files'))
_filter.add_mime_type(_mime_type)
_format_name = _('GeneWeb')

register_import(importData,_filter,_mime_type,0,_format_name)
