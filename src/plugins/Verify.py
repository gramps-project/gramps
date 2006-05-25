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

"View/Verify"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
import cStringIO
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import gtk.glade 

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import RelLib
import Utils
import GrampsDisplay
import ManagedWindow

from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# temp storage and related functions
#
#-------------------------------------------------------------------------
_person_store = {}
_family_store = {}
_event_store = {}

def find_event(db,handle):
    try:
        obj = _event_store[handle]
    except KeyError:
        obj = db.get_event_from_handle(handle)
        _event_store[handle] = obj
        print "reading event", obj.gramps_id
    return obj

def find_person(db,handle):
    try:
        obj = _person_store[handle]
    except KeyError:
        obj = db.get_person_from_handle(handle)
        _person_store[handle] = obj
        print "reading person", obj.gramps_id
    return obj

def find_family(db,handle):
    try:
        obj = _family_store[handle]
    except KeyError:
        obj = db.get_family_from_handle(handle)
        _family_store[handle] = obj
        print "reading family", obj.gramps_id
    return obj

def clear_storage():
    print "events:", len(_event_store), "families:", len(_family_store), \
          "people:", len(_person_store)
    _person_store.clear()
    _family_store.clear()
    _event_store.clear()
#-------------------------------------------------------------------------
#
# helper functions
#
#-------------------------------------------------------------------------
def get_date_from_event_handle(db,event_handle):
    if not event_handle:
        return 0
    event =  find_event(db,event_handle)
    date_obj = event.get_date_object()
    return date_obj.get_sort_value()

def get_date_from_event_type(db,person,event_type):
    if not person:
        return 0
    for event_ref in person.get_event_ref_list():
        event = find_event(db,event_ref.ref)
        if event.get_type() == event_type:
            date_obj = event.get_date_object()
            return date_obj.get_sort_value()
    return 0

def get_birth_date(db,person):
    if not person:
        return 0
    birth_ref = person.get_birth_ref()
    if not birth_ref:
        return 0
    return get_date_from_event_handle(db,birth_ref.ref)

def get_death_date(db,person):
    if not person:
        return 0
    death_ref = person.get_death_ref()
    if not death_ref:
        return 0
    return get_date_from_event_handle(db,death_ref.ref)

def get_bapt_date(db,person):
    return get_date_from_event_type(db,person,RelLib.EventType.BAPTISM)

def get_bury_date(db,person):
    return get_date_from_event_type(db,person,RelLib.EventType.BURIAL)

def get_age_at_death(db,person):
    birth_date = get_birth_date(db,person)
    death_date = get_death_date(db,person)
    if (birth_date > 0) and (death_date > 0):
        return death_date - birth_date
    return 0

def get_father(db,family):
    if not family:
        return None
    father_handle = family.get_father_handle()
    if father_handle:
        return find_person(db,father_handle)
    return None

def get_mother(db,family):
    if not family:
        return None
    mother_handle = family.get_mother_handle()
    if mother_handle:
        return find_person(db,mother_handle)
    return None

def get_child_birth_dates(db,family):
    dates = []
    for child_ref in family.get_child_ref_list():
        child = find_person(db,child_ref.ref)
        child_birth_date = get_birth_date(child)
        if child_birth_date > 0:
            dates.append(child_birth_date)
    return dates

