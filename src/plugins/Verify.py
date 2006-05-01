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

        personList = self.db.get_person_handles(sort_handles=False)
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

        error = cStringIO.StringIO()
        warn = cStringIO.StringIO()

        if not cli:
            progress = Utils.ProgressMeter(_('Verify the database'),'')
            progress.set_pass(_('Checking data'),
                              self.db.get_number_of_people())
        
        for person_handle in personList:
            person = self.db.get_person_from_handle(person_handle)
            idstr = "%s (%s)" % (person.get_primary_name().get_name(),person.get_gramps_id())

            # individual checks
            total_children = 0
            ageatdeath = 0

            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth_handle = birth_ref.ref
            else:
                birth_handle = None

            death_ref = person.get_death_ref()
            if death_ref:
                death_handle = death_ref.ref
            else:
                death_handle = None
                
            byear = self.get_year( birth_handle )
            bapyear = 0
            dyear = self.get_year( death_handle )
            buryear = 0

            for event_ref in person.get_event_ref_list():
                if event_ref:
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if event.get_type() == RelLib.EventType.BURIAL:
                        buryear = self.get_year( event.get_handle() )
                    elif event.get_type() == RelLib.EventType.BAPTISM:
                        bapyear = self.get_year( event.get_handle() )

            if byear>0 and bapyear>0:
                if byear > bapyear:
                    if person.get_gender() == RelLib.Person.MALE:
                        error.write( _("Baptized before birth: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                    if person.get_gender() == RelLib.Person.FEMALE:
                        error.write( _("Baptized before birth: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                if byear < bapyear:
                    if person.get_gender() == RelLib.Person.MALE:
                        warn.write( _("Baptized late: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                    if person.get_gender() == RelLib.Person.FEMALE:
                        warn.write( _("Baptized late: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
            if dyear>0 and buryear>0:
                if dyear > buryear:
                    if person.get_gender() == RelLib.Person.MALE:
                        error.write( _("Buried before death: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                    if person.get_gender() == RelLib.Person.FEMALE:
                        error.write( _("Buried before death: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                if dyear < buryear:
                    if person.get_gender() == RelLib.Person.MALE:
                        warn.write( _("Buried late: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                    if person.get_gender() == RelLib.Person.FEMALE:
                        warn.write( _("Buried late: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
            if dyear>0 and (byear>dyear):
                if person.get_gender() == RelLib.Person.MALE:
                    error.write( _("Died before birth: %(male_name)s born %(byear)d, died %(dyear)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    error.write( _("Died before birth: %(female_name)s born %(byear)d, died %(dyear)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
            if dyear>0 and (bapyear>dyear):
                if person.get_gender() == RelLib.Person.MALE:
                    error.write( _("Died before baptism: %(male_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
                        'male_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    error.write( _("Died before baptism: %(female_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
                        'female_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
            if buryear>0 and (byear>buryear):
                if person.get_gender() == RelLib.Person.MALE:
                    error.write( _("Buried before birth: %(male_name)s born %(byear)d, buried %(buryear)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    error.write( _("Buried before birth: %(female_name)s born %(byear)d, buried %(buryear)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
            if buryear>0 and (bapyear>buryear):
                if person.get_gender() == RelLib.Person.MALE:
                    error.write( _("Buried before baptism: %(male_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
                        'male_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    error.write( _("Buried before baptism: %(female_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
                        'female_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
            if byear == 0 and estimate_age:
                byear = bapyear  # guess baptism = birth
            if dyear == 0 and estimate_age:
                dyear = buryear  # guess burial = death
            if byear>0 and dyear>0:
                ageatdeath = dyear - byear
            else:
                ageatdeath = 0
            if ageatdeath > oldage:
                if person.get_gender() == RelLib.Person.MALE:
                    warn.write( _("Old age: %(male_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    warn.write( _("Old age: %(female_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
    
            # gender checks

            if person.get_gender() == RelLib.Person.FEMALE:
                oldpar = oldmom
                yngpar = yngmom
            if person.get_gender() == RelLib.Person.MALE:
                oldpar = olddad
                yngpar = yngdad
            if (person.get_gender() != RelLib.Person.FEMALE) and (person.get_gender() != RelLib.Person.MALE):
                warn.write( _("Unknown gender for %s.\n") % idstr )
                oldpar = olddad
                yngpar = yngdad
            if (person.get_gender() == RelLib.Person.FEMALE) and (person.get_gender() == RelLib.Person.MALE):
                error.write( _("Ambiguous gender for %s.\n") % idstr )
                oldpar = olddad
                yngpar = yngdad
        
            # multiple parentage check
            if( len( person.get_parent_family_handle_list() ) > 1 ):
                warn.write( _("Multiple parentage for %s.\n") % idstr )

            # marriage checks
            nkids = 0
            nfam  = len( person.get_family_handle_list() )
            if nfam > wedder:
                if person.get_gender() == RelLib.Person.MALE:
                    warn.write( _("Married often: %(male_name)s married %(nfam)d times.\n") % { 
                        'male_name' : idstr, 'nfam' : nfam } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    warn.write( _("Married often: %(female_name)s married %(nfam)d times.\n") % { 
                        'female_name' : idstr, 'nfam' : nfam } )
            if ageatdeath>oldunm and nfam == 0:
                if person.get_gender() == RelLib.Person.MALE:
                    warn.write( _("Old and unmarried: %(male_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
                        'male_name' : idstr, 'ageatdeath' : ageatdeath } )
                if person.get_gender() == RelLib.Person.FEMALE:
                    warn.write( _("Old and unmarried: %(female_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
                        'female_name' : idstr, 'ageatdeath' : ageatdeath } )
            prev_cbyear=0
            prev_maryear=0
            prev_sdyear=0
            fnum = 0

            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                fnum = fnum + 1
                mother_handle = family.get_mother_handle()
                father_handle = family.get_father_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                if father_handle:
                    father = self.db.get_person_from_handle(father_handle)
                if mother_handle and father_handle:
                    if ( mother.get_gender() == father.get_gender() ) and mother.get_gender() != RelLib.Person.UNKNOWN:
                        warn.write( _("Homosexual marriage: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
                if father_handle == person.get_handle() and person.get_gender() == RelLib.Person.FEMALE:
                    error.write( _("Female husband: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
                if mother_handle == person.get_handle() and person.get_gender() == RelLib.Person.MALE:
                    error.write( _("Male wife: %s in family %s.\n") % ( idstr, family.get_gramps_id() ) )
                if father_handle == person.get_handle():
                   spouse_id = mother_handle
                else:
                   spouse_id = father_handle
                if spouse_id:
                    spouse = self.db.get_person_from_handle(spouse_id)
                    if person.get_gender() == RelLib.Person.MALE and \
                           person.get_primary_name().get_surname() == spouse.get_primary_name().get_surname():
                        warn.write( _("Husband and wife with the same surname: %s in family %s, and %s.\n") % (
                            idstr,family.get_gramps_id(), spouse.get_primary_name().get_name() ) )


                    death_ref = spouse.get_death_ref()
                    if death_ref:
                        death_handle = death_ref.ref
                    else:
                        death_handle = None

                    birth_ref = spouse.get_birth_ref()
                    if birth_ref:
                        birth_handle = birth_ref.ref
                    else:
                        birth_handle = None
                        
                    sdyear = self.get_year( death_handle )
                    sbyear = self.get_year( birth_handle )
                    if sbyear != 0 and byear != 0 and abs(sbyear-byear) > hwdif:
                        warn.write( _("Large age difference between husband and wife: %s in family %s, and %s.\n") % (
                            idstr,family.get_gramps_id(), spouse.get_primary_name().get_name() ) )
                        
                    if sdyear == 0:
                        sdyear = 0  # burial year

                    for event_ref in family.get_event_ref_list():
                        if event_ref:
                            event_handle = event_ref.ref
                            event = self.db.get_event_from_handle(event_handle)
                            if event.get_type().xml_str() == "Marriage":
                                marriage_id = event_handle
                                break
                    else:
                        marriage_id = None

                    maryear = self.get_year( marriage_id )

                    if maryear == 0 and estimate_age:   #  estimate marriage year
                        cnum=0
                        for child_ref in family.get_child_ref_list():
                            cnum = cnum + 1
                            if maryear == 0:
                                child = self.db.get_person_from_handle(child_ref.ref)
                                birth_ref = child.get_birth_ref()
                                if birth_ref:
                                    birthyear = self.get_year(birth_ref.ref)
                                else:
                                    birthyear = 0
                            if birthyear > 0:
                                maryear = birthyear-cnum

                    if maryear > 0:
                        if byear > 0:
                            marage = maryear - byear
                            if marage < 0:
                                if person.get_gender() == RelLib.Person.MALE:
                                        error.write( _("Married before birth: %(male_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
                                        'male_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                                if person.get_gender() == RelLib.Person.FEMALE:
                                    error.write( _("Married before birth: %(female_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
                                        'female_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                            else:
                                if marage < yngmar:
                                    if person.get_gender() == RelLib.Person.MALE:
                                        warn.write( _("Young marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                    if person.get_gender() == RelLib.Person.FEMALE:
                                        warn.write( _("Young marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                if marage > oldmar:
                                   if person.get_gender() == RelLib.Person.MALE:
                                        warn.write( _("Old marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                   if person.get_gender() == RelLib.Person.FEMALE:
                                        warn.write( _("Old marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                        if dyear>0 and maryear > dyear:
                            if person.get_gender() == RelLib.Person.MALE:
                                error.write( _("Married after death: %(male_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
                                    'male_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                            if person.get_gender() == RelLib.Person.FEMALE:
                                error.write( _("Married after death: %(female_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
                                    'female_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                        if prev_cbyear > maryear:
                            if person.get_gender() == RelLib.Person.MALE:
                                warn.write( _("Marriage before birth from previous family: %(male_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
                                    'male_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
                            if person.get_gender() == RelLib.Person.FEMALE:
                                warn.write( _("Marriage before birth from previous family: %(female_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
                                    'female_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
                        prev_maryear = maryear
                    else:
                        maryear = prev_maryear
                                                        
                    if maryear>0 and prev_sdyear > 0:
                        wdwyear = maryear-prev_sdyear
                        if wdwyear > lngwdw:
                            if person.get_gender() == RelLib.Person.MALE:
                                warn.write( _("Long widowhood: %s was a widower %d years before, family %s.\n") % (idstr, wdwyear, family.get_gramps_id() ) )
                            if person.get_gender() == RelLib.Person.FEMALE:
                                warn.write( _("Long widowhood: %s was a widow %d years before, family %s.\n") % (idstr, wdwyear, family.get_gramps_id() ) )

                    if fnum==nfam and dyear>0 and sdyear>0:
                        wdwyear = dyear - sdyear
                        if wdwyear > lngwdw:
                            if person.get_gender() == RelLib.Person.MALE:
                                warn.write( _("Long widowhood: %s was a widower %d years.\n") % (idstr, wdwyear) )
                            if person.get_gender() == RelLib.Person.FEMALE:
                                warn.write( _("Long widowhood: %s was a widow %d years.\n") % (idstr, wdwyear) )

                    nkids = 0
                    cbyears = []
                    
                    total_children = total_children + len(family.get_child_ref_list())
                    for child_ref in family.get_child_ref_list():
                        nkids = nkids+1
                        child = self.db.get_person_from_handle(child_ref.ref)
                        birth_ref = child.get_birth_ref()
                        if birth_ref:
                            birth_handle = birth_ref.ref
                        else:
                            birth_handle = None
                            
                        cbyear = self.get_year( birth_handle )
                        if cbyear:
                            cbyears.append(cbyear)

                        # parentage checks 
                        if byear>0 and cbyear>0:
                            bage = cbyear - byear
                            if bage > oldpar:
                                if person.get_gender() == RelLib.Person.MALE:
                                    warn.write( _("Old father: %(male_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                        'male_name' : idstr, 'bage' : bage, 'fam' : family.get_handle(), 'child' : child.get_primary_name().get_name() } ) 
                                if person.get_gender() == RelLib.Person.FEMALE:
                                    warn.write( _("Old mother: %(female_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                        'female_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } ) 
                            if bage < 0:
                                if person.get_gender() == RelLib.Person.MALE:
                                    error.write( _("Unborn father: %(male_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'byear' : byear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
                                if person.get_gender() == RelLib.Person.FEMALE:
                                    error.write( _("Unborn mother: %(female_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'byear' : byear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
                            else:
                                if bage < yngpar:
                                    if person.get_gender() == RelLib.Person.MALE:
                                        warn.write( _("Young father: %(male_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                                        'male_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } )
                                        if person.get_gender() == RelLib.Person.FEMALE:
                                            warn.write( _("Young mother: %(female_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                                        'female_name' : idstr, 'bage' : bage, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name() } )
                        if dyear>0 and cbyear>dyear:
                            if cbyear-1>dyear:
                                if person.get_gender() == RelLib.Person.MALE:
                                    error.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                                if person.get_gender() == RelLib.Person.FEMALE:
                                    error.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                            else:
                                if person.get_gender() == RelLib.Person.MALE:
                                    warn.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                                if person.get_gender() == RelLib.Person.FEMALE:
                                    warn.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_gramps_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                    
                    if cbyears:
                        cbyears.sort()
                        if (cbyears[-1] - cbyears[0]) > cbspan:
                            warn.write(_("Large year span for all children: family %s.\n") % family.get_gramps_id() )
                    if len(cbyears) > 1:
                        cby_diff = [ cbyears[i+1]-cbyears[i] for i in range(len(cbyears)-1) ]
                        if max(cby_diff) > cspace:
                            warn.write(_("Large age differences between children: family %s.\n") % family.get_gramps_id() )

            if (person.get_gender() == RelLib.Person.MALE 
                                and total_children > mxchilddad) \
                        or (person.get_gender() == RelLib.Person.FEMALE 
                                and total_children > mxchildmom):
                warn.write(_("Too many children (%(num_children)d) for %(person_name)s.\n") % {
                    'num_children' : total_children, 'person_name' : idstr })
            if not cli:
                progress.step()

        if not cli:
            progress.close()

        err_text = error.getvalue()
        warn_text = warn.getvalue()
        error.close()
        warn.close()
        
        return err_text.strip(),warn_text.strip()

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
