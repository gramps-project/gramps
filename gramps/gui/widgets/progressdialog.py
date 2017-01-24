#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010 Brian G. Matherly
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
This module provides a progress dialog for displaying the status of
long running operations.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import time
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import logging
log = logging.getLogger("gen.progressdialog")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.callback import Callback

#-------------------------------------------------------------------------
#
# LongOpStatus
#
#-------------------------------------------------------------------------
class LongOpStatus(Callback):
    """
    LongOpStatus provides a way of communicating the status of a long
    running operations. The intended use is that when a long running operation
    is about to start it should create an instance of this class and emit
    it so that any listeners can pick it up and use it to record the status
    of the operation.


    **Signals**

    * op-heartbeat - emitted every 'interval' calls to heartbeat.
    * op-end       - emitted once when the operation completes.

    Example usage::

        class MyClass(Callback):

            __signals__ = {
           'op-start'   : object
            }

            def long(self):
                status = LongOpStatus("doing long job", 100, 10)

                for i in xrange(0,99):
                    time.sleep(0.1)
                    status.heartbeat()

                status.end()

        class MyListener:

             def __init__(self):
             self._op = MyClass()
             self._op.connect('op-start', self.start)
             self._current_op = None

             def start(self,long_op):
             self._current_op.connect('op-heartbeat', self.heartbeat)
             self._current_op.connect('op-end', self.stop)

             def hearbeat(self):
             # update status display

             def stop(self):
             # close the status display
                 self._current_op = None
    """

    __signals__ = {
    'op-heartbeat'   : None,
    'op-end'         : None
    }

    def __init__(self, msg="",
                 total_steps=None,
                 interval=1,
                 can_cancel=False):
        """
        :param msg: A Message to indicated the purpose of the operation.
        :type msg: string
        :param total_steps: The total number of steps that the operation
                            will perform.
        :type total_steps:
        :param interval: The number of iterations between emissions.
        :type interval:
        :param can_cancel: Set to True if the operation can be cancelled.
                           If this is set the operation that creates the status
                           object should check the 'should_cancel' method
                           regularly so that it can cancel the operation.
        :type can_cancel:
        """
        Callback.__init__(self)
        self._msg = msg
        self._total_steps = total_steps
        # don't allow intervals less that 1
        self._interval = max(interval, 1)
        self._can_cancel = can_cancel

        self._cancel = False
        self._count = 0
        self._countdown = interval
        self._secs_left = 0
        self._start = time.time()
        self._running = True

    def __del__(self):
        if self._running:
            self.emit('op-end')

    def heartbeat(self):
        """This should be called for each step in the operation. It will
        emit a 'op-heartbeat' every 'interval' steps. It recalcuates the
        'estimated_secs_to_complete' from the time taken for previous
        steps.
        """
        self._countdown -= 1
        if self._countdown <= 0:
            elapsed = time.time() - self._start
            self._secs_left = \
            ( elapsed / self._interval ) \
            * (self._total_steps - self._count)
            self._count += self._interval
            self._countdown = self._interval
            self._start = time.time()
            self.emit('op-heartbeat')

    def step(self):
        """
        Convenience function so LongOpStatus can be used as a ProgressBar
        if set up correctly
        """
        self.heartbeat()

    def estimated_secs_to_complete(self):
        """
        Return the number of seconds estimated left before operation
        completes. This will change as 'hearbeat' is called.

        :returns: estimated seconds to complete.
        :rtype: int
        """
        return self._secs_left

    def was_cancelled(self):
        """
        Has this process been cancelled?
        """
        return self._cancel

    def cancel(self):
        """
        Inform the operation that it should complete.
        """
        self._cancel = True
        self.end()

    def end(self):
        """
        End the operation. Causes the 'op-end' signal to be emitted.
        """
        self.emit('op-end')
        self._running = False

    def should_cancel(self):
        """
        Return true of the user has asked for the operation to be cancelled.

        :returns: True of the operation should be cancelled.
        :rtype: bool
        """
        return self._cancel

    def can_cancel(self):
        """
        :returns: True if the operation can be cancelled.
        :rtype: bool
        """
        return self._can_cancel

    def get_msg(self):
        """
        :returns: The current status description messages.
        :rtype: string
        """
        return self._msg

    def set_msg(self, msg):
        """
        Set the current description message.

        :param msg: The description message.
        :type msg: string
        """
        self._msg = msg

    def get_total_steps(self):
        """
        Get to total number of steps. NOTE: this is not the
        number of times that the 'op-heartbeat' message will be
        emited. 'op-heartbeat' is emited get_total_steps/interval
        times.

        :returns: total number of steps.
        :rtype: int
        """
        return self._total_steps

    def get_interval(self):
        """
        Get the interval between 'op-hearbeat' signals.

        :returns: the interval between 'op-hearbeat' signals.
        :rtype: int
        """
        return self._interval

