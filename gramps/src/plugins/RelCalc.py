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

"Utilities/Relationship calculator"

import os

from gtk import *
from gnome.ui import *
from libglade import *

import RelLib
import sort
import intl
import utils

_ = intl.gettext

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def filter(person,index,list,map):
    if person == None:
        return
    list.append(person)
    map[person] = index
    
    family = person.getMainFamily()
    if family != None:
        filter(family.getFather(),index+1,list,map)
        filter(family.getMother(),index+1,list,map)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_cousin(f,s,level,removed):
    if level == 1:
        if removed == 0:
            return "%s is the first cousin of %s." %(f,s)
        elif removed == 1:
            return "%s is the first cousin once removed of %s." %(f,s)
        elif removed == 2:
            return "%s is the first cousin twice removed of %s." %(f,s)
        else:
            return "%s is the first cousin %d times removed of %s." % (f,s,removed)
    elif level == 2:
        if removed == 0:
            return "%s is the second cousin of %s." %(f,s)
        elif removed == 1:
            return "%s is the second cousin once removed of %s." %(f,s)
        elif removed == 2:
            return "%s is the second cousin twice removed of %s." %(f,s)
        else:
            return "%s is the second cousin %d times removed of %s." % (f,s,removed)
    elif level == 3:
        if removed == 0:
            return "%s is the third cousin of %s." %(f,s)
        elif removed == 1:
            return "%s is the third cousin once removed of %s." %(f,s)
        elif removed == 2:
            return "%s is the third cousin twice removed of %s." %(f,s)
        else:
            return "%s is the third cousin %d times removed of %s." % (f,s,removed)
    else:
        if removed == 0:
            return "%s is the %dth cousin of %s." %(f,level,s)
        elif removed == 1:
            return "%s is the %dth cousin once removed of %s." %(f,level,s)
        elif removed == 2:
            return "%s is the %dth cousin twice removed of %s." %(f,level,s)
        else:
            return "%s is the %dth cousin %d times removed of %s." % (f,level,s,removed)

def get_father(f,s,level):
    if level == 1:
        return "%s is the father of %s." % (s,f)
    elif level == 2:
        return "%s is the grandfather of %s." % (s,f)
    elif level == 3:
        return "%s is the great grandfather of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great grandfather of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great grandfather of %s." % (s,f)
    else:
        return "%s is the %dth great grandfather of %s." % (s,level-2,f)

def get_son(f,s,level):
    if level == 1:
        return "%s is the son of %s." % (s,f)
    elif level == 2:
        return "%s is the grandson of %s." % (s,f)
    elif level == 3:
        return "%s is the great grandson of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great grandson of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great grandson of %s." % (s,f)
    else:
        return "%s is the %dth great grandson of %s." % (s,level-2,f)

def get_mother(f,s,level):
    if level == 1:
        return "%s is the mother of %s." % (s,f)
    elif level == 2:
        return "%s is the grandmother of %s." % (s,f)
    elif level == 3:
        return "%s is the great grandmother of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great grandmother of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great grandmother of %s." % (s,f)
    else:
        return "%s is the %dth great grandmother of %s." % (s,level-2,f)

def get_daughter(f,s,level):
    if level == 1:
        return "%s is the daughter of %s." % (s,f)
    elif level == 2:
        return "%s is the granddaughter of %s." % (s,f)
    elif level == 3:
        return "%s is the great granddaughter of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great granddaughter of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great granddaughter of %s." % (s,f)
    else:
        return "%s is the %dth great granddaughter of %s." % (s,level-2,f)

def get_aunt(f,s,level):
    if level == 1:
        return "%s is the sister of %s." % (s,f)
    elif level == 2:
        return "%s is the aunt of %s." % (s,f)
    elif level == 3:
        return "%s is the grandaunt of %s." % (s,f)
    elif level == 4:
        return "%s is the great grandaunt of %s." % (s,f)
    elif level == 5:
        return "%s is the 2nd great grandaunt of %s." % (s,f)
    elif level == 6:
        return "%s is the 3rd great grandaunt of %s." % (s,f)
    else:
        return "%s is the %dth great grandaunt of %s." % (s,level-3,f)

def get_uncle(f,s,level):
    if level == 1:
        return "%s is the brother of %s." % (s,f)
    elif level == 2:
        return "%s is the uncle of %s." % (s,f)
    elif level == 3:
        return "%s is the granduncle of %s." % (s,f)
    elif level == 4:
        return "%s is the great granduncle of %s." % (s,f)
    elif level == 5:
        return "%s is the 2nd great granduncle of %s." % (s,f)
    elif level == 6:
        return "%s is the 3rd great granduncle of %s." % (s,f)
    else:
        return "%s is the %dth great granduncle of %s." % (s,level-3,f)

