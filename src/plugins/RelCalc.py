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

_ = intl.gettext

topDialog = None
other_person = None
col2person = []

#-------------------------------------------------------------------------
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
def on_peopleList_select_row(obj,a,b,c):
    global other_person
    
    other_person = col2person[a]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    firstMap = {}
    firstList = []
    secondMap = {}
    secondList = []
    common = []
    rank = 9999999

    filter(active_person,0,firstList,firstMap)
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

    firstName = active_person.getPrimaryName().getRegularName()
    secondName = other_person.getPrimaryName().getRegularName()

    length = len(common)
    if length == 1:
        person = common[0]
        secondRel = firstMap[person]
        firstRel = secondMap[person]
        commontext = " Their common ancestor is "
        commontext = commontext + person.getPrimaryName().getRegularName() + "."
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
        text = "There is no relationship between " + firstName + " and " + secondName + "."
    elif firstRel == 0:
        if other_person.getGender() == RelLib.Person.male:
            root = "father"
        else:
            root = "mother"
        if secondRel == 0:
            text = firstName + " and " + secondName + " are the same person."
        else:
            text = secondName + get_prefix(secondRel,root) + firstName
    elif secondRel == 0:
        if other_person.getGender() == RelLib.Person.male:
            text = secondName + get_prefix(firstRel,"son") + firstName + "."
        else:
            text = secondName + get_prefix(firstRel,"daughter") + firstName + "."
    elif firstRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            root = "uncle"
        else:
            root = "aunt"
        if secondRel == 1:
            if other_person.getGender() == RelLib.Person.male:
                text = secondName + " is the brother of " + firstName + "."
            else:
                text = secondName + " is the sister of " + firstName + "."
        else:
            text = secondName + get_prefix(secondRel-1,root) + firstName + "."
    elif secondRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            text = secondName + get_prefix(firstRel-1,"nephew") + firstName + "."
        else:
            text = secondName + get_prefix(firstRel-1,"niece") + firstName + "."
    else:
        if secondRel > firstRel:
            text = secondName + cousin(secondRel-1,secondRel-firstRel) + firstName + "."
        else:
            text = secondName + cousin(firstRel-1,firstRel-secondRel) + firstName + "."

    text1 = topDialog.get_widget("text1")
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
def cousin(level,removed):
    if level == 1:
        root = " is the 1st cousin"
    elif level == 2:
        root = " is the 2nd cousin"
    elif level == 3:
        root = " is the 3rd cousin"
    else:
        root = " is the %dth cousin" % level

    if removed == 0:
        root = root + " of "
    elif removed == 1:
        root = root + " once removed of "
    elif removed == 2:
        root = root + " twice removed of "
    else:
        root = root + " %d times removed of " % removed

    return root
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_prefix(level,root):
    if level == 1:
        return " is the " + root + " of "
    elif level == 2:
        return " is the grand" + root + " of "
    elif level == 3:
        return " is the great grand" + root + " of "
    elif level == 4:
        return " is the 2nd great grand" + root + " of "
    elif level == 5:
        return " is the 3rd great grand" + root + " of "
    else:
        return " is the %dth great grand%s of " % (level - 2,root)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_close_clicked(obj):
    obj.destroy()
    while events_pending():
        mainiteration()

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
def runTool(database,person,callback):
    global active_person
    global topDialog
    global glade_file
    global db

    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "relcalc.glade"
    topDialog = GladeXML(glade_file,"relcalc")

    name = person.getPrimaryName().getRegularName()
    
    topDialog.get_widget("name").set_text("Relationship to " + name)
    peopleList = topDialog.get_widget("peopleList")

    name_list = database.getPersonMap().values()
    name_list.sort(sort.by_last_name)
    for per in name_list:
        col2person.append(per)
        name = per.getPrimaryName().getName()
        birthday = per.getBirth().getDate()
        peopleList.append([name,birthday])

    topDialog.signal_autoconnect({
        "on_close_clicked" : on_close_clicked,
        "on_peopleList_select_row" : on_peopleList_select_row,
        "on_apply_clicked" : on_apply_clicked
        })
    
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
