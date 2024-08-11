#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008,2010  Gary Burton
# Copyright (C) 2008       Craig J. Anderson
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2011-2013  Paul Franklin
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

"""
Specific option handling for a GUI.
"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import os

# -------------------------------------------------------------------------
#
# gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from ..utils import ProgressMeter
from ..pluginmanager import GuiPluginManager
from .. import widgets
from ..managedwindow import ManagedWindow
from ..dialog import OptionDialog
from ..selectors import SelectorFactory
from gramps.gen.errors import HandleError
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.filters import GenericFilterFactory, GenericFilter, rules
from gramps.gen.constfunc import get_curr_dir
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# ------------------------------------------------------------------------
#
# Dialog window used to select a surname
#
# ------------------------------------------------------------------------
class LastNameDialog(ManagedWindow):
    """
    A dialog that allows the selection of a surname from the database.
    """

    def __init__(self, database, uistate, track, surnames, skip_list=set()):
        ManagedWindow.__init__(self, uistate, track, self, modal=True)
        self.__dlg = Gtk.Dialog(
            transient_for=uistate.window, destroy_with_parent=True, modal=True
        )
        self.__dlg.add_buttons(
            _("_Cancel"), Gtk.ResponseType.REJECT, _("_OK"), Gtk.ResponseType.ACCEPT
        )
        self.set_window(self.__dlg, None, _("Select surname"))
        self.setup_configs("interface.lastnamedialog", 400, 400)

        # build up a container to display all of the people of interest
        self.__model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        self.__tree_view = Gtk.TreeView(model=self.__model)
        col1 = Gtk.TreeViewColumn(_("Surname"), Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_("Count"), Gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.__tree_view)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.OUT)
        self.__dlg.vbox.pack_start(scrolled_window, True, True, 0)
        self.show()

        if len(surnames) == 0:
            # we could use database.get_surname_list(), but if we do that
            # all we get is a list of names without a count...therefore
            # we'll traverse the entire database ourself and build up a
            # list that we can use
            #            for name in database.get_surname_list():
            #                self.__model.append([name, 0])

            # build up the list of surnames, keeping track of the count for each
            # name (this can be a lengthy process, so by passing in the
            # dictionary we can be certain we only do this once)
            progress = ProgressMeter(_("Finding Surnames"), parent=uistate.window)
            progress.set_pass(_("Finding surnames"), database.get_number_of_people())
            for person in database.iter_people():
                progress.step()
                key = person.get_primary_name().get_surname()
                count = 0
                if key in surnames:
                    count = surnames[key]
                surnames[key] = count + 1
            progress.close()

        # insert the names and count into the model
        for key in surnames:
            if key.encode("iso-8859-1", "xmlcharrefreplace") not in skip_list:
                self.__model.append([key, surnames[key]])

        # keep the list sorted starting with the most popular last name
        # (but after sorting the whole list alphabetically first, so
        # that surnames with the same number of people will be alphabetical)
        self.__model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.__model.set_sort_column_id(1, Gtk.SortType.DESCENDING)

        # the "OK" button should be enabled/disabled based on the selection of
        # a row
        self.__tree_selection = self.__tree_view.get_selection()
        self.__tree_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.__tree_selection.select_path(0)

    def run(self):
        """
        Display the dialog and return the selected surnames when done.
        """
        response = self.__dlg.run()
        surname_set = set()
        if response == Gtk.ResponseType.ACCEPT:
            (mode, paths) = self.__tree_selection.get_selected_rows()
            for path in paths:
                tree_iter = self.__model.get_iter(path)
                surname = self.__model.get_value(tree_iter, 0)
                surname_set.add(surname)
        if response != Gtk.ResponseType.DELETE_EVENT:
            # ManagedWindow: set the parent dialog to be modal again
            self.close()
        return surname_set

    def build_menu_names(self, obj):
        return (_("Select surname"), None)


# -------------------------------------------------------------------------
#
# GuiStringOption class
#
# -------------------------------------------------------------------------
class GuiStringOption(Gtk.Entry):
    """
    This class displays an option that is a simple one-line string.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.StringOption
        @return: nothing
        """
        Gtk.Entry.__init__(self)
        self.__option = option
        self.set_text(self.__option.get_value())

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.connect("changed", self.__text_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __text_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        self.__option.disable_signals()
        self.__option.set_value(self.get_text())
        self.__option.enable_signals()

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.handler_block(self.changekey)
        self.set_text(self.__option.get_value())
        self.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiColorOption class
#
# -------------------------------------------------------------------------
class GuiColorOption(Gtk.ColorButton):
    """
    This class displays an option that allows the selection of a colour.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        self.__option = option
        Gtk.ColorButton.__init__(self)
        rgba = Gdk.RGBA()
        rgba.parse(self.__option.get_value())
        self.set_rgba(rgba)

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.connect("color-set", self.__color_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __color_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of color made by the user.
        """
        rgba = self.get_rgba()
        value = "#%02x%02x%02x" % (
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255),
        )

        self.__option.disable_signals()
        self.__option.set_value(value)
        self.__option.enable_signals()

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.handler_block(self.changekey)
        rgba = Gdk.RGBA()
        rgba.parse(self.__option.get_value())
        self.set_rgba(rgba)
        self.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiNumberOption class
#
# -------------------------------------------------------------------------
class GuiNumberOption(Gtk.SpinButton):
    """
    This class displays an option that is a simple number with defined maximum
    and minimum values.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        self.__option = option

        decimals = 0
        step = self.__option.get_step()
        adj = Gtk.Adjustment(
            value=1,
            lower=self.__option.get_min(),
            upper=self.__option.get_max(),
            step_increment=step,
        )

        # Calculate the number of decimal places if necessary
        if step < 1:
            import math

            decimals = int(math.log10(step) * -1)

        Gtk.SpinButton.__init__(self, adjustment=adj, climb_rate=1, digits=decimals)
        Gtk.SpinButton.set_numeric(self, True)

        self.set_value(self.__option.get_value())

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.connect("value_changed", self.__number_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __number_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        vtype = type(self.__option.get_value())

        self.__option.set_value(vtype(self.get_value()))

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.handler_block(self.changekey)
        self.set_value(self.__option.get_value())
        self.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiTextOption class
#
# -------------------------------------------------------------------------
class GuiTextOption(Gtk.ScrolledWindow):
    """
    This class displays an option that is a multi-line string.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        self.__option = option
        Gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(Gtk.ShadowType.IN)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)

        # Add a TextView
        value = self.__option.get_value()
        gtext = Gtk.TextView()
        gtext.set_size_request(-1, 70)
        gtext.get_buffer().set_text("\n".join(value))
        gtext.set_editable(1)
        gtext.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.add(gtext)
        self.__buff = gtext.get_buffer()

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.bufcon = self.__buff.connect("changed", self.__text_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        # Required for tooltip
        gtext.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        gtext.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
        gtext.set_tooltip_text(self.__option.get_help())

    def __text_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        text_val = str(
            self.__buff.get_text(
                self.__buff.get_start_iter(), self.__buff.get_end_iter(), False
            )
        )

        self.__option.disable_signals()
        self.__option.set_value(text_val.split("\n"))
        self.__option.enable_signals()

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.__buff.handler_block(self.bufcon)

        value = self.__option.get_value()

        # Can only set using a string.  If we have a string value,
        # we'll use that.  If not, we'll assume a list and convert
        # it into a single string by assuming each list element
        # is separated by a newline.
        if isinstance(value, str):
            self.__buff.set_text(value)

            # Need to manually call the other handler so that the option
            # value is changed to be a list.  If left as a string,
            # it would be treated as a list, meaning each character
            # becomes a list element -- not what we want.
            self.__text_changed(None)
        else:
            self.__buff.set_text("\n".join(value))

        self.__buff.handler_unblock(self.bufcon)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None

        self.__buff.disconnect(self.bufcon)
        self.__buff = None


# -------------------------------------------------------------------------
#
# GuiBooleanOption class
#
# -------------------------------------------------------------------------
class GuiBooleanOption(Gtk.CheckButton):
    """
    This class displays an option that is a boolean (True or False).
    """

    def __init__(self, option, dbstate, uistate, track, override):
        self.__option = option
        Gtk.CheckButton.__init__(self)
        self.set_label(self.__option.get_label())
        self.set_active(self.__option.get_value())

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.connect("toggled", self.__state_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __state_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        self.__option.set_value(self.get_active())

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.handler_block(self.changekey)
        self.set_active(self.__option.get_value())
        self.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiEnumeratedListOption class
#
# -------------------------------------------------------------------------
class GuiEnumeratedListOption(Gtk.Box):
    """
    This class displays an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        Gtk.Box.__init__(self)
        evt_box = Gtk.EventBox()
        self.__option = option
        self.__combo = Gtk.ComboBoxText()
        if len(option.get_items()) > 18:
            self.__combo.set_popup_fixed_width(False)
            self.__combo.set_wrap_width(3)
        evt_box.add(self.__combo)
        self.pack_start(evt_box, True, True, 0)

        self.__update_options()

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.__combo.connect("changed", self.__selection_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey1 = self.__option.connect("options-changed", self.__update_options)
        self.conkey2 = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __selection_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        index = self.__combo.get_active()
        if index < 0:
            return
        items = self.__option.get_items()
        value, description = items[index]  # IGNORE:W0612 - description is unused

        # Don't disable the __option signals as is normally done for
        # the other widgets or bad things happen (like other needed
        # signals don't fire)

        self.__option.set_value(value)
        self.value_changed()  # Allow overriding so that another class
        # can add functionality

    def value_changed(self):
        """Allow overriding so that another class can add functionality"""
        pass

    def __update_options(self):
        """
        Handle the change of the available options.
        """
        self.__combo.remove_all()
        # self.__combo.get_model().clear()
        cur_val = self.__option.get_value()
        active_index = 0
        current_index = 0
        for value, description in self.__option.get_items():
            self.__combo.append_text(description)
            if value == cur_val:
                active_index = current_index
            current_index += 1
        self.__combo.set_active(active_index)

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.__combo.handler_block(self.changekey)
        self.__update_options()
        self.__combo.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey1)
        self.__option.disconnect(self.conkey2)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiPersonOption class
#
# -------------------------------------------------------------------------
class GuiPersonOption(Gtk.Box):
    """
    This class displays an option that allows a person from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.PersonOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__person_label = Gtk.Label()
        self.__person_label.set_halign(Gtk.Align.START)

        pevt = Gtk.EventBox()
        pevt.add(self.__person_label)
        person_button = widgets.SimpleButton("gtk-index", self.__get_person_clicked)
        person_button.set_relief(Gtk.ReliefStyle.NORMAL)

        self.pack_start(pevt, False, True, 0)
        self.pack_end(person_button, False, True, 0)

        gid = self.__option.get_value()

        # Pick up the active person
        try:
            person_handle = self.__uistate.get_active("Person")
            person = self.__dbstate.db.get_person_from_handle(person_handle)

            if override or not person:
                # Pick up the stored option value if there is one
                person = self.__db.get_person_from_gramps_id(gid)

            if not person:
                # If all else fails, get the default person to avoid bad values
                person = self.__db.get_default_person()

            if not person:
                person = self.__db.find_initial_person()
        except HandleError:
            person = None

        self.__update_person(person)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        pevt.set_tooltip_text(self.__option.get_help())
        person_button.set_tooltip_text(_("Select a different person"))

    def __get_person_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different person.
        """
        # Create a filter for the person selector.
        rfilter = GenericFilter()
        rfilter.set_logical_op("or")
        rfilter.add_rule(rules.person.IsBookmarked([]))
        rfilter.add_rule(rules.person.HasIdOf([self.__option.get_value()]))

        # Add the database home person if one exists.
        default_person = self.__db.get_default_person()
        if default_person:
            gid = default_person.get_gramps_id()
            rfilter.add_rule(rules.person.HasIdOf([gid]))

        # Add the selected person if one exists.
        person_handle = self.__uistate.get_active("Person")
        active_person = self.__dbstate.db.get_person_from_handle(person_handle)
        if active_person:
            gid = active_person.get_gramps_id()
            rfilter.add_rule(rules.person.HasIdOf([gid]))

        select_class = SelectorFactory("Person")
        sel = select_class(
            self.__dbstate,
            self.__uistate,
            self.__track,
            title=_("Select a person for the report"),
            filter=rfilter,
        )
        person = sel.run()
        self.__update_person(person)

    def __update_person(self, person):
        """
        Update the currently selected person.
        """
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.__person_label.set_text("%s (%s)" % (name, gid))
            self.__option.set_value(gid)

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        gid = self.__option.get_value()
        name = _nd.display(self.__db.get_person_from_gramps_id(gid))

        self.__person_label.set_text("%s (%s)" % (name, gid))

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiFamilyOption class
#
# -------------------------------------------------------------------------
class GuiFamilyOption(Gtk.Box):
    """
    This class displays an option that allows a family from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.FamilyOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__family_label = Gtk.Label()
        self.__family_label.set_halign(Gtk.Align.START)

        pevt = Gtk.EventBox()
        pevt.add(self.__family_label)
        family_button = widgets.SimpleButton("gtk-index", self.__get_family_clicked)
        family_button.set_relief(Gtk.ReliefStyle.NORMAL)

        self.pack_start(pevt, False, True, 0)
        self.pack_end(family_button, False, True, 0)

        self.__initialize_family(override)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        pevt.set_tooltip_text(self.__option.get_help())
        family_button.set_tooltip_text(_("Select a different family"))

    def __initialize_family(self, override):
        """
        Find a family to initialize the option with. If there is no specified
        family, try to find a family that the user is likely interested in.
        """
        family_list = []

        fid = self.__option.get_value()
        fid_family = self.__db.get_family_from_gramps_id(fid)
        active_family = self.__uistate.get_active("Family")

        if override and fid_family:
            # Use the stored option value if there is one
            family_list = [fid_family.get_handle()]

        if active_family and not family_list:
            # Use the active family if one is selected
            family_list = [active_family]

        if not family_list:
            # Next try the family of the active person
            person_handle = self.__uistate.get_active("Person")
            person = self.__dbstate.db.get_person_from_handle(person_handle)
            if person:
                family_list = person.get_family_handle_list()

        if fid_family and not family_list:
            # Next try the stored option value if there is one
            family_list = [fid_family.get_handle()]

        if not family_list:
            # Next try the family of the default person in the database.
            person = self.__db.get_default_person()
            if person:
                family_list = person.get_family_handle_list()

        if not family_list:
            # Finally, take any family you can find.
            for family in self.__db.iter_family_handles():
                self.__update_family(family)
                break
        else:
            self.__update_family(family_list[0])

    def __get_family_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different family.
        """
        # Create a filter for the person selector.
        rfilter = GenericFilterFactory("Family")()
        rfilter.set_logical_op("or")

        # Add the current family
        rfilter.add_rule(rules.family.HasIdOf([self.__option.get_value()]))

        # Add all bookmarked families
        rfilter.add_rule(rules.family.IsBookmarked([]))

        # Add the families of the database home person if one exists.
        default_person = self.__db.get_default_person()
        if default_person:
            family_list = default_person.get_family_handle_list()
            for family_handle in family_list:
                family = self.__db.get_family_from_handle(family_handle)
                gid = family.get_gramps_id()
                rfilter.add_rule(rules.family.HasIdOf([gid]))

        # Add the families of the selected person if one exists.
        # Same code as above one ! See bug #5032 feature request #5038
        ### active_person = self.__uistate.get_active('Person') ###
        # active_person = self.__db.get_default_person()
        # if active_person:
        # family_list = active_person.get_family_handle_list()
        # for family_handle in family_list:
        # family = self.__db.get_family_from_handle(family_handle)
        # gid = family.get_gramps_id()
        # rfilter.add_rule(rules.family.HasIdOf([gid]))

        select_class = SelectorFactory("Family")
        sel = select_class(self.__dbstate, self.__uistate, self.__track, filter=rfilter)
        family = sel.run()
        if family:
            self.__update_family(family.get_handle())

    def __update_family(self, handle):
        """
        Update the currently selected family.
        """
        if handle:
            family = self.__dbstate.db.get_family_from_handle(handle)
            family_id = family.get_gramps_id()
            fhandle = family.get_father_handle()
            mhandle = family.get_mother_handle()

            if fhandle:
                father = self.__db.get_person_from_handle(fhandle)
                father_name = _nd.display(father)
            else:
                father_name = _("unknown father")

            if mhandle:
                mother = self.__db.get_person_from_handle(mhandle)
                mother_name = _nd.display(mother)
            else:
                mother_name = _("unknown mother")

            name = _("%(father_name)s and %(mother_name)s (%(family_id)s)") % {
                "father_name": father_name,
                "mother_name": mother_name,
                "family_id": family_id,
            }

            self.__family_label.set_text(name)
            self.__option.set_value(family_id)

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        fid = self.__option.get_value()
        handle = self.__db.get_family_from_gramps_id(fid).get_handle()

        # Need to disable signals as __update_family() calls set_value()
        # which would launch the 'value-changed' signal which is what
        # we are reacting to here in the first place (don't need the
        # signal repeated)
        self.__option.disable_signals()
        self.__update_family(handle)
        self.__option.enable_signals()

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiNoteOption class
#
# -------------------------------------------------------------------------
class GuiNoteOption(Gtk.Box):
    """
    This class displays an option that allows a note from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.NoteOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__note_label = Gtk.Label()
        self.__note_label.set_halign(Gtk.Align.START)

        pevt = Gtk.EventBox()
        pevt.add(self.__note_label)
        note_button = widgets.SimpleButton("gtk-index", self.__get_note_clicked)
        note_button.set_relief(Gtk.ReliefStyle.NORMAL)

        self.pack_start(pevt, False, True, 0)
        self.pack_end(note_button, False, True, 0)

        # Initialize to the current value
        nid = self.__option.get_value()
        note = self.__db.get_note_from_gramps_id(nid)
        self.__update_note(note)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        pevt.set_tooltip_text(self.__option.get_help())
        note_button.set_tooltip_text(_("Select an existing note"))

    def __get_note_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different note.
        """
        select_class = SelectorFactory("Note")
        sel = select_class(self.__dbstate, self.__uistate, self.__track)
        note = sel.run()
        self.__update_note(note)

    def __update_note(self, note):
        """
        Update the currently selected note.
        """
        if note:
            note_id = note.get_gramps_id()
            txt = " ".join(note.get().split())
            if len(txt) > 35:
                txt = txt[:35] + "..."
            txt = "%s [%s]" % (txt, note_id)

            self.__note_label.set_text(txt)
            self.__option.set_value(note_id)
        else:
            txt = "<i>%s</i>" % _("No note given, click button to select one")
            self.__note_label.set_text(txt)
            self.__note_label.set_use_markup(True)
            self.__option.set_value("")

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        nid = self.__option.get_value()
        note = self.__db.get_note_from_gramps_id(nid)

        # Need to disable signals as __update_note() calls set_value()
        # which would launch the 'value-changed' signal which is what
        # we are reacting to here in the first place (don't need the
        # signal repeated)
        self.__option.disable_signals()
        self.__update_note(note)
        self.__option.enable_signals()

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiMediaOption class
#
# -------------------------------------------------------------------------
class GuiMediaOption(Gtk.Box):
    """
    This class displays an option that allows a media object from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.MediaOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__media_label = Gtk.Label()
        self.__media_label.set_halign(Gtk.Align.START)

        pevt = Gtk.EventBox()
        pevt.add(self.__media_label)
        media_button = widgets.SimpleButton("gtk-index", self.__get_media_clicked)
        media_button.set_relief(Gtk.ReliefStyle.NORMAL)

        self.pack_start(pevt, False, True, 0)
        self.pack_end(media_button, False, True, 0)

        # Initialize to the current value
        mid = self.__option.get_value()
        media = self.__db.get_media_from_gramps_id(mid)
        self.__update_media(media)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        pevt.set_tooltip_text(self.__option.get_help())
        media_button.set_tooltip_text(_("Select an existing media object"))

    def __get_media_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different note.
        """
        select_class = SelectorFactory("Media")
        sel = select_class(self.__dbstate, self.__uistate, self.__track)
        media = sel.run()
        self.__update_media(media)

    def __update_media(self, media):
        """
        Update the currently selected media.
        """
        if media:
            media_id = media.get_gramps_id()
            txt = "%s [%s]" % (media.get_description(), media_id)

            self.__media_label.set_text(txt)
            self.__option.set_value(media_id)
        else:
            txt = "<i>%s</i>" % _("No image given, click button to select one")
            self.__media_label.set_text(txt)
            self.__media_label.set_use_markup(True)
            self.__option.set_value("")

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        mid = self.__option.get_value()
        media = self.__db.get_media_from_gramps_id(mid)

        # Need to disable signals as __update_media() calls set_value()
        # which would launch the 'value-changed' signal which is what
        # we are reacting to here in the first place (don't need the
        # signal repeated)
        self.__option.disable_signals()
        self.__update_media(media)
        self.__option.enable_signals()

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiPersonListOption class
#
# -------------------------------------------------------------------------
class GuiPersonListOption(Gtk.Box):
    """
    This class displays a widget that allows multiple people from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.PersonListOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.set_size_request(150, 100)

        self.__model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.__tree_view = Gtk.TreeView(model=self.__model)
        col1 = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        self.__scrolled_window = Gtk.ScrolledWindow()
        self.__scrolled_window.add(self.__tree_view)
        self.__scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.__scrolled_window.set_shadow_type(Gtk.ShadowType.OUT)

        self.pack_start(self.__scrolled_window, True, True, 0)

        self.__value_changed()

        # now setup the '+' and '-' pushbutton for adding/removing people from
        # the container
        self.__add_person = widgets.SimpleButton("list-add", self.__add_person_clicked)
        self.__del_person = widgets.SimpleButton(
            "list-remove", self.__del_person_clicked
        )
        self.__vbbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        self.__vbbox.add(self.__add_person)
        self.__vbbox.add(self.__del_person)
        self.__vbbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.pack_end(self.__vbbox, False, False, 0)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__tree_view.set_tooltip_text(self.__option.get_help())

    def __add_person_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the add person button.
        """
        # people we already have must be excluded
        # so we don't list them multiple times
        skip_list = set()
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            gid = self.__model.get_value(tree_iter, 1)  # get the GID in col. #1
            person = self.__db.get_person_from_gramps_id(gid)
            skip_list.add(person.get_handle())
            tree_iter = self.__model.iter_next(tree_iter)

        select_class = SelectorFactory("Person")
        sel = select_class(self.__dbstate, self.__uistate, self.__track, skip=skip_list)
        person = sel.run()
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.__model.append([name, gid])

            # if this person has a spouse, ask if we should include the spouse
            # in the list of "people of interest"
            #
            # NOTE: we may want to make this an optional thing, determined
            # by the use of a parameter at the time this class is instatiated
            family_list = person.get_family_handle_list()
            for family_handle in family_list:
                family = self.__db.get_family_from_handle(family_handle)

                if person.get_handle() == family.get_father_handle():
                    spouse_handle = family.get_mother_handle()
                else:
                    spouse_handle = family.get_father_handle()

                if spouse_handle and (spouse_handle not in skip_list):
                    spouse = self.__db.get_person_from_handle(spouse_handle)
                    spouse_name = _nd.display(spouse)
                    text = _("Also include %s?") % spouse_name

                    prompt = OptionDialog(
                        _("Select Person"),
                        text,
                        _("No"),
                        None,
                        _("Yes"),
                        None,
                        parent=self.__uistate.window,
                    )
                    if prompt.get_response() == Gtk.ResponseType.YES:
                        gid = spouse.get_gramps_id()
                        self.__model.append([spouse_name, gid])

            self.__update_value()

    def __del_person_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the delete person button.
        """
        (path, column) = self.__tree_view.get_cursor()
        if path:
            tree_iter = self.__model.get_iter(path)
            self.__model.remove(tree_iter)
            self.__update_value()

    def __update_value(self):
        """
        Parse the object and return.
        """
        gidlist = ""
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            gid = self.__model.get_value(tree_iter, 1)
            gidlist = gidlist + gid + " "
            tree_iter = self.__model.iter_next(tree_iter)

        # Supress signals so that the set_value() handler
        # (__value_changed()) doesn't get called
        self.__option.disable_signals()
        self.__option.set_value(gidlist)
        self.__option.enable_signals()

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        value = self.__option.get_value()

        if not isinstance(value, str):
            # Convert array into a string
            # (convienence so that programmers can
            # set value using a list)
            value = " ".join(value)

            # Need to change __option value to be the string

            self.__option.disable_signals()
            self.__option.set_value(value)
            self.__option.enable_signals()

        # Remove all entries (the new values will REPLACE
        # rather than APPEND)
        self.__model.clear()

        for gid in value.split():
            person = self.__db.get_person_from_gramps_id(gid)
            if person:
                name = _nd.display(person)
                self.__model.append([name, gid])

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiPlaceListOption class
#
# -------------------------------------------------------------------------
class GuiPlaceListOption(Gtk.Box):
    """
    This class displays a widget that allows multiple places from the
    database to be selected.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.PlaceListOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.set_size_request(150, 150)

        self.__model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.__tree_view = Gtk.TreeView(self.__model)
        col1 = Gtk.TreeViewColumn(_("Place"), Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        self.__scrolled_window = Gtk.ScrolledWindow()
        self.__scrolled_window.add(self.__tree_view)
        self.__scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.__scrolled_window.set_shadow_type(Gtk.ShadowType.OUT)

        self.pack_start(self.__scrolled_window, True, True, 0)

        self.__value_changed()

        # now setup the '+' and '-' pushbutton for adding/removing places from
        # the container
        self.__add_place = widgets.SimpleButton("list-add", self.__add_place_clicked)
        self.__del_place = widgets.SimpleButton("list-remove", self.__del_place_clicked)
        self.__vbbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        self.__vbbox.add(self.__add_place)
        self.__vbbox.add(self.__del_place)
        self.__vbbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.pack_end(self.__vbbox, False, False, 0)

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__tree_view.set_tooltip_text(self.__option.get_help())

    def __add_place_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the add place button.
        """
        # places we already have must be excluded
        # so we don't list them multiple times
        skip_list = set()
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            gid = self.__model.get_value(tree_iter, 1)  # get the GID in col. #1
            place = self.__db.get_place_from_gramps_id(gid)
            skip_list.add(place.get_handle())
            tree_iter = self.__model.iter_next(tree_iter)

        select_class = SelectorFactory("Place")
        sel = select_class(self.__dbstate, self.__uistate, self.__track, skip=skip_list)
        place = sel.run()
        if place:
            place_name = _pd.display(self.__db, place)
            gid = place.get_gramps_id()
            self.__model.append([place_name, gid])
            self.__update_value()

    def __del_place_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the delete place button.
        """
        (path, column) = self.__tree_view.get_cursor()
        if path:
            tree_iter = self.__model.get_iter(path)
            self.__model.remove(tree_iter)
            self.__update_value()

    def __update_value(self):
        """
        Parse the object and return.
        """
        gidlist = ""
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            gid = self.__model.get_value(tree_iter, 1)
            gidlist = gidlist + gid + " "
            tree_iter = self.__model.iter_next(tree_iter)
        self.__option.set_value(gidlist)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        value = self.__option.get_value()

        if not isinstance(value, str):
            # Convert array into a string
            # (convienence so that programmers can
            # set value using a list)
            value = " ".join(value)

            # Need to change __option value to be the string

            self.__option.disable_signals()
            self.__option.set_value(value)
            self.__option.enable_signals()

        # Remove all entries (the new values will REPLACE
        # rather than APPEND)
        self.__model.clear()

        for gid in value.split():
            place = self.__db.get_place_from_gramps_id(gid)
            if place:
                place_name = _pd.display(self.__db, place)
                self.__model.append([place_name, gid])

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiSurnameColorOption class
#
# -------------------------------------------------------------------------
class GuiSurnameColorOption(Gtk.Box):
    """
    This class displays a widget that allows multiple surnames to be
    selected from the database, and to assign a colour (not necessarily
    unique) to each one.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.SurnameColorOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        item = uistate.gwm.get_item_from_track(track)
        self.__parent = item[0].window if isinstance(item, list) else item.window

        self.set_size_request(150, 150)

        # This will get populated the first time the dialog is run,
        # and used each time after.
        self.__surnames = {}  # list of surnames and count

        self.__model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.__tree_view = Gtk.TreeView(model=self.__model)
        self.__tree_view.connect("row-activated", self.__row_clicked)
        col1 = Gtk.TreeViewColumn(_("Surname"), Gtk.CellRendererText(), text=0)
        col2 = Gtk.TreeViewColumn(_("Color"), Gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sort_column_id(0)
        col1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.__tree_view)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window.set_shadow_type(Gtk.ShadowType.OUT)
        self.pack_start(self.scrolled_window, True, True, 0)

        self.add_surname = widgets.SimpleButton("list-add", self.__add_clicked)
        self.del_surname = widgets.SimpleButton("list-remove", self.__del_clicked)
        self.vbbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        self.vbbox.add(self.add_surname)
        self.vbbox.add(self.del_surname)
        self.vbbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.pack_end(self.vbbox, False, False, 0)

        self.__value_changed()

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__tree_view.set_tooltip_text(self.__option.get_help())

    def __add_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the add surname button.
        """
        skip_list = set()
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            surname = self.__model.get_value(tree_iter, 0)
            skip_list.add(surname.encode("iso-8859-1", "xmlcharrefreplace"))
            tree_iter = self.__model.iter_next(tree_iter)

        ln_dialog = LastNameDialog(
            self.__db, self.__uistate, self.__track, self.__surnames, skip_list
        )
        surname_set = ln_dialog.run()
        for surname in surname_set:
            self.__model.append([surname, "#ffffff"])
        self.__update_value()

    def __del_clicked(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the delete surname button.
        """
        (path, column) = self.__tree_view.get_cursor()
        if path:
            tree_iter = self.__model.get_iter(path)
            self.__model.remove(tree_iter)
            self.__update_value()

    def __row_clicked(self, treeview, path, column):
        """
        Handle the case of a row being clicked on.
        """
        # get the surname and colour value for this family
        tree_iter = self.__model.get_iter(path)
        surname = self.__model.get_value(tree_iter, 0)
        rgba = Gdk.RGBA()
        rgba.parse(self.__model.get_value(tree_iter, 1))

        title = _("Select color for %s") % surname
        colour_dialog = Gtk.ColorChooserDialog(title=title, transient_for=self.__parent)
        colour_dialog.set_rgba(rgba)
        response = colour_dialog.run()

        if response == Gtk.ResponseType.OK:
            rgba = colour_dialog.get_rgba()
            colour_name = "#%02x%02x%02x" % (
                int(rgba.red * 255),
                int(rgba.green * 255),
                int(rgba.blue * 255),
            )
            self.__model.set_value(tree_iter, 1, colour_name)

        colour_dialog.destroy()
        self.__update_value()

    def __update_value(self):
        """
        Parse the object and return.
        """
        surname_colours = ""
        tree_iter = self.__model.get_iter_first()
        while tree_iter:
            surname = self.__model.get_value(tree_iter, 0)
            # surname = surname.encode('iso-8859-1', 'xmlcharrefreplace')
            colour = self.__model.get_value(tree_iter, 1)
            # Tried to use a dictionary, and tried to save it as a tuple,
            # but couldn't get this to work right -- this is lame, but now
            # the surnames and colours are saved as a plain text string
            #
            # Hmmm...putting whitespace between the fields causes
            # problems when the surname has whitespace -- for example,
            # with surnames like "Del Monte".  So now we insert a non-
            # whitespace character which is unlikely to appear in
            # a surname.  (See bug report #2162.)
            surname_colours += surname + "\xb0" + colour + "\xb0"
            tree_iter = self.__model.iter_next(tree_iter)
        self.__option.set_value(surname_colours)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        value = self.__option.get_value()

        if not isinstance(value, str):
            # Convert dictionary into a string
            # (convienence so that programmers can
            # set value using a dictionary)
            value_str = ""

            for name in value:
                value_str += "%s\xb0%s\xb0" % (name, value[name])

            value = value_str

            # Need to change __option value to be the string

            self.__option.disable_signals()
            self.__option.set_value(value)
            self.__option.enable_signals()

        # Remove all entries (the new values will REPLACE
        # rather than APPEND)
        self.__model.clear()

        # populate the surname/colour treeview
        #
        # For versions prior to 3.0.2, the fields were delimited with
        # whitespace.  However, this causes problems when the surname
        # also has a space within it.  When populating the control,
        # support both the new and old format -- look for the \xb0
        # delimiter, and if it isn't there, assume this is the old-
        # style space-delimited format.  (Bug #2162.)
        if value.find("\xb0") >= 0:
            tmp = value.split("\xb0")
        else:
            tmp = value.split(" ")
        while len(tmp) > 1:
            surname = tmp.pop(0)
            colour = tmp.pop(0)
            self.__model.append([surname, colour])

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiDestinationOption class
#
# -------------------------------------------------------------------------
class GuiDestinationOption(Gtk.Box):
    """
    This class displays an option that allows the user to select a
    DestinationOption.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.DestinationOption
        @return: nothing
        """
        Gtk.Box.__init__(self)
        self.__option = option
        self.__uistate = uistate
        self.__entry = Gtk.Entry()
        self.__entry.set_text(self.__option.get_value())

        self.__button = Gtk.Button()
        img = Gtk.Image()
        img.set_from_icon_name("document-open", Gtk.IconSize.BUTTON)
        self.__button.add(img)
        self.__button.connect("clicked", self.__select_file)

        self.pack_start(self.__entry, True, True, 0)
        self.pack_end(self.__button, False, False, 0)

        # Set up signal handlers when the widget value is changed
        # from user interaction or programmatically.  When handling
        # a specific signal, we need to temporarily block the signal
        # that would call the other signal handler.
        self.changekey = self.__entry.connect("changed", self.__text_changed)
        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.conkey1 = self.__option.connect("options-changed", self.__option_changed)
        self.conkey2 = self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __option_changed(self):
        """
        Handle a change of the option.
        """
        extension = self.__option.get_extension()
        directory = self.__option.get_directory_entry()
        value = self.__option.get_value()

        if not directory and not value.endswith(extension):
            value = value + extension
            self.__option.set_value(value)
        elif directory and value.endswith(extension):
            value = value[: -len(extension)]
            self.__option.set_value(value)

        self.__entry.set_text(self.__option.get_value())

    def __select_file(self, obj):
        """
        Handle the user's request to select a file (or directory).
        """
        if self.__option.get_directory_entry():
            my_action = Gtk.FileChooserAction.SELECT_FOLDER
        else:
            my_action = Gtk.FileChooserAction.SAVE

        fcd = Gtk.FileChooserDialog(
            title=_("Save As"), action=my_action, transient_for=self.__uistate.window
        )
        fcd.add_buttons(
            _("_Cancel"), Gtk.ResponseType.CANCEL, _("_Open"), Gtk.ResponseType.OK
        )

        name = os.path.abspath(self.__option.get_value())
        if self.__option.get_directory_entry():
            while not os.path.isdir(name):
                # Keep looking up levels to find a valid drive.
                name, tail = os.path.split(name)
                if not name:
                    # Avoid infinite loops
                    name = get_curr_dir
            fcd.set_current_folder(name)
        else:
            fcd.set_current_name(os.path.basename(name))
            fcd.set_current_folder(os.path.dirname(name))

        status = fcd.run()
        if status == Gtk.ResponseType.OK:
            path = fcd.get_filename()
            if path:
                if not self.__option.get_directory_entry() and not path.endswith(
                    self.__option.get_extension()
                ):
                    path = path + self.__option.get_extension()
                self.__entry.set_text(path)
                self.__option.set_value(path)
        fcd.destroy()

    def __text_changed(self, obj):  # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value made by the user.
        """
        self.__option.disable_signals()
        self.__option.set_value(self.__entry.get_text())
        self.__option.enable_signals()

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        self.__entry.handler_block(self.changekey)
        self.__entry.set_text(self.__option.get_value())
        self.__entry.handler_unblock(self.changekey)

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option.disconnect(self.conkey1)
        self.__option.disconnect(self.conkey2)
        self.__option = None


# -------------------------------------------------------------------------
#
# GuiStyleOption class
#
# -------------------------------------------------------------------------
class GuiStyleOption(GuiEnumeratedListOption):  # TODO this is likely dead code
    """
    This class displays a StyleOption.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        """
        @param option: The option to display.
        @type option: gen.plug.menu.StyleOption
        @return: nothing
        """
        GuiEnumeratedListOption.__init__(self, option, dbstate, uistate, track)
        self.__option = option

        self.__button = Gtk.Button("%s..." % _("Style Editor"))
        self.__button.connect("clicked", self.__on_style_edit_clicked)

        self.pack_end(self.__button, False, False)
        self.uistate = uistate
        self.track = track

    def __on_style_edit_clicked(self, *obj):
        """The user has clicked on the 'Edit Styles' button.  Create a
        style sheet editor object and let them play.  When they are
        done, update the displayed styles."""
        from gramps.gen.plug.docgen import StyleSheetList
        from .report._styleeditor import StyleListDisplay

        style_list = StyleSheetList(
            self.__option.get_style_file(), self.__option.get_default_style()
        )
        StyleListDisplay(style_list, self.uistate, self.track)

        new_items = []
        for style_name in style_list.get_style_names():
            new_items.append((style_name, style_name))
        self.__option.set_items(new_items)


# -------------------------------------------------------------------------
#
# GuiBooleanListOption class
#
# -------------------------------------------------------------------------
class GuiBooleanListOption(Gtk.Box):
    """
    This class displays an option that provides a list of check boxes.
    Each possible value is assigned a value and a description.
    """

    def __init__(self, option, dbstate, uistate, track, override):
        Gtk.Box.__init__(self)
        self.__option = option
        self.__cbutton = []

        default = option.get_value().split(",")
        if len(default) < 15:
            columns = 2  # number of checkbox columns
        else:
            columns = 3
        column = []
        for dummy in range(columns):
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.pack_start(vbox, True, True, 0)
            column.append(vbox)
            vbox.show()

        counter = 0
        this_column_counter = 0
        ncolumn = 0
        for description in option.get_descriptions():
            button = Gtk.CheckButton(label=description)
            self.__cbutton.append(button)
            if counter < len(default):
                if default[counter] == "True":
                    button.set_active(True)
            button.connect("toggled", self.__list_changed)
            # show the items vertically, not alternating left and right
            # (if the number is uneven, the left column(s) will have one more)
            column[ncolumn].pack_start(button, True, True, 0)
            button.show()
            counter += 1
            this_column_counter += 1
            this_column_gets = (len(default) + (columns - (ncolumn + 1))) // columns
            if this_column_counter + 1 > this_column_gets:
                ncolumn += 1
                this_column_counter = 0

        self.valuekey = self.__option.connect("value-changed", self.__value_changed)

        self.__option.connect("avail-changed", self.__update_avail)
        self.__update_avail()

        self.set_tooltip_text(self.__option.get_help())

    def __list_changed(self, button):
        """
        Handle the change of the value made by the user.
        """
        value = ""
        for button in self.__cbutton:
            value = value + str(button.get_active()) + ","
        value = value[: len(value) - 1]

        self.__option.disable_signals()
        self.__option.set_value(value)
        self.__option.enable_signals()

    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

    def __value_changed(self):
        """
        Handle the change made programmatically
        """
        value = self.__option.get_value()

        self.__option.disable_signals()

        for button in self.__cbutton:
            for key in value:
                if key == button.get_label():
                    bool_value = value[key] == "True" or value[key] == True
                    button.set_active(bool_value)

        # Update __option value so that it's correct
        self.__list_changed(None)

        self.__option.enable_signals()

    def clean_up(self):
        """
        remove stuff that blocks garbage collection
        """
        self.__option.disconnect(self.valuekey)
        self.__option = None


# -----------------------------------------------------------------------------#
#                                                                             #
#   Table mapping menu types to gui widgets used in make_gui_option function  #
#                                                                             #
# -----------------------------------------------------------------------------#

from gramps.gen.plug import menu as menu

_OPTIONS = (
    (menu.BooleanListOption, True, GuiBooleanListOption),
    (menu.BooleanOption, False, GuiBooleanOption),
    (menu.ColorOption, True, GuiColorOption),
    (menu.DestinationOption, True, GuiDestinationOption),
    (menu.EnumeratedListOption, True, GuiEnumeratedListOption),
    (menu.FamilyOption, True, GuiFamilyOption),
    (menu.MediaOption, True, GuiMediaOption),
    (menu.NoteOption, True, GuiNoteOption),
    (menu.NumberOption, True, GuiNumberOption),
    (menu.PersonListOption, True, GuiPersonListOption),
    (menu.PersonOption, True, GuiPersonOption),
    (menu.PlaceListOption, True, GuiPlaceListOption),
    (menu.StringOption, True, GuiStringOption),
    (menu.StyleOption, True, GuiStyleOption),
    (menu.SurnameColorOption, True, GuiSurnameColorOption),
    (menu.TextOption, True, GuiTextOption),
    # This entry must be last!
    (menu.Option, None, None),
)
del menu


def make_gui_option(option, dbstate, uistate, track, override=False):
    """
    Stand-alone function so that Options can be used in other
    ways, too. Takes an Option and returns a GuiOption.

    override: if True will override the GuiOption's normal behavior
        (in a GuiOption-dependant fashion, for instance in a GuiPersonOption
        it will force the use of the options's value to set the GuiOption)
    """

    label, widget = True, None
    pmgr = GuiPluginManager.get_instance()
    external_options = pmgr.get_external_opt_dict()
    if option.__class__ in external_options:
        widget = external_options[option.__class__]
    else:
        for type_, label, widget in _OPTIONS:
            if isinstance(option, type_):
                break
        else:
            raise AttributeError(
                "can't make GuiOption: unknown option type: '%s'" % option
            )

    if widget:
        widget = widget(option, dbstate, uistate, track, override)

    return widget, label


def add_gui_options(dialog):
    """
    Stand-alone function to add user options to the GUI.
    """
    if not hasattr(dialog.options, "menu"):
        return
    o_menu = dialog.options.menu
    options_dict = dialog.options.options_dict
    for category in o_menu.get_categories():
        for name in o_menu.get_option_names(category):
            option = o_menu.get_option(category, name)

            # override option default with xml-saved value:
            if name in options_dict:
                option.set_value(options_dict[name])

            widget, label = make_gui_option(
                option, dialog.dbstate, dialog.uistate, dialog.track
            )
            if widget is not None:
                if label:
                    dialog.add_frame_option(category, option.get_label(), widget)
                else:
                    dialog.add_frame_option(category, "", widget)
