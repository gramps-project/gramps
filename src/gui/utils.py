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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

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
from gen.ggettext import gettext as _
# gtk is not included here, because this file is currently imported
# by code that needs to run without the DISPLAY variable (eg, in
# the cli only).

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
from gi.repository import PangoCairo

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gen.constfunc import has_display, is_quartz, mac, win
from gen.config import config

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class CLIVbox():
    """
    Command-line interface vbox, to keep compatible with Dialog.
    """
    def set_border_width(self, width):
        pass
    def add(self, widget):
        pass
    def set_spacing(self, spacing):
        pass
    def set_border_width(self, width):
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

class ProgressMeter(object):
    """
    Progress meter class for GRAMPS.

    The progress meter has two modes:

    MODE_FRACTION is used when you know the number of steps that will be taken.
    Set the total number of steps, and then call step() that many times.
    The progress bar will progress from left to right.

    MODE_ACTIVITY is used when you don't know the number of steps that will be
    taken. Set up the total number of steps for the bar to get from one end of
    the bar to the other. Then, call step() as many times as you want. The bar
    will move from left to right until you stop calling step.
    """

    MODE_FRACTION = 0
    MODE_ACTIVITY = 1

    def __init__(self, title, header='', can_cancel=False,
                 cancel_callback=None, message_area=False):
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
            self.__cancel_button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
            self.__cancel_button.connect('clicked', self.__cancel_callback)
            self.__dialog.vbox.add(self.__cancel_button)

        self.message_area = None
        if message_area:
            area = Gtk.ScrolledWindow()
            text = Gtk.TextView()
            text.set_border_width(6)
            text.set_editable(False)
            self.message_area = text
            area.add_with_viewport(text)
            area.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.__dialog.vbox.add(area)
            self.message_area_ok = Gtk.Button(stock=Gtk.STOCK_OK)
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
            print "Progress:", text

    def set_message(self, text):
        """
        Sets the text of the message area.
        """
        if self.message_area:
            buffer = self.message_area.get_buffer()
            buffer.set_text(text)
        else:
            print "Progress:", text

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
        from gui.dialog import WarningDialog
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog."),
            self.__dialog)
        return True

    def close(self, widget=None):
        """
        Close the progress meter
        """
        self.__dialog.destroy()

#-------------------------------------------------------------------------
#
# SystemFonts class
#
#-------------------------------------------------------------------------

class SystemFonts(object):
    """
    Define fonts available to Gramps    

    This is a workaround for bug which prevents the list_families method
    being called more than once.

    The bug is described here: https://bugzilla.gnome.org/show_bug.cgi?id=679654

    This code generate a warning:
    /usr/local/lib/python2.7/site-packages/gi/types.py:47: 
    Warning: g_value_get_object: assertion `G_VALUE_HOLDS_OBJECT (value)' failed

    To get a list of fonts, instantiate this class and call get_system_fonts()
    #TODO GTK3: the underlying bug may be fixed at some point in the future
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
def open_file_with_default_application( file_path ):
    """
    Launch a program to open an arbitrary file. The file will be opened using
    whatever program is configured on the host as the default program for that
    type of file.

    @param file_path: The path to the file to be opened.
        Example: "c:\foo.txt"
    @type file_path: string
    @return: nothing
    """
    from gui.dialog import ErrorDialog
    norm_path = os.path.normpath( file_path )

    if not os.path.exists(norm_path):
        ErrorDialog(_("Error Opening File"), _("File does not exist"))
        return

    if win():
        try:
            os.startfile(norm_path)
        except WindowsError, msg:
            ErrorDialog(_("Error Opening File"), str(msg))
    else:
        if mac():
            utility = '/usr/bin/open'
        else:
            utility = 'xdg-open'
        search = os.environ['PATH'].split(':')
        for lpath in search:
            prog = os.path.join(lpath, utility)
            if os.path.isfile(prog):
                os.spawnvpe(os.P_NOWAIT, prog, [prog, norm_path], os.environ)
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
    Returns True if the event is a button-3 or equivalent
    """
    from gi.repository import Gdk

    if event.type == Gdk.EventType.BUTTON_PRESS:
        if is_quartz():
            if (event.button == 3
                or (event.button == 1 and event.get_state() & Gdk.ModifierType.CONTROL_MASK)):
                return True

        if event.button == 3:
            return True

def color_graph_box(alive=False, gender=gen.lib.Person.MALE):
    """
    Returns based on the config the color for graph boxes in hex
    If gender is None, an empty box is assumed
    Return type: tuple (hex color fill, hex color border)
    """
    if gender == gen.lib.Person.MALE:
        if alive:
            return (config.get('preferences.color-gender-male-alive'),
                    config.get('preferences.bordercolor-gender-male-alive'))
        else:
            return (config.get('preferences.color-gender-male-death'),
                    config.get('preferences.bordercolor-gender-male-death'))
    elif gender == gen.lib.Person.FEMALE:
        if alive:
            return (config.get('preferences.color-gender-female-alive'),
                    config.get('preferences.bordercolor-gender-female-alive'))
        else:
            return (config.get('preferences.color-gender-female-death'),
                    config.get('preferences.bordercolor-gender-female-death'))
    elif gender == gen.lib.Person.UNKNOWN:
        if alive:
            return (config.get('preferences.color-gender-unknown-alive'),
                    config.get('preferences.bordercolor-gender-unknown-alive'))
        else:
            return (config.get('preferences.color-gender-unknown-death'),
                    config.get('preferences.bordercolor-gender-unknown-death'))
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
    Convert a hexademical value #FF00FF to rgb. Returns tuple of float between
    0 and 1
    """
    value = value.lstrip('#')
    lenv = len(value)
    return tuple(int(value[i:i+lenv/3], 16)/256.0 for i in range(0, lenv, lenv/3))

def hex_to_rgb(value):
    """
    Convert a hexademical value #FF00FF to rgb. Returns tuple of integers
    """
    value = value.lstrip('#')
    lenv = len(value)
    return tuple(int(value[i:i+lenv/3], 16) for i in range(0, lenv, lenv/3))

def rgb_to_hex(rgb):
    """
    Convert a tuple of integer or float rgb values to its hex value
    """
    if type(rgb[0]) == int:
        return '#%02x%02x%02x' % rgb
    else:
        rgbint = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        return '#%02x%02x%02x' % rgbint

def color_to_hex(color):
    """Convert Gdk.Color to hex string."""
    hexstring = ""
    for col in 'red', 'green', 'blue':
        hexfrag = hex(getattr(color, col) / (16 * 16)).split("x")[1]
        if len(hexfrag) < 2:
            hexfrag = "0" + hexfrag
        hexstring += hexfrag
    return '#' + hexstring
    
def hex_to_color(hex):
    """Convert hex string to Gdk.Color."""
    from gi.repository import Gdk
    color = Gdk.color_parse(hex)
    return color
