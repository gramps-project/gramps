#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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

__all__ = [
    "MonitoredCheckbox",
    "MonitoredEntry",
    "MonitoredEntryIndicator",
    "MonitoredSpinButton",
    "MonitoredText",
    "MonitoredType",
    "MonitoredDataType",
    "MonitoredMenu",
    "MonitoredStrMenu",
    "MonitoredDate",
    "MonitoredComboSelectedEntry",
    "MonitoredTagList",
]

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.monitoredwidgets")

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..autocomp import StandardCustomSelector, fill_entry
from gramps.gen.datehandler import displayer, parser
from gramps.gen.lib.date import Date, NextYear
from gramps.gen.errors import ValidationError

# -------------------------------------------------------------------------
#
# constants
#
# ------------------------------------------------------------------------

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")


# -------------------------------------------------------------------------
#
# MonitoredCheckbox class
#
# -------------------------------------------------------------------------
class MonitoredCheckbox:
    def __init__(self, obj, button, set_val, get_val, on_toggle=None, readonly=False):
        self.button = button
        self.button.connect("toggled", self._on_toggle)
        self.on_toggle = on_toggle
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.button.set_active(get_val())
        self.button.set_sensitive(not readonly)

    def _on_toggle(self, obj):
        self.set_val(obj.get_active())
        if self.on_toggle:
            self.on_toggle(self.get_val())


##    def destroy(self):
##        """
##        Unset all elements that can prevent garbage collection
##        """
##        self.set_val = None
##        self.get_val = None
##        self.obj = None


# -------------------------------------------------------------------------
#
# MonitoredEntry class
#
# -------------------------------------------------------------------------
class MonitoredEntry:
    def __init__(
        self, obj, set_val, get_val, read_only=False, autolist=None, changed=None
    ):
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.changed = changed

        if get_val():
            self.obj.set_text(get_val())
        self.obj.connect("changed", self._on_change)
        self.obj.connect("focus-out-event", self._on_quit)
        self.obj.set_editable(not read_only)

        if autolist:
            fill_entry(obj, autolist)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def set_text(self, text):
        self.obj.set_text(text)

    def connect(self, signal, callback, *data):
        self.obj.connect(signal, callback, *data)

    def _on_quit(self, obj, event):
        self.set_val(obj.get_text().strip())

    def _on_change(self, obj):
        self.set_val(obj.get_text())
        if self.changed:
            self.changed(obj)

    def force_value(self, value):
        self.obj.set_text(value)

    def get_value(self):
        return str(self.obj.get_text())

    def enable(self, value):
        self.obj.set_sensitive(value)
        self.obj.set_editable(value)

    def grab_focus(self):
        self.obj.grab_focus()

    def update(self):
        if self.get_val() is not None:
            self.obj.set_text(self.get_val())


# -------------------------------------------------------------------------
#
# MonitoredEntryIndicator class
#
# -------------------------------------------------------------------------
class MonitoredEntryIndicator(MonitoredEntry):
    """
    Show an Entry box with an indicator in it that disappears when
    entry becomes active
    """

    def __init__(
        self,
        obj,
        set_val,
        get_val,
        indicator,
        read_only=False,
        autolist=None,
        changed=None,
    ):
        MonitoredEntry.__init__(
            self, obj, set_val, get_val, read_only, autolist, changed
        )
        self.obj.set_placeholder_text(indicator)