def get_nephew(f,s,level):
    if level == 1:
        return "%s is the nephew of %s." % (s,f)
    elif level == 2:
        return "%s is the grandnephew of %s." % (s,f)
    elif level == 3:
        return "%s is the great grandnephew of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great grandnephew of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great grandnephew of %s." % (s,f)
    else:
        return "%s is the %dth great grandnephew of %s." % (s,level-2,f)

def get_niece(f,s,level):
    if level == 1:
        return "%s is the niece of %s." % (s,f)
    elif level == 2:
        return "%s is the grandniece of %s." % (s,f)
    elif level == 3:
        return "%s is the great grandniece of %s." % (s,f)
    elif level == 4:
        return "%s is the 2nd great grandniece of %s." % (s,f)
    elif level == 5:
        return "%s is the 3rd great grandniece of %s." % (s,f)
    else:
        return "%s is the %dth great grandniece of %s." % (s,level-2,f)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,person,callback):
    RelCalc(database,person)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelCalc:

    def __init__(self,database,person):
        self.person = person
        self.db = database

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "relcalc.glade"
        self.glade = GladeXML(glade_file,"relcalc")

        name = self.person.getPrimaryName().getRegularName()
    
        self.glade.get_widget("name").set_text(_("Relationship to %s") % name)
        self.people = self.glade.get_widget("peopleList")

        name_list = self.db.getPersonMap().values()
        name_list.sort(sort.by_last_name)
        index = 0
        self.people.freeze()
        for p in name_list:
            name = p.getPrimaryName().getName()
            birthday = p.getBirth().getDate()
            id = p.getId()
            self.people.append([name,id,birthday])
            self.people.set_row_data(index,p)
            index = index + 1
        self.people.thaw()
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : utils.destroy_passed_object,
            "on_apply_clicked" : self.on_apply_clicked
            })

    def on_apply_clicked(self,obj):
        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        common = []
        rank = 9999999

        if len(self.people.selection) == 0:
            return

        other_person = self.people.get_row_data(self.people.selection[0])
        filter(self.person,0,firstList,firstMap)
        filter(other_person,0,secondList,secondMap)

        for person in firstList:
            if person in secondList:
                new_rank = firstMap[person]
                if new_rank < rank:
                    rank = new_rank
                    common = [ person ]
                elif new_rank == rank:
                    common.append(person)

        firstRel = -1
        secondRel = -1

        firstName = self.person.getPrimaryName().getRegularName()
        secondName = other_person.getPrimaryName().getRegularName()

        length = len(common)

        if length == 1:
            person = common[0]
            secondRel = firstMap[person]
            firstRel = secondMap[person]
            name = person.getPrimaryName().getRegularName()
            commontext = " " + _("Their common ancestor is %s.") % name
        elif length > 1:
            index = 0
            commontext = " Their common ancestors are "
            for person in common:
                secondRel = firstMap[person]
                firstRel = secondMap[person]
                if length == index + 1:
                    commontext = commontext + " and "
                elif index != 0:
                    commontext = commontext + ", "
                commontext = commontext + person.getPrimaryName().getRegularName()
                index = index + 1
        else:
            commontext = ""

        if firstRel == -1:
            msg = _("There is no relationship between %s and %s.")
            text = msg % (firstName,secondName)
        elif firstRel == 0:
            if secondRel == 0:
                text = "%s and $s are the same person." % (firstName,secondName)
            elif other_person.getGender() == RelLib.Person.male:
                text = get_father(firstName,secondName,secondRel)
            else:
                text = get_mother(firstName,secondName,secondRel)
        elif secondRel == 0:
            if other_person.getGender() == RelLib.Person.male:
                text = get_son(firstName,secondName,firstRel)
            else:
                text = get_daughter(firstName,secondName,firstRel)
        elif firstRel == 1:
            if other_person.getGender() == RelLib.Person.male:
                text = get_uncle(firstName,secondName,secondRel)
            else:
                text = get_aunt(firstName,secondName,secondRel)
        elif secondRel == 1:
            if other_person.getGender() == RelLib.Person.male:
                text = get_nephew(firstName,secondName,firstRel-1)
            else:
                text = get_niece(firstName,secondName,firstRel-1)
        else:
            if secondRel > firstRel:
                text = get_cousin(firstName,secondName,firstRel-1,secondRel-firstRel)
            else:
                text = get_cousin(firstName,secondName,secondRel-1,firstRel-secondRel)

        text1 = self.glade.get_widget("text1")
        text1.set_point(0)
        length = text1.get_length()
        text1.forward_delete(length)
        if firstRel == 0 or secondRel == 0:
            text1.insert_defaults(text)
        else:    
            text1.insert_defaults(text + commontext)
        text1.set_word_wrap(1)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Relationship calculator"),
    category=_("Utilities"),
    description=_("Calculates the relationship between two people")
    )
