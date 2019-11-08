#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Utility functions that depend on GUI components or for GUI components
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
import subprocess
import threading
# gtk is not included here, because this file is currently imported
# by code that needs to run without the DISPLAY variable (eg, in
# the cli only).

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo
from gi.repository import GLib
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventType, EventRoleType, FamilyRelType
from gramps.gen.lib.person import Person
from gramps.gen.constfunc import has_display, is_quartz, mac, win
from gramps.gen.config import config
from gramps.gen.plug.utils import available_updates
from gramps.gen.errors import WindowActiveError

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class CLIVbox:
    """
    Command-line interface vbox, to keep compatible with Dialog.
    """
    def set_border_width(self, width):
        pass
    def add(self, widget):
        pass
    def set_spacing(self, spacing):
        pass

class CLIDialog:
    """
    Command-line interface vbox, to keep compatible with Dialog.
    """
    def connect(self, signal, callback):
        pass
    def set_title(self, title):
        pass
    def set_border_width(self, width):
        pass
    def set_size_request(self, width, height):
        pass
    def set_transient_for(self, window):
        pass
    def set_modal(self, flag):
        pass
    def show_all(self):
        pass
    def destroy(self):
        pass
    vbox = CLIVbox()

#-------------------------------------------------------------------------
#
#  Progress meter class
#
#-------------------------------------------------------------------------

