#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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
from gettext import gettext as _

db = None
glade_file = None
verifySettings = None

# returns the year of an event or 0 if no event==None or no year specified in the event
def get_year( event ):
    year = 0
    if event != None:
        dateObj = event.getDateObj()
        if dateObj != None:
	    year = dateObj.getYear()
    return year

def runTool(database,active_person,callback):
    global glade_file
    global db 
    global verifySettings
    
    db = database
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "verify.glade"

    verifySettings = gtk.glade.XML(glade_file,"verify_settings","gramps")
    verifySettings.signal_autoconnect({
        "destroy_passed_object" : Utils.destroy_passed_object,
        "on_verify_ok_clicked" : on_apply_clicked
        })

    Utils.set_titles(verifySettings.get_widget('verify_settings'),
                     verifySettings.get_widget('title'),
                     _('Database Verify'))


def on_apply_clicked(obj):
    global db 
    global verifySettings

    personList = db.getPersonMap().values()

    oldage = int(verifySettings.get_widget("oldage").get_text())
    yngmar = int(verifySettings.get_widget("yngmar").get_text())
    oldmar = int(verifySettings.get_widget("oldmar").get_text())
    oldmom = int(verifySettings.get_widget("oldmom").get_text())
    yngmom = int(verifySettings.get_widget("yngmom").get_text())
    olddad = int(verifySettings.get_widget("olddad").get_text())
    yngdad = int(verifySettings.get_widget("yngdad").get_text())
    wedder = int(verifySettings.get_widget("wedder").get_text())
    lngwdw = int(verifySettings.get_widget("lngwdw").get_text())
   
    oldunm = 99  # maximum age at death for unmarried person 

    error = cStringIO.StringIO()
    warn = cStringIO.StringIO()

    for person in personList:
        idstr = person.getPrimaryName().getName() + " (" + person.getId() + ")"
	
	# individual checks
	byear = get_year( person.getBirth() )
	bapyear = 0
	dyear = get_year( person.getDeath() )
	buryear = 0
	if byear>0 and bapyear>0:
	    if byear > bapyear:
	        if person.getGender() == RelLib.Person.male:
			error.write( _("Baptized before birth: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
				'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
	    	if person.getGender() == RelLib.Person.female:
			error.write( _("Baptized before birth: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
				'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
	    if byear < bapyear:
	        if person.getGender() == RelLib.Person.male:
			warn.write( _("Baptized late: %(male_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
				'male_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
	    	if person.getGender() == RelLib.Person.female:
			warn.write( _("Baptized late: %(female_name)s born %(byear)d, baptized %(bapyear)d.\n") % { 
				'female_name' : idstr, 'byear' : byear, 'bapyear' : bapyear } )
        if dyear>0 and buryear>0:
	    if dyear > buryear:
	        if person.getGender() == RelLib.Person.male:
			error.write( _("Buried before death: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
				'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
		if person.getGender() == RelLib.Person.female:
			error.write( _("Buried before death: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
				'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
	    if dyear < buryear:
	    	if person.getGender() == RelLib.Person.male:
			warn.write( _("Buried late: %(male_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
				'male_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
		if person.getGender() == RelLib.Person.female:
			warn.write( _("Buried late: %(female_name)s died %(dyear)d, buried %(buryear)d.\n") % { 
				'female_name' : idstr, 'dyear' : dyear, 'buryear' : buryear } )
	if dyear>0 and (byear>dyear):
	    if person.getGender() == RelLib.Person.male:
		    error.write( _("Died before birth: %(male_name)s born %(byear)d, died %(dyear)d.\n") % { 
		    	'male_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
	    if person.getGender() == RelLib.Person.female:
		    error.write( _("Died before birth: %(female_name)s born %(byear)d, died %(dyear)d.\n") % { 
		    	'female_name' : idstr, 'byear' : byear, 'dyear' : dyear } )
	if dyear>0 and (bapyear>dyear):
	    if person.getGender() == RelLib.Person.male:
	    	error.write( _("Died before baptism: %(male_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
			'male_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
	    if person.getGender() == RelLib.Person.female:
	    	error.write( _("Died before baptism: %(female_name)s baptized %(bapyear)d, died %(dyear)d.\n") % { 
			'female_name' : idstr, 'bapyear' : bapyear, 'dyear' : dyear } )
	if buryear>0 and (byear>buryear):
	    if person.getGender() == RelLib.Person.male:
	    	error.write( _("Buried before birth: %(male_name)s born %(byear)d, buried %(buryear)d.\n") % { 
			'male_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
	    if person.getGender() == RelLib.Person.female:
	    	error.write( _("Buried before birth: %(female_name)s born %(byear)d, buried %(buryear)d.\n") % { 
			'female_name' : idstr, 'byear' : byear, 'buryear' : buryear } )
	if buryear>0 and (bapyear>buryear):
	    if person.getGender() == RelLib.Person.male:
	    	error.write( _("Buried before baptism: %(male_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
			'male_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
	    if person.getGender() == RelLib.Person.female:
	    	error.write( _("Buried before baptism: %(female_name)s baptized %(bapyear)d, buried %(buryear)d.\n") % { 
			'female_name' : idstr, 'bapyear' : bapyear, 'buryear' : buryear } )
	if byear == 0:
	    byear = bapyear  # guess baptism = birth
	if dyear == 0:
	    dyear = buryear  # guess burial = death
	if byear>0 and dyear>0:
	    ageatdeath = dyear - byear
	else:
	    ageatdeath = 0
        if ageatdeath > oldage:
	    if person.getGender() == RelLib.Person.male:
	    	warn.write( _("Old age: %(male_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
			'male_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
	    if person.getGender() == RelLib.Person.female:
	    	warn.write( _("Old age: %(female_name)s born %(byear)d, died %(dyear)d, at the age of %(ageatdeath)d.\n") % { 
			'female_name' : idstr, 'byear' : byear, 'dyear' : dyear, 'ageatdeath' : ageatdeath } )
	    
	# gender checks

#FIXME
	if person.getGender() == RelLib.Person.female:
#	    parstr = _("mother ")
	    oldpar = oldmom
	    yngpar = yngmom
#	    waswidstr = _(" was a widow ")
	if person.getGender() == RelLib.Person.male:
#	    parstr = _("father ")
	    oldpar = olddad
	    yngpar = yngdad
#	    waswidstr = _(" was a widower ")
	if (person.getGender() != RelLib.Person.female) and (person.getGender() != RelLib.Person.male):
	    warn.write( _("Unknown gender for %s.\n") % idstr )
#	    parstr = _("parent ")
	    oldpar = olddad
	    yngpar = yngdad
#	    waswidstr = _(" was a widow ")
	if (person.getGender() == RelLib.Person.female) and (person.getGender() == RelLib.Person.male):
	    error.write( _("Ambiguous gender for %s.\n") % idstr )
#	    parstr = _("parent ")
	    oldpar = olddad
	    yngpar = yngdad
#	    waswidstr = _(" was a widow ")
	    
	# multiple parentage check
	if( len( person.getParentList() ) > 1 ):
	    warn.write( _("Multiple parentage for %s.\n") % idstr )

        # marriage checks
	nkids = 0
	nfam  = len( person.getFamilyList() )
	if nfam > wedder:
	    if person.getGender() == RelLib.Person.male:
	    	warn.write( _("Married often: %(male_name)s married %(nfam)d times.\n") % { 
			'male_name' : idstr, 'nfam' : nfam } )
	    if person.getGender() == RelLib.Person.female:
	    	warn.write( _("Married often: %(female_name)s married %(nfam)d times.\n") % { 
			'female_name' : idstr, 'nfam' : nfam } )
	if ageatdeath>oldunm and nfam == 0:
	    if person.getGender() == RelLib.Person.male:
	    	warn.write( _("Old and unmarried: %(male_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
			'male_name' : idstr, 'ageatdeath' : ageatdeath } )
	    if person.getGender() == RelLib.Person.female:
	    	warn.write( _("Old and unmarried: %(female_name)s died unmarried, at the age of %(ageatdeath)d years.\n") % { 
			'female_name' : idstr, 'ageatdeath' : ageatdeath } )
	first_cbyear = 99999
	last_cbyear=0
	prev_cbyear=0
	prev_maryear=0
	prev_sdyear=0
	fnum = 0
	for family in person.getFamilyList():
	    fnum = fnum + 1
	    mother = family.getMother()
	    father = family.getFather()
	    if mother!=None and father!=None:
	        if mother.getGender() == father.getGender():
		    warn.write( _("Homosexual marriage: %s in family %s.\n") % ( idstr, family.getId() ) )
	    if family.getFather() == person and person.getGender() == RelLib.Person.female:
	        error.write( _("Female husband: %s in family %s.\n") % ( idstr, family.getId() ) )
	    if family.getMother() == person and person.getGender() == RelLib.Person.male:
	        error.write( _("Male wife: %s in family %s.\n") % ( idstr, family.getId() ) )
	    if family.getFather() == person:
	       spouse = family.getMother()
	    else:
	       spouse = family.getFather()
	    if spouse != None:
	        if person.getGender() == RelLib.Person.male and \
		   person.getPrimaryName().getSurname() == spouse.getPrimaryName().getSurname():
		    warn.write( _("Husband and wife with the same surname: %s in family %s, and %s.\n") % ( idstr,family.getId(), spouse.getPrimaryName().getName() ) )
	        sdyear = get_year( spouse.getDeath() )
		if sdyear == 0:
		    sdyear = 0  # burial year
		maryear = get_year( family.getMarriage() )
		if maryear == 0:   #  estimate marriage year
		    cnum=0
		    for child in family.getChildList():
		        cnum = cnum + 1
		        if maryear == 0:
			    birthyear = get_year( child.getBirth() )
			    if birthyear > 0:
			        maryear = birthyear-cnum
		
		if maryear > 0:
		    if byear > 0:
		        marage = maryear - byear
			if marage < 0:
			    if person.getGender() == RelLib.Person.male:
			    	error.write( _("Married before birth: %(male_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
					'male_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName() } )
			    if person.getGender() == RelLib.Person.female:
			    	error.write( _("Married before birth: %(female_name)s born %(byear)d, married %(maryear)d to %(spouse)s.\n") %  { 
					'female_name' : idstr, 'byear' : byear, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName() } )
			else:
			    if marage < yngmar:
			       if person.getGender() == RelLib.Person.male:
			       	warn.write( _("Young marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
					'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.getPrimaryName().getName() } )
			       if person.getGender() == RelLib.Person.female:
			       	warn.write( _("Young marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
					'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.getPrimaryName().getName() } )
			    if marage > oldmar:
			       if person.getGender() == RelLib.Person.male:
			       	warn.write( _("Old marriage: %(male_name)s married at age %(marage)d to %(spouse)s.\n") % { 
					'male_name' : idstr, 'marage' : marage, 'spouse' : spouse.getPrimaryName().getName() } )
			       if person.getGender() == RelLib.Person.female:
			       	warn.write( _("Old marriage: %(female_name)s married at age %(marage)d to %(spouse)s.\n") % { 
					'female_name' : idstr, 'marage' : marage, 'spouse' : spouse.getPrimaryName().getName() } )
		    if dyear>0 and maryear > dyear:
		        if person.getGender() == RelLib.Person.male:
				error.write( _("Married after death: %(male_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
					'male_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName() } )
		        if person.getGender() == RelLib.Person.female:
				error.write( _("Married after death: %(female_name)s died %(dyear)d, married %(maryear)d to %(spouse)s.\n") % { 
					'female_name' : idstr, 'dyear' : dyear, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName() } )
		    if prev_cbyear > maryear:
		        if person.getGender() == RelLib.Person.male:
				warn.write( _("Marriage before birth from previous family: %(male_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
					'male_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName(), 'prev_cbyear' : prev_cbyear } )
		        if person.getGender() == RelLib.Person.female:
				warn.write( _("Marriage before birth from previous family: %(female_name)s married %(maryear)d to %(spouse)s, previous birth %(prev_cbyear)d.\n") % { 
					'female_name' : idstr, 'maryear' : maryear, 'spouse' : spouse.getPrimaryName().getName(), 'prev_cbyear' : prev_cbyear } )
		    prev_maryear = maryear
		else:
		    maryear = prev_maryear
		
		if maryear>0 and prev_sdyear > 0:
		    wdwyear = maryear-prev_sdyear
		    if wdwyear > lngwdw:
		        if person.getGender() == RelLib.Person.male:
				warn.write( _("Long widowhood: %s was a widower %d years before, family %s.\n") % (idstr, wdwyear, family.getId() ) )
		        if person.getGender() == RelLib.Person.female:
				warn.write( _("Long widowhood: %s was a widow %d years before, family %s.\n") % (idstr, wdwyear, family.getId() ) )
		
		if fnum==nfam and dyear>0 and sdyear>0:
		    wdwyear = dyear - sdyear
		    if wdwyear > lngwdw:
		        if person.getGender() == RelLib.Person.male:
				warn.write( _("Long widowhood: %s was a widower %d years.\n") % (idstr, wdwyear) )
		        if person.getGender() == RelLib.Person.female:
				warn.write( _("Long widowhood: %s was a widow %d years.\n") % (idstr, wdwyear) )

		nkids = 0
		for child in family.getChildList():
		    nkids = nkids+1
		    cbyear = get_year( child.getBirth() )
		    if cbyear>0 and cbyear < first_cbyear:
		        first_cbyear = cbyear
		    if cbyear>last_cbyear:
		        last_cbyear = cbyear
		    # parentage checks 
		    if byear>0 and cbyear>0:
		        bage = cbyear - byear
		        if bage > oldpar:
		        	if person.getGender() == RelLib.Person.male:
		        	    warn.write( _("Old father: %(male_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
		        	        'male_name' : idstr, 'bage' : bage, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName() } ) 
		        	if person.getGender() == RelLib.Person.female:
		        	    warn.write( _("Old mother: %(female_name)s at age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
		        	        'female_name' : idstr, 'bage' : bage, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName() } ) 
			if bage < 0:
				if person.getGender() == RelLib.Person.male:
					error.write( _("Unborn father: %(male_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'male_name' : idstr, 'byear' : byear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear } )
				if person.getGender() == RelLib.Person.female:
					error.write( _("Unborn mother: %(female_name)s born %(byear)d, in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'female_name' : idstr, 'byear' : byear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear } )
			else:
				if bage < yngpar:
					if person.getGender() == RelLib.Person.male:
						warn.write( _("Young father: %(male_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
							'male_name' : idstr, 'bage' : bage, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName() } )
					if person.getGender() == RelLib.Person.female:
						warn.write( _("Young mother: %(female_name)s at the age of %(bage)d in family %(fam)s had a child %(child)s.\n") % { 
							'female_name' : idstr, 'bage' : bage, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName() } )
		    if dyear>0 and cbyear>dyear:
		    	if cbyear-1>dyear:
		    		if person.getGender() == RelLib.Person.male:
		    			error.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'male_name' : idstr, 'dyear' : dyear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear} )
		    		if person.getGender() == RelLib.Person.female:
		    			error.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'female_name' : idstr, 'dyear' : dyear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear} )
		    	else:
		    		if person.getGender() == RelLib.Person.male:
		    			warn.write( _("Dead father: %(male_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'male_name' : idstr, 'dyear' : dyear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear} )
		    		if person.getGender() == RelLib.Person.female:
		    			warn.write( _("Dead mother: %(female_name)s died %(dyear)d, but in family %(fam)s had a child %(child)s born %(cbyear)d.\n") % { 
						'female_name' : idstr, 'dyear' : dyear, 'fam' : family.getId(), 'child' : child.getPrimaryName().getName(), 'cbyear' : cbyear} )
		    	    
	
    text = ""
    if error != "":
        text = _("ERRORS:\n") + error.getvalue() + "\n" 
    if warn != "":
        text = _("WARNINGS:\n") + warn.getvalue()
	    
    error.close()
    warn.close()
    
    verifyResult = gtk.glade.XML(glade_file,"verify_result","gramps")
    Utils.set_titles(verifyResult.get_widget('verify_result'),
                     verifyResult.get_widget('title'),
                     _('Database Verify'))
    
    verifyResult.signal_autoconnect({
        "destroy_passed_object" : Utils.destroy_passed_object,
        })
    top = verifyResult.get_widget("verify_result")
    textwindow = verifyResult.get_widget("textwindow")
    textwindow.get_buffer().set_text(text)
    top.show()
    
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

