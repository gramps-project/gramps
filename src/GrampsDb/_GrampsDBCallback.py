#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
    Introduction
    ============
    
    Gramps is devided into two parts. The database code, that does not
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
import os
import types
import traceback
import inspect
from gettext import gettext as _

from bsddb import db

log = sys.stderr.write

#-------------------------------------------------------------------------
#
# Callback signal support for non-gtk parts of Gramps
#
#-------------------------------------------------------------------------

class GrampsDBCallback(object):
    """
    Callback and signal support for non-gtk parts of gramps.

    Declaring signals
    =================
    
    Classes that want to emit signals need to inherit from the
    GrampsDBCallback class and ensure that its __init__ method
    is called. They then need to declare the signals that they
    can emit and the types of each callbacks arguments. For
    example::

        class TestSignals(GrampsDBCallback):

            __signals__ = {
                      'test-signal' : (int,),
                      'test-noarg'  : None
                     }

            def __init__(self):
                GrampsDBCallback.__init__(self)

    The type signature is a tuple of types or classes. The type
    checking code uses the isinstance method to check that the
    argument passed to the emit call is an instance of the type
    in the signature declaration.

    If the signal does not have an argument use None as the
    signature.

    The signals will be inherited by any subclasses. Duplicate
    signal names in subclasses are not alowed.


    Emitting signals
    ================

    Signals are emitted using the emit method. e.g.::

            def emit_signal(self):
                self.emit('test-signal',(1,))

    The parameters are passed as a tuple so a single parameter
    must be passed as a 1 element tuple.
    
    Connecting callbacks to signals
    ===============================
    
    Attaching a callback to the signals is similar to the gtk
    connect methods. e.g.::

        # connect to a function.
        def fn(i):
            print 'got signal value = ', i

        t = TestSignals()
        t.connect('test-signal', fn)

        # connect to a bound method
        class C(object):

            def cb_func(self, i):
                print 'got class signal = ', 1

        r = R()
        t.connect('test-signal', r.cb_func)
        

    Disconnecting callbacks
    =======================

    If you want to disconnect a callback from a signals you must remember the
    key returned from the connect call. This key can be passed to the disconnect
    method to remove the callback from the signals callback list.

    e.g.::

        t = TestSignals()

        # connect to a bound method
        class C(object):

            def cb_func(self, i):
                print 'got class signal = ', 1

        r = R()
        key = t.connect('test-signal', r.cb_func)

        ...

        t.disconnect(key)

    
    Stopping and starting signals
    =============================

    Signals can be blocked on a per instance bassis or they can be blocked
    for all instances of the GrampsDBCallback class. disable_signals() can
    be used to block the signals for a single instance and disable_all_signals()
    can be used to block signals for the class:

    e.g.::


           class TestSignals(GrampsDBCallback):

            __signals__ = {
                      'test-signal' : (int,),
                      'test-noarg'  : None
                     }

            def __init__(self):
                GrampsDBCallback.__init__(self)

            def emit_signal(self):
                self.emit('test-signal',(1,))

            t = TestSignals()

            # block signals from instance t
            t.disable_signals()

            ...
            
            # unblock
            t.enable_signals()

            # block all signals
            GrampsDBCallback.disable_all_signals()

            ...
            
            # unblock all signals
            GrampsDBCallback.enable_all_signals()


    Any signals emited whilst signals are blocked will be lost. 
            
            
    Debugging signal callbacks
    ==========================


    To help with debugging the signals and callbacks you can turn on
    lots of logging information. To switch on logging for a single
    instance call self.enable_logging(), to switch it off again call
    self.disable_logging(). To switch on logging for all instance
    you can toggle GrampsDBCallback.__LOG_ALL to True.
    
    """

    # If this True no signals will be emitted from any instance of
    # any class derived from this class. This should be toggled using
    # the class methods, dissable_all_signals() and enable_all_signals().
    __BLOCK_ALL_SIGNALS = False


    # If this is True logging will be turned on for all instances
    # whether or not instance based logging is enabled.
    try:
        __LOG_ALL = int(os.environ.get('GRAMPS_SIGNAL',"0")) == 1
    except:
        __LOG_ALL = False
    
    def __init__(self):
        self.__enable_logging = False # controls whether lots of debug
                                      # information will be produced.
        self.__block_instance_signals = False # controls the blocking of
                                              # signals from this instance
        self.__callback_map = {} # dictionary containing all the connected
                                 # callback functions. The keys are the
                                 # signal names and the values are tuples
                                 # of the form (key,bound_method), where
                                 # the key is unique within the instance
                                 # and the bound_method is the callback
                                 # that will be called when the signal is
                                 # emitted
        self.__signal_map = {}   # dictionary contains all the signals that
                                 # this instance can emit. The keys are the
                                 # signal names and the values are tuples
                                 # containing the list of types of the arguments
                                 # that the callback methods must accept.
        self._current_key = 0    # counter to give a unique key to each callback.
        self._current_signals = [] # list of all the signals that are currently
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
            if cls.__dict__.has_key('__signals__'):
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
            for (k,v) in s.items():
                if self.__signal_map.has_key(k):
                    # signal name clash
                    sys.err.write("Warning: signal name clash: %s\n" % str(k))
                self.__signal_map[k] = v

        # self.__signal_map now contains the connonical list
        # of signals that this instance can emit.

        self._log("registed signals: \n   %s\n" %
                  "\n   ".join([ "%s: %s" % (k,v) for (k,v)
                                 in self.__signal_map.items() ]))
        

    def connect(self, signal_name, callback):
        """
        Connect a callable to a signal_name. The callable will be called
        with the signal is emitted. The callable must accept the argument
        types declared in the signals signature.

        returns a unique key that can be passed to disconnect().
        """
        # Check that signal exists.
        if signal_name not in self.__signal_map.keys():
            self._log("Warning: attempt to connect to unknown signal: %s\n" % str(signal_name))
            return
        
        # Add callable to callback_map
        if signal_name not in self.__callback_map.keys():
            self.__callback_map[signal_name] = []

        self._current_key += 1
        self._log("Connecting callback to signal: "
                  "%s with key: %s\n"
                  % (signal_name,str(self._current_key)))
        self.__callback_map[signal_name].append((self._current_key,callback))

        return self._current_key

    def disconnect(self,key):
        """
        Disconnect a callback.
        """
        
        # Find the key in the callback map.
        for signal_name in self.__callback_map.keys():
            for cb in self.__callback_map[signal_name]:
                (skey,fn) = cb
                if skey == key:
                    # delete the callback from the map.
                    self._log("Disconnecting callback from signal"
                              ": %s with key: %s\n" % (signal_name,
                                                       str(key)))
                    self.__callback_map[signal_name].remove(cb)
                    
                    
    def emit(self, signal_name, args=tuple()):
        """
        Emit the signal called signal_name. The args must be a tuple of
        arguments that match the types declared for the signals signature.
        """
        # Check that signals are not blocked
        if GrampsDBCallback.__BLOCK_ALL_SIGNALS or \
               self.__block_instance_signals:
            return
        
        # Check signal exists
        if signal_name not in self.__signal_map.keys():
            self._warn("Attempt to emit to unknown signal: %s\n"
                       "         from: file: %s\n"
                       "               line: %d\n"
                       "               func: %s\n"
                       % ((str(signal_name),) + inspect.stack()[1][1:4]))
            return

        # check that the signal is not already being emitted. This prevents
        # against recursive signal emmissions.
        if signal_name in self._current_signals:
            self._warn("Signal recursion blocked. "
                       "Signals was : %s\n"
                       "        from: file: %s\n"
                       "              line: %d\n"
                       "              func: %s\n"
                       % ((str(signal_name),) + inspect.stack()[1][1:4]))
            return 

        try:
            self._current_signals.append(signal_name)

            # check that args is a tuple. This is a common programming error.
            if not (isinstance(args,tuple) or args == None):
                self._warn("Signal emitted with argument that is not a tuple.\n"
                           "  emit() takes two arguments, the signal name and a \n"
                           "  tuple that contains the arguments that are to be \n"
                           "  passed to the callbacks. If you are passing a signal \n"
                           "  argument it must be done as a single element tuple \n"
                           "  e.g. emit('my-signal',(1,)) \n"
                           "         signal was: %s\n"
                           "         from: file: %s\n"
                           "               line: %d\n"
                           "               func: %s\n"
                           % ((str(signal_name),) + inspect.stack()[1][1:4]))
                return

            # type check arguments
            arg_types = self.__signal_map[signal_name]
            if arg_types == None and len(args) > 0:
                self._warn("Signal emitted with "
                           "wrong number of args: %s\n"
                           "         from: file: %s\n"
                           "               line: %d\n"
                           "               func: %s\n"
                           % ((str(signal_name),) + inspect.stack()[1][1:4]))
                return

            if len(args) > 0:
                if len(args) != len(arg_types):
                    self._warn("Signal emitted with "
                               "wrong number of args: %s\n"
                               "         from: file: %s\n"
                               "               line: %d\n"
                               "               func: %s\n"
                               % ((str(signal_name),) + inspect.stack()[1][1:4]))
                    return

                if arg_types != None:
                    for i in range(0,len(arg_types)):
                        if not isinstance(args[i],arg_types[i]):
                            self._warn("Signal emitted with "
                                       "wrong arg types: %s\n"
                                       "         from: file: %s\n"
                                       "               line: %d\n"
                                       "               func: %s\n"
                                       "    arg passed was: %s, type of arg passed %s,  type should be: %s\n"
                                       % ((str(signal_name),) + inspect.stack()[1][1:4] +\
                                          (args[i],repr(type(args[i])),repr(arg_types[i]))))                   
                            return 

            if signal_name in self.__callback_map.keys():
                self._log("emmitting signal: %s\n" % (signal_name,))
                # Don't bother if there are no callbacks.
                for (key,fn) in self.__callback_map[signal_name]:
                    self._log("Calling callback with key: %s\n" % (key,))
                    try:
                        if type(fn) == tuple: # call class method
                            cb[0](fn[1],*args)
                        elif type(fn) == types.FunctionType or \
                                 type(fn) == types.MethodType: # call func
                            try:
                                fn(*args)
                            except db.DBRunRecoveryError:
                                display_error()
                        else:
                            self._warn("Badly formed entry in callback map.\n")
                    except:
                        self._warn("Exception occured in callback function.\n"
                                   "%s" % ("".join(traceback.format_exception(*sys.exc_info())),))
        finally:
            self._current_signals.remove(signal_name)

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

    def _log(self,msg):
        if GrampsDBCallback.__LOG_ALL or self.__enable_logging:
            log("%s: %s" % (self.__class__.__name__, str(msg)))

    def _warn(self,msg):
        log("Warning: %s: %s" % (self.__class__.__name__, str(msg)))

    #
    # Class methods
    #

    def __disable_all_signals(cls):
        GrampsDBCallback.__BLOCK_ALL_SIGNALS = True

    disable_all_signals = classmethod(__disable_all_signals)
    
    def __enable_all_signals(cls):
        GrampsDBCallback.__BLOCK_ALL_SIGNALS = False

    enable_all_signals = classmethod(__enable_all_signals)