#-------------------------------------------------------------------------
#
# _StatusObjectFacade
#
#-------------------------------------------------------------------------
class _StatusObjectFacade:
    """
    This provides a simple structure for recording the information
    needs about a status object.
    """

    def __init__(self, status_obj, heartbeat_cb_id=None, end_cb_id=None):
        """
        :param status_obj:
        :type status_obj: :class:`.LongOpStatus`
        :param heartbeat_cb_id: (default: None)
        :type heartbeat_cb_id: int
        :param end_cb_id: (default: None)
        :type end_cb_id: int
        """
        self.status_obj = status_obj
        self.heartbeat_cb_id = heartbeat_cb_id
        self.end_cb_id = end_cb_id
        self.pbar_idx = None
        self.active = False

#-------------------------------------------------------------------------
#
# ProgressMonitor
#
#-------------------------------------------------------------------------
class ProgressMonitor:
    """
    A dialog for displaying the status of long running operations.

    It will work with :class:`.LongOpStatus` objects to track the
    progress of long running operations. If the operations is going to
    take longer than *popup_time* it will pop up a dialog with a
    progress bar so that the user gets some feedback about what is
    happening.
    """

    __default_popup_time = 5 # seconds

    def __init__(self, dialog_class, dialog_class_params=(),
                 title=_("Progress Information"),
                 popup_time = None):
        """
        :param dialog_class: A class used to display the progress dialog.
        :type dialog_class: GtkProgressDialog or the same interface.
        :param dialog_class_params: A tuple that will be used as the initial
                                    arguments to the dialog_class, this might
                                    be used for passing in a parent window
                                    handle.
        :type dialog_class_params: tuple
        :param title: The title of the progress dialog
        :type title: string
        :param popup_time: number of seconds to wait before popup.
        :type popup_time: int
        """
        self._dialog_class = dialog_class
        self._dialog_class_params = dialog_class_params
        self._title = title
        self._popup_time = popup_time

        if self._popup_time is None:
            self._popup_time = self.__class__.__default_popup_time

        self._status_stack = [] # list of current status objects
        self._dlg = None

    def _get_dlg(self):
        if self._dlg is None:
            self._dlg = self._dialog_class(self._dialog_class_params,
                                           self._title)

        #self._dlg.show()

        return self._dlg

    def add_op(self, op_status):
        """
        Add a new status object to the progress dialog.

        :param op_status: the status object.
        :type op_status: :class:`.LongOpStatus`
        """

        log.debug("adding op to Progress Monitor")
        facade = _StatusObjectFacade(op_status)
        self._status_stack.append(facade)
        idx = len(self._status_stack)-1

        # wrap up the op_status object idx into the callback calls
        def heartbeat_cb():
            self._heartbeat(idx)
        def end_cb():
            self._end(idx)

        facade.heartbeat_cb_id = op_status.connect('op-heartbeat',
                                                   heartbeat_cb)
        facade.end_cb_id = op_status.connect('op-end', end_cb)

    def _heartbeat(self, idx):
        # check the estimated time to complete to see if we need
        # to pop up a progress dialog.

        log.debug("heartbeat in ProgressMonitor")

        if idx >= len(self._status_stack):
            # this item has been cancelled
            return

        facade = self._status_stack[idx]

        if facade.status_obj.estimated_secs_to_complete() > self._popup_time:
            facade.active = True

        if facade.active:
            dlg = self._get_dlg()

            if facade.pbar_idx is None:
                facade.pbar_idx = dlg.add(facade.status_obj)

            dlg.show()
            dlg.step(facade.pbar_idx)

    def _end(self, idx):
        # hide any progress dialog
        # remove the status object from the stack
        log.debug("received end in ProgressMonitor")

        if idx >= len(self._status_stack):
            # this item has been cancelled
            return

        while idx < len(self._status_stack) - 1:
            self._end(len(self._status_stack) - 1)

        facade = self._status_stack[idx]
        if facade.active:
            dlg = self._get_dlg()

            if len(self._status_stack) == 1:
                dlg.hide()

            dlg.remove(facade.pbar_idx)

        facade.status_obj.disconnect(facade.heartbeat_cb_id)
        facade.status_obj.disconnect(facade.end_cb_id)
        del self._status_stack[idx]
        if len(self._status_stack) == 0 and self._dlg:
            self._dlg.close()

