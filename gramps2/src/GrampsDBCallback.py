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

        # connect to a method
        t.connect_object('test-signal', R.func, r)
        
        t.emit_signal()
    
    """
    
    def __init__(self):
        self.__callback_map = {}
        self.__signal_map = {}
        
        # Build signal list, the signals can't change so we only
        # need to do this once.            
        def trav(cls):
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
                self.__signal_map[k] = v

        # self.__signal_map now contains the connonical list
        # of signals that this instance can emit.
        

    def connect(self, signal_name, callback):
        # Check that signal exists.
        if signal_name not in self.__signal_map.keys():
            print "Warning: attempt to connect to unknown signal: ", str(signal_name)
            return
        
        # Add callable to callback_map
        if signal_name not in self.__callback_map.keys():
            self.__callback_map[signal_name] = []
        self.__callback_map[signal_name].append(callback)

    def connect_object(self, signal_name, class_method, instance):
        # Check that signal exists.
        if signal_name not in self.__signal_map.keys():
            print "Warning: attempt to connect to unknown signal: ", str(signal_name)
            return

        # Add object and instance to callback_map
        self.__callback_map[signal_name].append((class_method,instance))

    def emit(self, signal_name, args=tuple()):
        # Check signal exists
        if signal_name not in self.__signal_map.keys():
            print "Warning: attempt to emit to unknown signal: ", str(signal_name)
            return

        # type check arguments
        arg_types = self.__signal_map[signal_name]
        if arg_types == None and len(args) > 0:
            print "Warning: signal emitted with wrong number of args: ", str(signal_name)
            return

        if len(args) > 0:
            if len(args) != len(arg_types):
                print "Warning: signal emitted with wrong number of args: ", str(signal_name)
                return

            if arg_types != None:
                for i in range(0,len(arg_types)):
                    if type(args[i]) != arg_types[i]:
                        print "Warning: signal emitted with wrong arg types: ", str(signal_name)
                        return 
                
        for cb in self.__callback_map[signal_name]:
            try:
                if type(cb) == tuple: # call class method
                    cb[0](cb[1],*args)
                elif type(cb) == types.FunctionType or \
                         type(cb) == types.MethodType: # call func
                    cb(*args)
                else:
                    print "Warning: badly formed entry in callback map"
            except:
                print "Warning: exception occured in callback function."



#-------------------------------------------------------------------------
#
# Testing code below this point
#
#-------------------------------------------------------------------------

if __name__ == "__main__":


    class TestSignals(GrampsDBCallback):

        __signals__ = {
                  'test-signal' : (int,)
                 }

        def __init__(self):
            GrampsDBCallback.__init__(self)

        def emit_signal(self):
            self.emit('test-signal',(1,))
            self.emit('test-signal',(0,2))
            self.emit('test-signal',(2.0,))

    class TestSignalsSubclass(TestSignals):

        __signals__ = {
                  'test-base-signal' : (str,str,list),
                  'test-noargs'      : None
                 }

        def emit_signal(self):
            self.emit('test-signal',(1,))
            self.emit('test-base-signal',("Hi","There",[1,2,3]))
            self.emit('test-noargs')

    class R(object):

        def func(self, i):
            print "got class signal = ", 1

    def fn(i):
        print "got signal value = ", i

    def fn2(s,t,l):
        print "got signal value = ", s, t, repr(l)

    def fn3():
        print "got signal noargs"

    t = TestSignals()
    t.connect('test-signal', fn)
    t.connect('test-signal', fn)
    t.connect('test-signal', fn)
    t.connect('test-signal', fn)
    #t.emit_signal()

    r = R()
    t.connect_object('test-signal', R.func, r)
    t.connect('test-signal',r.func)
    
    t.emit_signal()

    s = TestSignalsSubclass()
    s.connect('test-signal', fn)
    s.connect('test-base-signal', fn2)
    s.connect('test-noargs', fn3)
    #s.emit_signal()