def get_n_children(db,person):
    n = 0
    for family_handle in person.get_family_handle_list():
        family = find_family(db,family_handle)
        n += len(family.get_child_ref_list())

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class Verify(Tool.Tool, ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, options_class, name,callback=None):
        self.label = _('Database Verify tool')
        Tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        if uistate:
            self.init_gui()
        else:
            err_text,warn_text = self.run_tool(cli=True)
            self.print_results(err_text,warn_text)

    def init_gui(self):
        # Draw dialog and make it handle everything
        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_settings","gramps")
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_verify_ok_clicked"  : self.on_apply_clicked
        })

        window = self.top.get_widget('verify_settings')
        self.set_window(window,self.top.get_widget('title'),self.label)

        self.top.get_widget("oldage").set_value(
            self.options.handler.options_dict['oldage'])
        self.top.get_widget("hwdif").set_value(
            self.options.handler.options_dict['hwdif'])
        self.top.get_widget("cspace").set_value(
            self.options.handler.options_dict['cspace'])
        self.top.get_widget("cbspan").set_value(
            self.options.handler.options_dict['cbspan'])
        self.top.get_widget("yngmar").set_value(
            self.options.handler.options_dict['yngmar'])
        self.top.get_widget("oldmar").set_value(
            self.options.handler.options_dict['oldmar'])
        self.top.get_widget("oldmom").set_value(
            self.options.handler.options_dict['oldmom'])
        self.top.get_widget("yngmom").set_value(
            self.options.handler.options_dict['yngmom'])
        self.top.get_widget("olddad").set_value(
            self.options.handler.options_dict['olddad'])
        self.top.get_widget("yngdad").set_value(
            self.options.handler.options_dict['yngdad'])
        self.top.get_widget("wedder").set_value(
            self.options.handler.options_dict['wedder'])
        self.top.get_widget("mxchildmom").set_value(
            self.options.handler.options_dict['mxchildmom'])
        self.top.get_widget("mxchilddad").set_value(
            self.options.handler.options_dict['mxchilddad'])
        self.top.get_widget("lngwdw").set_value(
            self.options.handler.options_dict['lngwdw'])
        self.top.get_widget("estimate").set_active(
            self.options.handler.options_dict['estimate_age'])
                                                          
        self.show()

    def build_menu_names(self,obj):
        return (_("Tool settings"),self.label)

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-other')

    def get_year(self,event_handle):
        """
        Returns the year of an event (by its id) or 0 if no event_handle 
        or no year  specified in the event
        """
        year = 0
        if event_handle:
            event = self.db.get_event_from_handle(event_handle)
            dateObj = event.get_date_object()
            if dateObj:
                if dateObj.get_calendar() != RelLib.Date.CAL_GREGORIAN:
                    dateObj.set_calendar(RelLib.Date.CAL_GREGORIAN)
                year = dateObj.get_year()
        return year

    def on_apply_clicked(self,obj):
        self.options.handler.options_dict['oldage'] = self.top.get_widget(
            "oldage").get_value_as_int()
        self.options.handler.options_dict['hwdif']  = self.top.get_widget(
            "hwdif").get_value_as_int()
        self.options.handler.options_dict['cspace'] = self.top.get_widget(
            "cspace").get_value_as_int()
        self.options.handler.options_dict['cbspan'] = self.top.get_widget(
            "cbspan").get_value_as_int()
        self.options.handler.options_dict['yngmar'] = self.top.get_widget(
            "yngmar").get_value_as_int()
        self.options.handler.options_dict['oldmar'] = self.top.get_widget(
            "oldmar").get_value_as_int()
        self.options.handler.options_dict['oldmom'] = self.top.get_widget(
            "oldmom").get_value_as_int()
        self.options.handler.options_dict['yngmom'] = self.top.get_widget(
            "yngmom").get_value_as_int()
        self.options.handler.options_dict['olddad'] = self.top.get_widget(
            "olddad").get_value_as_int()
        self.options.handler.options_dict['yngdad'] = self.top.get_widget(
            "yngdad").get_value_as_int()
        self.options.handler.options_dict['wedder'] = self.top.get_widget(
            "wedder").get_value_as_int()
        self.options.handler.options_dict['mxchildmom'] = self.top.get_widget(
            "mxchildmom").get_value_as_int()
        self.options.handler.options_dict['mxchilddad'] = self.top.get_widget(
            "mxchilddad").get_value_as_int()
        self.options.handler.options_dict['lngwdw'] = self.top.get_widget(
            "lngwdw").get_value_as_int()

        self.options.handler.options_dict['estimate_age'] = \
                                                          self.top.get_widget(
            "estimate").get_active()

        err_text,warn_text = self.run_tool(cli=False)
        # Save options
        self.options.handler.save_options()
        VerifyResults(err_text, warn_text, self.uistate, self.track)

    def run_tool(self,cli=False):

        person_handles = self.db.get_person_handles(sort_handles=False)
        oldage = self.options.handler.options_dict['oldage']
        hwdif = self.options.handler.options_dict['hwdif']
        cspace = self.options.handler.options_dict['cspace']
        cbspan = self.options.handler.options_dict['cbspan']
        yngmar = self.options.handler.options_dict['yngmar']
        oldmar = self.options.handler.options_dict['oldmar']
        oldmom = self.options.handler.options_dict['oldmom']
        yngmom = self.options.handler.options_dict['yngmom']
        olddad = self.options.handler.options_dict['olddad']
        yngdad = self.options.handler.options_dict['yngdad']
        wedder = self.options.handler.options_dict['wedder']
        mxchildmom = self.options.handler.options_dict['mxchildmom']
        mxchilddad = self.options.handler.options_dict['mxchilddad']
        lngwdw = self.options.handler.options_dict['lngwdw']
        estimate_age = self.options.handler.options_dict['estimate_age']

        # FIXME: This has to become an option as well!
        # OR should be removed. What's the reason behind it?
        oldunm = 99  # maximum age at death for unmarried person 