# -------------------------------------------------------------------------
#
# MonitoredSpinButton class
#
# -------------------------------------------------------------------------
class MonitoredSpinButton:
    """
    Class for signal handling of spinbuttons.
    (Code is a modified copy of :class:`MonitoredEntry`)
    """

    def __init__(
        self, obj, set_val, get_val, read_only=False, autolist=None, changed=None
    ):
        """
        :param obj: widget to be monitored
        :type obj: Gtk.SpinButton
        :param set_val: callback to be called when obj is changed
        :param get_val: callback to be called to retrieve value for obj
        :param read_only: If SpinButton is read only.
        """

        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.changed = changed

        if get_val():
            self.obj.set_value(get_val())
        self.obj.connect("value-changed", self._on_change)
        self.obj.set_editable(not read_only)

        if autolist:
            fill_entry(obj, autolist)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None

    def reinit(self, set_val, get_val):
        """
        Reinitialize class with the specified callback functions.

        :param set_val: callback to be called when SpinButton is changed
        :param get_val: callback to be called to retrieve value for SpinButton
        """

        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def set_value(self, value):
        """
        Set the value of the monitored widget to the specified value.

        :param value: Value to be set.
        """

        self.obj.set_value(value)

    def connect(self, signal, callback):
        """
        Connect the signal of monitored widget to the specified callback.

        :param signal: Signal prototype for which a connection should be set up.
        :param callback: Callback function to be called when signal is emitted.
        """

        self.obj.connect(signal, callback)

    def _on_change(self, obj):
        """
        Event handler to be called when the monitored widget is changed.

        :param obj: Widget that has been changed.
        :type obj: Gtk.SpinButton
        """

        self.set_val(obj.get_value())
        if self.changed:
            self.changed(obj)

    def force_value(self, value):
        """
        Set the value of the monitored widget to the specified value.

        :param value: Value to be set.
        """

        self.obj.set_value(value)

    def get_value(self):
        """
        Get the current value of the monitored widget.

        :returns: Current value of monitored widget.
        """

        return self.obj.get_value()

    def enable(self, value):
        """
        Change the property editable and sensitive of the monitored widget to
        value.

        :param value: If widget should be editable or deactivated.
        :type value: bool
        """

        self.obj.set_sensitive(value)
        self.obj.set_editable(value)

    def grab_focus(self):
        """
        Assign the keyboard focus to the monitored widget.
        """

        self.obj.grab_focus()

    def update(self):
        """
        Updates value of monitored SpinButton with the value returned by the
        get_val callback.
        """

        if self.get_val():
            self.obj.set_value(self.get_val())


# -------------------------------------------------------------------------
#
# MonitoredText class
#
# -------------------------------------------------------------------------
class MonitoredText:
    def __init__(self, obj, set_val, get_val, read_only=False):
        self.buf = obj.get_buffer()
        self.set_val = set_val
        self.get_val = get_val

        if get_val():
            self.buf.set_text(get_val())
        self.buf.connect("changed", self.on_change)
        obj.set_editable(not read_only)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.buf = None

    def on_change(self, obj):
        s, e = self.buf.get_bounds()
        self.set_val(str(self.buf.get_text(s, e, False)))


# -------------------------------------------------------------------------
#
# MonitoredType class
#
# -------------------------------------------------------------------------
class MonitoredType:
    def __init__(
        self, obj, set_val, get_val, mapping, custom, readonly=False, custom_values=None
    ):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()
        if val:
            default = val[0]
        else:
            default = None

        self.sel = StandardCustomSelector(
            mapping, obj, custom, default, additional=custom_values
        )

        self.set_val(self.sel.get_values())
        self.obj.set_sensitive(not readonly)
        self.obj.connect("changed", self.on_change)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def update(self):
        if self.get_val():
            self.sel.set_values(self.get_val())

    def on_change(self, obj):
        self.set_val(self.sel.get_values())


