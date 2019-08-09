#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2010  Jakim Friant
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import types
import logging
LOG = logging.getLogger(".Gramplets")

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from ...gui.dbguielement import DbGUIElement
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


class Gramplet:
    """
    Base class for non-graphical gramplet code.
    """
    def __init__(self, gui, nav_group=0):
        """
        Internal constructor for non-graphical gramplets.
        """
        self._idle_id = 0
        self.track = []
        self.active = False
        self.dirty = True
        self.has_data = True
        self._pause = False
        self._generator = None
        self._need_to_update = False
        self.option_dict = {}
        self._signal = {}
        self.option_order = []
        # links to each other:
        self.gui = gui   # plugin gramplet has link to gui
        gui.pui = self   # gui has link to plugin ui
        self.nav_group = nav_group
        self.dbstate = gui.dbstate
        self.uistate = gui.uistate
        self.init()
        self.on_load()
        self.build_options()
        self.dbstate.connect("database-changed", self._db_changed)
        self.dbstate.connect("no-database", self._no_db)
        self.gui.textview.connect("button-press-event",
                                  self.gui.on_button_press)
        self.gui.textview.connect("motion-notify-event",
                                  self.gui.on_motion)
        self._db_changed(self.dbstate.db)
        active_person = self.get_active('Person')
        if active_person: # already changed
            self._active_changed(active_person)
        self.post_init()

    def connect_signal(self, nav_type, method):
        """
        Connect the given method to the active-changed signal for the
        navigation type requested.
        """
        self.uistate.register(self.dbstate, nav_type, self.nav_group)
        history = self.uistate.get_history(nav_type, self.nav_group)
        # print('History: nave-type = %s' % nav_type)
        self.connect(history, "active-changed", method)

    def init(self): # once, constructor
        """
        External constructor for developers to put their initialization
        code. Designed to be overridden.
        """
        pass

    def post_init(self):
        pass

    def build_options(self):
        """
        External constructor for developers to put code for building
        options.
        """
        pass

    def main(self): # return false finishes
        """
        The main place for the gramplet's code. This is a generator.
        Generator which will be run in the background, through :meth:`update`.
        """
        yield False

    def on_load(self):
        """
        Gramplets should override this to take care of loading previously
        their special data.
        """
        pass

    def on_save(self):
        """
        Gramplets should override this to take care of saving their
        special data.
        """
        return

    def get_active(self, nav_type):
        """
        Return the handle of the active object for the given navigation type.
        """
        return self.uistate.get_active(nav_type, self.nav_group)

    def get_active_object(self, nav_type):
        """
        Return the object of the active handle for the given navigation type.
        """
        handle = self.uistate.get_active(nav_type, self.nav_group)
        handle_func = getattr(self.dbstate.db,
                             'get_%s_from_handle' % nav_type.lower())
        if handle:
            return handle_func(handle)
        return None

    def set_active(self, nav_type, handle):
        """
        Change the handle of the active object for the given navigation type.
        """
        self.uistate.set_active(handle, nav_type, self.nav_group)

    def active_changed(self, handle):
        """
        Developers should put their code that occurs when the active
        person is changed.
        """
        pass

    def _active_changed(self, handle):
        """
        Private code that updates the GUI when active_person is changed.
        """
        self.active_changed(handle)

    def db_changed(self):
        """
        Method executed when the database is changed.
        """
        pass

    def link(self, text, link_type, data, size=None, tooltip=None):
        """
        Creates a clickable link in the textview area.
        """
        self.gui.link(text, link_type, data, size, tooltip)

    # Shortcuts to the gui functionality:

    def set_tooltip(self, tip):
        """
        Sets the tooltip for this gramplet.
        """
        self.gui.set_tooltip(tip)

    def get_text(self):
        """
        Returns the current text of the textview.
        """
        return self.gui.get_text()

    def insert_text(self, text):
        """
        Insert the given text in the textview at the cursor.
        """
        self.gui.insert_text(text)

    def render_text(self, text):
        """
        Render the given text, given that :meth:`set_use_markup` is on.
        """
        self.gui.render_text(text)

    def clear_text(self):
        """
        Clear all of the text from the textview.
        """
        self.gui.clear_text()

    def set_text(self, text, scroll_to='start'):
        """
        Clear and set the text to the given text. Additionally, move the
        cursor to the position given. Positions are:

            ========  =======================================
            Position  Description
            ========  =======================================
            'start'   start of textview
            'end'     end of textview
            'begin'   begin of line, before setting the text.
            ========  =======================================
        """
        self.gui.set_text(text, scroll_to)

    def append_text(self, text, scroll_to="end"):
        """
        Append the text to the textview. Additionally, move the
        cursor to the position given. Positions are:

            ========  =======================================
            Position  Description
            ========  =======================================
            'start'   start of textview
            'end'     end of textview
            'begin'   begin of line, before setting the text.
            ========  =======================================
        """
        self.gui.append_text(text, scroll_to)

    def set_use_markup(self, value):
        """
        Allows the use of render_text to show markup.
        """
        self.gui.set_use_markup(value)

    def set_wrap(self, value):
        """
        Set the textview to wrap or not.
        """
        textview = self.gui.textview
        from gi.repository import Gtk
        # Gtk.WrapMode.NONE, Gtk.WrapMode.CHAR, Gtk.WrapMode.WORD or Gtk.WrapMode.WORD_CHAR.
        if value in [True, 1]:
            textview.set_wrap_mode(Gtk.WrapMode.WORD)
        elif value in [False, 0, None]:
            textview.set_wrap_mode(Gtk.WrapMode.NONE)
        elif value in ["char"]:
            textview.set_wrap_mode(Gtk.WrapMode.CHAR)
        elif value in ["word char"]:
            textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        else:
            raise ValueError(
                    "Unknown wrap mode: '%s': use 0,1,'char' or 'word char')"
                        % value)

    def no_wrap(self):
        """
        The view in gramplet should not wrap.
        DEPRICATED: use :meth:`set_wrap` instead.
        """
        self.set_wrap(False)

    # Other functions of the gramplet:

    def load_data_to_text(self, pos=0):
        """
        Load information from the data portion of the saved
        Gramplet to the textview.
        """
        if len(self.gui.data) >= pos + 1:
            text = self.gui.data[pos]
            text = text.replace("\\n", chr(10))
            self.set_text(text, 'end')

    def save_text_to_data(self):
        """
        Save the textview to the data portion of a saved gramplet.
        """
        text = self.get_text()
        text = text.replace(chr(10), "\\n")
        self.gui.data.append(text)

    def update(self, *args):
        """
        The main interface for running the :meth:`main` method.
        """
        from gi.repository import GLib
        if ((not self.active) and
            not self.gui.force_update):
            self.dirty = True
            if self.dbstate.is_open():
                #print "  %s is not active" % self.gui.gname
                self.update_has_data()
            else:
                self.set_has_data(False)
            return
        #print "     %s is UPDATING" % self.gui.gname
        self.dirty = False
        LOG.debug("gramplet updater: %s: running" % self.gui.title)
        if self._idle_id != 0:
            self.interrupt()
        self._generator = self.main()
        self._pause = False
        self._idle_id = GLib.idle_add(self._updater,
                                      priority=GLib.PRIORITY_LOW - 10)

    def _updater(self):
        """
        Runs the generator.
        """
        LOG.debug("gramplet updater: %s" % self.gui.title)
        if not isinstance(self._generator, types.GeneratorType):
            self._idle_id = 0
            LOG.debug("gramplet updater: %s : One time, done!" % self.gui.title)
            return False
        try:
            retval = next(self._generator)
            if not retval:
                self._idle_id = 0
            if self._pause:
                LOG.debug("gramplet updater: %s: return False" % self.gui.title)
                return False
            LOG.debug("gramplet updater: %s: return %s" %
                      (self.gui.title, retval))
            return retval
        except StopIteration:
            self._idle_id = 0
            self._generator.close()
            LOG.debug("gramplet updater: %s: Done!"  % self.gui.title)
            return False
        except Exception as e:
            import traceback
            LOG.warning("Gramplet gave an error: %s" % self.gui.title)
            traceback.print_exc()
            print("Continuing after gramplet error...")
            self._idle_id = 0
            self.uistate.push_message(self.dbstate,
                _("Gramplet %s caused an error") % self.gui.title)
            return False

    def pause(self, *args):
        """
        Pause the :meth:`main` method.
        """
        self._pause = True

    def resume(self, *args):
        """
        Resume the :meth:`main` method that has previously paused.
        """
        from gi.repository import GLib
        self._pause = False
        self._idle_id = GLib.idle_add(self._updater,
                                      priority=GLib.PRIORITY_LOW - 10)

    def update_all(self, *args):
        """
        Force the main loop to run right now (as opposed to running in
        background).
        """
        self._generator = self.main()
        if isinstance(self._generator, types.GeneratorType):
            for step in self._generator:
                pass

    def interrupt(self, *args):
        """
        Force the generator to stop running.
        """
        from gi.repository import GLib
        self._pause = True
        if self._idle_id != 0:
            GLib.source_remove(self._idle_id)
            self._idle_id = 0

    def _db_changed(self, db):
        """
        Internal method for handling items that should happen when the
        database changes. This will push a message to the GUI status bar.
        """
        if self.dbstate.db.is_open():
            self.disconnect_all()  # clear the old signals from old db
        self.dbstate.db = db
        self.gui.dbstate.db = db
        if db.is_open():
            # the following prevents connecting to every Gramplet, and still
            # allows Person Gramplets to be informed of active-changed
            # Some Gramplets .gpr files don't have navtypes set, thus the
            # hasattr
            if hasattr(self.gui, 'navtypes') and 'Person' in self.gui.navtypes:
                self.connect_signal('Person', self._active_changed)
            self.db_changed()
        # Some Gramplets use DbGUIElement; and DbGUIElement needs to know if
        # db is changed.  However, at initialization, DbGUIElement is not yet
        # initialized when _db_changed is called, thus the test for callman
        if hasattr(self, "callman") and isinstance(self, DbGUIElement):
            # get DbGUIElement informed if in use
            self._change_db(db)       # DbGUIElement method

        self.update()

    def _no_db(self):
        self.disconnect_all()  # clear the old signals

    def get_option_widget(self, label):
        """
        Retrieve an option's widget by its label text.
        """
        return self.option_dict[label][0]

    def get_option(self, label):
        """
        Retireve an option by its label text.
        """
        return self.option_dict[label][1]

    def add_option(self, option):
        """
        Add an option to the GUI gramplet.
        """
        widget, label = self.gui.add_gui_option(option)
        self.option_dict.update({option.get_label(): [widget, option]})
        self.option_order.append(option.get_label())

    def save_update_options(self, obj):
        """
        Save a gramplet's options to file.
        """
        self.save_options()
        self.update()

    def save_options(self):
        pass

    def connect(self, signal_obj, signal, method):
        id = signal_obj.connect(signal, method)
        signal_list = self._signal.get(signal, [])
        signal_list.append((id, signal_obj))
        self._signal[signal] = signal_list

    def disconnect(self, signal):
        if signal in self._signal:
            for (id, signal_obj) in self._signal[signal]:
                signal_obj.disconnect(id)
            self._signal[signal] = []
        else:
            raise AttributeError("unknown signal: '%s'" % signal)

    def disconnect_all(self):
        """
        Used to disconnect all the signals for this specific gramplet
        """
        for signal in self._signal:
            for (sig_id, signal_obj) in self._signal[signal]:
                signal_obj.disconnect(sig_id)
            self._signal[signal] = []

    def hidden_widgets(self):
        """
        A list of widgets to keep hidden. Needed because Gramps uses
        show_all() in some places.
        """
        return []

    def set_has_data(self, value):
        """
        Set the status as to whether this gramplet has data.
        """
        if value != self.has_data:
            self.has_data = value
            self.gui.set_has_data(value)

    def update_has_data(self):
        """
        By default, assume that the gramplet has data.
        """
        self.set_has_data(True)
