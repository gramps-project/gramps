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

"Utilities/Relationship calculator"

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

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
import RelLib
import Utils
import NameDisplay
import ListModel
import DateHandler
import PeopleModel
from PluginUtils import Tool, relationship_class, register_tool

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelCalc(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        """
        Relationship calculator class.
        """

        self.person = person
        self.RelClass = relationship_class
        self.relationship = self.RelClass(self.db)
        self.parent = parent
        self.win_key = self

        base = os.path.dirname(__file__)
        glade_file = "%s/relcalc.glade" % base
        self.glade = gtk.glade.XML(glade_file,"relcalc","gramps")

        name = self.person.get_primary_name().get_regular_name()
        self.title = _('Relationship calculator: %(person_name)s') % { 
                                        'person_name' : name }
        self.window = self.glade.get_widget('relcalc')
        self.window.set_icon(self.parent.topWindow.get_icon())
        Utils.set_titles(self.window,
                         self.glade.get_widget('title'),
                         _('Relationship to %(person_name)s') % { 
                                        'person_name' : name },
                         self.title)
    
        self.tree = self.glade.get_widget("peopleList")
        
        self.model = PeopleModel.PeopleModel(self.db)
        self.tree.set_model(self.model)

        column = gtk.TreeViewColumn(_('Name'), gtk.CellRendererText(),text=0)
        column.set_resizable(True)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.tree.append_column(column)

        index = 1
        for pair in self.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(), markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self.tree.append_column(column)
            index += 1

        self.tree.get_selection().connect('changed',self.on_apply_clicked)
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : self.close,
            "on_delete_event"  : self.on_delete_event,
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
        self.parent_menu_item = gtk.MenuItem(self.title)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_apply_clicked(self,obj):
        model,node = self.tree.get_selection().get_selected()
        if not node:
            return
        
        handle = model.get_value(node,len(PeopleModel.COLUMN_DEFS)-1)
        other_person = self.db.get_person_from_handle(handle)

        if other_person != None:
            (rel_string,common) = self.relationship.get_relationship(self.person,other_person)
            length = len(common)
        else:
            length = 0

        if other_person == None:
            commontext = ""
        elif length == 1:
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

        if other_person:
            p1 = NameDisplay.displayer.display(self.person)
            p2 = NameDisplay.displayer.display(other_person)

        if other_person == None:
            rstr = ""
        elif self.person.handle == other_person.handle:
            rstr = _("%s and %s are the same person.") % (p1,p2)
        elif rel_string == "":
            rstr = _("%(person)s and %(active_person)s are not related.") % {
                'person' : p2, 'active_person' : p1 }
        else:
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s.") % {
                'person' : p2, 'relationship' : rel_string, 'active_person' : p1 }

        text1.set_text("%s %s" % (rstr, commontext))
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RelCalcOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'relcalc',
    category = Tool.TOOL_UTILS,
    tool_class = RelCalc,
    options_class = RelCalcOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Relationship calculator"),
    status=(_("Stable")),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Calculates the relationship between two people")
    )