# -------------------------------------------------------------------------
#
# MonitoredDataType class
#
# -------------------------------------------------------------------------
class MonitoredDataType:
    def __init__(
        self,
        obj,
        set_val,
        get_val,
        readonly=False,
        custom_values=None,
        ignore_values=None,
    ):
        """
        Constructor for the MonitoredDataType class.

        :param obj: Existing ComboBox widget to use with has_entry=True.
        :type obj: Gtk.ComboBox
        :param set_val: The function that sets value of the type in the object
        :type set_val: method
        :param get_val: The function that gets value of the type in the object.
                        This returns a GrampsType, of which get_map returns all
                        possible types
        :type get_val: method
        :param custom_values: Extra values to show in the combobox. These can be
                              text of custom type, tuple with type info or
                              GrampsType class
        :type custom_values: list of str, tuple or GrampsType
        :param ignore_values: list of values not to show in the combobox. If the
                              result of get_val is in these, it is not ignored
        :type ignore_values: list of int
        """
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()

        if val:
            default = int(val)
        else:
            default = None

        map = get_val().get_map().copy()
        if ignore_values:
            for key in list(map.keys()):
                if key in ignore_values and key not in (None, default):
                    del map[key]

        self.sel = StandardCustomSelector(
            map,
            obj,
            get_val().get_custom(),
            default,
            additional=custom_values,
            menu=get_val().get_menu(),
        )

        self.sel.set_values((int(get_val()), str(get_val())))
        self.obj.set_sensitive(not readonly)
        self.obj.connect("changed", self.on_change)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def fix_value(self, value):
        if value[0] == self.get_val().get_custom():
            return value
        else:
            return (value[0], "")

    def update(self):
        val = self.get_val()
        if isinstance(val, tuple):
            self.sel.set_values(val)
        else:
            self.sel.set_values((int(val), str(val)))

    def on_change(self, obj):
        value = self.fix_value(self.sel.get_values())
        self.set_val(value)


# -------------------------------------------------------------------------
#
# MonitoredMenu class
#
# -------------------------------------------------------------------------
class MonitoredMenu:
    def __init__(self, obj, set_val, get_val, mapping, readonly=False, changed=None):
        self.set_val = set_val
        self.get_val = get_val

        self.changed = changed
        self.obj = obj

        self.change_menu(mapping)
        self.obj.connect("changed", self.on_change)
        self.obj.set_sensitive(not readonly)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None

    def force(self, value):
        self.obj.set_active(value)

    def change_menu(self, mapping):
        self.data = {}
        self.model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        index = 0
        for t, v in mapping:
            self.model.append(row=[t, v])
            self.data[v] = index
            index += 1
        self.obj.set_model(self.model)
        self.obj.set_active(self.data.get(self.get_val(), 0))

    def on_change(self, obj):
        self.set_val(self.model.get_value(obj.get_active_iter(), 1))
        if self.changed:
            self.changed()


# -------------------------------------------------------------------------
#
# MonitoredStrMenu class
#
# -------------------------------------------------------------------------
class MonitoredStrMenu:
    def __init__(self, obj, set_val, get_val, mapping, readonly=False):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj
        self.model = Gtk.ListStore(GObject.TYPE_STRING)

        # Make sure that the menu is visible on small screen devices.
        # Some LDS temples were not visible on a 4 or 5 column layout.
        # See bug #7333
        if len(mapping) > 20:
            self.obj.set_wrap_width(3)

        self.model.append(row=[""])
        index = 0
        self.data = [""]

        default = get_val()
        active = 0

        for t, v in mapping:
            self.model.append(row=[v])
            self.data.append(t)
            index += 1
            if t == default:
                active = index

        self.obj.set_model(self.model)
        self.obj.set_active(active)
        self.obj.connect("changed", self.on_change)
        self.obj.set_sensitive(not readonly)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val = None
    ##        self.get_val = None
    ##        self.obj = None
    ##        self.model = None

    def on_change(self, obj):
        self.set_val(self.data[obj.get_active()])


