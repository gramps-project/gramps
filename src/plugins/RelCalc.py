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

# $Id$

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
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import Utils
import GrampsCfg
import ListModel
import Plugins
from gettext import gettext as _

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
        self.RelClass = Plugins.relationship_class
        self.relationship = self.RelClass(database)

        base = os.path.dirname(__file__)
        glade_file = "%s/relcalc.glade" % base
        self.glade = gtk.glade.XML(glade_file,"relcalc","gramps")

        name = self.person.get_primary_name().get_regular_name()

        Utils.set_titles(self.glade.get_widget('relcalc'),
                         self.glade.get_widget('title'),
                         _('Relationship to %s') % name,
                         _('Relationship calculator'))
    
        self.people = self.glade.get_widget("peopleList")

        self.clist = ListModel.ListModel(self.people, [(_('Name'),3,150),(_('ID'),1,50),
                                                       (_('Birth Date'),4,150),
                                                       ('',-1,0),('',-1,0)],
                                         self.on_apply_clicked)
        self.clist.new_model()
        for key in self.db.get_person_keys():
            p = self.db.get_person(key)
            if p == self.person:
                continue
            val = self.db.get_person_display(key)
            self.clist.add([val[0],val[1],val[3],val[5],val[6]],p.get_id())

        self.clist.connect_model()
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : Utils.destroy_passed_object,
            "on_apply_clicked" : self.on_apply_clicked
            })

    def on_apply_clicked(self,obj):
        model,iter = self.clist.get_selected()
        if not iter:
            return
        
        id = self.clist.get_object(iter)
        other_person = self.db.get_person(id)

        (rel_string,common) = self.relationship.get_relationship(self.person,other_person)
        length = len(common)

        if length == 1:
            person = self.db.find_person_from_id(common[0])
            name = person.get_primary_name().get_regular_name()
            commontext = " " + _("Their common ancestor is %s.") % name
        elif length == 2:
            p1 = self.db.find_person_from_id(common[0])
            p2 = self.db.find_person_from_id(common[1])
            commontext = " " + _("Their common ancestors are %s and %s.") % \
                         (p1.get_primary_name().get_regular_name(),\
                          p2.get_primary_name().get_regular_name())
        elif length > 2:
            index = 0
            commontext = " " + _("Their common ancestors are : ")
            for person_id in common:
                person = self.db.find_person_form_id(person_id)
                if index != 0:
                    commontext = commontext + ", "
                commontext = commontext + person.get_primary_name().get_regular_name()
                index = index + 1
            commontext = commontext + "."
        else:
            commontext = ""

        text1 = self.glade.get_widget("text1").get_buffer()
        p1 = GrampsCfg.nameof(self.person)
        p2 = GrampsCfg.nameof(other_person)

        if rel_string == "":
            rstr = _("%(person)s and %(active_person)s are not related.") % {
                'person' : p2, 'active_person' : p1 }
        else:
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s.") % {
                'person' : p2, 'relationship' : rel_string, 'active_person' : p1 }

        text1.set_text("%s %s" % (rstr, commontext))
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

Plugins.register_tool(
    runTool,
    _("Relationship calculator"),
    category=_("Utilities"),
    description=_("Calculates the relationship between two people")
    )