class ProgressMeter:
    """
    Progress meter class for Gramps.

    The progress meter has two modes:

    MODE_FRACTION is used when you know the number of steps that will be taken.
    Set the total number of steps, and then call :meth:`step` that many times.
    The progress bar will progress from left to right.

    MODE_ACTIVITY is used when you don't know the number of steps that will be
    taken. Set up the total number of steps for the bar to get from one end of
    the bar to the other. Then, call :meth:`step` as many times as you want. The
    bar will move from left to right until you stop calling :meth:`step`.
    """

    MODE_FRACTION = 0
    MODE_ACTIVITY = 1

    def __init__(self, title, header='', can_cancel=False,
                 cancel_callback=None, message_area=False, parent=None):
        """
        Specify the title and the current pass header.
        """
        from gi.repository import Gtk
        self.__mode = ProgressMeter.MODE_FRACTION
        self.__pbar_max = 100.0
        self.__pbar_index = 0.0
        self.__old_val = -1
        self.__can_cancel = can_cancel
        self.__cancelled = False
        if cancel_callback:
            self.__cancel_callback = cancel_callback
        else:
            self.__cancel_callback = self.handle_cancel

        if has_display():
            self.__dialog = Gtk.Dialog()
        else:
            self.__dialog = CLIDialog()
        if self.__can_cancel:
            self.__dialog.connect('delete_event', self.__cancel_callback)
        else:
            self.__dialog.connect('delete_event', self.__warn)
        self.__dialog.set_title(title)
        self.__dialog.set_border_width(12)
        self.__dialog.vbox.set_spacing(10)
        self.__dialog.vbox.set_border_width(24)
        self.__dialog.set_size_request(400, 125)
        if not parent:  # if we don't have an explicit parent, try to find one
            for win in Gtk.Window.list_toplevels():
                if win.is_active():
                    parent = win
                    break
        # if we still don't have a parent, give up
        if parent:
            self.__dialog.set_transient_for(parent)
            self.__dialog.set_modal(True)

        tlbl = Gtk.Label(label='<span size="larger" weight="bold">%s</span>' % title)
        tlbl.set_use_markup(True)
        self.__dialog.vbox.add(tlbl)

        self.__lbl = Gtk.Label(label=header)
        self.__lbl.set_use_markup(True)
        self.__dialog.vbox.add(self.__lbl)

        self.__pbar = Gtk.ProgressBar()
        self.__dialog.vbox.add(self.__pbar)

        if self.__can_cancel:
            self.__dialog.set_size_request(350, 170)
            self.__cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
            self.__cancel_button.connect('clicked', self.__cancel_callback)
            self.__dialog.vbox.add(self.__cancel_button)

        self.message_area = None
        if message_area:
            area = Gtk.ScrolledWindow()
            text = Gtk.TextView()
            text.set_border_width(6)
            text.set_editable(False)
            self.message_area = text
            area.add(text)
            area.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.__dialog.vbox.add(area)
            self.message_area_ok = Gtk.Button.new_with_mnemonic(_('_OK'))
            self.message_area_ok.connect("clicked", self.close)
            self.message_area_ok.set_sensitive(False)
            self.__dialog.vbox.pack_start(self.message_area_ok, expand=False, fill=False)
            self.__dialog.set_size_request(500, 350)

        self.__dialog.show_all()
        if header == '':
            self.__lbl.hide()

    def append_message(self, text):
        """
        Method to add text to message area.
        """
        if self.message_area:
            buffer = self.message_area.get_buffer()
            end = buffer.get_end_iter()
            buffer.insert(end, text)
        else:
            print("Progress:", text)

    def set_message(self, text):
        """
        Sets the text of the message area.
        """
        if self.message_area:
            buffer = self.message_area.get_buffer()
            buffer.set_text(text)
        else:
            print("Progress:", text)

    def handle_cancel(self, *args, **kwargs):
        """
        Default cancel handler (if enabled).
        """
        self.__cancel_button.set_sensitive(False)
        self.__lbl.set_label(_("Canceling..."))
        self.__cancelled = True

    def get_cancelled(self):
        """
        Returns cancelled setting. True if progress meter has been
        cancelled.
        """
        return self.__cancelled

    def set_pass(self, header="", total=100, mode=MODE_FRACTION):
        """
        Reset for another pass. Provide a new header and define number
        of steps to be used.
        """

        from gi.repository import Gtk
        self.__mode = mode
        self.__pbar_max = total
        self.__pbar_index = 0.0

        # If it is cancelling, don't overwite that message:
        if not self.__cancelled:
            self.__lbl.set_text(header)
            if header == '':
                self.__lbl.hide()
            else:
                self.__lbl.show()

        if self.__mode is ProgressMeter.MODE_FRACTION:
            self.__pbar.set_fraction(0.0)
        else: # ProgressMeter.MODE_ACTIVITY
            self.__pbar.set_pulse_step(1.0/self.__pbar_max)

        while Gtk.events_pending():
            Gtk.main_iteration()

    def step(self):
        """
        Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%.
        """

        from gi.repository import Gtk
        if self.__mode is ProgressMeter.MODE_FRACTION:
            self.__pbar_index = self.__pbar_index + 1.0

            if self.__pbar_index > self.__pbar_max:
                self.__pbar_index = self.__pbar_max

            try:
                val = int(100*self.__pbar_index/self.__pbar_max)
            except ZeroDivisionError:
                val = 0

            if val != self.__old_val:
                self.__pbar.set_text("%d%%" % val)
                self.__pbar.set_fraction(val/100.0)
                self.__old_val = val
        else: # ProgressMeter.MODE_ACTIVITY
            self.__pbar.pulse()

        while Gtk.events_pending():
            Gtk.main_iteration()

        return self.__cancelled

    def set_header(self, text):
        from gi.repository import Gtk
        self.__lbl.set_text(text)
        while Gtk.events_pending():
            Gtk.main_iteration()

    def __warn(self, *obj):
        """
        Don't let the user close the progress dialog.
        """
        from .dialog import WarningDialog
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog."),
            parent=self.__dialog)
        return True

    def close(self, widget=None):
        """
        Close the progress meter
        """
        del self.__cancel_callback
        self.__dialog.destroy()

#-------------------------------------------------------------------------
#
# SystemFonts class
#
#-------------------------------------------------------------------------

class SystemFonts:
    """
    Define fonts available to Gramps

    This is a workaround for bug which prevents the list_families method
    being called more than once.

    The bug is described here: https://bugzilla.gnome.org/show_bug.cgi?id=679654

    This code generates a warning:
    /usr/local/lib/python2.7/site-packages/gi/types.py:47:
    Warning: g_value_get_object: assertion `G_VALUE_HOLDS_OBJECT (value)' failed

    To get a list of fonts, instantiate this class and call
    :meth:`get_system_fonts`

    .. todo:: GTK3: the underlying bug may be fixed at some point in the future
    """

    __FONTS = None

    def __init__(self):
        """
        Populate the class variable __FONTS only once.
        """
        if SystemFonts.__FONTS is None:
            families = PangoCairo.font_map_get_default().list_families()
            #print ('GRAMPS GTK3: a g_value_get_object warning:')
            SystemFonts.__FONTS = [family.get_name() for family in families]
            SystemFonts.__FONTS.sort()

    def get_system_fonts(self):
        """
        Return a sorted list of fonts available to Gramps
        """
        return SystemFonts.__FONTS

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def display_error_dialog (index, errorstrings, uistate=None):
    """
    Display a message box for errors resulting from xdg-open/open
    """
    from .dialog import ErrorDialog
    error = _("The external program failed to launch or experienced an error")
    if errorstrings:
        if isinstance(errorstrings, dict):
            try:
                error = errorstrings[index]
            except KeyError:
                pass
        else:
            error = errorstrings

    ErrorDialog(_("Error from external program"),
                error, parent=uistate.window)