#        error = cStringIO.StringIO()
#        warn = cStringIO.StringIO()

        if not cli:
            progress = Utils.ProgressMeter(_('Verify the database'),'')
            progress.set_pass(_('Checking data'),
                              self.db.get_number_of_people())
        
        for person_handle in person_handles:
            person = find_person(self.db,person_handle)

            the_rule = BirthAfterBapt(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = DeathBeforeBapt(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = BirthAfterBury(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = DeathAfterBury(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = BirthAfterDeath(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = BaptAfterBury(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = OldAge(self.db,person,oldage)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = UnknownGender(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = MultipleParents(self.db,person)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = MarriedOften(self.db,person,wedder)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = OldUnmarried(self.db,person,oldunm)
            if the_rule.broken():
                print the_rule.get_message()
                
            the_rule = TooManyChildren(self.db,person,mxchilddad,mxchildmom)
            if the_rule.broken():
                print the_rule.get_message()

            clear_storage()
             
                
##             if byear>0 and bapyear>0:
##                 if byear > bapyear:
##                     if person.get_gender() == RelLib.Person.MALE:
##                         error.write( _("Baptized before birth: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
##                             'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
##                     if person.get_gender() == RelLib.Person.FEMALE:
##                         error.write( _("Baptized before birth: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
##                             'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
##                 if byear < bapyear:
##                     if person.get_gender() == RelLib.Person.MALE:
##                         warn.write( _("Baptized late: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
##                             'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
##                     if person.get_gender() == RelLib.Person.FEMALE:
##                         warn.write( _("Baptized late: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
##                             'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
##             if dyear>0 and buryear>0:
##                 if dyear > buryear:
##                     if person.get_gender() == RelLib.Person.MALE:
##                         error.write( _("Buried before death: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
##                             'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
##                     if person.get_gender() == RelLib.Person.FEMALE:
##                         error.write( _("Buried before death: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
##                             'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
##                 if dyear < buryear:
##                     if person.get_gender() == RelLib.Person.MALE:
##                         warn.write( _("Buried late: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
##                             'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
##                     if person.get_gender() == RelLib.Person.FEMALE:
##                         warn.write( _("Buried late: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
##                             'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
##             if dyear>0 and (byear>dyear):
##                 if person.get_gender() == RelLib.Person.MALE:
##                     error.write( _("Died before birth: %(male_name)s born %(byear)d, died %(dyear)d.\n") % { 
##                         'male_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     error.write( _("Died before birth: %(female_name)s born %(byear)d, died %(dyear)d.\n") % { 
##                         'female_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
##             if dyear>0 and (bapyear>dyear):
##                 if person.get_gender() == RelLib.Person.MALE:
##                     error.write( _("Died before baptism: %(male_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
##                         'male_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     error.write( _("Died before baptism: %(female_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
##                         'female_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
##             if buryear>0 and (byear>buryear):
##                 if person.get_gender() == RelLib.Person.MALE:
##                     error.write( _("Buried before birth: %(male_name)s born %(byear)d, buried %(buryear)d.\n") % { 
##                         'male_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     error.write( _("Buried before birth: %(female_name)s born %(byear)d, buried %(buryear)d.\n") % { 
##                         'female_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
##             if buryear>0 and (bapyear>buryear):
##                 if person.get_gender() == RelLib.Person.MALE:
##                     error.write( _("Buried before baptism: %(male_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
##                         'male_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     error.write( _("Buried before baptism: %(female_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
##                         'female_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
##             if byear == 0 and estimate_age:
##                 byear = bapyear  # guess baptism = birth
##             if dyear == 0 and estimate_age:
##                 dyear = buryear  # guess burial = death
##             if byear>0 and dyear>0:
##                 ageatdeath = dyear - byear
##             else:
##                 ageatdeath = 0
##             if ageatdeath > oldage:
##                 if person.get_gender() == RelLib.Person.MALE:
##                     warn.write( _("Old age: %(male_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
##                         'male_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     warn.write( _("Old age: %(female_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
##                         'female_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
    
##             # gender checks

##             if person.get_gender() == RelLib.Person.FEMALE:
##                 oldpar = oldmom
##                 yngpar = yngmom
##             if person.get_gender() == RelLib.Person.MALE:
##                 oldpar = olddad
##                 yngpar = yngdad
##             if (person.get_gender() != RelLib.Person.FEMALE) and (person.get_gender() != RelLib.Person.MALE):
##                 warn.write( _("Unknown gender for %s.\n") % idstr )
##                 oldpar = olddad
##                 yngpar = yngdad
##             if (person.get_gender() == RelLib.Person.FEMALE) and (person.get_gender() == RelLib.Person.MALE):
##                 error.write( _("Ambiguous gender for %s.\n") % idstr )
##                 oldpar = olddad
##                 yngpar = yngdad
        
##             # multiple parentage check
##             if( len( person.get_parent_family_handle_list() ) > 1 ):
##                 warn.write( _("Multiple parentage for %s.\n") % idstr )

##             # marriage checks
##             nkids = 0
##             nfam  = len( person.get_family_handle_list() )
##             if nfam > wedder:
##                 if person.get_gender() == RelLib.Person.MALE:
##                     warn.write( _("Married often: %(male_name)s married %(nfam)d times.\n") % { 
##                         'male_name' : idstr, 'nfam' : nfam } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     warn.write( _("Married often: %(female_name)s married %(nfam)d times.\n") % { 
##                         'female_name' : idstr, 'nfam' : nfam } )
##             if ageatdeath>oldunm and nfam == 0:
##                 if person.get_gender() == RelLib.Person.MALE:
##                     warn.write( _("Old and unmarried: %(male_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
##                         'male_name' : idstr, 'ageatdeath' : ageatdeath } )
##                 if person.get_gender() == RelLib.Person.FEMALE:
##                     warn.write( _("Old and unmarried: %(female_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
##                         'female_name' : idstr, 'ageatdeath' : ageatdeath } )
##             prev_cbyear=0
##             prev_maryear=0
##             prev_sdyear=0
##             fnum = 0

##             for family_handle in person.get_family_handle_list():
##                 family = self.db.get_family_from_handle(family_handle)
##                 fnum = fnum + 1
##                 mother_handle = family.get_mother_handle()
##                 father_handle = family.get_father_handle()
##                 if mother_handle:
##                     mother = self.db.get_person_from_handle(mother_handle)
##                 if father_handle:
##                     father = self.db.get_person_from_handle(father_handle)
##                 if mother_handle and father_handle:
##                     if ( mother.get_gender() == father.get_gender() ) and mother.get_gender() != RelLib.Person.UNKNOWN:
##                         warn.write( _("Homosexual marriage: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
##                 if father_handle == person.get_handle() and person.get_gender() == RelLib.Person.FEMALE:
##                     error.write( _("Female husband: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
##                 if mother_handle == person.get_handle() and person.get_gender() == RelLib.Person.MALE:
##                     error.write( _("Male wife: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
##                 if father_handle == person.get_handle():
##                    spouse_id = mother_handle
##                 else:
##                    spouse_id = father_handle
##                 if spouse_id:
##                     spouse = self.db.get_person_from_handle(spouse_id)
##                     if person.get_gender() == RelLib.Person.MALE and \
##                            person.get_primary_name().get_surname() == spouse.get_primary_name().get_surname():
##                         warn.write( _("Husband and wife with the same surname: %s in family %s, and %s.\n") % (
##                             idstr,family.get_gramps_id(), spouse.get_primary_name().get_name() ) )


##                     death_ref = spouse.get_death_ref()
##                     if death_ref:
##                         death_handle = death_ref.ref
##                     else:
##                         death_handle = None

##                     birth_ref = spouse.get_birth_ref()
##                     if birth_ref:
##                         birth_handle = birth_ref.ref
##                     else:
##                         birth_handle = None
                        
##                     sdyear = self.get_year( death_handle )
##                     sbyear = self.get_year( birth_handle )
##                     if sbyear != 0 and byear != 0 and abs(sbyear-byear) > hwdif:
##                         warn.write( _("Large age difference between husband and wife: %s in family %s, and %s.\n") % (
##                             idstr,family.get_gramps_id(), spouse.get_primary_name().get_name() ) )
                        
##                     if sdyear == 0:
##                         sdyear = 0  # burial year

##                     for event_ref in family.get_event_ref_list():
##                         if event_ref:
##                             event_handle = event_ref.ref
##                             event = self.db.get_event_from_handle(event_handle)
##                             if event.get_type().xml_str() == "Marriage":
##                                 marriage_id = event_handle
##                                 break
##                     else:
##                         marriage_id = None

##                     maryear = self.get_year( marriage_id )

##                     if maryear == 0 and estimate_age:   #  estimate marriage year
##                         cnum=0
##                         for child_ref in family.get_child_ref_list():
##                             cnum = cnum + 1
##                             if maryear == 0:
##                                 child = self.db.get_person_from_handle(child_ref.ref)
##                                 birth_ref = child.get_birth_ref()
##                                 if birth_ref:
##                                     birthyear = self.get_year(birth_ref.ref)
##                                 else:
##                                     birthyear = 0
##                             if birthyear > 0:
##                                 maryear = birthyear-cnum

##                     if maryear > 0:
##                         if byear > 0:
##                             marage = maryear - byear
##                             if marage < 0:
##                                 if person.get_gender() == RelLib.Person.MALE:
##                                         error.write( _("Married before birth: %(male_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
##                                         'male_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
##                                 if person.get_gender() == RelLib.Person.FEMALE:
##                                     error.write( _("Married before birth: %(female_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
##                                         'female_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
##                             else:
##                                 if marage < yngmar:
##                                     if person.get_gender() == RelLib.Person.MALE:
##                                         warn.write( _("Young marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
##                                             'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
##                                     if person.get_gender() == RelLib.Person.FEMALE:
##                                         warn.write( _("Young marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
##                                             'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
##                                 if marage > oldmar:
##                                    if person.get_gender() == RelLib.Person.MALE:
##                                         warn.write( _("Old marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
##                                             'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
##                                    if person.get_gender() == RelLib.Person.FEMALE:
##                                         warn.write( _("Old marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
##                                             'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
##                         if dyear>0 and maryear > dyear:
##                             if person.get_gender() == RelLib.Person.MALE:
##                                 error.write( _("Married after death: %(male_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
##                                     'male_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
##                             if person.get_gender() == RelLib.Person.FEMALE:
##                                 error.write( _("Married after death: %(female_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
##                                     'female_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
##                         if prev_cbyear > maryear:
##                             if person.get_gender() == RelLib.Person.MALE:
##                                 warn.write( _("Marriage before birth from previous family: %(male_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
##                                     'male_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
##                             if person.get_gender() == RelLib.Person.FEMALE:
##                                 warn.write( _("Marriage before birth from previous family: %(female_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
##                                     'female_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
##                         prev_maryear = maryear
##                     else:
##                         maryear = prev_maryear
                                                        
##                     if maryear>0 and prev_sdyear > 0:
##                         wdwyear = maryear-prev_sdyear
##                         if wdwyear > lngwdw:
##                             if person.get_gender() == RelLib.Person.MALE:
##                                 warn.write( _("Long widowhood: %s was a widower %d years before, family %s.\n") % (idstr, wdwyear, family.get_gramps_id() ) )
##                             if person.get_gender() == RelLib.Person.FEMALE:
##                                 warn.write( _("Long widowhood: %s was a widow %d years before, family %s.\n") % (idstr, wdwyear, family.get_gramps_id() ) )

##                     if fnum==nfam and dyear>0 and sdyear>0:
##                         wdwyear = dyear - sdyear
##                         if wdwyear > lngwdw:
##                             if person.get_gender() == RelLib.Person.MALE:
##                                 warn.write( _("Long widowhood: %s was a widower %d years.\n") % (idstr, wdwyear) )
##                             if person.get_gender() == RelLib.Person.FEMALE:
##                                 warn.write( _("Long widowhood: %s was a widow %d years.\n") % (idstr, wdwyear) )

##                     nkids = 0
##                     cbyears = []
                    
##                     total_children = total_children + len(family.get_child_ref_list())
##                     for child_ref in family.get_child_ref_list():
##                         nkids = nkids+1
##                         child = self.db.get_person_from_handle(child_ref.ref)
##                         birth_ref = child.get_birth_ref()
##                         if birth_ref:
##                             birth_handle = birth_ref.ref
##                         else:
##                             birth_handle = None
                            
##                         cbyear = self.get_year( birth_handle )
##                         if cbyear:
##                             cbyears.append(cbyear)

##                         # parentage checks 
##                         if byear>0 and cbyear>0:
##                             bage = cbyear - byear
##                             if bage > oldpar:
##                                 if person.get_gender() == RelLib.Person.MALE:
##                                     warn.write( _("Old father: %(male_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
##                                         'male_name' : idstr, 'bage' : bage, 'fam' : family.get_handle(), 'child' : child.get_primary_name().get_name() } ) 
##                                 if person.get_gender() == RelLib.Person.FEMALE:
##                                     warn.write( _("Old mother: %(female_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
##                                         'female_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } ) 
##                             if bage < 0:
##                                 if person.get_gender() == RelLib.Person.MALE:
##                                     error.write( _("Unborn father: %(male_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'male_name' : idstr, 'byear' : byear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
##                                 if person.get_gender() == RelLib.Person.FEMALE:
##                                     error.write( _("Unborn mother: %(female_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'female_name' : idstr, 'byear' : byear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
##                             else:
##                                 if bage < yngpar:
##                                     if person.get_gender() == RelLib.Person.MALE:
##                                         warn.write( _("Young father: %(male_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
##                                                         'male_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } )
##                                         if person.get_gender() == RelLib.Person.FEMALE:
##                                             warn.write( _("Young mother: %(female_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
##                                                         'female_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } )
##                         if dyear>0 and cbyear>dyear:
##                             if cbyear-1>dyear:
##                                 if person.get_gender() == RelLib.Person.MALE:
##                                     error.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
##                                 if person.get_gender() == RelLib.Person.FEMALE:
##                                     error.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
##                             else:
##                                 if person.get_gender() == RelLib.Person.MALE:
##                                     warn.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
##                                 if person.get_gender() == RelLib.Person.FEMALE:
##                                     warn.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
##                                                 'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                    
##                     if cbyears:
##                         cbyears.sort()
##                         if (cbyears[-1] - cbyears[0]) > cbspan:
##                             warn.write(_("Large year span for all children: family %s.\n") % family.get_gramps_id() )
##                     if len(cbyears) > 1:
##                         cby_diff = [ cbyears[i+1]-cbyears[i] for i in range(len(cbyears)-1) ]
##                         if max(cby_diff) > cspace:
##                             warn.write(_("Large age differences between children: family %s.\n") % family.get_gramps_id() )

##             if (person.get_gender() == RelLib.Person.MALE 
##                                 and total_children > mxchilddad) \
##                         or (person.get_gender() == RelLib.Person.FEMALE 
##                                 and total_children > mxchildmom):
##                 warn.write(_("Too many children (%(num_children)d) for %(person_name)s.\n") % {
##                     'num_children' : total_children, 'person_name' : idstr })
            if not cli:
                progress.step()

        if not cli:
            progress.close()

##         err_text = error.getvalue()
##         warn_text = warn.getvalue()
##         error.close()
##         warn.close()
        
        return ("","") #err_text.strip(),warn_text.strip()

    def print_results(self,err_text,warn_text):
        if warn_text:
            print "\nWARNINGS:"
            print warn_text
        if err_text:
            print "\nERRORS:"
            print err_text
        if not (warn_text or err_text):
            print "No warnings or errors during verification!"
    
#-------------------------------------------------------------------------
#
# Display the results
#
#-------------------------------------------------------------------------
class VerifyResults(ManagedWindow.ManagedWindow):
    def __init__(self,err_text,warn_text,uistate,track):
        self.title = _('Database Verification Results')

        ManagedWindow.ManagedWindow.__init__(self,uistate,track,self.__class__)

        self.err_text = err_text
        self.warn_text = warn_text

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_result","gramps")
        window = self.top.get_widget("verify_result")
        self.set_window(window,self.top.get_widget('title'),self.title)
    
        self.top.signal_autoconnect({
            "destroy_passed_object"  : self.close,
            })

        err_window = self.top.get_widget("err_window")
        warn_window = self.top.get_widget("warn_window")
        err_window.get_buffer().set_text(self.err_text)
        warn_window.get_buffer().set_text(self.warn_text)
        
        self.show()

    def build_menu_names(self,obj):
        return (self.title,None)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class VerifyOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'oldage'       : 90,
            'hwdif'       : 30,
            'cspace'       : 8,
            'cbspan'       : 25,
            'yngmar'       : 17,
            'oldmar'       : 50,
            'oldmom'       : 48,
            'yngmom'       : 17,
            'yngdad'       : 18,
            'olddad'       : 65,
            'wedder'       : 3,
            'mxchildmom'   : 12,
            'mxchilddad'   : 15,
            'lngwdw'       : 30,
            'estimate_age' : 0,
        }
        self.options_help = {
            'oldage'       : ("=num","Maximum age","Age in years"),
            'hwdif'       : ("=num","Maximum husband-wife age difference",
                              "Age difference in years"),
            'cspace'       : ("=num",
                              "Maximum number of years between children",
                              "Number of years"),
            'cbspan'       : ("=num",
                              "Maximum span of years for all children",
                              "Span in years"),
            'yngmar'       : ("=num","Minimum age to marry","Age in years"),
            'oldmar'       : ("=num","Maximum age to marry","Age in years"),
            'oldmom'       : ("=num","Maximum age to bear a child",
                              "Age in years"),
            'yngmom'       : ("=num","Minimum age to bear a child",
                              "Age in years"),
            'yngdad'       : ("=num","Minimum age to father a child",
                              "Age in years"),
            'olddad'       : ("=num","Maximum age to father a child",
                              "Age in years"),
            'wedder'       : ("=num","Maximum number of spouses for a person",
                              "Number of spouses"),
            'mxchildmom'   : ("=num","Maximum number of children for a woman",
                              "Number of children"),
            'mxchilddad'   : ("=num","Maximum  number of children for a man",
                              "Number of chidlren"),
            'lngwdw'       : ("=num","Maximum number of consecutive years "
                              "of widowhood","Number of years"),
            'estimate_age' : ("=0/1","Whether to estimate missing dates",
                              ["Do not estimate","Estimate dates"],
                              True),
        }

#-------------------------------------------------------------------------
#
# Base classes for different tests -- the rules
#
#-------------------------------------------------------------------------
class Rule:
    """
    Basic class for use in this tool.

    Other rules must inherit from this.
    """
    ERROR   = 1
    WARNING = 2

    def __init__(self,db):
        self.db = db
        self.hidden = False

    def broken(self):
        """
        Return boolean indicating whether this rule is violated.
        """
        return False

    def hide(self):
        self.hidden = True

    def unhide(self):
        self.hidden = False

    def get_message(self):
        assert False, "Need to be overriden in the derived class"

    def get_id_str(self):
        assert False, "Need to be overriden in the derived class"

    def get_level(self):
        return Rule.WARNING

class PersonRule(Rule):
    """
    Person-based class.
    """
    def __init__(self,db,person):
        Rule.__init__(self,db)
        self.obj_type = 'Person'
        self.obj = person

    def get_id_str(self):
        return "%s (%s)" % (self.obj.get_primary_name().get_name(),
                            self.obj.get_gramps_id())

class FamilyRule(Rule):
    """
    Family-based class.
    """
    def __init__(self,db,family):
        Rule.__init__(self,db)
        self.obj_type = 'Family'
        self.obj = family()

    def get_id_str(self):
        return get_family_name(self.db,self.obj)

#-------------------------------------------------------------------------
#
# Actual rules for testing
#
#-------------------------------------------------------------------------
class BirthAfterBapt(PersonRule):
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        bapt_date = get_bapt_date(self.db,self.obj)
        birth_ok = birth_date > 0
        bapt_ok = bapt_date > 0
        birth_after_death = birth_date > bapt_date
        return (birth_ok and bapt_ok and birth_after_death)

    def get_message(self):
        return _("Baptism before birth")

class DeathBeforeBapt(PersonRule):
    def broken(self):
        death_date = get_death_date(self.db,self.obj)
        bapt_date = get_bapt_date(self.db,self.obj)
        bapt_ok = bapt_date > 0
        death_ok = death_date > 0
        death_before_bapt = bapt_date > death_date
        return (death_ok and bapt_ok and death_before_bapt)

    def get_message(self):
        return _("Death before baptism")

class BirthAfterBury(PersonRule):
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        birth_ok = birth_date > 0
        bury_ok = bury_date > 0
        birth_after_bury = birth_date > bury_date
        return (birth_ok and bury_ok and birth_after_bury)

    def get_message(self):
        return _("Burial before birth")

class DeathAfterBury(PersonRule):
    def broken(self):
        death_date = get_death_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        death_ok = death_date > 0
        bury_ok = bury_date > 0
        death_after_bury = death_date > bury_date
        return (death_ok and bury_ok and death_after_bury)

    def get_message(self):
        return _("Burial before death")

class BirthAfterDeath(PersonRule):
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        death_date = get_death_date(self.db,self.obj)
        birth_ok = birth_date > 0
        death_ok = death_date > 0
        birth_after_death = birth_date > death_date
        return (birth_ok and death_ok and birth_after_death)

    def get_message(self):
        return _("Death before birth")

class BaptAfterBury(PersonRule):
    def broken(self):
        bapt_date = get_bapt_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        bapt_ok = bapt_date > 0
        bury_ok = bury_date > 0
        bapt_after_bury = bapt_date > bury_date
        return (bapt_ok and bury_ok and bapt_after_bury)

    def get_message(self):
        return _("Burial before baptism")

class OldAge(PersonRule):
    def __init__(self,db,person,old_age):
        PersonRule.__init__(self,db,person)
        self.old_age = old_age

    def broken(self):
        age_at_death = get_age_at_death(self.db,self.obj)
        return (age_at_death > self.old_age)

    def get_message(self):
        return _("Old age at death")

class UnknownGender(PersonRule):
    def broken(self):
        female = self.obj.get_gender() == RelLib.Person.FEMALE
        male = self.obj.get_gender() == RelLib.Person.MALE
        return (male or female)

    def get_message(self):
        return _("Unknown gender")

class MultipleParents(PersonRule):
    def broken(self):
        n_parent_sets = len(self.obj.get_parent_family_handle_list())
        return (n_parent_sets>1)

    def get_message(self):
        return _("Multiple parents")

class MarriedOften(PersonRule):
    def __init__(self,db,person,wedder):
        PersonRule.__init__(self,db,person)
        self.wedder = wedder

    def broken(self):
        n_spouses = len(self.obj.get_family_handle_list())
        return (n_spouses>self.wedder)

    def get_message(self):
        return _("Married often")

class OldUnmarried(PersonRule):
    def __init__(self,db,person,old_unm):
        PersonRule.__init__(self,db,person)
        self.old_unm = old_unm

    def broken(self):
        age_at_death = get_age_at_death(self.db,self.obj)
        n_spouses = len(self.obj.get_family_handle_list())
        return (age_at_death>self.old_unm and n_spouses==0)

    def get_message(self):
        return _("Old and unmarried")

class SameSexFamily(FamilyRule):
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        same_sex = (mother.get_gender() == father.get_gender())
        unknown_sex = (mother.get_gender() == RelLib.Person.UNKNOWN)
        return (same_sex and not unknown_sex)

    def get_message(self):
        return _("Same sex marriage")

class FemaleHusband(FamilyRule):
    def broken(self):
        father = get_father(self.db,self.obj)
        return (father.get_gender() == RelLib.Person.FEMALE)

    def get_message(self):
        return _("Female husband")

class MaleWife(FamilyRule):
    def broken(self):
        mother = get_mother(self.db,self.obj)
        return (mother.get_gender() == RelLib.Person.MALE)

    def get_message(self):
        return _("Male wife")

class SameSurnameFamily(FamilyRule):
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        same_surname = (mother.get_primary_name().get_surname() ==
                        father.get_primary_name().get_surname())
        empty_surname = len(mother.get_primary_name().get_surname())==0
        return (same_surname and not empty_surname)

    def get_message(self):
        return _("Husband and wife with the same surname")

class LargeAgeGapFamily(FamilyRule):
    def __init__(self,db,obj,hw_diff):
        FamilyRule.__init__(self,db,obj)
        self.hw_diff = hw_diff

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0
        large_diff = abs(father_birth_date-mother_birth_date) > self.hw_diff
        return (mother_birth_date_ok and father_birth_date_ok and large_diff)

    def get_message(self):
        return _("Large age difference between husband and wife")

class MarriageBeforeBirth(FamilyRule):
    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (father_birth_date > marr_date))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (mother_birth_date > marr_date))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Marriage before birth")

class MarriageAfterDeath(FamilyRule):
    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_death_date = get_death_date(self.db,mother)
        father_death_date = get_death_date(self.db,father)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        father_broken = (father_death_date_ok and marr_date_ok
                         and (father_death_date > marr_date))
        mother_broken = (mother_death_date_ok and marr_date_ok
                         and (mother_death_date > marr_date))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Marriage after death")

class EarlyMarriage(FamilyRule):
    def __init__(self,db,obj,yng_mar):
        FamilyRule__init__(self,db,obj)
        self.yng_mar = yng_mar

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (marr_date - father_birth_date < self.yng_mar))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (marr_date - mother_birth_date < self.yng_mar))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Early marriage")

class LateMarriage(FamilyRule):
    def __init__(self,db,obj,old_mar):
        FamilyRule__init__(self,db,obj)
        self.old_mar = old_mar

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (marr_date - father_birth_date > self.old_mar))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (marr_date - mother_birth_date > self.old_mar))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Late marriage")