# -------------------------------------------------------------------------
#
# MonitoredDate class
#
# -------------------------------------------------------------------------
class MonitoredDate:
    """
    Class that associates a pixmap with a text widget, providing visual
    feedback that indicates if the text widget contains a valid date.
    """

    def __init__(self, field, button, value, uistate, track, readonly=False):
        """
        Create a connection between the date_obj, text_obj and the pixmap_obj.
        Assigns callbacks to parse and change date when the text
        in text_obj is changed, and to invoke Date Editor when the LED
        button_obj is pressed.
        """
        self.uistate = uistate
        self.track = track
        self.date_obj = value
        self.text_obj = field
        self.button_obj = button

        image = Gtk.Image()
        image.set_from_icon_name("gramps-date-edit", Gtk.IconSize.BUTTON)
        self.button_obj.set_image(image)
        self.button_obj.set_relief(Gtk.ReliefStyle.NORMAL)
        self.pixmap_obj = self.button_obj.get_child()

        self.text_obj.connect("validate", self.validate)
        self.text_obj.connect("content-changed", self.set_date)
        self.button_obj.connect("clicked", self.invoke_date_editor)

        self.text_obj.set_text(displayer.display(self.date_obj))
        self.text_obj.validate()

        self.text_obj.set_editable(not readonly)
        self.button_obj.set_sensitive(not readonly)

    def set_date(self, widget):
        """
        Parse date from text entry to date object
        """
        date = parser.parse(str(self.text_obj.get_text()))
        self.date_obj.copy(date)

    def validate(self, widget, data):
        """
        Validate current date in text entry
        """
        # if text could not be parsed it is assumed invalid
        if self.date_obj.get_modifier() == Date.MOD_TEXTONLY:
            return ValidationError(_("Bad Date"))
        elif self.date_obj.to_calendar(calendar_name=Date.CAL_GREGORIAN) >> NextYear():
            return ValidationError(_("Date more than one year in the future"))

    def invoke_date_editor(self, obj):
        """
        Invokes Date Editor dialog when the user clicks the Calendar button.
        If date was in fact built, sets the date_obj to the newly built
        date.
        """
        from ..editors import EditDate

        date_dialog = EditDate(self.date_obj, self.uistate, self.track)
        the_date = date_dialog.return_date
        self.update_after_editor(the_date)

    def update_after_editor(self, date_obj):
        """
        Update text entry and validate it
        """
        if date_obj:
            # first we set the text entry, that emits 'content-changed'
            # signal thus the date object gets updated too
            self.text_obj.set_text(displayer.display(date_obj))
            self.text_obj.validate()


