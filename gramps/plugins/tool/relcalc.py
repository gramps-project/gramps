#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Gary Burton
# Copyright (C) 2010       Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tools/Utilities/Relationship Calculator"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.display.name import displayer as name_displayer
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.views.treemodels import PeopleBaseModel, PersonTreeModel
from gramps.plugins.lib.libpersonview import BasePersonView
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.display import display_help

from gramps.gui.dialog import ErrorDialog
from gramps.gui.plug import tool
from gramps.gui.glade import Glade

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

column_names = [column[0] for column in BasePersonView.COLUMNS]
WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Tools"
WIKI_HELP_SEC = _('Relationship Calculator')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelCalc(tool.Tool, ManagedWindow):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        """
        Relationship calculator class.
        """

        tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.__init__(self,uistate,[],self.__class__)

        #set the columns to see
        for data in BasePersonView.CONFIGSETTINGS:
            if data[0] == 'columns.rank':
                colord = data[1]
            elif data[0] == 'columns.visible':
                colvis = data[1]
            elif data[0] == 'columns.size':
                colsize = data[1]
        self.colord = []
        for col, size in zip(colord, colsize):
            if col in colvis:
                self.colord.append((1, col, size))
            else:
                self.colord.append((0, col, size))

        self.dbstate = dbstate
        self.relationship = get_relationship_calculator(glocale)
        self.relationship.connect_db_signals(dbstate)

        self.glade = Glade()
        self.person = self.db.get_person_from_handle(
                                            uistate.get_active('Person'))
        name = ''
        if self.person:
            name = name_displayer.display(self.person)
        self.title = _('Relationship calculator: %(person_name)s'
                       ) % {'person_name' : name}
        window = self.glade.toplevel
        self.titlelabel = self.glade.get_object('title')
        self.set_window(window, self.titlelabel,
                        _('Relationship to %(person_name)s'
                          ) % {'person_name' : name},
                        self.title)
        self.setup_configs('interface.relcalc', 600, 400)

        self.tree = self.glade.get_object("peopleList")
        self.text = self.glade.get_object("text1")
        self.textbuffer = Gtk.TextBuffer()
        self.text.set_buffer(self.textbuffer)

        self.model = PersonTreeModel(self.db, uistate)
        self.tree.set_model(self.model)

        self.tree.connect('key-press-event', self._key_press)
        self.selection = self.tree.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        #keep reference of column so garbage collection works
        self.columns = []
        for pair in self.colord:
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = Gtk.TreeViewColumn(name, Gtk.CellRendererText(),
                                        markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
            self.tree.append_column(column)
            #keep reference of column so garbage collection works
            self.columns.append(column)

        self.sel = self.tree.get_selection()
        self.changedkey = self.sel.connect('changed',self.on_apply_clicked)
        self.closebtn = self.glade.get_object("button5")
        self.closebtn.connect('clicked', self.close)
        help_btn = self.glade.get_object("help_btn")
        help_btn.connect('clicked', lambda x: display_help(WIKI_HELP_PAGE,
                                                           WIKI_HELP_SEC))

        if not self.person:
            self.window.hide()
            ErrorDialog(_('Active person has not been set'),
                        _('You must select an active person for this '
                          'tool to work properly.'),
                        parent=uistate.window)
            self.close()
            return

        self.show()

    def close(self, *obj):
        """ Close relcalc tool. Remove non-gtk connections so garbage
            collection can do its magic.
        """
        self.relationship.disconnect_db_signals(self.dbstate)
        self.sel.disconnect(self.changedkey)
        ManagedWindow.close(self, *obj)

    def build_menu_names(self, obj):
        return (_("Relationship Calculator tool"),None)

    def on_apply_clicked(self, obj):
        model, iter_ = self.tree.get_selection().get_selected()
        if not iter_:
            return

        other_person = None
        handle = model.get_handle_from_iter(iter_)
        if handle:
            other_person = self.db.get_person_from_handle(handle)
        if other_person is None:
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
            rstr = _("%(person)s and %(active_person)s are the same person.") % {
                        'person': p1,
                        'active_person': p2
                        }
            text.append((rstr, ""))
        elif len(rel_strings) == 0:
            rstr = _("%(person)s and %(active_person)s are not related.") % {
                            'person': p2,
                            'active_person': p1
                            }
            text.append((rstr, ""))

        for rel_string, common in zip(rel_strings, common_an):
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s."
                        ) % {'person': p2,
                             'relationship': rel_string,
                             'active_person': p1
                            }
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
                commontext = " " + _("Their common ancestors are %(ancestor1)s and %(ancestor2)s.") % {
                                          'ancestor1': p1str,
                                          'ancestor2': p2str
                                          }
            elif length > 2:
                index = 0
                commontext = " " + _("Their common ancestors are: ")
                for person_handle in common:
                    person = self.db.get_person_from_handle(person_handle)
                    if index:
                        # TODO for Arabic, should the next comma be translated?
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
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
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
class RelCalcOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)