def poll_external (args):
    """
    Check the for completion of a task launched with
    subprocess.Popen().  This function is intended to be passed to
    GLib.timeout_add_seconds, so the arguments are in a tuple because that
    function takes only a single data argument.

    :param proc: the process, returned from subprocess.Popen()
    :param errorstrings: a dict of possible response values and the
                         corresponding messages to display.
    :return: bool returned to timeout_add_seconds: should this function be
             called again?
    """
    (proc, errorstrings, uistate) = args
    resp = proc.poll()
    if resp is None:
        return True

    if resp != 0:
        display_error_dialog(resp, errorstrings, uistate)
    return False

def open_file_with_default_application(path, uistate):
    """
    Launch a program to open an arbitrary file. The file will be opened using
    whatever program is configured on the host as the default program for that
    type of file.

    :param file_path: The path to the file to be opened.
                      Example: "c:\\foo.txt"
    :type file_path: string
    :return: nothing
    """

    errstrings = None

    norm_path = os.path.normpath(path)
    if not os.path.exists(norm_path):
        display_error_dialog(0, _("File %s does not exist") % norm_path,
                             uistate)
        return

    if win():
        try:
            os.startfile(norm_path)
        except WindowsError as msg:
            display_error_dialog(0, str(msg),
                             uistate)

        return

    if mac():
        utility = '/usr/bin/open'
    else:
        utility = 'xdg-open'
        errstrings = {1:'Error in command line syntax.',
                      2:'One of the files passed on the command line did not exist.',
                      3:' A required tool could not be found.',
                      4:'The action failed.'}

    proc = subprocess.Popen([utility, norm_path], stderr=subprocess.STDOUT)

    from gi.repository import GLib
    GLib.timeout_add_seconds(1, poll_external, (proc, errstrings, uistate))
    return

def process_pending_events(max_count=10):
    """
    Process pending events, but don't get into an infinite loop.
    """
    from gi.repository import Gtk
    count = 0
    while Gtk.events_pending():
        Gtk.main_iteration()
        count += 1
        if count >= max_count:
            break

# Then there's the infamous Mac one-button mouse (or more likely these
# days, one-button trackpad). The canonical mac way to generate what
# Gdk calls a button-3 is <ctrl> button-1, but that's not baked into
# Gdk. We'll emulate the behavior here.

def is_right_click(event):
    """
    Returns True if the event is to open the context menu.
    """
    from gi.repository import Gdk
    if Gdk.Event.triggers_context_menu(event):
        return True

def color_graph_family(family, dbstate):
    """
    :return: based on the config the color for graph family node in hex
    :rtype: tuple (hex color fill, hex color border)
    """
    scheme = config.get('colors.scheme')
    for event_ref in family.get_event_ref_list():
        event = dbstate.db.get_event_from_handle(event_ref.ref)
        if (event.type == EventType.DIVORCE and
                event_ref.get_role() in (EventRoleType.FAMILY,
                                         EventRoleType.PRIMARY)):
            return (config.get('colors.family-divorced')[scheme],
                    config.get('colors.border-family-divorced')[scheme])

    fam_rel_type = family.get_relationship()

    family_color = config.get('colors.family')[scheme]
    border_color = config.get('colors.border-family')[scheme]

    if fam_rel_type == FamilyRelType.MARRIED:
        family_color = config.get('colors.family-married')[scheme]
    elif fam_rel_type == FamilyRelType.UNMARRIED:
        family_color = config.get('colors.family-unmarried')[scheme]
    elif fam_rel_type == FamilyRelType.CIVIL_UNION:
        family_color = config.get('colors.family-civil-union')[scheme]
    elif fam_rel_type == FamilyRelType.UNKNOWN:
        family_color = config.get('colors.family-unknown')[scheme]

    return (family_color, border_color)

