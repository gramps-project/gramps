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
try:
    set()
except NameError:
    from sets import Set as set

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
import NameDisplay
import ManagedWindow
import ListModel
import DateHandler
from DisplayModels import PeopleModel

from QuestionDialog import ErrorDialog
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
class RelCalc(Tool.Tool, ManagedWindow.ManagedWindow):
    
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        """
        Relationship calculator class.
        """
        
        Tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        if not self.person:
            ErrorDialog(_('Active person has not been set'),
                        _('You must select an active person for this '
                          'tool to work properly.'))
            return
        
        self.RelClass = relationship_class
        self.relationship = self.RelClass(self.db)

        base = os.path.dirname(__file__)
        glade_file = "%s/relcalc.glade" % base
        self.glade = gtk.glade.XML(glade_file,"relcalc","gramps")

        name = NameDisplay.displayer.display(self.person)
        self.title = _('Relationship calculator: %(person_name)s'
                       ) % {'person_name' : name}
        window = self.glade.get_widget('relcalc')
        self.set_window(window,self.glade.get_widget('title'),
                        _('Relationship to %(person_name)s'
                          ) % {'person_name' : name },
                        self.title)
    
        self.tree = self.glade.get_widget("peopleList")
        
        self.model = PeopleModel(self.db,None)
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
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(),
                                        markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self.tree.append_column(column)
            index += 1

        self.tree.get_selection().connect('changed',self.on_apply_clicked)
            
        self.glade.signal_autoconnect({
            "on_close_clicked" : self.close,
            })

        self.show()

    def build_menu_names(self,obj):
        return (_("Relationship Calculator tool"),None)

    def on_apply_clicked(self,obj):
        model,node = self.tree.get_selection().get_selected()
        if not node:
            return
        
        handle = model.get_value(node,len(PeopleModel.COLUMN_DEFS)-1)
        other_person = self.db.get_person_from_handle(handle)

        if other_person != None:
            (rel_string,common) = self.relationship.get_relationship(
                self.person,other_person)
            # A quick way to get unique list
            common = list(set(common))
            length = len(common)
        else:
            length = 0

        if other_person == None:
            commontext = ""
        elif length == 1:
            person = self.db.get_person_from_handle(common[0])
            name = NameDisplay.displayer.display(person)
            commontext = " " + _("Their common ancestor is %s.") % name
        elif length == 2:
            p1 = self.db.get_person_from_handle(common[0])
            p2 = self.db.get_person_from_handle(common[1])
            p1str = NameDisplay.displayer.display(p1)
            p2str = NameDisplay.displayer.display(p2)
            commontext = " " + _("Their common ancestors are %s and %s."
                                 ) % (p1str,p2str)
        elif length > 2:
            index = 0
            commontext = " " + _("Their common ancestors are: ")
            for person_handle in common:
                person = self.db.get_person_from_handle(person_handle)
                if index != 0:
                    commontext = commontext + ", "
                commontext = commontext + NameDisplay.displayer.display(person)
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
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s."
                     ) % {'person' : p2, 'relationship' : rel_string,
                          'active_person' : p1 }

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