def display_error():
    from QuestionDialog import ErrorDialog
    ErrorDialog(
        _('Database error'),
        _('A problem as been detected in your database. '
          'This is probably caused by opening a database that was '
          'created with one transaction setting when the database was '
          'created with another, or by moving a non-portable database '
          'to a different machine.'))
    
#-------------------------------------------------------------------------
#
# Testing code below this point
#
#-------------------------------------------------------------------------

if __name__ == "__main__":

    import unittest

    class TestGrampsDBCallback(unittest.TestCase):

        def test_simple(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-signal' : (int,)
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            t = TestSignals()
            t.connect('test-signal',fn)
            t.emit('test-signal',(1,))
    
            
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"


        def test_exception_catch(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-signal' : (int,)
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            def borked(i):
                rubish.append(i)

            t = TestSignals()

            def null(s):
                pass

            
            global log
            _log = log
            log = null
            
            t.connect('test-signal',borked)
            t.connect('test-signal',fn)
            t.emit('test-signal',(1,))
            log = _log
            
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"

        def test_disconnect(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-signal' : (int,)
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            t = TestSignals()
            key = t.connect('test-signal',fn)
            t.emit('test-signal',(1,))
    
            
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"

            t.disconnect(key)

            t.emit('test-signal',(1,))
                
            assert len(rl) == 1, "Callback not disconnected"
            assert rl[0] == 1, "Callback not disconnected"

        def test_noargs(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-noargs' : None
                         }

            rl = []
            def fn(r=rl):
                rl.append(1)

            t = TestSignals()
            t.connect('test-noargs',fn)
            t.emit('test-noargs')
    
            
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"

        def test_no_callback(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-noargs' : None
                         }

            t = TestSignals()
            t.emit('test-noargs')

        def test_subclassing(self):

            class TestSignals(GrampsDBCallback):
                __signals__ = {
                          'test-signal' : (int,)
                         }
                
            class TestSignalsSubclass(TestSignals):
                __signals__ = {
                          'test-sub-signal' : (int,),
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            t = TestSignalsSubclass()
            t.connect('test-signal',fn)
            t.emit('test-signal',(1,))
                
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"

            t.connect('test-sub-signal',fn)
            t.emit('test-sub-signal',(1,))
                
            assert len(rl) == 2, "No subclass signal emitted"
            assert rl[1] == 1, "Wrong argument recieved in subclass"

        def test_signal_block(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-signal' : (int,)
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            t = TestSignals()
            t.connect('test-signal',fn)
            t.emit('test-signal',(1,))    
            
            assert len(rl) == 1, "No signal emitted"
            assert rl[0] == 1, "Wrong argument recieved"

            GrampsDBCallback.disable_all_signals()
            t.emit('test-signal',(1,))    
            assert len(rl) == 1, "Signal emitted while class blocked"

            GrampsDBCallback.enable_all_signals()
            t.emit('test-signal',(1,))    
            assert len(rl) == 2, "Signals not class unblocked"

            t.disable_signals()
            t.emit('test-signal',(1,))    
            assert len(rl) == 2, "Signal emitted while instance blocked"

            t.enable_signals()
            t.emit('test-signal',(1,))    
            assert len(rl) == 3, "Signals not instance unblocked"

        def test_type_checking(self):

            class TestSignals(GrampsDBCallback):
                __signals__ = {
                          'test-int' : (int,),
                          'test-list': (list,),
                          'test-object': (object,),
                          'test-str': (str,),
                          'test-float': (float,),
                          'test-dict': (dict,),
                          'test-lots': (int,str,list,object,float)
                         }

            rl = []
            def fn(i,r=rl):
                rl.append(i)

            t = TestSignals()
            t.connect('test-int',fn), t.emit('test-int',(1,))
            assert type(rl[0]) == int, "not int"

            t.connect('test-list',fn), t.emit('test-list',([1,2],))
            assert type(rl[1]) == list, "not list"

            t.connect('test-object',fn), t.emit('test-object',(t,))
            assert isinstance(rl[2],object), "not object"

            t.connect('test-float',fn), t.emit('test-float',(2.3,))
            assert type(rl[3]) == float, "not float"

            t.connect('test-dict',fn), t.emit('test-dict',({1:2},))
            assert type(rl[4]) == dict, "not dict"

            rl = []
            def fn2(i,s,l,o,f,r=rl):
                rl.append(i)

            t.connect('test-lots',fn2), t.emit('test-lots',(1,'a',[1,2],t,1.2))
            assert type(rl[0]) == int, "not lots"

            # This should fail because the type of arg1 is wrong
            res=[]
            def fn(s,r=res):
                res.append(s)
            t._warn = fn
            t.connect('test-lots',fn2), t.emit('test-lots',('a','a',[1,2],t,1.2))
            assert res[0][0:6] == "Signal", "Type error not detected"

        def test_recursion_block(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-recursion' : (GrampsDBCallback,)
                         }

            def fn(cb):
                cb.emit('test-recursion',(t,))

            res=[]
            def fn2(s,r=res):
                res.append(s)

            t = TestSignals()
            t._warn = fn2
            t.connect('test-recursion',fn)

            try:
                t.emit('test-recursion',(t,))
            except RuntimeError:
                assert False, "signal recursion not blocked1."

            assert res[0][0:6] == "Signal", "signal recursion not blocked"


        def test_multisignal_recursion_block(self):

            class TestSignals(GrampsDBCallback):

                __signals__ = {
                          'test-top' : (GrampsDBCallback,),
                          'test-middle' : (GrampsDBCallback,),
                          'test-bottom' : (GrampsDBCallback,)
                         }

            def top(cb):
                cb.emit('test-middle',(t,))
            def middle(cb):
                cb.emit('test-bottom',(t,))
            def bottom(cb):
                cb.emit('test-top',(t,))

            res=[]
            def fn2(s,r=res):
                res.append(s)

            t = TestSignals()
            t._warn = fn2
            t.connect('test-top',top)
            t.connect('test-middle',middle)
            t.connect('test-bottom',bottom)

            try:
                t.emit('test-top',(t,))
            except RuntimeError:
                assert False, "multisignal recursion not blocked1."

            assert res[0][0:6] == "Signal", "multisignal recursion not blocked"


    unittest.main()