def color_graph_box(alive=False, gender=Person.MALE):
    """
    :return: based on the config the color for graph boxes in hex
             If gender is None, an empty box is assumed
    :rtype: tuple (hex color fill, hex color border)
    """
    scheme = config.get('colors.scheme')
    if gender == Person.MALE:
        if alive:
            return (config.get('colors.male-alive')[scheme],
                    config.get('colors.border-male-alive')[scheme])
        else:
            return (config.get('colors.male-dead')[scheme],
                    config.get('colors.border-male-dead')[scheme])
    elif gender == Person.FEMALE:
        if alive:
            return (config.get('colors.female-alive')[scheme],
                    config.get('colors.border-female-alive')[scheme])
        else:
            return (config.get('colors.female-dead')[scheme],
                    config.get('colors.border-female-dead')[scheme])
    elif gender == Person.UNKNOWN:
        if alive:
            return (config.get('colors.unknown-alive')[scheme],
                    config.get('colors.border-unknown-alive')[scheme])
        else:
            return (config.get('colors.unknown-dead')[scheme],
                    config.get('colors.border-unknown-dead')[scheme])
    #empty box, no gender
    return ('#d2d6ce', '#000000')
##    print 'male alive', rgb_to_hex((185/256.0, 207/256.0, 231/256.0))
##    print 'female alive', rgb_to_hex((255/256.0, 205/256.0, 241/256.0))
##    print 'unknown alive', rgb_to_hex((244/256.0, 220/256.0, 183/256.0))
##    print 'male death', rgb_to_hex((185/256.0, 207/256.0, 231/256.0))
##    print 'female death', rgb_to_hex((255/256.0, 205/256.0, 241/256.0))
##    print 'unknown death', rgb_to_hex((244/256.0, 220/256.0, 183/256.0))
##
##    print 'border male alive', rgb_to_hex((32/256.0, 74/256.0, 135/256.0))
##    print 'border female alive', rgb_to_hex((135/256.0, 32/256.0, 106/256.0))
##    print 'border unknown alive', rgb_to_hex((143/256.0, 89/256.0, 2/256.0))
##    print 'empty', rgb_to_hex((211/256.0, 215/256.0, 207/256.0))

# color functions. For hsv and hls values, use import colorsys !

