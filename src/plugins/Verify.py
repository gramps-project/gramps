#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
#

"View/Verify"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os

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
from intl import gettext as _

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

    verifySettings = gtk.glade.XML(glade_file,"verify_settings")
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

    error = ""
    warn  = ""

    for person in personList:
        idstr = person.getId() + " " +person.getPrimaryName().getName()
	
	# individual checks
	byear = get_year( person.getBirth() )
	bapyear = 0
	dyear = get_year( person.getDeath() )
	buryear = 0
	if byear>0 and bapyear>0:
	    if byear > bapyear:
	        error = error + _("Baptized before birth %s born %d baptized %d.\n") % (idstr, byear, bapyear) 
	    if byear < bapyear:
	        warn = warn + _("Baptized late %s born %d baptized %d.\n") % (idstr, byear, bapyear) 
        if dyear>0 and buryear>0:
	    if dyear > buryear:
	        error = error + _("Buried before death %s died %d buried %d.\n") % (idstr, dyear, buryear) 
	    if dyear < buryear:
	        warn = warn + _("Buried late %s died %d buried %d.\n") % (idstr, dyear, buryear) 
	if dyear>0 and (byear>dyear):
	    error = error + _("Died before birth %s born %d died %d.\n") % (idstr, byear, dyear) 
	if dyear>0 and (bapyear>dyear):
	    error = error + _("Died before birth %s baptized %d died %d.\n") % (idstr, bapyear, dyear) 
	if buryear>0 and (byear>buryear):
	    error = error + _("Buried before birth %s born %d died %d.\n") % (idstr, byear, buryear) 
	if buryear>0 and (bapyear>buryear):
	    error = error + _("Buried before birth %s baptized %d died %d.\n") % (idstr, bapyear, buryear) 
	if byear == 0:
	    byear = bapyear  # guess baptism = birth
	if dyear == 0:
	    dyear = buryear  # guess burial = death
	if byear>0 and dyear>0:
	    ageatdeath = dyear - byear
	else:
	    ageatdeath = 0
        if ageatdeath > oldage:
	    warn = warn + _("Old age %s born %d died %d age %d.\n") % (idstr, byear, dyear, ageatdeath)
	    
	# gender checks
	if person.getGender() == RelLib.Person.female:
	    parstr = _("mother ")
	    oldpar = oldmom
	    yngpar = yngmom
	    waswidstr = _(" was a widow ")
	if person.getGender() == RelLib.Person.male:
	    parstr = _("father ")
	    oldpar = olddad
	    yngpar = yngdad
	    waswidstr = _(" was a widower ")
	if (person.getGender() != RelLib.Person.female) and (person.getGender() != RelLib.Person.male):
	    warn = warn + _("Unknown gender %s.\n") % idstr
	    parstr = _("parent ")
	    oldpar = olddad
	    yngpar = yngdad
	    waswidstr = _(" was a widow ")
	if (person.getGender() == RelLib.Person.female) and (person.getGender() == RelLib.Person.male):
	    error = error + _("Ambigous gender %s.\n") % idstr
	    parstr = _("parent ")
	    oldpar = olddad
	    yngpar = yngdad
	    waswidstr = _(" was a widow ")
	    
	# multiple parentage check
	if( len(person.getParentList()) > 1 ):
	    warn = warn + _("Multiple parentage %s.\n") % idstr

        # marriage checks
	nkids = 0
	nfam  = len( person.getFamilyList() )
	if nfam > wedder:
	    warn = warn + _("Married often %s married %d times.\n") % (idstr, nfam)
	if ageatdeath>oldunm and nfam == 0:
	    warn = warn + _("Old and unmarried %s died unmarried aged %d years.\n") % (idstr, ageatdeath)
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
		    warn = warn + _("Homosexual marriage %s family %s.\n") % (idstr, family.getId())
	    if family.getFather() == person and person.getGender() == RelLib.Person.female:
	        error = error + _("Female husband %s family %s.\n") % (idstr, family.getId())
	    if family.getMother() == person and person.getGender() == RelLib.Person.male:
	        error = error + _("Male wife %s family %s.\n") % (idstr, family.getId())
	    if family.getFather() == person:
	       spouse = family.getMother()
	    else:
	       spouse = family.getFather()
	    if spouse != None:
	        if person.getGender() == RelLib.Person.male and \
		   person.getPrimaryName().getSurname() == spouse.getPrimaryName().getSurname():
		    warn = warn + _("Husband and wife with same surname %s family %s %s.\n") % ( idstr,family.getId(), spouse.getPrimaryName().getName())
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
			    error = error + _("Married before birth %s born %d married %d to %s.\n") % (idstr, byear, maryear, spouse.getPrimaryName().getName())
			else:
			    if marage < yngmar:
			       warn = warn + _("Young marriage %s married at age %d to %s.\n") % (idstr, marage, spouse.getPrimaryName().getName())
			    if marage > oldmar:
			       warn = warn + _("Old marriage %s married at age %d to %s.\n") % (idstr, marage, spouse.getPrimaryName().getName())
		    if dyear>0 and maryear > dyear:
		        error = error + _("Married after death %s died %d married %d to %s.\n") % (idstr, dyear, maryear, spouse.getPrimaryName().getName())
		    if prev_cbyear > maryear:
		        warn = warn + _("Marriage before birth from previous family %s married %d to %s previous birth %d.\n") % (idstr, maryear, spouse.getPrimaryName().getName(), prev_cbyear)
		    prev_maryear = maryear
		else:
		    maryear = prev_maryear
		
		if maryear>0 and prev_sdyear > 0:
		    wdwyear = maryear-prev_sdyear
		    if wdwyear > lngwdw:
		        warn = warn + _("Long widowhood %s %s %d years before family %s.\n") % (idstr, waswidstr, wdwyear,family.getId() ) 
		
		if fnum==nfam and dyear>0 and sdyear>0:
		    wdwyear = dyear - sdyear
		    if wdwyear > lngwdw:
		        warn =  warn + _("Long widowhood %s %s %d years.\n") % (idstr, waswidstr, wdwyear) 

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
			    warn = warn + _("Old %s %s age %d family %s child %s.\n") % (parstr, idstr, bage, family.getId(), child.getPrimaryName().getName())
			if bage < 0:
			    error = error + _("Unborn %s %s born %d family %s child %s born %d.\n") % (parstr, idstr, byear, family.getId(), child.getPrimaryName().getName(), cbyear)
			else:
			    if bage < yngpar:
			        warn = warn + _("Young %s %s age %d family %s child %s.\n") % (parstr, idstr, bage, family.getId(), child.getPrimaryName().getName())
		    if dyear>0 and cbyear>dyear:
		        if person.getGender() == RelLib.Person.male:
			    if cbyear-1>dyear:
			        error = error + _("Dead %s %s died %d family %s child %s born %d.\n") % (parstr, idstr, dyear, family.getId(), child.getPrimaryName().getName(), cbyear)
			    else:
			        warn = warn + _("Dead %s %s died %d family %s child %s born %d.\n") % (parstr, idstr, dyear, family.getId(), child.getPrimaryName().getName(), cbyear)
			else:
			    error = error + _("Dead %s %s died %d family %s child %s born %d.\n") % (parstr, idstr, dyear, family.getId(), child.getPrimaryName().getName(), cbyear)
		    	    
	
    text = ""
    if error != "":
        text = _("ERRORS:\n") + error + "\n" 
    if warn != "":
        text = _("WARNINGS:\n") + warn
	    
    verifyResult = gtk.glade.XML(glade_file,"verify_result")
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
    description=_("List exceptions to assertions or checks about the database")
    )

