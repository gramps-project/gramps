#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

#
# Modified by Alex Roitman to enable translation of warnings and errors.
# Modified further to use cStringIO object. 
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

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gnome.ui import *
import gtk
import gtk.glade 

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import RelLib
import Utils
import Gregorian

from gettext import gettext as _


def runTool(database,active_person,callback,parent=None):
    Verify(database,active_person,parent)

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
class Verify:
    def __init__(self,database,active_person,parent):
        self.db = database
        self.parent = parent
        self.win_key = self

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_settings","gramps")
        self.top.signal_autoconnect({
            "destroy_passed_object"  : self.close,
            "on_verify_delete_event" : self.on_delete_event,
            "on_verify_ok_clicked"   : self.on_apply_clicked
        })

        self.window = self.top.get_widget('verify_settings')
        Utils.set_titles(self.window,
                     self.top.get_widget('title'),
                     _('Database Verify'))

        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Database Verify'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def get_year(self,event_id):
        """
        Returns the year of an event (by its id) or 0 if no event_id 
        or no year  specified in the event
        """
        year = 0
        if event_id:
            event = self.db.find_event_from_id(event_id)
            dateObj = event.get_date_object()
            if dateObj:
                if dateObj.get_calendar().NAME != Gregorian.Gregorian:
                    dateObj.set_calendar(Gregorian.Gregorian)
                year = dateObj.get_year()
        return year

    def on_apply_clicked(self,obj):

        personList = self.db.get_person_keys()

        oldage = int(self.top.get_widget("oldage").get_text())
        hwdif = int(self.top.get_widget("hwdif").get_text())
        cspace = int(self.top.get_widget("cspace").get_text())
        cbspan = int(self.top.get_widget("cbspan").get_text())
        yngmar = int(self.top.get_widget("yngmar").get_text())
        oldmar = int(self.top.get_widget("oldmar").get_text())
        oldmom = int(self.top.get_widget("oldmom").get_text())
        yngmom = int(self.top.get_widget("yngmom").get_text())
        olddad = int(self.top.get_widget("olddad").get_text())
        yngdad = int(self.top.get_widget("yngdad").get_text())
        wedder = int(self.top.get_widget("wedder").get_text())
        lngwdw = int(self.top.get_widget("lngwdw").get_text())
        estimate_age = self.top.get_widget("estimate").get_active()

        oldunm = 99  # maximum age at death for unmarried person 

        error = cStringIO.StringIO()
        warn = cStringIO.StringIO()

        for person_id in personList:
            person = self.db.try_to_find_person_from_id(person_id)
            idstr = "%s (%s)" % (person.get_primary_name().get_name(),person_id)

            # individual checks
            ageatdeath = 0
            byear = self.get_year( person.get_birth_id() )
            bapyear = 0
            dyear = self.get_year( person.get_death_id() )
            buryear = 0
            if byear>0 and bapyear>0:
                if byear > bapyear:
                    if person.get_gender() == RelLib.Person.male:
                        error.write( _("Baptized before birth: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                    if person.get_gender() == RelLib.Person.female:
                        error.write( _("Baptized before birth: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                if byear < bapyear:
                    if person.get_gender() == RelLib.Person.male:
                        warn.write( _("Baptized late: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
                    if person.get_gender() == RelLib.Person.female:
                        warn.write( _("Baptized late: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
                            'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
            if dyear>0 and buryear>0:
                if dyear > buryear:
                    if person.get_gender() == RelLib.Person.male:
                        error.write( _("Buried before death: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                    if person.get_gender() == RelLib.Person.female:
                        error.write( _("Buried before death: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                if dyear < buryear:
                    if person.get_gender() == RelLib.Person.male:
                        warn.write( _("Buried late: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
                    if person.get_gender() == RelLib.Person.female:
                        warn.write( _("Buried late: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
                            'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
            if dyear>0 and (byear>dyear):
                if person.get_gender() == RelLib.Person.male:
                    error.write( _("Died before birth: %(male_name)s born %(byear)d, died %(dyear)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
                if person.get_gender() == RelLib.Person.female:
                    error.write( _("Died before birth: %(female_name)s born %(byear)d, died %(dyear)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
            if dyear>0 and (bapyear>dyear):
                if person.get_gender() == RelLib.Person.male:
                    error.write( _("Died before baptism: %(male_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
                        'male_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
                if person.get_gender() == RelLib.Person.female:
                    error.write( _("Died before baptism: %(female_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
                        'female_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
            if buryear>0 and (byear>buryear):
                if person.get_gender() == RelLib.Person.male:
                    error.write( _("Buried before birth: %(male_name)s born %(byear)d, buried %(buryear)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
                if person.get_gender() == RelLib.Person.female:
                    error.write( _("Buried before birth: %(female_name)s born %(byear)d, buried %(buryear)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
            if buryear>0 and (bapyear>buryear):
                if person.get_gender() == RelLib.Person.male:
                    error.write( _("Buried before baptism: %(male_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
                        'male_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
                if person.get_gender() == RelLib.Person.female:
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
                if person.get_gender() == RelLib.Person.male:
                    warn.write( _("Old age: %(male_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
                        'male_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
                if person.get_gender() == RelLib.Person.female:
                    warn.write( _("Old age: %(female_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
                        'female_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
    
            # gender checks

            if person.get_gender() == RelLib.Person.female:
                oldpar = oldmom
                yngpar = yngmom
            if person.get_gender() == RelLib.Person.male:
                oldpar = olddad
                yngpar = yngdad
            if (person.get_gender() != RelLib.Person.female) and (person.get_gender() != RelLib.Person.male):
                warn.write( _("Unknown gender for %s.\n") % idstr )
                oldpar = olddad
                yngpar = yngdad
            if (person.get_gender() == RelLib.Person.female) and (person.get_gender() == RelLib.Person.male):
                error.write( _("Ambiguous gender for %s.\n") % idstr )
                oldpar = olddad
                yngpar = yngdad
        
            # multiple parentage check
            if( len( person.get_parent_family_id_list() ) > 1 ):
                warn.write( _("Multiple parentage for %s.\n") % idstr )

            # marriage checks
            nkids = 0
            nfam  = len( person.get_family_id_list() )
            if nfam > wedder:
                if person.get_gender() == RelLib.Person.male:
                    warn.write( _("Married often: %(male_name)s married %(nfam)d times.\n") % { 
                        'male_name' : idstr, 'nfam' : nfam } )
                if person.get_gender() == RelLib.Person.female:
                    warn.write( _("Married often: %(female_name)s married %(nfam)d times.\n") % { 
                        'female_name' : idstr, 'nfam' : nfam } )
            if ageatdeath>oldunm and nfam == 0:
                if person.get_gender() == RelLib.Person.male:
                    warn.write( _("Old and unmarried: %(male_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
                        'male_name' : idstr, 'ageatdeath' : ageatdeath } )
                if person.get_gender() == RelLib.Person.female:
                    warn.write( _("Old and unmarried: %(female_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
                        'female_name' : idstr, 'ageatdeath' : ageatdeath } )
            prev_cbyear=0
            prev_maryear=0
            prev_sdyear=0
            fnum = 0
            for family_id in person.get_family_id_list():
                family = self.db.find_family_from_id(family_id)
                fnum = fnum + 1
                mother_id = family.get_mother_id()
                father_id = family.get_father_id()
                if mother_id:
                    mother = self.db.try_to_find_person_from_id(mother_id)
                if father_id:
                    father = self.db.try_to_find_person_from_id(father_id)
                if mother_id and father_id:
                    if ( mother.get_gender() == father.get_gender() ) and mother.get_gender() != RelLib.Person.unknown:
                        warn.write( _("Homosexual marriage: %s in family %s.\n") % ( idstr, family.get_id() ) )
                if father_id == person.get_id() and person.get_gender() == RelLib.Person.female:
                    error.write( _("Female husband: %s in family %s.\n") % ( idstr, family.get_id() ) )
                if mother_id == person.get_id() and person.get_gender() == RelLib.Person.male:
                    error.write( _("Male wife: %s in family %s.\n") % ( idstr, family.get_id() ) )
                if father_id == person.get_id():
                   spouse_id = mother_id
                else:
                   spouse_id = father_id
                if spouse_id:
                    spouse = self.db.try_to_find_person_from_id(spouse_id)
                    if person.get_gender() == RelLib.Person.male and \
                           person.get_primary_name().get_surname() == spouse.get_primary_name().get_surname():
                        warn.write( _("Husband and wife with the same surname: %s in family %s, and %s.\n") % (
                            idstr,family.get_id(), spouse.get_primary_name().get_name() ) )
                    sdyear = self.get_year( spouse.get_death_id() )
                    sbyear = self.get_year( spouse.get_birth_id() )
                    if abs(sbyear-byear) > hwdif:
                        warn.write( _("Large age difference between husband and wife: %s in family %s, and %s.\n") % (
                            idstr,family.get_id(), spouse.get_primary_name().get_name() ) )
                        
                    if sdyear == 0:
                        sdyear = 0  # burial year

                    for event_id in family.get_event_list():
                        if event_id:
                            event = self.db.find_event_from_id(event_id)
                            if event.get_name() == "Marriage":
                                marriage_id = event_id
                                break
                    else:
                        marriage_id = None

                    maryear = self.get_year( marriage_id )

                    if maryear == 0 and estimate_age:   #  estimate marriage year
                        cnum=0
                        for child_id in family.get_child_id_list():
                            cnum = cnum + 1
                            if maryear == 0:
                                child = self.db.try_to_find_person_from_id(child_id)
                                birthyear = self.get_year( child.get_birth_id() )
                            if birthyear > 0:
                                maryear = birthyear-cnum

                    if maryear > 0:
                        if byear > 0:
                            marage = maryear - byear
                            if marage < 0:
                                if person.get_gender() == RelLib.Person.male:
                                        error.write( _("Married before birth: %(male_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
                                        'male_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                                if person.get_gender() == RelLib.Person.female:
                                    error.write( _("Married before birth: %(female_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
                                        'female_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                            else:
                                if marage < yngmar:
                                    if person.get_gender() == RelLib.Person.male:
                                        warn.write( _("Young marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                    if person.get_gender() == RelLib.Person.female:
                                        warn.write( _("Young marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                if marage > oldmar:
                                   if person.get_gender() == RelLib.Person.male:
                                        warn.write( _("Old marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                                   if person.get_gender() == RelLib.Person.female:
                                        warn.write( _("Old marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
                                            'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.get_primary_name().get_name() } )
                        if dyear>0 and maryear > dyear:
                            if person.get_gender() == RelLib.Person.male:
                                error.write( _("Married after death: %(male_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
                                    'male_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                            if person.get_gender() == RelLib.Person.female:
                                error.write( _("Married after death: %(female_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
                                    'female_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name() } )
                        if prev_cbyear > maryear:
                            if person.get_gender() == RelLib.Person.male:
                                warn.write( _("Marriage before birth from previous family: %(male_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
                                    'male_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
                            if person.get_gender() == RelLib.Person.female:
                                warn.write( _("Marriage before birth from previous family: %(female_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
                                    'female_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.get_primary_name().get_name(), 'prev_cbyear' : prev_cbyear } )
                        prev_maryear = maryear
                    else:
                        maryear = prev_maryear
                                                        
                    if maryear>0 and prev_sdyear > 0:
                        wdwyear = maryear-prev_sdyear
                        if wdwyear > lngwdw:
                            if person.get_gender() == RelLib.Person.male:
                                warn.write( _("Long widowhood: %s was a widower %d years before, family %s.\n") % (idstr, wdwyear, family.get_id() ) )
                            if person.get_gender() == RelLib.Person.female:
                                warn.write( _("Long widowhood: %s was a widow %d years before, family %s.\n") % (idstr, wdwyear, family.get_id() ) )

                    if fnum==nfam and dyear>0 and sdyear>0:
                        wdwyear = dyear - sdyear
                        if wdwyear > lngwdw:
                            if person.get_gender() == RelLib.Person.male:
                                warn.write( _("Long widowhood: %s was a widower %d years.\n") % (idstr, wdwyear) )
                            if person.get_gender() == RelLib.Person.female:
                                warn.write( _("Long widowhood: %s was a widow %d years.\n") % (idstr, wdwyear) )

                    nkids = 0
                    cbyears = []
                    for child_id in family.get_child_id_list():
                        nkids = nkids+1
                        child = self.db.try_to_find_person_from_id(child_id)
                        cbyear = self.get_year( child.get_birth_id() )
                        if cbyear:
                            cbyears.append(cbyear)

                        # parentage checks 
                        if byear>0 and cbyear>0:
                            bage = cbyear - byear
                            if bage > oldpar:
                                if person.get_gender() == RelLib.Person.male:
                                    warn.write( _("Old father: %(male_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                        'male_name' : idstr, 'bage' : bage, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name() } ) 
                                if person.get_gender() == RelLib.Person.female:
                                    warn.write( _("Old mother: %(female_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                        'female_name' : idstr, 'bage' : bage, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name() } ) 
                            if bage < 0:
                                if person.get_gender() == RelLib.Person.male:
                                    error.write( _("Unborn father: %(male_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'byear' : byear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
                                if person.get_gender() == RelLib.Person.female:
                                    error.write( _("Unborn mother: %(female_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'byear' : byear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear } )
                            else:
                                if bage < yngpar:
                                    if person.get_gender() == RelLib.Person.male:
                                        warn.write( _("Young father: %(male_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                                        'male_name' : idstr, 'bage' : bage, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name() } )
                                        if person.get_gender() == RelLib.Person.female:
                                            warn.write( _("Young mother: %(female_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
                                                        'female_name' : idstr, 'bage' : bage, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name() } )
                        if dyear>0 and cbyear>dyear:
                            if cbyear-1>dyear:
                                if person.get_gender() == RelLib.Person.male:
                                    error.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                                if person.get_gender() == RelLib.Person.female:
                                    error.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                            else:
                                if person.get_gender() == RelLib.Person.male:
                                    warn.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'male_name' : idstr, 'dyear' : dyear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                                if person.get_gender() == RelLib.Person.female:
                                    warn.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
                                                'female_name' : idstr, 'dyear' : dyear, 'fam' : family.get_id(), 'child' : child.get_primary_name().get_name(), 'cbyear' : cbyear} )
                    
                    if cbyears:
                        cbyears.sort()
                        if (cbyears[-1] - cbyears[0]) > cbspan:
                            warn.write(_("Large year span for all children: family %s.\n") % family.get_id() )
                    if len(cbyears) > 1:
                        cby_diff = [ cbyears[i+1]-cbyears[i] for i in range(len(cbyears)-1) ]
                        if max(cby_diff) > cspace:
                            warn.write(_("Large age differences between children: family %s.\n") % family.get_id() )

        text = ""
        if error:
            text = _("ERRORS:\n") + error.getvalue() + "\n" 
        if warn:
            text = _("WARNINGS:\n") + warn.getvalue()
            
        error.close()
        warn.close()
    
        top = gtk.glade.XML(self.glade_file,"verify_result","gramps")
        Utils.set_titles(top.get_widget('verify_result'),
                     top.get_widget('title'),
                     _('Database Verify'))
    
        top.signal_autoconnect({
            "destroy_passed_object"  : self.close_result,
            "on_result_delete_event" : self.on_result_delete_event,
        })
    
        self.topwin = top.get_widget("verify_result")
        self.win_result_key = self.topwin
        textwindow = top.get_widget("textwindow")
        textwindow.get_buffer().set_text(text)
        
        self.add_result_to_menu()
        self.topwin.show()
    
    def on_result_delete_event(self,obj,b):
        self.remove_result_from_menu()

    def close_result(self,obj):
        self.remove_result_from_menu()
        self.topwin.destroy()

    def add_result_to_menu(self):
        self.parent.child_windows[self.win_result_key] = self.topwin
        self.result_parent_menu_item = gtk.MenuItem(_('Database Verify results'))
        self.result_parent_menu_item.connect("activate",self.present_result)
        self.result_parent_menu_item.show()
        self.parent.winsmenu.append(self.result_parent_menu_item)

    def remove_result_from_menu(self):
        del self.parent.child_windows[self.win_result_key]
        self.result_parent_menu_item.destroy()

    def present_result(self,obj):
        self.topwin.present()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Verify the database"),
    category=_("Utilities"),
    description=_("Lists exceptions to assertions or checks about the database")
    )