def hex_to_rgb_float(value):
    """
    Convert a 6 or 12 digit hexademical value to rgb. Returns tuple of floats
    between 0 and 1.
    """
    value = value.lstrip('#')
    lenv = len(value)
    return tuple(int(value[i:i+lenv//3], 16)/16.0**(lenv//3)
                 for i in range(0, lenv, lenv//3))

def hex_to_rgb(value):
    """
    Convert a 6 or 12 digit hexadecimal value to rgb. Returns tuple of integers.
    """
    value = value.lstrip('#')
    lenv = len(value)
    return tuple(int(value[i:i+lenv//3], 16) for i in range(0, lenv, lenv//3))

def rgb_to_hex(rgb):
    """
    Convert a tuple of integer or float rgb values to its hex value
    """
    if type(rgb[0]) == int:
        return '#%02x%02x%02x' % rgb
    else:
        rgbint = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        return '#%02x%02x%02x' % rgbint

def get_link_color(context):
    """
    Find the link color for the current theme.
    """
    from gi.repository import Gtk

    if Gtk.get_minor_version() > 11:
        col = context.get_color(Gtk.StateFlags.LINK)
    else:
        found, col = context.lookup_color('link_color')
        if not found:
            col.parse('blue')

    return rgb_to_hex((col.red, col.green, col.blue))

def edit_object(dbstate, uistate, reftype, ref):
    """
    Invokes the appropriate editor for an object type and given handle.
    """
    from .editors import (EditEvent, EditPerson, EditFamily, EditSource,
                          EditPlace, EditMedia, EditRepository, EditCitation)

    if reftype == 'Person':
        try:
            person = dbstate.db.get_person_from_handle(ref)
            EditPerson(dbstate, uistate, [], person)
        except WindowActiveError:
            pass
    elif reftype == 'Family':
        try:
            family = dbstate.db.get_family_from_handle(ref)
            EditFamily(dbstate, uistate, [], family)
        except WindowActiveError:
            pass
    elif reftype == 'Source':
        try:
            source = dbstate.db.get_source_from_handle(ref)
            EditSource(dbstate, uistate, [], source)
        except WindowActiveError:
            pass
    elif reftype == 'Citation':
        try:
            citation = dbstate.db.get_citation_from_handle(ref)
            EditCitation(dbstate, uistate, [], citation)
        except WindowActiveError:
            """
            Return the text used when citation cannot be edited
            """
            blocked_text = _("Cannot open new citation editor at this time. "
                             "Either the citation is already being edited, "
                             "or the associated source is already being "
                             "edited, and opening a citation editor "
                             "(which also allows the source "
                             "to be edited), would create ambiguity "
                             "by opening two editors on the same source. "
                             "\n\n"
                             "To edit the citation, close the source "
                             "editor and open an editor for the citation "
                             "alone")

            from .dialog import WarningDialog
            WarningDialog(_("Cannot open new citation editor"),
                          blocked_text,
                          parent=uistate.window)
    elif reftype == 'Place':
        try:
            place = dbstate.db.get_place_from_handle(ref)
            EditPlace(dbstate, uistate, [], place)
        except WindowActiveError:
            pass
    elif reftype == 'Media':
        try:
            obj = dbstate.db.get_media_from_handle(ref)
            EditMedia(dbstate, uistate, [], obj)
        except WindowActiveError:
            pass
    elif reftype == 'Event':
        try:
            event = dbstate.db.get_event_from_handle(ref)
            EditEvent(dbstate, uistate, [], event)
        except WindowActiveError:
            pass
    elif reftype == 'Repository':
        try:
            repo = dbstate.db.get_repository_from_handle(ref)
            EditRepository(dbstate, uistate, [], repo)
        except WindowActiveError:
            pass

#-------------------------------------------------------------------------
#
# AvailableUpdates
#
#-------------------------------------------------------------------------
class AvailableUpdates(threading.Thread):
    def __init__(self, uistate):
        threading.Thread.__init__(self)
        self.uistate = uistate
        self.addon_update_list = []

    def emit_update_available(self):
        self.uistate.emit('update-available', (self.addon_update_list, ))

    def run(self):
        self.addon_update_list = available_updates()
        if len(self.addon_update_list) > 0:
            GLib.idle_add(self.emit_update_available)

def model_to_text(model, cols=None, treeiter=None, indent="",
                  level=None, sep=", "):
    """
    Given a model, return the text from the rows as a string.
      model - the actual model
      cols - a list representing the columns to get, or None for all
      treeiter - (optional), initially, the first iterator
      ident - the current indent level text
      level - use None for no level indicator, or number (eg, 1)
      sep - separating text between columns
    """
    text = ""
    if treeiter is None:
        treeiter = model.get_iter_first()
    while treeiter is not None:
        if cols is None:
            items = sep.join([str(item) for item in model[treeiter][:]])
        else:
            items = sep.join([str(model[treeiter][col]) for col in cols])
        if level is not None:
            text += (indent + str(level) + ". " + items + "\n")
        else:
            text += (indent + items + "\n")
        if model.iter_has_child(treeiter):
            childiter = model.iter_children(treeiter)
            if level is not None:
                text += model_to_text(model, cols, childiter, indent + (" " * 4),
                                      level + 1, sep)
            else:
                text += model_to_text(model, cols, childiter, indent + (" " * 4),
                                      sep=sep)
        treeiter = model.iter_next(treeiter)
    return text

def text_to_clipboard(text):
    """
    Put any text into the clipboard
    """
    from gi.repository import Gdk
    from gi.repository import Gtk
    clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                                              Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)

def match_primary_mask(test_mask, addl_mask=0):
    """
    Return True if test_mask fully matches all bits of
    GdkModifierIntent.PRIMARY_ACCELERATOR and addl_mask, False
    otherwise.
    """
    keymap = Gdk.Keymap.get_default()
    primary = keymap.get_modifier_mask(Gdk.ModifierIntent.PRIMARY_ACCELERATOR)
    return ((test_mask & (primary | addl_mask)) == (primary | addl_mask))

def no_match_primary_mask(test_mask, addl_mask=0):
    """
    Return False if test_mask matches any bit of
    GdkModifierIntent.PRIMARY_ACCELERATOR or addl_mask, True
    otherwise.
    """
    keymap = Gdk.Keymap.get_default()
    primary = keymap.get_modifier_mask(Gdk.ModifierIntent.PRIMARY_ACCELERATOR)
    return (test_mask & (primary | addl_mask)) == 0