## class MarriageBeforePrefiousMarrChild(PersonRule):
##     def broken(self):
##         marr_date = get_marriage_date(self.obj)
##         prev_marr_child_date = get_prev_marr_child_date(self.obj)
##         return (prev_marr_child_date>marr_date)

##     def get_message(self):
##         return _("Marriage before having a child from previous marriage")

## class LongWidowhood(FamilyRule):
##     def broken(self):
##         marr_date = get_marriage_date(self.obj)
##         prev_marr_spouse_death_date = get_prev_marr_spouse_death_date(self.obj)
##         birth_date = get_birth_date(self.obj)
##         return (marr_date-prev_marr_spouse_death_date>lngwdw)

##     def get_message(self):
##         return _("Long Windowhood")

class OldParent(FamilyRule):
    def __init__(self,db,obj,old_par):
        FamilyRule__init__(self,db,obj)
        self.old_par = old_par

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok and (
                father_birth_date - child_birth_date > self.old_par))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok and (
                mother_birth_date - child_birth_date > self.old_par))
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        return _("Old father")

    def mother_message(self):
        return _("Old mother")

class YoungParent(FamilyRule):
    def __init__(self,db,obj,yng_par):
        FamilyRule__init__(self,db,obj)
        self.yng_par = yng_par

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok and (
                father_birth_date - child_birth_date < self.yng_par))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok and (
                mother_birth_date - child_birth_date < self.yng_par))
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        return _("Young father")

    def mother_message(self):
        return _("Young mother")