#-------------------------------------------------------------------------
#
# _GtkProgressBar
#
#-------------------------------------------------------------------------
class _GtkProgressBar(Gtk.Box):
    """
    This widget displays the progress bar and labels for a progress
    indicator. It provides an interface to updating the progress bar.
    """

    def __init__(self, long_op_status):
        """
        :param long_op_status: the status of the operation.
        :type long_op_status: :class:`.LongOpStatus`
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        msg = long_op_status.get_msg()
        self._old_val = -1
        self._lbl = Gtk.Label(label=msg)
        self._lbl.set_use_markup(True)
        #self.set_border_width(24)

        self._pbar = Gtk.ProgressBar()
        self._hbox = Gtk.Box()

        # Only display the cancel button is the operation
        # can be canceled.
        if long_op_status.can_cancel():
            self._cancel = Gtk.Button.new_with_mnemonic(_('_Cancel'))
            self._cancel.connect("clicked",
                                 lambda x: long_op_status.cancel())
            self._cancel.show()
            self._hbox.pack_end(self._cancel, False, True, 0)

        self._hbox.pack_start(self._pbar, True, True, 0)

        self.pack_start(self._lbl, False, False, 0)
        self.pack_start(self._hbox, False, False, 0)


        self._pbar_max = (long_op_status.get_total_steps()/
                         long_op_status.get_interval())
        self._pbar_index = 0.0
        self._pbar.set_fraction(((100/float(long_op_status.get_total_steps())*
                                 float(long_op_status.get_interval())))/
                                 100.0)

        if msg != '':
            self._lbl.show()
        self._pbar.show()
        self._hbox.show()

    def step(self):
        """
        Move the progress bar on a step.
        """
        self._pbar_index = self._pbar_index + 1.0

        if self._pbar_index > self._pbar_max:
            self._pbar_index = self._pbar_max

        try:
            val = int(100*self._pbar_index/self._pbar_max)
        except ZeroDivisionError:
            val = 0

        if val != self._old_val:
            self._pbar.set_text("%d%%" % val)
            self._pbar.set_fraction(val/100.0)
            self._pbar.old_val = val

#-------------------------------------------------------------------------
#
# GtkProgressDialog
#
#-------------------------------------------------------------------------
class GtkProgressDialog(Gtk.Dialog):
    """
    A gtk window to display the status of a long running
    process.
    """

    def __init__(self, window_params, title):
        """
        :param title: The title to display on the top of the window.
        :type title: string
        """
        Gtk.Dialog.__init__(self)
        parent = None
        if len(window_params) >= 2:
            parent = window_params[1]   # we got an explicit parent
        else:                           # try to find an active window
            for win in Gtk.Window.list_toplevels():
                if win.is_active():
                    parent = win
                    break
        # if we still don't have a parent, give up
        if parent:
            self.set_transient_for(parent)
        if len(window_params) >= 3:
            flags = window_params[2]
            if Gtk.DialogFlags.MODAL & flags:
                self.set_modal(True)
            if Gtk.DialogFlags.DESTROY_WITH_PARENT & flags:
                self.set_destroy_with_parent(True)
        if len(window_params) >= 4:
            self.add_buttons(window_params[3:])
        self.connect('delete_event', self._warn)
        self.set_title(title)
        #self.set_resize_mode(Gtk.RESIZE_IMMEDIATE)
        #self.show()

        self._progress_bars = []

    def add(self, long_op_status):
        """
        Add a new status object to the progress dialog.

        :param long_op_status: the status object.
        :type long_op_status: :class:`.LongOpStatus`
        :returns: a key that can be used as the ``pbar_idx``  to the other
                  methods.
        :rtype: int
        """
        pbar = _GtkProgressBar(long_op_status)

        self.vbox.pack_start(pbar, False, False, 0)

        pbar.show()
        # this seems to cause an infinite loop:
        #self.resize_children()

        self._progress_bars.append(pbar)
        # This is a bad idea; could cause deletes while adding:
        #self._process_events()
        return len(self._progress_bars)-1

    def remove(self, pbar_idx):
        """
        Remove the specified status object from the progress dialog.

        :param pbar_idx: the index as returned from :meth:`add`
        :type pbar_idx: int
        """
        if pbar_idx is not None:
            pbar = self._progress_bars[pbar_idx]
            self.vbox.remove(pbar)
            del self._progress_bars[pbar_idx]

    def step(self, pbar_idx):
        """
        Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%.

        :param pbar_idx: the index as returned from :meth:`add`
        :type pbar_idx: int
        """
        if pbar_idx < len(self._progress_bars):
            self._progress_bars[pbar_idx].step()
        self._process_events()

    def _process_events(self):
        while Gtk.events_pending():
            Gtk.main_iteration()

    def show(self):
        """
        Show the dialog and process any events.
        """
        Gtk.Dialog.show(self)
        self._process_events()

    def hide(self):
        """
        Hide the dialog and process any events.
        """
        Gtk.Dialog.hide(self)
        self._process_events()

    def _warn(self, x, y):
        return True

    def close(self):
        self.destroy()


#-------------------------------------------------------------------------
#
# Gramps main status bar Progress indicator
#
#-------------------------------------------------------------------------
class StatusProgress:
    """
    A gtk progress in main Gramps window status bar to display the status
    of a long running process.
    """

    def __init__(self, window_params, title):
        """
        :param title: The title to display on the top of the window.
        :type title: string
        """
        # self.set_title(title)
        self.uistate = window_params[0]
        self.title = title
        self._old_val = -1
        self._progress_bars = False

    def add(self, long_op_status):
        """
        Add a new status object to the statusbar progress.

        :param long_op_status: the status object.
        :type long_op_status: :class:`.LongOpStatus`
        :returns: a key that can be used as the ``pbar_idx``  to the other
                  methods.
        :rtype: int
        """
        assert(not self._progress_bars)
        self._pbar = self.uistate.progress

        self._pbar_max = (long_op_status.get_total_steps() /
                          long_op_status.get_interval())
        self._pbar_index = 0.0
        self._pbar.set_fraction(
            ((100 / float(long_op_status.get_total_steps()) *
              float(long_op_status.get_interval()))) / 100.0)

        self.uistate.status.push(
            self.uistate.status_id, self.title)
        self._pbar.show()

        return True

    def remove(self, pbar_idx):
        """
        Remove the specified status object from the progress dialog.

        :param pbar_idx: the index as returned from :meth:`add` (not used)
        :type pbar_idx: int
        """
        self._progress_bars = False
        self._pbar.hide()

    def step(self, pbar_idx):
        """
        Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%.

        :param pbar_idx: the index as returned from :meth:`add` (not used)
        :type pbar_idx: int
        """

        self._pbar_index = self._pbar_index + 1.0

        if self._pbar_index > self._pbar_max:
            self._pbar_index = self._pbar_max

        try:
            val = int(100 * self._pbar_index / self._pbar_max)
        except ZeroDivisionError:
            val = 0

        if val != self._old_val:
            self._pbar.set_text("%d%%" % val)
            self._pbar.set_fraction(val / 100.0)
            self._pbar.old_val = val

        self._process_events()

    def _process_events(self):
        while Gtk.events_pending():
            Gtk.main_iteration()

    def show(self):
        """
        Show the dialog and process any events.
        """
        self._pbar.show()
        self._process_events()

    def hide(self):
        """
        Hide the dialog and process any events.
        """
        self._pbar.hide()
        self.uistate.status.pop(
            self.uistate.status_id)
        self._process_events()

    def _warn(self, x, y):
        return True

    def close(self):
        # self.destroy()
        pass

if __name__ == '__main__':

    def test(a, b):
        d = ProgressMonitor(GtkProgressDialog)

        s = LongOpStatus("Doing very long operation", 100, 10, can_cancel=True)

        d.add_op(s)

        for i in range(0, 99):
            if s.should_cancel():
                break
            time.sleep(0.1)
            if i == 30:
                t = LongOpStatus("doing a shorter one", 100, 10,
                                 can_cancel=True)
                d.add_op(t)
                for j in range(0, 99):
                    if s.should_cancel():
                        t.cancel()
                        break
                    if t.should_cancel():
                        break
                    time.sleep(0.1)
                    t.heartbeat()
                if not t.was_cancelled():
                    t.end()
            if i == 60:
                t = LongOpStatus("doing another shorter one", 100, 10)
                d.add_op(t)
                for j in range(0, 99):
                    if s.should_cancel():
                        t.cancel()
                        break
                    time.sleep(0.1)
                    t.heartbeat()
                t.end()
            s.heartbeat()
        if not s.was_cancelled():
            s.end()

    w = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    w.connect('destroy', Gtk.main_quit)
    button = Gtk.Button("Test")
    button.connect("clicked", test, None)
    w.add(button)
    button.show()
    w.show()
    Gtk.main()
    print('done')
