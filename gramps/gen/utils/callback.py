#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
**Introduction**

Gramps is divided into two parts. The database code, that does not
require any particular GUI libraries, and the gtk-based UI code
that requires gtk and gnome libraries. The gtk-based code can use
the gobject signal support to manage callback signals but the database
code can not.

The module provides a subset of the signal mechanisms that are available
from the gobject framework. It enables the database code to use signals
to communicate events to any callback methods in either the database code
or the UI code.
"""
import sys
import types
import traceback
import inspect
import copy

log = sys.stderr.write

# -------------------------------------------------------------------------
#
# Callback signal support for non-gtk parts of Gramps
#
# -------------------------------------------------------------------------


class Callback:
    """
    Callback and signal support objects.

    **Declaring signals**

    Classes that want to emit signals need to inherit from the
    DBCallback class and ensure that its :meth:`__init__` method
    is called. They then need to declare the signals that they
    can emit and the types of each callbacks arguments. For
    example::

        class TestSignals(Callback):

            __signals__ = {
                      'test-signal' : (int, ),
                      'test-noarg'  : None
                     }

            def __init__(self):
                Callback.__init__(self)

    The type signature is a tuple of types or classes. The type
    checking code uses the isinstance method to check that the
    argument passed to the emit call is an instance of the type
    in the signature declaration.

    If the signal does not have an argument use None as the
    signature.

    The signals will be inherited by any subclasses. Duplicate
    signal names in subclasses are not alowed.


    **Emitting signals**

    Signals are emitted using the emit method. e.g.::

            def emit_signal(self):
                self.emit('test-signal', (1, ))

    The parameters are passed as a tuple so a single parameter
    must be passed as a 1 element tuple.

    **Connecting callbacks to signals**

    Attaching a callback to the signals is similar to the gtk
    connect methods. e.g.::

        # connect to a function.
        def fn(i):
            print 'got signal value = ', i

        t = TestSignals()
        t.connect('test-signal', fn)

        # connect to a bound method
        class C:

            def cb_func(self, i):
                print 'got class signal = ', 1

        r = R()
        t.connect('test-signal', r.cb_func)


    **Disconnecting callbacks**

    If you want to disconnect a callback from a signals you must remember the
    key returned from the connect call. This key can be passed to the disconnect
    method to remove the callback from the signals callback list.

    e.g.::

        t = TestSignals()

        # connect to a bound method
        class C:

            def cb_func(self, i):
                print 'got class signal = ', 1

        r = R()
        key = t.connect('test-signal', r.cb_func)

        ...

        t.disconnect(key)


    **Stopping and starting signals**

    Signals can be blocked on a per instance bassis or they can be blocked
    for all instances of the Callback class. :meth:`disable_signals` can
    be used to block the signals for a single instance and
    :meth:`disable_all_signals` can be used to block signals for the class:

    e.g.::


           class TestSignals(Callback):

            __signals__ = {
                      'test-signal' : (int, ),
                      'test-noarg'  : None
                     }

            def __init__(self):
                Callback.__init__(self)

            def emit_signal(self):
                self.emit('test-signal', (1, ))

            t = TestSignals()

            # block signals from instance t
            t.disable_signals()

            ...

            # unblock
            t.enable_signals()

            # block all signals
            Callback.disable_all_signals()

            ...

            # unblock all signals
            Callback.enable_all_signals()


    Any signals emitted whilst signals are blocked will be lost.


    **Debugging signal callbacks**


    To help with debugging the signals and callbacks you can turn on
    lots of logging information. To switch on logging for a single
    instance call :meth:`enable_logging`, to switch it off again call
    :meth:`disable_logging`. To switch on logging for all instance
    you can toggle Callback.__LOG_ALL to True.

    """

    # If this True no signals will be emitted from any instance of
    # any class derived from this class. This should be toggled using
    # the class methods, dissable_all_signals() and enable_all_signals().
    __BLOCK_ALL_SIGNALS = False
    __LOG_ALL = False

    def __init__(self):
        self.__enable_logging = False  # controls whether lots of debug
        # information will be produced.
        self.__block_instance_signals = False  # controls the blocking of
        # signals from this instance
        self.__callback_map = {}  # dictionary containing all the connected
        # callback functions. The keys are the
        # signal names and the values are tuples
        # of the form (key, bound_method), where
        # the key is unique within the instance
        # and the bound_method is the callback
        # that will be called when the signal is
        # emitted
        self.__signal_map = {}  # dictionary contains all the signals that
        # this instance can emit. The keys are the
        # signal names and the values are tuples
        # containing the list of types of the arguments
        # that the callback methods must accept.
        self._current_key = 0  # counter to give a unique key to each callback
        self._current_signals = []  # list of all the signals that are currently
        # being emitted by this instance. This is
        # used to prevent recursive emittion of the
        # same signal.

        # To speed up the signal type checking the signals declared by
        # each of the classes in the inheritance tree of this instance
        # are consolidated into a single dictionary.
        # The signals can't change so we only need to do this once.

        def trav(cls):
            """A traversal function to walk through all the classes in
            the inheritance tree. The return is a list of all the
            __signals__ dictionaries."""
            if "__signals__" in cls.__dict__:
                signal_list = [cls.__signals__]
            else:
                signal_list = []

            for base_cls in cls.__bases__:
                base_list = trav(base_cls)
                if len(base_list) > 0:
                    signal_list = signal_list + base_list

            return signal_list

        # Build a signal dict from the list of signal dicts
        for s in trav(self.__class__):
            for k, v in s.items():
                if k in self.__signal_map:
                    # signal name clash
                    sys.stderr.write("Warning: signal name clash: %s\n" % str(k))
                self.__signal_map[k] = v
        # Set to None to prevent a memory leak in this recursive function
        trav = None

        # self.__signal_map now contains the connonical list
        # of signals that this instance can emit.

        self._log(
            "registered signals: \n   %s\n"
            % "\n   ".join(
                ["%s: %s" % (k, v) for (k, v) in list(self.__signal_map.items())]
            )
        )

    def connect(self, signal_name, callback):
        """
        Connect a callable to a signal_name. The callable will be called
        with the signal is emitted. The callable must accept the argument
        types declared in the signals signature.

        returns a unique key that can be passed to :meth:`disconnect`.
        """
        # Check that signal exists.
        if signal_name not in self.__signal_map:
            self._log(
                "Warning: attempt to connect to unknown signal: %s\n" % str(signal_name)
            )
            return

        # Add callable to callback_map
        if signal_name not in self.__callback_map:
            self.__callback_map[signal_name] = []

        self._current_key += 1
        self._log(
            "Connecting callback to signal: "
            "%s with key: %s\n" % (signal_name, str(self._current_key))
        )
        self.__callback_map[signal_name].append((self._current_key, callback))

        return self._current_key

    def disconnect(self, key):
        """
        Disconnect a callback.
        """

        # Find the key in the callback map.
        for signal_name in self.__callback_map:
            for cb in self.__callback_map[signal_name]:
                (skey, fn) = cb
                if skey == key:
                    # delete the callback from the map.
                    self._log(
                        "Disconnecting callback from signal"
                        ": %s with key: %s\n" % (signal_name, str(key))
                    )
                    self.__callback_map[signal_name].remove(cb)

    def disconnect_all(self):  # Find the key in the callback map.
        for signal_name in self.__callback_map:
            keymap = copy.copy(self.__callback_map[signal_name])
            for key in keymap:
                self.__callback_map[signal_name].remove(key)
            self.__callback_map[signal_name] = None
        self.__callback_map = {}

    def emit(self, signal_name, args=tuple()):
        """
        Emit the signal called signal_name. The args must be a tuple of
        arguments that match the types declared for the signals signature.
        """
        # Check that signals are not blocked
        if self.__BLOCK_ALL_SIGNALS or self.__block_instance_signals:
            return

        # Check signal exists
        frame = inspect.currentframe()
        c_frame = frame.f_back
        c_code = c_frame.f_code
        frame_info = (c_code.co_filename, c_frame.f_lineno, c_code.co_name)
        if signal_name not in self.__signal_map:
            self._warn(
                "Attempt to emit to unknown signal: %s\n"
                "         from: file: %s\n"
                "               line: %d\n"
                "               func: %s\n" % ((str(signal_name),) + frame_info)
            )
            return

        # check that the signal is not already being emitted. This prevents
        # against recursive signal emissions.
        if signal_name in self._current_signals:
            self._warn(
                "Signal recursion blocked. "
                "Signals was : %s\n"
                "        from: file: %s\n"
                "              line: %d\n"
                "              func: %s\n" % ((str(signal_name),) + frame_info)
            )
            return

        try:
            self._current_signals.append(signal_name)

            # check that args is a tuple. This is a common programming error.
            if not (isinstance(args, tuple) or args is None):
                self._warn(
                    "Signal emitted with argument that is not a tuple.\n"
                    "  emit() takes two arguments, the signal name and a \n"
                    "  tuple that contains the arguments that are to be \n"
                    "  passed to the callbacks. If you are passing a signal \n"
                    "  argument it must be done as a single element tuple \n"
                    "  e.g. emit('my-signal', (1, )) \n"
                    "         signal was: %s\n"
                    "         from: file: %s\n"
                    "               line: %d\n"
                    "               func: %s\n" % ((str(signal_name),) + frame_info)
                )
                return

            # type check arguments
            arg_types = self.__signal_map[signal_name]
            if arg_types is None and len(args) > 0:
                self._warn(
                    "Signal emitted with "
                    "wrong number of args: %s\n"
                    "         from: file: %s\n"
                    "               line: %d\n"
                    "               func: %s\n" % ((str(signal_name),) + frame_info)
                )
                return

            if len(args) > 0:
                if len(args) != len(arg_types):
                    self._warn(
                        "Signal emitted with "
                        "wrong number of args: %s\n"
                        "         from: file: %s\n"
                        "               line: %d\n"
                        "               func: %s\n" % ((str(signal_name),) + frame_info)
                    )
                    return

                if arg_types is not None:
                    for i in range(0, len(arg_types)):
                        if not isinstance(args[i], arg_types[i]):
                            self._warn(
                                "Signal emitted with "
                                "wrong arg types: %s\n"
                                "         from: file: %s\n"
                                "               line: %d\n"
                                "               func: %s\n"
                                "    arg passed was: %s, type of arg passed %s,  type should be: %s\n"
                                % (
                                    (str(signal_name),)
                                    + frame_info
                                    + (args[i], repr(type(args[i])), repr(arg_types[i]))
                                )
                            )
                            return
            if signal_name in self.__callback_map:
                self._log("emitting signal: %s\n" % (signal_name,))
                # Don't bother if there are no callbacks.
                for key, fn in self.__callback_map[signal_name]:
                    self._log("Calling callback with key: %s\n" % (key,))
                    try:
                        if isinstance(fn, types.FunctionType) or isinstance(
                            fn, types.MethodType
                        ):  # call func
                            fn(*args)
                        else:
                            self._warn("Badly formed entry in callback map.\n")
                    except:
                        self._warn(
                            "Exception occurred in callback function.\n"
                            "%s"
                            % ("".join(traceback.format_exception(*sys.exc_info())),)
                        )
        finally:
            self._current_signals.remove(signal_name)

        del frame  # Needed for garbage collection

    #
    # instance signals control methods
    #
    def disable_signals(self):
        self.__block_instance_signals = True

    def enable_signals(self):
        self.__block_instance_signals = False

    # logging methods

    def disable_logging(self):
        self.__enable_logging = False

    def enable_logging(self):
        self.__enable_logging = True

    def _log(self, msg):
        if self.__LOG_ALL or self.__enable_logging:
            log("%s: %s" % (self.__class__.__name__, str(msg)))

    def _warn(self, msg):
        log("Warning: %s: %s" % (self.__class__.__name__, str(msg)))

    #
    # Class methods
    #

    @classmethod
    def log_all(cls, enable):
        cls.__LOG_ALL = enable

    @classmethod
    def disable_all_signals(cls):
        cls.__BLOCK_ALL_SIGNALS = True

    @classmethod
    def enable_all_signals(cls):
        cls.__BLOCK_ALL_SIGNALS = False
