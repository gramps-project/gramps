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
def runTool(database,person,callback,parent=None):
    RelCalc(database,person,parent)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelCalc:
    """
    Relationship calculator class.
    """

    def __init__(self,database,person,parent):
        self.person = person
        self.db = database
        self.RelClass = Plugins.relationship_class
        self.relationship = self.RelClass(database)
        self.parent = parent
        self.win_key = self

        base = os.path.dirname(__file__)
        glade_file = "%s/relcalc.glade" % base
        self.glade = gtk.glade.XML(glade_file,"relcalc","gramps")

        name = self.person.get_primary_name().get_regular_name()

        self.window = self.glade.get_widget('relcalc')
        Utils.set_titles(self.window,
                         self.glade.get_widget('title'),
                         _('Relationship to %s') % name,
                         _('Relationship calculator'))
    
        self.people = self.glade.get_widget("peopleList")

        self.clist = ListModel.ListModel(self.people, [(_('Name'),3,150),(_('ID'),1,50),
                                                       (_('Birth Date'),4,150),
                                                       ('',-1,0),('',-1,0)],
                                         self.on_apply_clicked)
        self.clist.new_model()
        for key in self.db.get_person_handles(sort_handles=False):
            p = self.db.get_person_from_handle(key)
            if p == self.person:
                continue
            val = self.db.get_person_from_handle(key).get_display_info()
            self.clist.add([val[0],val[1],val[3],val[5],val[6]],p.get_handle())

        self.clist.connect_model()
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : self.close,
            "on_delete_event"  : self.on_delete_event,
            "on_apply_clicked" : self.on_apply_clicked
            })

        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Relationship calculator tool'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_apply_clicked(self,obj):
        model,iter = self.clist.get_selected()
        if not iter:
            return
        
        id = self.clist.get_object(iter)
        other_person = self.db.get_person_from_handle(id)

        (rel_string,common) = self.relationship.get_relationship(self.person,other_person)
        length = len(common)

        if length == 1:
            person = self.db.get_person_from_handle(common[0])
            name = person.get_primary_name().get_regular_name()
            commontext = " " + _("Their common ancestor is %s.") % name
        elif length == 2:
            p1 = self.db.get_person_from_handle(common[0])
            p2 = self.db.get_person_from_handle(common[1])
            commontext = " " + _("Their common ancestors are %s and %s.") % \
                         (p1.get_primary_name().get_regular_name(),\
                          p2.get_primary_name().get_regular_name())
        elif length > 2:
            index = 0
            commontext = " " + _("Their common ancestors are : ")
            for person_handle in common:
                person = self.db.get_person_from_handle(person_handle)
                if index != 0:
                    commontext = commontext + ", "
                commontext = commontext + person.get_primary_name().get_regular_name()
                index = index + 1
            commontext = commontext + "."
        else:
            commontext = ""

        text1 = self.glade.get_widget("text1").get_buffer()
        p1 = GrampsCfg.get_nameof()(self.person)
        p2 = GrampsCfg.get_nameof()(other_person)

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
