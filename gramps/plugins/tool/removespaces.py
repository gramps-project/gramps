#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009   Stephane Charette
# Copyright (C) 2019-       Serge Noiraud
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

"Find possible leading and/or trailing spaces in places name and people"

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.plug import tool
from gramps.gui.editors import (EditPlace, EditPerson)
from gramps.gen.errors import WindowActiveError
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.utils import ProgressMeter
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Remove_leading_and_trailing_spaces', 'manual')

def validate_lat_lon(field):
    """
    Return True if some characters are found in the field
    # hyphen (u+2010)
    # non-breaking hyphen (u+2011)
    # figure dash (u+2012)
    # en dash (u+2013)
    # em dash (u+2014)
    # horizontal bar (u+2015)
    """
    for char in (',', '\u2010', '\u2011', '\u2012',
                 '\u2013', '\u2014', '\u2015'):
        if field.find(char) != -1:
            return True
    return False

#------------------------------------------------------------------------
#
# RemoveSpaces class
#
#------------------------------------------------------------------------
class RemoveSpaces(ManagedWindow):
    """
    Find leading and trailing spaces in Place names and person names
    """
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        dummy_opt = options_class
        dummy_nme = name
        dummy_cb = callback

        self.title = _('Clean input data')
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.dbstate = dbstate
        self.uistate = uistate
        self.db = dbstate.db
        self.tooltip = ""
        self.f_lat = False
        self.f_lon = False

        top_dialog = Glade()

        top_dialog.connect_signals({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_event"       : self.close,
        })

        window = top_dialog.toplevel
        title = top_dialog.get_object("title")
        self.set_window(window, title, self.title)
        tip = _('Search leading and/or trailing spaces for persons'
                ' and places. Search comma or bad sign in coordinates'
                ' fields.\n'
                'Double click on a row to edit its content.')
        title.set_tooltip_text(tip)

        # start the progress indicator
        self.progress = ProgressMeter(self.title, _('Starting'),
                                      parent=uistate.window)
        steps = self.db.get_number_of_people() + self.db.get_number_of_places()
        self.progress.set_pass(_('Looking for possible fields with leading or'
                                 ' trailing spaces'), steps)

        self.model_1 = Gtk.ListStore(
            GObject.TYPE_STRING,    # 0==handle
            GObject.TYPE_STRING,    # 1==firstname
            GObject.TYPE_STRING,    # 2==surname
            GObject.TYPE_STRING,    # 3==alternate name
            GObject.TYPE_STRING,    # 4==group_as
            )
        self.model_1.set_sort_column_id(
            Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, 1)

        self.label_1 = top_dialog.get_object("label_1")
        self.label_1.set_text(_('Person'))
        self.treeview_1 = top_dialog.get_object("treeview_1")
        self.treeview_1.set_model(self.model_1)
        col1 = Gtk.TreeViewColumn(_('handle'),
                                  Gtk.CellRendererText(), text=0)
        renderer1 = Gtk.CellRendererText()
        renderer1.set_property('underline-set', True)
        renderer1.set_property('underline', 2) # 2=double underline
        col2 = Gtk.TreeViewColumn(_('firstname'), renderer1, text=1)
        renderer2 = Gtk.CellRendererText()
        renderer2.set_property('underline-set', True)
        renderer2.set_property('underline', 2) # 2=double underline
        col3 = Gtk.TreeViewColumn(_('surname'), renderer2, text=2)
        renderer3 = Gtk.CellRendererText()
        renderer3.set_property('underline-set', True)
        renderer3.set_property('underline', 2) # 2=double underline
        col4 = Gtk.TreeViewColumn(_('alternate name'), renderer3, text=3)
        renderer4 = Gtk.CellRendererText()
        renderer4.set_property('underline-set', True)
        renderer4.set_property('underline', 2) # 2=double underline
        col5 = Gtk.TreeViewColumn(_('group as'), renderer4, text=4)
        col1.set_resizable(True)
        col1.set_visible(False)
        col2.set_resizable(True)
        col3.set_resizable(True)
        col4.set_resizable(True)
        col5.set_resizable(True)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col4.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col5.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview_1.append_column(col1)
        self.treeview_1.append_column(col2)
        self.treeview_1.append_column(col3)
        self.treeview_1.append_column(col4)
        self.treeview_1.append_column(col5)
        self.treeselection = self.treeview_1.get_selection()
        self.treeview_1.connect('row-activated', self.rowactivated_cb1)

        self.model_2 = Gtk.ListStore(
            GObject.TYPE_STRING,    # 0==handle
            GObject.TYPE_STRING,    # 1==name
            GObject.TYPE_STRING,    # 2==latitude
            GObject.TYPE_STRING,    # 3==longitude
            GObject.TYPE_STRING)    # 4==tooltip
        self.model_2.set_sort_column_id(
            Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, 1)

        self.label_2 = top_dialog.get_object("label_2")
        self.label_2.set_text(_('Place'))
        self.treeview_2 = top_dialog.get_object("treeview_2")
        self.treeview_2.set_model(self.model_2)
        col1 = Gtk.TreeViewColumn(_('handle'),
                                  Gtk.CellRendererText(), text=0)
        renderer5 = Gtk.CellRendererText()
        renderer5.set_property('underline-set', True)
        renderer5.set_property('underline', 2) # 2=double underline
        col2 = Gtk.TreeViewColumn(_('name'), renderer5, text=1)
        renderer6 = Gtk.CellRendererText()
        renderer6.set_property('underline-set', True)
        renderer6.set_property('underline', 2) # 2=double underline
        col3 = Gtk.TreeViewColumn(_('latitude'), renderer6, text=2)
        renderer7 = Gtk.CellRendererText()
        renderer7.set_property('underline-set', True)
        renderer7.set_property('underline', 2) # 2=double underline
        col4 = Gtk.TreeViewColumn(_('longitude'), renderer7, text=3)
        col5 = Gtk.TreeViewColumn(_('tooltip'),
                                  Gtk.CellRendererText(), text=4)
        col1.set_resizable(True)
        col1.set_visible(False)
        col2.set_resizable(True)
        col3.set_resizable(True)
        col4.set_resizable(True)
        col5.set_visible(False)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col4.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col5.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.treeview_2.append_column(col1)
        self.treeview_2.append_column(col2)
        self.treeview_2.append_column(col3)
        self.treeview_2.append_column(col4)
        self.treeview_2.append_column(col5)
        self.treeview_2.set_tooltip_column(4)
        self.treeselection = self.treeview_2.get_selection()
        self.treeview_2.connect('row-activated', self.rowactivated_cb2)

        self.places()
        self.people()

        # close the progress bar
        self.progress.close()

        self.show()

    def add_text_to_tip(self, nll, mess):
        """
        Add a text to tooltip for places.
        nll: 0: name
             1: latitude
             2: longitude
        mess: text to add
        """
        if nll == 0:
            self.tooltip = _("Name:")
            self.tooltip += " "
            self.tooltip += mess
        elif nll == 1:
            if not self.f_lat:
                if self.tooltip != "":
                    self.tooltip += "\n"
                self.tooltip += _("Latitude:")
                self.tooltip += " "
                self.f_lat = True
            else:
                self.tooltip += ", "
            self.tooltip += mess
        elif nll == 2:
            if not self.f_lon:
                if self.tooltip != "":
                    self.tooltip += "\n"
                self.tooltip += _("Longitude:")
                self.tooltip += " "
                self.f_lon = True
            else:
                self.tooltip += ", "
            self.tooltip += mess

    def places(self):
        """
        For all places in the database, if the name contains leading or
        trailing spaces.
        """
        for place_handle in self.db.get_place_handles():
            self.progress.step()
            place = self.db.get_place_from_handle(place_handle)
            place_name = place.get_name()
            pname = place_name.get_value()
            found = False
            self.tooltip = ""
            if pname != pname.strip():
                self.add_text_to_tip(0, _("leading and/or trailing spaces"))
                found = True
            plat = place.get_latitude()
            plon = place.get_longitude()
            lat, lon = conv_lat_lon(plat, plon, "D.D8")
            self.f_lat = self.f_lon = False
            if not lat:
                self.add_text_to_tip(1, _("invalid format"))
                found = True
            if plat != plat.strip():
                self.add_text_to_tip(1, _("leading and/or trailing spaces"))
                found = True
            if plat.find(',') != -1:
                self.add_text_to_tip(1, _("comma instead of dot"))
                found = True
            if validate_lat_lon(plat):
                self.add_text_to_tip(1, _("invalid char instead of '-'"))
                found = True
            if not lon:
                self.add_text_to_tip(2, _("invalid format"))
                found = True
            if plon != plon.strip():
                self.add_text_to_tip(2, _("leading and/or trailing spaces"))
                found = True
            if plon.find(',') != -1:
                self.add_text_to_tip(2, _("comma instead of dot"))
                found = True
            if validate_lat_lon(plat):
                self.add_text_to_tip(1, _("invalid char instead of '-'"))
                found = True
            if found:
                value = (place_handle, pname, plat, plon, self.tooltip)
                self.model_2.append(value)
        return True

    def people(self):
        """
        For all persons in the database, if the name contains leading or
        trailing spaces. Works for alternate names and group_as.
        """
        for person_handle in self.db.get_person_handles():
            self.progress.step()
            person = self.db.get_person_from_handle(person_handle)
            primary_name = person.get_primary_name()
            fname = primary_name.get_first_name()
            found = False
            if fname != fname.strip():
                found = True
            sname = primary_name.get_primary_surname().get_surname()
            if sname != sname.strip():
                found = True
            paname = ""
            for name in primary_name.get_surname_list():
                aname = name.get_surname()
                if aname != sname and aname != aname.strip():
                    found = True
                    if paname != "":
                        paname += ', '
                    paname += aname
            groupas = primary_name.group_as
            if groupas != groupas.strip():
                found = True
            if found:
                value = (person_handle, fname, sname, paname, groupas)
                self.model_1.append(value)
        return True

    def rowactivated_cb1(self, treeview, path, column):
        """
        Called when a Person row is activated.
        """
        dummy_tv = treeview
        dummy_col = column
        iter_ = self.model_1.get_iter(path)
        handle = self.model_1.get_value(iter_, 0)
        person = self.dbstate.db.get_person_from_handle(handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                pass
            return True
        return False

    def rowactivated_cb2(self, treeview, path, column):
        """
        Called when a Place row is activated.
        """
        dummy_tv = treeview
        dummy_col = column
        iter_ = self.model_2.get_iter(path)
        handle = self.model_2.get_value(iter_, 0)
        place = self.dbstate.db.get_place_from_handle(handle)
        if place:
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except WindowActiveError:
                pass
            return True
        return False

    def on_help_clicked(self, _obj):
        """
        Display the relevant portion of Gramps manual.
        """
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def close(self, *obj):
        ManagedWindow.close(self, *obj)

#------------------------------------------------------------------------
#
# RemoveSpacesOptions
#
#------------------------------------------------------------------------
class RemoveSpacesOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        """ Initialize the options class """
        tool.ToolOptions.__init__(self, name, person_id)
