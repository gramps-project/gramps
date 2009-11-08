#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""Tools/Utilities/Relationship Calculator"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from BasicUtils import name_displayer
import ManagedWindow
from gui.views.treemodels import PeopleModel
import Relationship

from QuestionDialog import ErrorDialog
from PluginUtils import Tool
from glade import Glade

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

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

        self.dbstate = dbstate
        self.relationship = Relationship.get_relationship_calculator()
        self.relationship.connect_db_signals(dbstate)

        self.glade = Glade()

        name = ''
        if self.person:
            name = name_displayer.display(self.person)
        self.title = _('Relationship calculator: %(person_name)s'
                       ) % {'person_name' : name}
        window = self.glade.toplevel
        self.titlelabel = self.glade.get_object('title')
        self.set_window(window, self.titlelabel,
                        _('Relationship to %(person_name)s'
                          ) % {'person_name' : name },
                        self.title)
    
        self.tree = self.glade.get_object("peopleList")
        self.text = self.glade.get_object("text1")
        self.textbuffer = gtk.TextBuffer()
        self.text.set_buffer(self.textbuffer)
        
        self.model = PeopleModel(self.db,None)
        self.tree.set_model(self.model)

        self.tree.connect('key-press-event', self._key_press)
        self.selection = self.tree.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)

        column = gtk.TreeViewColumn(_('Name'), gtk.CellRendererText(),text=0)
        column.set_resizable(True)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.tree.append_column(column)
        #keep reference of column so garbage collection works
        self.columns = [column]

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
            #keep reference of column so garbage collection works
            self.columns.append(column)
            index += 1

        self.sel = self.tree.get_selection()
        self.changedkey = self.sel.connect('changed',self.on_apply_clicked)
        self.closebtn = self.glade.get_object("button5")
        self.closebtn.connect('clicked', self.close)

        if not self.person:
            self.window.hide()
            ErrorDialog(_('Active person has not been set'),
                        _('You must select an active person for this '
                          'tool to work properly.'))
            self.close()
            return

        self.show()

    def close(self, *obj):
        """ Close relcalc tool. Remove non-gtk connections so garbage
            collection can do its magic.
        """
        self.relationship.disconnect_db_signals(self.dbstate)
        self.sel.disconnect(self.changedkey)
        ManagedWindow.ManagedWindow.close(self, *obj)

    def build_menu_names(self, obj):
        return (_("Relationship Calculator tool"),None)

    def on_apply_clicked(self, obj):
        model, node = self.tree.get_selection().get_selected()
        if not node:
            return
        
        handle = model.get_value(node,len(PeopleModel.COLUMN_DEFS)-1)
        other_person = self.db.get_person_from_handle(handle)        
        if other_person is None :
            self.textbuffer.set_text("")
            return
        
        #now determine the relation, and print it out        
        rel_strings, common_an = self.relationship.get_all_relationships(
                                            self.db, self.person, other_person)

        p1 = name_displayer.display(self.person)
        p2 = name_displayer.display(other_person)

        text = []
        if other_person is None: 
            pass
        elif self.person.handle == other_person.handle:
            rstr = _("%s and %s are the same person.") % (p1, p2)
            text.append((rstr, ""))
        elif len(rel_strings) == 0:
            rstr = _("%(person)s and %(active_person)s are not related.") % {
                            'person' : p2, 'active_person' : p1 }
            text.append((rstr, ""))

        for rel_string, common in zip(rel_strings, common_an):
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s."
                        ) % {'person' : p2, 'relationship' : rel_string,
                             'active_person' : p1 }
            length = len(common)
            if length == 1:
                person = self.db.get_person_from_handle(common[0])
                if common[0] in [other_person.handle, self.person.handle]:
                    commontext = ''
                else :
                    name = name_displayer.display(person)
                    commontext = " " + _("Their common ancestor is %s.") % name
            elif length == 2:
                p1c = self.db.get_person_from_handle(common[0])
                p2c = self.db.get_person_from_handle(common[1])
                p1str = name_displayer.display(p1c)
                p2str = name_displayer.display(p2c)
                commontext = " " + _("Their common ancestors are %s and %s."
                                    ) % (p1str,p2str)
            elif length > 2:
                index = 0
                commontext = " " + _("Their common ancestors are: ")
                for person_handle in common:
                    person = self.db.get_person_from_handle(person_handle)
                    if index:
                        commontext += ", "
                    commontext += name_displayer.display(person)
                    index += 1
                commontext += "."
            else:
                commontext = ""
            text.append((rstr, commontext))

        textval = ""
        for val in text:
            textval += "%s %s\n" % (val[0], val[1])
        self.textbuffer.set_text(textval)
    
    def _key_press(self, obj, event):
        if not event.state or event.state  in (gtk.gdk.MOD2_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                store, paths = self.selection.get_selected_rows()
                if paths and len(paths[0]) == 1 :
                    if self.tree.row_expanded(paths[0]):
                        self.tree.collapse_row(paths[0])
                    else:
                        self.tree.expand_row(paths[0], 0)
                    return True
        return False

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RelCalcOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)