# -------------------------------------------------------------------------
#
# MonitoredComboSelectedEntry class
#
# -------------------------------------------------------------------------
class MonitoredComboSelectedEntry:
    """
    A MonitoredEntry driven by a Combobox to select what the entry field
    works upon
    """

    def __init__(
        self,
        objcombo,
        objentry,
        textlist,
        set_val_list,
        get_val_list,
        default=0,
        read_only=False,
    ):
        """
        Create a MonitoredComboSelectedEntry
        Objcombo and objentry should be the gtk widgets to use
        textlist is the values that must be used in the combobox
        Every value needs an entry in set/get_val_list with the data retrieval
        and storage method of the data entered in the entry box
        Read_only should be true if no changes may be done
        default is the entry in the combobox that must be preselected
        """
        self.objcombo = objcombo
        self.objentry = objentry
        self.set_val_list = set_val_list
        self.get_val_list = get_val_list

        # fill the combobox, set on a specific entry
        self.mapping = dict(
            [[i, x] for (i, x) in zip(list(range(len(textlist))), textlist)]
        )

        self.active_key = default
        self.active_index = 0

        self.__fill()
        self.objcombo.clear()
        self.objcombo.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.objcombo.pack_start(cell, True)
        self.objcombo.add_attribute(cell, "text", 1)
        self.objcombo.set_active(self.active_index)
        self.objcombo.connect("changed", self.on_combochange)

        # fill the entrybox with required data
        self.entry_reinit()
        self.objentry.connect("changed", self._on_change_entry)

        # set correct editable
        self.enable(not read_only)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.set_val_list = None
    ##        self.get_val_list = None
    ##        self.objcombo = None
    ##        self.objentry = None

    def __fill(self):
        """
        Fill combo with data
        """
        self.store = Gtk.ListStore(GObject.TYPE_INT, GObject.TYPE_STRING)
        keys = sorted(list(self.mapping.keys()), key=self.__by_value_key)

        for index, key in enumerate(keys):
            self.store.append(row=[key, self.mapping[key]])
            if key == self.active_key:
                self.active_index = index

    def __by_value(self, first, second):
        """
        Method for sorting keys based on the values.
        """
        fvalue = self.mapping[first]
        svalue = self.mapping[second]
        return glocale.strcoll(fvalue, svalue)

    def __by_value_key(self, first):
        """
        Method for sorting keys based on the values.
        """
        return glocale.sort_key(self.mapping[first])

    def on_combochange(self, obj):
        """
        callback for change on the combo, change active iter, update
        associated entrybox
        """
        self.active_key = self.store.get_value(self.objcombo.get_active_iter(), 0)
        self.entry_reinit()

    def reinit(self, set_val_list, get_val_list):
        """
        The interface is attached to another object, so the methods need to be
        reset.
        """
        self.set_val_list = set_val_list
        self.get_val_list = get_val_list
        self.update()

    def entry_reinit(self):
        """
        Make the entry field show the value corresponding to the active key
        """
        self.objentry.set_text(self.get_val_list[self.active_key]())
        self.set_val = self.set_val_list[self.active_key]
        self.get_val = self.get_val_list[self.active_key]

    def _on_change_entry(self, obj):
        """
        Callback when the entry field changes
        """
        self.set_val_list[self.active_key](self.get_value_entry())

    def get_value_entry(self):
        return str(self.objentry.get_text())

    def enable(self, value):
        self.objentry.set_sensitive(value)
        self.objentry.set_editable(value)

    def update(self):
        """
        Method called when object changed without interface change
        Eg: name editor save brings you back to person editor that must update
        """
        self.entry_reinit()


# -------------------------------------------------------------------------
#
# MonitoredTagList class
#
# -------------------------------------------------------------------------
class MonitoredTagList:
    """
    A MonitoredTagList consists of a label to display a list of tags and a
    button to invoke the tag editor.
    """

    def __init__(
        self, label, button, set_list, get_list, db, uistate, track, readonly=False
    ):
        self.uistate = uistate
        self.track = track
        self.db = db
        self.set_list = set_list

        self.tag_list = []
        for handle in get_list():
            tag = self.db.get_tag_from_handle(handle)
            if tag:
                self.tag_list.append((handle, tag.get_name()))

        self.all_tags = []
        for handle in self.db.get_tag_handles(sort_handles=True):
            tag = self.db.get_tag_from_handle(handle)
            self.all_tags.append((tag.get_handle(), tag.get_name()))

        self.label = label
        self.label.set_halign(Gtk.Align.START)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        image = Gtk.Image()
        image.set_from_icon_name("gramps-tag", Gtk.IconSize.MENU)
        button.set_image(image)
        button.set_tooltip_text(_("Edit the tag list"))
        button.connect("button-press-event", self.cb_edit)
        button.connect("key-press-event", self.cb_edit)
        button.set_sensitive(not readonly)

        self._display()

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.uistate = None
    ##        self.track = None
    ##        self.db = None
    ##        self.set_list = None

    def _display(self):
        """
        Display the tag list.
        """
        tag_text = ", ".join(item[1] for item in self.tag_list)
        self.label.set_text(tag_text)
        self.label.set_tooltip_text(tag_text)

    def cb_edit(self, button, event):
        """
        Invoke the tag editor.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS or (
            event.type == Gdk.EventType.KEY_PRESS
            and event.keyval in (_RETURN, _KP_ENTER)
        ):
            from ..editors import EditTagList

            editor = EditTagList(self.tag_list, self.all_tags, self.uistate, self.track)
            if editor.return_list is not None:
                self.tag_list = editor.return_list
                self._display()
                self.set_list([item[0] for item in self.tag_list])
            return True
        return False
