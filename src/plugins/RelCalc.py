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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import sort
import Utils
import ListModel
from intl import gettext as _

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def filter(person,index,list,map):
    if person == None:
        return
    list.append(person)
    map[person.getId()] = index
    
    family = person.getMainParents()
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
            return _("%(p1)s is the first cousin of %(p2)s.") % {
                'p1' : f, 'p2' : s}
        elif removed == 1:
            return _("%(p1)s is the first cousin once removed of %(p2)s.") % {
                'p1' : f, 'p2' : s}
        elif removed == 2:
            return _("%(p1)s is the first cousin twice removed of %(p2)s.") % {
                'p1' : f,'p2' : s}
        else:
            return _("%(p1)s is the first cousin %(removed)d times removed of %(p2)s.") % {
                'p1' :f, 'p2' :s, 'removed' : removed}
    elif level == 2:
        if removed == 0:
            return _("%(p1)s is the second cousin of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        elif removed == 1:
            return _("%(p1)s is the second cousin once removed of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        elif removed == 2:
            return _("%(p1)s is the second cousin twice removed of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        else:
            return _("%(p1)s is the second cousin %(removed)d times removed of %(p2)s.") % {
                'p1' : f, 'p2' : s, 'removed' : removed }
    elif level == 3:
        if removed == 0:
            return _("%(p1)s is the third cousin of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        elif removed == 1:
            return _("%(p1)s is the third cousin once removed of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        elif removed == 2:
            return _("%(p1)s is the third cousin twice removed of %(p2)s.") % {
                'p1' : f, 'p2' : s }
        else:
            return _("%(p1)s is the third cousin %(removed)d times removed of %(p2)s.") % {
                'p1' : f, 'p2' : s, 'removed' : removed }
    else:
        if removed == 0:
            return _("%(p1)s is the %(level)dth cousin of %(p2)s.") % {
                'p1': f, 'level': level, 'p2' : s }
        elif removed == 1:
            return _("%(p1)s is the %(level)dth cousin once removed of %(p2)s.") % {
                'p1': f, 'level': level, 'p2' : s }
        elif removed == 2:
            return _("%(p1)s is the %(level)dth cousin twice removed of %(p2)s.") % {
                'p1': f, 'level': level, 'p2' : s }
        else:
            return _("%(p1)s is the %(level)dth cousin %(removed)d times removed of %(p2)s.") % {
                'p1': f, 'level': level, 'removed' : removed, 'p2' : s }

def get_father(f,s,level):
    if level == 1:
        return _("%(p1)s is the father of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the grandfather of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great grandfather of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great grandfather of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great grandfather of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandfather of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

def get_son(f,s,level):
    if level == 1:
        return _("%(p1)s is the son of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the grandson of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great grandson of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great grandson of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great grandson of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandson of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

def get_mother(f,s,level):
    if level == 1:
        return _("%(p1)s is the mother of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the grandmother of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great grandmother of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great grandmother of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great grandmother of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandmother of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

def get_daughter(f,s,level):
    if level == 1:
        return _("%(p1)s is the daughter of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the granddaughter of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great granddaughter of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great granddaughter of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great granddaughter of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great granddaughter of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

def get_aunt(f,s,level):
    if level == 1:
        return _("%(p1)s is the sister of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the aunt of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the grandaunt of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the great grandaunt of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the second great grandaunt of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 6:
        return _("%(p1)s is the third great grandaunt of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandaunt of %(p2)s.") % {
            'p1': s, 'level' : level-3, 'p2': f }

def get_uncle(f,s,level):
    if level == 1:
        return _("%(p1)s is the brother of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the uncle of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the granduncle of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the great granduncle of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the second great granduncle of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 6:
        return _("%(p1)s is the third great granduncle of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great granduncle of %(p2)s.") % {
            'p1': s, 'level' : level-3, 'p2': f }

def get_nephew(f,s,level):
    if level == 1:
        return _("%(p1)s is the nephew of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the grandnephew of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great grandnephew of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great grandnephew of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great grandnephew of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandnephew of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

def get_niece(f,s,level):
    if level == 1:
        return _("%(p1)s is the niece of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 2:
        return _("%(p1)s is the grandniece of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 3:
        return _("%(p1)s is the great grandniece of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 4:
        return _("%(p1)s is the second great grandniece of %(p2)s.") % {
            'p1': s, 'p2': f }
    elif level == 5:
        return _("%(p1)s is the third great grandniece of %(p2)s.") % {
            'p1': s, 'p2': f }
    else:
        return _("%(p1)s is the %(level)dth great grandniece of %(p2)s.") % {
            'p1': s, 'level' : level-2, 'p2': f }

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
    """
    Relationship calculator class.
    """

    def __init__(self,database,person):
        self.person = person
        self.db = database

        base = os.path.dirname(__file__)
        glade_file = "%s/relcalc.glade" % base
        self.glade = gtk.glade.XML(glade_file,"relcalc")

        name = self.person.getPrimaryName().getRegularName()
    
        self.glade.get_widget("name").set_text(_("Relationship to %s") % name)
        self.people = self.glade.get_widget("peopleList")

        self.clist = ListModel.ListModel(self.people, [(_('Name'),3,150),(_('ID'),1,50),
                                                       (_('Birthday'),4,150),
                                                       ('',-1,0),('',-1,0)])
        self.clist.new_model()
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            val = self.db.getPersonDisplay(key)
            self.clist.add([val[0],val[1],val[3],val[5],val[6]],p.getId())

        self.clist.connect_model()
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : Utils.destroy_passed_object,
            "on_apply_clicked" : self.on_apply_clicked
            })

    def on_apply_clicked(self,obj):
        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        common = []
        rank = 9999999

        model,iter = self.clist.get_selected()
        if not iter:
            return
        
        id = self.clist.get_object(iter)
        other_person = self.db.getPerson(id)
        filter(self.person,0,firstList,firstMap)
        filter(other_person,0,secondList,secondMap)

        for person in firstList:
            if person in secondList:
                new_rank = firstMap[person.getId()]
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
            secondRel = firstMap[person.getId()]
            firstRel = secondMap[person.getId()]
            name = person.getPrimaryName().getRegularName()
            commontext = " " + _("Their common ancestor is %s.") % name
        elif length == 2:
            p1 = common[0]
            p2 = common[1]
            secondRel = firstMap[p1.getId()]
            firstRel = secondMap[p1.getId()]
            commontext = " " + _("Their common ancestors are %s and %s.") % \
                         (p1.getPrimaryName().getRegularName(),\
                          p2.getPrimaryName().getRegularName())
        elif length > 2:
            index = 0
            commontext = " " + _("Their common ancestors are : ")
            for person in common:
                secondRel = firstMap[person.getId()]
                firstRel = secondMap[person.getId()]
                if index != 0:
                    commontext = commontext + ", "
                commontext = commontext + person.getPrimaryName().getRegularName()
                index = index + 1
            commontext = commontext + "."
        else:
            commontext = ""

        if firstRel == -1:
            msg = _("There is no relationship between %s and %s.")
            text = msg % (firstName,secondName)
        elif firstRel == 0:
            if secondRel == 0:
                text = _("%s and %s are the same person.") % (firstName,secondName)
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

        text1 = self.glade.get_widget("text1").get_buffer()
        if firstRel == 0 or secondRel == 0:
            text1.set_text(text)
        else:    
            text1.set_text(text + commontext)
    
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