class UnbornParent(FamilyRule):
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother)
        father_birth_date = get_birth_date(self.db,father)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok
                             and (father_birth_date > child_birth_date))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok
                             and (mother_birth_date > child_birth_date))
            if mother_broken:
                self.get_message = self.mother_message
                return True

    def father_message(self):
        return _("Unborn father")

    def mother_message(self):
        return _("Unborn mother")

class DeadParent(FamilyRule):
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_death_date = get_death_date(self.db,mother)
        father_death_date = get_death_date(self.db,father)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_death_date_ok
                             and (father_death_date < child_birth_date))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_death_date_ok
                             and (mother_death_date < child_birth_date))
            if mother_broken:
                self.get_message = self.mother_message
                return True

    def father_message(self):
        return _("Dead father")

    def mother_message(self):
        return _("Dead mother")

class LargeChildrenSpan(FamilyRule):
    def __init__(self,db,obj,cb_span):
        FamilyRule__init__(self,db,obj)
        self.cb_span = cb_span

    def broken(self):
        child_birh_dates = get_child_birth_dates(self.db,self.obj)
        child_birh_dates.sort()
        
        return (child_birh_dates[-1] - child_birh_dates[0] > self.cb_span)

    def get_message(self):
        return _("Large year span for all children")

class LargeChildrenAgeDiff(FamilyRule):
    def __init__(self,db,obj,c_space):
        FamilyRule__init__(self,db,obj)
        self.c_space = c_space

    def broken(self):
        child_birh_dates = get_child_birth_dates(self.db,self.obj)
        child_birh_dates_diff = [child_birh_dates[i+1] - child_birh_dates[i]
                                 for i in range(len(child_birh_dates)-1) ]
        
        return (max(child_birh_dates_diff) < self.c_space)

    def get_message(self):
        return _("Large age differences between children")

class TooManyChildren(PersonRule):
    def __init__(self,db,obj,mx_child_dad,mx_child_mom):
        PersonRule.__init__(self,db,obj)
        self.mx_child_dad = mx_child_dad
        self.mx_child_mom = mx_child_mom

    def broken(self):
        n_child = get_n_children(self.db,self.obj)

        if (self.obj.get_gender == RelLib.Person.MALE) \
               and (n_child > self.mx_child_dad):
            return True

        if (self.obj.get_gender == RelLib.Person.FEMALE) \
               and (n_child > self.mx_child_mom):
            return True

        return False

    def get_message(self):
        return _("Too many children")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'verify',
    category = Tool.TOOL_UTILS,
    tool_class = Verify,
    options_class = VerifyOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Verify the database"),
    description = _("Lists exceptions to assertions or checks "
                    "about the database")
    )
