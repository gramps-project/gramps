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

import types
import sys

#-------------------------------------------------------------------------
#
# Callback signal support for non-gtk parts of Gramps
#
#-------------------------------------------------------------------------

class GrampsDBCallback(object):
    """
    Callback and signal support for non-gtk parts of gramps.

    Classes that want to emit signals need to inherit from this
    class and call its __init__ method. They then need to declare
    the signals that they can emit and the types of their
    arguments.

    e.g.

        class TestSignals(GrampsDBCallback):

            __signals__ = {
                      'test-signal' : (int,)
                     }

            def __init__(self):
                GrampsDBCallback.__init__(self)

            def emit_signal(self):
                self.emit('test-signal',(1,))

    The signals will be inherited by any subclasses.

    Attaching a callback to the signals is similar to the gtk
    connect methods. e.g.

        class C(object):

            def cb_func(self, i):
                print "got class signal = ", 1

        def fn(i):
            print "got signal value = ", i

        t = TestSignals()

        # connect to a function.
        t.connect('test-signal', fn)
        
        t.emit_signal()

        r = R()
    """

    # If this True no signals will be emitted from any instance of
    # any class derived from this class. This should be toggled using
    # the class methods, dissable_all_signals() and enable_all_signals().
    __BLOCK_ALL_SIGNALS = False
    
    def __init__(self):
        self.__block_instance_signals = False # controls the blocking of
                                              # signals from this instance
        self.__callback_map = {} # dictionary containing all the connected
                                 # callback functions. The keys are the
                                 # signal names and the values are the
                                 # bound methods that will be called when
                                 # the signal is emitted
        self.__signal_map = {}   # dictionary contains all the signals that
                                 # this instance can emit. The keys are the
                                 # signal names and the values are tuples
                                 # containing the list of types of the arguments
                                 # that the callback methods must accept.
        
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
        

    def connect(self, signal_name, callback):
        # Check that signal exists.
        if signal_name not in self.__signal_map.keys():
            sys.stderr.write("Warning: attempt to connect to unknown signal: %s\n" % str(signal_name))
            return
        
        # Add callable to callback_map
        if signal_name not in self.__callback_map.keys():
            self.__callback_map[signal_name] = []
        self.__callback_map[signal_name].append(callback)

    def emit(self, signal_name, args=tuple()):
        # Check that signals are not blocked
        if GrampsDBCallback.__BLOCK_ALL_SIGNALS or \
               self.__block_instance_signals:
            return
        
        # Check signal exists
        if signal_name not in self.__signal_map.keys():
            sys.stderr.write("Warning: attempt to emit to unknown signal: %s\n"
                                % str(signal_name))
            return

        # type check arguments
        arg_types = self.__signal_map[signal_name]
        if arg_types == None and len(args) > 0:
            sys.stderr.write("Warning: signal emitted with "\
                             "wrong number of args: %s\n" % str(signal_name))
            return

        if len(args) > 0:
            if len(args) != len(arg_types):
                sys.stderr.write("Warning: signal emitted with "\
                                 "wrong number of args: %s\n" % str(signal_name))
                return

            if arg_types != None:
                for i in range(0,len(arg_types)):
                    if not isinstance(args[i],arg_types[i]):
                        sys.stderr.write("Warning: signal emitted with "\
                                         "wrong arg types: %s\n" % (str(signal_name),))
                        sys.stderr.write("    arg passed was: %s, type should be: %s\n"
                                         % (args[i],repr(arg_types[i])))
                        return 

        if signal_name in self.__callback_map.keys():
            # Don't bother if there are no callbacks.
            for cb in self.__callback_map[signal_name]:
                try:
                    if type(cb) == tuple: # call class method
                        cb[0](cb[1],*args)
                    elif type(cb) == types.FunctionType or \
                             type(cb) == types.MethodType: # call func
                        cb(*args)
                    else:
                        sys.stderr.write("Warning: badly formed entry in callback map.\n")
                except:
                    sys.stderr.write("Warning: exception occured in callback function.\n")

    #
    # instance signals control methods
    #
    def disable_signals(self):
        self.__block_instance_signals = True
        
    def enable_signals(self):
        self.__block_instance_signals = False
        
    #
    # Class methods
    #

    def __disable_all_signals(cls):
        GrampsDBCallback.__BLOCK_ALL_SIGNALS = True

    disable_all_signals = classmethod(__disable_all_signals)
    
    def __enable_all_signals(cls):
        GrampsDBCallback.__BLOCK_ALL_SIGNALS = False

    enable_all_signals = classmethod(__enable_all_signals)
    
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
            class C:
                def write(self,s,r=res):
                    res.append(s)
            sys.stderr = C()
            t.connect('test-lots',fn2), t.emit('test-lots',('a','a',[1,2],t,1.2))
            assert res[0][0:8] == "Warning:", "Type error not detected"


    unittest.main()
